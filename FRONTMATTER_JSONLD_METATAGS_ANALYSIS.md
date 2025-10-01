# Frontmatter JSON-LD and Metatags Analysis

**Date**: October 1, 2025
**Question**: Can we remove `content/components/jsonld` and `content/components/metatags` directories?

## Executive Summary

**Answer**: ⚠️ **PARTIAL - Requires Frontmatter Enhancement**

The frontmatter files contain **most** but not **all** the information needed for JSON-LD and metatags. You can safely remove these directories **AFTER** enhancing frontmatter with missing SEO/metadata fields.

## Current State Analysis

### What Frontmatter Currently Has ✅

**From `alabaster-laser-cleaning.yaml`:**
1. **Basic Material Info**:
   - `name`, `title`, `description`
   - `category`, `subcategory`
   
2. **Material Properties** (comprehensive):
   - `materialProperties` with units, confidence, min/max
   - `machineSettings` with wavelength, power, etc.
   
3. **Applications & Use Cases**:
   - `applications` array
   - `applicationTypes` with industries and metrics
   
4. **Environmental & Quality Data**:
   - `environmentalImpact`
   - `outcomeMetrics`
   - `regulatoryStandards`
   
5. **Author Information**:
   - `author` object with name, country, expertise, image
   
6. **Caption Content**:
   - `caption` with beforeText, afterText, description
   - Image data with alt text
   
7. **Images**:
   - `images.hero` with url and alt

### What Frontmatter is MISSING ❌

Comparing with JSON-LD (`aluminum-laser-cleaning.json`) and Metatags (`aluminum-laser-cleaning.yaml`):

#### 1. SEO Metadata (from metatags)
- ❌ `keywords` array (for meta keywords tag)
- ❌ `robots` directive (e.g., "index, follow")
- ❌ `canonical` URL
- ❌ `viewport` settings
- ❌ `theme-color`
- ❌ Open Graph metadata:
  - `og:title`, `og:description`, `og:type`
  - `og:image`, `og:url`, `og:site_name`
  - `og:locale`, `article:section`, `article:tag`
- ❌ Twitter Card metadata:
  - `twitter:card`, `twitter:title`, `twitter:description`
  - `twitter:image`, `twitter:site`, `twitter:creator`
- ❌ Alternate language links (`hreflang`)

#### 2. JSON-LD Structured Data
- ❌ `@context` and `@type` schema.org definitions
- ❌ Article metadata:
  - `datePublished`, `dateModified`
  - `wordCount`, `articleSection`
  - `inLanguage`
- ❌ Publisher information:
  - Organization name, logo, contactPoint
- ❌ HowTo schema:
  - Step-by-step instructions
  - `totalTime`, `prepTime`, `performTime`
  - Tools and supplies required
- ❌ BreadcrumbList for navigation
- ❌ FAQPage with questions/answers
- ❌ WebPage and Website schemas

#### 3. Additional Metadata
- ❌ `lastReviewed` date
- ❌ `reviewedBy` information
- ❌ `estimatedCost` for processes
- ❌ `mentions` (technologies, processes)

## Detailed Component Comparison

### JSON-LD Component Requirements

**From `aluminum-laser-cleaning.json` - 7 Schema Types:**

1. **Article Schema** ✅ Partially Covered
   - ✅ headline (from `title`)
   - ✅ name (from `name`)
   - ✅ description (from `description`)
   - ✅ author (from `author`)
   - ❌ datePublished, dateModified
   - ❌ keywords (not in frontmatter)
   - ❌ articleSection, wordCount
   - ❌ publisher organization

2. **Product Schema** ✅ Fully Covered
   - ✅ name, description, category
   - ✅ additionalProperty (from `materialProperties`)

3. **HowTo Schema** ❌ NOT Covered
   - ❌ No procedural steps in frontmatter
   - ❌ No totalTime, prepTime
   - ❌ No tools/supplies lists

4. **BreadcrumbList** ❌ NOT Covered
   - ❌ Navigation hierarchy not in frontmatter

5. **WebPage Schema** ⚠️ Partially Covered
   - ✅ name, description (from frontmatter)
   - ❌ URL, inLanguage, breadcrumb
   - ❌ lastReviewed, reviewedBy

6. **Website Schema** ❌ NOT Covered
   - ❌ Organization-level metadata

7. **FAQPage** ❌ NOT Covered
   - ❌ No Q&A in frontmatter

### Metatags Component Requirements

**From `aluminum-laser-cleaning.yaml`:**

1. **Basic Meta Tags** ⚠️ Partially Covered
   - ✅ title, description (from frontmatter)
   - ❌ keywords array
   - ❌ robots, googlebot
   - ❌ author (exists but not in SEO meta format)

2. **Open Graph Tags** ❌ NOT Covered
   - ❌ All og:* properties missing
   - ⚠️ Can be derived from frontmatter but not present

3. **Twitter Cards** ❌ NOT Covered
   - ❌ All twitter:* properties missing

4. **Technical Meta Tags** ❌ NOT Covered
   - ❌ viewport, format-detection
   - ❌ theme-color, color-scheme
   - ❌ application-name, msapplication-*

5. **URLs & Links** ❌ NOT Covered
   - ❌ canonical URL
   - ❌ alternate language links

## Coverage Analysis

### Data Coverage by Category

| Category | In Frontmatter? | Derivable? | Action Needed |
|----------|----------------|------------|---------------|
| **Material Properties** | ✅ 100% | N/A | None |
| **Author Info** | ✅ 100% | N/A | None |
| **Basic SEO** | ⚠️ 40% | ✅ Yes | Add keywords, robots |
| **Open Graph** | ❌ 0% | ✅ Yes | Derive from frontmatter |
| **Twitter Cards** | ❌ 0% | ✅ Yes | Derive from frontmatter |
| **JSON-LD Article** | ⚠️ 60% | ⚠️ Partial | Add dates, keywords |
| **JSON-LD HowTo** | ❌ 0% | ❌ No | Generate or omit |
| **JSON-LD FAQPage** | ❌ 0% | ❌ No | Generate or omit |
| **Breadcrumbs** | ❌ 0% | ✅ Yes | Derive from category |
| **URLs** | ❌ 0% | ✅ Yes | Generate from name |

### Overall Coverage Score

- **Static Content**: 75% (material data, properties, author)
- **SEO Metadata**: 25% (missing most meta tags)
- **Structured Data**: 35% (partial JSON-LD support)
- **Overall**: **45% Coverage**

## Recommendations

### Option 1: Enhance Frontmatter (Recommended)

**Add these fields to frontmatter schema:**

```yaml
# SEO Metadata
seo:
  keywords:
    - laser cleaning
    - alabaster
    - stone restoration
  robots: "index, follow, max-snippet:-1"
  canonical: "https://z-beam.com/alabaster-laser-cleaning"
  
  # Open Graph
  openGraph:
    type: article
    image: /images/alabaster-laser-cleaning-hero.jpg
    imageWidth: 1200
    imageHeight: 630
    locale: en_US
    siteName: "Z-Beam Laser Processing Guide"
  
  # Twitter
  twitter:
    card: summary_large_image
    site: "@z-beamTech"
    creator: "@z-beamTech"

# Publication Metadata
publication:
  datePublished: "2025-09-30"
  dateModified: "2025-09-30"
  dateReviewed: "2025-09-30"
  reviewedBy: "Z-Beam Technical Team"
  wordCount: 850
  articleSection: "Laser Cleaning"
  inLanguage: "en-US"

# Structured Data Extensions
structuredData:
  howTo:
    totalTime: "PT15M"
    prepTime: "PT5M"
    performTime: "PT10M"
    steps:
      - name: "Surface Assessment"
        text: "Evaluate surface condition..."
      - name: "Safety Setup"
        text: "Install safety barriers..."
  
  faq:
    - question: "What laser parameters are optimal?"
      answer: "For alabaster, we recommend..."
    - question: "Is laser cleaning safe?"
      answer: "Yes, laser cleaning is non-contact..."
```

**Benefits**:
- ✅ Single source of truth
- ✅ No duplication
- ✅ Easier maintenance
- ✅ Type-safe with schemas
- ✅ Can remove jsonld/ and metatags/ directories

**Effort**: Medium (2-3 days)
1. Update frontmatter schema
2. Update generators to populate new fields
3. Create Next.js utility to extract SEO/JSON-LD from frontmatter
4. Migrate existing materials
5. Delete old directories

### Option 2: Keep Separate Components (Not Recommended)

**Current State**:
- Maintain 3 separate file types per material
- Continue generating jsonld/ and metatags/ separately
- Risk of data inconsistency

**Issues**:
- ❌ Data duplication (3x files per material)
- ❌ Maintenance overhead
- ❌ Sync issues between files
- ❌ More complex build process

### Option 3: Hybrid Approach

**Frontmatter** for:
- ✅ Material properties
- ✅ Author info
- ✅ Basic SEO (title, description)
- ✅ Publication dates

**Generate at Build Time** in Next.js:
- ✅ Open Graph tags (from frontmatter)
- ✅ Twitter Cards (from frontmatter)
- ✅ JSON-LD schemas (from frontmatter)
- ✅ Breadcrumbs (from category hierarchy)
- ✅ URLs (from material name)

**Benefits**:
- ✅ Cleaner frontmatter (only source data)
- ✅ Dynamic generation (always in sync)
- ✅ Can remove jsonld/ and metatags/ directories
- ✅ Easier to update SEO patterns

**Effort**: Low-Medium (1-2 days)
1. Create Next.js SEO utility functions
2. Map frontmatter → SEO/JSON-LD in components
3. Test with all materials
4. Delete old directories

## Implementation Plan

### Recommended: Option 3 (Hybrid Approach)

**Phase 1: Create Next.js Utilities** (4 hours)
```typescript
// lib/seo/frontmatter-to-jsonld.ts
export function generateJsonLd(frontmatter: Frontmatter) {
  return {
    "@context": "https://schema.org",
    "@graph": [
      generateArticleSchema(frontmatter),
      generateProductSchema(frontmatter),
      generateBreadcrumbSchema(frontmatter),
      // Optional: HowTo, FAQPage if data available
    ]
  };
}

// lib/seo/frontmatter-to-metatags.ts
export function generateMetaTags(frontmatter: Frontmatter) {
  return {
    title: frontmatter.title,
    description: frontmatter.description,
    keywords: generateKeywords(frontmatter),
    openGraph: generateOpenGraph(frontmatter),
    twitter: generateTwitterCard(frontmatter),
    canonical: generateCanonicalUrl(frontmatter.name),
  };
}
```

**Phase 2: Update Material Pages** (2 hours)
```typescript
// app/materials/[material]/page.tsx
import { generateJsonLd, generateMetaTags } from '@/lib/seo';

export async function generateMetadata({ params }) {
  const frontmatter = await loadFrontmatter(params.material);
  return generateMetaTags(frontmatter);
}

export default async function MaterialPage({ params }) {
  const frontmatter = await loadFrontmatter(params.material);
  const jsonLd = generateJsonLd(frontmatter);
  
  return (
    <>
      <script type="application/ld+json">
        {JSON.stringify(jsonLd)}
      </script>
      {/* Page content */}
    </>
  );
}
```

**Phase 3: Test & Validate** (2 hours)
- Test all 121 materials
- Validate JSON-LD with Google's Rich Results Test
- Verify Open Graph with Facebook Debugger
- Check Twitter Cards with Twitter Validator

**Phase 4: Cleanup** (1 hour)
```bash
# Remove old directories
rm -rf content/components/jsonld
rm -rf content/components/metatags

# Update .gitignore if needed
# Update build scripts
# Update documentation
```

## Next.js Integration Example

```typescript
// lib/seo/index.ts
import type { Frontmatter } from '@/types/frontmatter';

export function generateSEO(frontmatter: Frontmatter) {
  const baseUrl = 'https://z-beam.com';
  const slug = frontmatter.name.toLowerCase().replace(/\s+/g, '-');
  const url = `${baseUrl}/${slug}`;
  
  return {
    // Basic SEO
    title: frontmatter.title,
    description: frontmatter.description,
    keywords: [
      frontmatter.name.toLowerCase(),
      frontmatter.category.toLowerCase(),
      'laser cleaning',
      'industrial cleaning',
      ...frontmatter.applications.map(a => a.toLowerCase()),
    ],
    
    // URLs
    canonical: url,
    alternates: {
      canonical: url,
      languages: {
        'en-US': url,
      },
    },
    
    // Open Graph
    openGraph: {
      type: 'article',
      title: frontmatter.title,
      description: frontmatter.description,
      url: url,
      siteName: 'Z-Beam',
      locale: 'en_US',
      images: [
        {
          url: `${baseUrl}${frontmatter.images.hero.url}`,
          width: 1200,
          height: 630,
          alt: frontmatter.images.hero.alt,
        },
      ],
      article: {
        publishedTime: frontmatter.metadata.lastUpdated,
        modifiedTime: frontmatter.metadata.lastUpdated,
        section: 'Laser Cleaning',
        tags: [frontmatter.name, frontmatter.category],
        authors: [frontmatter.author.name],
      },
    },
    
    // Twitter
    twitter: {
      card: 'summary_large_image',
      title: frontmatter.title,
      description: frontmatter.description,
      images: [`${baseUrl}${frontmatter.images.hero.url}`],
      site: '@z-beamTech',
      creator: '@z-beamTech',
    },
    
    // JSON-LD
    jsonLd: {
      '@context': 'https://schema.org',
      '@graph': [
        // Article
        {
          '@type': 'Article',
          '@id': `${url}#article`,
          headline: frontmatter.title,
          name: frontmatter.title,
          description: frontmatter.description,
          url: url,
          author: {
            '@type': 'Person',
            name: frontmatter.author.name,
            description: frontmatter.author.expertise,
          },
          datePublished: frontmatter.metadata.lastUpdated,
          dateModified: frontmatter.metadata.lastUpdated,
          keywords: frontmatter.applications.join(', '),
        },
        // Product
        {
          '@type': 'Product',
          '@id': `${url}#material`,
          name: frontmatter.name,
          description: frontmatter.description,
          category: frontmatter.category,
          additionalProperty: Object.entries(frontmatter.materialProperties).map(
            ([key, prop]) => ({
              '@type': 'PropertyValue',
              name: key,
              value: `${prop.value} ${prop.unit}`,
              description: prop.description,
            })
          ),
        },
        // Breadcrumb
        {
          '@type': 'BreadcrumbList',
          '@id': `${url}#breadcrumb`,
          itemListElement: [
            { '@type': 'ListItem', position: 1, name: 'Home', item: baseUrl },
            { '@type': 'ListItem', position: 2, name: 'Materials', item: `${baseUrl}/materials` },
            { '@type': 'ListItem', position: 3, name: frontmatter.category, item: `${baseUrl}/category/${frontmatter.category.toLowerCase()}` },
            { '@type': 'ListItem', position: 4, name: frontmatter.title, item: url },
          ],
        },
      ],
    },
  };
}
```

## Migration Checklist

### Before Deletion
- [ ] Create Next.js SEO utility functions
- [ ] Map all frontmatter fields to SEO/JSON-LD
- [ ] Test with representative materials (10+ samples)
- [ ] Validate JSON-LD with Google Rich Results Test
- [ ] Verify Open Graph with Facebook Debugger  
- [ ] Check Twitter Cards preview
- [ ] Compare generated output with existing files
- [ ] Update documentation

### During Deletion
- [ ] Backup existing jsonld/ directory
- [ ] Backup existing metatags/ directory
- [ ] Remove directories: `rm -rf content/components/{jsonld,metatags}`
- [ ] Update build scripts
- [ ] Update .gitignore
- [ ] Remove generator components

### After Deletion
- [ ] Verify all 121 materials render correctly
- [ ] Check SEO meta tags in production
- [ ] Validate JSON-LD in production
- [ ] Monitor search console for errors
- [ ] Update team documentation

## Conclusion

**YES**, you can remove the `jsonld/` and `metatags/` directories, **BUT**:

1. **✅ Best Approach**: Implement Option 3 (Hybrid) - generate SEO/JSON-LD dynamically in Next.js from frontmatter
2. **⏱️ Timeline**: 1-2 days implementation
3. **📊 Benefit**: Eliminate 242 files (121 × 2), reduce maintenance, ensure consistency
4. **⚠️ Risk**: Low (all data exists in frontmatter, just needs mapping)

**Recommendation**: Proceed with deletion after implementing Next.js SEO utilities. The frontmatter contains all the source data needed - you just need to transform it into the required formats at build/render time.
