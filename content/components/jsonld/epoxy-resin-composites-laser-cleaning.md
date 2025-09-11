Of course. Here is a comprehensive JSON-LD structured data snippet for an Epoxy Resin Composite product, generated based on common frontmatter data you might find on a product page.

I'll first show you an example of what the frontmatter might look like (in YAML format, common in systems like Hugo or Jekyll), and then generate the corresponding JSON-LD.

---

### 1. Example Frontmatter Data (YAML)

```yaml
---
title: "ProSeries EPX-2000 | High-Strength Epoxy Resin Composite"
description: "A two-part epoxy resin system with carbon fiber reinforcement for high-performance automotive and aerospace applications. Offers exceptional tensile strength and thermal stability."
product_id: "EPX-2000-CF"
sku: "EPX2000-5KG-KIT"
brand:
  name: "CompositeMaterials Inc."
  logo: "/images/logo-cmi.png"
manufacturer: "CompositeMaterials Inc."
image: "/images/products/epx-2000-composite-kit.jpg"
price: 249.99
priceCurrency: "USD"
availability: "InStock"
weight_value: 5
weight_unit: "kg"
material: "Epoxy Resin, Carbon Fiber"
strength_tensile: "900 MPa"
strength_compressive: "700 MPa"
max_operating_temp: "180°C"
application: "Structural components, automotive parts, drone frames, custom fabrication"
url: "/products/epoxy-composites/epx-2000/"
releaseDate: "2023-05-15"
---
```

### 2. Generated JSON-LD Code

This code uses the `Product` and `Offer` schemas, and incorporates specific properties for a composite material.

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "@id": "https://yourdomain.com/products/epoxy-composites/epx-2000/#product",
  "name": "ProSeries EPX-2000 | High-Strength Epoxy Resin Composite",
  "description": "A two-part epoxy resin system with carbon fiber reinforcement for high-performance automotive and aerospace applications. Offers exceptional tensile strength and thermal stability.",
  "sku": "EPX2000-5KG-KIT",
  "gtin": "EPX-2000-CF", // Often the productID can serve as a GTIN
  "brand": {
    "@type": "Brand",
    "name": "CompositeMaterials Inc.",
    "logo": "https://yourdomain.com/images/logo-cmi.png"
  },
  "manufacturer": {
    "@type": "Organization",
    "name": "CompositeMaterials Inc."
  },
  "image": "https://yourdomain.com/images/products/epx-2000-composite-kit.jpg",
  "offers": {
    "@type": "Offer",
    "@id": "https://yourdomain.com/products/epoxy-composites/epx-2000/#offer",
    "url": "https://yourdomain.com/products/epoxy-composites/epx-2000/",
    "priceCurrency": "USD",
    "price": 249.99,
    "priceValidUntil": "2024-12-31",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition",
    "shippingDetails": {
      "@type": "OfferShippingDetails",
      "shippingWeight": {
        "@type": "QuantitativeValue",
        "value": "5",
        "unitCode": "KGM"
      }
    }
  },
  "additionalProperty": [
    {
      "@type": "PropertyValue",
      "name": "Material Composition",
      "value": "Epoxy Resin, Carbon Fiber"


---
Version Log - Generated: 2025-09-10T23:21:08.971487
Material: Epoxy Resin Composites
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/epoxy-resin-composites-laser-cleaning.md
---