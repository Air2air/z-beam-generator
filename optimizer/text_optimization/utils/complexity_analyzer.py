#!/usr/bin/env python3
"""
AI Detection Configuration Complexity Analyzer
Analyzes the current ai_detection.yaml file and suggests modular breakdown.
"""

import json
from collections import defaultdict
from pathlib import Path

import yaml


def analyze_complexity(file_path: str) -> dict:
    """Analyze the complexity of the AI detection configuration file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse YAML
    config = yaml.safe_load(content)

    # Basic metrics
    lines = content.split("\n")
    total_lines = len(lines)

    # Structural analysis
    structure = {
        "total_lines": total_lines,
        "top_level_keys": len(config.keys()),
        "max_nesting_depth": 0,
        "sections": {},
        "complexity_score": 0,
    }

    def analyze_section(section, path="", depth=0):
        """Recursively analyze a configuration section."""
        if depth > structure["max_nesting_depth"]:
            structure["max_nesting_depth"] = depth

        section_name = path.split(".")[-1] if path else "root"
        section_info = {
            "depth": depth,
            "type": type(section).__name__,
            "size": 0,
            "subsections": {},
        }

        if isinstance(section, dict):
            section_info["size"] = len(section)
            for key, value in section.items():
                subsection_path = f"{path}.{key}" if path else key
                section_info["subsections"][key] = analyze_section(
                    value, subsection_path, depth + 1
                )
        elif isinstance(section, list):
            section_info["size"] = len(section)
        else:
            section_info["size"] = len(str(section))

        structure["sections"][section_name] = section_info
        return section_info

    # Analyze the entire config
    analyze_section(config)

    # Calculate complexity score
    structure["complexity_score"] = (
        total_lines * 0.3
        + structure["max_nesting_depth"] * 10
        + structure["top_level_keys"] * 5
    )

    return structure


def suggest_modular_breakdown(analysis: dict) -> dict:
    """Suggest how to break down the monolithic file into modules."""
    suggestions = {
        "recommended_modules": {},
        "migration_priority": [],
        "estimated_complexity_reduction": 0,
    }

    # Analyze sections for modular breakdown
    sections = analysis["sections"]

    # Group related sections
    module_groups = {
        "human_characteristics": [
            "conversational_elements",
            "cognitive_variability",
            "natural_imperfections",
        ],
        "detection_avoidance": ["algorithmic_patterns", "detection_triggers"],
        "authenticity_enhancements": [
            "personal_touch",
            "conversational_flow",
            "paragraph_rhythm_breakers",
        ],
        "structural_improvements": [
            "paragraph_structure_variability",
            "sentence_level_improvements",
            "uniform_pattern_breakers",
        ],
        "cultural_adaptation": ["cultural_humanization", "nationality_adaptation"],
        "core_configuration": [
            "ai_detection_focus",
            "success_metrics",
            "iteration_refinement_mechanism",
        ],
    }

    # Calculate module sizes and complexity
    for module_name, section_names in module_groups.items():
        module_size = 0
        module_sections = []

        for section_name in section_names:
            if section_name in sections:
                section = sections[section_name]
                module_size += section["size"]
                module_sections.append(
                    {
                        "name": section_name,
                        "size": section["size"],
                        "depth": section["depth"],
                    }
                )

        if module_sections:
            suggestions["recommended_modules"][module_name] = {
                "sections": module_sections,
                "total_size": module_size,
                "estimated_lines": module_size * 3,  # Rough estimate
                "complexity_score": sum(
                    s["size"] * s["depth"] for s in module_sections
                ),
            }

    # Sort by complexity for migration priority
    suggestions["migration_priority"] = sorted(
        suggestions["recommended_modules"].keys(),
        key=lambda x: suggestions["recommended_modules"][x]["complexity_score"],
        reverse=True,
    )

    # Estimate complexity reduction
    original_complexity = analysis["complexity_score"]
    modular_complexity = sum(
        module["complexity_score"] * 0.3  # 70% reduction per module
        for module in suggestions["recommended_modules"].values()
    )
    suggestions["estimated_complexity_reduction"] = (
        original_complexity - modular_complexity
    )

    return suggestions


def generate_migration_plan(suggestions: dict) -> str:
    """Generate a detailed migration plan."""
    plan = ["# AI Detection Configuration Migration Plan", ""]

    plan.append("## Current Complexity Analysis")
    plan.append("- Monolithic file with high complexity")
    plan.append("- Deep nesting and interdependencies")
    plan.append("- Difficult to maintain and test")
    plan.append("")

    plan.append("## Recommended Modular Structure")
    for module_name, module_info in suggestions["recommended_modules"].items():
        plan.append(f"### {module_name.replace('_', ' ').title()}")
        plan.append(f"- **Estimated size**: {module_info['estimated_lines']} lines")
        plan.append(f"- **Complexity score**: {module_info['complexity_score']:.1f}")
        plan.append("- **Sections**:")
        for section in module_info["sections"]:
            plan.append(f"  - {section['name']} ({section['size']} items)")
        plan.append("")

    plan.append("## Migration Priority")
    for i, module in enumerate(suggestions["migration_priority"], 1):
        plan.append(f"{i}. {module.replace('_', ' ').title()}")
    plan.append("")

    plan.append("## Benefits of Modular Structure")
    plan.append("- **Maintainability**: Easier to modify individual components")
    plan.append("- **Testability**: Isolated testing of specific features")
    plan.append("- **Reusability**: Components can be reused across different contexts")
    plan.append("- **Performance**: Faster loading of only required components")
    plan.append(
        "- **Collaboration**: Multiple developers can work on different modules"
    )
    plan.append("")

    plan.append(f"## Expected Complexity Reduction")
    plan.append(
        f"- **Current complexity**: {suggestions.get('current_complexity', 'Unknown')}"
    )
    plan.append(
        f"- **Estimated reduction**: {suggestions['estimated_complexity_reduction']:.1f} points"
    )
    plan.append("")

    return "\n".join(plan)


def main():
    """Main analysis function."""
    config_file = "components/text/prompts/ai_detection.yaml"

    if not Path(config_file).exists():
        print(f"❌ Configuration file not found: {config_file}")
        return

    print("🔍 Analyzing AI detection configuration complexity...")

    # Analyze current structure
    analysis = analyze_complexity(config_file)

    print("📊 Current Structure:")
    print(f"   - Total lines: {analysis['total_lines']}")
    print(f"   - Top-level sections: {analysis['top_level_keys']}")
    print(f"   - Maximum nesting depth: {analysis['max_nesting_depth']}")
    print(".1f")
    print()

    # Generate suggestions
    suggestions = suggest_modular_breakdown(analysis)
    suggestions["current_complexity"] = analysis["complexity_score"]

    # Generate migration plan
    migration_plan = generate_migration_plan(suggestions)

    # Save migration plan
    plan_file = "components/text/prompts/MIGRATION_PLAN.md"
    with open(plan_file, "w", encoding="utf-8") as f:
        f.write(migration_plan)

    print(f"✅ Migration plan saved to: {plan_file}")
    print()
    print("🎯 Key Recommendations:")
    print("1. Break down monolithic file into focused modules")
    print("2. Implement modular loading system")
    print("3. Add comprehensive testing for each module")
    print("4. Establish clear governance rules")
    print(".1f")


if __name__ == "__main__":
    main()
