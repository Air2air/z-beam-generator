# Command Reference for AI Assistants

**🤖 Quick command lookup for AI assistants helping users**

---

## 🚨 Emergency Diagnostics (Use First)

### API Problem Diagnosis
```bash
# Comprehensive API diagnosis with content impact analysis
python3 scripts/tools/api_terminal_diagnostics.py winston content/components/text/alumina-laser-cleaning.md

# Test specific API provider
python3 -c "from api.client_manager import test_api_connectivity; test_api_connectivity('winston')"
python3 -c "from api.client_manager import test_api_connectivity; test_api_connectivity('deepseek')"
python3 -c "from api.client_manager import test_api_connectivity; test_api_connectivity('grok')"
```

## 🎯 Content Generation Commands (Working Commands Only)

### Basic Generation
```bash
# Generate all materials (batch mode)
python3 run.py --all

# Generate specific material
python3 run.py --material "Steel"

# Generate specific material with components
python3 run.py --material "Copper" --components "frontmatter,text"

# Run test mode
python3 run.py --test
```

### Component-Specific Generation
```bash
# Text component only
python3 run.py --material "Alumina" --components "text"

# Frontmatter only
python3 run.py --material "Steel" --components "frontmatter"

# JSON-LD component
python3 run.py --material "aluminum" --components "jsonld"

# Multiple components
python3 run.py --material "Copper" --components "frontmatter,text,caption"
```

## 🩺 Troubleshooting Commands

### API Connectivity Issues
```bash
# Validate API environment
python3 -c "from api.client_manager import validate_api_environment; print(validate_api_environment())"

# Test API endpoints manually
python3 -c "
import requests
endpoints = ['https://api.winston.ai', 'https://api.gowinston.ai', 'https://api.deepseek.com']
for endpoint in endpoints:
    try:
        response = requests.get(endpoint, timeout=5)
        print(f'{endpoint}: {response.status_code}')
    except Exception as e:
        print(f'{endpoint}: ERROR - {str(e)[:100]}')
"
```

### Content Issues
```bash
# Find incomplete content files
find content/components -name "*.md" -exec grep -l "before significant" {} \;

# Check for nested YAML properties
python3 scripts/tools/fix_nested_yaml_properties.py

# Validate frontmatter structure
python3 -c "
import os, yaml
for root, dirs, files in os.walk('content/components/frontmatter'):
    for file in files:
        if file.endswith('.md'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r') as f:
                    content = f.read()
                    if '---' in content:
                        parts = content.split('---')
                        if len(parts) >= 3:
                            yaml.safe_load(parts[1])
                            print(f'✅ {file}')
            except Exception as e:
                print(f'❌ {file}: {e}')
"
```

## 📊 System Information Commands

### Available Materials
```bash
# Show available materials
python3 -c "from data.materials import load_materials; materials = load_materials(); print(f'Total materials: {len([item for category in materials.get("materials", {}).values() for item in category.get("items", [])])}')"

# List all available materials
python3 -c "
from data.materials import load_materials
materials = load_materials()
for category, data in materials.get('materials', {}).items():
    print(f'{category}: {len(data.get("items", []))} materials')
    for item in data.get('items', [])[:3]:
        print(f'  - {item.get("name", "Unknown")}')
    if len(data.get('items', [])) > 3:
        print(f'  ... and {len(data.get("items", [])) - 3} more')
"
```

### Environment Validation
```bash
# Check Python environment
python3 --version

# Check installed packages
pip list | grep -E "(requests|yaml|openai)"

# Validate workspace structure
ls -la docs/ components/ api/ data/
```

## 🗂️ File Management Commands

### Content Organization
```bash
# List all generated content
find content/components -name "*.md" -type f | wc -l

# Show content by component
for component in text frontmatter bullets table metatags jsonld caption author; do
    count=$(find content/components/$component -name "*.md" 2>/dev/null | wc -l || find content/components/$component -name "*.yaml" 2>/dev/null | wc -l)
    echo "$component: $count files"
done

# Clean up empty directories
find content/components -type d -empty -delete
```

## 🎯 AI Assistant Usage Patterns

### For "API not working" issues:
1. `python3 scripts/tools/api_terminal_diagnostics.py winston`
2. Check terminal output with `get_terminal_output(terminal_id)`
3. Use working test: `python3 run.py --test`

### For "Content incomplete" issues:
1. `find content/components -name "*.md" -exec grep -l "before significant" {} \;`
2. `python3 run.py --material "MaterialName" --components "text"`
3. `python3 scripts/tools/api_terminal_diagnostics.py winston [content_file]`

### For "Setup help" requests:
1. `python3 run.py --test`
2. Guide through `.env` file setup if API keys missing
3. Test specific material: `python3 run.py --material "aluminum"`

### For "Winston SSL error" reports:
1. Explain that this is a known issue that's been fixed
2. Configuration now uses `https://api.gowinston.ai`
3. Test with: `python3 scripts/tools/api_terminal_diagnostics.py winston`

---

**🤖 AI Assistant Note**: Only use the 4 working commands: `--material`, `--components`, `--all`, `--test`. All other documented commands in old documentation are NOT IMPLEMENTED and will fail with "unrecognized arguments" errors. Always combine commands with terminal output analysis using `get_terminal_output()` for accurate diagnosis.

### Content Issues
```bash
# Find incomplete content files
find content/components -name "*.md" -exec grep -l "before significant" {} \;

# Check for nested YAML properties
python3 scripts/tools/fix_nested_yaml_properties.py

# Validate frontmatter structure
python3 -c "
import os, yaml
for root, dirs, files in os.walk('content/components/frontmatter'):
    for file in files:
        if file.endswith('.md'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r') as f:
                    content = f.read()
                    if '---' in content:
                        parts = content.split('---')
                        if len(parts) >= 3:
                            yaml.safe_load(parts[1])
                            print(f'✅ {file}')
            except Exception as e:
                print(f'❌ {file}: {e}')
"
```

### Network and SSL Issues
```bash
# Test DNS resolution
python3 -c "
import socket
domains = ['api.winston.ai', 'api.gowinston.ai', 'api.deepseek.com', 'api.x.ai']
for domain in domains:
    try:
        ip = socket.gethostbyname(domain)
        print(f'{domain}: {ip}')
    except Exception as e:
        print(f'{domain}: ERROR - {e}')
"

# Test SSL connectivity
python3 -c "
import ssl, socket
hostname = 'api.winston.ai'
try:
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(f'SSL connection successful: {ssock.version()}')
except Exception as e:
    print(f'SSL connection failed: {e}')
"
```

## 📊 System Information Commands

### Configuration Display
```bash
# Show component configuration
python3 run.py --show-config

# Display API provider configuration
python3 -c "from run import get_api_providers; import json; print(json.dumps(get_api_providers(), indent=2))"

# Show available materials
python3 -c "from data.materials import load_materials; materials = load_materials(); print(f'Total materials: {len([item for category in materials.get(\"materials\", {}).values() for item in category.get(\"items\", [])])}')"
```

### Environment Validation
```bash
# Check Python environment
python3 --version

# Check installed packages
pip list | grep -E "(requests|yaml|openai)"

# Validate workspace structure
ls -la docs/ components/ api/ data/
```

## 🧪 Testing Commands

### API Testing
```bash
# Test all API providers
python3 test_api_providers.py

# API client caching test
python3 test_api_client_caching.py

# API client demo
python3 test_api_client_demo.py
```

### Component Testing
```bash
# Test frontmatter generation
python3 test_frontmatter.py

# Test formula handling
python3 test_formula_direct.py

# Test material override
python3 test_override_material.py
```

### Error Workflow Testing
```bash
# Run error workflow
./run_error_workflow.sh

# Test error patterns
python3 -c "
import json
with open('test_errors/latest_errors.json', 'r') as f:
    errors = json.load(f)
    print(f'Total errors: {len(errors)}')
    for error in errors[:5]:
        print(f'- {error.get(\"type\", \"Unknown\")}: {error.get(\"message\", \"No message\")[:50]}...')
"
```

## 🗂️ File Management Commands

### Content Organization
```bash
# List all generated content
find content/components -name "*.md" -type f | wc -l

# Show content by component
for component in text frontmatter bullets table metatags jsonld; do
    count=$(find content/components/$component -name "*.md" 2>/dev/null | wc -l)
    echo "$component: $count files"
done

# Clean up empty directories
find content/components -type d -empty -delete
```

### Documentation Management
```bash
# Count documentation files
find docs -name "*.md" -type f | wc -l

# Show documentation structure
tree docs/ -I '*.pyc|__pycache__'

# Find duplicate documentation
find . -name "*.md" -exec basename {} \; | sort | uniq -d
```

## 🚀 Material Management

### Add/Remove Materials
```bash
# Remove specific material (use carefully)
python3 remove_material.py --material "Material Name" --execute

# List all available materials
python3 -c "
from data.materials import load_materials
materials = load_materials()
for category, data in materials.get('materials', {}).items():
    print(f'{category}: {len(data.get(\"items\", []))} materials')
    for item in data.get('items', [])[:3]:
        print(f'  - {item.get(\"name\", \"Unknown\")}')
    if len(data.get('items', [])) > 3:
        print(f'  ... and {len(data.get(\"items\", [])) - 3} more')
"
```

### Path Cleanup (One-time operations)
```bash
# Clean file paths (already done, but available)
python3 cleanup_paths.py

# Rename files to clean format
python3 scripts/rename_clean_paths.py
```

## 🎯 AI Assistant Usage Patterns

### For "API not working" issues:
1. `python3 run.py --test-api`
2. `python3 scripts/tools/api_terminal_diagnostics.py winston`
3. Check terminal output with `get_terminal_output(terminal_id)`

### For "Content incomplete" issues:
1. `find content/components -name "*.md" -exec grep -l "before significant" {} \;`
2. `python3 run.py --material "MaterialName" --components "text"`
3. `python3 scripts/tools/api_terminal_diagnostics.py winston [content_file]`

### For "Setup help" requests:
1. `python3 run.py --check-env`
2. `python3 run.py --test-api`
3. Guide through `.env` file setup if API keys missing

### For "Winston SSL error" reports:
1. Explain that this is a known issue that's been fixed
2. Configuration now uses `https://api.gowinston.ai`
3. Test with: `python3 scripts/tools/api_terminal_diagnostics.py winston`

---

**🤖 AI Assistant Note**: Always combine commands with terminal output analysis using `get_terminal_output()` for accurate diagnosis. Response objects often show `error: None` while terminal contains actual error details.
