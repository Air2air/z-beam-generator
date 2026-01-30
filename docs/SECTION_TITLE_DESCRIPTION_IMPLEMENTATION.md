# Section Title & Description Implementation Guide

**Date**: January 15, 2026  
**Status**: ✅ Components Updated - Awaiting YAML Population  
**Purpose**: Guide for adding sectionTitle/sectionDescription to material frontmatter

---

## 🎯 What Was Changed

All material section components now support `sectionTitle` and `sectionDescription` props from frontmatter `_section` metadata. This allows content editors to customize section titles and descriptions in YAML files instead of relying on hardcoded defaults.

### Components Updated
1. **LaserMaterialInteraction** - Accepts sectionTitle/sectionDescription
2. **MaterialCharacteristics** - Accepts sectionTitle/sectionDescription
3. **RelatedMaterials** - Accepts sectionTitle/sectionDescription
4. **FAQPanel** - Accepts sectionTitle/sectionDescription
5. **MaterialsLayout** - Passes _section metadata to all components

---

## 📋 Required YAML Updates

### Test Material: Aluminum
File: `frontmatter/materials/aluminum-laser-cleaning.yaml`

Add `sectionTitle` and `sectionDescription` to the `_section` metadata for these sections:

### 1. Material Characteristics Section

**Location**: `properties.materialCharacteristics._section`

**Current Structure**:
```yaml
properties:
  materialCharacteristics:
    title: Aluminum's Distinctive Traits
    sectionDescription: Physical properties that define aluminum's behavior during laser cleaning processes
    _section:
      icon: wrench
      order: 50
      variant: default
    density:
      value: 2.7
      unit: g/cm³
      # ... rest of properties
```

**Add These Fields**:
```yaml
properties:
  materialCharacteristics:
    title: Aluminum's Distinctive Traits
    sectionDescription: Physical properties that define aluminum's behavior during laser cleaning processes
    _section:
      sectionTitle: Physical Characteristics
      sectionDescription: Core material properties including density, thermal conductivity, and mechanical strength that determine aluminum's response to laser cleaning
      icon: wrench
      order: 50
      variant: default
```

**Fallback Behavior**: If not provided, component uses: `"${materialName} physical characteristics"` (e.g., "Aluminum physical characteristics")

---

### 2. Laser Material Interaction Section

**Location**: `properties.laserMaterialInteraction._section`

**Current Structure**:
```yaml
  laserMaterialInteraction:
    title: Aluminum Laser Interaction Dynamics
    sectionDescription: How laser energy interacts with aluminum surfaces during cleaning operations
    _section:
      icon: zap
      order: 60
      variant: default
    absorptionCoefficient:
      value: 8
      unit: '%'
      # ... rest of properties
```

**Add These Fields**:
```yaml
  laserMaterialInteraction:
    title: Aluminum Laser Interaction Dynamics
    sectionDescription: How laser energy interacts with aluminum surfaces during cleaning operations
    _section:
      sectionTitle: Laser-Material Interaction
      sectionDescription: How laser energy absorbs, reflects, and ablates aluminum surfaces during the cleaning process
      icon: zap
      order: 60
      variant: default
```

**Fallback Behavior**: If not provided, component uses: `"${materialName} Laser-Material Interaction"` (e.g., "Aluminum Laser-Material Interaction")

---

### 3. FAQ Section

**Location**: `faq._section` (new field to add)

**Current Structure**:
```yaml
faq:
- question: What safety considerations...
  answer: Professionals often deal with...
  category: safety
- question: How does thermal conductivity...
  answer: Aluminum's high thermal conductivity...
  category: technical
- question: What contaminants are most effectively...
  answer: Laser cleaning excels at removing...
  category: application
```

**Add _section Metadata**:
```yaml
faq:
  _section:
    sectionTitle: Aluminum Laser Cleaning FAQ
    sectionDescription: Expert answers to common questions about laser cleaning aluminum surfaces
    icon: help-circle
    order: 100
    variant: default
  items:
    - question: What safety considerations...
      answer: Professionals often deal with...
      category: safety
    - question: How does thermal conductivity...
      answer: Aluminum's high thermal conductivity...
      category: technical
    - question: What contaminants are most effectively...
      answer: Laser cleaning excels at removing...
      category: application
```

**⚠️ Note**: This requires restructuring FAQ from flat array to object with `_section` and `items` properties.

**Fallback Behavior**: If not provided, component uses: `"FAQs for laser cleaning ${entityName}"` (e.g., "FAQs for laser cleaning Aluminum")

---

### 4. Related Materials Section

**Location**: `relationships.discovery.relatedMaterials._section` (new field to add)

**Current Structure**: No existing structure - materials discovered dynamically

**Add This Structure**:
```yaml
relationships:
  discovery:
    relatedMaterials:
      _section:
        sectionTitle: Similar Non-Ferrous Metals
        sectionDescription: Other lightweight metals with comparable laser cleaning characteristics and industrial applications
        icon: layers
        order: 110
        variant: default
```

**Fallback Behavior**: If not provided, component uses: `"Other ${subcategory} Materials"` (e.g., "Other Non-Ferrous Materials")

---

## 🧪 Testing the Implementation

### Before Testing
1. Add sectionTitle/sectionDescription fields to aluminum YAML (see above)
2. Restart dev server to pick up YAML changes
3. Clear browser cache

### Test Page
Visit: http://localhost:3000/materials/metal/non-ferrous/aluminum-laser-cleaning

### Expected Results

**✅ Physical Characteristics Section**:
- Title displays: "Physical Characteristics" (custom)
- Description: "Core material properties including density, thermal conductivity..."

**✅ Laser-Material Interaction Section**:
- Title displays: "Laser-Material Interaction" (custom)
- Description: "How laser energy absorbs, reflects, and ablates..."

**✅ FAQ Section**:
- Title displays: "Aluminum Laser Cleaning FAQ" (custom)
- Description: "Expert answers to common questions..."

**✅ Related Materials Section**:
- Title displays: "Similar Non-Ferrous Metals" (custom)
- Description: "Other lightweight metals with comparable..."

### Fallback Testing

To verify fallbacks work:
1. Remove sectionTitle from one section
2. Check that default title appears
3. Confirms backward compatibility

---

## 📊 Implementation Status

| Section | Component Updated | YAML Field Added | Tested |
|---------|------------------|------------------|--------|
| Material Characteristics | ✅ | ⏳ Pending | ⏳ |
| Laser Interaction | ✅ | ⏳ Pending | ⏳ |
| FAQ | ✅ | ⏳ Pending | ⏳ |
| Related Materials | ✅ | ⏳ Pending | ⏳ |

---

## 🔄 Rollout Plan

### Phase 1: Test on Aluminum (Current)
- Add fields to aluminum YAML
- Verify display and fallbacks
- Check all 4 sections render correctly

### Phase 2: Document Pattern
- Update FRONTMATTER_OPTIMAL_STRUCTURE.md with examples
- Add to material frontmatter template

### Phase 3: Rollout to All Materials
- Add sectionTitle/sectionDescription to all material YAML files
- Use batch script if needed
- Verify consistency across materials

---

## 📝 Quick Copy-Paste for Aluminum

```yaml
properties:
  materialCharacteristics:
    title: Aluminum's Distinctive Traits
    sectionDescription: Physical properties that define aluminum's behavior during laser cleaning processes
    _section:
      sectionTitle: Physical Characteristics
      sectionDescription: Core material properties including density, thermal conductivity, and mechanical strength that determine aluminum's response to laser cleaning
      icon: wrench
      order: 50
      variant: default
    # ... existing density, thermalConductivity, etc.

  laserMaterialInteraction:
    title: Aluminum Laser Interaction Dynamics
    sectionDescription: How laser energy interacts with aluminum surfaces during cleaning operations
    _section:
      sectionTitle: Laser-Material Interaction
      sectionDescription: How laser energy absorbs, reflects, and ablates aluminum surfaces during the cleaning process
      icon: zap
      order: 60
      variant: default
    # ... existing absorptionCoefficient, ablationThreshold, etc.

# Add new structure for FAQ
faq:
  _section:
    sectionTitle: Aluminum Laser Cleaning FAQ
    sectionDescription: Expert answers to common questions about laser cleaning aluminum surfaces
    icon: help-circle
    order: 100
    variant: default
  items:
    - question: What safety considerations should we keep in mind when laser cleaning aluminum surfaces, especially regarding its reflective qualities?
      answer: Professionals often deal with aluminum's shiny and reflective surface, which can bounce laser beams around unpredictably and increase risks if not handled properly, so we use full eye protection rated for the specific laser wavelength. Additionally, proper enclosure systems prevent stray reflections from reaching unprotected areas, and we always maintain proper ventilation to handle any particles dispersed during the cleaning process.
      category: safety
    - question: How does thermal conductivity affect laser cleaning parameters for aluminum?
      answer: Aluminum's high thermal conductivity of 237 W/m·K means heat dissipates rapidly across the surface, requiring higher laser power or slower scan speeds compared to materials like stainless steel. This rapid heat transfer actually benefits the cleaning process by preventing localized melting or warping, but it also means you need consistent energy delivery to maintain effective ablation temperatures across the entire cleaning area.
      category: technical
    - question: What contaminants are most effectively removed from aluminum surfaces using laser cleaning?
      answer: Laser cleaning excels at removing oxidation layers, industrial oils, grease, adhesive residues, and light corrosion from aluminum surfaces. The process works particularly well for aerospace and automotive applications where chemical-free cleaning is essential to preserve material properties. However, heavy corrosion or thick paint layers may require multiple passes or alternative methods.
      category: application

# Add new structure for related materials
relationships:
  discovery:
    relatedMaterials:
      _section:
        sectionTitle: Similar Non-Ferrous Metals
        sectionDescription: Other lightweight metals with comparable laser cleaning characteristics and industrial applications
        icon: layers
        order: 110
        variant: default
  # ... existing interactions, operational, safety sections
```

---

## 🚨 Important Notes

1. **FAQ Structure Change**: FAQ must be restructured from flat array to object with `_section` and `items`
2. **Backward Compatibility**: All fields optional - components fall back to defaults
3. **Icon Names**: Use Lucide icon names (wrench, zap, help-circle, layers, etc.)
4. **Order**: Numbers determine display order (50, 60, 100, 110)
5. **Variant**: Use 'default' unless specific styling needed

---

## 📞 Questions?

If you encounter issues:
1. Check MaterialsLayout.tsx line 62-120 for how props are passed
2. Verify _section is at correct nesting level
3. Restart dev server after YAML changes
4. Check browser console for errors
