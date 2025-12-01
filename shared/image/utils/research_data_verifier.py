#!/usr/bin/env python3
"""
Research Data Verifier

Verifies that all researched data (contamination patterns, material properties,
visual characteristics) actually appears in the final optimized prompt.

This prevents silent data loss during prompt optimization.

Author: AI Assistant  
Date: November 30, 2025
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Result of research data verification."""
    is_valid: bool = True
    missing_data: List[str] = field(default_factory=list)
    present_data: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    data_retention_score: float = 100.0  # Percentage of data that made it through
    
    def add_missing(self, description: str, severity: str = "HIGH"):
        """Add missing data item."""
        self.missing_data.append(f"[{severity}] {description}")
        if severity in ("HIGH", "CRITICAL"):
            self.is_valid = False
    
    def add_present(self, description: str):
        """Add verified present data item."""
        self.present_data.append(description)
    
    def add_warning(self, description: str):
        """Add warning (not critical)."""
        self.warnings.append(description)
    
    def calculate_retention(self, total_expected: int):
        """Calculate data retention percentage."""
        if total_expected == 0:
            self.data_retention_score = 100.0
        else:
            self.data_retention_score = (len(self.present_data) / total_expected) * 100
    
    def get_summary(self) -> str:
        """Get human-readable summary."""
        status = "✅ PASSED" if self.is_valid else "❌ FAILED"
        return (
            f"{status}: {len(self.present_data)} items verified, "
            f"{len(self.missing_data)} missing, {len(self.warnings)} warnings "
            f"({self.data_retention_score:.1f}% retention)"
        )
    
    def format_report(self) -> str:
        """Format detailed report."""
        lines = [
            "=" * 80,
            "🔍 RESEARCH DATA VERIFICATION REPORT",
            "=" * 80,
            "",
            f"Status: {self.get_summary()}",
            ""
        ]
        
        if self.missing_data:
            lines.append("❌ MISSING DATA:")
            for item in self.missing_data:
                lines.append(f"   • {item}")
            lines.append("")
        
        if self.warnings:
            lines.append("⚠️  WARNINGS:")
            for item in self.warnings:
                lines.append(f"   • {item}")
            lines.append("")
        
        if self.present_data:
            lines.append(f"✅ VERIFIED PRESENT ({len(self.present_data)} items):")
            for item in self.present_data[:10]:  # Show first 10
                lines.append(f"   • {item}")
            if len(self.present_data) > 10:
                lines.append(f"   ... and {len(self.present_data) - 10} more")
        
        lines.append("")
        lines.append("=" * 80)
        return "\n".join(lines)


class ResearchDataVerifier:
    """
    Verifies research data presence in final prompts.
    
    Checks that:
    1. Material name appears in prompt
    2. Contamination pattern names appear
    3. Visual characteristics (colors, textures) appear
    4. Key physics/distribution data appears
    5. Material-specific feedback (if any) appears
    
    Usage:
        verifier = ResearchDataVerifier()
        result = verifier.verify(
            prompt=optimized_prompt,
            research_data=research_data,
            material_name="Aluminum"
        )
        if not result.is_valid:
            logger.error(result.format_report())
    """
    
    # Minimum expected data items for valid verification
    MIN_PATTERN_MENTIONS = 1
    MIN_VISUAL_DETAILS = 2
    
    def verify(
        self,
        prompt: str,
        research_data: Dict[str, Any],
        material_name: str,
        material_properties: Optional[Dict[str, Any]] = None
    ) -> VerificationResult:
        """
        Verify that research data appears in the prompt.
        
        Args:
            prompt: Final optimized prompt
            research_data: Research data dict with patterns, settings, etc.
            material_name: Material name
            material_properties: Optional material properties from Materials.yaml
            
        Returns:
            VerificationResult with detailed findings
        """
        result = VerificationResult()
        prompt_lower = prompt.lower()
        total_expected = 0
        
        # 1. Verify material name
        total_expected += 1
        if material_name.lower() in prompt_lower:
            result.add_present(f"Material name: {material_name}")
        else:
            result.add_missing(f"Material name '{material_name}' not found in prompt", "CRITICAL")
        
        # 2. Verify contamination patterns
        patterns = research_data.get('selected_patterns', research_data.get('contaminants', []))
        for pattern in patterns:
            pattern_name = pattern.get('pattern_name', pattern.get('name', ''))
            if pattern_name:
                total_expected += 1
                # Check for pattern name or key identifying words
                pattern_words = pattern_name.lower().replace('-', ' ').replace('_', ' ').split()
                found = any(word in prompt_lower for word in pattern_words if len(word) > 3)
                
                if found:
                    result.add_present(f"Pattern: {pattern_name}")
                else:
                    result.add_missing(f"Pattern '{pattern_name}' keywords not found in prompt", "HIGH")
        
        # 3. Verify visual characteristics
        visual_items_found = 0
        for pattern in patterns:
            visual = pattern.get('visual_characteristics', {})
            
            # Check colors
            colors = visual.get('color_variations', visual.get('color_range', ''))
            if colors:
                total_expected += 1
                colors_str = str(colors).lower()
                # Extract color words
                color_words = re.findall(r'\b(red|orange|brown|black|white|gray|grey|green|blue|yellow|rust|patina|silver|gold|dark|light)\b', colors_str)
                found_colors = [c for c in color_words if c in prompt_lower]
                if found_colors:
                    result.add_present(f"Colors: {', '.join(found_colors[:3])}")
                    visual_items_found += 1
                else:
                    result.add_warning(f"Color data from research not found: {colors_str[:50]}...")
            
            # Check textures
            texture = visual.get('texture_details', visual.get('texture_detail', ''))
            if texture:
                total_expected += 1
                texture_str = str(texture).lower()
                texture_words = re.findall(r'\b(rough|smooth|flaky|powdery|granular|porous|glossy|matte|pitted|scaly)\b', texture_str)
                found_textures = [t for t in texture_words if t in prompt_lower]
                if found_textures:
                    result.add_present(f"Textures: {', '.join(found_textures[:3])}")
                    visual_items_found += 1
                else:
                    result.add_warning(f"Texture data from research not found: {texture_str[:50]}...")
            
            # Check distribution
            distribution = visual.get('distribution_patterns', '')
            if distribution:
                total_expected += 1
                dist_str = str(distribution).lower()
                dist_words = re.findall(r'\b(edges|center|corners|uniform|patchy|random|clustered|streaky)\b', dist_str)
                found_dist = [d for d in dist_words if d in prompt_lower]
                if found_dist:
                    result.add_present(f"Distribution: {', '.join(found_dist[:3])}")
                    visual_items_found += 1
        
        # Check minimum visual details
        if visual_items_found < self.MIN_VISUAL_DETAILS and patterns:
            result.add_warning(f"Only {visual_items_found} visual details found (expected at least {self.MIN_VISUAL_DETAILS})")
        
        # 4. Verify context/background
        context_bg = research_data.get('context_background', '')
        if context_bg:
            total_expected += 1
            bg_words = context_bg.lower().split()
            found_bg = any(word in prompt_lower for word in bg_words if len(word) > 4)
            if found_bg:
                result.add_present(f"Context background: {context_bg}")
            else:
                result.add_warning(f"Context background '{context_bg}' not found")
        
        # 5. Verify common object/shape
        common_object = research_data.get('common_object', research_data.get('common_shape', ''))
        if common_object:
            total_expected += 1
            obj_words = common_object.lower().split()
            found_obj = any(word in prompt_lower for word in obj_words if len(word) > 3)
            if found_obj:
                result.add_present(f"Object/shape: {common_object}")
            else:
                result.add_missing(f"Object/shape '{common_object}' not found in prompt", "MEDIUM")
        
        # 6. Verify material properties (if provided)
        if material_properties:
            # Check for visual properties
            if material_properties.get('color'):
                total_expected += 1
                if material_properties['color'].lower() in prompt_lower:
                    result.add_present(f"Material color: {material_properties['color']}")
                else:
                    result.add_warning(f"Material color '{material_properties['color']}' not found")
            
            if material_properties.get('reflectivity'):
                refl = str(material_properties['reflectivity']).lower()
                if any(word in prompt_lower for word in ['reflective', 'shiny', 'matte', 'dull', refl]):
                    result.add_present("Reflectivity indicator present")
        
        # 7. Verify image generation feedback
        for pattern in patterns:
            feedback = pattern.get('image_generation_feedback', '')
            if feedback:
                total_expected += 1
                # Feedback should appear in CRITICAL section
                if 'critical' in prompt_lower and any(word in prompt_lower for word in feedback.lower().split()[:5]):
                    result.add_present(f"Image gen feedback for {pattern.get('pattern_name', 'pattern')}")
        
        # Calculate retention score
        result.calculate_retention(total_expected)
        
        # Log result
        if result.is_valid:
            logger.info(f"✅ Research data verification: {result.get_summary()}")
        else:
            logger.warning(f"⚠️  Research data verification: {result.get_summary()}")
        
        return result
    
    def verify_post_optimization(
        self,
        original_prompt: str,
        optimized_prompt: str,
        research_data: Dict[str, Any],
        enforce_threshold: bool = True,
        minimum_retention: float = 60.0
    ) -> VerificationResult:
        """
        Compare original and optimized prompts to detect data loss.
        
        Args:
            original_prompt: Pre-optimization prompt
            optimized_prompt: Post-optimization prompt
            research_data: Research data for context
            enforce_threshold: If True, raise error when retention < minimum_retention
            minimum_retention: Minimum data retention percentage (default: 70%)
            
        Returns:
            VerificationResult highlighting what was lost
            
        Raises:
            ValueError: If enforce_threshold=True and retention < minimum_retention
        """
        result = VerificationResult()
        
        # Extract key data markers from original
        patterns = research_data.get('selected_patterns', [])
        pattern_names = [p.get('pattern_name', '') for p in patterns if p.get('pattern_name')]
        
        orig_lower = original_prompt.lower()
        opt_lower = optimized_prompt.lower()
        
        # Check what was lost
        for pattern_name in pattern_names:
            words = pattern_name.lower().replace('-', ' ').split()
            key_words = [w for w in words if len(w) > 3]
            
            in_original = any(w in orig_lower for w in key_words)
            in_optimized = any(w in opt_lower for w in key_words)
            
            if in_original and not in_optimized:
                result.add_missing(f"Pattern '{pattern_name}' lost during optimization", "HIGH")
            elif in_optimized:
                result.add_present(f"Pattern '{pattern_name}' retained")
        
        # Check for CONTAMINATION SPECIFICS section
        if 'contamination specifics' in orig_lower:
            if 'contamination specifics' in opt_lower:
                result.add_present("CONTAMINATION SPECIFICS section retained")
            else:
                result.add_missing("CONTAMINATION SPECIFICS section lost during optimization", "CRITICAL")
        
        # Check length reduction
        reduction = len(original_prompt) - len(optimized_prompt)
        reduction_pct = (reduction / len(original_prompt) * 100) if original_prompt else 0
        
        if reduction_pct > 50:
            result.add_warning(f"Significant reduction: {reduction_pct:.1f}% ({reduction} chars) - verify critical data retained")
        
        result.calculate_retention(len(result.present_data) + len(result.missing_data))
        
        # ENFORCE threshold - fail-fast if too much data lost
        if enforce_threshold and result.data_retention_score < minimum_retention:
            logger.error(
                f"❌ DATA RETENTION BELOW THRESHOLD: {result.data_retention_score:.1f}% < {minimum_retention}%"
            )
            logger.error(f"Missing data: {len(result.missing_data)} items")
            for item in result.missing_data[:5]:
                logger.error(f"   • {item}")
            
            raise ValueError(
                f"Prompt optimization lost too much research data: "
                f"{result.data_retention_score:.1f}% retention (minimum: {minimum_retention}%). "
                f"Missing {len(result.missing_data)} critical data items. "
                f"Optimization cannot proceed - research data must appear in final prompt."
            )
        
        return result


def verify_research_data(
    prompt: str,
    research_data: Dict[str, Any],
    material_name: str,
    material_properties: Optional[Dict[str, Any]] = None
) -> VerificationResult:
    """
    Convenience function to verify research data in prompt.
    
    Args:
        prompt: Final prompt to verify
        research_data: Research data dict
        material_name: Material name
        material_properties: Optional material properties
        
    Returns:
        VerificationResult
    """
    verifier = ResearchDataVerifier()
    return verifier.verify(prompt, research_data, material_name, material_properties)


def verify_optimization(
    original_prompt: str,
    optimized_prompt: str,
    research_data: Dict[str, Any],
    enforce_threshold: bool = True,
    minimum_retention: float = 60.0
) -> VerificationResult:
    """
    Convenience function to verify data retention after optimization.
    
    Args:
        original_prompt: Pre-optimization prompt
        optimized_prompt: Post-optimization prompt
        research_data: Research data for context
        enforce_threshold: If True, raise error when retention < minimum_retention
        minimum_retention: Minimum data retention percentage (default: 70%)
        
    Returns:
        VerificationResult
        
    Raises:
        ValueError: If enforce_threshold=True and retention < minimum_retention
    """
    verifier = ResearchDataVerifier()
    return verifier.verify_post_optimization(
        original_prompt, optimized_prompt, research_data,
        enforce_threshold=enforce_threshold,
        minimum_retention=minimum_retention
    )
