# Z-Beam Generator Troubleshooting Guide

**Comprehensive troubleshooting guide for the consolidated 6-component architecture**

---

## Quick Start Diagnostics

### System Health Check
```bash
# Test basic system functionality
python3 run.py --check-env

# Test API connectivity
python3 run.py --test-api

# Verify component system
python3 -c "from components.component_factory import ComponentGeneratorFactory; factory = ComponentGeneratorFactory(); print(f'Available components: {factory.list_available_components()}')"
```

### Expected Output
```
Available components: ['frontmatter', 'author', 'badgesymbol', 'metatags', 'jsonld', 'propertiestable']
API Status: All providers operational
Environment: All required variables present
```

---

## Component-Specific Issues

### 1. Frontmatter Component Issues

#### Problem: Missing or Incomplete Material Properties
**Symptoms:**
- Empty materialProperties section
- Missing machineSettings section
- Properties without values or units

**Diagnosis:**
```bash
# Test frontmatter generation
python3 run.py --material "Aluminum" --components "frontmatter"

# Check PropertyResearcher status
python3 -c "from components.frontmatter.research.property_researcher import PropertyResearcher; pr = PropertyResearcher(); print('PropertyResearcher initialized successfully')"
```

**Common Solutions:**
1. **Missing Material Data**: Check `data/Materials.yaml` for material entry
2. **Research Failure**: Verify PropertyResearcher has necessary data sources
3. **Schema Validation**: Ensure `schemas/frontmatter.json` is properly configured

#### Problem: Property Research Failures
**Symptoms:**
- Generic property values (0.0, "unknown")
- Low confidence scores (<50%)
- Missing research sources

**Solutions:**
```bash
# Verify materials data
python3 -c "from data.materials import load_materials_data; data = load_materials_data(); print(f'Materials loaded: {len(data)} entries')"

# Test specific material lookup
python3 -c "from data.materials import load_materials_data; data = load_materials_data(); print('Aluminum' in [m['name'] for m in data])"
```

### 2. Author Component Issues

#### Problem: No Author Generated
**Symptoms:**
- Missing author metadata
- Empty author fields
- Generic author names

**Diagnosis:**
```bash
# Test author component
python3 run.py --material "Steel" --components "author"

# Verify author personas
python3 -c "from components.author.author_generator import AuthorGenerator; ag = AuthorGenerator(); print(f'Author personas available: {len(ag.personas)}')"
```

**Solutions:**
1. Check `components/author/personas/` directory exists with YAML files
2. Verify persona YAML files are properly formatted
3. Ensure material-to-author mapping logic works

### 3. Badge Symbol Component Issues

#### Problem: Generic or Missing Badges
**Symptoms:**
- Default badge symbols
- Missing category-specific badges
- Inconsistent badge styling

**Diagnosis:**
```bash
# Test badge generation
python3 run.py --material "Copper" --components "badgesymbol"

# Check badge mapping
python3 -c "from components.badgesymbol.badge_generator import BadgeSymbolGenerator; bg = BadgeSymbolGenerator(); print(f'Badge categories: {list(bg.category_badges.keys())}')"
```

### 4. Meta Tags Component Issues

#### Problem: SEO Meta Tags Missing
**Symptoms:**
- Empty meta description
- Missing keywords
- No Open Graph tags

**Diagnosis:**
```bash
# Test meta tags generation
python3 run.py --material "Titanium" --components "metatags"
```

### 5. JSON-LD Component Issues

#### Problem: Invalid Structured Data
**Symptoms:**
- JSON syntax errors
- Missing required properties
- Schema validation failures

**Diagnosis:**
```bash
# Test JSON-LD generation
python3 run.py --material "Ceramic" --components "jsonld"

# Validate JSON structure
python3 -c "import json; content = open('content/components/jsonld/ceramic-laser-cleaning.json').read(); json.loads(content); print('Valid JSON')"
```

### 6. Properties Table Component Issues

#### Problem: Empty or Malformed Tables
**Symptoms:**
- No property data in tables
- Missing units or values
- Formatting issues

**Diagnosis:**
```bash
# Test properties table
python3 run.py --material "Aluminum" --components "propertiestable"
```

---

## API-Related Issues

### Connection Problems
**Reference:** See [API Error Handling Guide](docs/api/ERROR_HANDLING.md) for comprehensive API troubleshooting.

**Quick Fixes:**
```bash
# Test specific API provider
python3 scripts/tools/api_terminal_diagnostics.py deepseek

# Check API configuration
python3 -c "from run import API_PROVIDERS; print(list(API_PROVIDERS.keys()))"
```

### Content Generation Failures
**Symptoms:**
- Incomplete content files
- Files ending mid-sentence
- Multiple frontmatter sections

**Solutions:**
1. Check terminal output for API errors
2. Verify API keys are properly set
3. Test with smaller materials first

---

## Schema and Validation Issues

### Schema Validation Errors
**Symptoms:**
- Component factory creation failures
- Invalid YAML/JSON output
- Missing required fields

**Diagnosis:**
```bash
# Verify schema files
ls -la schemas/
python3 -c "import json; schema = json.load(open('schemas/frontmatter.json')); print(f'Schema loaded: {len(schema)} properties')"

# Test schema validation
python3 -c "from schemas.validator import validate_frontmatter; print('Schema validator working')"
```

### Data Structure Problems
**Common Issues:**
1. **Missing materialProperties section**: Check PropertyResearcher configuration
2. **Invalid machineSettings**: Verify machine settings generator
3. **Malformed YAML**: Check for proper indentation and quoting

---

## Performance Issues

### Slow Generation Times
**Symptoms:**
- Long response times (>60 seconds)
- Timeout errors
- Memory usage spikes

**Optimization:**
```bash
# Test with minimal material set
python3 run.py --material "Steel" --components "author,badgesymbol"

# Monitor memory usage
python3 -c "import psutil; print(f'Available memory: {psutil.virtual_memory().available // (1024**3)} GB')"
```

### High Memory Usage
**Solutions:**
1. Process materials individually rather than in batches
2. Clear cache between runs: `rm -rf .cache/`
3. Use specific component generation rather than all components

---

## File System Issues

### Permission Problems
**Symptoms:**
- Cannot write to content/ directory
- Schema files not readable
- Cache write failures

**Solutions:**
```bash
# Check permissions
ls -la content/components/
chmod -R 755 content/
chmod -R 755 schemas/

# Verify write access
touch content/test_file && rm content/test_file && echo "Write access OK"
```

### Missing Directories
**Common Missing Paths:**
```bash
# Create required directories
mkdir -p content/components/{frontmatter,author,badgesymbol,metatags,jsonld,propertiestable}
mkdir -p logs/
mkdir -p .cache/
```

---

## Common Error Messages

### "No generator found for component type: X"
**Cause:** Component factory cannot find the specified component
**Solution:**
```bash
# Verify component exists
python3 -c "from components.component_factory import ComponentGeneratorFactory; factory = ComponentGeneratorFactory(); print(factory.list_available_components())"

# Check component directory
ls -la components/X/
```

### "PropertyResearcher initialization failed"
**Cause:** Material data or property research system failure
**Solution:**
```bash
# Check materials data
python3 -c "from data.materials import load_materials_data; load_materials_data()"

# Verify property researcher
python3 -c "from components.frontmatter.research.property_researcher import PropertyResearcher; PropertyResearcher()"
```

### "Schema validation failed"
**Cause:** Generated content doesn't match expected schema
**Solution:**
```bash
# Check schema files
find schemas/ -name "*.json" -exec python3 -c "import json; json.load(open('{}'))" \;

# Validate specific content
python3 -c "from schemas.validator import validate_content; validate_content('content/components/frontmatter/test.md')"
```

---

## Debugging Tools and Commands

### Component Testing
```bash
# Test individual component
python3 run.py --material "TestMaterial" --components "frontmatter"

# Test all components for one material
python3 run.py --material "Aluminum" --components "all"

# Debug mode with verbose output
python3 run.py --material "Steel" --components "frontmatter" --debug
```

### System Validation
```bash
# Run integration tests
python3 -m pytest tests/test_consolidated_architecture.py -v

# Check system health
python3 -c "
from components.component_factory import ComponentGeneratorFactory
from data.materials import load_materials_data
from api.client_manager import test_api_connectivity

factory = ComponentGeneratorFactory()
materials = load_materials_data()
api_status = test_api_connectivity('deepseek')

print(f'Components: {len(factory.list_available_components())}')
print(f'Materials: {len(materials)}')
print(f'API: {\"✅\" if api_status else \"❌\"}')
"
```

### Log Analysis
```bash
# Check recent logs
tail -f logs/z_beam_generator.log

# Search for errors
grep -i error logs/z_beam_generator.log

# Check API calls
grep -i "api" logs/z_beam_generator.log
```

---

## Migration from Legacy System

### If You Have Old Components
**Archived Components:** text, bullets, caption, tags, settings, table (old version)
**Current Components:** frontmatter, author, badgesymbol, metatags, jsonld, propertiestable

**Migration Steps:**
1. **Update run commands**: Replace old component names with new ones
2. **Check content structure**: New frontmatter includes both materialProperties and machineSettings
3. **Update any custom scripts**: Use new component factory methods

### Configuration Updates
```bash
# Old configuration check
grep -r "text\|bullets\|caption" config/ || echo "No legacy references found"

# Update any hardcoded component lists
find . -name "*.py" -exec grep -l "components.*=.*\[.*text.*\]" {} \;
```

---

## Contact and Support

### Self-Service Resources
1. **Quick Reference**: [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)
2. **Architecture Guide**: [docs/CONSOLIDATED_ARCHITECTURE_GUIDE.md](docs/CONSOLIDATED_ARCHITECTURE_GUIDE.md)
3. **API Documentation**: [docs/api/ERROR_HANDLING.md](docs/api/ERROR_HANDLING.md)

### Diagnostic Commands Summary
```bash
# Complete system check
python3 run.py --check-env && python3 run.py --test-api

# Component validation
python3 -c "from components.component_factory import ComponentGeneratorFactory; print(ComponentGeneratorFactory().list_available_components())"

# Test generation
python3 run.py --material "Aluminum" --components "frontmatter,author"

# Check logs
tail -20 logs/z_beam_generator.log
```

---

**Last Updated:** September 2025  
**Architecture Version:** Consolidated 6-Component System  
**Compatible with:** PropertyResearcher integration, DataMetrics compliance