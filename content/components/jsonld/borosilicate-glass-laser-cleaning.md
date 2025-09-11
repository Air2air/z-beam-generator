Of course. Here is the JSON-LD structured data for a Borosilicate Glass product, generated from a typical set of frontmatter data.

I'll first show you a realistic example of what the frontmatter might look like (in YAML format, commonly used in static site generators like Hugo or Jekyll), and then generate the corresponding JSON-LD.

---

### 1. Example Frontmatter Data (YAML)

```yaml
# This is the data you might have in your markdown file's frontmatter
product_id: "BG-500-001"
name: "Classic Borosilicate Glass Beaker - 500ml"
brand: "Pyrex"
description: "A durable 500ml borosilicate glass beaker, perfect for high-temperature applications and laboratory use. Features excellent chemical resistance and a spout for easy pouring."
image: "https://example.com/images/beaker-500ml.jpg"
sku: "BG500001"
gtin: "012345678905"
offers:
  price: "24.99"
  priceCurrency: "USD"
  availability: "InStock"
  seller: "Science Supply Co."
material: "Borosilicate Glass"
features:
  - "Heat resistant up to 515°C (959°F)"
  - "Low thermal expansion coefficient"
  - "High chemical durability"
  - "Graduated markings for accurate measurement"
  - "Precision spout for clean pouring"
product_weight_grams: 250
height: "15 cm"
width: "8 cm"
depth: "8 cm"
category: "Laboratory Glassware"
rating_value: "4.8"
review_count: 142
url: "https://example.com/products/borosilicate-beaker-500ml"
```

---

### 2. Generated JSON-LD Content

This JSON-LD uses the `Product` schema from schema.org and incorporates all the data from the frontmatter above.

```json
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "@id": "https://example.com/products/borosilicate-beaker-500ml#product",
  "productID": "BG-500-001",
  "name": "Classic Borosilicate Glass Beaker - 500ml",
  "description": "A durable 500ml borosilicate glass beaker, perfect for high-temperature applications and laboratory use. Features excellent chemical resistance and a spout for easy pouring.",
  "image": "https://example.com/images/beaker-500ml.jpg",
  "sku": "BG500001",
  "gtin": "012345678905",
  "brand": {
    "@type": "Brand",
    "name": "Pyrex"
  },
  "category": "Laboratory Glassware",
  "material": "Borosilicate Glass",
  "weight": {
    "@type": "QuantitativeValue",
    "value": "250",
    "unitCode": "GRM"
  },
  "size": "500ml",
  "height": {
    "@type": "QuantitativeValue",
    "value": "15",
    "unitCode": "CMT"
  },
  "width": {
    "@type": "QuantitativeValue",
    "value": "8",
    "unitCode": "CMT"
  },
  "depth": {
    "@type": "QuantitativeValue",
    "value": "8",
    "unitCode": "CMT"
  },
  "url": "https://example.com/products/borosilicate-beaker-500ml",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "142"
  },
  "offers

---
Version Log - Generated: 2025-09-10T23:33:45.733283
Material: Borosilicate Glass
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/borosilicate-glass-laser-cleaning.md
---