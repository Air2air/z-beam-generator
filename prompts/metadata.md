You are an AI tasked with generating a JSON metadata file for a technical article about laser cleaning of a specified material, {{materialType}}, wrapped in an `<xaiArtifact>` tag. The JSON is tailored to the material provided via inputs and designed for article generation with Markdown content output. Use the following inputs to create the JSON:

- materialType: "{{materialType}}" // The type of material from PRIMARY USER SETTINGS
- authorId: {{authorId}} // The ID of the author from PRIMARY USER SETTINGS
- articleType: "{{articleType}}" // The type of article from PRIMARY USER SETTINGS

Based on these inputs, generate a comprehensive JSON object with the following requirements:

1. The JSON describes an article titled "Laser Cleaning {{materialType}}", focusing on laser cleaning of the specified material for applications in relevant industries (e.g., aerospace, construction, restoration).
2. Include exactly the following 35 metadata fields (34 original fields plus `generalClassifier`) with the specified instructions, substituting {{materialType}} with the input `materialType` where applicable. For each field, research and validate values using scientific literature, industry standards, or reliable sources (e.g., NIST, MatWeb, ASTM standards, laser cleaning studies). For non-elemental or composite materials (e.g., Stone, Wood), use representative values (e.g., granite for Stone) and set `atomicNumber` and `chemicalSymbol` to null. If specific data is unavailable, use reasonable estimates based on similar materials and note the assumption.
   - **title**: Set to "Laser Cleaning {{materialType}}" (string, e.g., "Laser Cleaning Aluminum").
   - **contentCategory**: Use the input `articleType` (string, e.g., "laser_cleaning", "material", "region", "application").
   - **nameShort**: Set to the input `materialType` (string, e.g., "Aluminum").
   - **description**: Set to "Explore how laser cleaning removes contaminants from {{materialType}}, enhancing performance and safety in relevant industries such as Aerospace, Construction, Restoration, Manufacturing, or others." (string, substituting {{materialType}}).
   - **publishedAt**: Set to "2025-07-01" (string, YYYY-MM-DD format, fixed publication date).
   - **authorId**: Use the input `authorId` (integer, e.g., 3).
   - **tags**: An array of strings including ["Laser Cleaning", "Aerospace", "Construction", "Manufacturing", "Restoration"] plus copies of all values from `safetyConsiderations`, `processingChallenges`, `applications`, `industryStandards`, `alternativeMethods`, `costFactors`, `relatedMaterials`, and `regulatoryCompliance`. Long tag names should be shortened to concise, human-readable versions (e.g., "Restoration of historical monuments" becomes "Historical Restoration") while remaining suitable for SEO and website rendering.
   - **image**: Set to "/images/Material/material_{materialType | lowercase}.jpg" (string, file path with {materialType} in lowercase, e.g., "/images/Material/material_aluminum.jpg"). Validate as a plausible path convention.
   - **atomicNumber**: For elemental materials, research the atomic number from the periodic table (e.g., 13 for Aluminum). For non-elemental materials (e.g., Quartzite), set to null. Use integer or null format.
   - **chemicalSymbol**: For elemental materials, research the chemical symbol from the periodic table (e.g., "Al" for Aluminum). For non-elemental materials, set to null. Use string or null format.
   - **materialType**: Use the input `materialType` (string, e.g., "Aluminum").
   - **generalClassifier**: Dynamically set based on materialType: "metal" for elemental metals (e.g., Aluminum), "stone" for Stone, Quartzite, or Masonry, "wood" for Wood, "polymer" for Plastics and Composites. Use string format (e.g., "metal" for Aluminum).
   - **materialClass**: Research the material's classification (e.g., "Light Metal" for Aluminum, "Natural Stone" for Quartzite, "Organic" for Wood). Use string format.
   - **crystalStructure**: For crystalline materials, research the crystal structure at room temperature (e.g., "Face-centered cubic" for Aluminum). For non-crystalline or composite materials, set to "Amorphous" or "Mixed". Use string format.
   - **density**: Research the material's density at room temperature (e.g., 2.70 g/cm³ for Aluminum). Use string format with units (g/cm³). For composites, use a representative value or range.
   - **meltingPoint**: Research the material's melting point (e.g., 660°C for Aluminum). For non-melting materials (e.g., Wood), set to "N/A" or describe the decomposition temperature. Use string format with units (°C) or description.
   - **thermalConductivity**: Research the material's thermal conductivity at room temperature (e.g., 205 W/(m·K) for Aluminum). Use string format with units (W/(m·K)). For composites, use a representative value.
   - **reflectivityIr**: Research the material's infrared reflectivity at a standard wavelength (e.g., 90-95% for Aluminum at 10.6 µm). Use string format with percentage. If unavailable, estimate based on material properties.
   - **reflectivityWavelength**: Set to the wavelength used for `reflectivityIr` (e.g., "10.6 µm", typical for CO2 lasers). Use string format with units (µm). Validate with laser processing literature.
   - **hardnessMohs**: Research the material's Mohs hardness (e.g., 2.75 for Aluminum). For soft materials, use a range or estimate. Use number format.
   - **youngsModulus**: Research the material's Young's modulus (e.g., 70 GPa for Aluminum). For flexible materials, use a lower value. Use string format with units (GPa).
   - **specificHeatCapacity**: Research the material's specific heat capacity at room temperature (e.g., 0.897 J/(g·K) for Aluminum). Use string format with units (J/(g·K)). For composites, use a representative value.
   - **applications**: Research typical applications in relevant industries (e.g., ["Aerospace components", "Automotive parts", "Construction materials"] for Aluminum). Use an array of strings in human-readable format.
   - **laserCleaningParameters**: Research laser cleaning parameters optimized for the material, referencing studies or industry practices. Use an object with the following fields:
     - **wavelength**: Research a suitable laser wavelength (e.g., 1064 nm for Aluminum). Use string format with units (nm).
     - **pulseDuration**: Research the pulse duration (e.g., "nanoseconds" for Aluminum). Use string format.
     - **powerDensity**: Research the power density for effective cleaning without damage (e.g., 10^6–10^7 W/cm² for Aluminum). Use string format with units (W/cm²).
     - **pulseFrequency**: Research the pulse repetition rate (e.g., 10–30 kHz for Aluminum). Use string format with units (kHz) or range.
     - **scanningSpeed**: Research the beam scanning speed (e.g., 500–1500 mm/s for Aluminum). Use string format with units (mm/s) or range.
     - **spotSize**: Research the laser beam spot diameter (e.g., 0.3 mm for Aluminum). Use string format with units (mm).
     - **fluence**: Research the energy density for safe cleaning (e.g., 0.3–1.5 J/cm² for Aluminum). Use string format with units (J/cm²) or range.
     - **pulsesPerSpot**: Research the number of pulses per spot (e.g., 1–5 for Aluminum). Use string format or range.
     - **beamProfile**: Research the beam energy distribution (e.g., "Gaussian" for Aluminum). Use string format.
     - **ambientConditions**: Research the optimal cleaning environment (e.g., "Ambient air" for Aluminum). Use string format.
   - **safetyConsiderations**: Research safety concerns for laser cleaning the material (e.g., ["Laser radiation protection", "Metal vapor exposure", "Fire hazard"] for Aluminum). Use an array of strings in human-readable format.
   - **industryStandards**: Research relevant standards for the material's processing (e.g., ["ASTM B209", "ISO 14001", "AWS D1.2"] for Aluminum). Use an array of strings.
   - **environmentalImpact**: Research the material's environmental impact during laser cleaning (e.g., "Minimal impact, vapor management required" for Aluminum). Use string format.
   - **processingChallenges**: Research challenges in laser cleaning the material (e.g., ["High reflectivity", "Thermal conductivity", "Oxide layer formation"] for Aluminum). Use an array of strings in human-readable format.
   - **alternativeMethods**: Set to an array of strings: ["Chemical etching", "Mechanical polishing", "Ultrasonic cleaning"] (fixed, common alternatives for cleaning).
   - **performanceMetrics**: Research typical performance metrics for laser cleaning the material. Use an object with the following fields:
     - **contaminantRemovalEfficiency**: Research the cleaning effectiveness (e.g., "98%" for Aluminum). Use string format with percentage.
     - **surfaceRoughnessReduction**: Research the improvement in surface smoothness (e.g., "0.2 µm" for Aluminum). Use string format with units (µm).
     - **processingTime**: Research the typical cleaning duration (e.g., "seconds" for Aluminum). Use string format.
   - **materialPurity**: Research the typical industrial purity (e.g., "99.5%" for Aluminum). Use string format.
   - **costFactors**: Set to an array of strings: ["Equipment investment", "Energy consumption", "Safety compliance"] (fixed, common for laser cleaning).
   - **lastUpdated**: Set to "2025-07-08" (string, YYYY-MM-DD format, today's date).
   - **relatedMaterials**: Research materials commonly used alongside the input material (e.g., ["Steel", "Copper", "Titanium"] for Aluminum). Use an array of strings.
   - **regulatoryCompliance**: Research regulations governing the material's handling (e.g., ["OSHA Metal Dust Standards", "EPA Air Quality Guidelines"] for Aluminum). Use an array of strings in human-readable format.
3. Ensure the `materialType`, `authorId`, and `articleType` inputs are used as specified from PRIMARY USER SETTINGS.
4. Do not include a `targetAudience` field, `researchReferences` field, or any other fields beyond the 35 listed above.
5. For the materialType input, research and validate values using scientific literature (e.g., NIST, MatWeb) or industry sources. If data is unavailable, estimate and justify based on similar materials.
6. Wrap the JSON in an `<xaiArtifact>` tag with:
   - artifact_id: "3abf1ab9-000d-455d-aa26-602a37b335c7" (fixed, matching previous artifact).
   - title: "{materialType | lowercase}_metadata.json" (e.g., "aluminum_metadata.json").
   - contentType: "application/json".
7. Ensure the JSON is syntactically correct, well-organized (group related fields, e.g., material properties together), and free of duplicate fields.
8. The JSON will be used with Markdown content output for article generation, so ensure fields like `title`, `description`, `tags`, and `image` are suitable for website rendering and SEO based on the `articleType` setting.

**CRITICAL OUTPUT FORMAT:**
Return ONLY the JSON wrapped in the <xaiArtifact> tags. Do not include any explanatory text, introductory sentences, markdown code blocks, or additional formatting. Your response must start immediately with the <xaiArtifact> tag and end with the closing </xaiArtifact> tag.

Expected format:
<xaiArtifact artifact_id="3abf1ab9-000d-455d-aa26-602a37b335c7" title="{{materialType | lower | replace(' ', '_')}}_metadata.json" contentType="application/json">
{
  "title": "Laser Cleaning {{materialType}}",
  "contentCategory": "{{articleType}}",
  "nameShort": "{{materialType}}",
  // ... all 35 fields as specified above ...
}
</xaiArtifact>

DO NOT include any text before the <xaiArtifact> tag or after the </xaiArtifact> tag. Return only the artifact.

