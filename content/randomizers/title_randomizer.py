import random
from typing import Dict, List, Optional

class TitleRandomizer:
    """Provides highly randomized section titles with creative variations."""
    
    # Expanded creative title variations
    _variations = {
        "overview": [
            "Overview", "Introduction", "About", "Background", "At a Glance", "Key Facts",
            "Getting Started", "Fundamental Concepts", "Essentials", "Primer", 
            "Basic Information", "What to Know", "Core Concepts"
        ],
        "applications": [
            "Applications", "Use Cases", "Industry Uses", "Practical Uses", "Implementation", "Where It's Used",
            "Real-World Applications", "Field Usage", "Commercial Applications", "Industrial Deployment",
            "Practical Implementation", "Application Scenarios", "Usage Examples"
        ],
        "technicalSpecifications": [
            "Technical Specifications", "Tech Specs", "Technical Details", "Specifications", 
            "Technical Properties", "Performance Data", "Engineering Parameters", "Technical Characteristics",
            "System Specifications", "Performance Metrics", "Technical Requirements",
            "Operating Specifications", "Technical Profile"
        ],
        "facilities": [
            "Facilities", "Regional Centers", "Local Infrastructure", "Operating Locations", 
            "Production Sites", "Manufacturing Centers", "Processing Facilities", 
            "Service Locations", "Regional Facilities", "Operation Centers",
            "Distribution Network", "Industrial Sites"
        ],
        "regulations": [
            "Regulations", "Compliance Requirements", "Regulatory Framework", "Standards & Compliance", 
            "Industry Standards", "Legal Requirements", "Regulatory Compliance",
            "Certification Standards", "Industry Regulations", "Compliance Framework",
            "Regulatory Guidelines", "Governing Standards"
        ],
        "challenges": [
            "Challenges", "Limitations & Solutions", "Common Issues", "Problem Solving", 
            "Technical Challenges", "Obstacles & Solutions", "Common Problems",
            "Key Challenges", "Addressing Difficulties", "Implementation Challenges",
            "Critical Issues", "Technical Constraints"
        ],
        "outcomes": [
            "Outcomes", "Results", "Performance Metrics", "Measured Results", "Key Outcomes", 
            "Achievement Metrics", "Success Indicators", "Performance Results",
            "Impact Assessment", "Quantified Results", "Effectiveness Measures",
            "Success Metrics"
        ],
        "qualityStandards": [
            "Quality Standards", "Quality Assurance", "Quality Metrics", "Quality Control", 
            "Quality Requirements", "Quality Frameworks", "Quality Protocols",
            "Quality Management", "Quality Guidelines", "Excellence Standards",
            "Quality Certification", "Quality Parameters"
        ],
        "benefits": [
            "Benefits", "Advantages", "Value Proposition", "Key Advantages", "Why Choose This", 
            "Comparative Strengths", "Core Benefits", "Distinctive Advantages",
            "Value Benefits", "Key Strengths", "Competitive Advantages",
            "Performance Benefits", "Strategic Advantages"
        ],
        "specifications": [
            "Specifications", "Key Properties", "Technical Data", "Material Properties", 
            "Performance Specs", "Technical Characteristics", "Physical Properties",
            "Performance Properties", "Characteristic Profile", "Material Specifications",
            "Technical Parameters", "Property Data"
        ]
    }
    
    # Basic title mapping for fallback
    _basic_titles = {
        "technicalSpecifications": "Technical Specifications",
        "regulatoryStandards": "Regulatory Standards",
        "qualityStandards": "Quality Standards",
        "overview": "Overview",
        "applications": "Applications",
        "facilities": "Facilities",
        "regulations": "Regulations",
        "challenges": "Challenges",
        "outcomes": "Outcomes",
        "benefits": "Benefits",
        "specifications": "Specifications"
    }
    
    @classmethod
    def get_title(cls, section_id: str, use_variations: bool = True) -> str:
        """
        Get a highly randomized title for a section.
        
        Args:
            section_id: The ID of the section
            use_variations: Whether to use creative variations
            
        Returns:
            A formatted section title
        """
        # If not using variations or no variations exist for this section
        if not use_variations or section_id not in cls._variations:
            return cls._basic_titles.get(
                section_id, 
                " ".join(word.capitalize() for word in section_id.split("_"))
            )
            
        # Return a random variation
        return random.choice(cls._variations[section_id])

if __name__ == "__main__":
    print("Testing title randomizer functionality...")
    print("Overview title:", TitleRandomizer.get_title("overview", True))
    print("Applications title:", TitleRandomizer.get_title("applications", True))
    print("Technical title:", TitleRandomizer.get_title("technicalSpecifications", True))