Of course. Here is the JSON-LD structured data for a "Float Glass" product page, generated based on common frontmatter data you might find on such a page.

I'll first show you an example of what the frontmatter might look like (in YAML format), and then generate the corresponding JSON-LD.

---

### Example Frontmatter (YAML)

```yaml
title: "Clear Float Glass - 6mm Thickness"
description: "Premium quality clear float glass, perfect for windows, doors, and furniture. Available in 6mm thickness for enhanced strength and clarity."
product_id: "FG-CLR-6MM"
sku: "FLOAT-6-CLEAR"
brand: "GlassPro"
price: 45.99
price_currency: "USD"
availability: "InStock"
images:
  - "/images/float-glass-clear-6mm.jpg"
  - "/images/float-glass-packaging.jpg"
product_type: "Building Material > Glass & Glazing > Sheet Glass"
rating_value: 4.7
review_count: 128
weight_value: 15.5
weight_unit: "kg"
width_value: 1220
width_unit: "mm"
height_value: 1830
height_unit: "mm"
depth_value: 6
depth_unit: "mm"
material: "Soda-lime Silicate"
color: "Clear"
```

---

### Generated JSON-LD

This JSON-LD uses Schema.org's `Product` type and includes relevant properties for an e-commerce site.

```json
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "name": "Clear Float Glass - 6mm Thickness",
  "description": "Premium quality clear float glass, perfect for windows, doors, and furniture. Available in 6mm thickness for enhanced strength and clarity.",
  "productID": "FG-CLR-6MM",
  "sku": "FLOAT-6-CLEAR",
  "brand": {
    "@type": "Brand",
    "name": "GlassPro"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://www.yourglasswebsite.com/products/float-glass-6mm", // You should add this URL
    "priceCurrency": "USD",
    "price": 45.99,
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition",
    "shippingDetails": {
      "@type": "OfferShippingDetails",
      "shippingRate": {
        "@type": "MonetaryAmount",
        "value": 0,
        "currency": "USD"
      },
      "shippingDestination": {
        "@type": "DefinedRegion",
        "addressCountry": "US"
      }
    }
  },
  "image": [
    "https://www.yourglasswebsite.com/images/float-glass-clear-6mm.jpg",
    "https://www.yourglasswebsite.com/images/float-glass-packaging.jpg"
  ],
  "category": "Building Material > Glass & Glazing > Sheet Glass",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": 4.7,
    "reviewCount": 128
  },
  "material": "Soda-lime Silicate",
  "color": "Clear",
  "additionalProperty": [
    {
      "@type": "PropertyValue",
      "name": "Thickness",
      "value": "6",
      "unitCode": "MMT"
    },
    {
      "@type": "PropertyValue",
      "name": "Width",
      "value": "1220",
      "unitCode": "MMT"
    },


---
Version Log - Generated: 2025-09-10T23:34:52.880787
Material: Float Glass
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/float-glass-laser-cleaning.md
---