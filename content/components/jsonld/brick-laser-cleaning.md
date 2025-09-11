I'll help you generate JSON-LD structured data for Brick using frontmatter data. Here's a comprehensive example:

## Frontmatter Data Structure

```yaml
---
title: "Red Clay Brick - Standard Building Material"
description: "High-quality red clay brick for construction projects. Durable, weather-resistant, and perfect for building walls, facades, and structural elements."
price: 0.85
priceCurrency: USD
sku: "BRK-RED-STD-001"
brand: "ClayCraft Bricks"
availability: "InStock"
material: "Clay"
color: "Red"
dimensions: "215mm x 102.5mm x 65mm"
weight: "2.5 kg"
image: "https://example.com/images/red-brick.jpg"
ratingValue: 4.7
reviewCount: 124
manufacturer: "ClayCraft Manufacturing"
productionDate: "2024-03-15"
---
```

## JSON-LD Output

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Red Clay Brick - Standard Building Material",
  "description": "High-quality red clay brick for construction projects. Durable, weather-resistant, and perfect for building walls, facades, and structural elements.",
  "sku": "BRK-RED-STD-001",
  "brand": {
    "@type": "Brand",
    "name": "ClayCraft Bricks"
  },
  "offers": {
    "@type": "Offer",
    "price": 0.85,
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition"
  },
  "material": "Clay",
  "color": "Red",
  "size": "215mm x 102.5mm x 65mm",
  "weight": "2.5 kg",
  "image": "https://example.com/images/red-brick.jpg",
  "manufacturer": {
    "@type": "Organization",
    "name": "ClayCraft Manufacturing"
  },
  "productionDate": "2024-03-15",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": 4.7,
    "reviewCount": 124
  },
  "additionalProperty": [
    {
      "@type": "PropertyValue",
      "name": "Material Type",
      "value": "Fired Clay"
    },
    {
      "@type": "PropertyValue",
      "name": "Compressive Strength",
      "value": "20 MPa"
    },
    {
      "@type": "PropertyValue",
      "name": "Water Absorption",
      "value": "≤ 20%"
    }
  ]
}
```

## Alternative: Multiple Bricks Collection

If you have multiple brick types:

```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "Construction Bricks Collection",
  "description": "Various types of high-quality construction bricks",
  "numberOfItems": 3,
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "item": {
        "@type": "Product",
        "name": "Red Clay Brick",
        "sku": "BRK-RED-001",
        "offers": {
          "@type": "Offer",
          "price": 0.85,
          "priceCurrency": "USD"
        }
      }
    },
    {
      "@type": "ListItem",
      "position": 2,
      "item": {
        "@type": "Product",
        "name": "Concrete Brick

---
Version Log - Generated: 2025-09-10T23:42:32.452846
Material: Brick
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/brick-laser-cleaning.md
---