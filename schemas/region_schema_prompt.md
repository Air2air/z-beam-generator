```yaml
schemaVersion: "1.0"
schemaType: "CityLaserCleaningProfile"
cityProfile:
  # Core city information
  cityName: "{{cityName}}" # Placeholder for dynamic city name
  stateOrRegion:
    type: string
    description: "State, province, or region where the city is located"
    example: "California"
  country:
    type: string
    description: "Country where the city is located"
    example: "United States"
  coordinates:
    latitude:
      type: number
      description: "Geographic latitude of the city"
      example: 37.5202
    longitude:
      type: number
      description: "Geographic longitude of the city"
      example: -122.2757
  population:
    type: integer
    description: "Approximate population of the city"
    example: 27000
  economicOverview:
    type: string
    description: "Brief description of the city's economic base and industrial significance"
    example: "A balanced mix of residential, commercial, and industrial zones, with a focus on sustainability and technology-driven industries."

  # Land use distribution
  landUseDistribution:
    type: object
    properties:
      description:
        type: string
        description: "Overview of the city's land use zoning"
        example: "Belmont’s land is allocated across residential, commercial, retail, industrial, and institutional zones, with industrial and commercial sectors driving laser cleaning demand."
      categories:
        type: array
        items:
          type: object
          properties:
            name:
              type: string
              description: "Name of the land use category"
              example: "Industrial"
            percentage:
              type: number
              description: "Percentage of total land use"
              example: 30
        example:
          - name: "Industrial"
            percentage: 30
          - name: "Commercial"
            percentage: 25
          - name: "Residential"
            percentage: 35
          - name: "Retail"
            percentage: 7
          - name: "Institutional"
            percentage: 3
      chartConfig:
        type: object
        properties:
          type:
            type: string
            description: "Type of chart for visualization"
            example: "pie"
          dataSource:
            type: string
            description: "Source of the land use data"
            example: "City of Belmont Planning Department, 2024"
        example:
          type: "pie"
          dataSource: "City of Belmont Planning Department, 2024"

  # Laser cleaning applications specific to the city
  laserCleaningApplications:
    type: array
    items:
      type: object
      properties:
        applicationName:
          type: string
          description: "Name of the laser cleaning application"
          example: "Rust Removal"
        description:
          type: string
          description: "Description of how the application is used in the city"
          example: "Used in {{cityName}}’s industrial parks to remove rust from heavy machinery, ensuring operational efficiency."
        industries:
          type: array
          items:
            type: string
          description: "Industries in the city using this application"
          example: ["Manufacturing", "Industrial Maintenance"]
        materials:
          type: array
          items:
            type: string
          description: "Materials commonly cleaned with this application in the city"
          example: ["Steel", "Iron"]
        benefits:
          type: array
          items:
            type: string
          description: "Benefits of this application in the city's context"
          example:
            ["Enhanced equipment longevity", "Compliance with environmental regulations"]

  # Cleaning efficiency metrics
  efficiencyMetrics:
    type: object
    properties:
      description:
        type: string
        description: "Overview of laser cleaning efficiency in the city"
        example: "Laser cleaning in {{cityName}} achieves high efficiency for rust, paint, and oil removal, adhering to ASTM D7091 standards."
      substrates:
        type: array
        items:
          type: object
          properties:
            substrate:
              type: string
              description: "Substrate type"
              example: "Rust"
            efficiency:
              type: number
              description: "Efficiency percentage for contaminant removal"
              example: 95
        example:
          - substrate: "Rust"
            efficiency: 95
          - substrate: "Paint"
            efficiency: 90
          - substrate: "Oil"
            efficiency: 92
      standards:
        type: array
        items:
          type: string
        description: "Standards used to measure efficiency"
        example: ["ASTM D7091"]
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

  # Industries in the city utilizing laser cleaning
  industries:
    type: array
    items:
      type: object
      properties:
        industryName:
          type: string
          description: "Name of the industry"
          example: "Manufacturing"
        description:
          type: string
          description: "Role of laser cleaning in this industry within the city"
          example: "In {{cityName}}, manufacturing facilities use laser cleaning for machinery maintenance and surface preparation."
        keyCompanies:
          type: array
          items:
            type: string
          description: "Major companies in the city using laser cleaning in this industry"
          example: ["Belmont Industrial Co.", "TechMach Inc."]
        economicImpact:
          type: string
          description: "Economic significance of laser cleaning in this industry"
          example: "Supports $200M in annual production value in {{cityName}}."

  # Cost comparison
  costComparison:
    type: object
    properties:
      description:
        type: string
        description: "Overview of cost comparisons for cleaning methods"
        example: "Laser cleaning in {{cityName}} offers long-term savings compared to sandblasting and chemical cleaning, despite higher initial costs."
      methods:
        type: array
        items:
          type: object
          properties:
            method:
              type: string
              description: "Cleaning method"
              example: "Laser Cleaning"
            initialCost:
              type: number
              description: "Initial cost in USD"
              example: 50000
            longTermCost:
              type: number
              description: "Long-term cost in USD per year"
              example: 10000
        example:
          - method: "Laser Cleaning"
            initialCost: 50000
            longTermCost: 10000
          - method: "Sandblasting"
            initialCost: 20000
            longTermCost: 25000
          - method: "Chemical Cleaning"
            initialCost: 15000
            longTermCost: 30000
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
            example: "Industry reports, 2024"
        example:
          type: "bar"
          dataSource: "Industry reports, 2024"

  # Case studies
  caseStudies:
    type: array
    items:
      type: object
      properties:
        title:
          type: string
          description: "Title of the case study"
          example: "{{cityName}} Industrial Park Restoration"
        description:
          type: string
          description: "Description of the case study"
          example: "A 2024 project in {{cityName}} used laser cleaning to restore machinery, achieving 95% contaminant removal with minimal downtime."
        year:
          type: integer
          description: "Year of the case study"
          example: 2024
        equipment:
          type: string
          description: "Equipment used in the case study"
          example: "1000W Fiber Laser"
        outcomes:
          type: array
          items:
            type: string
          description: "Key outcomes of the case study"
          example:
            ["95% contaminant removal", "40% reduction in downtime"]
        standards:
          type: array
          items:
            type: string
          description: "Standards applied in the case study"
          example: ["ASTM D7091"]

  # Regional advantages
  regionalAdvantages:
    type: array
    items:
      type: object
      properties:
        advantage:
          type: string
          description: "Name of the regional advantage"
          example: "Industrial Hub"
        description:
          type: string
          description: "Description of the advantage"
          example: "{{cityName}}’s 30% industrial land use drives demand for laser cleaning in machinery maintenance."
      example:
        - advantage: "Industrial Hub"
          description: "{{cityName}}’s 30% industrial land use drives demand for laser cleaning in machinery maintenance."
        - advantage: "Sustainability Incentives"
          description: "Local grants support adoption of eco-friendly technologies like laser cleaning."

  # Local innovations
  localInnovations:
    type: array
    items:
      type: object
      properties:
        innovation:
          type: string
          description: "Name of the innovation"
          example: "Portable Laser Units"
        description:
          type: string
          description: "Description of the innovation"
          example: "Compact laser systems developed in {{cityName}} for mobile cleaning applications."
      example:
        - innovation: "Portable Laser Units"
          description: "Compact laser systems developed in {{cityName}} for mobile cleaning applications."
        - innovation: "AI Integration"
          description: "Smart sensors optimize cleaning parameters for {{cityName}}’s industrial needs."

  # Adoption trends
  adoptionTrends:
    type: object
    properties:
      description:
        type: string
        description: "Overview of laser cleaning adoption trends"
        example: "Laser cleaning adoption in {{cityName}} has grown 15% annually from 2024–2025, driven by industrial demand."
      growthRate:
        type: number
        description: "Annual growth rate in adoption (percentage)"
        example: 15
      years:
        type: array
        items:
          type: object
          properties:
            year:
              type: integer
              description: "Year of adoption data"
              example: 2024
            adoptionLevel:
              type: number
              description: "Adoption level (e.g., percentage of industries using)"
              example: 20
        example:
          - year: 2024
            adoptionLevel: 20
          - year: 2025
            adoptionLevel: 23
      chartConfig:
        type: object
        properties:
          type:
            type: string
            description: "Type of chart for visualization"
            example: "line"
          dataSource:
            type: string
            description: "Source of adoption data"
            example: "Industry reports, 2024–2025"
        example:
          type: "line"
          dataSource: "Industry reports, 2024–2025"

  # Future outlook
  futureOutlook:
    type: array
    items:
      type: object
      properties:
        trend:
          type: string
          description: "Name of the future trend"
          example: "Expanded Applications"
        description:
          type: string
          description: "Description of the trend"
          example: "Laser cleaning in {{cityName}} will extend to residential and institutional zones by 2030."
      example:
        - trend: "Expanded Applications"
          description: "Laser cleaning in {{cityName}} will extend to residential and institutional zones by 2030."
        - trend: "Cost Reductions"
          description: "Economies of scale will lower laser cleaning equipment costs in {{cityName}}."

  # Technical laser cleaning parameters
  laserCleaningParameters:
    type: object
    properties:
      energyDensity:
        type: number
        description: "Typical energy density used (J/cm²)"
        example: 1.2
      pulseDuration:
        type: number
        description: "Pulse duration in nanoseconds"
        example: 12
      repetitionRate:
        type: number
        description: "Repetition rate in Hz"
        example: 1200
      wavelength:
        type: number
        description: "Laser wavelength in nanometers"
        example: 1064
      equipmentTypes:
        type: array
        items:
          type: string
        description: "Types of laser cleaning equipment commonly used in the city"
        example: ["Fiber Lasers", "Pulsed Nd:YAG Lasers"]

  # Safety and regulatory considerations
  safetyConsiderations:
    type: object
    properties:
      general:
        type: array
        items:
          type: string
        description: "General safety requirements for laser cleaning"
        example:
          ["Mandatory laser-safe goggles", "OSHA-compliant technician training", "Ventilation systems for vaporized contaminants"]
      regionSpecific:
        type: array
        items:
          type: string
        description: "Region-specific safety considerations"
        example:
          ["Dust management due to {{cityName}}’s dry climate"]

  regulatoryStandards:
    type: array
    items:
      type: string
    description: "Industry standards and regulations applicable in the city"
    example: ["ISO 9001:2015", "OSHA 1910.147", "California Environmental Regulations"]

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
        example: "city-profile"
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
        example: "2025-07-10T20:11:12.721302Z"
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
          example: "Laser Cleaning in Silicon Valley: Regional Impact"
        url:
          type: string
          description: "URL of related content"
          example: "https://example.com/articles/laser-cleaning-silicon-valley"
        type:
          type: string
          description: "Type of related content"
          example: "article"
```