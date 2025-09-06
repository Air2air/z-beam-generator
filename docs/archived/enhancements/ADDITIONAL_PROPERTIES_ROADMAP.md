# Additional Material Properties - Percentile Enhancement Roadmap

## 🎯 **Priority 1: Laser-Specific Properties**

### **Laser Absorption Coefficient (α)**
```yaml
# Category ranges for 1064nm laser absorption
metal:
  laserAbsorption:
    min: "0.02 cm⁻¹"     # Highly reflective metals (silver, aluminum)
    max: "100 cm⁻¹"     # Absorptive metals (oxidized steel)
ceramic:
  laserAbsorption:
    min: "0.1 cm⁻¹"     # Transparent ceramics
    max: "50 cm⁻¹"      # Dark/carbon-containing ceramics
```

### **Laser Reflectivity (%)**
```yaml
metal:
  laserReflectivity:
    min: "2%"           # Oxidized/dark metals
    max: "98%"          # Polished silver/aluminum
glass:
  laserReflectivity:
    min: "4%"           # Standard glass at 1064nm
    max: "15%"          # Coated/metallic glass
```

## 🔧 **Priority 2: Thermal Processing Properties**

### **Thermal Diffusivity (α)**
```yaml
metal:
  thermalDiffusivity:
    min: "4 mm²/s"      # Stainless steel
    max: "174 mm²/s"    # Silver
composite:
  thermalDiffusivity:
    min: "0.1 mm²/s"    # Insulating composites
    max: "5 mm²/s"      # Conductive fiber composites
```

### **Coefficient of Thermal Expansion (CTE)**
```yaml
metal:
  thermalExpansion:
    min: "0.5 µm/m·K"   # Invar alloys
    max: "29 µm/m·K"    # Aluminum
ceramic:
  thermalExpansion:
    min: "0.5 µm/m·K"   # Quartz
    max: "8 µm/m·K"     # Alumina
```

## ⚡ **Priority 3: Electrical Properties**

### **Electrical Conductivity (σ)**
```yaml
metal:
  electricalConductivity:
    min: "1.4×10⁶ S/m"  # Stainless steel
    max: "6.3×10⁷ S/m"  # Silver
semiconductor:
  electricalConductivity:
    min: "1×10⁻⁶ S/m"   # Intrinsic silicon
    max: "1×10⁴ S/m"    # Heavily doped silicon
```

## 📊 **Example Enhanced Frontmatter**

```yaml
properties:
  # Current properties (6)
  density: "8.96 g/cm³"
  densityPercentile: 45.2

  # NEW: Laser properties (4)
  laserAbsorption: "15 cm⁻¹"
  absorptionPercentile: 23.5
  laserReflectivity: "85%"
  reflectivityPercentile: 78.9

  # NEW: Advanced thermal (3)
  thermalDiffusivity: "111 mm²/s"
  diffusivityPercentile: 89.2
  thermalExpansion: "16.5 µm/m·K"
  expansionPercentile: 67.3

  # NEW: Electrical (2)
  electricalConductivity: "5.96×10⁷ S/m"
  conductivityPercentile: 95.8
```

## 🔬 **Real-World Value Examples**

### **Copper (Metal Category):**
- **Laser Reflectivity:** 85% = 78.9% through metal range (highly reflective)
- **Electrical Conductivity:** 59.6 MS/m = 95.8% through metal range (excellent conductor)
- **Thermal Diffusivity:** 111 mm²/s = 89.2% through metal range (great heat spreader)

### **Silicon (Semiconductor Category):**
- **Laser Absorption:** 1000 cm⁻¹ = 65.4% through semiconductor range (good absorption)
- **Electrical Resistivity:** Variable from 10⁻⁶ to 10⁶ Ω·m depending on doping

## 🛠 **Implementation Effort Estimates**

### **Phase 1: Laser Properties (2 weeks)**
- Research and compile laser absorption/reflectivity data for all 8 categories
- Add 4 new property fields to templates and database
- Update percentile calculator with new units (cm⁻¹, %)

### **Phase 2: Thermal Properties (2 weeks)**
- Research thermal diffusivity and expansion coefficients
- Add 3 new thermal property fields
- Update unit parsing for mm²/s and µm/m·K

### **Phase 3: Electrical Properties (1 week)**
- Add electrical conductivity and resistivity ranges
- Update templates with electrical property fields
- Handle scientific notation in percentile calculator

## 🎯 **Strategic Value**

### **For Laser Cleaning Applications:**
1. **Laser Absorption/Reflectivity** - Critical for parameter optimization
2. **Thermal Properties** - Prevent damage during processing
3. **Electrical Properties** - Important for semiconductor cleaning

### **For User Decision Making:**
- "This material has 95% electrical conductivity ranking" → Perfect for electrical applications
- "Laser reflectivity is 78% through the range" → Need higher power settings
- "Thermal expansion is only 23% through range" → Good dimensional stability

### **For Next.js UI Enhancement:**
```tsx
<PropertyRadar
  density={33.3}
  laserAbsorption={23.5}
  thermalStability={67.3}
  electricalPerformance={95.8}
  mechanicalStrength={21.0}
/>
```

Would create a beautiful radar chart showing material performance across all dimensions!
