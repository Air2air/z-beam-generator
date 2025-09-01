#!/usr/bin/env python3
"""
Frontmatter Component Mock Generator

Component-specific mock data generation for testing frontmatter components.
"""

import random
from typing import Dict, Any


def generate_mock_frontmatter(material_name: str, category: str = "metal") -> str:
    """
    Generate mock frontmatter for testing.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        Mock frontmatter content string
    """
    # Mock data templates
    categories = ["metal", "ceramic", "glass", "composite", "plastic", "stone", "wood"]
    if category not in categories:
        category = "metal"
    
    # Generate mock properties based on category
    mock_properties = _generate_mock_properties(category)
    mock_chemical = _generate_mock_chemical_properties(material_name, category)
    
    frontmatter = f"""---
name: "{material_name}"
description: "Technical overview of {material_name.lower()} for laser cleaning applications, including {mock_properties['density']}, {mock_properties['wavelength']}, and industrial applications."
author: "{_get_random_author()}"
keywords: "{material_name.lower()}, {material_name.lower()} {category}, laser ablation, laser cleaning, non-contact cleaning, pulsed fiber laser, surface contamination removal, industrial laser parameters, thermal processing, surface restoration"
category: "{category}"
chemicalProperties:
  symbol: "{mock_chemical['symbol']}"
  formula: "{mock_chemical['formula']}"
  materialType: "{mock_chemical['materialType']}"
properties:
  density: "{mock_properties['density']}"
  densityMin: "{mock_properties['densityMin']}"
  densityMax: "{mock_properties['densityMax']}"
  densityPercentile: {mock_properties['densityPercentile']}
  meltingPoint: "{mock_properties['meltingPoint']}"
  meltingMin: "{mock_properties['meltingMin']}"
  meltingMax: "{mock_properties['meltingMax']}"
  meltingPercentile: {mock_properties['meltingPercentile']}
  thermalConductivity: "{mock_properties['thermalConductivity']}"
  thermalMin: "{mock_properties['thermalMin']}"
  thermalMax: "{mock_properties['thermalMax']}"
  thermalPercentile: {mock_properties['thermalPercentile']}
  tensileStrength: "{mock_properties['tensileStrength']}"
  tensileMin: "{mock_properties['tensileMin']}"
  tensileMax: "{mock_properties['tensileMax']}"
  tensilePercentile: {mock_properties['tensilePercentile']}
  hardness: "{mock_properties['hardness']}"
  hardnessMin: "{mock_properties['hardnessMin']}"
  hardnessMax: "{mock_properties['hardnessMax']}"
  hardnessPercentile: {mock_properties['hardnessPercentile']}
  youngsModulus: "{mock_properties['youngsModulus']}"
  modulusMin: "{mock_properties['modulusMin']}"
  modulusMax: "{mock_properties['modulusMax']}"
  modulusPercentile: {mock_properties['modulusPercentile']}
  laserType: "{mock_properties['laserType']}"
  wavelength: "{mock_properties['wavelength']}"
  fluenceRange: "{mock_properties['fluenceRange']}"
  chemicalFormula: "{mock_chemical['formula']}"
composition:
- "{_get_random_composition()}"
- "{_get_random_composition()}"
compatibility:
- "{_get_random_compatibility()}"
- "{_get_random_compatibility()}"
regulatoryStandards: "{_get_random_standard()}"
images:
  hero:
    alt: "{material_name} surface undergoing laser cleaning showing precise contamination removal"
    url: "/images/{material_name.lower().replace(' ', '-')}-laser-cleaning-hero.jpg"
  micro:
    alt: "Microscopic view of {material_name.lower()} surface after laser treatment showing preserved microstructure"
    url: "/images/{material_name.lower().replace(' ', '-')}-laser-cleaning-micro.jpg"
title: "Laser Cleaning {material_name} - Technical Guide for Optimal Processing"
headline: "Comprehensive technical guide for laser cleaning {category} {material_name.lower()}"
environmentalImpact:
- benefit: "Reduced chemical waste"
  description: "Eliminates 100% of solvent use compared to traditional cleaning methods, preventing ~200L/year of hazardous waste in medium-scale operations."
- benefit: "Energy efficiency"
  description: "Advanced fiber laser systems achieve {random.randint(20, 40)}% better energy efficiency compared to conventional cleaning methods."
---"""
    
    return frontmatter


def _generate_mock_properties(category: str) -> Dict[str, Any]:
    """Generate mock material properties based on category."""
    
    # Property ranges by category
    property_ranges = {
        "metal": {
            "density": (2.7, 19.3, "g/cm³"),
            "melting": (419, 3695, "°C"),
            "thermal": (15, 400, "W/m·K"),
            "tensile": (200, 2000, "MPa"),
            "hardness": (15, 600, "HV"),
            "modulus": (70, 400, "GPa")
        },
        "ceramic": {
            "density": (2.0, 6.0, "g/cm³"),
            "melting": (1200, 2800, "°C"),
            "thermal": (1, 50, "W/m·K"),
            "tensile": (50, 500, "MPa"),
            "hardness": (500, 2500, "HV"),
            "modulus": (150, 400, "GPa")
        },
        "glass": {
            "density": (2.2, 4.5, "g/cm³"),
            "melting": (573, 1700, "°C"),
            "thermal": (0.5, 5, "W/m·K"),
            "tensile": (30, 200, "MPa"),
            "hardness": (400, 800, "HV"),
            "modulus": (50, 90, "GPa")
        }
    }
    
    ranges = property_ranges.get(category, property_ranges["metal"])
    
    # Generate random values within ranges
    density_val = round(random.uniform(ranges["density"][0], ranges["density"][1]), 1)
    melting_val = random.randint(int(ranges["melting"][0]), int(ranges["melting"][1]))
    thermal_val = round(random.uniform(ranges["thermal"][0], ranges["thermal"][1]), 1)
    tensile_val = random.randint(int(ranges["tensile"][0]), int(ranges["tensile"][1]))
    hardness_val = random.randint(int(ranges["hardness"][0]), int(ranges["hardness"][1]))
    modulus_val = random.randint(int(ranges["modulus"][0]), int(ranges["modulus"][1]))
    
    return {
        "density": f"{density_val} {ranges['density'][2]}",
        "densityMin": f"{ranges['density'][0]} {ranges['density'][2]}",
        "densityMax": f"{ranges['density'][1]} {ranges['density'][2]}",
        "densityPercentile": round(random.uniform(10, 90), 1),
        "meltingPoint": f"{melting_val}°C",
        "meltingMin": f"{ranges['melting'][0]}°C",
        "meltingMax": f"{ranges['melting'][1]}°C",
        "meltingPercentile": round(random.uniform(10, 90), 1),
        "thermalConductivity": f"{thermal_val} {ranges['thermal'][2]}",
        "thermalMin": f"{ranges['thermal'][0]} {ranges['thermal'][2]}",
        "thermalMax": f"{ranges['thermal'][1]} {ranges['thermal'][2]}",
        "thermalPercentile": round(random.uniform(10, 90), 1),
        "tensileStrength": f"{tensile_val} {ranges['tensile'][2]}",
        "tensileMin": f"{ranges['tensile'][0]} {ranges['tensile'][2]}",
        "tensileMax": f"{ranges['tensile'][1]} {ranges['tensile'][2]}",
        "tensilePercentile": round(random.uniform(10, 90), 1),
        "hardness": f"{hardness_val} {ranges['hardness'][2]}",
        "hardnessMin": f"{ranges['hardness'][0]} {ranges['hardness'][2]}",
        "hardnessMax": f"{ranges['hardness'][1]} {ranges['hardness'][2]}",
        "hardnessPercentile": round(random.uniform(10, 90), 1),
        "youngsModulus": f"{modulus_val} {ranges['modulus'][2]}",
        "modulusMin": f"{ranges['modulus'][0]} {ranges['modulus'][2]}",
        "modulusMax": f"{ranges['modulus'][1]} {ranges['modulus'][2]}",
        "modulusPercentile": round(random.uniform(10, 90), 1),
        "laserType": random.choice(["Nd:YAG pulsed laser", "Fiber laser", "CO₂ laser", "Excimer laser"]),
        "wavelength": random.choice(["1064nm", "1070nm", "532nm", "355nm", "10.6μm"]),
        "fluenceRange": f"{random.uniform(0.1, 2.0):.1f}–{random.uniform(3.0, 10.0):.1f} J/cm²"
    }


def _generate_mock_chemical_properties(material_name: str, category: str) -> Dict[str, str]:
    """Generate mock chemical properties."""
    
    # Generate symbol from material name
    words = material_name.split()
    if len(words) == 1:
        symbol = words[0][:3].upper()
    else:
        symbol = ''.join(word[0].upper() for word in words[:2])
    
    # Mock formulas by category
    formulas = {
        "metal": [f"{symbol}", f"{symbol}₂O₃", f"{symbol}Cl₂"],
        "ceramic": [f"Al₂O₃·{symbol}O₂", f"{symbol}₂SiO₄", f"{symbol}O₂"],
        "glass": [f"SiO₂·{symbol}O", "Na₂O·CaO·6SiO₂", f"B₂O₃·{symbol}O"],
        "composite": [f"C₆H₄O₂·{symbol}", f"{symbol}(CF₂)ₙ", f"C₈H₈·{symbol}"],
        "plastic": ["(C₂H₄)ₙ", "(C₃H₆)ₙ", "C₈H₈"],
        "stone": [f"CaCO₃·{symbol}O", "SiO₂·Al₂O₃", "CaMg(CO₃)₂"],
        "wood": ["C₆H₁₀O₅", "C₁₅H₂₂O₄", "C₉H₁₀O₂"]
    }
    
    formula = random.choice(formulas.get(category, formulas["metal"]))
    
    material_types = {
        "metal": ["element", "alloy"],
        "ceramic": ["compound", "composite"],
        "glass": ["compound"],
        "composite": ["composite"],
        "plastic": ["compound"],
        "stone": ["compound"],
        "wood": ["compound"]
    }
    
    material_type = random.choice(material_types.get(category, ["compound"]))
    
    return {
        "symbol": symbol,
        "formula": formula,
        "materialType": material_type
    }


def _get_random_author() -> str:
    """Get a random author name."""
    authors = [
        "Dr. Sarah Chen", "Prof. Michael Rodriguez", "Dr. Anna Kowalski",
        "Dr. Hiroshi Tanaka", "Prof. Elena Petrov", "Dr. James Wilson",
        "Dr. Maria Garcia", "Prof. David Kim", "Dr. Lisa Anderson"
    ]
    return random.choice(authors)


def _get_random_composition() -> str:
    """Get random composition element."""
    compositions = [
        "Iron 60-70%", "Carbon 0.2-0.8%", "Silicon 1-3%", "Aluminum 85-95%",
        "Titanium 90-99%", "Chromium 10-20%", "Nickel 8-12%", "Copper 99.9%",
        "SiO₂ 60-75%", "Al₂O₃ 15-25%", "CaO 5-10%", "MgO 2-5%"
    ]
    return random.choice(compositions)


def _get_random_compatibility() -> str:
    """Get random compatibility material."""
    materials = [
        "Metals", "Ceramics", "Composites", "Glasses", "Polymers",
        "Natural stone", "Concrete", "Alloys", "Semiconductors"
    ]
    return random.choice(materials)


def _get_random_standard() -> str:
    """Get random regulatory standard."""
    standards = [
        "ISO 11553 Safety of machinery - Laser processing machines",
        "ANSI Z136.1 Safe Use of Lasers",
        "IEC 60825 Safety of laser products",
        "OSHA 29 CFR 1926 Construction Standards",
        "EN 60825 Safety of laser products"
    ]
    return random.choice(standards)
