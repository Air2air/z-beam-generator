"""
Feedback Rewriter - Translates user feedback into Imagen 4-effective language.

Imagen 4 struggles with abstract concepts like "contamination" but responds well to:
- Concrete visual references (old deck boards, barn wood, rusty metal)
- Color shift descriptions (blonde → gray/brown)
- Physical location terms (INTO the grain, soaked, embedded)
- Reference objects people recognize visually
"""

from typing import Dict, List, Tuple
import re


class FeedbackRewriter:
    """Rewrites user feedback into more effective Imagen 4 instructions."""
    
    # Abstract terms → Concrete visual translations
    TRANSLATIONS: Dict[str, Dict[str, str]] = {
        # Contamination terms
        "contamination": {
            "wood": "weathered gray patina and water stain discoloration",
            "metal": "rust streaks, oxidation patches, and grime buildup",
            "stone": "dark staining, mineral deposits, and weathering marks",
            "glass": "hazy film, water spots, and grimy residue",
            "plastic": "yellowed discoloration and surface grime",
            "default": "visible dirt, staining, and surface degradation"
        },
        "contaminants": {
            "wood": "gray weathering, water stains, and dark discoloration",
            "metal": "rust, oxidation, and oily residue",
            "default": "dirt, grime, and visible staining"
        },
        "dirty": {
            "wood": "gray-brown weathered like old deck boards left outside",
            "metal": "grimy with rust streaks like old tools",
            "default": "visibly soiled with dark staining"
        },
        "contaminated": {
            "wood": "weathered gray-brown like barn wood or old fencing",
            "metal": "corroded and grimy like neglected equipment",
            "default": "heavily stained and discolored"
        },
        
        # Texture/depth terms
        "ingrained": {
            "wood": "soaked deep INTO the wood grain - not sitting on top",
            "metal": "embedded in the surface texture",
            "default": "penetrated into the material"
        },
        "embedded": {
            "wood": "absorbed into the wood fibers",
            "metal": "worked into surface pits and scratches",
            "default": "deep within the surface texture"
        },
        "surface level": {
            "default": "sitting ON TOP of the material, not absorbed"
        },
        
        # Coverage terms
        "evenly spread": {
            "default": "distributed across the entire surface with consistent coverage"
        },
        "patchy": {
            "default": "in irregular blotches and spots across the surface"
        },
        "heavy": {
            "wood": "thick dark weathering covering most of the surface",
            "metal": "heavy rust and grime obscuring the original surface",
            "default": "thick buildup obscuring much of the original surface"
        },
        "light": {
            "wood": "subtle gray tint like wood starting to weather",
            "metal": "light surface oxidation and minor discoloration",
            "default": "thin film of surface discoloration"
        },
        
        # Appearance terms
        "aged": {
            "wood": "gray-silver weathered like driftwood or old barn siding",
            "metal": "patina and oxidation like antique hardware",
            "default": "showing years of wear and exposure"
        },
        "weathered": {
            "wood": "silver-gray like wood left outdoors for years",
            "metal": "oxidized and worn like outdoor fixtures",
            "default": "showing environmental exposure damage"
        },
        "old": {
            "wood": "gray and worn like reclaimed lumber",
            "metal": "tarnished and corroded like vintage equipment",
            "default": "showing significant age and wear"
        },
        
        # Position/contrast terms
        "more contrast": {
            "default": "DRAMATIC difference - left side MUCH darker/dirtier than right"
        },
        "visible difference": {
            "default": "obvious before/after - left DIRTY, right CLEAN with clear distinction"
        },
        "same on both sides": {
            "default": "PROBLEM: left and right look identical - need LEFT much dirtier than RIGHT"
        },
        "identical": {
            "default": "PROBLEM: both sides match - LEFT must be heavily stained, RIGHT must be clean"
        },
        
        # Rotation terms
        "rotation": {
            "default": "horizontal rotation 10-20 degrees showing a DIFFERENT FACE of the object"
        },
        "not rotated": {
            "default": "PROBLEM: same viewing angle on both sides - RIGHT side needs 10-20° horizontal rotation"
        },
        "same angle": {
            "default": "PROBLEM: identical perspective - rotate RIGHT side horizontally to show different face"
        }
    }
    
    # Reference objects by category for concrete examples
    REFERENCE_OBJECTS: Dict[str, List[str]] = {
        "wood": [
            "old deck boards left outside for years",
            "weathered barn wood",
            "driftwood",
            "reclaimed lumber",
            "old fence posts"
        ],
        "metal": [
            "old rusty tools",
            "weathered outdoor furniture",
            "antique hardware",
            "neglected machinery",
            "old car parts"
        ],
        "stone": [
            "old gravestones",
            "weathered statues",
            "ancient building stones",
            "river rocks with mineral deposits"
        ],
        "glass": [
            "old windows with hard water stains",
            "greenhouse glass",
            "car windshield with road grime"
        ]
    }
    
    # Color shifts by category
    COLOR_SHIFTS: Dict[str, str] = {
        "wood": "natural blonde/tan → gray/brown/silver",
        "metal": "shiny metallic → dull with rust-orange and dark spots",
        "stone": "original color → darkened with mineral staining",
        "glass": "clear/transparent → hazy/cloudy/spotted"
    }
    
    def __init__(self):
        pass
    
    def rewrite(self, feedback: str, category: str = "default") -> Tuple[str, List[str]]:
        """
        Rewrite feedback into more effective Imagen 4 language.
        
        Args:
            feedback: Original user feedback
            category: Material category (wood, metal, stone, etc.)
            
        Returns:
            Tuple of (rewritten_feedback, list of changes made)
        """
        category = category.lower() if category else "default"
        rewritten = feedback
        changes_made = []
        applied_terms = set()  # Track what we've already replaced
        
        # Apply translations (sorted by length descending to match longer phrases first)
        sorted_terms = sorted(self.TRANSLATIONS.keys(), key=len, reverse=True)
        
        for term in sorted_terms:
            translations = self.TRANSLATIONS[term]
            # Skip if this term is part of a replacement we already made
            if any(term.lower() in applied.lower() for applied in applied_terms):
                continue
                
            pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
            if pattern.search(rewritten):
                # Get category-specific or default translation
                replacement = translations.get(category, translations.get("default", term))
                if replacement != term:
                    rewritten = pattern.sub(replacement, rewritten)
                    changes_made.append(f"'{term}' → '{replacement}'")
                    applied_terms.add(replacement)  # Track what we added
        
        # Add reference objects if talking about appearance
        appearance_words = ["look", "appear", "like", "show", "dirty", "weathered", "aged"]
        if any(word in feedback.lower() for word in appearance_words):
            refs = self.REFERENCE_OBJECTS.get(category, [])
            if refs and not any(ref in rewritten.lower() for ref in refs):
                # Add a reference example
                ref_example = refs[0]  # Use first reference
                if f"like {ref_example}" not in rewritten.lower():
                    rewritten += f" - think visually: like {ref_example}"
                    changes_made.append(f"Added reference: '{ref_example}'")
        
        # Add color shift context if discussing contamination/appearance
        color_words = ["color", "contamination", "dirty", "weathered", "discoloration", "stain"]
        if any(word in feedback.lower() for word in color_words):
            color_shift = self.COLOR_SHIFTS.get(category)
            if color_shift and color_shift not in rewritten:
                rewritten += f" (color shift: {color_shift})"
                changes_made.append(f"Added color shift: '{color_shift}'")
        
        return rewritten, changes_made
    
    def format_rewrite_report(self, original: str, rewritten: str, 
                               changes: List[str], category: str) -> str:
        """Format a report showing original vs rewritten feedback."""
        report = []
        report.append("=" * 70)
        report.append("📝 FEEDBACK REWRITTEN FOR IMAGEN 4 EFFECTIVENESS")
        report.append("=" * 70)
        report.append("")
        report.append(f"📦 Category: {category}")
        report.append("")
        report.append("❌ ORIGINAL (abstract terms Imagen struggles with):")
        report.append(f"   {original}")
        report.append("")
        report.append("✅ REWRITTEN (concrete visual language):")
        report.append(f"   {rewritten}")
        report.append("")
        if changes:
            report.append("🔄 TRANSLATIONS APPLIED:")
            for change in changes:
                report.append(f"   • {change}")
        report.append("")
        report.append("=" * 70)
        return "\n".join(report)


# Convenience function for quick rewrites
def rewrite_feedback(feedback: str, category: str = "default") -> Tuple[str, str]:
    """
    Quick function to rewrite feedback.
    
    Returns:
        Tuple of (rewritten_feedback, formatted_report)
    """
    rewriter = FeedbackRewriter()
    rewritten, changes = rewriter.rewrite(feedback, category)
    report = rewriter.format_rewrite_report(feedback, rewritten, changes, category)
    return rewritten, report


if __name__ == "__main__":
    # Demo the rewriter
    test_cases = [
        ("contamination should be evenly spread and ingrained into surface", "wood"),
        ("the contamination is not visible enough", "metal"),
        ("both sides look identical, need more contrast", "wood"),
        ("rotation not visible between left and right", "default"),
        ("surface looks too clean, needs to be more dirty and aged", "wood"),
    ]
    
    rewriter = FeedbackRewriter()
    
    for feedback, category in test_cases:
        rewritten, changes = rewriter.rewrite(feedback, category)
        report = rewriter.format_rewrite_report(feedback, rewritten, changes, category)
        print(report)
        print()
