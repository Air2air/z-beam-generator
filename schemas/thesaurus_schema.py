#!/usr/bin/env python3
"""
Thesaurus Schema - Schema for thesaurus articles
"""
import logging
from typing import Dict, Any, List
from .base_schema import BaseSchema

logger = logging.getLogger(__name__)

class ThesaurusSchema(BaseSchema):
    """Schema for thesaurus-type articles"""
    
    def __init__(self):
        super().__init__("thesaurus")
    
    def get_metadata_schema(self) -> Dict[str, Any]:
        """Get metadata schema for thesaurus articles"""
        return {
            "type": "object",
            "required": [
                "title", "technicalTerm", "termCategory",
                "authorName", "authorCountry"
            ],
            "properties": {
                "title": {"type": "string"},
                "technicalTerm": {"type": "string"},
                "termCategory": {"type": "string"},
                "definition": {"type": "string"},
                "scientificNotation": {"type": "string"},
                "relatedTerms": {"type": "array", "items": {"type": "string"}},
                "applications": {"type": "array", "items": {"type": "string"}},
                "measurementUnits": {"type": "string"},
                "applicableMaterials": {"type": "array", "items": {"type": "string"}},  # Optional array
                "authorName": {"type": "string"},
                "authorCountry": {"type": "string"},
                "articleType": {"type": "string", "enum": ["thesaurus"]}
            }
        }
    
    def get_tag_schema(self) -> Dict[str, Any]:
        """Get tag generation schema for thesaurus articles"""
        return {
            "max_tags": 15,
            "required_tags": ["LaserCleaning"],
            "tag_categories": [
                "technical_terminology", # Technical term and variations
                "term_category",        # Category of the term
                "scientific_technical", # Scientific and technical aspects
                "educational_reference", # Educational and reference value
                "application_context"   # Application context
            ],
            "tag_weights": {
                "technical_terminology": 0.35,
                "term_category": 0.20,
                "scientific_technical": 0.25,
                "educational_reference": 0.15,
                "application_context": 0.05
            },
            "context_fields": [
                "technicalTerm", "technical_term_title", "termCategory", 
                "scientificNotation", "authorName", "authorCountry"
            ]
        }
    
    def get_jsonld_schema(self) -> Dict[str, Any]:
        """Get JSON-LD schema for thesaurus articles"""
        return {
            "@context": {
                "@vocab": "https://schema.org/",
                "laser": "https://laser-cleaning.org/terms/",
                "technical": "https://technical-terms.org/terms/"
            },
            "@type": "Article",
            "about": {
                "@type": "technical:Term",
                "name": "{technical_term}",
                "termCategory": "{termCategory}",
                "definition": "{definition}",
                "scientificNotation": "{scientificNotation}",
                "applicableMaterials": "{applicableMaterials}"
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "name": "{technical_term} - Laser Cleaning Technical Term"
            },
            "applicationCategory": "laser:TechnicalTerminology",
            "audience": "technical-professionals"
        }
    
    def get_template_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get template context for thesaurus articles"""
        technical_term = data.get("technicalTerm", data.get("subject", "LaserCleaning"))
        
        return {
            "technical_term": technical_term,
            "technical_term_title": technical_term.title(),
            "authorName": data.get("authorName", "Unknown"),
            "authorCountry": data.get("authorCountry", "Unknown"),
            "termCategory": data.get("termCategory", self._get_term_category(technical_term)),
            "scientificNotation": data.get("scientificNotation", "SIUnits"),
            "applicableMaterials": ", ".join(data.get("applicableMaterials", ["Various materials"])),
            "term_variations": self._get_term_variations(technical_term),
            "related_concepts": self._get_related_concepts(technical_term),
            "primary_applications": self._get_term_applications(technical_term),
            "target_industries": self._get_term_industries(technical_term),
            "definition_type": self._get_definition_type(technical_term),
            "measurement_context": self._get_measurement_context(technical_term)
        }
    
    def validate_data(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate data against thesaurus schema"""
        errors = []
        
        if not data.get("subject"):
            errors.append("Technical term (subject) is required")
        
        if data.get("article_type") != "thesaurus":
            errors.append("Article type must be 'thesaurus'")
        
        # Optional: Validate technical term format
        subject = data.get("subject", "")
        if subject and len(subject) < 2:
            errors.append("Technical term must be at least 2 characters")
        
        # Optional: Check for common technical term patterns
        if subject and " " in subject and not any(char.isupper() for char in subject[1:]):
            errors.append("Technical terms should use CamelCase or contain uppercase letters")
        
        return len(errors) == 0, errors
    
    def get_fallback_tags(self) -> List[str]:
        """Get fallback tags for thesaurus articles"""
        return [
            "LaserCleaning", "TechnicalTerminology", "MaterialScience",
            "LaserPhysics", "EngineeringTerms", "ScientificDefinition",
            "TechnicalReference", "ResearchTerms", "LaserTechnology",
            "SurfaceEngineering", "IndustrialProcesses", "TechnicalEducation"
        ]
    
    def _get_term_category(self, term: str) -> str:
        """Get term category based on technical term"""
        term_lower = term.lower()
        
        if "ablation" in term_lower or "fluence" in term_lower or "irradiance" in term_lower:
            return "LaserPhysics"
        elif "cleaning" in term_lower or "processing" in term_lower or "treatment" in term_lower:
            return "LaserProcessing"
        elif "power" in term_lower or "energy" in term_lower or "wavelength" in term_lower:
            return "LaserParameters"
        elif "surface" in term_lower or "coating" in term_lower or "contamination" in term_lower:
            return "SurfaceEngineering"
        elif "quality" in term_lower or "control" in term_lower or "inspection" in term_lower:
            return "QualityControl"
        else:
            return "LaserTechnology"
    
    def _get_term_variations(self, term: str) -> str:
        """Get term variations and alternative spellings"""
        term_variations = []
        
        # Remove spaces for compound terms
        if " " in term:
            term_variations.append(term.replace(" ", ""))
        
        # Add common variations
        term_lower = term.lower()
        if "laser" in term_lower:
            term_variations.append(term.replace("Laser", "LASER"))
        if "cleaning" in term_lower:
            term_variations.append(term.replace("Cleaning", "Processing"))
        
        return ", ".join(term_variations) if term_variations else term
    
    def _get_related_concepts(self, term: str) -> str:
        """Get related concepts for the technical term"""
        term_lower = term.lower()
        
        if "ablation" in term_lower:
            return "LaserEtching, MaterialRemoval, SurfaceModification"
        elif "fluence" in term_lower:
            return "LaserEnergy, PowerDensity, EnergyDensity"
        elif "cleaning" in term_lower:
            return "SurfacePreparation, ContaminantRemoval, Decoating"
        elif "wavelength" in term_lower:
            return "LaserSpectrum, OpticalProperties, PhotonEnergy"
        else:
            return "LaserProcessing, SurfaceEngineering, MaterialScience"
    
    def _get_term_applications(self, term: str) -> str:
        """Get primary applications for the technical term"""
        term_lower = term.lower()
        
        if "ablation" in term_lower:
            return "MaterialRemoval, SurfaceTexturing, ThinFilmDeposition"
        elif "cleaning" in term_lower:
            return "IndustrialCleaning, SurfacePreparation, Restoration"
        elif "fluence" in term_lower:
            return "ProcessOptimization, QualityControl, ParameterSetting"
        else:
            return "IndustrialProcessing, ManufacturingApplications, SurfaceTreatment"
    
    def _get_term_industries(self, term: str) -> str:
        """Get target industries for the technical term"""
        return "Manufacturing, Aerospace, Automotive, Electronics, Medical"
    
    def _get_definition_type(self, term: str) -> str:
        """Get the type of definition needed"""
        term_lower = term.lower()
        
        if any(word in term_lower for word in ["power", "energy", "wavelength", "frequency"]):
            return "QuantitativeDefinition"
        elif any(word in term_lower for word in ["process", "method", "technique"]):
            return "ProcessDefinition"
        elif any(word in term_lower for word in ["quality", "standard", "specification"]):
            return "QualityDefinition"
        else:
            return "ConceptualDefinition"
    
    def _get_measurement_context(self, term: str) -> str:
        """Get measurement context for the technical term"""
        term_lower = term.lower()
        
        if "power" in term_lower or "energy" in term_lower:
            return "Watts, Joules, PowerDensity"
        elif "wavelength" in term_lower or "frequency" in term_lower:
            return "Nanometers, Hertz, OpticalSpectrum"
        elif "time" in term_lower or "pulse" in term_lower:
            return "Seconds, Milliseconds, PulseFrequency"
        elif "area" in term_lower or "spot" in term_lower:
            return "SquareMillimeters, BeamDiameter, SpotSize"
        else:
            return "SIUnits, StandardMeasurements, MetricSystem"