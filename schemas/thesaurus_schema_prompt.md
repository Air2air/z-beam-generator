```yaml
schemaVersion: "1.0"
schemaType: "LaserCleaningThesaurusProfile"
termProfile:
  # Core term information
  term: "{{term}}" # Placeholder for dynamic term name
  definition:
    type: string
    description: "Technical definition of the term in the context of laser cleaning"
    example: "Fluence is the energy delivered per unit area by a laser beam, measured in J/cm², critical for controlling ablation in laser cleaning."
  pronunciation:
    type: string
    description: "Phonetic pronunciation of the term"
    example: "/ˈfluːəns/"
  partOfSpeech:
    type: string
    description: "Part of speech (e.g., noun, verb)"
    example: "Noun"
  primaryAudience:
    type: string
    description: "Primary target audience for the term"
    example: "Materials Engineers"
  secondaryAudience:
    type: string
    description: "Secondary target audience for the term"
    example: "Technicians"

  # Contextual usage
  usage:
    type: object
    properties:
      description:
        type: string
        description: "Explanation of how the term is used in laser cleaning"
        example: "In laser cleaning, {{term}} determines the energy intensity applied to remove contaminants from surfaces like cobalt or steel, requiring precise calibration to avoid substrate damage."
      industries:
        type: array
        items:
          type: string
        description: "Industries where the term is relevant"
        example: ["Aerospace", "Automotive", "Manufacturing"]
      applications:
        type: array
        items:
          type: string
        description: "Laser cleaning applications where the term is used"
        example: ["Powder Coating Removal", "Rust Removal", "Surface Preparation"]
      materials:
        type: array
        items:
          type: string
        description: "Materials where the term is relevant"
        example: ["Cobalt", "Steel", "Aluminum"]

  # Synonyms and related terms
  synonyms:
    type: array
    items:
      type: string
    description: "Synonyms or near-synonyms for the term"
    example: ["Energy Density", "Irradiance"]
  relatedTerms:
    type: array
    items:
      type: object
      properties:
        term:
          type: string
          description: "Related term"
          example: "Pulse Duration"
        description:
          type: string
          description: "Explanation of the relationship"
          example: "Pulse duration affects {{term}} by determining the time over which energy is delivered, impacting cleaning efficiency."
      example:
        - term: "Pulse Duration"
          description: "Pulse duration affects {{term}} by determining the time over which energy is delivered, impacting cleaning efficiency."
        - term: "Wavelength"
          description: "Wavelength influences {{term}} absorption by the material, critical for optimizing cleaning outcomes."

  # Technical metrics
  technicalMetrics:
    type: object
    properties:
      description:
        type: string
        description: "Overview of technical metrics associated with the term"
        example: "{{term}} values in laser cleaning typically range from 1.0–4.6 J/cm², optimized for different substrates and applications."
      metrics:
        type: array
        items:
          type: object
          properties:
            name:
              type: string
              description: "Name of the metric"
              example: "{{term}} Range"
            unit:
              type: string
              description: "Unit of measurement"
              example: "J/cm²"
            typicalValues:
              type: string
              description: "Typical range or value for the metric"
              example: "2.2–2.6 J/cm²"
            optimalContext:
              type: string
              description: "Context for optimal values"
              example: "Optimal for powder coating removal on steel"
        example:
          - name: "{{term}} Range"
            unit: "J/cm²"
            typicalValues: "2.2–2.6 J/cm²"
            optimalContext: "Optimal for powder coating removal on steel"
          - name: "{{term}} for Cobalt"
            unit: "J/cm²"
            typicalValues: "1.0–2.0 J/cm²"
            optimalContext: "Prevents thermal damage in medical implants"
      dataSource:
        type: string
        description: "Source of technical metrics"
        example: "Optics & Laser Technology, 2023"
      chartConfig:
        type: object
        properties:
          type:
            type: string
            description: "Type of chart for visualization"
            example: "bar"
          dataSource:
            type: string
            description: "Source of chart data"
            example: "Industry testing reports, 2024"
        example:
          type: "bar"
          dataSource: "Industry testing reports, 2024"

  # Practical considerations
  considerations:
    type: array
    items:
      type: object
      properties:
        consideration:
          type: string
          description: "Name of the practical consideration"
          example: "Parameter Sensitivity"
        description:
          type: string
          description: "Description of the consideration"
          example: "Incorrect {{term}} settings may cause incomplete cleaning or substrate damage, requiring precise calibration."
      example:
        - consideration: "Parameter Sensitivity"
          description: "Incorrect {{term}} settings may cause incomplete cleaning or substrate damage, requiring precise calibration."
        - consideration: "Operator Expertise"
          description: "Adjusting {{term}} requires trained operators to optimize for material and application."

  # Safety and regulatory considerations
  safetyConsiderations:
    type: array
    items:
      type: string
    description: "Safety requirements related to the term in laser cleaning"
    example:
      - "Ensure proper {{term}} calibration to avoid excessive heat exposure"
      - "Mandatory laser-safe goggles when adjusting {{term}} settings"

  regulatoryStandards:
    type: array
    items:
      type: string
    description: "Industry standards relevant to the term"
    example: ["ANSI Z136.1", "OSHA 1910.147"]

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
        example: "thesaurus-profile"
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
        example: "2025-07-10T21:03:00.000000Z"
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
          example: "Understanding {{term}} in Powder Coating Removal"
        url:
          type: string
          description: "URL of related content"
          example: "https://example.com/articles/powder-coating-removal-fluence"
        type:
          type: string
          description: "Type of related content"
          example: "article"
```