```yaml
schemaVersion: "1.0"
schemaType: "LaserCleaningMaterialProfile"
materialProfile:
  # Core material information
  materialName: "{{materialName}}" # Placeholder for dynamic material name
  description:
    type: string
    description: "Overview of laser cleaning for the material"
    example: "Laser cleaning of {{materialName}} removes oxides and residues, preserving structural integrity and biocompatibility for aerospace and medical applications."
  materialClass:
    type: string
    description: "Class of the material (e.g., Metal, Alloy)"
    example: "Metal"
  materialType:
    type: string
    description: "Type of material (e.g., General, Specialized)"
    example: "Specialized"
  primaryAudience:
    type: string
    description: "Primary target audience for the material"
    example: "Materials Engineers"
  secondaryAudience:
    type: string
    description: "Secondary target audience for the material"
    example: "Technicians"
  industries:
    type: array
    items:
      type: string
    description: "Industries where the material is commonly cleaned"
    example: ["Aerospace", "Medical Implants", "High-Performance Alloys"]

  # Material substrates
  substrates:
    type: array
    items:
      type: object
      properties:
        substrateName:
          type: string
          description: "Name of the substrate or material variant"
          example: "Pure {{materialName}}"
        properties:
          type: array
          items:
            type: string
          description: "Key properties of the substrate"
          example: ["High hardness (5.0 Mohs)", "Magnetic"]
        cleaningConsiderations:
          type: string
          description: "Specific considerations for cleaning the substrate"
          example: "Use short pulses to avoid thermal cracking"
      example:
        - substrateName: "Pure {{materialName}}"
          properties: ["High hardness (5.0 Mohs)", "Magnetic"]
          cleaningConsiderations: "Use short pulses to avoid thermal cracking"
        - substrateName: "{{materialName}}-Chromium Alloys"
          properties: ["Corrosion-resistant", "High strength"]
          cleaningConsiderations: "Adjust wavelength for alloy absorption"
        - substrateName: "Stellite ({{materialName}}-Based)"
          properties: ["Extreme wear resistance", "High melting point"]
          cleaningConsiderations: "High scan speed to reduce heat-affected zones"

  # Successful cleaning outcomes
  outcomes:
    type: array
    items:
      type: object
      properties:
        outcome:
          type: string
          description: "Name of the outcome"
          example: "Effective Contaminant Removal"
        description:
          type: string
          description: "Description of the outcome"
          example: "Achieves 98% removal of oxides and residues from {{materialName}}, ensuring consistency."
      example:
        - outcome: "Effective Contaminant Removal"
          description: "Achieves 98% removal of oxides and residues from {{materialName}}, ensuring consistency."
        - outcome: "Substrate Integrity"
          description: "Preserves {{materialName}}’s surface hardness and biocompatibility, critical for medical implants."
        - outcome: "Eco-Friendly Process"
          description: "Eliminates chemical solvents, reducing environmental footprint for {{materialName}} cleaning."

  # Challenges
  challenges:
    type: array
    items:
      type: object
      properties:
        challenge:
          type: string
          description: "Name of the challenge"
          example: "Oxide Layer Tenacity"
        description:
          type: string
          description: "Description of the challenge"
          example: "{{materialName}}’s oxide films resist removal, requiring higher pulse energies and precise wavelengths."
      example:
        - challenge: "Oxide Layer Tenacity"
          description: "{{materialName}}’s oxide films resist removal, requiring higher pulse energies and precise wavelengths."
        - challenge: "Thermal Sensitivity"
          description: "Excessive heat risks microcracking in {{materialName}}, mitigated by real-time thermal monitoring."
        - challenge: "Calibration Precision"
          description: "Laser alignment errors reduce efficiency for {{materialName}}, necessitating skilled operators."

  # Cleaning efficiency comparison
  cleaningEfficiencyComparison:
    type: object
    properties:
      description:
        type: string
        description: "Overview of cleaning efficiency comparison"
        example: "Laser cleaning of {{materialName}} achieves up to 12 m²/hour, surpassing traditional methods in speed and precision."
      methods:
        type: array
        items:
          type: object
          properties:
            method:
              type: string
              description: "Cleaning method"
              example: "Laser Cleaning"
            efficiency:
              type: string
              description: "Efficiency range (e.g., m²/hour)"
              example: "10–15 m²/hour"
        example:
          - method: "Laser Cleaning"
            efficiency: "10–15 m²/hour"
          - method: "Abrasive Blasting"
            efficiency: "5–8 m²/hour"
          - method: "Chemical Cleaning"
            efficiency: "4–7 m²/hour"
          - method: "Manual Cleaning"
            efficiency: "2–4 m²/hour"
      chartConfig:
        type: object
        properties:
          type:
            type: string
            description: "Type of chart for visualization"
            example: "bar"
          dataSource:
            type: string
            description: "Source of efficiency data"
            example: "Industry testing reports, 2024"
        example:
          type: "bar"
          dataSource: "Industry testing reports, 2024"

  # Risks of traditional cleaning methods
  risksOfTraditionalMethods:
    type: array
    items:
      type: object
      properties:
        method:
          type: string
          description: "Traditional cleaning method"
          example: "Abrasive Blasting"
        risks:
          type: array
          items:
            type: string
          description: "Risks associated with the method for the material"
          example: ["Surface abrasion compromising {{materialName}}’s wear resistance", "Damage to biocompatibility"]
      example:
        - method: "Abrasive Blasting"
          risks: ["Surface abrasion compromising {{materialName}}’s wear resistance", "Damage to biocompatibility"]
        - method: "Chemical Cleaning"
          risks: ["Etching of {{materialName}} surfaces", "Residue interference with coating adhesion"]
        - method: "Manual Scraping"
          risks: ["Scratches on {{materialName}}", "Inconsistent cleaning results"]

  # Cleaning performance metrics
  cleaningPerformanceMetrics:
    type: object
    properties:
      description:
        type: string
        description: "Overview of performance metrics for the material"
        example: "Performance metrics for {{materialName}} ensure efficient cleaning with minimal thermal damage."
      metrics:
        type: array
        items:
          type: object
          properties:
            name:
              type: string
              description: "Name of the metric"
              example: "Removal Rate"
            value:
              type: string
              description: "Value or range of the metric"
              example: "10–15 m²/hour"
            consideration:
              type: string
              description: "Consideration for applying the metric"
              example: "Varies with oxide thickness"
        example:
          - name: "Removal Rate"
            value: "10–15 m²/hour"
            consideration: "Varies with oxide thickness"
          - name: "Pulse Energy"
            value: "0.8–2.5 mJ"
            consideration: "Lower for coatings"
          - name: "Wavelength"
            value: "1064 nm"
            consideration: "Matches {{materialName}} absorption"
          - name: "Scan Speed"
            value: "6–12 mm/s"
            consideration: "Adjust for geometry"
          - name: "Heat-Affected Zone"
            value: "<0.08 mm"
            consideration: "Critical for precision parts"
      dataSource:
        type: string
        description: "Source of performance metrics"
        example: "Materials Science Reports, 2023"

  # Cost comparison
  costComparison:
    type: object
    properties:
      description:
        type: string
        description: "Overview of cost comparison for cleaning methods"
        example: "Laser cleaning of {{materialName}} offers lower long-term costs compared to traditional methods, despite higher upfront expenses."
      methods:
        type: array
        items:
          type: object
          properties:
            method:
              type: string
              description: "Cleaning method"
              example: "Laser Cleaning"
            cost:
              type: string
              description: "Cost range in USD per square meter"
              example: "$15–25/m²"
        example:
          - method: "Laser Cleaning"
            cost: "$15–25/m²"
          - method: "Abrasive Blasting"
            cost: "$30–50/m²"
          - method: "Chemical Cleaning"
            cost: "$25–40/m²"
          - method: "Manual Cleaning"
            cost: "$35–60/m²"
      chartConfig:
        type: object
        properties:
          type:
            type: string
            description: "Type of chart for visualization"
            example: "bar"
          dataSource:
            type: string
            description: "Source of cost data"
            example: "Surface Engineering Journal, 2022"
        example:
          type: "bar"
          dataSource: "Surface Engineering Journal, 2022"

  # Laser cleaning parameters
  laserCleaningParameters:
    type: object
    properties:
      energyDensity:
        type: number
        description: "Typical energy density used (J/cm²)"
        example: 1.0
      pulseDuration:
        type: number
        description: "Pulse duration in nanoseconds"
        example: 10
      repetitionRate:
        type: number
        description: "Repetition rate in Hz"
        example: 1000
      wavelength:
        type: number
        description: "Laser wavelength in nanometers"
        example: 1064
      equipmentTypes:
        type: array
        items:
          type: string
        description: "Types of laser cleaning equipment used for the material"
        example: ["Fiber Lasers", "Pulsed Nd:YAG Lasers"]

  # Safety and regulatory considerations
  safetyConsiderations:
    type: array
    items:
      type: string
    description: "Safety requirements for cleaning the material"
    example:
      - "Mandatory laser-safe goggles for operators"
      - "Ventilation systems to manage vaporized contaminants"
      - "Real-time thermal monitoring to prevent {{materialName}} damage"

  regulatoryStandards:
    type: array
    items:
      type: string
    description: "Industry standards and regulations applicable to cleaning the material"
    example: ["ISO 9001:2015", "OSHA 1910.147", "EPA Hazardous Waste Regulations"]

  # Author information
  author:
    type: object
    properties:
      authorId:
        type: string
        description: "Unique identifier for the author"
        example: "4"
      authorName:
        type: string
        description: "Full name of the author"
        example: "Ikmanda Roswati"
      authorTitle:
        type: string
        description: "Professional title of the author"
        example: "Laser Cleaning Expert"
      authorCountry:
        type: string
        description: "Country of the author"
        example: "Indonesia"
      authorImage:
        type: string
        description: "URL of the author's image"
        example: "/images/authors/ikmanda-roswati.jpg"
      authorSlug:
        type: string
        description: "Slug for the author's profile page"
        example: "ikmanda-roswati"

  # Content management information
  contentManagement:
    type: object
    properties:
      articleType:
        type: string
        description: "Type of article"
        example: "material-profile"
      publishedAt:
        type: string
        format: date
        description: "Publication date"
        example: "2025-07-10"
      lastUpdated:
        type: string
        format: date
        description: "Last update date"
        example: "2025-07-10"
      generationTimestamp:
        type: string
        format: date-time
        description: "Timestamp of content generation"
        example: "2025-07-10T20:49:19.851551Z"
      modelUsed:
        type: string
        description: "Model used for content generation"
        example: "Grok3"

  # Related content
  relatedContent:
    type: array
    items:
      type: object
      properties:
        title:
          type: string
          description: "Title of related content"
          example: "Laser Cleaning in Aerospace: Cobalt Applications"
        url:
          type: string
          description: "URL of related content"
          example: "https://example.com/articles/laser-cleaning-aerospace-cobalt"
        type:
          type: string
          description: "Type of related content"
          example: "article"
```