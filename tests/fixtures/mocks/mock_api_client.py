#!/usr/bin/env python3
"""
Mock API Client for Testing

Provides mock implementations of API clients to speed up tests
by avoiding real API calls during development and CI/CD.
"""

import json
import random
import time
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

# Import the real API client classes for compatibility
from api.client import APIResponse, GenerationRequest


class MockAPIClient:
    """Mock API client that simulates responses without making real API calls"""

    def __init__(
        self,
        provider_name: str = "mock",
        api_key: str = "test_key",
        simulate_failures: bool = False,
    ):
        self.provider_name = provider_name
        self.api_key = api_key
        self.call_count = 0
        self.response_delay = 0.1  # Fast response for testing
        self.simulate_failures = simulate_failures
        self.failure_rate = 0.05  # 5% failure rate when enabled
        self.retry_count = 0

        # Statistics tracking (same as real API client)
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_response_time": 0.0,
        }

        # Provider-specific configurations
        self._setup_provider_config()

    def _setup_provider_config(self):
        """Setup provider-specific configurations and optimizations"""
        self.provider_configs = {
            "deepseek": {
                "model": "deepseek-chat",
                "max_tokens": 32000,
                "supports_function_calling": True,
                "optimal_temperature": 0.7,
                "component_optimizations": {
                    "frontmatter": {"max_tokens": 2000, "temperature": 0.3},
                    "content": {"max_tokens": 4000, "temperature": 0.7},
                    "jsonld": {"max_tokens": 1500, "temperature": 0.2},
                    "table": {"max_tokens": 1000, "temperature": 0.3},
                    "metatags": {"max_tokens": 800, "temperature": 0.4},
                    "tags": {"max_tokens": 500, "temperature": 0.5},
                    "bullets": {"max_tokens": 1200, "temperature": 0.6},
                    "caption": {"max_tokens": 600, "temperature": 0.6},
                    "propertiestable": {"max_tokens": 500, "temperature": 0.2},
                },
            },
            "grok": {
                "model": "grok-4",
                "max_tokens": 8000,
                "supports_reasoning": True,
                "optimal_temperature": 0.7,
                "exclude_params": ["frequency_penalty", "presence_penalty"],
            },
            "openai": {
                "model": "gpt-4-turbo",
                "max_tokens": 4000,
                "optimal_temperature": 0.7,
            },
        }

    def generate(self, request: GenerationRequest) -> APIResponse:
        """Mock content generation with realistic but fast responses"""
        self.call_count += 1
        self.stats["total_requests"] += 1

        # Simulate network failures if enabled
        if self.simulate_failures and random.random() < self.failure_rate:
            self.stats["failed_requests"] += 1
            return self._simulate_failure(request)

        # Simulate API delay with some variance
        delay = self.response_delay * (0.8 + random.random() * 0.4)  # 80-120% variance
        time.sleep(delay)

        # Apply provider-specific optimizations
        optimized_request = self._apply_provider_optimizations(request)

        # Generate mock response based on prompt content
        content = self._generate_content_from_prompt(optimized_request.prompt)

        # Simulate token usage with variance
        prompt_tokens = len(optimized_request.prompt.split())
        completion_tokens = len(content.split())
        total_tokens = prompt_tokens + completion_tokens

        # Update successful request stats
        self.stats["successful_requests"] += 1
        self.stats["total_tokens"] += total_tokens
        self.stats["total_response_time"] += delay

        return APIResponse(
            success=True,
            content=content,
            response_time=delay,
            token_count=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model_used=self._get_model_name(),
            request_id=f"mock-{self.call_count}-{int(time.time())}",
        )

    def _apply_provider_optimizations(
        self, request: GenerationRequest
    ) -> GenerationRequest:
        """Apply provider-specific optimizations to the request"""
        if self.provider_name not in self.provider_configs:
            return request

        config = self.provider_configs[self.provider_name]

        # Apply component-specific optimizations for DeepSeek
        if self.provider_name == "deepseek":
            component_type = self._detect_component_type(request.prompt)
            if component_type in config["component_optimizations"]:
                opt = config["component_optimizations"][component_type]
                return GenerationRequest(
                    prompt=request.prompt,
                    system_prompt=request.system_prompt,
                    max_tokens=min(request.max_tokens or 4000, opt["max_tokens"]),
                    temperature=opt["temperature"],
                    top_p=request.top_p,
                    frequency_penalty=request.frequency_penalty,
                    presence_penalty=request.presence_penalty,
                )

        # For Grok, exclude certain parameters
        if self.provider_name == "grok" and "exclude_params" in config:
            return GenerationRequest(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                frequency_penalty=0.0,  # Grok doesn't use these
                presence_penalty=0.0,
            )

        return request

    def _detect_component_type(self, prompt: str) -> str:
        """Detect component type from prompt content"""
        prompt_lower = prompt.lower()

        # Component detection patterns
        patterns = {
            "frontmatter": ["yaml", "frontmatter", "metadata", "properties"],
            "content": ["comprehensive", "technical article", "detailed explanation"],
            "jsonld": ["json-ld", "structured data", "schema.org"],
            "table": ["markdown table", "tabular", "comparison table"],
            "metatags": ["meta tags", "seo", "open graph"],
            "tags": ["tags", "categories", "keywords"],
            "bullets": ["bullet points", "key features", "advantages"],
            "caption": ["caption", "image description", "visual"],
            "propertiestable": [
                "properties table",
                "specifications",
                "characteristics",
            ],
        }

        for component, keywords in patterns.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return component

        return "content"  # Default fallback

    def _get_model_name(self) -> str:
        """Get the appropriate model name for this provider"""
        if self.provider_name in self.provider_configs:
            return self.provider_configs[self.provider_name]["model"]
        return f"{self.provider_name}-mock-model"

    def _simulate_failure(self, request: GenerationRequest) -> APIResponse:
        """Simulate various types of API failures"""
        failure_types = [
            ("timeout", "Request timeout after 30 seconds"),
            ("rate_limit", "Rate limit exceeded. Please try again later."),
            ("server_error", "Internal server error"),
            ("invalid_request", "Invalid request parameters"),
            ("auth_error", "Authentication failed"),
        ]

        failure_type, error_msg = random.choice(failure_types)

        return APIResponse(
            success=False,
            content="",
            error=error_msg,
            response_time=self.response_delay * 2,  # Failures take longer
            token_count=0,
            prompt_tokens=0,
            completion_tokens=0,
            model_used=self._get_model_name(),
            retry_count=self.retry_count,
        )

    def generate_simple(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = None,
        temperature: float = None,
    ) -> APIResponse:
        """Simplified generation method for backward compatibility"""
        request = GenerationRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens or 4000,
            temperature=temperature or 0.7,
        )
        return self.generate(request)

    def generate_with_retry(
        self, request: GenerationRequest, max_retries: int = 3
    ) -> APIResponse:
        """Generate content with built-in retry logic"""
        last_response = None

        for attempt in range(max_retries):
            try:
                response = self.generate(request)
                if response.success:
                    return response
                last_response = response

                # Exponential backoff for failures
                if attempt < max_retries - 1:
                    delay = (2**attempt) * 0.1  # 0.1, 0.2, 0.4 seconds
                    time.sleep(delay)

            except Exception as e:
                if attempt == max_retries - 1:
                    return APIResponse(
                        success=False,
                        content="",
                        error=f"Failed after {max_retries} attempts: {str(e)}",
                        response_time=0.0,
                        retry_count=attempt,
                    )

        return last_response or APIResponse(
            success=False,
            content="",
            error="All retry attempts failed",
            response_time=0.0,
            retry_count=max_retries,
        )

    def _generate_content_from_prompt(self, prompt: str) -> str:
        """Generate mock response based on prompt content with expanded material support"""
        prompt_lower = prompt.lower()

        # Component-specific content (check first to override material-specific content)
        component_patterns = {
            "frontmatter": ["yaml", "frontmatter", "metadata"],
            "jsonld": ["json-ld", "structured data"],
            "table": ["markdown table", "tabular data"],
            "metatags": ["meta tags", "seo optimization"],
            "tags": ["tags", "categories", "keywords"],
            "bullets": ["bullet points", "key features"],
            "caption": ["caption", "image description"],
            "propertiestable": ["properties table", "specifications"],
        }

        for component, patterns in component_patterns.items():
            if any(pattern in prompt_lower for pattern in patterns):
                method_name = f"_generate_{component}_content"
                if component == "frontmatter":
                    return getattr(self, method_name)(prompt)
                else:
                    return getattr(self, method_name)()

        # Material-specific content generation
        materials = {
            "steel": ["steel", "iron", "carbon steel", "stainless steel"],
            "aluminum": ["aluminum", "aluminium", "al alloy"],
            "copper": ["copper", "brass", "bronze"],
            "titanium": ["titanium", "ti alloy"],
            "composite": ["composite", "carbon fiber", "fiberglass"],
            "ceramic": ["ceramic", "silicon carbide", "alumina"],
            "plastic": ["plastic", "polymer", "nylon", "ptfe"],
            "glass": ["glass", "silica", "quartz"],
        }

        # Check for material + laser cleaning combination
        for material, keywords in materials.items():
            if (
                any(keyword in prompt_lower for keyword in keywords)
                and "laser" in prompt_lower
            ):
                return getattr(self, f"_generate_{material}_content")()

        # Generic laser cleaning content
        if "laser" in prompt_lower and (
            "cleaning" in prompt_lower or "removal" in prompt_lower
        ):
            return self._generate_generic_laser_content()

        # Default to generic content
        return self._generate_generic_content()

    def _generate_steel_content(self) -> str:
        """Generate mock steel-related content"""
        return """### Steel Surface Preparation with Laser Technology

Steel substrates present unique challenges and opportunities for laser cleaning applications. The process effectively removes rust, scale, paint, and other contaminants while maintaining the integrity of the base material.

### Material Properties
- Thermal conductivity: 50-60 W/m·K
- Melting point: 1370-1530°C
- Surface reflectivity: 60-70% at 1064nm wavelength
- Common contaminants: Iron oxide, carbon deposits, oils

### Process Optimization
The laser parameters must be carefully selected based on the specific steel alloy and contamination type. Higher energy densities may be required for heavily oxidized surfaces, while more delicate cleaning can be achieved with lower fluences.

### Industrial Applications
- Automotive component preparation
- Ship hull maintenance
- Bridge structure restoration
- Pipeline cleaning and inspection"""

    def _generate_aluminum_content(self) -> str:
        """Generate mock aluminum-related content"""
        return """### Aluminum Laser Cleaning Applications

Aluminum and its alloys respond exceptionally well to laser cleaning processes due to their favorable optical and thermal properties. The technology provides precise control over surface preparation for various industrial applications.

#### Material Characteristics
- High reflectivity: 85-95% at near-IR wavelengths
- Thermal conductivity: 200-250 W/m·K
- Melting point: 660°C
- Oxide layer thickness: 2-5 nanometers

#### Process Parameters
- Optimal wavelength: 1064nm (fundamental Nd:YAG)
- Pulse energy: 0.5-2.0 mJ
- Spot size: 50-200 μm
- Scanning speed: 100-500 mm/s

#### Surface Quality Considerations
The laser cleaning process can achieve surface roughness values comparable to chemical etching while maintaining the dimensional accuracy of the original component."""

    def _generate_generic_laser_content(self) -> str:
        """Generate generic laser cleaning content"""
        return """### Laser Cleaning Technology Overview

Laser cleaning represents a cutting-edge approach to surface preparation and contamination removal. This non-contact method utilizes focused laser energy to vaporize unwanted materials from substrate surfaces.

#### Key Advantages
- Precise material removal with minimal substrate damage
- Environmentally friendly process with no chemical waste
- Excellent control over cleaning depth and intensity
- Suitable for automation and integration into production lines

#### Technical Specifications
- Wavelength range: 1064nm (fundamental) to 532nm (frequency doubled)
- Pulse duration: 10-100 nanoseconds
- Energy density: 1-10 J/cm²
- Repetition rate: 10-1000 Hz

The technology offers significant improvements over traditional cleaning methods, providing both economic and environmental benefits for industrial applications."""

    def _generate_copper_content(self) -> str:
        """Generate mock copper-related content"""
        return """### Copper Laser Cleaning Applications

Copper and its alloys present excellent characteristics for laser cleaning processes due to their high thermal conductivity and favorable optical properties. The technology enables precise surface preparation for various industrial applications.

### Material Properties
- Thermal conductivity: 380-400 W/m·K
- Melting point: 1085°C
- Surface reflectivity: 85-90% at 1064nm wavelength
- Common contaminants: Copper oxide, sulfides, oils

### Process Parameters
- Optimal wavelength: 1064nm (fundamental Nd:YAG)
- Pulse energy: 0.8-3.0 mJ
- Spot size: 60-250 μm
- Scanning speed: 150-600 mm/s

### Industrial Applications
- Printed circuit board manufacturing
- Electrical component preparation
- Heat exchanger maintenance
- Plumbing system restoration"""

    def _generate_titanium_content(self) -> str:
        """Generate mock titanium-related content"""
        return """### Titanium Laser Cleaning Technology

Titanium and titanium alloys offer exceptional strength-to-weight ratios and corrosion resistance, making them ideal candidates for laser cleaning applications in aerospace and medical industries.

### Material Characteristics
- Thermal conductivity: 15-25 W/m·K
- Melting point: 1668°C
- Surface reflectivity: 40-60% at 1064nm wavelength
- Oxide layer: Titanium dioxide (TiO₂)

### Process Optimization
- Optimal wavelength: 1064nm with frequency doubling option
- Pulse energy: 1.0-4.0 mJ
- Spot size: 80-300 μm
- Scanning speed: 100-400 mm/s

### Aerospace Applications
- Aircraft component maintenance
- Engine part cleaning
- Structural component preparation
- Satellite surface treatment"""

    def _generate_composite_content(self) -> str:
        """Generate mock composite material content"""
        return """### Composite Material Laser Processing

Composite materials present unique challenges and opportunities for laser cleaning applications. The technology enables selective removal of surface contaminants while preserving the integrity of the composite structure.

### Material Properties
- Thermal conductivity: 0.2-50 W/m·K (matrix dependent)
- Decomposition temperature: 200-400°C
- Surface characteristics: Mixed reflectivity
- Common contaminants: Release agents, oils, surface debris

### Process Considerations
- Optimal wavelength: 1064nm (fundamental)
- Pulse energy: 0.5-2.5 mJ
- Spot size: 100-400 μm
- Scanning speed: 200-800 mm/s

### Manufacturing Applications
- Aerospace component finishing
- Automotive part preparation
- Wind turbine blade maintenance
- Marine composite cleaning"""

    def _generate_ceramic_content(self) -> str:
        """Generate mock ceramic material content"""
        return """### Ceramic Laser Cleaning Applications

Ceramic materials offer excellent hardness and thermal stability, making them suitable for high-precision laser cleaning applications in various industrial sectors.

### Material Properties
- Thermal conductivity: 2-30 W/m·K
- Melting point: 1200-2500°C
- Surface reflectivity: 10-40% at 1064nm wavelength
- Common contaminants: Processing residues, oils, particulates

### Process Parameters
- Optimal wavelength: 1064nm with green option
- Pulse energy: 1.5-5.0 mJ
- Spot size: 50-200 μm
- Scanning speed: 100-500 mm/s

### Industrial Applications
- Semiconductor manufacturing
- Electronic substrate cleaning
- Optical component preparation
- Medical device processing"""

    def _generate_plastic_content(self) -> str:
        """Generate mock plastic material content"""
        return """### Plastic Laser Cleaning Technology

Plastic materials require careful laser parameter selection due to their lower melting points and potential for thermal damage. Modern laser systems enable effective cleaning with minimal substrate degradation.

### Material Properties
- Thermal conductivity: 0.1-0.5 W/m·K
- Melting point: 100-400°C
- Surface reflectivity: 5-30% at 1064nm wavelength
- Common contaminants: Mold release agents, oils, surface debris

### Process Optimization
- Optimal wavelength: 1064nm (fundamental)
- Pulse energy: 0.3-1.5 mJ
- Spot size: 80-300 μm
- Scanning speed: 300-1000 mm/s

### Manufacturing Applications
- Injection molded part cleaning
- 3D printed component finishing
- Automotive interior preparation
- Consumer product manufacturing"""

    def _generate_glass_content(self) -> str:
        """Generate mock glass material content"""
        return """### Glass Laser Cleaning Applications

Glass substrates offer excellent optical properties and surface quality requirements for laser cleaning applications. The technology enables contamination removal without compromising optical performance.

### Material Properties
- Thermal conductivity: 0.8-1.4 W/m·K
- Softening point: 500-800°C
- Surface reflectivity: 4-8% at 1064nm wavelength
- Common contaminants: Oils, fingerprints, particulate matter

### Process Parameters
- Optimal wavelength: 1064nm (fundamental)
- Pulse energy: 0.5-2.0 mJ
- Spot size: 50-200 μm
- Scanning speed: 200-800 mm/s

### Optical Applications
- Lens manufacturing and cleaning
- Display panel preparation
- Optical fiber processing
- Precision optics maintenance"""

    def _extract_template_variables(self, prompt: str) -> Dict[str, str]:
        """Extract template variables from the prompt containing YAML template"""
        import re

        variables = {}

        # Look for template variables in the format {variable_name}
        # Common patterns we expect to find
        patterns = {
            'author_name': r'author:\s*"([^"]+)"',
            'author_object_country': r'country:\s*"([^"]+)"',
            'author_object_expertise': r'expertise:\s*"([^"]+)"',
            'author_id': r'id:\s*([^}\s]+)',
            'material_name': r'name:\s*"([^"]+)"',
            'material_symbol': r'symbol:\s*"([^"]+)"',
        }

        for var_name, pattern in patterns.items():
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                variables[var_name] = match.group(1)

        # Also try to extract from template format {variable_name}
        template_vars = re.findall(r'\{([^}]+)\}', prompt)
        for var in template_vars:
            if var in ['author_name', 'author_object_country', 'author_object_expertise', 'author_id', 'material_name', 'material_symbol']:
                # Try to find the value in the prompt context
                # Look for patterns like "author_name": "Ikmanda Roswati"
                value_pattern = rf'"{var}":\s*"([^"]+)"'
                match = re.search(value_pattern, prompt)
                if match:
                    variables[var] = match.group(1)

        return variables

    def _generate_frontmatter_content(self, prompt: str = "") -> str:
        """Generate mock YAML frontmatter matching the comprehensive template format"""
        # Extract template variables from the prompt
        template_vars = self._extract_template_variables(prompt)

        # Use extracted variables or fallbacks
        author_name = template_vars.get('author_name', 'Dr. Sarah Chen')
        author_country = template_vars.get('author_object_country', 'China')
        author_expertise = template_vars.get('author_object_expertise', 'Laser Materials Processing')
        author_id = template_vars.get('author_id', 'sarah_chen')
        material_name = template_vars.get('material_name', 'Steel')
        material_symbol = template_vars.get('material_symbol', 'Fe')

        return f"""---
name: "{material_name}"
applications:
- industry: "Electronics Manufacturing"
  detail: "Removal of surface oxides and contaminants from {material_name} substrates"
- industry: "Aerospace Components"
  detail: "Cleaning of thermal barrier coatings and metal matrix composites"
technicalSpecifications:
  powerRange: "50-200W"
  pulseDuration: "20-100ns"
  wavelength: "1064nm (primary), 532nm (optional)"
  spotSize: "0.2-1.5mm"
  repetitionRate: "20-100kHz"
  fluenceRange: "1.0–4.5 J/cm²"
  safetyClass: "Class 4 (requires full enclosure)"
description: "Technical overview of {material_name}, {material_symbol}, for laser cleaning applications, including optimal 1064nm wavelength interaction, and industrial applications in surface preparation."
author: "{author_name}"
author_object:
  id: {author_id}
  name: "{author_name}"
  sex: "female"
  title: "Materials Scientist"
  country: "{author_country}"
  expertise: "{author_expertise}"
  image: null
keywords: "{material_name.lower()}, {material_name.lower()} metal, laser ablation, laser cleaning, non-contact cleaning, pulsed fiber laser, surface contamination removal, industrial laser parameters, thermal processing, surface restoration"
category: "metal"
chemicalProperties:
  symbol: "{material_symbol}"
  formula: "{material_symbol}"
  materialType: "metal"
properties:
  density: "7.85 g/cm³"
  densityMin: "1.8 g/cm³"
  densityMax: "6.0 g/cm³"
  densityPercentile: 51.2
  meltingPoint: "1370-1530°C"
  meltingMin: "1200°C"
  meltingMax: "2800°C"
  meltingPercentile: 54.5
  thermalConductivity: "50.2 W/m·K"
  thermalMin: "0.5 W/m·K"
  thermalMax: "200 W/m·K"
  thermalPercentile: 14.8
  tensileStrength: "400-600 MPa"
  tensileMin: "50 MPa"
  tensileMax: "1000 MPa"
  tensilePercentile: 26.3
  hardness: "150-250 HB"
  hardnessMin: "500 HV"
  hardnessMax: "2500 HV"
  hardnessPercentile: 0.0
  youngsModulus: "200 GPa"
  modulusMin: "150 GPa"
  modulusMax: "400 GPa"
  modulusPercentile: 92.0
  laserType: "Pulsed Fiber Laser"
  wavelength: "1064nm"
  fluenceRange: "1.0–4.5 J/cm²"
  chemicalFormula: "{material_symbol}"
composition:
- "{material_name} ({material_symbol}) 99.6%"
- "Trace elements (Si, Fe, Na, Mg)"
compatibility:
- "Stainless Steel"
- "Titanium Alloys"
- "Nickel-based Superalloys"
regulatoryStandards: "ISO 18562, ASTM F2100, IEC 60601-1"
images:
  hero:
    alt: "{material_name} surface undergoing laser cleaning showing precise contamination removal"
    url: "/images/{material_name.lower()}-laser-cleaning-hero.jpg"
  micro:
    alt: "Microscopic view of {material_name} surface after laser treatment showing preserved microstructure"
    url: "/images/{material_name.lower()}-laser-cleaning-micro.jpg"
title: "Laser Cleaning {material_name} - Technical Guide for Optimal Processing"
headline: "Comprehensive technical guide for laser cleaning metal {material_name}"
environmentalImpact:
- benefit: "Chemical Solvent Elimination"
  description: "Reduces chemical usage by 100% compared to traditional solvent cleaning methods"
- benefit: "Water Conservation"
  description: "Saves approximately 5000 liters of water per month in industrial applications"
- benefit: "Energy Efficiency"
  description: "Consumes 40% less energy than thermal cleaning processes"
outcomes:
- result: "Surface Cleanliness Level"
  metric: "Achieves ISO 14644-1 Class 7 cleanliness standard"
- result: "Material Removal Precision"
  metric: "±5μm accuracy with no substrate damage"
- result: "Processing Speed"
  metric: "2-5 m²/hour cleaning rate depending on contamination level"
---"""

    def _generate_jsonld_content(self) -> str:
        """Generate mock JSON-LD structured data"""
        return """{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "Laser Cleaning Technology Overview",
  "description": "Comprehensive technical overview of laser cleaning processes and applications",
  "author": {
    "@type": "Organization",
    "name": "Industrial Technology Institute"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Manufacturing Technology Journal"
  },
  "datePublished": "2025-01-15",
  "technicalSpecifications": {
    "@type": "PropertyValue",
    "name": "Wavelength Range",
    "value": "532-1064 nm"
  },
  "application": {
    "@type": "Text",
    "value": "Industrial surface preparation and contamination removal"
  }
}"""

    def _generate_table_content(self) -> str:
        """Generate mock markdown table"""
        return """| Material | Thermal Conductivity (W/m·K) | Optimal Wavelength (nm) | Pulse Energy (mJ) | Applications |
|----------|------------------------------|-------------------------|-------------------|---------------|
| Steel | 50-60 | 1064 | 1.0-3.0 | Automotive, Shipbuilding |
| Aluminum | 200-250 | 1064 | 0.5-2.0 | Aerospace, Electronics |
| Copper | 380-400 | 1064 | 0.8-3.0 | Electrical, Plumbing |
| Titanium | 15-25 | 1064/532 | 1.0-4.0 | Aerospace, Medical |
| Ceramic | 2-30 | 1064/532 | 1.5-5.0 | Semiconductor, Optics |
| Plastic | 0.1-0.5 | 1064 | 0.3-1.5 | Manufacturing, 3D Printing |
| Glass | 0.8-1.4 | 1064 | 0.5-2.0 | Optics, Displays |
| Composite | 0.2-50 | 1064 | 0.5-2.5 | Aerospace, Automotive |"""

    def _generate_metatags_content(self) -> str:
        """Generate mock meta tags"""
        return """<title>Laser Cleaning Technology | Industrial Surface Preparation Guide</title>
<meta name="description" content="Comprehensive guide to laser cleaning technology for industrial applications. Learn about process parameters, material compatibility, and optimal cleaning techniques.">
<meta name="keywords" content="laser cleaning, surface preparation, industrial technology, contamination removal, manufacturing processes">
<meta name="author" content="Industrial Technology Institute">
<meta name="robots" content="index, follow">
<meta property="og:title" content="Laser Cleaning Technology Guide">
<meta property="og:description" content="Advanced laser cleaning techniques for industrial surface preparation and contamination removal">
<meta property="og:type" content="article">
<meta property="og:url" content="https://industrial-tech.com/laser-cleaning">
<meta property="og:image" content="https://industrial-tech.com/images/laser-cleaning-process.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Laser Cleaning Technology">
<meta name="twitter:description" content="Industrial laser cleaning processes and applications">"""

    def _generate_tags_content(self) -> str:
        """Generate mock tags"""
        return "laser-cleaning, surface-preparation, industrial-technology, manufacturing-processes, contamination-removal, material-processing, quality-control, precision-cleaning, automation, industrial-applications"

    def _generate_bullets_content(self) -> str:
        """Generate mock bullet points"""
        return """- **Precision Cleaning**: Laser technology enables micron-level precision in contamination removal
- **Non-Contact Process**: Eliminates mechanical stress and potential substrate damage
- **Environmentally Friendly**: No chemical solvents or abrasive materials required
- **Selective Removal**: Ability to remove specific contaminants while preserving substrate integrity
- **Automation Ready**: Easily integrated into automated manufacturing and quality control systems
- **Cost Effective**: Reduced waste, lower operational costs, and improved process efficiency
- **Versatile Applications**: Suitable for metals, ceramics, composites, and various industrial materials
- **Quality Assurance**: Consistent, repeatable results with minimal operator intervention"""

    def _generate_caption_content(self) -> str:
        """Generate mock image caption"""
        return "High-precision laser cleaning system processing aerospace-grade titanium alloy components. The focused laser beam selectively removes surface contaminants while maintaining dimensional accuracy and surface finish requirements for critical aerospace applications."

    def _generate_propertiestable_content(self) -> str:
        """Generate mock properties table"""
        return """Thermal Conductivity|50-400|W/m·K|Material-dependent heat transfer rate
Melting Point|100-2500|°C|Temperature threshold for material damage
Surface Reflectivity|4-95|%|Laser energy absorption efficiency
Optimal Wavelength|532-1064|nm|Laser wavelength for best cleaning efficiency
Pulse Energy|0.3-5.0|mJ|Energy delivered per laser pulse
Spot Size|50-400|μm|Laser beam diameter on target surface
Scanning Speed|100-1000|mm/s|Processing speed for optimal results
Repetition Rate|10-1000|Hz|Laser pulse frequency"""

    def get_call_count(self) -> int:
        """Get the number of API calls made"""
        return self.call_count

    def reset_call_count(self):
        """Reset the call count"""
        self.call_count = 0

    def test_connection(self) -> bool:
        """Mock connection test - always succeeds"""
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive client usage statistics"""
        total_time = self.stats["total_response_time"]
        total_requests = self.stats["total_requests"]

        avg_response_time = total_time / total_requests if total_requests > 0 else 0
        success_rate = (
            (self.stats["successful_requests"] / total_requests * 100)
            if total_requests > 0
            else 0
        )
        failure_rate = (
            (self.stats["failed_requests"] / total_requests * 100)
            if total_requests > 0
            else 0
        )

        return {
            **self.stats,
            "average_response_time": round(avg_response_time, 3),
            "success_rate": round(success_rate, 2),
            "failure_rate": round(failure_rate, 2),
            "provider_name": self.provider_name,
            "model_used": self._get_model_name(),
            "call_count": self.call_count,
            "retry_count": self.retry_count,
            "failure_simulation_enabled": self.simulate_failures,
        }

    def reset_statistics(self):
        """Reset usage statistics"""
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_response_time": 0.0,
        }
        self.call_count = 0
        self.retry_count = 0

    def enable_failure_simulation(self, failure_rate: float = 0.05):
        """Enable random failure simulation for testing retry logic"""
        self.simulate_failures = True
        self.failure_rate = min(max(failure_rate, 0.0), 1.0)

    def disable_failure_simulation(self):
        """Disable failure simulation"""
        self.simulate_failures = False
        self.failure_rate = 0.0

    def set_response_delay(self, delay: float):
        """Set custom response delay for testing"""
        self.response_delay = max(delay, 0.0)

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the mock provider configuration"""
        if self.provider_name in self.provider_configs:
            config = self.provider_configs[self.provider_name]
            return {
                "provider": self.provider_name,
                "model": config.get("model", "unknown"),
                "max_tokens": config.get("max_tokens", 4000),
                "optimal_temperature": config.get("optimal_temperature", 0.7),
                "capabilities": list(config.keys()),
                "component_optimizations": config.get("component_optimizations", {}),
                "mock_features": {
                    "failure_simulation": self.simulate_failures,
                    "response_delay": self.response_delay,
                    "call_count": self.call_count,
                },
            }
        return {
            "provider": self.provider_name,
            "model": f"{self.provider_name}-mock-model",
            "max_tokens": 4000,
            "optimal_temperature": 0.7,
            "capabilities": ["basic_generation"],
            "mock_features": {
                "failure_simulation": self.simulate_failures,
                "response_delay": self.response_delay,
                "call_count": self.call_count,
            },
        }

class MockAPIClientManager:
    """Manager for mock API clients with different configurations"""

    def __init__(self):
        self.clients = {}

    def get_client(self, provider_name: str, **kwargs) -> MockAPIClient:
        """Get or create a mock client for the specified provider"""
        if provider_name not in self.clients:
            self.clients[provider_name] = MockAPIClient(provider_name, **kwargs)
        return self.clients[provider_name]

    def reset_all_clients(self):
        """Reset call counts for all clients"""
        for client in self.clients.values():
            client.reset_call_count()


# Global instance for easy access in tests
mock_client_manager = MockAPIClientManager()


def get_mock_client(provider_name: str = "grok", **kwargs) -> MockAPIClient:
    """Convenience function to get a mock client"""
    return mock_client_manager.get_client(provider_name, **kwargs)


def create_provider_specific_mock(provider_name: str, **kwargs) -> MockAPIClient:
    """Create a mock client optimized for a specific provider"""
    client = MockAPIClient(provider_name=provider_name, **kwargs)

    # Provider-specific optimizations
    if provider_name == "deepseek":
        client.set_response_delay(0.15)  # Slightly slower for realism
    elif provider_name == "grok":
        client.set_response_delay(0.12)  # Fast response

    return client


def create_failure_prone_mock(failure_rate: float = 0.1, **kwargs) -> MockAPIClient:
    """Create a mock client that simulates failures for testing retry logic"""
    client = MockAPIClient(**kwargs)
    client.enable_failure_simulation(failure_rate)
    return client


def create_fast_mock_client(**kwargs) -> MockAPIClient:
    """Create a mock client with very fast response times for unit tests"""
    client = MockAPIClient(**kwargs)
    client.response_delay = 0.01  # Very fast for unit tests
    return client


# Test utilities
def assert_mock_client_behavior(client: MockAPIClient):
    """Assert that a mock client behaves correctly"""
    assert isinstance(client, MockAPIClient)
    assert client.call_count >= 0
    assert client.response_delay >= 0
    assert 0.0 <= client.failure_rate <= 1.0


def test_mock_client_compatibility():
    """Test that mock clients are compatible with real API client interface"""
    from api.client import APIResponse, GenerationRequest

    # Test basic functionality
    client = MockAPIClient("test_provider")

    # Test request creation
    request = GenerationRequest(
        prompt="Test prompt",
        system_prompt="Test system",
        max_tokens=1000,
        temperature=0.8,
    )

    # Test generation
    response = client.generate(request)

    # Verify response structure
    assert isinstance(response, APIResponse)
    assert isinstance(response.success, bool)
    assert isinstance(response.content, str)
    assert isinstance(response.response_time, (int, float))
    assert response.response_time >= 0

    print("✅ Mock client compatibility test passed")


def benchmark_mock_providers():
    """Benchmark different mock provider configurations"""
    providers = ["deepseek", "grok", "openai"]
    results = {}

    for provider in providers:
        client = create_provider_specific_mock(provider)
        start_time = time.time()

        # Run multiple requests
        for _ in range(10):
            request = GenerationRequest(prompt=f"Test {provider} content")
            response = client.generate(request)
            assert response.success

        total_time = time.time() - start_time
        avg_time = total_time / 10

        results[provider] = {
            "total_time": round(total_time, 3),
            "avg_time": round(avg_time, 3),
            "calls": client.call_count,
        }

    print("🚀 Mock Provider Benchmark Results:")
    print("-" * 40)
    for provider, stats in results.items():
        print(f"{provider:8}: {stats['avg_time']:.3f}s avg, {stats['calls']} calls")

    return results


if __name__ == "__main__":
    # Test the mock client
    client = MockAPIClient("test_provider")

    # Test basic functionality
    response = client.generate_simple("Test laser cleaning prompt")
    print(f"Mock response: {response.success}")
    print(f"Content length: {len(response.content)}")
    print(f"Call count: {client.get_call_count()}")

    # Test different content types
    steel_response = client.generate_simple("Steel cleaning process")
    aluminum_response = client.generate_simple("Aluminum surface treatment")

    print(f"Steel content length: {len(steel_response.content)}")
    print(f"Aluminum content length: {len(aluminum_response.content)}")
    print(f"Total calls: {client.get_call_count()}")

    # Test provider-specific optimizations
    print("\n🧪 Testing provider-specific optimizations...")
    deepseek_client = create_provider_specific_mock("deepseek")
    grok_client = create_provider_specific_mock("grok")

    print(f"DeepSeek delay: {deepseek_client.response_delay}")
    print(f"Grok delay: {grok_client.response_delay}")

    # Test failure simulation
    print("\n🧪 Testing failure simulation...")
    failure_client = create_failure_prone_mock(failure_rate=0.5)
    failure_client.enable_failure_simulation(0.3)

    success_count = 0
    for i in range(10):
        request = GenerationRequest(prompt=f"Test request {i}")
        response = failure_client.generate(request)
        if response.success:
            success_count += 1

    print(f"Success rate with 30% failure rate: {success_count}/10")

    print("\n✅ All mock client tests completed!")
