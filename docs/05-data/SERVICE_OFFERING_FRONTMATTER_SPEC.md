# Service Offering Frontmatter Specification

## Purpose

Add `serviceOffering` field to material frontmatter files to enable Service/Product JSON-LD schema generation for SEO rich snippets. Pricing is already centralized in `app/config/site.ts` - this spec only adds material-specific service details.

---

## Frontmatter Field to Add

Add the following `serviceOffering` object to each material's YAML frontmatter file:

```yaml
serviceOffering:
  enabled: true
  type: "professionalCleaning"
  materialSpecific:
    estimatedHoursMin: 1
    estimatedHoursTypical: 3
    targetContaminants:
      - "Primary contaminant"
      - "Secondary contaminant"
    notes: "Optional material-specific notes"
```

---

## Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | Yes | Always `true` to enable service schema |
| `type` | string | Yes | Either `"professionalCleaning"` or `"equipmentRental"` |
| `materialSpecific.estimatedHoursMin` | number | Yes | Minimum hours for typical job (usually 1) |
| `materialSpecific.estimatedHoursTypical` | number | Yes | Typical hours based on material difficulty |
| `materialSpecific.targetContaminants` | array | Yes | List of contaminants this service removes |
| `materialSpecific.notes` | string | No | Material-specific safety or process notes |

---

## Pricing Reference (DO NOT DUPLICATE)

Pricing is already defined in `app/config/site.ts`:

```typescript
pricing: {
  professionalCleaning: {
    hourlyRate: 390,
    currency: 'USD',
    label: 'Professional Laser Cleaning',
    unit: 'hour'
  },
  equipmentRental: {
    hourlyRate: 320,
    currency: 'USD',
    label: 'Equipment Rental',
    unit: 'hour'
  }
}
```

The schema generator will automatically pull pricing from this config based on `serviceOffering.type`.

---

## Estimated Hours by Material Difficulty

| Difficulty | Materials | `estimatedHoursTypical` |
|------------|-----------|-------------------------|
| **Easy** | Aluminum, Copper, Brass, Bronze | 2-3 |
| **Standard** | Steel, Iron, Cast Iron, Zinc | 3-5 |
| **Complex** | Titanium, Inconel, Stainless Steel, Nickel Alloys | 5-8 |
| **Delicate** | Plastics (ABS, PMMA), Carbon Fiber, Composites | 2-3 |
| **Heavy** | Concrete, Stone, Masonry, Brick | 4-8 |
| **Precision** | Glass, Ceramics, Alumina | 2-4 |
| **Careful** | Wood (Hardwood, Softwood) | 2-4 |

---

## Target Contaminants by Material Category

### Metals - Ferrous
- Rust and corrosion
- Mill scale
- Paint and coatings
- Weld discoloration
- Heat treatment scale

### Metals - Non-Ferrous (Aluminum, Copper, etc.)
- Oxide layer
- Paint and coatings
- Grease and oils
- Anodizing
- Tarnish/patina

### Metals - Refractory (Titanium, Inconel, etc.)
- Oxide scale
- Heat discoloration
- Alpha case
- Thermal barrier coatings

### Plastics & Composites
- Surface contamination
- Mold release agents
- Adhesive residue
- Paint overspray

### Stone & Masonry
- Efflorescence
- Paint and graffiti
- Biological growth
- Soot and smoke damage

### Wood
- Char and weathering
- Paint and finish
- Stain
- Surface contamination

---

## Complete Examples

### Example 1: Aluminum (Easy - Non-Ferrous Metal)

```yaml
serviceOffering:
  enabled: true
  type: "professionalCleaning"
  materialSpecific:
    estimatedHoursMin: 1
    estimatedHoursTypical: 3
    targetContaminants:
      - "Aluminum oxide layer"
      - "Paint and coatings"
      - "Grease and oils"
      - "Anodizing removal"
    notes: "Low power settings required due to high reflectivity (91%)"
```

### Example 2: Steel (Standard - Ferrous Metal)

```yaml
serviceOffering:
  enabled: true
  type: "professionalCleaning"
  materialSpecific:
    estimatedHoursMin: 1
    estimatedHoursTypical: 4
    targetContaminants:
      - "Rust and corrosion"
      - "Mill scale"
      - "Paint and coatings"
      - "Weld discoloration"
    notes: "Standard 1064nm wavelength optimal for iron oxide absorption"
```

### Example 3: Titanium (Complex - Refractory Metal)

```yaml
serviceOffering:
  enabled: true
  type: "professionalCleaning"
  materialSpecific:
    estimatedHoursMin: 2
    estimatedHoursTypical: 6
    targetContaminants:
      - "Titanium oxide scale"
      - "Alpha case layer"
      - "Heat discoloration"
      - "Thermal barrier coatings"
    notes: "Controlled atmosphere may be required to prevent re-oxidation"
```

### Example 4: ABS Plastic (Delicate - Polymer)

```yaml
serviceOffering:
  enabled: true
  type: "professionalCleaning"
  materialSpecific:
    estimatedHoursMin: 1
    estimatedHoursTypical: 2
    targetContaminants:
      - "Surface contamination"
      - "Mold release agents"
      - "Adhesive residue"
      - "Paint overspray"
    notes: "Low fluence required - stay below 2.5 J/cm² to prevent melting"
```

### Example 5: Concrete (Heavy - Masonry)

```yaml
serviceOffering:
  enabled: true
  type: "professionalCleaning"
  materialSpecific:
    estimatedHoursMin: 2
    estimatedHoursTypical: 6
    targetContaminants:
      - "Efflorescence"
      - "Paint and coatings"
      - "Oil stains"
      - "Biological growth"
    notes: "Higher power settings tolerated - porous surface requires multiple passes"
```

---

## File Location

Add to existing frontmatter files in:
```
frontmatter/materials/{material-slug}-laser-cleaning.yaml
```

### Placement in File

Add `serviceOffering` after existing fields like `machineSettings` and `faq`:

```yaml
title: "Aluminum Laser Cleaning"
description: "..."
category: "Metal"
subcategory: "Non-Ferrous"

# ... existing fields ...

machineSettings:
  # ... existing settings ...

faq:
  # ... existing FAQ ...

# ADD HERE:
serviceOffering:
  enabled: true
  type: "professionalCleaning"
  materialSpecific:
    estimatedHoursMin: 1
    estimatedHoursTypical: 3
    targetContaminants:
      - "Aluminum oxide layer"
      - "Paint and coatings"
    notes: "Low power settings required"
```

---

## Schema Generation

Once frontmatter includes `serviceOffering`, the SchemaFactory will automatically generate:

1. **Service Schema** with:
   - Service name: `"{MaterialName} Laser Cleaning Service"`
   - Price: From `SITE_CONFIG.pricing.professionalCleaning.hourlyRate`
   - Currency: From `SITE_CONFIG.pricing.professionalCleaning.currency`
   - Area served: From `SITE_CONFIG.address`
   - Provider: Z-Beam organization details

2. **Offer Schema** (nested) with:
   - Price specification (hourly rate)
   - Availability: `"InStock"` / `"ByAppointment"`

---

## Validation

After adding to frontmatter, verify with:

```bash
npm run validate:seo-infrastructure
```

Expected output:
```
✅ Valid Service schema on Material Page
```

---

## Notes for Generator

1. **DO NOT hardcode prices** - always reference `SITE_CONFIG.pricing`
2. **Use material properties** to determine difficulty and estimated hours
3. **Pull contaminants** from existing `machineSettings.contaminantType` if available
4. **Notes field** should reference relevant `machineSettings` parameters (fluence limits, power settings)
5. **All materials get `professionalCleaning`** type unless specifically equipment-focused
