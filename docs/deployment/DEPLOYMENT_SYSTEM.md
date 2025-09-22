# Deployment System Documentation

## Overview

The Z-Beam deployment system provides automated deployment of generated content components to production environments using the `--deploy` flag.

## Deployment Command

```bash
# Deploy all components to production
python3 run.py --all --deploy
```

## Deployment Process

### 1. Component Processing
The deployment system processes components in this order:
1. **settings** - Configuration files (.yaml)
2. **propertiestable** - Material property tables (.md) 
3. **bullets** - Bullet point content (.md)
4. **author** - Author information (.yaml)
5. **frontmatter** - Page frontmatter (.md)
6. **tags** - Content tags (.md)
7. **table** - Data tables (.yaml)
8. **metatags** - HTML meta tags (.yaml)
9. **text** - Main content (.md)
10. **badgesymbol** - Badge symbols (may be skipped)
11. **jsonld** - Structured data (.json)

### 2. File Operations
- **✅ Updated**: Existing files modified with new content
- **✨ Created**: New files added to production
- **⚠️ Skipped**: Components with no files found
- **❌ Errors**: Failed operations (should be 0)

### 3. Target Directory
```
/Users/todddunning/Desktop/Z-Beam/z-beam-test-push/content/components/
```

## Recent Deployment Results

### September 2025 - PropertiesTable 4-Field Update
```
📦 Deployment completed!
📊 Statistics:
  ✨ Created: 0 files
  ✅ Updated: 946 files
  ⚠️ Skipped: 1 components (badgesymbol)
  ❌ Errors: 0 files
🎉 Deployment successful! Next.js production site updated.
```

### Component Breakdown
- **PropertiesTable**: 109 files (all materials)
- **Frontmatter**: 109 files (all materials)
- **JSONld**: 109 files (all materials)
- **Author**: 109 files (all materials)
- **Settings**: 109 files (all materials)
- **Text**: 7 files (selective materials)
- **Other Components**: Variable counts

## PropertiesTable Deployment Verification

After deployment, verify 4-field compliance:

### Validation Commands
```bash
# Check total propertiestable files (should be 109)
find content/components/propertiestable -name "*-laser-cleaning.md" | wc -l

# Check for forbidden laser properties (should be 0)
grep -l 'Laser Type\|Wavelength\|Fluence Range' content/components/propertiestable/*-laser-cleaning.md 2>/dev/null | wc -l

# Check for old thermal label (should be 0)
grep -l 'Thermal Cond\.' content/components/propertiestable/*-laser-cleaning.md 2>/dev/null | wc -l

# Verify correct Conductivity label (should be 109)
grep -l '| Conductivity |' content/components/propertiestable/*-laser-cleaning.md 2>/dev/null | wc -l
```

### Expected Results
```
✅ Total files: 109
✅ Laser properties: 0 (removed)
✅ Wrong thermal label: 0 (corrected)
✅ Correct Conductivity label: 109 (all files)
```

## Deployment Architecture

### Source Directories
```
content/components/{component}/
├── aluminum-laser-cleaning.{ext}
├── steel-laser-cleaning.{ext}
├── copper-laser-cleaning.{ext}
└── ... (109 materials total)
```

### Target Structure
```
z-beam-test-push/content/components/{component}/
├── aluminum-laser-cleaning.{ext}
├── steel-laser-cleaning.{ext}
├── copper-laser-cleaning.{ext}
└── ... (109 materials total)
```

## File Extension Mapping

| Component | Extension | Count |
|-----------|-----------|-------|
| propertiestable | .md | 109 |
| frontmatter | .md | 109 |
| text | .md | 7 |
| jsonld | .json | 109 |
| author | .yaml | 109 |
| settings | .yaml | 109 |
| metatags | .yaml | 109 |
| table | .yaml | 109 |
| tags | .md | 109 |
| bullets | .md | 2 |

## Error Handling

### Common Issues
- **Missing files**: Components with no generated content
- **Permission errors**: Insufficient write access to target
- **Path errors**: Incorrect target directory configuration

### Success Criteria
- ✅ Zero errors in deployment statistics
- ✅ All critical components deployed
- ✅ File counts match expectations
- ✅ Production site successfully updated

## Monitoring and Validation

### Post-Deployment Checks
1. **File Count Verification**: Ensure all 109 materials deployed
2. **Content Validation**: Verify 4-field propertiestable structure
3. **Format Compliance**: Check markdown and YAML syntax
4. **Production Testing**: Validate Next.js site functionality

### Rollback Procedures
If deployment issues occur:
1. Regenerate problematic components
2. Run validation commands
3. Re-deploy with `--all --deploy`
4. Verify production site functionality

## Integration with Development Workflow

### Typical Workflow
1. **Generate/Regenerate**: `python3 run.py --all --components propertiestable`
2. **Validate**: Run compliance checks
3. **Deploy**: `python3 run.py --all --deploy`
4. **Verify**: Check production site

### Continuous Integration
- Automated testing before deployment
- Validation of component compliance
- Error reporting and rollback capabilities
- Production environment monitoring
