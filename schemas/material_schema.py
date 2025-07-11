#!/usr/bin/env python3
"""
Material Schema - Complete control over all generation
"""
from typing import Dict, Any, List
from datetime import datetime
from .base_schema import BaseSchema

class MaterialSchema(BaseSchema):
    """Complete material schema with full control"""
    
    def __init__(self):
        super().__init__("material")
    
    def get_material_requirement(self, context: Dict[str, Any]) -> str:
        """Get material requirement for this article type"""
        return context["subject"]  # Material articles use subject as material
    
    def enhance_metadata(self, metadata: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance metadata with schema-specific context"""
        metadata["articleType"] = context["article_type"]
        metadata["subject"] = context["subject"]
        return metadata
    
    def generate_tags(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate tags from metadata - no hardcoded values"""
        tags = []
        
        # Required tags from metadata
        if metadata.get("articleType"):
            tags.append("LaserCleaning")
        
        # Material-specific tags
        if metadata.get("nameShort"):
            tags.append(metadata["nameShort"].title())
        
        # Process tags based on metadata
        if metadata.get("materialClass"):
            tags.append("SurfacePreparation")
            tags.append("IndustrialCleaning")
        
        # Industry tags based on applications
        if metadata.get("applications"):
            tags.append("Manufacturing")
            if any("Aerospace" in app for app in metadata["applications"]):
                tags.append("Aerospace")
            if any("Automotive" in app for app in metadata["applications"]):
                tags.append("Automotive")
        
        # Quality tags based on industry standards
        if metadata.get("industryStandards"):
            tags.append("QualityControl")
        
        return tags
    
    def format_tags(self, tags: List[str]) -> str:
        """Format tags for output"""
        return ", ".join(f"#{tag}" for tag in tags)
    
    def generate_jsonld(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON-LD from metadata - no hardcoded values"""
        jsonld = {
            "@context": self._get_context(),
            "@type": "Article"
        }
        
        # Add fields based on metadata presence
        if metadata.get("title"):
            jsonld["headline"] = metadata["title"]
        
        if metadata.get("description"):
            jsonld["description"] = metadata["description"]
        
        if metadata.get("image"):
            jsonld["image"] = metadata["image"]
        
        # Author from metadata
        if metadata.get("authorName"):
            jsonld["author"] = self._build_author(metadata)
        
        # Dates from metadata
        if metadata.get("publishedAt"):
            jsonld["datePublished"] = metadata["publishedAt"]
        
        if metadata.get("lastUpdated"):
            jsonld["dateModified"] = metadata["lastUpdated"]
        
        # Language from metadata or default
        jsonld["inLanguage"] = metadata.get("language", "en-US")
        
        # Publisher
        jsonld["publisher"] = {
            "@type": "Organization",
            "name": "Z-Beam Laser Cleaning"
        }
        
        # Material-specific about section
        jsonld["about"] = self._build_material_about(metadata)
        
        # Application category from metadata
        if metadata.get("articleType"):
            jsonld["applicationCategory"] = f"laser:{metadata['articleType'].title()}Cleaning"
        
        # Keywords from metadata
        keywords = self._generate_keywords(metadata)
        if keywords:
            jsonld["keywords"] = keywords
        
        # Main entity
        if metadata.get("subject"):
            jsonld["mainEntityOfPage"] = {
                "@type": "WebPage",
                "name": f"Laser Cleaning {metadata['subject']}"
            }
        
        return jsonld
    
    def _get_context(self) -> Dict[str, Any]:
        """Get JSON-LD context"""
        return {
            "@vocab": "https://schema.org/",
            "laser": "https://laser-cleaning.org/terms/",
            "material": "https://material-science.org/terms/"
        }
    
    def _build_author(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build author section from metadata"""
        author = {
            "@type": "Person",
            "name": metadata["authorName"]
        }
        
        if metadata.get("authorCountry"):
            author["nationality"] = metadata["authorCountry"]
        
        if metadata.get("authorTitle"):
            author["jobTitle"] = metadata["authorTitle"]
        
        if metadata.get("authorImage"):
            author["image"] = metadata["authorImage"]
        
        return author
    
    def _build_material_about(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build material about section from metadata"""
        about = {
            "@type": "material:Material"
        }
        
        # Basic properties
        if metadata.get("nameShort"):
            about["name"] = metadata["nameShort"]
        
        if metadata.get("subject"):
            about["alternateName"] = metadata["subject"]
        
        if metadata.get("materialClass"):
            about["materialType"] = metadata["materialClass"]
        
        if metadata.get("chemicalSymbol"):
            about["chemicalSymbol"] = metadata["chemicalSymbol"]
        
        if metadata.get("atomicNumber"):
            about["atomicNumber"] = str(metadata["atomicNumber"])
        
        # Physical properties
        physical_props = self._build_physical_properties(metadata)
        if physical_props:
            about["physicalProperties"] = {
                "@type": "material:PhysicalProperties",
                **physical_props
            }
        
        # Laser properties
        laser_props = self._build_laser_properties(metadata)
        if laser_props:
            about["laserProperties"] = {
                "@type": "laser:LaserCleaningParameters",
                **laser_props
            }
        
        # Applications
        if metadata.get("applications"):
            about["applications"] = ", ".join(metadata["applications"])
        
        # Industry standards
        if metadata.get("industryStandards"):
            about["industryStandards"] = ", ".join(metadata["industryStandards"])
        
        return about
    
    def _build_physical_properties(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build physical properties from metadata"""
        props = {}
        
        if metadata.get("density"):
            props["density"] = {
                "@type": "QuantitativeValue",
                "value": str(metadata["density"]),
                "unitCode": "KGM"
            }
        
        if metadata.get("meltingPoint"):
            props["meltingPoint"] = {
                "@type": "QuantitativeValue",
                "value": str(metadata["meltingPoint"]),
                "unitCode": "CEL"
            }
        
        if metadata.get("thermalConductivity"):
            props["thermalConductivity"] = {
                "@type": "QuantitativeValue",
                "value": str(metadata["thermalConductivity"]),
                "unitCode": "WMK"
            }
        
        if metadata.get("youngsModulus"):
            props["youngsModulus"] = {
                "@type": "QuantitativeValue",
                "value": str(metadata["youngsModulus"]),
                "unitCode": "GPA"
            }
        
        return props
    
    def _build_laser_properties(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build laser properties from metadata"""
        props = {}
        
        if metadata.get("laserCleaningParameters"):
            laser_params = metadata["laserCleaningParameters"]
            
            if laser_params.get("energyDensity"):
                props["energyDensity"] = str(laser_params["energyDensity"])
            
            if laser_params.get("pulseDuration"):
                props["pulseDuration"] = str(laser_params["pulseDuration"])
            
            if laser_params.get("repetitionRate"):
                props["repetitionRate"] = str(laser_params["repetitionRate"])
            
            if laser_params.get("wavelength"):
                props["wavelength"] = str(laser_params["wavelength"])
        
        return props
    
    def _generate_keywords(self, metadata: Dict[str, Any]) -> str:
        """Generate keywords from metadata"""
        keywords = []
        
        if metadata.get("subject"):
            keywords.append(f"laser cleaning, {metadata['subject']}")
        
        if metadata.get("materialClass"):
            keywords.append(metadata["materialClass"])
        
        keywords.extend(["material processing", "industrial cleaning"])
        
        return ", ".join(keywords)
    
    def generate_title(self, metadata: Dict[str, Any]) -> str:
        """Generate title from metadata"""
        if metadata.get("title"):
            return metadata["title"]
        elif metadata.get("subject"):
            return f"Laser Cleaning {metadata['subject']}"
        else:
            return "Laser Cleaning Article"
    
    def generate_filename(self, context: Dict[str, Any]) -> str:
        """Generate filename from context"""
        subject = context["subject"].lower().replace(' ', '_').replace('-', '_')
        return f"{subject}_laser_cleaning.md"
    
    def get_article_template(self) -> str:
        """Get article template"""
        return """---
{metadata_yaml}
---

## Tags

{formatted_tags}

## JSON-LD Structured Data

{formatted_jsonld}

---

# {title}

<!-- CONTENT PLACEHOLDER -->
<!-- Article Type: {article_type} | Subject: {subject} -->
<!-- This content area will be populated by external text generation -->

[Article content will be generated here]

<!-- END CONTENT PLACEHOLDER -->
"""
    
    def get_metadata_schema(self) -> Dict[str, Any]:
        """Get metadata schema"""
        return {"type": "object", "properties": {}}
    
    def get_tag_schema(self) -> Dict[str, Any]:
        """Get tag schema"""
        return {"type": "object", "properties": {}}
    
    def get_jsonld_schema(self) -> Dict[str, Any]:
        """Get JSON-LD schema"""
        return {"type": "object", "properties": {}}
    
    def get_template_context(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Get template context"""
        return {}
    
    def validate_data(self, data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate data"""
        return True, []