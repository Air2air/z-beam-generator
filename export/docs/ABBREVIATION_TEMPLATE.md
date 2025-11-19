# Frontmatter Abbreviation Template

## Overview

The frontmatter component now includes standardized abbreviation formatting for materials with common industry abbreviations. This ensures consistency and professional presentation across all material documentation.

## Template Format

For materials with established abbreviations, the frontmatter follows this standardized template:

### Before (Old Format)
```yaml
name: Fiber Reinforced Polyurethane Frpu
category: Composite
subcategory: Fiber Reinforced Polyurethane Frpu
title: Fiber Reinforced Polyurethane Frpu Laser Cleaning
```

### After (New Template)
```yaml
name: FRPU
category: Composite
subcategory: Fiber Reinforced Polyurethane (FRPU)
title: FRPU Laser Cleaning
```

## Template Rules

1. **Name Field**: Use the standard abbreviation (e.g., `FRPU`, `GFRP`, `CFRP`)
2. **Subcategory Field**: Full material name with abbreviation in parentheses (e.g., `Fiber Reinforced Polyurethane (FRPU)`)
3. **Title Field**: Abbreviation + " Laser Cleaning" (e.g., `FRPU Laser Cleaning`)
4. **Description Field**: May reference the abbreviation for clarity

## Supported Materials

The following materials currently use the abbreviation template:

| Material | Abbreviation | Full Name |
|----------|--------------|-----------|
| Fiber Reinforced Polyurethane FRPU | FRPU | Fiber Reinforced Polyurethane |
| Glass Fiber Reinforced Polymers GFRP | GFRP | Glass Fiber Reinforced Polymers |
| Carbon Fiber Reinforced Polymer | CFRP | Carbon Fiber Reinforced Polymer |
| Metal Matrix Composites MMCs | MMCs | Metal Matrix Composites |
| Ceramic Matrix Composites CMCs | CMCs | Ceramic Matrix Composites |
| MDF | MDF | Medium Density Fiberboard |
| Polyvinyl Chloride | PVC | Polyvinyl Chloride |
| Polytetrafluoroethylene | PTFE | Polytetrafluoroethylene |

## Implementation

### Automatic Generation

The frontmatter generator automatically applies the abbreviation template when generating content for supported materials. The mapping is defined in `MATERIAL_ABBREVIATIONS` within the streamlined generator.

### Code Location

- **Generator Logic**: `components/frontmatter/core/streamlined_generator.py`
- **Mapping Definition**: `MATERIAL_ABBREVIATIONS` constant
- **Template Application**: `_apply_abbreviation_template()` method

### Adding New Abbreviations

To add a new material abbreviation:

1. Add an entry to the `MATERIAL_ABBREVIATIONS` dictionary:
   ```python
   'Full Material Name': {
       'abbreviation': 'ABBR',
       'full_name': 'Full Material Name'
   }
   ```

2. Update the test cases in `tests/test_abbreviation_template.py`

3. Regenerate the frontmatter for the material to apply the template

## Testing

The abbreviation template is validated through comprehensive tests:

- **Mapping Tests**: Verify all expected abbreviations are defined
- **Template Application**: Test the abbreviation formatting logic
- **File Consistency**: Validate existing frontmatter files follow the template
- **Format Validation**: Ensure consistency across name, subcategory, and title fields

Run tests with:
```bash
python3 -m pytest tests/test_abbreviation_template.py -v
```

## Benefits

1. **Consistency**: Standardized format across all abbreviated materials
2. **Professional Presentation**: Industry-standard abbreviations are prominently displayed
3. **Clarity**: Full names are preserved in subcategories for context
4. **SEO Optimization**: Both abbreviated and full names are included for search optimization
5. **Maintainability**: Centralized mapping makes updates easy

## Migration Notes

When updating existing materials to use the abbreviation template:

1. The original material name in the database should remain unchanged
2. Only the frontmatter presentation changes
3. Files are renamed to use the full descriptive filename (no change needed)
4. All existing URLs and references remain valid

This approach ensures backward compatibility while providing a professional, consistent presentation format.