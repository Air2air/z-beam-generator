Of course. Here is the JSON-LD structured data (Schema.org) for a Quartz Glass product, generated from typical frontmatter data you might find in a headless CMS or static site generator.

### 1. Frontmatter Data Example

First, let's define the frontmatter data that a content editor might use. This is typically in YAML or TOML format at the top of a markdown file.

```yaml
---
title: "Premium Fused Quartz Glass Tube - 25mm OD x 1000mm L"
sku: "QG-T25-1000"
description: "High-purity fused quartz glass tube for laboratory and industrial applications. Features exceptional thermal shock resistance and UV transparency."
price: 249.99
priceCurrency: "USD"
brand: "QuartzPro"
material: "Fused Silica (SiO₂)"
productID: "P-98765"
availability: "InStock"
ratingValue: 4.8
reviewCount: 47
image: "/images/products/quartz-tube-25mm.jpg"
productType: "LaboratorySupplies"
specifications:
  - name: "Outer Diameter"
    value: "25 mm"
  - name: "Length"
    value: "1000 mm"
  - name: "Wall Thickness"
    value: "1.5 mm"
  - name: "Purity"
    value: "99.995%"
  - name: "Thermal Expansion Coefficient"
    value: "5.5 x 10⁻⁷ /°C"
  - name: "Softening Point"
    value: "1683°C"
features:
  - "Excellent optical transmission from UV to IR"
  - "Very low thermal expansion"
  - "High chemical purity and resistance"
  - "Resists devitrification"
  - "Good electrical insulator"
---
```

### 2. Generated JSON-LD Content

Based on the frontmatter above, here is the corresponding JSON-LD script. This code should be placed in the `<head>` section of your HTML page.

```json
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "name": "Premium Fused Quartz Glass Tube - 25mm OD x 1000mm L",
  "sku": "QG-T25-1000",
  "description": "High-purity fused quartz glass tube for laboratory and industrial applications. Features exceptional thermal shock resistance and UV transparency.",
  "brand": {
    "@type": "Brand",
    "name": "QuartzPro"
  },
  "image": "/images/products/quartz-tube-25mm.jpg",
  "offers": {
    "@type": "Offer",
    "url": "https://www.yourwebsite.com/products/quartz-glass-tube-25mm", // You should add this URL
    "priceCurrency": "USD",
    "price": 249.99,
    "itemCondition": "https://schema.org/NewCondition",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "Organization",
      "name": "Your Company Name" // You should add your company name
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": 4.8,
    "reviewCount": 47
  },
  "material": "Fused Silica (SiO₂)",
  "productID": "P-98765",
  "additionalProperty": [
    {
      "@type": "PropertyValue",
      "name": "Outer Diameter",
      "value": "25 mm"
    },
    {
      "@type": "PropertyValue

---
Version Log - Generated: 2025-09-10T23:39:11.667833
Material: Quartz Glass
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/quartz-glass-laser-cleaning.md
---