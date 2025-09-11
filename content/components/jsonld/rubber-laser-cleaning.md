Of course. Here is the JSON-LD structured data for a `Rubber` product, generated from typical frontmatter data you might find in a CMS or static site generator.

I'll first show you an example of what the frontmatter might look like, and then generate the corresponding JSON-LD.

---

### Example Frontmatter (YAML)

This is the data a content editor might provide.

```yaml
---
title: "Premium Natural Rubber Sheet - 1/4 inch"
sku: "RNB-NAT-025"
description: "High-quality, sustainably sourced natural rubber sheet. Perfect for gaskets, seals, vibration damping, and DIY projects."
price: 49.99
priceCurrency: "USD"
availability: "InStock"
brand: "ElastoPro"
productType: "MaterialSheet"
material: "Natural Rubber"
width: "24 in"
length: "24 in"
thickness: "0.25 in"
weight: "5.5 lb"
image: "/images/products/rubber-sheet-natural.jpg"
ratingValue: 4.7
reviewCount: 128
---
```

---

### Generated JSON-LD Code

This is the structured data output based on the frontmatter above.

```json
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "name": "Premium Natural Rubber Sheet - 1/4 inch",
  "image": "/images/products/rubber-sheet-natural.jpg",
  "description": "High-quality, sustainably sourced natural rubber sheet. Perfect for gaskets, seals, vibration damping, and DIY projects.",
  "sku": "RNB-NAT-025",
  "brand": {
    "@type": "Brand",
    "name": "ElastoPro"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://www.yourwebsite.com/products/premium-natural-rubber", // You would need to add this URL
    "priceCurrency": "USD",
    "price": 49.99,
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "Organization",
      "name": "Your Company Name" // You would need to add this
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": 4.7,
    "reviewCount": 128
  },
  "additionalProperty": [
    {
      "@type": "PropertyValue",
      "name": "material",
      "value": "Natural Rubber"
    },
    {
      "@type": "PropertyValue",
      "name": "width",
      "value": "24 in"
    },
    {
      "@type": "PropertyValue",
      "name": "length",
      "value": "24 in"
    },
    {
      "@type": "PropertyValue",
      "name": "thickness",
      "value": "0.25 in"
    },
    {
      "@type": "PropertyValue",
      "name": "weight",
      "value": "5.5 lb"
    }
  ]
}
```

---

### How to Use This in Your HTML

You would place this JSON-LD code within a `<script>` tag in the `<head>` or `<body>` of your HTML page.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "name": "Premium Natural Rubber Sheet - 1/4 inch",
  ... // The rest of the JSON from above
}
</script>
```

---

### Key Explanations:

1.  **`@context` & `@type`**: Define the vocabulary (Schema.org) and the type

---
Version Log - Generated: 2025-09-10T23:26:04.394763
Material: Rubber
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/rubber-laser-cleaning.md
---