{
  "name": "application",
  "version": "1.0",
  "schemaType": "LaserCleaningApplicationProfile",
  
  "generatorConfig": {
    "tags": {
      "includeIndustries": true,
      "includeSubstrates": true,
      "primaryKeywords": ["laser cleaning", "surface preparation"]
    },
    "jsonld": {
      "schemaType": "TechnicalArticle",
      "includeIndustries": true,
      "includeSubstrates": true
    },
    "metadata": {
      "includeDescription": true,
      "includeAuthor": true,
      "category": "LaserApplications"
    }
  },

  "sections": {
    "overview": {
      "required": true,
      "prompt": "Write a comprehensive overview of {subject} application. Include what it is, how it works, and its primary benefits. Focus on factual information and keep it concise but informative (200-250 words)."
    },
    "parameters": {
      "required": true,
      "prompt": "Describe the key laser parameters for {subject} application, including optimal settings for scan speed, fluence, pulse duration, and power output. Include specific ranges with units and explain how each parameter affects cleaning results."
    },
    "outcomes": {
      "required": true,
      "prompt": "Explain the successful outcomes of using {subject} application, including substrate preservation, efficiency, and environmental benefits. Provide specific examples where possible."
    },
    "challenges": {
      "required": true,
      "prompt": "Discuss the main challenges associated with {subject} application, such as parameter sensitivity, equipment costs, and operator expertise requirements. Include potential solutions for each challenge."
    },
    "performance": {
      "required": true,
      "prompt": "Detail the performance metrics for {subject} application, including cycle time, surface roughness, energy consumption, and cleaning efficiency. Use specific values with units and cite relevant data sources."
    },
    "comparison": {
      "required": true,
      "prompt": "Compare {subject} to traditional cleaning methods in terms of speed, cost, and effectiveness. Include quantitative data where possible and explain the advantages laser cleaning offers over alternatives."
    },
    "safety": {
      "required": true,
      "prompt": "Outline the safety considerations and regulatory standards applicable to {subject} application, including required protective equipment, facility requirements, and industry regulations."
    }
  },

  "applicationProfile": {
    "name": {
      "type": "string",
      "required": true,
      "description": "Name of the laser cleaning application"
    },
    "description": {
      "type": "string",
      "required": true,
      "description": "Overview of the laser cleaning application"
    },
    "primaryAudience": {
      "type": "string",
      "required": true,
      "description": "Primary target audience for the application"
    },
    "secondaryAudience": {
      "type": "string",
      "required": false,
      "description": "Secondary target audience for the application"
    },
    "industries": {
      "type": "array",
      "items": {"type": "string"},
      "required": true,
      "description": "Industries where the application is commonly used"
    },
    "substrates": {
      "type": "array",
      "items": {"type": "string"},
      "required": true,
      "description": "Substrates commonly cleaned in this application"
    },
    "keywords": {
      "type": "array",
      "items": {"type": "string"},
      "required": true,
      "description": "Keywords for SEO, tagging, and JSON-LD"
    },
    "schemaOrgType": {
      "type": "string",
      "required": true,
      "description": "Schema.org type for JSON-LD",
      "default": "TechnicalArticle"
    },
    "url": {
      "type": "string",
      "required": false,
      "description": "Canonical URL for the application page"
    },
    "laserParameters": {
      "type": "object",
      "required": true,
      "properties": {
        "description": {
          "type": "string",
          "required": true,
          "description": "Overview of laser parameters for the application"
        },
        "parameters": {
          "type": "array",
          "required": true,
          "items": {
            "type": "object",
            "properties": {
              "name": {"type": "string", "required": true},
              "unit": {"type": "string", "required": true},
              "optimalRange": {"type": "string", "required": true},
              "fullRanges": {
                "type": "array",
                "items": {"type": "string"},
                "required": false
              }
            }
          }
        },
        "dataSource": {
          "type": "string",
          "required": false,
          "description": "Source of parameter data"
        }
      }
    },
    "outcomes": {
      "type": "array",
      "required": true,
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string", "required": true},
          "description": {"type": "string", "required": true}
        }
      }
    },
    "challenges": {
      "type": "array",
      "required": true,
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string", "required": true},
          "description": {"type": "string", "required": true}
        }
      }
    },
    "performanceMetrics": {
      "type": "object",
      "required": true,
      "properties": {
        "description": {"type": "string", "required": true},
        "metrics": {
          "type": "array",
          "required": true,
          "items": {
            "type": "object",
            "properties": {
              "name": {"type": "string", "required": true},
              "unit": {"type": "string", "required": true},
              "optimalRange": {"type": "string", "required": true},
              "fullRanges": {
                "type": "array",
                "items": {"type": "string"},
                "required": false
              }
            }
          }
        },
        "dataSource": {"type": "string", "required": false}
      }
    },
    "cleaningSpeedComparison": {
      "type": "object",
      "required": true,
      "properties": {
        "description": {"type": "string", "required": true},
        "methods": {
          "type": "array",
          "required": true,
          "items": {
            "type": "object",
            "properties": {
              "method": {"type": "string", "required": true},
              "speed": {"type": "string", "required": true}
            }
          }
        },
        "chartConfig": {
          "type": "object",
          "required": false,
          "properties": {
            "type": {"type": "string", "required": false},
            "dataSource": {"type": "string", "required": false}
          }
        }
      }
    },
    "costComparison": {
      "type": "object",
      "required": true,
      "properties": {
        "description": {"type": "string", "required": true},
        "methods": {
          "type": "array",
          "required": true,
          "items": {
            "type": "object",
            "properties": {
              "method": {"type": "string", "required": true},
              "cost": {"type": "string", "required": true}
            }
          }
        },
        "chartConfig": {
          "type": "object",
          "required": false,
          "properties": {
            "type": {"type": "string", "required": false},
            "dataSource": {"type": "string", "required": false}
          }
        }
      }
    },
    "safetyConsiderations": {
      "type": "array",
      "required": true,
      "items": {"type": "string"}
    },
    "regulatoryStandards": {
      "type": "array",
      "required": true,
      "items": {"type": "string"}
    },
    "author": {
      "type": "object",
      "required": true,
      "properties": {
        "id": {"type": "string", "required": true},
        "name": {"type": "string", "required": true},
        "title": {"type": "string", "required": false},
        "country": {"type": "string", "required": false},
        "image": {"type": "string", "required": false},
        "slug": {"type": "string", "required": false},
        "url": {"type": "string", "required": false}
      }
    },
    "contentManagement": {
      "type": "object",
      "required": true,
      "properties": {
        "articleType": {"type": "string", "required": true, "default": "application-profile"},
        "publishedAt": {"type": "string", "format": "date", "required": false},
        "lastUpdated": {"type": "string", "format": "date", "required": false},
        "generationTimestamp": {"type": "string", "format": "date-time", "required": false},
        "modelUsed": {"type": "string", "required": false}
      }
    },
    "relatedContent": {
      "type": "array",
      "required": false,
      "items": {
        "type": "object",
        "properties": {
          "title": {"type": "string", "required": true},
          "url": {"type": "string", "required": true},
          "type": {"type": "string", "required": true}
        }
      }
    }
  },

  "jsonLD": {
    "@type": "TechnicalArticle",
    "requiredProperties": [
      "headline",
      "description",
      "author"
    ],
    "recommendedProperties": [
      "datePublished",
      "dateModified",
      "publisher",
      "keywords",
      "industry"
    ]
  },

  "validation": {
    "requiredSections": [
      "Overview",
      "Parameters",
      "Outcomes",
      "Challenges",
      "Performance",
      "Comparison",
      "Safety"
    ],
    "jsonLD": {
      "@type": "TechnicalArticle",
      "requiredProperties": [
        "headline",
        "description",
        "author"
      ],
      "recommendedProperties": [
        "datePublished",
        "dateModified",
        "publisher",
        "keywords",
        "industry"
      ]
    }
  }
}