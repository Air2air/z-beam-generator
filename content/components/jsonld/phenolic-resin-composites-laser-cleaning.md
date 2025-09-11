Of course. Here is the JSON-LD structured data for a webpage about "Phenolic Resin Composites," generated based on common frontmatter data you might find on a technical product page.

This example uses the `Product` and `HowTo` schemas to cover both the material's properties and potential usage instructions.

### 1. Standard Product/Technical Data Page

This is the most common use case, focusing on the material as a product with specific properties.

**Hypothetical Frontmatter Data:**
```yaml
title: "Novolac Phenolic Resin Composite PF-8000"
description: "High-performance, heat-resistant phenolic resin composite reinforced with carbon fiber. Ideal for aerospace and automotive braking applications."
productID: "PF-8000-CF"
brand: "PolymerTech Innovations"
manufacturer: "PolymerTech Innovations"
materialType: "Thermoset Composite"
reinforcement: "Carbon Fiber"
application: "Brake pads, heat shields, electrical insulators"
image: "https://example.com/images/pf-8000-composite.jpg"
datePublished: "2023-10-15"
dateModified: "2024-05-22"
author: "Dr. Emily Chen"
```

**Generated JSON-LD:**

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "@id": "https://example.com/composites/pf-8000#product",
  "name": "Novolac Phenolic Resin Composite PF-8000",
  "description": "High-performance, heat-resistant phenolic resin composite reinforced with carbon fiber. Ideal for aerospace and automotive braking applications.",
  "sku": "PF-8000-CF",
  "brand": {
    "@type": "Brand",
    "name": "PolymerTech Innovations"
  },
  "manufacturer": {
    "@type": "Organization",
    "name": "PolymerTech Innovations"
  },
  "image": "https://example.com/images/pf-8000-composite.jpg",
  "material": "Phenolic Resin, Carbon Fiber",
  "additionalProperty": [
    {
      "@type": "PropertyValue",
      "name": "Reinforcement Type",
      "value": "Carbon Fiber"
    },
    {
      "@type": "PropertyValue",
      "name": "Material Type",
      "value": "Thermoset Composite"
    },
    {
      "@type": "PropertyValue",
      "name": "Max Operating Temperature",
      "value": "300°C",
      "unitCode": "CEL"
    },
    {
      "@type": "PropertyValue",
      "name": "Tensile Strength",
      "value": "415",
      "unitCode": "MPA"
    }
  ],
  "keywords": "phenolic resin, composite, carbon fiber, heat-resistant, brake pads, thermoset",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/composites/pf-8000"
  }
}
```

---

### 2. Page Including Processing Instructions (HowTo)

If the page includes a guide on how to use or process the material (e.g., molding instructions), you can combine schemas.

**Hypothetical Frontmatter Data (extended):**
```yaml
title: "How to Mold Phenolic Resin Composites: A Technical Guide"
description: "Step-by-step instructions for compression molding our Novolac PF-8000 phenolic composite. Learn about temperature, pressure, and cure cycles."
howtoTitle: "Compression Molding Guide for PF-8000"
supplies: ["PF-8000 Preform", "Mold Release Agent", "Heated Compression Mold"]
tools: ["Compression Molding Press", "Ther

---
Version Log - Generated: 2025-09-10T23:23:51.069780
Material: Phenolic Resin Composites
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/phenolic-resin-composites-laser-cleaning.md
---