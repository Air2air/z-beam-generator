Of course. Here is the JSON-LD structured data for a `Tempered Glass` product, generated from typical frontmatter data.

I'll first show you an example of what the frontmatter might look like (in YAML format, commonly used in static site generators), and then generate the corresponding JSON-LD.

---

### 1. Example Frontmatter Data (YAML)

This is the kind of data you might find in a markdown file for a product page.

```yaml
---
title: "iPhone 14 Pro Max Tempered Glass Screen Protector"
sku: "TGL-IP14PM-001"
description: "9H hardness, ultra-clear, anti-fingerprint tempered glass screen protector for iPhone 14 Pro Max. Easy installation kit included."
price: "19.99"
priceCurrency: "USD"
brand: "ShieldGlass"
availability: "InStock"
productImage: "https://example.com/images/ip14pm-tempered-glass.jpg"
ratingValue: "4.8"
reviewCount: "142"
productCategory: "Phone Accessories"
compatibleWith: "iPhone 14 Pro Max"
material: "Tempered Glass"
hardness: "9H"
thickness: "0.33mm"
features:
  - "99.9% High Transparency"
  - "Oleophobic Coating (Anti-Smudge)"
  - "Bubble-Free Installation"
  - "Shatter-Resistant"
  - "HD Clarity"
---
```

---

### 2. Generated JSON-LD Content

Based on the frontmatter above, here is the corresponding JSON-LD script. This uses the `Product` schema from schema.org, which is the most appropriate type for an item for sale.

```json
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "name": "iPhone 14 Pro Max Tempered Glass Screen Protector",
  "sku": "TGL-IP14PM-001",
  "description": "9H hardness, ultra-clear, anti-fingerprint tempered glass screen protector for iPhone 14 Pro Max. Easy installation kit included.",
  "brand": {
    "@type": "Brand",
    "name": "ShieldGlass"
  },
  "image": "https://example.com/images/ip14pm-tempered-glass.jpg",
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/products/tempered-glass-ip14pm", // You would add your product URL here
    "priceCurrency": "USD",
    "price": "19.99",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "142"
  },
  "category": "Phone Accessories",
  "additionalProperty": [
    {
      "@type": "PropertyValue",
      "name": "Compatible With",
      "value": "iPhone 14 Pro Max"
    },
    {
      "@type": "PropertyValue",
      "name": "Material",
      "value": "Tempered Glass"
    },
    {
      "@type": "PropertyValue",
      "name": "Hardness",
      "value": "9H"
    },
    {
      "@type": "PropertyValue",
      "name": "Thickness",
      "value": "0.33mm"
    }
  ],
  "keywords": "tempered glass, screen protector, iPhone 14 Pro Max, anti-scratch, 9H hardness" // A good place for SEO keywords not covered by properties
}
```

---



---
Version Log - Generated: 2025-09-10T23:41:24.227307
Material: Tempered Glass
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/tempered-glass-laser-cleaning.md
---