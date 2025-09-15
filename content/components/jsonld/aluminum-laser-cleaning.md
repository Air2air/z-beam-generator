Of course. Here is the JSON-LD structured data for an aluminum product, generated from a set of example frontmatter data.

### 1. Example Frontmatter Data

First, let's assume this is the data you have in your frontmatter (in YAML format, for example):

```yaml
id: AL-6061-T6-SHEET-12x12
name: 6061-T6 Aluminum Sheet
description: A high-strength, heat-treatable aluminum alloy sheet, ideal for structural and general purpose applications. Offers good corrosion resistance and machinability.
sku: ALUM-6061-12x12x0.125
brand:
  name: Coastal Metals
  url: https://www.coastalmetals.example
offers:
  price: 45.99
  priceCurrency: USD
  availability: https://schema.org/InStock
  seller:
    name: Metal Supermarkets Online
image: https://www.example.com/images/aluminum-6061-sheet.jpg
productID: AL-6061-T6-SHEET-12x12
material: Aluminum Alloy 6061-T6
weight:
  value: 1.75
  unit: lb
width:
  value: 12
  unit: inches
length:
  value: 12
  unit: inches
thickness:
  value: 0.125
  unit: inches
```

---

### 2. Generated JSON-LD

This JSON-LD code uses the data from the frontmatter above. It combines `Product` and `Offer` schemas, which is the standard way to represent products for sale for search engines like Google.

```json
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "@id": "https://www.yourwebsite.example/product/#AL-6061-T6-SHEET-12x12",
  "productID": "AL-6061-T6-SHEET-12x12",
  "sku": "ALUM-6061-12x12x0.125",
  "name": "6061-T6 Aluminum Sheet",
  "description": "A high-strength, heat-treatable aluminum alloy sheet, ideal for structural and general purpose applications. Offers good corrosion resistance and machinability.",
  "brand": {
    "@type": "Brand",
    "name": "Coastal Metals",
    "url": "https://www.coastalmetals.example"
  },
  "image": "https://www.example.com/images/aluminum-6061-sheet.jpg",
  "material": "Aluminum Alloy 6061-T6",
  "size": "12\" x 12\" x 0.125\"",
  "weight": {
    "@type": "QuantitativeValue",
    "value": "1.75",
    "unitCode": "LBR"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://www.yourwebsite.example/product/aluminum-6061-sheet/",
    "priceCurrency": "USD",
    "price": "45.99",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "Organization",
      "name": "Metal Supermarkets Online"
    },
    "itemOffered": {
      "@type": "Product",
      "name": "6061-T6 Aluminum Sheet",
      "sku": "ALUM-6061-12x12x0.125",
      "@id": "https://www.yourwebsite.example/product/#AL-6061-T6-SHEET-12x12"
    }
  }
}
```

---

### 3. Key Explanations and Best Practices:

1.  **

---
Version Log - Generated: 2025-09-14T23:24:07.466396
Material: aluminum
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/aluminum-laser-cleaning.md
---