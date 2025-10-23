# Frontend Integration Prompt for Next.js Assistant

## Context
The Z-Beam laser cleaning system has rearchitected its frontmatter data structure to organize material properties by scientific category. This provides better organization, semantic clarity, and improved user experience.

## What Changed

### OLD Structure (Flat)
```yaml
materialProperties:
  density:
    value: 2.7
    unit: g/cm³
    confidence: 95
    min: 0.53
    max: 22.6
  thermalConductivity:
    value: 237
    unit: W/m·K
    confidence: 95
    min: 6.0
    max: 429.0
  # ... 20+ more properties in no particular order
```

### NEW Structure (Categorized)
```yaml
materialProperties:
  thermal:
    label: "Thermal Properties"
    description: "Heat-related material characteristics including conductivity, expansion, and destruction points"
    percentage: 29.1
    properties:
      thermalConductivity:
        value: 237
        unit: W/m·K
        confidence: 95
        description: Rate of heat transfer through material
        min: 6.0
        max: 429.0
      meltingPoint:
        value: 660
        unit: °C
        confidence: 99
        min: 30
        max: 3422
      specificHeat:
        value: 900
        unit: J/kg·K
        confidence: 92
        min: 100
        max: 900
  
  mechanical:
    label: "Mechanical Properties"
    description: "Strength, elasticity, and structural characteristics"
    percentage: 18.2
    properties:
      density:
        value: 2.7
        unit: g/cm³
        confidence: 99
        min: 0.53
        max: 22.6
      hardness:
        value: 167
        unit: HV
        confidence: 95
        min: 0.5
        max: 3500
      tensileStrength:
        value: 276
        unit: MPa
        confidence: 88
        min: 3.0
        max: 3000.0
  
  optical_laser:
    label: "Optical/Laser Properties"
    description: "Light interaction and laser response characteristics"
    percentage: 16.4
    properties:
      laserAbsorption:
        value: 5
        unit: cm⁻¹
        confidence: 85
        min: 0.02
        max: 100
      laserReflectivity:
        value: 92
        unit: '%'
        confidence: 90
        min: 5
        max: 98
  
  electrical:
    label: "Electrical Properties"
    description: "Electrical conductivity and resistance"
    percentage: 7.3
    properties:
      electricalConductivity:
        value: 37.7
        unit: MS/m
        confidence: 95
        min: 1.0
        max: 100.0
  
  # Additional categories: surface, chemical, environmental, compositional, physical_structural
```

## Property Categories (Physics-Based v3.0)

The system uses **4 physics-based categories** following the laser cleaning process:

1. **laser_interaction** (16.4% - 9 properties) - *Energy Absorption*
   - laserAbsorption, laserReflectivity, reflectivity, ablationThreshold, absorptivity, emissivity, refractiveIndex, laserDamageThreshold, opticalTransmittance
   - **Physics**: First-order photon coupling - how laser energy enters material vs. reflects away

2. **thermal_response** (25.5% - 14 properties) - *Energy Dissipation*
   - thermalConductivity, specificHeat, thermalDiffusivity, thermalExpansion, thermalDestruction, boilingPoint, heatCapacity, glasTransitionTemperature, etc.
   - **Physics**: How absorbed energy distributes through material and when phase transitions occur

3. **mechanical_response** (18.2% - 10 properties) - *Material Response*
   - hardness, tensileStrength, youngsModulus, yieldStrength, elasticity, bulkModulus, shearModulus, compressiveStrength, flexuralStrength, fractureResistance
   - **Physics**: How material physically reacts to rapid thermal stress

4. **material_characteristics** (40.0% - 22 properties) - *Supporting Properties*
   - density, viscosity, porosity, surfaceRoughness, permeability, surfaceEnergy, wettability, electricalResistivity, electricalConductivity, dielectricConstant, chemicalStability, oxidationResistance, corrosionResistance, moistureContent, waterSolubility, weatherResistance, crystallineStructure, celluloseContent, grainSize, magneticPermeability, photonPenetrationDepth
   - **Physics**: Intrinsic properties affecting secondary outcomes like surface finish and process efficiency

Plus **other** category for uncategorized material-specific properties.

## Category Object Structure

Each category object contains:
- **label** (string): Human-readable category name
- **description** (string): Category purpose and contents
- **percentage** (number): Percentage of total property taxonomy (0-100)
- **properties** (object): Nested property objects with value, unit, confidence, min, max

## Property Value Structure

Each property contains:
- **value** (number|string): The actual property value
- **unit** (string): Unit of measurement
- **confidence** (number): Confidence score 0-100
- **description** (string): Property description
- **min** (number): Minimum value in category range
- **max** (number): Maximum value in category range
- **source** (string, optional): Data source (typically "ai_research")

## TypeScript Interfaces

```typescript
interface PropertyValue {
  value: number | string;
  unit: string;
  confidence: number;
  description: string;
  min?: number;
  max?: number;
  source?: string;
}

interface PropertyCategory {
  label: string;
  description: string;
  percentage: number;
  properties: {
    [propertyName: string]: PropertyValue;
  };
}

interface MaterialProperties {
  laser_interaction?: PropertyCategory;
  thermal_response?: PropertyCategory;
  mechanical_response?: PropertyCategory;
  material_characteristics?: PropertyCategory;
  other?: PropertyCategory;
}

interface Frontmatter {
  name: string;
  category: string;
  subcategory: string;
  title: string;
  description: string;
  materialProperties: MaterialProperties;
  // ... other frontmatter fields
}
```

## Frontend Implementation Tasks

### 1. Update Type Definitions
Update your frontmatter types to use the new `MaterialProperties` interface with categorized structure.

### 2. Update Property Display Components
**Before:**
```tsx
// OLD: Flat structure
{Object.entries(materialProperties).map(([key, prop]) => (
  <PropertyRow key={key} name={key} {...prop} />
))}
```

**After:**
```tsx
// NEW: Categorized structure
{Object.entries(materialProperties).map(([categoryId, category]) => (
  <PropertyCategory key={categoryId} categoryId={categoryId}>
    <CategoryHeader>
      <h3>{category.label}</h3>
      <span>{category.percentage}%</span>
      <p>{category.description}</p>
    </CategoryHeader>
    <PropertiesGrid>
      {Object.entries(category.properties).map(([key, prop]) => (
        <PropertyRow key={key} name={key} {...prop} />
      ))}
    </PropertiesGrid>
  </PropertyCategory>
))}
```

### 3. Add Category-Based Features

**Collapsible Categories:**
```tsx
const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
  new Set(['laser_interaction', 'thermal_response', 'mechanical_response']) // Default expanded - physics flow
);

const toggleCategory = (categoryId: string) => {
  setExpandedCategories(prev => {
    const next = new Set(prev);
    if (next.has(categoryId)) {
      next.delete(categoryId);
    } else {
      next.add(categoryId);
    }
    return next;
  });
};
```

**Category Filtering:**
```tsx
const [selectedCategories, setSelectedCategories] = useState<string[]>([]);

const filteredProperties = selectedCategories.length === 0
  ? materialProperties
  : Object.fromEntries(
      Object.entries(materialProperties).filter(([id]) => 
        selectedCategories.includes(id)
      )
    );
```

**Category Icons/Colors:**
```tsx
const categoryConfig = {
  thermal: { icon: '🔥', color: '#FF6B6B' },
  mechanical: { icon: '⚙️', color: '#4ECDC4' },
  optical_laser: { icon: '💡', color: '#FFE66D' },
  surface: { icon: '🎨', color: '#95E1D3' },
  electrical: { icon: '⚡', color: '#F38181' },
  chemical: { icon: '🧪', color: '#AA96DA' },
  environmental: { icon: '🌍', color: '#67B279' },
  compositional: { icon: '🔬', color: '#C490D1' },
  physical_structural: { icon: '📐', color: '#A8DADC' }
};
```

### 4. Update Data Fetching
Ensure your API routes and data fetching functions handle the new structure:

```typescript
// pages/api/materials/[slug].ts
export default async function handler(req, res) {
  const { slug } = req.query;
  const frontmatter = await loadFrontmatter(slug);
  
  // Validate structure
  if (frontmatter.materialProperties) {
    const firstCategory = Object.values(frontmatter.materialProperties)[0];
    if (!firstCategory?.label || !firstCategory?.properties) {
      throw new Error('Invalid frontmatter structure - expected categorized properties');
    }
  }
  
  res.status(200).json(frontmatter);
}
```

### 5. Update Search/Filter Logic
```typescript
// Search across categories and properties
function searchProperties(query: string, materialProperties: MaterialProperties) {
  const results = [];
  
  for (const [categoryId, category] of Object.entries(materialProperties)) {
    // Search category labels
    if (category.label.toLowerCase().includes(query.toLowerCase())) {
      results.push({ type: 'category', id: categoryId, ...category });
    }
    
    // Search property names and descriptions
    for (const [propName, prop] of Object.entries(category.properties)) {
      if (propName.toLowerCase().includes(query.toLowerCase()) ||
          prop.description.toLowerCase().includes(query.toLowerCase())) {
        results.push({ 
          type: 'property', 
          categoryId, 
          categoryLabel: category.label,
          name: propName, 
          ...prop 
        });
      }
    }
  }
  
  return results;
}
```

### 6. Update Documentation Display
```tsx
<MaterialPropertiesSection>
  <SectionHeader>
    <h2>Material Properties</h2>
    <p>Properties organized by scientific domain</p>
  </SectionHeader>
  
  {Object.entries(materialProperties)
    .sort(([, a], [, b]) => b.percentage - a.percentage) // Sort by importance
    .map(([categoryId, category]) => (
      <CategoryCard key={categoryId} importance={category.percentage}>
        <CategoryInfo>
          <CategoryBadge percentage={category.percentage}>
            {categoryConfig[categoryId]?.icon} {category.label}
          </CategoryBadge>
          <PercentageBar value={category.percentage} />
          <CategoryDescription>{category.description}</CategoryDescription>
        </CategoryInfo>
        
        <PropertyList>
          {Object.entries(category.properties).map(([name, prop]) => (
            <PropertyCard key={name}>
              <PropertyName>{formatPropertyName(name)}</PropertyName>
              <PropertyValue>
                {prop.value} {prop.unit}
              </PropertyValue>
              <ConfidenceBadge level={prop.confidence}>
                {prop.confidence}% confidence
              </ConfidenceBadge>
              {prop.min !== undefined && (
                <Range>Range: {prop.min} - {prop.max} {prop.unit}</Range>
              )}
            </PropertyCard>
          ))}
        </PropertyList>
      </CategoryCard>
    ))}
</MaterialPropertiesSection>
```

## Benefits for Frontend

1. **Better UX**: Properties grouped logically by domain
2. **Progressive Disclosure**: Show/hide categories, fold/unfold sections
3. **Visual Hierarchy**: Use percentages to emphasize important categories
4. **Improved Search**: Filter by category, search within categories
5. **Enhanced Navigation**: Jump to specific property categories
6. **Better Mobile**: Collapsible categories reduce scrolling
7. **Semantic HTML**: Use proper `<section>` and `<article>` tags per category
8. **Accessibility**: Better screen reader support with category landmarks

## Migration Checklist

- [ ] Update TypeScript interfaces for categorized structure
- [ ] Modify property display components to iterate categories
- [ ] Add category header components (label, description, percentage)
- [ ] Implement collapsible/expandable categories
- [ ] Add category filtering UI
- [ ] Update search functionality for nested structure
- [ ] Add category icons/colors for visual distinction
- [ ] Update API validation for new structure
- [ ] Test with sample frontmatter files
- [ ] Update Storybook/component documentation
- [ ] Verify mobile responsive behavior
- [ ] Test accessibility with screen readers
- [ ] Update any property-specific logic (comparisons, conversions)

## Example Files to Update

1. `components/MaterialProperties.tsx` - Main property display component
2. `types/frontmatter.ts` - Type definitions
3. `lib/frontmatter.ts` - Data loading/parsing
4. `pages/materials/[slug].tsx` - Material detail page
5. `components/PropertySearch.tsx` - Search functionality
6. `styles/properties.css` - Category-specific styling

## Sample Frontmatter Location

All 122 frontmatter files are in: `/content/frontmatter/`

Example files to test with:
- `aluminum-laser-cleaning.yaml`
- `steel-laser-cleaning.yaml`
- `copper-laser-cleaning.yaml`

## Questions to Answer

1. Should categories be collapsible by default or all expanded?
2. Should category percentage be prominently displayed?
3. Do you want category-based color coding throughout the UI?
4. Should search results highlight which category contains the match?
5. Do you want a category navigation sidebar for quick jumping?

## Support

For technical questions about the backend structure or property categories:
- See: `docs/CATEGORIZED_FRONTMATTER_OUTPUT.md`
- See: `data/Categories.yaml` → `propertyCategories` section
- See: `schemas/frontmatter.json` → `MaterialProperties` definition

The categorized structure is now the ONLY supported format. All 122 frontmatter files will be regenerated with this structure before frontend deployment.
