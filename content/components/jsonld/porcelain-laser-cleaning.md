Of course. I'll generate JSON-LD structured data for a porcelain product page, assuming we have a standard set of frontmatter data points.

### 1. Frontmatter Data (Example)

First, let's assume your content has the following frontmatter:

```yaml
---
title: "Harmony Blue Fluted Mega Bowl"
sku: "PB-7842-MEGA"
description: "A stunning, hand-painted large porcelain bowl featuring the iconic Blue Fluted pattern. Perfect as a fruit bowl or a statement centerpiece."
price: 149.99
priceCurrency: "USD"
availability: "InStock"
brand: "Royal Porcelain"
image: "https://example.com/images/harmony-blue-bowl.jpg"
productCategory: "Home & Kitchen > Kitchen & Dining > Serveware > Bowls"
ratingValue: 4.8
reviewCount: 47
---
```

### 2. Generated JSON-LD

Based on the frontmatter above, here is the corresponding JSON-LD script. This uses the `Product` schema from Schema.org, which is the most appropriate for an individual product page.

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Harmony Blue Fluted Mega Bowl",
  "sku": "PB-7842-MEGA",
  "description": "A stunning, hand-painted large porcelain bowl featuring the iconic Blue Fluted pattern. Perfect as a fruit bowl or a statement centerpiece.",
  "offers": {
    "@type": "Offer",
    "price": "149.99",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "" // You would dynamically insert the page URL here
  },
  "brand": {
    "@type": "Brand",
    "name": "Royal Porcelain"
  },
  "image": "https://example.com/images/harmony-blue-bowl.jpg",
  "category": "Home & Kitchen > Kitchen & Dining > Serveware > Bowls",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "47"
  }
}
```

---

### 3. Dynamic Template for a Static Site Generator (SSG)

If you are using a static site generator like Hugo, Jekyll, or 11ty, you would dynamically populate these values. Here's an example of how the JSON-LD might look in a template (e.g., using Nunjucks, Liquid, or similar):

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{{ title | escape }}",
  "sku": "{{ sku }}",
  "description": "{{ description | escape }}",
  "offers": {
    "@type": "Offer",
    "price": "{{ price }}",
    "priceCurrency": "{{ priceCurrency }}",
    "availability": "https://schema.org/{{ availability }}",
    "url": "{{ page.url | absoluteUrl }}" // Example function to create full URL
  },
  "brand": {
    "@type": "Brand",
    "name": "{{ brand }}"
  },
  "image": "{{ image }}",
  "category": "{{ productCategory }}",
  {% if ratingValue %}
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "{{ ratingValue }}",
    "reviewCount": "{{ reviewCount }}"
  }
  {% endif %}
}
</script>
```

### 4. Explanation of Key Properties:

*   **`@type: Product`**: Tells search engines this is data about

---
Version Log - Generated: 2025-09-10T23:16:05.456906
Material: Porcelain
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/porcelain-laser-cleaning.md
---