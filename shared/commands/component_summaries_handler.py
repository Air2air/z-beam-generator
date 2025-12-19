#!/usr/bin/env python3
"""
Per-Component Summary Generation Handler

Generates component summaries one at a time (multiple API calls) instead of
all at once (1 monolithic call). This ensures prompts stay under the
8000 character API limit and produces higher quality focused output.

Architecture:
1. Load component definitions from domain config (component_summaries.yaml)
2. Load base prompt template from domain config.yaml (prompts.component_summary_base)
3. For each component:
   - Build focused prompt with component-specific context
   - Make API call using shared.generation.api_helper
   - Save to component_summaries.{component_id} field
4. Sync to frontmatter/{domain}/{slug}-{domain}.yaml

Uses reusable helpers from shared.generation:
- api_helper: For API calls
- yaml_helper: For atomic YAML operations  
- author_helper: For voice variation

Domain-agnostic: Uses DomainAdapter for all paths and configuration.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

# Reusable helpers (domain-agnostic)
from shared.generation import (
    generate_text,
    get_api_client,
    get_random_author,
    load_yaml_file,
    update_yaml_field,
)

logger = logging.getLogger(__name__)


def _get_domain_paths(domain: str = 'settings') -> tuple:
    """
    Get paths for component summaries based on domain.
    
    Args:
        domain: Domain name (default: 'settings')
        
    Returns:
        Tuple of (components_config_path, domain_config_path, data_yaml_path)
    """
    domain_path = Path(f"domains/{domain}")
    components_config = domain_path / "config" / "component_summaries.yaml"
    domain_config = domain_path / "config.yaml"
    
    # Get data path from domain config
    config = load_yaml_file(domain_config)
    data_path = Path(config.get('data_path', f"data/{domain}/{domain.title()}.yaml"))
    
    return (components_config, domain_config, data_path)


def load_component_definitions(domain: str = 'settings') -> Dict[str, Any]:
    """Load component definitions from domain config."""
    components_config, _, _ = _get_domain_paths(domain)
    data = load_yaml_file(components_config)
    return data.get('components', {})


def load_prompt_template(domain: str = 'settings') -> str:
    """Load base prompt template from domain config.yaml."""
    _, domain_config, _ = _get_domain_paths(domain)
    data = load_yaml_file(domain_config)
    template = data.get('prompts', {}).get('component_summary_base')
    if not template:
        raise KeyError(f"prompts.component_summary_base not found in {domain}/config.yaml")
    return template


def get_item_facts(identifier: str, domain: str = 'settings') -> str:
    """
    Get item facts for prompt context.
    
    Args:
        identifier: Item name/ID
        domain: Domain name (default: 'settings')
        
    Returns:
        Formatted facts string for prompt context
    """
    # Use DomainAdapter for all domains (domain-agnostic)
    from generation.core.adapters.domain_adapter import DomainAdapter
    adapter = DomainAdapter(domain)
    
    try:
        item_data = adapter.get_item_data(identifier)
        return adapter.build_context(item_data)
    except ValueError:
        return f"Item: {identifier}"


def load_persona_voice(country: str) -> str:
    """
    Load voice instruction from persona file based on country.
    
    Returns core_voice_instruction from the persona, or a default if not found.
    """
    import yaml

    # Map country to persona file
    country_to_file = {
        "Taiwan": "taiwan.yaml",
        "Italy": "italy.yaml", 
        "Indonesia": "indonesia.yaml",
        "United States": "united_states.yaml",
    }
    
    filename = country_to_file.get(country)
    if not filename:
        return "Write in clear, professional English with natural sentence variation."
    
    persona_path = Path("shared/voice/profiles") / filename
    if not persona_path.exists():
        return "Write in clear, professional English with natural sentence variation."
    
    try:
        with open(persona_path, 'r') as f:
            persona = yaml.safe_load(f)
        
        # Get core voice instruction
        voice = persona.get('core_voice_instruction', '').strip()
        if voice:
            return voice
        
        return "Write in clear, professional English with natural sentence variation."
    except Exception:
        return "Write in clear, professional English with natural sentence variation."


def generate_single_component(
    material_name: str,
    component_id: str,
    component_config: Dict[str, Any],
    template: str,
    facts: str,
    api_client=None
) -> Optional[str]:
    """
    Generate description for a single component.
    
    Uses DynamicConfig for temperature/tokens - no hardcoded values.
    Returns the generated text or None if generation fails.
    """
    from generation.config.dynamic_config import DynamicConfig

    # Get dynamic config for generation parameters
    dynamic_config = DynamicConfig()
    
    # Get random author for voice variation
    author = get_random_author()
    
    # Load persona voice instruction for this author's country
    voice_instruction = load_persona_voice(author['country'])
    
    # Build the prompt with voice instruction
    prompt = template.format(
        author=author['name'],
        country=author['country'],
        voice_instruction=voice_instruction,
        material=material_name,
        component_title=component_config['title'],
        component_description=component_config['description'].strip(),
        component_id=component_id,
        facts=facts
    )
    
    # Get parameters from DynamicConfig (not hardcoded)
    temperature = dynamic_config.calculate_temperature('component_summary')
    max_tokens = dynamic_config.calculate_max_tokens('component_summary')
    
    print(f"   📝 Prompt: {len(prompt)} chars")
    print(f"   🎭 Author: {author['name']} ({author['country']})")
    print(f"   🌡️  Temperature: {temperature:.3f} (from DynamicConfig)")
    print(f"   🎯 Max tokens: {max_tokens} (from DynamicConfig)")
    
    # Use reusable API helper with dynamic config
    result = generate_text(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        api_client=api_client
    )
    
    return result


def generate_component_summaries(
    identifier: str,
    skip_integrity_check: bool = False,
    domain: str = 'settings'
) -> bool:
    """
    Generate all component summaries using per-component API calls.
    
    This replaces the monolithic approach with focused API calls per component,
    producing higher quality output while staying under prompt limits.
    
    Args:
        identifier: Item name/ID (e.g., material name)
        skip_integrity_check: Skip pre-generation integrity check
        domain: Domain name (default: 'settings')
        
    Returns:
        True if generation succeeded, False otherwise
    """
    print("=" * 80)
    print(f"📊 COMPONENT SUMMARIES GENERATION: {identifier}")
    print("=" * 80)
    print()
    print("📋 Per-component generation (focused API calls for quality output)")
    print(f"📁 Domain: {domain}")
    print()
    
    # Run pre-generation integrity check
    if not skip_integrity_check:
        from shared.commands.integrity_helper import run_pre_generation_check
        if not run_pre_generation_check(skip_check=False, quick=True):
            return False
    
    try:
        # Get domain-specific paths
        _, _, data_yaml_path = _get_domain_paths(domain)
        
        # Initialize API client
        print("🔧 Initializing API client...")
        api_client = get_api_client('grok')
        print("✅ API client ready")
        print()
        
        # Load configurations
        print("📂 Loading component definitions...")
        components = load_component_definitions(domain)
        template = load_prompt_template(domain)
        facts = get_item_facts(identifier, domain)
        print(f"   ✅ Loaded {len(components)} component definitions")
        print(f"   ✅ Template: {len(template)} chars")
        print(f"   ✅ Item facts: {len(facts)} chars")
        print()
        
        # Generate each component
        summaries = {}
        success_count = 0
        fail_count = 0
        
        print("🔄 Generating component summaries...")
        print("-" * 60)
        
        for i, (component_id, component_config) in enumerate(components.items(), 1):
            print(f"\n[{i}/{len(components)}] {component_config['title']} ({component_id})")
            
            result = generate_single_component(
                material_name=identifier,
                component_id=component_id,
                component_config=component_config,
                template=template,
                facts=facts,
                api_client=api_client
            )
            
            if result:
                summaries[component_id] = {
                    'title': component_config['title'],
                    'description': result
                }
                success_count += 1
                print(f"   ✅ Generated: {len(result)} chars")
                # Show preview
                preview = result[:80] + "..." if len(result) > 80 else result
                print(f"   📝 \"{preview}\"")
            else:
                fail_count += 1
                print("   ❌ Failed to generate")
        
        print()
        print("-" * 60)
        print(f"📊 Generation complete: {success_count} succeeded, {fail_count} failed")
        print()
        
        if not summaries:
            print("❌ No summaries generated!")
            return False
        
        # Determine root key for YAML structure
        root_key = domain if domain != 'materials' else 'materials'
        
        # Save to domain YAML using reusable helper
        print(f"💾 Saving to {data_yaml_path}...")
        success = update_yaml_field(
            yaml_path=data_yaml_path,
            keys=[root_key, identifier, 'component_summaries'],
            value=summaries
        )
        
        if success:
            print(f"   ✅ Saved to {data_yaml_path}")
        else:
            print(f"   ❌ Failed to save to {data_yaml_path}")
            return False
        
        # Sync to frontmatter
        print("💾 Syncing to frontmatter...")
        from generation.utils.frontmatter_sync import sync_field_to_frontmatter
        sync_field_to_frontmatter(identifier, 'component_summaries', summaries)
        print(f"   ✅ Synced to frontmatter/{domain}/")
        
        # Show summary report
        print()
        print("=" * 80)
        print("📊 COMPONENT SUMMARIES REPORT")
        print("=" * 80)
        print()
        for comp_id, comp_data in summaries.items():
            print(f"📌 {comp_data['title']}")
            print(f"   {comp_data['description']}")
            print()
        
        print("=" * 80)
        print(f"✨ Component summaries generation complete for {identifier}!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during component summaries generation: {e}")
        import traceback
        traceback.print_exc()
        return False
