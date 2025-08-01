# Table Generator Component

The Table Generator component is responsible for creating formatted Markdown tables from structured data in the frontmatter. It validates and ensures consistent formatting of tables.

## Features

- Generates Markdown tables from structured data (objects, lists, key-value pairs)
- Enforces consistent table formatting with proper spacing and alignment
- Validates table structure to ensure headers, separators, and expected row counts
- Processes multiple frontmatter keys to generate comprehensive tables

## Configuration

The Table Generator can be configured in `run.py` with the following options:

```python
"table": {
    "enabled": True,
    "ai_provider": "deepseek",
    "options": {
        "temperature": 0.7,
        "max_tokens": 1500
    },
    "rows": 3,  # Minimum number of expected rows
    "table_keys": ["technicalSpecifications", "applications", "compatibility"]
}
```

## Format Options

The prompt.yaml file contains additional formatting options:

```yaml
format:
  header_style: "bold"
  include_descriptions: true
  table_style: "detailed"
  section_title_format: "## {title}"
  preserve_original_values: true
```

## Usage

The TableGenerator processes structured data in the frontmatter and generates properly formatted Markdown tables:

- Objects (dictionaries) are formatted as key-value tables
- Lists of objects are formatted as multi-column tables
- Lists of simple values are formatted as single-column tables

## Example Output

```markdown
## Technical Specifications
| Parameter | Value |
| --- | --- |
| density | 2.7 g/cm³ |
| meltingPoint | 660°C |
| thermalConductivity | 237 W/(m·K) |

## Applications
| Name | Description |
| --- | --- |
| Aerospace | Used in aircraft structures |
| Electronics | Excellent conductor |
| Construction | Lightweight building material |
```

## Testing

Run the tests for the Table Generator component:

```bash
# Run basic test script
python3 components/table/test_markdown_tables.py

# Run pytest tests (requires pytest)
# pip install pytest
pytest components/table/test_table_pytest.py
```
