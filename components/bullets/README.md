# Bullets Component

Generates key characteristics and bullet points for laser cleaning materials.

## 📋 Overview

The bullets component creates concise, technical bullet points highlighting the most important characteristics and applications of materials for laser cleaning processes.

## 🔧 Configuration

```yaml
# Component configuration
bullets:
  enabled: true
  api_provider: deepseek
  ai_detection: true
```

## 📝 Usage

```python
from components.bullets.generator import BulletsComponentGenerator

generator = BulletsComponentGenerator()
result = generator.generate(
    material_name="aluminum",
    material_data=material_data,
    api_client=api_client
)
```

## 📊 Output Format

The component generates bullet points covering:
- Material properties relevant to laser cleaning
- Surface preparation requirements
- Cleaning parameter recommendations
- Safety considerations

## 🧪 Testing

Run component tests:
```bash
python3 -m pytest components/bullets/testing/ -v
```

## 🔗 Dependencies

- Requires: DeepSeek API client
- Optional: AI detection service for quality optimization</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/components/bullets/README.md
