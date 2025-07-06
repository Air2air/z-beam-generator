"""
Modern repository implementations for the new clean architecture.
"""

import json
import os
from typing import Optional, List, Dict
from datetime import datetime

from domain.entities import Content
from domain.value_objects import ContentSpecs
from domain.simple_repositories import ISimpleContentRepository, ISimplePromptRepository


class ModernFileContentRepository(ISimpleContentRepository):
    """Modern file-based content repository implementation."""
    
    def __init__(self, storage_path: str = "output"):
        self._storage_path = storage_path
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Ensure storage directory exists."""
        os.makedirs(self._storage_path, exist_ok=True)
    
    async def save(self, content: Content) -> None:
        """Save content to file."""
        # Create filename based on content attributes
        filename = f"{content.material.lower()}_{content.category.lower()}_{content.id}.mdx"
        file_path = os.path.join(self._storage_path, filename)
        
        # Prepare content with metadata
        content_with_metadata = self._format_content_for_storage(content)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_with_metadata)
    
    async def get_by_id(self, content_id: str) -> Optional[Content]:
        """Get content by ID."""
        # Search for file with the content ID
        for filename in os.listdir(self._storage_path):
            if content_id in filename and filename.endswith('.mdx'):
                file_path = os.path.join(self._storage_path, filename)
                return await self._load_content_from_file(file_path)
        return None
    
    async def find_by_material(self, material: str) -> List[Content]:
        """Find content by material."""
        contents = []
        material_lower = material.lower()
        
        for filename in os.listdir(self._storage_path):
            if filename.startswith(material_lower) and filename.endswith('.mdx'):
                file_path = os.path.join(self._storage_path, filename)
                content = await self._load_content_from_file(file_path)
                if content:
                    contents.append(content)
        
        return contents
    
    async def delete(self, content_id: str) -> bool:
        """Delete content by ID."""
        for filename in os.listdir(self._storage_path):
            if content_id in filename and filename.endswith('.mdx'):
                file_path = os.path.join(self._storage_path, filename)
                os.remove(file_path)
                return True
        return False
    
    def _format_content_for_storage(self, content: Content) -> str:
        """Format content for file storage with metadata."""
        metadata = {
            "id": content.id,
            "material": content.material,
            "category": content.category,
            "created_at": content.created_at.isoformat(),
            "specs": {
                "max_words": content.specs.max_words,
                "target_style": content.specs.target_style,
                "requirements": content.specs.requirements
            } if content.specs else None
        }
        
        return f"""---
{json.dumps(metadata, indent=2)}
---

{content.body}
"""
    
    async def _load_content_from_file(self, file_path: str) -> Optional[Content]:
        """Load content from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content_text = f.read()
            
            # Parse metadata and content
            if content_text.startswith('---'):
                parts = content_text.split('---', 2)
                if len(parts) >= 3:
                    metadata_text = parts[1].strip()
                    body = parts[2].strip()
                    
                    metadata = json.loads(metadata_text)
                    
                    # Create ContentSpecs if available
                    specs = None
                    if metadata.get('specs'):
                        specs_data = metadata['specs']
                        specs = ContentSpecs(
                            max_words=specs_data.get('max_words', 1000),
                            target_style=specs_data.get('target_style', 'professional'),
                            requirements=specs_data.get('requirements', [])
                        )
                    
                    return Content(
                        id=metadata['id'],
                        body=body,
                        material=metadata['material'],
                        category=metadata['category'],
                        created_at=datetime.fromisoformat(metadata['created_at']),
                        specs=specs
                    )
            
            return None
            
        except Exception:
            return None


class ModernFilePromptRepository(ISimplePromptRepository):
    """Modern file-based prompt repository implementation."""
    
    def __init__(self, prompts_path: str = "prompts"):
        self._prompts_path = prompts_path
        self._cache: Dict[str, str] = {}
    
    async def get_content_prompt(
        self,
        material: str,
        category: str,
        specs: ContentSpecs
    ) -> str:
        """Get content generation prompt."""
        # Use short prompt for small word counts
        if specs.max_words <= 400:
            short_prompt = await self._load_prompt("prompt_material_short")
            if short_prompt:
                return self._customize_prompt(short_prompt, material, category, specs)
        
        # Look for material-specific prompt first
        material_prompt = await self._load_prompt(f"prompt_{material.lower()}")
        if material_prompt:
            return self._customize_prompt(material_prompt, material, category, specs)
        
        # Fallback to generic content prompt
        generic_prompt = await self._load_prompt("prompt_material")
        if generic_prompt:
            return self._customize_prompt(generic_prompt, material, category, specs)
        
        # Ultimate fallback
        return self._create_default_content_prompt(material, category, specs)
    
    async def get_ai_detection_prompt(self, content: str) -> str:
        """Get AI detection prompt."""
        detection_prompt = await self._load_prompt("ai_detection")
        if detection_prompt:
            return f"{detection_prompt}\n\nContent to analyze:\n{content}"
        
        return f"""Analyze the following content and rate how much it appears to be AI-generated on a scale of 0-100, where 0 is completely human-written and 100 is obviously AI-generated.

Look for these AI indicators:
- Repetitive phrasing or structure
- Overly formal or robotic tone
- Generic statements without specific details
- Perfect grammar without natural variations
- Lists that feel artificially structured

Provide only a numeric score (0-100) followed by a brief explanation.

Content to analyze:
{content}"""
    
    async def get_human_detection_prompt(self, content: str) -> str:
        """Get human voice detection prompt."""
        human_prompt = await self._load_prompt("natural_voice_detection")
        if human_prompt:
            return f"{human_prompt}\n\nContent to analyze:\n{content}"
        
        return f"""Analyze the following content and rate how natural and human-like the writing voice is on a scale of 0-100, where 0 is robotic/artificial and 100 is naturally human.

Look for these human indicators:
- Natural conversational flow
- Personal opinions or experiences
- Varied sentence structure
- Industry-specific knowledge
- Authentic enthusiasm or passion for the topic

Provide only a numeric score (0-100) followed by a brief explanation.

Content to analyze:
{content}"""
    
    async def get_improvement_prompt(self, content: str, detection_result) -> str:
        """Get content improvement prompt."""
        improvement_prompt = await self._load_prompt("improvement")
        if improvement_prompt:
            base_prompt = improvement_prompt
        else:
            base_prompt = """Improve the following content to make it sound more natural and human-written while maintaining the technical accuracy and informational value."""
        
        # Add specific guidance based on detection results
        if hasattr(detection_result, 'ai_score') and detection_result.ai_score > 50:
            base_prompt += "\n\nFocus on reducing AI-like characteristics such as repetitive phrasing, overly formal tone, and generic statements."
        
        if hasattr(detection_result, 'human_score') and detection_result.human_score < 50:
            base_prompt += "\n\nFocus on adding more natural human voice, conversational flow, and authentic enthusiasm."
        
        return f"{base_prompt}\n\nContent to improve:\n{content}"
    
    async def _load_prompt(self, prompt_name: str) -> Optional[str]:
        """Load prompt from file with caching."""
        if prompt_name in self._cache:
            return self._cache[prompt_name]
        
        # Try different file extensions and locations
        possible_paths = [
            f"{self._prompts_path}/{prompt_name}.txt",
            f"{self._prompts_path}/{prompt_name}.md",
            f"prompt_archive/{prompt_name}.txt",
            f"detection/{prompt_name}.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    
                    # Handle JSON files (like detection prompts)
                    if path.endswith('.json'):
                        import json
                        data = json.loads(content)
                        if isinstance(data, dict) and 'prompt' in data:
                            content = data['prompt']
                        elif isinstance(data, list) and len(data) > 0:
                            content = data[0] if isinstance(data[0], str) else str(data[0])
                    
                    self._cache[prompt_name] = content
                    return content
                    
                except Exception:
                    continue
        
        return None
    
    def _customize_prompt(
        self,
        base_prompt: str,
        material: str,
        category: str,
        specs: ContentSpecs
    ) -> str:
        """Customize prompt with specific material and requirements."""
        # Replace placeholders in the prompt - support both new and legacy formats
        customized = base_prompt.replace("{material}", material)
        customized = customized.replace("{category}", category)
        customized = customized.replace("{max_words}", str(specs.max_words))
        customized = customized.replace("{style}", specs.target_style)
        
        # Legacy placeholders for backward compatibility
        customized = customized.replace("[Substrate]", material)
        customized = customized.replace("[Category]", category)
        
        # Add requirements if specified
        if specs.requirements:
            requirements_text = "\n".join(f"- {req}" for req in specs.requirements)
            customized += f"\n\nAdditional requirements:\n{requirements_text}"
        
        return customized
    
    def _create_default_content_prompt(
        self,
        material: str,
        category: str,
        specs: ContentSpecs
    ) -> str:
        """Create a default content generation prompt."""
        return f"""Write a comprehensive, informative article about {material} in the {category} category.

Requirements:
- Maximum {specs.max_words} words
- Professional and {specs.target_style} tone
- Include practical applications and benefits
- Provide technical details where appropriate
- Write in a natural, engaging style that doesn't sound AI-generated

Focus on providing valuable, accurate information that would be useful to professionals in the industry."""
