Of course. Here is the JSON-LD structured data for a "Lead Crystal" product page, generated from typical frontmatter data. I'll first show you the frontmatter example, then the resulting JSON-LD, and finally explain the key components.

---

### Example Frontmatter Data (YAML)

This is the kind of data you might find at the top of your Markdown file or CMS entry for a lead crystal product.

```yaml
---
title: "Athena Premium Lead Crystal Decanter"
sku: "LCD-ATH-2024"
description: "Handcrafted decanter made from 24% lead crystal. Features a classic diamond-cut pattern and a sterling silver stopper. Perfect for whiskey, brandy, or as an elegant gift."
image: 
  - "/images/products/athena-decanter-1.jpg"
  - "/images/products/athena-decanter-2.jpg"
brand: 
  name: "Crystal Heritage"
  logo: "/logos/crystal-heritage-logo.png"
offers:
  price: "129.99"
  priceCurrency: "USD"
  availability: "InStock"
  itemCondition: "NewCondition"
  url: "/products/lead-crystal/athena-decanter"
reviews:
  averageRating: 4.8
  reviewCount: 42
productID: "LCD-ATH-2024"
material: "24% Lead Crystal, Sterling Silver"
---
```

---

### Generated JSON-LD Content

This JSON-LD code should be placed in the `<head>` section of your HTML page.

```json
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "@id": "https://yourdomain.com/products/lead-crystal/athena-decanter#product",
  "name": "Athena Premium Lead Crystal Decanter",
  "sku": "LCD-ATH-2024",
  "description": "Handcrafted decanter made from 24% lead crystal. Features a classic diamond-cut pattern and a sterling silver stopper. Perfect for whiskey, brandy, or as an elegant gift.",
  "image": [
    "https://yourdomain.com/images/products/athena-decanter-1.jpg",
    "https://yourdomain.com/images/products/athena-decanter-2.jpg"
  ],
  "brand": {
    "@type": "Brand",
    "name": "Crystal Heritage",
    "logo": "https://yourdomain.com/logos/crystal-heritage-logo.png"
  },
  "offers": {
    "@type": "Offer",
    "@id": "https://yourdomain.com/products/lead-crystal/athena-decanter#offer",
    "price": "129.99",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition",
    "url": "https://yourdomain.com/products/lead-crystal/athena-decanter",
    "seller": {
      "@type": "Organization",
      "name": "Your Store Name"
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "42"
  },
  "material": "24% Lead Crystal, Sterling Silver",
  "additionalProperty": {
    "@type": "PropertyValue",
    "name": "Crystal Type",
    "value": "Full-Lead Crystal"
  },
  "category": "Home & Kitchen > Kitchen & Dining > Bar & Wine > Decanters"
}
</script>
```

---

### Key Components

---
Version Log - Generated: 2025-09-10T23:37:05.796035
Material: Lead Crystal
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/lead-crystal-laser-cleaning.md
---