#!/usr/bin/env python3
"""
JSON-LD Generator - Schema-driven structured data generation
"""
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class JSONLDGenerator:
    """Generate JSON-LD structured data dynamically from schemas"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def generate_jsonld(self, article_type: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON-LD for article type using schema"""
        logger.info(f"🔗 Generating JSON-LD for {article_type}")
        
        try:
            # Get schema for article type
            schema = self._get_schema(article_type)
            
            # Generate JSON-LD template from schema
            template = self._generate_template_from_schema(schema, article_type)
            
            # Prepare context data
            jsonld_context = self._prepare_context(article_type, metadata, context, schema)
            
            # Generate JSON-LD
            jsonld_data = self._populate_template(template, jsonld_context)
            
            # Add common fields
            jsonld_data = self._add_common_fields(jsonld_data, metadata)
            
            # Validate JSON-LD
            self._validate_jsonld(jsonld_data)
            
            logger.info(f"✅ Generated JSON-LD with {len(jsonld_data)} fields")
            return jsonld_data
            
        except Exception as e:
            logger.warning(f"⚠️ JSON-LD generation failed: {e}")
            return self._get_fallback_jsonld(article_type, metadata, context)
    
    def _get_schema(self, article_type: str):
        """Get schema for article type"""
        try:
            # Try to import schema factory
            from schemas.schema_factory import SchemaFactory
            return SchemaFactory.get_schema(article_type)
        except ImportError:
            # Fallback to direct imports if no schema factory
            if article_type == "material":
                from schemas.material_schema import MaterialSchema
                return MaterialSchema()
            elif article_type == "application":
                from schemas.application_schema import ApplicationSchema
                return ApplicationSchema()
            elif article_type == "region":
                from schemas.region_schema import RegionSchema
                return RegionSchema()
            elif article_type == "thesaurus":
                from schemas.thesaurus_schema import ThesaurusSchema
                return ThesaurusSchema()
            else:
                raise ValueError(f"Unknown article type: {article_type}")
    
    def _generate_template_from_schema(self, schema, article_type: str) -> Dict[str, Any]:
        """Generate JSON-LD template dynamically from schema"""
        try:
            # If schema has JSON-LD method, use it
            if hasattr(schema, 'get_jsonld_schema'):
                return schema.get_jsonld_schema()
            else:
                # Generate from metadata schema
                return self._build_jsonld_from_metadata_schema(schema, article_type)
        except Exception as e:
            logger.warning(f"⚠️ Schema-based template generation failed: {e}")
            return self._get_base_template(article_type)
    
    def _build_jsonld_from_metadata_schema(self, schema, article_type: str) -> Dict[str, Any]:
        """Build JSON-LD template from metadata schema"""
        metadata_schema = schema.get_metadata_schema()
        properties = metadata_schema.get("properties", {})
        
        # Base JSON-LD structure
        jsonld_template = {
            "@context": self._get_context_for_type(article_type),
            "@type": "Article",
            "headline": "{title}",
            "about": self._build_about_section(article_type, properties),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "name": self._get_page_name_template(article_type)
            },
            "applicationCategory": self._get_application_category(article_type),
            "keywords": self._get_keywords_template(article_type)
        }
        
        return jsonld_template
    
    def _get_context_for_type(self, article_type: str) -> Dict[str, Any]:
        """Get JSON-LD context for article type"""
        base_context = {
            "@vocab": "https://schema.org/",
            "laser": "https://laser-cleaning.org/terms/"
        }
        
        if article_type == "material":
            base_context["material"] = "https://material-science.org/terms/"
        elif article_type == "application":
            base_context["industrial"] = "https://industrial-process.org/terms/"
        elif article_type == "region":
            base_context["geo"] = "https://geo.org/terms/"
        elif article_type == "thesaurus":
            base_context["technical"] = "https://technical-terms.org/terms/"
        
        return base_context
    
    def _build_about_section(self, article_type: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Build the 'about' section based on article type and schema properties"""
        if article_type == "material":
            return {
                "@type": "material:Material",
                "name": "{material}",
                "materialType": "{material_class}",
                "chemicalSymbol": "{chemical_symbol}",
                "physicalProperties": {
                    "@type": "material:PhysicalProperties",
                    "density": {
                        "@type": "QuantitativeValue",
                        "value": "{density}",
                        "unitCode": "KGM"
                    },
                    "meltingPoint": {
                        "@type": "QuantitativeValue",
                        "value": "{melting_point}",
                        "unitCode": "CEL"
                    }
                }
            }
        elif article_type == "application":
            return {
                "@type": "industrial:Application",
                "name": "{application}",
                "applicationType": "{industry_category}",
                "componentType": "{component_type}",
                "applicableMaterials": "{material_types}"
            }
        elif article_type == "region":
            return {
                "@type": "geo:Region",
                "name": "{region}",
                "addressLocality": "{region}",
                "addressRegion": "{state}",
                "addressCountry": "{country}",
                "primaryIndustry": "{primary_industries}"
            }
        elif article_type == "thesaurus":
            return {
                "@type": "technical:Term",
                "name": "{technical_term}",
                "termCategory": "{term_category}",
                "definition": "{definition}",
                "scientificNotation": "{scientific_notation}"
            }
        else:
            return {
                "@type": "Thing",
                "name": "{subject}"
            }
    
    def _get_page_name_template(self, article_type: str) -> str:
        """Get page name template for article type"""
        if article_type == "material":
            return "Laser Cleaning {material}"
        elif article_type == "application":
            return "Laser Cleaning for {application}"
        elif article_type == "region":
            return "Laser Cleaning in {region}"
        elif article_type == "thesaurus":
            return "{technical_term} - Laser Cleaning Technical Term"
        else:
            return "Laser Cleaning {subject}"
    
    def _get_application_category(self, article_type: str) -> str:
        """Get application category for article type"""
        categories = {
            "material": "laser:MaterialCleaning",
            "application": "laser:ApplicationCleaning",
            "region": "laser:RegionalMarket",
            "thesaurus": "laser:TechnicalTerminology"
        }
        return categories.get(article_type, "laser:LaserCleaning")
    
    def _get_keywords_template(self, article_type: str) -> str:
        """Get keywords template for article type"""
        if article_type == "material":
            return "laser cleaning, {material}, material processing, industrial cleaning"
        elif article_type == "application":
            return "laser cleaning, {application}, industrial applications, {industry_category}"
        elif article_type == "region":
            return "laser cleaning, {region}, regional market, {primary_industries}"
        elif article_type == "thesaurus":
            return "laser cleaning, {technical_term}, technical terminology, {term_category}"
        else:
            return "laser cleaning, {subject}, industrial processing"
    
    def _get_base_template(self, article_type: str) -> Dict[str, Any]:
        """Get basic template if schema-based generation fails"""
        return {
            "@context": "https://schema.org/",
            "@type": "Article",
            "headline": "{title}",
            "about": "{subject}",
            "articleSection": "LaserCleaning",
            "applicationCategory": self._get_application_category(article_type)
        }
    
    def _prepare_context(self, article_type: str, metadata: Dict[str, Any], context: Dict[str, Any], schema=None) -> Dict[str, Any]:
        """Prepare context data using schema template context"""
        try:
            # Use schema's template context if available
            if schema and hasattr(schema, 'get_template_context'):
                # Prepare data for schema
                schema_data = {
                    **metadata,
                    **context,
                    "technicalTerm": context.get("subject") if article_type == "thesaurus" else None,
                    "application": context.get("subject") if article_type == "application" else None,
                    "region": context.get("subject") if article_type == "region" else None,
                    "material": context.get("subject") if article_type == "material" else None
                }
                
                template_context = schema.get_template_context(schema_data)
                
                # Add base context
                template_context.update({
                    "title": metadata.get("title", "Laser Cleaning Article"),
                    "author_name": metadata.get("authorName", "Unknown"),
                    "author_country": metadata.get("authorCountry", "Unknown"),
                    "publish_date": datetime.now().isoformat(),
                    "article_type": article_type,
                    "subject": context.get("subject", "LaserCleaning")
                })
                
                return template_context
            else:
                # Fallback to original context preparation
                return self._prepare_context_fallback(article_type, metadata, context)
                
        except Exception as e:
            logger.warning(f"⚠️ Schema context preparation failed: {e}")
            return self._prepare_context_fallback(article_type, metadata, context)
    
    def _prepare_context_fallback(self, article_type: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback context preparation"""
        base_context = {
            "title": metadata.get("title", "Laser Cleaning Article"),
            "author_name": metadata.get("authorName", "Unknown"),
            "author_country": metadata.get("authorCountry", "Unknown"),
            "publish_date": datetime.now().isoformat(),
            "article_type": article_type,
            "subject": context.get("subject", "LaserCleaning")
        }
        
        # Add type-specific context
        if article_type == "material":
            base_context.update(self._get_material_context(metadata, context))
        elif article_type == "application":
            base_context.update(self._get_application_context(metadata, context))
        elif article_type == "region":
            base_context.update(self._get_region_context(metadata, context))
        elif article_type == "thesaurus":
            base_context.update(self._get_thesaurus_context(metadata, context))
        
        return base_context
    
    def _get_material_context(self, metadata: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Get context for material articles"""
        material = context.get("subject", "steel")
        
        return {
            "material": material,
            "material_class": metadata.get("materialClass", "Metal"),
            "chemical_symbol": metadata.get("chemicalSymbol", ""),
            "density": metadata.get("density", 0),
            "melting_point": metadata.get("meltingPoint", 0),
            "thermal_conductivity": metadata.get("thermalConductivity", 0),
            "applications": ", ".join(metadata.get("applications", ["Industrial cleaning"]))
        }
    
    def _get_application_context(self, metadata: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Get context for application articles"""
        application = context.get("subject", "Industrial Application")
        
        return {
            "application": application,
            "industry_category": metadata.get("industryCategory", "Manufacturing"),
            "component_type": metadata.get("componentType", "Industrial Components"),
            "material_types": ", ".join(metadata.get("materialTypes", ["Various materials"])),
            "benefits": ", ".join(metadata.get("benefits", ["Efficient cleaning"]))
        }
    
    def _get_region_context(self, metadata: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Get context for region articles"""
        region = context.get("subject", "Manufacturing Region")
        
        return {
            "region": region,
            "county": metadata.get("county", "Unknown County"),
            "state": metadata.get("state", "California"),
            "country": "United States",
            "primary_industries": ", ".join(metadata.get("primaryIndustries", ["Manufacturing"])),
            "material_focus": context.get("material", "steel")
        }
    
    def _get_thesaurus_context(self, metadata: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Get context for thesaurus articles"""
        technical_term = context.get("subject", "LaserCleaning")
        
        return {
            "technical_term": technical_term,
            "term_category": metadata.get("termCategory", "LaserTechnology"),
            "definition": metadata.get("definition", "Technical term related to laser cleaning"),
            "scientific_notation": metadata.get("scientificNotation", "SIUnits"),
            "applicable_materials": ", ".join(metadata.get("applicableMaterials", ["Various materials"])),
            "related_terms": ", ".join(metadata.get("relatedTerms", ["LaserProcessing"]))
        }
    
    def _populate_template(self, template: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Populate template with context data"""
        # Convert template to string, replace placeholders, convert back
        template_str = json.dumps(template, indent=2)
        
        # Replace placeholders safely
        for key, value in context.items():
            if value is not None:
                placeholder = f"{{{key}}}"
                template_str = template_str.replace(placeholder, str(value))
        
        # Remove unreplaced placeholders
        import re
        template_str = re.sub(r'\{[^}]+\}', '', template_str)
        
        return json.loads(template_str)
    
    def _add_common_fields(self, jsonld_data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Add common fields to all JSON-LD structures"""
        jsonld_data.update({
            "datePublished": datetime.now().isoformat(),
            "inLanguage": "en-US",
            "publisher": {
                "@type": "Organization",
                "name": "Z-Beam Laser Cleaning",
                "url": "https://z-beam-laser-cleaning.com"
            },
            "author": {
                "@type": "Person",
                "name": metadata.get("authorName", "Unknown"),
                "nationality": metadata.get("authorCountry", "Unknown")
            }
        })
        
        return jsonld_data
    
    def _validate_jsonld(self, jsonld_data: Dict[str, Any]) -> None:
        """Basic validation of JSON-LD structure"""
        required_fields = ["@context", "@type"]
        
        for field in required_fields:
            if field not in jsonld_data:
                raise ValueError(f"Missing required JSON-LD field: {field}")
    
    def _get_fallback_jsonld(self, article_type: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback JSON-LD if generation fails"""
        return {
            "@context": "https://schema.org/",
            "@type": "Article",
            "headline": metadata.get("title", "Laser Cleaning Article"),
            "about": context.get("subject", "LaserCleaning"),
            "articleSection": "LaserCleaning",
            "author": {
                "@type": "Person",
                "name": metadata.get("authorName", "Unknown")
            },
            "datePublished": datetime.now().isoformat(),
            "inLanguage": "en-US"
        }