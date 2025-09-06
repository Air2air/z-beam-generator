# Properties Table Component

Generates technical properties tables for laser cleaning materials.

## 📋 Overview

The propertiestable component creates structured, technical tables containing key material properties relevant to laser cleaning processes.

## 🔧 Configuration

```yaml
# Component configuration
propertiestable:
  enabled: true
  api_provider: none
  data_source: material_data
```

## 📝 Usage

```python
from components.propertiestable.generator import PropertiesTableComponentGenerator

generator = PropertiesTableComponentGenerator()
result = generator.generate(
    material_name="steel",
    material_data=material_data
)
```

## 📊 Output Format

Generates a markdown table with columns for:
- Property name
- Value
- Unit
- Description/Relevance to laser cleaning

## 🧪 Testing

Run component tests:
```bash
python3 -m pytest components/propertiestable/testing/ -v
```

## 🔗 Dependencies

- No external API required
- Uses material data from frontmatter or data files</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/components/propertiestable/README.md
