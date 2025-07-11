{
  "name": "region",
  "version": "1.0",
  "schemaType": "RegionProfile",
  
  "generatorConfig": {
    "tags": {
      "includeCountries": true,
      "includeIndustries": true,
      "primaryKeywords": ["regional profile", "manufacturing region"]
    },
    "jsonld": {
      "schemaType": "Place",
      "includeGeo": true,
      "includeIndustries": true
    },
    "metadata": {
      "includeDescription": true,
      "includeLocation": true
    }
  },

  "sections": {
    "overview": {
      "required": true,
      "prompt": "Write a comprehensive overview of the {subject} region. Include geographical location, industrial significance, and economic importance. Focus on factual information and keep it concise but informative (200-250 words)."
    },
    "economy": {
      "required": true,
      "prompt": "Describe the economic landscape of the {subject} region, including key industries, GDP contributions, trade relationships, and manufacturing centers. Include specific data points where available."
    },
    "industries": {
      "required": true,
      "prompt": "Explain the major industries in the {subject} region, with special focus on manufacturing, technology, and industrial applications. Include notable companies, manufacturing zones, and industrial parks where applicable."
    },
    "infrastructure": {
      "required": true,
      "prompt": "Detail the infrastructure supporting industry in the {subject} region, including transportation networks, power generation, industrial facilities, and technology infrastructure."
    },
    "workforce": {
      "required": true,
      "prompt": "Describe the workforce characteristics of the {subject} region, including skill levels, education, labor costs, and specializations relevant to manufacturing and industrial applications."
    }
  },

  "regionProfile": {
    "name": {
      "type": "string",
      "required": true,
      "description": "Name of the region"
    },
    "description": {
      "type": "string",
      "required": true,
      "description": "Overview of the region"
    },
    "countries": {
      "type": "array",
      "items": {"type": "string"},
      "required": true,
      "description": "Countries within the region"
    },
    "keywords": {
      "type": "array",
      "items": {"type": "string"},
      "required": true,
      "description": "Keywords for SEO, tagging, and JSON-LD"
    },
    "economicData": {
      "type": "object",
      "required": true,
      "properties": {
        "gdp": {
          "type": "string",
          "required": false,
          "description": "GDP of the region"
        },
        "majorIndustries": {
          "type": "array",
          "items": {"type": "string"},
          "required": true,
          "description": "Major industries in the region"
        }
      }
    },
    "manufacturingCenters": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string", "required": true},
          "description": {"type": "string", "required": true}
        }
      },
      "required": true,
      "description": "Major manufacturing centers in the region"
    },
    "contentManagement": {
      "type": "object",
      "required": true,
      "properties": {
        "articleType": {"type": "string", "required": true, "default": "region-profile"},
        "publishedAt": {"type": "string", "format": "date", "required": false},
        "lastUpdated": {"type": "string", "format": "date", "required": false}
      }
    }
  },

  "jsonLD": {
    "@type": "Place",
    "requiredProperties": [
      "name",
      "description"
    ],
    "recommendedProperties": [
      "geo",
      "containsPlace",
      "mainEntityOfPage"
    ]
  },

  "validation": {
    "requiredSections": [
      "Overview",
      "Economy",
      "Industries",
      "Infrastructure",
      "Workforce"
    ],
    "jsonLD": {
      "@type": "Place",
      "requiredProperties": [
        "name",
        "description"
      ],
      "recommendedProperties": [
        "geo",
        "containsPlace",
        "mainEntityOfPage"
      ]
    }
  }
}