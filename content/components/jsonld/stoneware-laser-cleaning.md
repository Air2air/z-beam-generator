Of course. Here is the JSON-LD structured data for a Stoneware product, generated from typical frontmatter data you might find in a CMS or static site generator.

I'll first show you an example of what the frontmatter might look like, and then generate the corresponding JSON-LD.

---

### 1. Example Frontmatter (YAML)

This is the kind of data you might have in your content's frontmatter.

```yaml
---
title: "Artisan Hand-Painted Stoneware Bowl"
sku: "STW-BWL-2024-L"
description: "A beautiful, microwave and dishwasher-safe stoneware bowl, featuring a unique hand-painted blue glaze. Perfect for everyday meals or as a decorative piece."
price: 45.99
priceCurrency: "USD"
availability: "InStock"
brand: "ClayCraft Pottery"
image: "/images/products/stoneware-bowl-blue.jpg"
ratingValue: 4.7
reviewCount: 128
productCategory: "Home & Kitchen > Kitchen & Dining > Tableware > Serveware > Bowls"
material: "Stoneware"
color: "Cobalt Blue"
pattern: "Hand-Painted"
width: "8in"
height: "3in"
depth: "8in"
weight: "1.5lb"
---
```

---

### 2. Generated JSON-LD

Based on the frontmatter above, here is the corresponding JSON-LD script. This uses Schema.org's `Product` type and is optimized for search engines like Google.

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "productID": "STW-BWL-2024-L",
  "sku": "STW-BWL-2024-L",
  "name": "Artisan Hand-Painted Stoneware Bowl",
  "description": "A beautiful, microwave and dishwasher-safe stoneware bowl, featuring a unique hand-painted blue glaze. Perfect for everyday meals or as a decorative piece.",
  "image": "https://yourwebsite.com/images/products/stoneware-bowl-blue.jpg",
  "brand": {
    "@type": "Brand",
    "name": "ClayCraft Pottery"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://yourwebsite.com/products/stoneware-bowl-blue",
    "priceCurrency": "USD",
    "price": 45.99,
    "priceValidUntil": "2024-12-31",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition",
    "shippingDetails": {
      "@type": "OfferShippingDetails",
      "shippingRate": {
        "@type": "MonetaryAmount",
        "value": 5.99,
        "currency": "USD"
      },
      "shippingDestination": {
        "@type": "DefinedRegion",
        "addressCountry": "US"
      },
      "deliveryTime": {
        "@type": "ShippingDeliveryTime",
        "handlingTime": {
          "@type": "QuantitativeValue",
          "minValue": 1,
          "maxValue": 2
        },
        "transitTime": {
          "@type": "QuantitativeValue",
          "minValue": 3,
          "maxValue": 5
        }
      }
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.7",
    "reviewCount": "128"
  },
  "category": "Home & Kitchen > Kitchen & Dining > Tableware > Serveware > Bowls",
  "material": "Stoneware",
  "color": "Cobalt Blue",
  "pattern":

---
Version Log - Generated: 2025-09-10T23:17:46.117904
Material: Stoneware
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/stoneware-laser-cleaning.md
---