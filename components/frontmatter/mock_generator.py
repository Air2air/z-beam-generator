#!/usr/bin/env python3
"""
Frontmatter Component Mock Generator

Simplified mock data generation for testing frontmatter components.
"""

import random


def generate_mock_frontmatter(material_name: str, category: str) -> str:
    """
    Generate simple mock frontmatter for testing.
    
    Args:
        material_name: Name of the material
        category: Material category (required)
        
    Returns:
        Mock frontmatter content string
    """
    # Simple mock author
    authors = ["Dr. Test Author", "Prof. Mock Expert", "Dr. Sample Researcher"]
    author = random.choice(authors)
    
    # Basic mock properties
    density = round(random.uniform(1.0, 10.0), 1)
    melting_point = random.randint(500, 2000)
    
    frontmatter = f"""---
name: "{material_name}"
description: "Mock technical overview of {material_name.lower()} for testing purposes"
author: "{author}"
keywords: "{material_name.lower()}, {category}, laser cleaning, test data"
category: "{category}"
chemicalProperties:
  symbol: "{material_name[:2].upper()}"
  formula: "MockFormula"
  materialType: "compound"
properties:
  density: "{density} g/cm³"
  meltingPoint: "{melting_point}°C"
  thermalConductivity: "50 W/m·K"
  laserType: "Test Laser"
  wavelength: "1064nm"
  fluenceRange: "1-5 J/cm²"
composition:
- "Component 1: 80%"
- "Component 2: 20%"
compatibility:
- "Compatible Material A"
- "Compatible Material B"
regulatoryStandards: "Test Standard ISO-TEST"
images:
  hero:
    alt: "Test image alt text"
    url: "/images/test-hero.jpg"
  micro:
    alt: "Test micro image alt text"  
    url: "/images/test-micro.jpg"
title: "Test: Laser Cleaning {material_name}"
headline: "Test technical guide for {category} {material_name.lower()}"
environmentalImpact:
- benefit: "Test environmental benefit"
  description: "Mock quantified description for testing"
subject: "{material_name}"
article_type: "material"
---"""
    
    return frontmatter
