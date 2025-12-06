"""
Voice Instruction Centralization Policy - Enforcement Tests

Tests verify that ALL voice instructions exist ONLY in persona files.

Policy: docs/08-development/VOICE_INSTRUCTION_CENTRALIZATION_POLICY.md
Grade: F violation if any test fails
"""
import pytest
import re
from pathlib import Path


class TestVoiceInstructionCentralization:
    """Enforce voice instruction centralization policy"""
    
    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent
    
    @pytest.fixture
    def domain_prompts(self, project_root):
        """Get all domain prompt template files"""
        domains_dir = project_root / "domains"
        return list(domains_dir.glob("*/prompts/*.txt"))
    
    @pytest.fixture
    def generation_code(self, project_root):
        """Get all generation Python files"""
        generation_dir = project_root / "generation"
        return list(generation_dir.glob("**/*.py"))
    
    @pytest.fixture
    def shared_code(self, project_root):
        """Get all shared Python files (excluding persona loader)"""
        shared_dir = project_root / "shared"
        files = list(shared_dir.glob("**/*.py"))
        # Exclude persona-related files (they legitimately reference personas)
        return [f for f in files if "persona" not in f.name.lower()]
    
    def test_domain_prompts_no_voice_instructions(self, domain_prompts):
        """
        Domain prompts must NOT contain voice instructions.
        Only {voice_instruction} placeholder is allowed.
        """
        forbidden_patterns = [
            r"conversational\s+(tone|style|professional)",
            r"active\s+voice\s+\(\d+%\)",
            r"Write\s+like\s+you're",
            r"MANDATORY\s+VOICE",
            r"NO\s+conversational\s+tone",
            r"Mix\s+sentence\s+lengths",
            r"Write\s+in\s+conversational",
            r"forbidden\s+(phrases|words|patterns):",
            r"tone:\s*(conversational|professional|formal)",
            r"Use\s+active\s+voice\s+and",
        ]
        
        violations = []
        
        for prompt_file in domain_prompts:
            content = prompt_file.read_text()
            
            # Check for forbidden patterns
            for pattern in forbidden_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Allow {voice_instruction} placeholder
                    if "{voice_instruction}" in content[max(0, match.start()-50):match.end()+50]:
                        continue
                    
                    # Get context around match
                    start = max(0, match.start() - 40)
                    end = min(len(content), match.end() + 40)
                    context = content[start:end].replace('\n', ' ')
                    
                    violations.append({
                        'file': str(prompt_file.relative_to(prompt_file.parent.parent.parent.parent)),
                        'pattern': pattern,
                        'context': context
                    })
        
        if violations:
            error_msg = "\n\n🚨 VOICE INSTRUCTION VIOLATIONS IN DOMAIN PROMPTS:\n\n"
            for v in violations:
                error_msg += f"File: {v['file']}\n"
                error_msg += f"Pattern: {v['pattern']}\n"
                error_msg += f"Context: ...{v['context']}...\n\n"
            error_msg += "❌ Voice instructions must ONLY exist in shared/prompts/personas/*.yaml\n"
            error_msg += "✅ Use {voice_instruction} placeholder instead\n"
            pytest.fail(error_msg)
    
    def test_domain_prompts_have_voice_placeholder(self, domain_prompts):
        """
        Domain prompts SHOULD have {voice_instruction} placeholder.
        """
        missing_placeholder = []
        
        for prompt_file in domain_prompts:
            content = prompt_file.read_text()
            
            # Check if file references voice/author but lacks placeholder
            has_author = "{author}" in content or "{country}" in content
            has_placeholder = "{voice_instruction}" in content
            
            if has_author and not has_placeholder:
                missing_placeholder.append(str(prompt_file.relative_to(
                    prompt_file.parent.parent.parent.parent
                )))
        
        if missing_placeholder:
            error_msg = "\n\n⚠️ MISSING {voice_instruction} PLACEHOLDER:\n\n"
            for file in missing_placeholder:
                error_msg += f"- {file}\n"
            error_msg += "\n✅ Add 'VOICE STYLE:\\n{voice_instruction}' section\n"
            pytest.fail(error_msg)
    
    def test_generation_code_no_voice_instructions(self, generation_code):
        """
        Generation code must NOT contain hardcoded voice instructions.
        Only persona loading and placeholder rendering is allowed.
        """
        forbidden_patterns = [
            r"system_prompt\s*=\s*['\"].*conversational",
            r"prompt\s*\+=\s*['\"].*active\s+voice",
            r"voice_style\s*=\s*['\"]",
            r"tone\s*=\s*['\"]",
            r"['\"]Write\s+like\s+you're",
            r"['\"]Use\s+active\s+voice",
            r"forbidden_phrases\s*=\s*\[",
        ]
        
        violations = []
        
        for code_file in generation_code:
            # Skip test files
            if "test_" in code_file.name:
                continue
            
            content = code_file.read_text()
            
            for pattern in forbidden_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Get line number
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Get context
                    lines = content.split('\n')
                    context_line = lines[line_num - 1] if line_num <= len(lines) else ""
                    
                    violations.append({
                        'file': str(code_file.relative_to(code_file.parent.parent.parent)),
                        'line': line_num,
                        'pattern': pattern,
                        'context': context_line.strip()
                    })
        
        if violations:
            error_msg = "\n\n🚨 VOICE INSTRUCTION VIOLATIONS IN GENERATION CODE:\n\n"
            for v in violations:
                error_msg += f"File: {v['file']}:{v['line']}\n"
                error_msg += f"Pattern: {v['pattern']}\n"
                error_msg += f"Code: {v['context']}\n\n"
            error_msg += "❌ Voice instructions must ONLY exist in shared/prompts/personas/*.yaml\n"
            error_msg += "✅ Load persona and use persona['core_voice_instruction'] instead\n"
            pytest.fail(error_msg)
    
    def test_shared_code_no_voice_overrides(self, shared_code):
        """
        Shared code must NOT contain voice instruction overrides.
        Voice logic should delegate to persona files.
        """
        forbidden_patterns = [
            r"conversational_style\s*=",
            r"voice_override\s*=",
            r"tone_mapping\s*=\s*{",
            r"default_voice\s*=\s*['\"]",
        ]
        
        violations = []
        
        for code_file in shared_code:
            # Skip test files
            if "test_" in code_file.name:
                continue
            
            content = code_file.read_text()
            
            for pattern in forbidden_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    lines = content.split('\n')
                    context_line = lines[line_num - 1] if line_num <= len(lines) else ""
                    
                    violations.append({
                        'file': str(code_file.relative_to(code_file.parent.parent)),
                        'line': line_num,
                        'pattern': pattern,
                        'context': context_line.strip()
                    })
        
        if violations:
            error_msg = "\n\n🚨 VOICE OVERRIDE VIOLATIONS IN SHARED CODE:\n\n"
            for v in violations:
                error_msg += f"File: {v['file']}:{v['line']}\n"
                error_msg += f"Pattern: {v['pattern']}\n"
                error_msg += f"Code: {v['context']}\n\n"
            error_msg += "❌ Voice overrides not permitted in shared code\n"
            error_msg += "✅ All voice logic must come from persona files\n"
            pytest.fail(error_msg)
    
    def test_persona_files_exist(self, project_root):
        """Verify all 4 persona files exist"""
        persona_dir = project_root / "shared" / "prompts" / "personas"
        required_personas = ["indonesia.yaml", "italy.yaml", "taiwan.yaml", "united_states.yaml"]
        
        missing = []
        for persona in required_personas:
            if not (persona_dir / persona).exists():
                missing.append(persona)
        
        if missing:
            pytest.fail(f"Missing persona files: {', '.join(missing)}")
    
    def test_persona_files_complete(self, project_root):
        """Verify persona files have required voice instruction fields"""
        persona_dir = project_root / "shared" / "prompts" / "personas"
        required_fields = ["core_voice_instruction", "tonal_restraint", "forbidden"]
        
        personas = list(persona_dir.glob("*.yaml"))
        incomplete = []
        
        for persona_file in personas:
            import yaml
            with open(persona_file, 'r') as f:
                data = yaml.safe_load(f)
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                incomplete.append({
                    'file': persona_file.name,
                    'missing': missing_fields
                })
        
        if incomplete:
            error_msg = "\n\n⚠️ INCOMPLETE PERSONA FILES:\n\n"
            for item in incomplete:
                error_msg += f"File: {item['file']}\n"
                error_msg += f"Missing: {', '.join(item['missing'])}\n\n"
            pytest.fail(error_msg)


class TestVoiceInstructionQuality:
    """Test that voice instructions produce distinct outputs"""
    
    def test_personas_have_unique_voice_instructions(self):
        """Each persona should have unique voice characteristics"""
        from pathlib import Path
        import yaml
        
        project_root = Path(__file__).parent.parent
        persona_dir = project_root / "shared" / "prompts" / "personas"
        
        personas = []
        for persona_file in persona_dir.glob("*.yaml"):
            with open(persona_file, 'r') as f:
                personas.append({
                    'name': persona_file.stem,
                    'data': yaml.safe_load(f)
                })
        
        # Check that core_voice_instruction differs between personas
        voice_instructions = [p['data'].get('core_voice_instruction', '') for p in personas]
        
        # Simple check: all should be different
        unique_instructions = set(voice_instructions)
        
        if len(unique_instructions) != len(voice_instructions):
            pytest.fail("Some personas have identical core_voice_instruction - should be unique")
