# Table Component

Generates structured data tables for laser cleaning materials.

## 📋 Overview

The table component creates comprehensive data tables containing technical specifications and properties for materials used in laser cleaning applications.

## 🔧 Configuration

```yaml
# Component configuration
table:
  enabled: true
  api_provider: grok
  ai_detection: false
```

## 📝 Usage

```python
from components.table.generator import TableComponentGenerator

generator = TableComponentGenerator()
result = generator.generate(
    material_name="titanium",
    material_data=material_data,
    api_client=api_client
)
```

## 📊 Output Format

Generates structured tables with:
- Material specifications
- Laser cleaning parameters
- Performance characteristics
- Safety data

## 🧪 Testing

Run component tests:
```bash
python3 -m pytest components/table/testing/ -v
```

## 🔗 Dependencies

- Requires: Grok API client
- Optional: AI detection service</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/components/table/README.md
