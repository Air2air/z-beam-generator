#!/usr/bin/env python3
"""
Demonstration of Image Prompt Payload Validator

Shows how the validator detects different types of issues:
- Contradictions in color, texture, state
- Impossible material-contaminant combinations
- Physics violations (gravity, floating)
- Length issues
- Quality anti-patterns
- Ambiguous language
- Duplications

Author: AI Assistant
Date: November 26, 2025
"""

from shared.image.validation.payload_validator import (
    ImagePromptPayloadValidator,
    validate_prompt
)


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def demo_valid_prompt():
    """Demonstrate a valid prompt that passes all checks"""
    print_section("VALID PROMPT - Should Pass")
    
    prompt = """
High-resolution photo of steel industrial component with oil contamination.

VISUAL DETAILS:
- Surface: Brushed steel finish, metallic gray
- Contamination: Dark brown oil patches with rainbow iridescence
- Pattern: Drip marks flowing downward from top
- Texture: Fresh deposits glossy, aged deposits matte
- Scale: Moderate contamination (0.5-1mm thickness)

LIGHTING:
- Direct sunlight showing rainbow sheen on fresh oil
- Natural lighting emphasizing texture differences

TECHNICAL:
- High resolution, industrial photography style
- Accurate color representation
- Scientific documentation quality
"""
    
    validator = ImagePromptPayloadValidator()
    result = validator.validate(prompt, material="Steel", contaminant="oil-grease")
    
    print("PROMPT:")
    print(prompt)
    print("\n" + result.format_report())


def demo_color_contradiction():
    """Demonstrate color contradiction detection"""
    print_section("COLOR CONTRADICTION - Should Fail")
    
    prompt = "Show dark black surface with bright white highlights and light coloring"
    
    validator = ImagePromptPayloadValidator()
    result = validator.validate(prompt)
    
    print("PROMPT:")
    print(prompt)
    print("\n" + result.format_report())


def demo_texture_contradiction():
    """Demonstrate texture contradiction detection"""
    print_section("TEXTURE CONTRADICTION - Should Fail")
    
    prompt = "Surface is smooth and glossy with polished finish, featuring rough matte texture"
    
    validator = ImagePromptPayloadValidator()
    result = validator.validate(prompt)
    
    print("PROMPT:")
    print(prompt)
    print("\n" + result.format_report())


def demo_impossible_contamination():
    """Demonstrate impossible contamination detection"""
    print_section("IMPOSSIBLE CONTAMINATION - Should Fail")
    
    prompt = "Aluminum surface with rust contamination showing iron oxide oxidation"
    
    validator = ImagePromptPayloadValidator()
    result = validator.validate(prompt, material="Aluminum", contaminant="rust-oxidation")
    
    print("PROMPT:")
    print(prompt)
    print("\n" + result.format_report())


def demo_physics_violation():
    """Demonstrate physics violation detection"""
    print_section("PHYSICS VIOLATION - Should Fail")
    
    prompt = "Oil contamination flowing upward from bottom to top, floating above surface"
    
    validator = ImagePromptPayloadValidator()
    result = validator.validate(prompt)
    
    print("PROMPT:")
    print(prompt)
    print("\n" + result.format_report())


def demo_forbidden_dirt():
    """Demonstrate dirt/soil contamination detection"""
    print_section("FORBIDDEN DIRT CONTAMINATION - Should Fail")
    
    prompt = "Metal component with dirt and soil contamination showing muddy deposits"
    
    validator = ImagePromptPayloadValidator()
    result = validator.validate(prompt)
    
    print("PROMPT:")
    print(prompt)
    print("\n" + result.format_report())


def demo_ambiguous_language():
    """Demonstrate ambiguous language detection"""
    print_section("AMBIGUOUS LANGUAGE - Should Warn")
    
    prompt = "Maybe show some kind of contamination that might be somewhat present"
    
    validator = ImagePromptPayloadValidator()
    result = validator.validate(prompt)
    
    print("PROMPT:")
    print(prompt)
    print("\n" + result.format_report())


def demo_quality_antipatterns():
    """Demonstrate quality anti-pattern detection"""
    print_section("QUALITY ANTI-PATTERNS - Should Warn")
    
    prompt = "Very dark surface with really heavy contamination, extremely dirty!!!"
    
    validator = ImagePromptPayloadValidator()
    result = validator.validate(prompt)
    
    print("PROMPT:")
    print(prompt)
    print("\n" + result.format_report())


def demo_length_violation():
    """Demonstrate length limit violation"""
    print_section("LENGTH VIOLATION - Should Fail")
    
    # Create prompt that exceeds 4096 character limit
    prompt = "A" * 5000
    
    validator = ImagePromptPayloadValidator()
    result = validator.validate(prompt)
    
    print(f"PROMPT: (Truncated - {len(prompt)} characters)")
    print(f"{prompt[:200]}...")
    print("\n" + result.format_report())


def demo_duplication():
    """Demonstrate duplication detection"""
    print_section("DUPLICATION - Should Warn")
    
    prompt = (
        "Show the surface. Show the surface. Show the surface. "
        "The contamination pattern is visible. "
        "The surface shows heavy contamination with dark patches. "
        "The surface shows heavy contamination with dark patches."
    )
    
    validator = ImagePromptPayloadValidator()
    result = validator.validate(prompt)
    
    print("PROMPT:")
    print(prompt)
    print("\n" + result.format_report())


def demo_multiple_issues():
    """Demonstrate prompt with multiple issues"""
    print_section("MULTIPLE ISSUES - Should Fail with Multiple Errors")
    
    prompt = """
Very bright aluminum with dark rust contamination floating upward!!!
Maybe show some kind of dirt or soil possibly present.
The surface is smooth and glossy with rough matte texture.
The contamination is fresh and new but heavily aged and weathered.
Show the surface. Show the surface. Show the surface.
""" * 30  # Repeat to exceed length limit
    
    validator = ImagePromptPayloadValidator()
    result = validator.validate(prompt, material="Aluminum", contaminant="rust")
    
    print(f"PROMPT: (Truncated - {len(prompt)} characters)")
    print(f"{prompt[:300]}...")
    print("\n" + result.format_report())


def main():
    """Run all demonstrations"""
    print("\n" + "="*80)
    print("  IMAGE PROMPT PAYLOAD VALIDATOR DEMONSTRATION")
    print("="*80)
    
    demos = [
        ("Valid Prompt", demo_valid_prompt),
        ("Color Contradiction", demo_color_contradiction),
        ("Texture Contradiction", demo_texture_contradiction),
        ("Impossible Contamination", demo_impossible_contamination),
        ("Physics Violation", demo_physics_violation),
        ("Forbidden Dirt", demo_forbidden_dirt),
        ("Ambiguous Language", demo_ambiguous_language),
        ("Quality Anti-patterns", demo_quality_antipatterns),
        ("Length Violation", demo_length_violation),
        ("Duplication", demo_duplication),
        ("Multiple Issues", demo_multiple_issues),
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {e}")
    
    print("\n" + "="*80)
    print("  DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nUse ImagePromptPayloadValidator.validate() to check prompts before")
    print("submitting to Imagen API. The validator will catch issues early and")
    print("prevent bad prompts from wasting API credits.")


if __name__ == '__main__':
    main()
