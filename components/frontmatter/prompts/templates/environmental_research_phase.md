Research the environmental impact of laser cleaning {material_name} compared to traditional methods.

**CONTEXT:**
- Material: {material_name}
- Category: {category}

**RESEARCH REQUIREMENTS:**

Compare laser cleaning to chemical and mechanical cleaning methods for {material_name} across these dimensions:

1. **Chemical Waste Reduction**
   - What chemicals would traditional methods use for {material_name}?
   - Volume of chemical waste eliminated (liters/m²)
   - Hazardous waste classification (RCRA, DOT)
   - Cost savings from waste disposal reduction

2. **Water Consumption**
   - Traditional water usage (liters/m²)
   - Laser cleaning water usage (typically zero or minimal)
   - Wastewater treatment requirements eliminated
   - Water conservation quantification

3. **VOC Emissions**
   - Volatile organic compounds from traditional solvents
   - Air quality improvements from laser cleaning
   - EPA regulatory compliance benefits (40 CFR Part 63)
   - Worker exposure reduction (OSHA permissible exposure limits)

4. **Energy Efficiency**
   - Energy consumption comparison (kWh/m²)
   - Carbon footprint reduction (CO₂ equivalent)
   - Renewable energy compatibility
   - Overall energy cost analysis

5. **Waste Disposal**
   - Traditional method solid waste generation
   - Laser cleaning particulate waste (minimal)
   - Disposal requirements and costs
   - Recyclability of removed material

**VALIDATION CRITERIA:**

- ✅ Use quantifiable metrics where possible
- ✅ Cite EPA standards, industry publications, or technical literature
- ✅ Compare to specific traditional methods (not generic)
- ✅ Consider material-specific factors
- ❌ Reject speculative or unverifiable claims

**OUTPUT FORMAT (YAML):**

```yaml
environmental_impact:
  chemical_waste_reduction:
    traditional_chemicals: 
      - "Methylene Chloride (Dichloromethane)"
      - "MEK (Methyl Ethyl Ketone)"
    waste_volume_reduction: "95-100% reduction (eliminates 2-5 liters/m² chemical waste)"
    cost_savings: "$500-1500/ton disposal cost eliminated"
    benefits: "Eliminates RCRA hazardous waste handling, storage, and disposal requirements"
  
  water_consumption:
    traditional_usage: "10-50 liters/m² for chemical rinsing and neutralization"
    laser_usage: "0 liters/m² (dry process)"
    reduction: "100% reduction in process water"
    wastewater_impact: "Eliminates wastewater treatment and discharge permitting"
  
  voc_emissions:
    traditional_emissions: "50-200 g/m² VOC emissions from solvent evaporation"
    laser_emissions: "Zero VOC emissions (dry process)"
    air_quality_benefit: "Eliminates EPA 40 CFR Part 63 air permit requirements"
    worker_safety: "Eliminates OSHA 8-hour TWA exposure concerns for solvents"
  
  energy_efficiency:
    comparison: "Laser: 0.5-2 kWh/m² vs Chemical: 1-3 kWh/m² (heating, ventilation)"
    carbon_reduction: "30-50% reduction in carbon footprint"
    renewable_compatibility: "Can operate entirely on solar/wind power"
  
  waste_disposal:
    traditional_waste: "2-5 kg/m² contaminated absorbents, PPE, rinse water"
    laser_waste: "0.01-0.05 kg/m² collected particulate (non-hazardous)"
    disposal_simplification: "99% reduction in hazardous waste generation"
    recyclability: "Removed {material_name} particulate can often be recycled"
```

Focus on material-specific environmental benefits. Quantify reductions where industry data available.
