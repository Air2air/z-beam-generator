#!/usr/bin/env python3
"""
Metadata Generator - Generates structured metadata without tags
"""
import logging
import json
from datetime import datetime
from pathlib import Path  # Add this import

logger = logging.getLogger(__name__)

class MetadataGenerator:
    """Generates structured metadata for laser cleaning articles"""
    
    def __init__(self, config, api_client):
        self.config = config
        self.api_client = api_client
        self.authors_data = self._load_authors_data()
        # REMOVED: self.tag_generator = TagGenerator(api_client)
    
    def generate_metadata(self, material, author_id, article_type):
        """Generate metadata using structured data with AI-generated material properties"""
        logger.info(f"📊 Generating metadata for {material} by author ID {author_id}")
        
        # Get author data - FAIL if not found
        author_data = self._get_author_data(author_id)
        
        # Generate material properties via AI - FAIL if unable
        material_data = self._generate_material_properties(material)
        
        # Generate all required fields (NO TAGS)
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
            
            # Author fields - required
            "authorName": author_data["name"],
            "authorSlug": author_data["slug"],
            "authorImage": author_data["image"],
            "authorTitle": author_data["title"],
            "authorCountry": author_data["country"],
            
            # Material properties (AI-generated) - required
            "atomicNumber": material_data["atomicNumber"],
            "chemicalSymbol": material_data["chemicalSymbol"],
            "generalClassifier": material_data["generalClassifier"],
            "materialClass": material_data["materialClass"],
            "crystalStructure": material_data["crystalStructure"],
            "density": material_data["density"],
            "meltingPoint": material_data["meltingPoint"],
            "thermalConductivity": material_data["thermalConductivity"],
            "reflectivityIr": material_data["reflectivityIr"],
            "reflectivityWavelength": material_data["reflectivityWavelength"],
            "hardnessMohs": material_data["hardnessMohs"],
            "youngsModulus": material_data["youngsModulus"],
            "specificHeatCapacity": material_data["specificHeatCapacity"],
            "materialPurity": material_data["materialPurity"],
            "materialType": material_data["materialType"],
            
            # Keep only non-redundant fields (not already in tags)
            "environmentalImpact": material_data["environmentalImpact"],
            
            # Ensure proper data types - arrays and objects, NOT strings
            "processingChallenges": material_data["processingChallenges"],         
            "laserCleaningParameters": material_data["laserCleaningParameters"],   
            "performanceMetrics": material_data["performanceMetrics"],             
            "alternativeMethods": ["Chemical etching", "Mechanical polishing", "Ultrasonic cleaning"],  
            "costFactors": ["Equipment investment", "Energy consumption", "Safety compliance"],          
            
            # REMOVED: "tags": self.tag_generator.generate_tags(material, material_data)
        }
        
        logger.info(f"✅ Metadata generated for {material}")
        return metadata, material_data  # Return both metadata and material_data for tags
    
    def _generate_material_properties(self, material):
        """Generate material properties via AI prompt - FAIL if unable"""
        logger.info(f"🔬 Generating material properties for {material}")
        
        prompt = f"""Generate comprehensive material properties for {material} in JSON format. 

CRITICAL: Return valid JSON with proper data types:
- Arrays must be actual JSON arrays: ["item1", "item2"] NOT string representations
- Objects must be actual JSON objects: {{"key": "value"}} NOT string representations
- Do not wrap arrays or objects in quotes

Required fields with exact data types:

- atomicNumber: string or null
- chemicalSymbol: string or null  
- generalClassifier: string ("metal", "ceramic", "polymer", "composite")
- materialClass: string (e.g., "Transition Metal", "Thermoplastic")
- crystalStructure: string
- density: string with units
- meltingPoint: string with units
- thermalConductivity: string with units
- reflectivityIr: string percentage
- reflectivityWavelength: string (default "10.6 µm")
- hardnessMohs: string or number
- youngsModulus: string with units
- specificHeatCapacity: string with units
- materialPurity: string percentage
- materialType: "{material}"
- applications: ARRAY of 3-4 strings (NOT a string)
- safetyConsiderations: ARRAY of 3-4 strings (NOT a string)
- industryStandards: ARRAY of 2-3 strings (NOT a string)
- environmentalImpact: string description
- processingChallenges: ARRAY of 2-3 strings (NOT a string)
- relatedMaterials: ARRAY of 3-4 strings (NOT a string)
- regulatoryCompliance: ARRAY of 2-3 strings (NOT a string)
- laserCleaningParameters: OBJECT with keys: wavelength, pulseDuration, powerDensity, pulseFrequency, scanningSpeed, spotSize, fluence, pulsesPerSpot, beamProfile, ambientConditions (NOT a string)
- performanceMetrics: OBJECT with keys: contaminantRemovalEfficiency, surfaceRoughnessReduction, processingTime (NOT a string)

Example format:
{{
  "applications": ["Aerospace structures", "Medical implants", "Automotive parts"],
  "safetyConsiderations": ["Avoid dust inhalation", "Use eye protection", "Ensure ventilation"],
  "laserCleaningParameters": {{
    "wavelength": "1064 nm",
    "pulseDuration": "100 ns",
    "powerDensity": "5 kW/cm²"
  }}
}}

Output ONLY valid JSON. Use realistic, technically accurate values."""

        try:
            response = self.api_client.call(prompt, "material-properties")
            
            # Clean response
            if response.startswith('```json'):
                response = response[7:-3]
            elif response.startswith('```'):
                response = response[3:-3]
            
            material_data = json.loads(response)
            
            # Validate and convert string arrays/objects if needed
            material_data = self._fix_data_types(material_data)
            
            # Validate required fields are present
            required_fields = [
                "atomicNumber", "chemicalSymbol", "generalClassifier", "materialClass",
                "crystalStructure", "density", "meltingPoint", "thermalConductivity",
                "reflectivityIr", "reflectivityWavelength", "hardnessMohs", "youngsModulus",
                "specificHeatCapacity", "materialPurity", "materialType", "applications",
                "safetyConsiderations", "industryStandards", "environmentalImpact",
                "processingChallenges", "relatedMaterials", "regulatoryCompliance",
                "laserCleaningParameters", "performanceMetrics"
            ]
            
            missing_fields = [field for field in required_fields if field not in material_data]
            if missing_fields:
                raise ValueError(f"Missing required fields in material data: {missing_fields}")
            
            logger.info(f"✅ Material properties generated for {material}")
            return material_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse material properties JSON: {e}")
            raise RuntimeError(f"Failed to generate valid material properties JSON for {material}: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to generate material properties: {e}")
            raise RuntimeError(f"Failed to generate material properties for {material}: {e}")

    def _fix_data_types(self, material_data):
        """Fix data types if AI returned strings instead of arrays/objects"""
        import ast
        
        # Fields that should be arrays
        array_fields = ["applications", "safetyConsiderations", "industryStandards", "processingChallenges", "relatedMaterials", "regulatoryCompliance"]
        
        # Fields that should be objects
        object_fields = ["laserCleaningParameters", "performanceMetrics"]
        
        # Fix arrays
        for field in array_fields:
            if field in material_data and isinstance(material_data[field], str):
                try:
                    # Try to parse string representation of array
                    material_data[field] = ast.literal_eval(material_data[field])
                    logger.warning(f"⚠️ Converted string to array for field: {field}")
                except (ValueError, SyntaxError):
                    logger.error(f"❌ Failed to convert string to array for field: {field}")
                    raise ValueError(f"Invalid array format for field: {field}")
        
        # Fix objects
        for field in object_fields:
            if field in material_data and isinstance(material_data[field], str):
                try:
                    # Try to parse string representation of object
                    material_data[field] = ast.literal_eval(material_data[field])
                    logger.warning(f"⚠️ Converted string to object for field: {field}")
                except (ValueError, SyntaxError):
                    logger.error(f"❌ Failed to convert string to object for field: {field}")
                    raise ValueError(f"Invalid object format for field: {field}")
        
        return material_data
    
    def _load_authors_data(self):
        """Load authors data from JSON file - FAIL if unable"""
        authors_file = Path(self.config.get("authors_file", "prompts/authors/authors.json"))
        
        if not authors_file.exists():
            raise FileNotFoundError(f"Authors file not found: {authors_file}")
        
        try:
            with open(authors_file, 'r', encoding='utf-8') as f:
                authors = json.load(f)
            
            if not authors:
                raise ValueError("Authors file is empty")
                
            logger.info(f"✅ Loaded {len(authors)} authors from {authors_file}")
            return authors
            
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse authors JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load authors file: {e}")
    
    def _get_author_data(self, author_id):
        """Get author data by ID - FAIL if not found"""
        # Find author by ID
        for author in self.authors_data:
            if author.get("id") == author_id:
                # Validate required author fields
                required_fields = ["name", "slug", "image", "title", "country"]
                missing_fields = [field for field in required_fields if not author.get(field)]
                
                if missing_fields:
                    raise ValueError(f"Author {author_id} missing required fields: {missing_fields}")
                
                logger.info(f"✅ Found author: {author['name']} (ID: {author_id})")
                return author
        
        # FAIL if author not found
        raise ValueError(f"Author ID {author_id} not found in authors database")