# Categories Data Generator

A standalone tool for generating and maintaining the Categories.yaml database with AI-powered material property research.

## Quick Start

```bash
# Generate initial Categories.yaml database
python3 scripts/generators/categories_generator.py --generate

# Refresh existing database with updated research  
python3 scripts/generators/categories_generator.py --refresh

# Validate existing Categories.yaml structure
python3 scripts/generators/categories_generator.py --validate

# Enable verbose logging
python3 scripts/generators/categories_generator.py --generate --verbose
```

## What it Does

1. **Extracts Categories**: Parses `data/Materials.yaml` to identify all material categories and subcategories
2. **AI Research**: Uses API-based AI research to validate and enhance property ranges for each category/subcategory
3. **Generates Database**: Creates comprehensive `data/Categories.yaml` with scientifically researched property ranges
4. **Validates Structure**: Ensures generated database follows the JSON schema specification

## Generated Output

The tool creates `data/Categories.yaml` with:

- **Metadata**: Version, generation date, source tracking, confidence thresholds
- **Category Ranges**: Inherited from existing `Materials.yaml` structure  
- **Subcategory Properties**: AI-researched property ranges for each subcategory
- **Applications**: Common laser cleaning applications per category
- **Research Sources**: Documentation of data provenance and confidence levels

## Features

- ✅ **Standalone Operation**: No integration dependencies
- ✅ **Fail-Fast Architecture**: Validates all inputs and dependencies immediately
- ✅ **AI-Powered Research**: Uses existing API infrastructure for property validation  
- ✅ **Schema Validation**: Ensures data quality and structure consistency
- ✅ **Graceful Degradation**: Works in validation-only mode if API unavailable
- ✅ **Version Tracking**: Monitors changes to source Materials.yaml

## Architecture

- **Input**: `data/Materials.yaml` (existing material database)
- **Output**: `data/Categories.yaml` (generated property ranges database)
- **Schema**: `schemas/categories_schema.json` (validation specification)
- **API Integration**: Uses existing API clients for research validation

## Status: Ready to Use

The generator is fully functional and tested. It successfully:
- ✅ Parses Materials.yaml structure
- ✅ Generates Categories.yaml database 
- ✅ Validates output against schema
- ✅ Handles API availability gracefully
- ✅ Provides comprehensive logging

## Future Enhancements

When API integration is fully available:
- Enhanced AI research for subcategory-specific property ranges
- Research source validation and confidence scoring
- Periodic refresh with latest scientific literature
- Advanced property correlation analysis