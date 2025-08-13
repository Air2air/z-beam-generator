#!/usr/bin/env python3
"""
Direct Recovery Runner

A direct recovery system that calls generators without using run.py.
This bypasses the BATCH_CONFIG system and allows targeted component recovery.
"""

import os
import sys
import logging
from typing import Dict, List

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

class DirectRecoveryRunner:
    """Direct recovery runner that calls generators without using run.py"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Component mapping - must match actual generator classes
        self.component_generators = {
            'frontmatter': ('components.frontmatter.generator', 'FrontmatterGenerator'),
            'metatags': ('components.metatags.generator', 'MetatagsGenerator'),
            'table': ('components.table.generator', 'TableGenerator'),
            'bullets': ('components.bullets.generator', 'BulletsGenerator'),
            'caption': ('components.caption.generator', 'CaptionGenerator'),
            'propertiestable': ('components.propertiestable.generator', 'PropertiesTableGenerator'),
            'tags': ('components.tags.generator', 'TagsGenerator'),
            'jsonld': ('components.jsonld.generator', 'JsonldGenerator'),
            'content': ('components.content.generator', 'ContentGenerator'),
        }
    
    def load_run_py_config(self):
        """Load configuration from run.py BATCH_CONFIG"""
        try:
            import run
            return run.BATCH_CONFIG
        except Exception as e:
            self.logger.error(f"Failed to load BATCH_CONFIG from run.py: {e}")
            return None
    
    def load_author_data(self, author_id: int) -> Dict:
        """Load author data by ID"""
        try:
            from components.author.author_service import AuthorService
            author_service = AuthorService()
            author_data = author_service.get_author_by_id(author_id)
            
            if not author_data:
                raise ValueError(f"Author with ID {author_id} not found")
            
            return {
                "author_name": author_data["name"],
                "author_country": author_data["country"],
                "author_id": author_data["id"],
                "author_slug": author_data.get("slug", ""),
                "author_title": author_data.get("title", ""),
                "author_bio": author_data.get("bio", ""),
                "author_specialties": author_data.get("specialties", [])
            }
        except Exception as e:
            self.logger.error(f"Failed to load author data: {e}")
            return {}
    
    def load_schema(self, article_type: str) -> Dict:
        """Load schema for article type"""
        try:
            import json
            schema_path = f"schemas/{article_type}.json"
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Failed to load schema for {article_type}: {e}")
            return {}
    
    def create_component_config(self, component_name: str, batch_config: Dict) -> Dict:
        """Create component configuration"""
        if not batch_config:
            # Default configuration
            return {
                "enabled": True,
                "temperature": 0.7,
                "max_tokens": 2000,
                "ai_provider": "deepseek",
                "options": {
                    "model": "deepseek-chat",
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            }
        
        # Get component config from batch config
        component_config = batch_config.get("components", {}).get(component_name, {}).copy()
        
        # Merge with global AI config
        global_ai = batch_config.get("ai", {})
        component_config["ai_provider"] = global_ai.get("provider", "deepseek")
        component_config["options"] = global_ai.get("options", {}).copy()
        
        # Apply component-specific overrides
        for key in ["temperature", "max_tokens", "model"]:
            if key in component_config:
                component_config["options"][key] = component_config.pop(key)
        
        return component_config
    
    def get_output_path(self, component_name: str, subject: str, article_type: str = "material") -> str:
        """Get output path for component file"""
        from components.base.utils.slug_utils import SlugUtils
        
        # Create safe filename
        safe_subject = SlugUtils.create_slug(subject)
        
        # Use the same pattern as run.py - article type specific
        if article_type == "material":
            filename = f"{safe_subject}-laser-cleaning.md"
        else:
            filename = f"{safe_subject}.md"
        
        # Create directory structure
        base_dir = "content/components"
        component_dir = os.path.join(base_dir, component_name)
        os.makedirs(component_dir, exist_ok=True)
        
        return os.path.join(component_dir, filename)
    
    def recover_component(self, component_name: str, subject: str, 
                         article_type: str = "material", category: str = "composite",
                         author_id: int = 1, timeout: int = 60) -> bool:
        """Recover a single component for a subject"""
        
        if component_name not in self.component_generators:
            self.logger.error(f"Unknown component: {component_name}")
            return False
        
        module_path, class_name = self.component_generators[component_name]
        
        try:
            # Load configuration
            batch_config = self.load_run_py_config()
            component_config = self.create_component_config(component_name, batch_config)
            author_data = self.load_author_data(author_id)
            schema = self.load_schema(article_type)
            
            # Add category to config
            component_config["category"] = category
            component_config["author_id"] = author_id
            
            # Import generator dynamically
            import importlib
            module = importlib.import_module(module_path)
            generator_class = getattr(module, class_name)
            
            # Initialize generator
            generator = generator_class(
                subject=subject,
                article_type=article_type,
                schema=schema,
                author_data=author_data,
                component_config=component_config
            )
            
            self.logger.info(f"Generating {component_name} for {subject}...")
            
            # Generate content
            content = generator.generate()
            
            if not content or not content.strip():
                self.logger.error(f"Generated content is empty for {component_name}")
                return False
            
            # Save content
            output_path = self.get_output_path(component_name, subject, article_type)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Validate the generated content for quality
            from recovery.validator import ContentValidator
            validator = ContentValidator()
            result = validator.validate_markdown_file(output_path, component_name)
            
            if result.status.value in ['success']:
                self.logger.info(f"✅ {component_name} successfully generated and validated: {output_path}")
                return True
            elif result.status.value in ['invalid']:
                self.logger.warning(f"⚠️ {component_name} generated but has quality issues: {', '.join(result.issues)}")
                return False  # Consider invalid content as failure for recovery purposes
            else:
                self.logger.error(f"❌ {component_name} generation failed validation: {', '.join(result.issues)}")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to recover {component_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def recover_components(self, subject: str, failed_components: List[str],
                          article_type: str = "material", category: str = None,
                          author_id: int = 1, timeout: int = 60, retry_count: int = 3) -> Dict[str, bool]:
        """Recover multiple components for a subject"""
        
        # Auto-detect category if not provided
        if not category:
            if any(word in subject.lower() for word in ['glass', 'ceramic', 'alumina', 'zirconia']):
                category = 'ceramic'
            elif any(word in subject.lower() for word in ['metal', 'aluminum', 'steel', 'brass', 'bronze']):
                category = 'metal'
            elif any(word in subject.lower() for word in ['polymer', 'plastic', 'resin', 'composite']):
                category = 'composite'
            elif any(word in subject.lower() for word in ['stone', 'concrete', 'brick', 'mortar']):
                category = 'masonry'
            else:
                category = 'composite'  # Default
        
        results = {}
        
        for component in failed_components:
            success = False
            
            for attempt in range(retry_count):
                if attempt > 0:
                    self.logger.info(f"Retry {attempt + 1}/{retry_count} for {component}...")
                
                success = self.recover_component(
                    component, subject, article_type, category, author_id, timeout
                )
                
                if success:
                    break
            
            results[component] = success
        
        return results
