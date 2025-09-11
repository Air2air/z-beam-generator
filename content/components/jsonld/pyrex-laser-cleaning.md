Here's JSON-LD content for Pyrex using frontmatter data:

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "@id": "https://example.com/pyrex#product",
  "name": "Pyrex",
  "description": "Heat-resistant glassware for cooking, baking, and food storage",
  "brand": {
    "@type": "Brand",
    "name": "Pyrex"
  },
  "manufacturer": {
    "@type": "Organization",
    "name": "Corning Inc."
  },
  "category": "Kitchenware",
  "material": "Borosilicate glass",
  "features": [
    "Heat resistant",
    "Oven safe",
    "Microwave safe",
    "Dishwasher safe",
    "Freezer safe"
  ],
  "slogan": "The original heat-tempered glassware",
  "url": "https://example.com/pyrex",
  "image": "https://example.com/images/pyrex-baking-dish.jpg",
  "offers": {
    "@type": "Offer",
    "priceCurrency": "USD",
    "price": "24.99",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "Organization",
      "name": "Kitchen Supply Store"
    }
  },
  "review": {
    "@type": "Review",
    "reviewRating": {
      "@type": "Rating",
      "ratingValue": "4.8",
      "bestRating": "5"
    },
    "author": {
      "@type": "Person",
      "name": "Home Cook"
    }
  }
}
```

If you have specific frontmatter data, here's a template that can be populated with your actual values:

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "@id": "{{url}}#product",
  "name": "{{title}}",
  "description": "{{description}}",
  "brand": {
    "@type": "Brand",
    "name": "{{brand}}"
  },
  "category": "{{category}}",
  "material": "{{material}}",
  "features": {{features | json}},
  "url": "{{url}}",
  "image": "{{image}}",
  "offers": {
    "@type": "Offer",
    "priceCurrency": "{{priceCurrency}}",
    "price": "{{price}}",
    "availability": "{{availability}}"
  }
}
```

**Common frontmatter variables you might use:**
- `title`: Product name
- `description`: Product description
- `price`: Product price
- `image`: Product image URL
- `sku`: Product SKU
- `category`: Product category
- `brand`: Brand name
- `features`: Array of features
- `rating`: Customer rating
- `reviewCount`: Number of reviews

Would you like me to customize this for specific frontmatter variables you're using?

---
Version Log - Generated: 2025-09-10T23:38:05.567296
Material: Pyrex
Component: jsonld
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/jsonld/pyrex-laser-cleaning.md
---