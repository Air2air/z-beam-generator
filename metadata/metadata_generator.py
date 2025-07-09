#!/usr/bin/env python3
"""
Metadata Generator - Generates structured metadata without AI prompts
"""
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class MetadataGenerator:
    """Generates structured metadata for laser cleaning articles"""
    
    def __init__(self, config, api_client):
        self.config = config
        self.api_client = api_client
        self.authors_data = self._load_authors_data()
        
    def generate_metadata(self, material, author_id, article_type):
        """Generate metadata using structured data with AI-generated material properties"""
        logger.info(f"📊 Generating metadata for {material} by author ID {author_id}")
        
        # Get author data
        author_data = self._get_author_data(author_id)
        
        # Generate material properties via AI
        material_data = self._generate_material_properties(material)
        
        # Generate all required fields
        metadata = {
            # Basic article info
            "title": f"Laser Cleaning {material}",
            "articleType": article_type,
            "nameShort": material,
            "description": f"Explore how laser cleaning removes contaminants from {material}, enhancing performance and safety in relevant industries such as Aerospace, Construction, Restoration, Manufacturing, or others.",
            "publishedAt": "2025-07-01",
            "authorId": str(author_id),
            "image": f"/images/Material/material_{material.lower()}.jpg",
            "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
            
            # Author fields
            "authorName": author_data.get("name"),
            "authorSlug": author_data.get("slug"),
            "authorImage": author_data.get("image"),
            "authorTitle": author_data.get("title"),
            "authorBio": author_data.get("bio"),
            "authorCountry": author_data.get("country"),
            
            # Material properties (AI-generated)
            **material_data,
            
            # Fixed values
            "alternativeMethods": ["Chemical etching", "Mechanical polishing", "Ultrasonic cleaning"],
            "costFactors": ["Equipment investment", "Energy consumption", "Safety compliance"],
            
            # Generated tags
            "tags": self._generate_tags(material, material_data)
        }
        
        logger.info(f"✅ Metadata generated with {len(metadata)} fields for author: {author_data.get('name', 'Unknown')}")
        return metadata
    
    def _generate_material_properties(self, material):
        """Generate material properties via AI prompt"""
        logger.info(f"🔬 Generating material properties for {material}")
        
        prompt = f"""Generate comprehensive material properties for {material} in JSON format. Include exactly these fields:

- atomicNumber: atomic number (string) or null for non-elemental materials
- chemicalSymbol: chemical symbol (string) or null for non-elemental materials  
- generalClassifier: "metal", "ceramic", "polymer", "composite", etc.
- materialClass: specific class like "Transition Metal", "Thermoplastic", etc.
- crystalStructure: crystal structure or "Amorphous" for non-crystalline
- density: density with units (string)
- meltingPoint: melting point with units (string)
- thermalConductivity: thermal conductivity with units (string)
- reflectivityIr: IR reflectivity percentage (string)
- reflectivityWavelength: wavelength specification (string, default "10.6 µm")
- hardnessMohs: Mohs hardness (string or number)
- youngsModulus: Young's modulus with units (string)
- specificHeatCapacity: specific heat capacity with units (string)
- materialPurity: typical purity percentage (string)
- materialType: "{material}"
- applications: array of 3-4 main applications
- safetyConsiderations: array of 3-4 safety considerations for laser cleaning
- industryStandards: array of 2-3 relevant industry standards
- environmentalImpact: brief environmental impact description
- processingChallenges: array of 2-3 laser cleaning challenges
- relatedMaterials: array of 3-4 similar materials
- regulatoryCompliance: array of 2-3 relevant regulations
- laserCleaningParameters: object with wavelength, pulseDuration, powerDensity, pulseFrequency, scanningSpeed, spotSize, fluence, pulsesPerSpot, beamProfile, ambientConditions
- performanceMetrics: object with contaminantRemovalEfficiency, surfaceRoughnessReduction, processingTime

Output only valid JSON. Use realistic, technically accurate values."""

        try:
            response = self.api_client.call(prompt, "material-properties")
            
            # Clean response
            if response.startswith('```json'):
                response = response[7:-3]
            elif response.startswith('```'):
                response = response[3:-3]
            
            material_data = json.loads(response)
            logger.info(f"✅ Material properties generated for {material}")
            return material_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse material properties JSON: {e}")
            return self._get_default_material_data(material)
        except Exception as e:
            logger.error(f"❌ Failed to generate material properties: {e}")
            return self._get_default_material_data(material)
    
    def _get_default_material_data(self, material):
        """Return default material data if AI generation fails"""
        logger.warning(f"⚠️ Using default material data for {material}")
        
        return {
            "atomicNumber": None,
            "chemicalSymbol": None,
            "generalClassifier": "unknown",
            "materialClass": "Unknown",
            "crystalStructure": "Unknown",
            "density": "Unknown",
            "meltingPoint": "Unknown",
            "thermalConductivity": "Unknown",
            "reflectivityIr": "Unknown",
            "reflectivityWavelength": "10.6 µm",
            "hardnessMohs": "Unknown",
            "youngsModulus": "Unknown",
            "specificHeatCapacity": "Unknown",
            "materialPurity": "Unknown",
            "materialType": material,
            "applications": [],
            "safetyConsiderations": ["Laser radiation protection"],
            "industryStandards": [],
            "environmentalImpact": "Unknown",
            "processingChallenges": [],
            "relatedMaterials": [],
            "regulatoryCompliance": [],
            "laserCleaningParameters": {
                "wavelength": "1064 nm",
                "pulseDuration": "nanoseconds",
                "powerDensity": "10^6–10^7 W/cm²",
                "pulseFrequency": "10–30 kHz",
                "scanningSpeed": "500–1500 mm/s",
                "spotSize": "0.3 mm",
                "fluence": "0.3–1.5 J/cm²",
                "pulsesPerSpot": "1–5",
                "beamProfile": "Gaussian",
                "ambientConditions": "Ambient air"
            },
            "performanceMetrics": {
                "contaminantRemovalEfficiency": "98%",
                "surfaceRoughnessReduction": "0.2 µm",
                "processingTime": "seconds"
            }
        }
    
    def _load_authors_data(self):
        """Load authors data from JSON file"""
        authors_file = Path(self.config.get("authors_file", "prompts/authors/authors.json"))
        
        if not authors_file.exists():
            logger.error(f"❌ Authors file not found: {authors_file}")
            return []
        
        try:
            with open(authors_file, 'r', encoding='utf-8') as f:
                authors = json.load(f)
            logger.info(f"✅ Loaded {len(authors)} authors from {authors_file}")
            return authors
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse authors JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Failed to load authors file: {e}")
            return []
    
    def _get_author_data(self, author_id):
        """Get author data by ID"""
        # Find author by ID
        for author in self.authors_data:
            if author.get("id") == author_id:
                logger.info(f"✅ Found author: {author.get('name')} (ID: {author_id})")
                return author
        
        # Return default if not found
        logger.warning(f"⚠️ Author ID {author_id} not found, using defaults")
        return {
            "name": "Unknown Author",
            "slug": "unknown-author",
            "image": "/images/Site/Author/default.jpg",
            "title": "Laser Cleaning Expert",
            "bio": "Laser cleaning expert specializing in industrial applications.",
            "country": "Unknown"
        }
    
    def _generate_tags(self, material, material_data):
        """Generate high-quality tags"""
        
        # Base tags
        base_tags = ["Laser Cleaning", "Aerospace", "Construction", "Manufacturing", "Restoration"]
        
        # Collect from material data
        collected_tags = []
        source_fields = [
            "safetyConsiderations", "processingChallenges", "applications", 
            "industryStandards", "relatedMaterials", "regulatoryCompliance"
        ]
        
        for field in source_fields:
            values = material_data.get(field, [])
            if isinstance(values, list):
                collected_tags.extend(values)
        
        # Add fixed tags
        collected_tags.extend(["Chemical etching", "Mechanical polishing", "Ultrasonic cleaning"])
        collected_tags.extend(["Equipment investment", "Energy consumption", "Safety compliance"])
        
        # Shorten and clean tags
        shortened_tags = [self._shorten_tag(tag) for tag in collected_tags]
        
        # Combine and deduplicate
        all_tags = base_tags + [tag for tag in shortened_tags if tag]
        unique_tags = []
        for tag in all_tags:
            if tag and tag not in unique_tags:
                unique_tags.append(tag)
        
        return unique_tags
    
    def _shorten_tag(self, tag):
        """Shorten tag names for better readability"""
        shortenings = {
            "Laser radiation protection": "Radiation Protection",
            "Metal vapor exposure": "Vapor Exposure",
            "Equipment investment": "Equipment Cost",
            "Energy consumption": "Energy Cost",
            "Safety compliance": "Safety Standards",
            "Oxide layer removal": "Oxide Removal",
            "Surface finish improvement": "Surface Finishing",
            "OSHA Metal Dust Standards": "OSHA Standards",
            "EPA Air Quality Guidelines": "EPA Guidelines"
        }
        
        return shortenings.get(tag, tag)