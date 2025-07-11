#!/usr/bin/env python3
"""
Tag Generator - Schema-ready tag generation
"""
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class TagGenerator:
    """Schema-ready tag generator"""
    
    def __init__(self, config: Dict[str, Any], api_client):
        self.config = config
        self.api_client = api_client
        
    def generate_tags(self, material: str, material_data: Dict[str, Any], article_type: str) -> List[str]:
        """Generate tags - ready for schema integration"""
        logger.info(f"🏷️ Generating tags for {material} ({article_type})")
        
        try:
            # Future: Schema-based tag generation
            # schema = SchemaFactory.get_schema(article_type)
            # tag_config = schema.get_tag_schema()
            # template_context = schema.get_template_context(material_data)
            
            # Current: Simple template-based approach
            template_path = f"tags/tag_{article_type}.md"
            prompt = self._load_and_format_template(template_path, material, material_data, article_type)
            
            # Make API call
            result = self.api_client.call(prompt, f"tag-generation-{article_type}")
            tags = self._parse_tags(result)
            
            # Future: Schema-based tag validation
            # validated_tags = schema.validate_tags(tags, tag_config)
            
            logger.info(f"✅ Generated {len(tags)} tags")
            return tags
            
        except Exception as e:
            logger.warning(f"⚠️ Tag generation failed: {e}")
            return self._get_fallback_tags(material, article_type)
    
    def _load_and_format_template(self, template_path: str, material: str, material_data: Dict[str, Any], article_type: str) -> str:
        """Load and format template - ready for schema contexts"""
        template_file = Path(template_path)
        
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Future: Schema-based context preparation
        # context = schema.get_template_context(material_data)
        
        # Current: Simple context based on article type
        if article_type == "material":
            context = {
                "material": material,
                "material_title": material.title(),
                "author_name": material_data.get("authorName", "Unknown"),
                "author_country": material_data.get("authorCountry", "Unknown"),
            }
        elif article_type == "application":
            context = {
                "application": material_data.get("subject", "Application"),
                "application_title": material_data.get("subject", "Application").title(),
                "author_name": material_data.get("authorName", "Unknown"),
                "author_country": material_data.get("authorCountry", "Unknown"),
            }
        elif article_type == "region":
            context = {
                "region": material_data.get("subject", "Region"),
                "region_title": material_data.get("subject", "Region").title(),
                "material": material,
                "material_title": material.title(),
                "author_name": material_data.get("authorName", "Unknown"),
                "author_country": material_data.get("authorCountry", "Unknown"),
            }
        elif article_type == "thesaurus":
            context = {
                "technical_term": material_data.get("subject", "TechnicalTerm"),
                "technical_term_title": material_data.get("subject", "TechnicalTerm").title(),
                "author_name": material_data.get("authorName", "Unknown"),
                "author_country": material_data.get("authorCountry", "Unknown"),
            }
        else:
            context = {
                "material": material,
                "material_title": material.title(),
                "author_name": material_data.get("authorName", "Unknown"),
                "author_country": material_data.get("authorCountry", "Unknown"),
            }
        
        return template.format(**context)
    
    def _parse_tags(self, response: str) -> List[str]:
        """Parse tags from response"""
        tags = []
        
        for line in response.split('\n'):
            if '#' in line:
                parts = line.split(',')
                for part in parts:
                    part = part.strip()
                    if part.startswith('#'):
                        tag = part[1:].strip()
                        if tag:
                            tags.append(tag)
        
        return tags[:15]  # Limit to 15 tags
    
    def _get_fallback_tags(self, material: str, article_type: str) -> List[str]:
        """Get fallback tags - ready for schema-based fallbacks"""
        base_tags = ["LaserCleaning", "SurfacePreparation"]
        
        # Future: Schema-based fallback tags
        # return schema.get_fallback_tags()
        
        if article_type == "material":
            return base_tags + [material.title(), "IndustrialCleaning", "Manufacturing", "QualityControl"]
        elif article_type == "application":
            return base_tags + ["IndustrialApplications", "ProcessOptimization", "Efficiency"]
        elif article_type == "region":
            return base_tags + [material.title(), "MarketAnalysis", "ManufacturingHub", "RegionalTrends"]
        elif article_type == "thesaurus":
            return base_tags + ["TechnicalTerminology", "LaserPhysics", "EngineeringTerms"]
        
        return base_tags + [material.title(), "IndustrialCleaning", "Manufacturing"]