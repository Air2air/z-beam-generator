# Z-Beam Version Logging System

## Overview

The Z-Beam Version Logging System automatically tracks and maintains version history for all generated content components. This feature provides comprehensive audit trails, generation metadata, and version management capabilities.

## Features

### 🔄 Automatic Version Tracking
- **File Footer Logs**: Every component file includes a standardized version footer
- **JSON History Files**: Separate version history files for detailed tracking
- **Generation Metadata**: Captures author, timestamp, platform, and system information

### 📊 Version History Management
- **Persistent Storage**: Version histories stored in `content/version_history/`
- **Automatic Cleanup**: Keeps last 10 versions to prevent storage bloat
- **CLI Access**: Command-line interface for viewing version histories

### 🎯 Comprehensive Metadata
Each version entry includes:
- Generation timestamp (ISO format)
- Material and component type
- Author information
- Generator version
- Platform and Python version
- File path and system hostname

## File Structure

```
content/
├── components/
│   └── {component_type}/
│       └── {material}-laser-cleaning.md  # Content with version footer
└── version_history/
    └── {material}-{component_type}-versions.json  # Detailed history
```

## Usage

### Command Line Interface

```bash
# View version history for a specific component
python3 run.py --version-history "Alumina:text"

# Generate content (automatically includes version logging)
python3 run.py --material "Alumina"
```

### Programmatic Access

```python
from utils.file_operations import (
    display_version_history,
    get_version_history,
    cleanup_old_versions
)

# Display formatted version history
display_version_history("Alumina", "text")

# Get raw version data
history = get_version_history("Alumina", "text")

# Clean up old versions (keep last 5)
removed = cleanup_old_versions("Alumina", "text", keep_versions=5)
```

## Version Log Format

### File Footer Format
```markdown
---
Version Log - Generated: 2025-09-06T11:10:04.733418
Material: Alumina
Component: text
Generator: Z-Beam v2.1.0
Author: Alessandro Moretti
Platform: Darwin (3.12.4)
File: /path/to/component.md
---
```

### JSON History Format
```json
{
  "material": "Alumina",
  "component_type": "text",
  "versions": [
    {
      "material": "Alumina",
      "component_type": "text",
      "filepath": "/path/to/component.md",
      "timestamp": "2025-09-06T11:10:04.733418",
      "generator_version": "2.1.0",
      "system_info": {
        "platform": "Darwin",
        "python_version": "3.12.4",
        "hostname": "Todds-MacBook-Pro.local"
      },
      "author": "Alessandro Moretti"
    }
  ]
}
```

## Integration Points

### Automatic Integration
The version logging system is automatically integrated into:
- `generators/workflow_manager.py` - All component generation workflows
- `utils/file_operations.py` - File saving operations
- `run.py` - Command-line interface

### Backward Compatibility
- Existing components continue to work without modification
- Version logging is additive - doesn't break existing functionality
- Optional features can be disabled if needed

## Configuration

### Version Retention
```python
# In utils/file_operations.py
KEEP_VERSIONS = 10  # Configurable retention count
```

### Generator Version
```python
# Update in create_version_log_entry()
"generator_version": "2.1.0"  # Update as needed
```

## Benefits

### 🔍 Audit Trail
- Complete history of content generation
- Author and timestamp tracking
- System and platform information

### 🛠️ Debugging Support
- Generation context for troubleshooting
- Platform-specific issue identification
- Version comparison capabilities

### 📈 Content Management
- Track content evolution over time
- Identify regeneration patterns
- Support for rollback scenarios

### 🤖 AI Integration
- Generation metadata for AI model improvement
- Quality tracking over time
- Performance analytics support

## API Reference

### Core Functions

#### `add_version_log_to_content(content, material, component_type, filepath)`
Adds version log footer to component content.

#### `create_version_log_entry(material, component_type, filepath)`
Creates a version log entry dictionary.

#### `save_version_history(material, component_type, version_entry)`
Saves version entry to persistent history file.

#### `get_version_history(material, component_type)`
Retrieves version history for a component.

#### `display_version_history(material, component_type)`
Displays formatted version history.

#### `cleanup_old_versions(material, component_type, keep_versions=5)`
Removes old versions, keeping only recent ones.

## Future Enhancements

### Planned Features
- **Version Diffing**: Compare different versions of content
- **Rollback Support**: Restore previous versions
- **Version Tags**: Label important versions (e.g., "production", "staging")
- **Bulk Operations**: Manage versions across multiple components
- **Export Capabilities**: Export version histories to various formats

### Integration Opportunities
- **Git Integration**: Link versions to Git commits
- **Database Storage**: Migrate from JSON to database for better querying
- **Web Interface**: Browser-based version history viewer
- **API Endpoints**: REST API for version management

## Troubleshooting

### Common Issues

#### Version History Not Showing
```bash
# Check if version history files exist
find content/version_history -name "*.json"

# Manually trigger version logging
python3 -c "from utils.file_operations import display_version_history; display_version_history('Material', 'component')"
```

#### Storage Bloat
```python
# Clean up old versions
from utils.file_operations import cleanup_old_versions
cleanup_old_versions("Material", "component", keep_versions=5)
```

#### Permission Issues
```bash
# Ensure write permissions on content directory
chmod -R 755 content/
```

## Contributing

When modifying the version logging system:

1. **Test Thoroughly**: Ensure version logging works across all component types
2. **Maintain Compatibility**: Don't break existing functionality
3. **Update Documentation**: Keep this README current
4. **Version Updates**: Update generator version when making changes
5. **Performance**: Monitor impact on generation speed

## Changelog

### v2.1.0 (Current)
- ✅ Automatic version logging for all components
- ✅ JSON history file storage
- ✅ CLI version history viewer
- ✅ Comprehensive metadata capture
- ✅ Automatic cleanup of old versions

### v2.0.0 (Previous)
- Basic version tracking in frontmatter components only
- Manual version management
- Limited metadata capture</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/docs/VERSION_LOGGING_SYSTEM.md
