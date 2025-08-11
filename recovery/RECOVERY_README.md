# Material Generation Recovery System

A comprehensive system for validating generated content and recovering from component failures in the Z-Beam material generation pipeline.

## Overview

When generating materials, some components may fail due to:
- API timeouts or connectivity issues
- Rate limiting
- Content validation failures  
- File system issues

The recovery system provides:
1. **Content Validation** - Analyze generated markdown files for quality and completeness
2. **Failure Detection** - Identify missing, empty, or invalid components
3. **Selective Recovery** - Re-run only failed components with timeout protection
4. **Quality Scoring** - Rate content quality and provide improvement suggestions

## Quick Start

### Basic Validation

```bash
# Validate all materials
python3 validate.py

# Validate specific material
python3 validate.py "Tempered Glass"

# Auto-recover all failures
python3 validate.py --recover
```

### Manual Recovery

```bash
# Advanced validation with recovery options
python3 recovery_system.py --scan --recover --timeout 60 --retry 3

# Validate specific subject only
python3 recovery_system.py --subject "Ceramic Coating"
```

## Component Validation Rules

### Status Categories

- **SUCCESS** (✅): Content meets quality standards (70%+ score)
- **INVALID** (⚠️): Content exists but has quality issues (40-70% score)
- **FAILED** (❌): Content is severely inadequate (<40% score)
- **EMPTY** (🔍): File exists but contains only delimiters or minimal content
- **MISSING** (🚨): File doesn't exist

### Quality Scoring

Each component is scored on:

**Frontmatter (YAML)**
- Valid YAML structure (30 points)
- Required fields: name, description, category (10 points each)
- Minimum content size (20 points)

**Tables**
- Markdown table presence (30 points)
- Section headers (20 points)  
- Complete table structure (20 points)
- Minimum size requirement (20 points)

**Bullets**
- Bullet points found (30 points)
- Adequate count (3+) (20 points)
- Bold formatting present (10 points)
- Minimum size requirement (20 points)

**JSON-LD**
- JSON-LD structure markers (@context, @type) (30 points)
- Valid content structure (40 points)

**Tags**
- Tag count (3+ tags) (40 points)
- Content presence (30 points)

**Metatags**
- Meta tag structure (30 points)
- HTML tag patterns (40 points)

## Usage Examples

### Example 1: Check Current Status

```bash
python3 validate.py
```

Output:
```
🔍 Scanning all materials...

📈 Summary: 3/5 materials healthy

⚠️  Materials needing attention (2):
  • Tempered Glass: frontmatter, metatags, jsonld
  • Ceramic Coating: metatags

💡 Run 'python3 validate.py --recover' to auto-fix issues
```

### Example 2: Detailed Material Analysis

```bash
python3 validate.py "Tempered Glass"
```

Output:
```
🔍 Validating Tempered Glass...

📊 Validation Report: Tempered Glass
==================================================
Overall Status: INVALID
Success Rate: 5/8 (62.5%)

❌ Failed Components: frontmatter, metatags, jsonld

📋 Component Details:
  ✅ table: success (2156 bytes, quality: 90.0%)
  ✅ bullets: success (456 bytes, quality: 80.0%)
  ✅ caption: success (123 bytes, quality: 70.0%)
  ✅ propertiestable: success (234 bytes, quality: 75.0%)
  ✅ tags: success (67 bytes, quality: 85.0%)
  ❌ frontmatter: empty (8 bytes, quality: 0.0%)
    ⚠️  Contains only empty frontmatter delimiters
  ❌ metatags: empty (8 bytes, quality: 0.0%)  
    ⚠️  Contains only empty frontmatter delimiters
  ❌ jsonld: empty (8 bytes, quality: 0.0%)
    ⚠️  Contains only empty frontmatter delimiters

💡 Recommendations:
  🔄 Re-run empty components: frontmatter, metatags, jsonld (likely API timeouts)
  💡 Consider running components individually to avoid API timeouts
  🔧 Frontmatter failure may indicate API connectivity issues

🔧 Recovery Commands:
  python3 run.py --component frontmatter --subject "Tempered Glass"
  python3 run.py --component metatags --subject "Tempered Glass"
  python3 run.py --component jsonld --subject "Tempered Glass"
```

### Example 3: Automated Recovery

```bash
python3 validate.py --recover
```

Output:
```
🔍 Scanning all materials for recovery...

🔄 Recovering Tempered Glass...
Recovery results: 2/3 succeeded

🔄 Recovering Ceramic Coating...
Recovery results: 1/1 succeeded
```

## Advanced Features

### Custom Timeout and Retry Settings

```bash
python3 recovery_system.py --scan --recover --timeout 90 --retry 5
```

### Programmatic Usage

```python
from recovery_system import MaterialRecoverySystem, print_validation_report

# Initialize system
recovery = MaterialRecoverySystem()

# Validate specific material
report = recovery._validate_material("Tempered Glass")
print_validation_report(report)

# Run recovery if needed
if report.failed_components:
    results = recovery.run_recovery(
        "Tempered Glass", 
        report.failed_components,
        timeout=60,
        retry_count=3
    )
```

## Integration with Existing Workflow

### 1. After Initial Generation

```bash
# Generate material
python3 run.py --subject "New Material"

# Immediately validate
python3 validate.py "New Material"

# Recover failures if any
python3 validate.py --recover
```

### 2. Batch Processing

```bash
# Generate multiple materials
for material in "Glass" "Metal" "Ceramic"; do
    python3 run.py --subject "$material"
done

# Validate all at once
python3 validate.py

# Auto-recover any failures
python3 validate.py --recover
```

### 3. Scheduled Maintenance

```bash
#!/bin/bash
# Daily validation script

echo "$(date): Running material validation..."
python3 validate.py --recover >> validation.log 2>&1
echo "$(date): Validation complete"
```

## Troubleshooting

### Common Issues

**Empty Components (API Timeouts)**
- Solution: Re-run individual components
- Prevention: Use shorter timeouts, run components separately

**Persistent Failures**
- Check API connectivity
- Verify API keys and configuration
- Check network/firewall settings

**Low Quality Scores**
- Review component prompts
- Check if content meets minimum requirements
- Validate YAML/JSON syntax

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## File Structure

```
z-beam-generator/
├── recovery_system.py      # Main recovery system
├── validate.py            # Quick validation script
├── content/components/     # Generated content
│   ├── frontmatter/
│   ├── metatags/
│   ├── table/
│   └── ...
└── logs/                  # Recovery logs
```

## Configuration

The system automatically detects components and subjects from the file system. To customize:

```python
# Custom component list
recovery = MaterialRecoverySystem()
recovery.components = ['frontmatter', 'table', 'bullets']  # Subset

# Custom content directory
recovery = MaterialRecoverySystem(content_dir="custom/path")

# Custom validation rules
recovery.validator.min_content_sizes['custom_component'] = 200
```

## Best Practices

1. **Run validation after each generation session**
2. **Use recovery for API timeout issues**
3. **Monitor quality scores for content improvement**
4. **Set appropriate timeouts based on component complexity**
5. **Check logs for recurring patterns**
6. **Validate before deploying generated content**

## Performance Tips

- Use `--timeout 45` for faster recovery (trade-off with success rate)
- Run recovery immediately after detection for best results
- Use individual component recovery for persistent failures
- Monitor API rate limits and adjust retry counts accordingly
