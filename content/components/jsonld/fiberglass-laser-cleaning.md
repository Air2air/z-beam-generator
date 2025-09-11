Of course. Here is the JSON-LD structured data for a `Fiberglass` product, generated from a set of hypothetical frontmatter data.

I'll first present the frontmatter data (as it might appear in a CMS or markdown file), then the resulting JSON-LD, and finally an explanation of the key properties.

---

### 1. Example Frontmatter Data (Source)

This is the data we are using to generate the JSON-LD.

```yaml
# Frontmatter for: /products/industrial-fiberglass-mat
title: "EcoCoat 450 Industrial Grade Fiberglass Mat"
description: "A high-strength, non-woven fiberglass mat designed for marine, automotive, and construction composite applications. Excellent resin compatibility."
sku: "FBG-MAT-450-100"
brand: "EcoCoat Composites"
price: "89.99"
priceCurrency: "USD"
weight: "4.2"
weightUnit: "kg"
width: "1.2"
height: "50"
depth: "0.01"
widthUnit: "m"
heightUnit: "m"
depthUnit: "m"
images:
  - "/images/fiberglass-mat-1.jpg"
  - "/images/fiberglass-mat-closeup.jpg"
availability: "InStock"
material: "Fiberglass"
productID: "450-100-2023"
url: "https://www.example.com/products/industrial-fiberglass-mat"
```

---

### 2. Generated JSON-LD Output

This is the JSON-LD code you would place in the `<head>` of your HTML page.

```json
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "name": "EcoCoat 450 Industrial Grade Fiberglass Mat",
  "description": "A high-strength, non-woven fiberglass mat designed for marine, automotive, and construction composite applications. Excellent resin compatibility.",
  "sku": "FBG-MAT-450-100",
  "brand": {
    "@type": "Brand",
    "name": "EcoCoat Composites"
  },
  "offers": {
    "@type": "Offer",
    "price": "89.99",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "https://www.example.com/products/industrial-fiberglass-mat",
    "shippingDetails": {
      "@type": "OfferShippingDetails",
      "shippingRate": {
        "@type": "MonetaryAmount",
        "value": "0",
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
          "minValue": "1",
          "maxValue": "2"
        },
        "transitTime": {
          "@type": "QuantitativeValue",
          "minValue": "3",
          "maxValue": "5"
        }
      }
    }
  },
  "image": [
    "https://www.example.com/images/fiberglass-mat-1.jpg",
    "https://www.example.com/images/fiberglass-mat-closeup.jpg"
  ],
  "productID": "450-100-2023",
  "material": "Fiberglass",
  "weight": {
    "@type": "QuantitativeValue",
    "value": "4.2",
    "unitCode": "KGM"
  },
  "additionalProperty": [
    {
      "@type": "PropertyValue",
      "name": "Width",
      "value

---
Version Log - Generated: 2025-09-10T23:22:16.862385
Material: Fiberglass
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/fiberglass-laser-cleaning.md
---