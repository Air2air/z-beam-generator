"""
Mock API client for testing components without making actual API calls.
"""

class MockAPIClient:
    """Mock API client for testing without making actual API calls."""
    
    def __init__(self, model="mock-model", temperature=0.7, max_tokens=2000):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def complete(self, prompt):
        """Generate a mock response based on the prompt."""
        # Return a basic frontmatter response that passes validation
        # This is a simplified response that should work for testing
        return """
name: ceramic
description: A comprehensive overview of ceramic materials used in laser cleaning applications, including properties, types, and applications.
headline: Understanding Ceramic Materials in Laser Cleaning Processes
keywords:
  - ceramic
  - laser cleaning
  - material science
  - technical ceramics
  - industrial applications
datePublished: 2023-08-15
dateModified: 2023-09-01
author:
  name: Test Author
  organization: Test Organization
  bio: Materials science expert specializing in laser technologies
image: /images/materials/ceramic.jpg
category: Materials
subcategory: Ceramic
tableOfContents: true
properties:
  composition: Inorganic, non-metallic materials
  density: 2.0-6.0 g/cm³
  meltingPoint: 1200-2800°C
  thermalConductivity: 0.5-50 W/(m·K)
  applications:
    - Electronics
    - Aerospace
    - Medical devices
    - Industrial manufacturing
"""
