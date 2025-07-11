# Tag Generation Prompt for Laser Cleaning Materials

Generate 12-15 focused, SEO-optimized hashtags for laser cleaning **{material}** content.

## Context:
- **Material**: {material}
- **Author**: {author_name} ({author_country})
- **Article Type**: {article_type}
- **Target Audience**: Industrial engineers, manufacturing professionals, laser technicians

## Tag Categories Required:

### 1. Material-Specific Tags (3-4 tags)
- Material name: #{material_title}
- Material class: #{material_class}
- Chemical symbol: #{chemical_symbol}Element
- Related materials: #{related_materials}

### 2. Application Tags (3-4 tags)
Based on material applications:
- Industry-specific: #Nuclear, #Aerospace, #Medical, #Automotive, #Electronics
- Process-specific: #ReactorComponents, #TurbineBlades, #MedicalImplants
- Use case: #PrecisionCleaning, #SurfacePreparation, #ContaminantRemoval

### 3. Technical Property Tags (2-3 tags)
- #HardMaterials (if Mohs > 6)
- #HighTemperature (if melting point > 1000°C)
- #CorrosionResistant (if applicable)
- #Conductive, #Magnetic, #Ceramic, #Polymer (as appropriate)

### 4. Process Tags (2-3 tags)
- #LaserCleaning (always include)
- #SurfacePreparation (always include)
- #IndustrialCleaning
- #NonAbrasiveCleaning

### 5. Industry Tags (2-3 tags)
- #Manufacturing
- #QualityControl
- #SustainableCleaning
- #PrecisionEngineering

## Format Requirements:
- Return ONLY hashtags, no explanations
- Use PascalCase (e.g., #LaserCleaning, not #laser_cleaning)
- No spaces in hashtags
- Separate tags with commas
- Maximum 15 tags total

## Example Output Format:
#Hafnium, #TransitionMetal, #HfElement, #Nuclear, #ReactorComponents, #Aerospace, #HardMaterials, #HighTemperature, #LaserCleaning, #SurfacePreparation, #ContaminantRemoval, #Manufacturing, #PrecisionEngineering, #IndustrialCleaning, #QualityControl

Generate hashtags for **{material}** laser cleaning now: