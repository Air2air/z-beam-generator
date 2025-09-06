# Caption Component

Generates brief, descriptive captions for laser cleaning materials.

## 📋 Overview

The caption component creates concise, professional descriptions that summarize the key characteristics and applications of materials in laser cleaning contexts.

## 🔧 Configuration

```yaml
# Component configuration
caption:
  enabled: true
  api_provider: gemini
  ai_detection: true
```

## 📝 Usage

```python
from components.caption.generator import CaptionComponentGenerator

generator = CaptionComponentGenerator()
result = generator.generate(
    material_name="copper",
    material_data=material_data,
    api_client=api_client
)
```

## 📊 Output Format

Generates a single, well-crafted sentence that captures:
- Material type and category
- Primary laser cleaning applications
- Key material properties
- Professional tone suitable for technical documentation

## 🧪 Testing

Run component tests:
```bash
python3 -m pytest components/caption/testing/ -v
```

## 🔗 Dependencies

- Requires: Gemini API client
- Optional: AI detection service for quality optimization</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/components/caption/README.md
