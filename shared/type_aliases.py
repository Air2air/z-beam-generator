"""
Type Aliases for Z-Beam Generator

Provides semantic type aliases for better code readability and IDE support.
Use these instead of raw Dict[str, Any] for domain-specific data structures.

Usage:
    from shared.type_aliases import MaterialData, FrontmatterData, ConfigData
    
    def process_material(data: MaterialData) -> ProcessedMaterial:
        # IDE now provides better autocomplete and type checking
        pass

Created: January 7, 2026
Part of Python Best Practices improvements
"""

from typing import Dict, List, Any, Union, TypeAlias, Literal

# ============================================================================
# Domain Data Types
# ============================================================================

MaterialData: TypeAlias = Dict[str, Any]
"""
Material data from Materials.yaml.
Keys: name, category, properties, relationships, etc.
"""

ContaminantData: TypeAlias = Dict[str, Any]
"""
Contaminant data from Contaminants.yaml.
Keys: name, category, appearance, removal_methods, etc.
"""

CompoundData: TypeAlias = Dict[str, Any]
"""
Compound data from Compounds.yaml.
Keys: name, formula, hazard_class, safety_data, etc.
"""

SettingsData: TypeAlias = Dict[str, Any]
"""
Settings data from Settings.yaml.
Keys: machineSettings, recommended_parameters, etc.
"""

# ============================================================================
# Processing Types
# ============================================================================

ProcessedMaterial: TypeAlias = Dict[str, Any]
"""Material data after enrichment and processing."""

FrontmatterData: TypeAlias = Dict[str, Any]
"""Frontmatter YAML structure for website content."""

ConfigData: TypeAlias = Dict[str, Any]
"""Configuration data from config.yaml files."""

# ============================================================================
# Generation Types
# ============================================================================

GenerationContext: TypeAlias = Dict[str, Any]
"""
Context data for content generation.
Keys: material_name, component_type, author_id, etc.
"""

GenerationResult: TypeAlias = Dict[str, Union[bool, str, Any]]
"""
Result from generation operation.
Keys: success, content, error, metadata, etc.
"""

PromptData: TypeAlias = Dict[str, Any]
"""
Data structure for prompt template rendering.
Keys: material_name, properties, context, voice_instructions, etc.
"""

# ============================================================================
# Validation Types
# ============================================================================

ValidationResult: TypeAlias = Dict[str, Any]
"""
Result from validation operation.
Keys: valid, errors, warnings, metadata, etc.
"""

SchemaDefinition: TypeAlias = Dict[str, Any]
"""
Schema definition for data validation.
Keys: required_fields, field_types, constraints, etc.
"""

# ============================================================================
# Export Types
# ============================================================================

ExportConfig: TypeAlias = Dict[str, Any]
"""
Export configuration from export/config/*.yaml.
Keys: domain, output_path, generators, enrichers, etc.
"""

DatasetMetadata: TypeAlias = Dict[str, Any]
"""
Metadata for dataset generation.
Keys: dataset_type, field_list, schema_version, etc.
"""

# ============================================================================
# API Types
# ============================================================================

APIResponse: TypeAlias = Dict[str, Any]
"""
Response from API calls (Grok, Winston, etc.).
Keys: content, success, error, metadata, etc.
"""

QualityScores: TypeAlias = Dict[str, Union[float, int, str]]
"""
Quality evaluation scores.
Keys: winston_score, realism_score, readability_status, etc.
"""

# ============================================================================
# Learning Types
# ============================================================================

LearningData: TypeAlias = Dict[str, Any]
"""
Data for learning system.
Keys: parameters, scores, patterns, attempt_data, etc.
"""

# ============================================================================
# Literal Types for Constants
# ============================================================================

DomainType: TypeAlias = Literal['materials', 'contaminants', 'compounds', 'settings']
"""Valid domain types in the system for compile-time validation."""

ComponentType: TypeAlias = Literal['description', 'micro', 'faq', 'excerpt', 'caption']
"""Valid text component types that can be generated."""

GenerationStatus: TypeAlias = Literal['success', 'failure', 'partial', 'skipped']
"""Status of generation operation."""

ValidationLevel: TypeAlias = Literal['strict', 'standard', 'permissive']
"""Level of validation enforcement."""

ExportFormat: TypeAlias = Literal['yaml', 'json', 'markdown', 'html']
"""Supported export formats."""

ParameterSet: TypeAlias = Dict[str, Union[float, int, str]]
"""
API parameter set for generation.
Keys: temperature, frequency_penalty, presence_penalty, etc.
"""
