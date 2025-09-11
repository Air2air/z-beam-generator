Of course. Here is the JSON-LD structured data for a "Polyester Resin Composite" product, generated based on common frontmatter data fields you might find in a CMS or product information management system.

I'll first show you a typical example of the frontmatter data, and then generate the JSON-LD from it.

---

### 1. Example Frontmatter Data (Hypothetical)

This is the kind of data you might have in your content's frontmatter (in YAML format for clarity).

```yaml
---
title: "EcoPoly 500 - High-Strength Polyester Resin Composite"
sku: "EP500-HS-GF"
description: "A general-purpose, orthophthalic polyester resin composite reinforced with E-glass fibers. Ideal for marine applications, automotive parts, and industrial fabrication."
image: "https://example.com/images/ep500-hs-composite.jpg"
brand: "CompositeMaterials Inc."
material: "Polyester Resin, E-Glass Fiber"
weight_kg: 1.2
price: 89.99
priceCurrency: "USD"
availability: "InStock"
product_category: "Polymer Composites"
strength_tensile_mpa: 300
strength_flexural_mpa: 450
application: "Marine, Automotive, Industrial"
---
```

---

### 2. Generated JSON-LD Content

Based on the frontmatter above, here is the corresponding JSON-LD script, using Schema.org's `Product` and additional types for depth.

```json
{
  "@context": "https://schema.org/",
  "@type": ["Product", "ChemicalSubstance"],
  "name": "EcoPoly 500 - High-Strength Polyester Resin Composite",
  "sku": "EP500-HS-GF",
  "description": "A general-purpose, orthophthalic polyester resin composite reinforced with E-glass fibers. Ideal for marine applications, automotive parts, and industrial fabrication.",
  "image": "https://example.com/images/ep500-hs-composite.jpg",
  "brand": {
    "@type": "Brand",
    "name": "CompositeMaterials Inc."
  },
  "material": "Polyester Resin, E-Glass Fiber",
  "weight": "1.2 kg",
  "offers": {
    "@type": "Offer",
    "availability": "https://schema.org/InStock",
    "price": "89.99",
    "priceCurrency": "USD",
    "seller": {
      "@type": "Organization",
      "name": "CompositeMaterials Inc."
    }
  },
  "category": "Polymer Composites",
  "additionalProperty": [
    {
      "@type": "PropertyValue",
      "name": "Tensile Strength",
      "value": "300",
      "unitCode": "MPA",
      "valueReference": "https://schema.org/QuantitativeValue"
    },
    {
      "@type": "PropertyValue",
      "name": "Flexural Strength",
      "value": "450",
      "unitCode": "MPA",
      "valueReference": "https://schema.org/QuantitativeValue"
    }
  ],
  "keywords": "polyester resin, composite, fiberglass, marine composite, automotive parts, industrial fabrication"
}
```

---

### 3. Explanation of Key Schema Choices:

*   **`@type`: [`Product`, `ChemicalSubstance`]**: Using multiple types is valid in JSON-LD. `Product` is the primary type, and `ChemicalSubstance` adds a layer of specificity that is highly relevant for search engines and knowledge graphs when dealing with materials.
*   **`brand`**: Structured as a nested `Brand` object, which is better than a simple string.
*   **`off

---
Version Log - Generated: 2025-09-10T23:24:57.119331
Material: Polyester Resin Composites
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/polyester-resin-composites-laser-cleaning.md
---