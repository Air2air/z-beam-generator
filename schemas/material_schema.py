#!/usr/bin/env python3
"""
Material Schema - JSON-LD focused material article schema
"""
from typing import Dict, Any
from .base_schema import BaseSchema

class MaterialSchema(BaseSchema):
    """Schema for material-type articles"""
    
    def __init__(self):
        super().__init__("material")
    
    def get_metadata_schema(self) -> Dict[str, Any]:
        """Get metadata schema for material articles"""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "nameShort": {"type": "string"},
                "subject": {"type": "string"},
                "materialClass": {"type": "string"},
                "chemicalSymbol": {"type": "string"},
                "atomicNumber": {"type": "integer"},
                "density": {"type": "number"},
                "meltingPoint": {"type": "number"},
                "thermalConductivity": {"type": "number"},
                "youngsModulus": {"type": "number"},
                "applications": {"type": "array"},
                "industryStandards": {"type": "array"},
                "laserCleaningParameters": {"type": "object"},
                "authorName": {"type": "string"},
                "authorCountry": {"type": "string"},
                "authorTitle": {"type": "string"},
                "authorImage": {"type": "string"},
                "description": {"type": "string"},
                "image": {"type": "string"},
                "publishedAt": {"type": "string"},
                "lastUpdated": {"type": "string"}
            }
        }
    
    def get_tag_schema(self) -> Dict[str, Any]:
        """Get tag generation schema for material articles"""
        return {
            "required_tags": ["LaserCleaning", "SurfacePreparation", "IndustrialCleaning", "Manufacturing"],
            "material_tag": "{nameShort}",
            "process_tags": ["QualityControl", "SurfacePreparation"],
            "industry_tags": ["Manufacturing", "Industrial"]
        }
    
    def get_jsonld_schema(self) -> Dict[str, Any]:
        """Get JSON-LD schema for material articles"""
        return {
            "@context": {
                "@vocab": "https://schema.org/",
                "laser": "https://laser-cleaning.org/terms/",
                "material": "https://material-science.org/terms/"
            },
            "@type": "Article",
            "headline": "{title}",
            "about": {
                "@type": "material:Material",
                "name": "{nameShort}",
                "alternateName": "{subject}",
                "materialType": "{materialClass}",
                "chemicalSymbol": "{chemicalSymbol}",
                "atomicNumber": "{atomicNumber}",
                "physicalProperties": {
                    "@type": "material:PhysicalProperties",
                    "density": {
                        "@type": "QuantitativeValue",
                        "value": "{density}",
                        "unitCode": "KGM"
                    },
                    "meltingPoint": {
                        "@type": "QuantitativeValue",
                        "value": "{meltingPoint}",
                        "unitCode": "CEL"
                    },
                    "thermalConductivity": {
                        "@type": "QuantitativeValue",
                        "value": "{thermalConductivity}",
                        "unitCode": "WMK"
                    },
                    "youngsModulus": {
                        "@type": "QuantitativeValue",
                        "value": "{youngsModulus}",
                        "unitCode": "GPA"
                    }
                },
                "laserProperties": {
                    "@type": "laser:LaserCleaningParameters",
                    "energyDensity": "{laserCleaningParameters.energyDensity}",
                    "pulseDuration": "{laserCleaningParameters.pulseDuration}",
                    "repetitionRate": "{laserCleaningParameters.repetitionRate}",
                    "wavelength": "{laserCleaningParameters.wavelength}"
                },
                "applications": "{applications}",
                "industryStandards": "{industryStandards}"
            },
            "author": {
                "@type": "Person",
                "name": "{authorName}",
                "nationality": "{authorCountry}",
                "jobTitle": "{authorTitle}",
                "image": "{authorImage}"
            },
            "description": "{description}",
            "image": "{image}",
            "datePublished": "{publishedAt}",
            "dateModified": "{lastUpdated}",
            "inLanguage": "en-US",
            "publisher": {
                "@type": "Organization",
                "name": "Z-Beam Laser Cleaning"
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "name": "Laser Cleaning {nameShort}"
            },
            "applicationCategory": "laser:MaterialCleaning",
            "keywords": "laser cleaning, {nameShort}, {materialClass}, material processing, industrial cleaning"
        }
    
    def get_template_context(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Get template context for material articles"""
        return {
            "title": metadata.get("title", ""),
            "nameShort": metadata.get("nameShort", ""),
            "subject": metadata.get("subject", ""),
            "materialClass": metadata.get("materialClass", ""),
            "chemicalSymbol": metadata.get("chemicalSymbol", ""),
            "atomicNumber": metadata.get("atomicNumber", ""),
            "density": metadata.get("density", ""),
            "meltingPoint": metadata.get("meltingPoint", ""),
            "thermalConductivity": metadata.get("thermalConductivity", ""),
            "youngsModulus": metadata.get("youngsModulus", ""),
            "applications": ", ".join(metadata.get("applications", [])),
            "industryStandards": ", ".join(metadata.get("industryStandards", [])),
            "laserCleaningParameters.energyDensity": metadata.get("laserCleaningParameters", {}).get("energyDensity", ""),
            "laserCleaningParameters.pulseDuration": metadata.get("laserCleaningParameters", {}).get("pulseDuration", ""),
            "laserCleaningParameters.repetitionRate": metadata.get("laserCleaningParameters", {}).get("repetitionRate", ""),
            "laserCleaningParameters.wavelength": metadata.get("laserCleaningParameters", {}).get("wavelength", ""),
            "authorName": metadata.get("authorName", ""),
            "authorCountry": metadata.get("authorCountry", ""),
            "authorTitle": metadata.get("authorTitle", ""),
            "authorImage": metadata.get("authorImage", ""),
            "description": metadata.get("description", ""),
            "image": metadata.get("image", ""),
            "publishedAt": metadata.get("publishedAt", ""),
            "lastUpdated": metadata.get("lastUpdated", "")
        }
    
    def validate_data(self, data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate data against schema"""
        errors = []
        
        # Check required fields
        required_fields = ["title", "nameShort", "subject", "materialClass"]
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Check numeric fields
        numeric_fields = ["density", "meltingPoint", "thermalConductivity", "youngsModulus"]
        for field in numeric_fields:
            if field in data and data[field] is not None:
                try:
                    float(data[field])
                except (ValueError, TypeError):
                    errors.append(f"Invalid numeric value for {field}: {data[field]}")
        
        return len(errors) == 0, errors