#!/usr/bin/env python3
"""
Generator Data Flow Analysis
Detailed breakdown of how the content generator uses prompts and frontmatter data
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def analyze_data_flow():
    """Analyze the complete data flow of prompts and frontmatter."""
    
    print("🔍 GENERATOR DATA FLOW ANALYSIS")
    print("How the Generator Uses Prompts and Frontmatter Data")
    print("=" * 60)
    
    print("\n📊 DATA SOURCE INTEGRATION")
    print("-" * 30)
    
    data_sources = {
        "1. FRONTMATTER DATA": {
            "Source": "content/components/frontmatter/{material}-laser-cleaning.md",
            "Usage": "Primary data source for material properties and author detection",
            "Key Fields": [
                "author → Author detection and country mapping",
                "authorCountry → Country-specific prompt selection",
                "chemicalProperties.formula → Chemical formula extraction",
                "properties.* → Material properties (density, melting point, etc.)",
                "technicalSpecifications → Laser parameters (wavelength, power, etc.)",
                "applications → Industry-specific use cases",
                "description → Material context"
            ]
        },
        "2. PROMPT CONFIGURATIONS": {
            "Source": "components/content/prompts/{country}_prompt.yaml",
            "Usage": "Language patterns and writing style for content generation",
            "Key Sections": [
                "language_patterns.introduction → Overview section patterns",
                "language_patterns.properties → Material properties patterns",
                "language_patterns.applications → Industrial applications patterns",
                "content_structure.sections → Section configuration",
                "writing_style → Author-specific language nuances"
            ]
        },
        "3. BASE PROMPT": {
            "Source": "components/content/prompts/base_content_prompt.yaml",
            "Usage": "Shared technical requirements and author configurations",
            "Key Sections": [
                "author_configurations → Word limits and specializations",
                "technical_requirements → Required technical content",
                "content_structure → Standard section organization"
            ]
        },
        "4. AUTHOR DATA": {
            "Source": "components/author/authors.json",
            "Usage": "Author metadata and country mappings",
            "Key Fields": [
                "id → Author identification",
                "name → Author name matching",
                "country → Country-to-prompt mapping"
            ]
        }
    }
    
    for source_name, details in data_sources.items():
        print(f"\n{source_name}")
        print(f"  📁 Source: {details['Source']}")
        print(f"  🎯 Usage: {details['Usage']}")
        print(f"  🔧 Key Fields/Sections:")
        for field in details['Key Fields'] if 'Key Fields' in details else details['Key Sections']:
            print(f"     • {field}")
    
    print("\n🔄 INTEGRATION FLOW")
    print("-" * 30)
    
    flow_steps = [
        {
            "step": "1. AUTHOR DETECTION",
            "process": "Extract author from frontmatter.author field",
            "data_used": "frontmatter_data['author'] → 'Yi-Chun Lin'",
            "mapping": "Author name → country mapping → prompt file selection"
        },
        {
            "step": "2. COUNTRY & PROMPT SELECTION", 
            "process": "Map author to country and load corresponding prompt",
            "data_used": "'Yi-Chun Lin' → 'taiwan' → taiwan_prompt.yaml",
            "mapping": "Country determines language patterns and writing style"
        },
        {
            "step": "3. CHEMICAL FORMULA EXTRACTION",
            "process": "Multi-source formula extraction with fallbacks",
            "data_used": "frontmatter.chemicalProperties.formula OR frontmatter.properties.chemicalFormula",
            "mapping": "Formula used in overview section with formula_integration pattern"
        },
        {
            "step": "4. MATERIAL PROPERTIES INTEGRATION",
            "process": "Extract technical properties for laser parameters",
            "data_used": "frontmatter.properties.{density, thermalConductivity, etc.}",
            "mapping": "Properties → technical content in Key Properties section"
        },
        {
            "step": "5. TECHNICAL SPECIFICATIONS",
            "process": "Laser parameter extraction for Optimal Parameters section",
            "data_used": "frontmatter.technicalSpecifications.{wavelength, powerRange, etc.}",
            "mapping": "Tech specs → recommended laser parameters content"
        },
        {
            "step": "6. APPLICATIONS MAPPING",
            "process": "Industry applications for Industrial Applications section",
            "data_used": "frontmatter.applications[].{industry, detail}",
            "mapping": "Applications → industry-specific use case examples"
        },
        {
            "step": "7. LANGUAGE PATTERN APPLICATION",
            "process": "Apply country-specific writing patterns to content",
            "data_used": "prompt.language_patterns.{introduction, properties, applications}",
            "mapping": "Patterns → section-specific language and structure"
        },
        {
            "step": "8. CONTENT STRUCTURE ASSEMBLY",
            "process": "Organize sections according to prompt configuration",
            "data_used": "prompt.content_structure.sections + base_config requirements",
            "mapping": "Structure → final markdown content with author voice"
        }
    ]
    
    for i, step_info in enumerate(flow_steps, 1):
        print(f"\n{step_info['step']}")
        print(f"  🔄 Process: {step_info['process']}")
        print(f"  📊 Data Used: {step_info['data_used']}")
        print(f"  🎯 Mapping: {step_info['mapping']}")
    
    print("\n💡 SPECIFIC INTEGRATION EXAMPLES")
    print("-" * 30)
    
    examples = [
        {
            "example": "TAIWAN AUTHOR OVERVIEW GENERATION",
            "frontmatter_input": "author: 'Yi-Chun Lin', chemicalProperties.formula: 'Aluminum'",
            "prompt_pattern": "language_patterns.introduction.formula_integration: 'The chemical composition {material_formula} provides fundamental understanding'",
            "generated_output": "'The chemical composition Aluminum provides fundamental understanding for effective surface processing.'"
        },
        {
            "example": "TECHNICAL PARAMETERS SECTION",
            "frontmatter_input": "technicalSpecifications: {wavelength: '1064nm', powerRange: '50-200W'}",
            "prompt_pattern": "Enhanced generation method extracts specs dynamically",
            "generated_output": "'• **Wavelength**: 1064nm for optimal Aluminum absorption\\n• **Power Range**: 50-200W optimized for Aluminum processing'"
        },
        {
            "example": "MATERIAL PROPERTIES INTEGRATION",
            "frontmatter_input": "properties: {density: '2.7 g/cm³', thermalConductivity: '237 W/m·K'}",
            "prompt_pattern": "language_patterns.properties patterns + dynamic property extraction",
            "generated_output": "'• **Thermal Properties**: 237 W/m·K affects heat dissipation during laser cleaning'"
        },
        {
            "example": "INDUSTRY APPLICATIONS",
            "frontmatter_input": "applications: [{industry: 'Automotive', detail: 'Engine component cleaning'}]",
            "prompt_pattern": "language_patterns.applications.industrial + frontmatter mapping",
            "generated_output": "'• **Automotive**: Engine component cleaning'"
        }
    ]
    
    for example in examples:
        print(f"\n📝 {example['example']}")
        print(f"  📊 Frontmatter Input: {example['frontmatter_input']}")
        print(f"  🎨 Prompt Pattern: {example['prompt_pattern']}")
        print(f"  ✅ Generated Output: {example['generated_output']}")
    
    print("\n🔧 PROMPT PATTERN USAGE BY SECTION")
    print("-" * 30)
    
    section_patterns = {
        "Overview": {
            "patterns_used": ["introduction.opening", "introduction.formula_integration"],
            "frontmatter_data": ["chemicalProperties.formula", "name"],
            "output": "Technical introduction with chemical formula integration"
        },
        "Key Properties": {
            "patterns_used": ["properties.section_intro", "properties.thermal", "properties.optical"],
            "frontmatter_data": ["properties.density", "properties.thermalConductivity"],
            "output": "Material characteristics with laser interaction details"
        },
        "Industrial Applications": {
            "patterns_used": ["applications.industrial", "applications.sectors"],
            "frontmatter_data": ["applications[].industry", "applications[].detail"],
            "output": "Industry-specific use cases and examples"
        },
        "Optimal Parameters": {
            "patterns_used": ["Enhanced generation (not pure prompt)"],
            "frontmatter_data": ["technicalSpecifications.*"],
            "output": "Recommended laser parameters from frontmatter"
        },
        "Advantages": {
            "patterns_used": ["applications.quality", "Enhanced generation"],
            "frontmatter_data": ["General material context"],
            "output": "Benefits of laser cleaning for the material"
        },
        "Safety Considerations": {
            "patterns_used": ["Enhanced generation"],
            "frontmatter_data": ["technicalSpecifications.safetyClass"],
            "output": "Safety protocols and requirements"
        }
    }
    
    for section_name, details in section_patterns.items():
        print(f"\n📋 {section_name}")
        print(f"  🎨 Patterns Used: {', '.join(details['patterns_used'])}")
        print(f"  📊 Frontmatter Data: {', '.join(details['frontmatter_data'])}")
        print(f"  ✅ Output: {details['output']}")
    
    print("\n🎯 CONFIGURATION HIERARCHY")
    print("-" * 30)
    
    hierarchy = [
        "1. Base Configuration (base_content_prompt.yaml)",
        "   ├── Technical requirements (laser specs, safety)",
        "   ├── Author configurations (word limits, specializations)",
        "   └── Content structure guidelines",
        "",
        "2. Country-Specific Prompts ({country}_prompt.yaml)",
        "   ├── Language patterns (introduction, properties, applications)",
        "   ├── Writing style (sentence structure, cultural elements)",
        "   ├── Content structure (sections, randomization)",
        "   └── Author persona details",
        "",
        "3. Frontmatter Data (material-specific)",
        "   ├── Author assignment (overrides command-line)",
        "   ├── Technical specifications (laser parameters)",
        "   ├── Material properties (physical characteristics)",
        "   └── Applications (industry use cases)",
        "",
        "4. Generated Content",
        "   ├── Combines all data sources",
        "   ├── Applies country-specific patterns",
        "   ├── Integrates technical specifications",
        "   └── Maintains author voice and style"
    ]
    
    for line in hierarchy:
        print(line)
    
    return True

if __name__ == '__main__':
    analyze_data_flow()
