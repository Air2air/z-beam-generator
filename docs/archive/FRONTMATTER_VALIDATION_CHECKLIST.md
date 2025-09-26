# Frontmatter YAML Validation Checklist

## Pre-Generation Requirements ✅

Before generating all frontmatter files for all materials, ensure ALL items below are completed:

### 1. **YAML Structure Validation** 
- [ ] All 110 frontmatter files use proper `---` YAML delimiters
- [ ] No files use malformed delimiters (````markdown, ```yaml)
- [ ] All YAML blocks parse without syntax errors
- [ ] No truncated content or incomplete fields

### 2. **Quote Usage Standardization**
- [ ] Text fields consistently quoted: `name: "Material Name"`
- [ ] Numeric fields never quoted: `densityPercentile: 72.4`
- [ ] Special characters properly quoted: `powerRange: "50-200W"`
- [ ] All string escaping handled correctly (no \1, \2 sequences)

### 3. **Content Completeness**
- [ ] All image alt text is complete and descriptive
- [ ] No truncated descriptions or headlines
- [ ] All required fields present: name, category, author, description
- [ ] Technical specifications properly formatted

### 4. **Version Log Consistency**
- [ ] All files have standardized version information
- [ ] Generation timestamps are consistent format
- [ ] File paths are correctly referenced
- [ ] Author attribution is complete

### 5. **Materials Database Integration**
- [ ] Materials.yaml optimization is complete (✅ DONE)
- [ ] Parameter templates are functional (✅ DONE)
- [ ] Material index supports all 109 materials (✅ DONE)
- [ ] Backward compatibility maintained (✅ DONE)

## Validation Commands

### Quick YAML Syntax Check
```bash
python3 -c "
import yaml
import os
from pathlib import Path

frontmatter_dir = Path('content/components/frontmatter')
errors = []

for file_path in frontmatter_dir.glob('*.md'):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        if content.startswith('---'):
            yaml_end = content.find('---', 3)
            if yaml_end > 0:
                yaml_content = content[4:yaml_end]
                yaml.safe_load(yaml_content)
            else:
                errors.append(f'{file_path.name}: No closing delimiter')
        else:
            errors.append(f'{file_path.name}: No opening delimiter')
    
    except Exception as e:
        errors.append(f'{file_path.name}: {str(e)}')

if errors:
    print(f'❌ {len(errors)} YAML errors found:')
    for error in errors[:10]:  # Show first 10 errors
        print(f'   {error}')
    if len(errors) > 10:
        print(f'   ... and {len(errors) - 10} more errors')
else:
    print('✅ All YAML files parse successfully!')
    print(f'📁 Validated {len(list(frontmatter_dir.glob(\"*.md\")))} files')
"
```

### Complete Content Validation
```bash
python3 -c "
import yaml
import os
from pathlib import Path

frontmatter_dir = Path('content/components/frontmatter')
required_fields = ['name', 'category', 'author', 'description']
validation_results = {
    'syntax_errors': [],
    'missing_fields': [],
    'truncated_content': [],
    'quote_issues': []
}

for file_path in frontmatter_dir.glob('*.md'):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        if not content.startswith('---'):
            validation_results['syntax_errors'].append(f'{file_path.name}: No opening delimiter')
            continue
        
        yaml_end = content.find('---', 3)
        if yaml_end <= 0:
            validation_results['syntax_errors'].append(f'{file_path.name}: No closing delimiter')
            continue
        
        yaml_content = content[4:yaml_end]
        data = yaml.safe_load(yaml_content)
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                validation_results['missing_fields'].append(f'{file_path.name}: Missing {field}')
        
        # Check for truncated content
        if 'images' in data and 'micro' in data['images']:
            alt_text = data['images']['micro'].get('alt', '')
            if alt_text.endswith('preserved') or len(alt_text) < 50:
                validation_results['truncated_content'].append(f'{file_path.name}: Truncated alt text')
        
        # Check for quote issues
        yaml_lines = yaml_content.split('\n')
        for line in yaml_lines:
            if '\\\1' in line or '\\\2' in line:
                validation_results['quote_issues'].append(f'{file_path.name}: Escape sequence issues')
                break
    
    except Exception as e:
        validation_results['syntax_errors'].append(f'{file_path.name}: {str(e)}')

# Report results
total_files = len(list(frontmatter_dir.glob('*.md')))
total_errors = sum(len(errors) for errors in validation_results.values())

print(f'📊 FRONTMATTER VALIDATION REPORT')
print(f'=' * 50)
print(f'📁 Total files: {total_files}')
print(f'❌ Total issues: {total_errors}')
print()

for category, errors in validation_results.items():
    if errors:
        print(f'{category.replace(\"_\", \" \").title()}: {len(errors)} issues')
        for error in errors[:5]:  # Show first 5 errors per category
            print(f'   {error}')
        if len(errors) > 5:
            print(f'   ... and {len(errors) - 5} more')
        print()

if total_errors == 0:
    print('🎉 ALL VALIDATION CHECKS PASSED!')
    print('✅ Ready for bulk frontmatter generation')
else:
    print('⚠️  VALIDATION FAILED - Fix issues before proceeding')
"
```

## Current Status

### ✅ Completed Items
- [x] Materials.yaml optimization (25.9% reduction)
- [x] Parameter templates implementation
- [x] Material index creation (O(1) lookups)
- [x] Backward compatibility validation
- [x] Normalization script creation
- [x] Individual file repairs (zirconia, alumina)

### 🔄 In Progress
- [ ] YAML syntax normalization (109/110 files need fixes)
- [ ] Quote escaping issues resolution
- [ ] Version log standardization

### ❌ Pending
- [ ] Complete content validation
- [ ] Bulk generation readiness confirmation
- [ ] Final system integration testing

## Recommended Action Plan

### Phase 1: Immediate Fixes (Required)
1. **Restore clean backups** and fix normalization script
2. **Resolve quote escaping issues** in YAML processing
3. **Complete syntax normalization** for all 110 files
4. **Run full validation suite** to confirm readiness

### Phase 2: Quality Assurance
1. **Test random sample** of 10-15 files with content generation
2. **Validate component integration** with fixed frontmatter
3. **Verify Materials.yaml integration** works with normalized files
4. **Performance testing** on bulk operations

### Phase 3: Production Readiness
1. **Create pre-commit hooks** for YAML validation
2. **Document formatting standards** for future files
3. **Implement automated testing** for content generation
4. **Final approval** for bulk frontmatter generation

## Decision Gate

**DO NOT PROCEED** with bulk frontmatter generation until:
- ✅ All YAML syntax errors are resolved
- ✅ All validation commands pass without errors  
- ✅ Random sample testing shows successful content generation
- ✅ Materials database integration is fully functional

## Risk Assessment

**HIGH RISK**: Proceeding with malformed YAML files will cause:
- Content generation failures
- System instability  
- Component parsing errors
- Data corruption in output files

**MITIGATION**: Complete normalization and validation before bulk operations.

---

**Last Updated**: September 16, 2025
**Status**: VALIDATION REQUIRED - Do not proceed with bulk generation
**Priority**: HIGH - System stability depends on frontmatter quality
