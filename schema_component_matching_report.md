# Schema-Component Matching Analysis

## Executive Summary

- **Total Examples Analyzed**: 5
- **Schema Compliant Examples**: 4/5 (80.0%)
- **Fields Analyzed**: 21

## Field Usage Analysis

### Required Fields

| Field | Usage | Type(s) | Example Values |
|-------|-------|---------|----------------|
| compatibility | 100.0% (5/5) | list | list[3]; list[3] |
| chemicalProperties | 100.0% (5/5) | dict | dict[3]; dict[2] |
| category | 100.0% (5/5) | str | metal; ceramic |
| images | 100.0% (5/5) | dict | dict[2]; dict[4] |
| properties | 100.0% (5/5) | dict | dict[7]; dict[6] |
| title | 80.0% (4/5) | str | Comprehensive Guide to Laser Cleaning Aluminum Sur...; Advanced Laser Cleaning Techniques for Stoneware C... |
| environmentalImpact | 80.0% (4/5) | list | list[2]; list[2] |
| headline | 80.0% (4/5) | str | Advanced Laser Cleaning Solutions for Aluminum Com...; Precision Surface Treatment of Stoneware Using Pul... |
| outcomes | 80.0% (4/5) | list | list[2]; list[2] |
| applications | 80.0% (4/5) | list | list[2]; list[2] |

### Optional Fields

| Field | Usage | Type(s) | Example Values |
|-------|-------|---------|----------------|
| keywords | 100.0% (5/5) | str | aluminum laser cleaning, oxide removal, surface pr...; stoneware laser cleaning, ceramic surface treatmen... |
| description | 100.0% (5/5) | str | Aluminum (Al) is a lightweight metallic element wi...; Stoneware is a dense ceramic material with excelle... |
| name | 100.0% (5/5) | str | Aluminum; Stoneware |
| author | 100.0% (5/5) | str | Dr. Elena Rodriguez, Materials Engineering Special...; Dr. Evelyn Wu |
| regulatoryStandards | 100.0% (5/5) | str | ISO 9013, ASTM E2017, IEC 60825-1; ISO 11553-1, IEC 60825-1, EN 207/208 laser safety ... |
| composition | 100.0% (5/5) | list | list[3]; list[3] |
| technicalSpecifications | 80.0% (4/5) | dict | dict[7]; dict[7] |
| subject | 80.0% (4/5) | str | Aluminum; Stoneware |
| article_type | 80.0% (4/5) | str | material; material |
| materialType | 20.0% (1/5) | str | material |
| chemicalFormula | 20.0% (1/5) | str | N/A |

## Optimization Recommendations

1. Required field compliance is 90.0%. Some examples missing required fields.
2. Consider making these fields required: technicalSpecifications (80.0%), keywords (100.0%), subject (80.0%), article_type (80.0%), description (100.0%), name (100.0%), author (100.0%), regulatoryStandards (100.0%), composition (100.0%)
3. Required fields with low usage: title (80.0%), environmentalImpact (80.0%), headline (80.0%), outcomes (80.0%), applications (80.0%)
4. Schema defines 10 required fields out of 21 total fields used. Schema coverage: 47.6%

## Technical Assessment for Laser Cleaning Website

### Schema Completeness
- **Required field coverage**: 10/21 fields (47.6%)
- **High-usage optional fields**: 9 fields used in 80%+ examples
- **Schema compliance rate**: 80.0%

### Recommendations for Production

⚠️ **NEEDS MINOR OPTIMIZATION** - Good compliance with room for improvement