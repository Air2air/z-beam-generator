import random
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class OrderRandomizer:
    """Randomizes section ordering while maintaining logical flow."""
    
    @staticmethod
    def randomize_sections(sections: List[Dict[str, Any]], keep_overview_first: bool = False) -> List[Dict[str, Any]]:
        """
        Randomize the order of sections with intelligent constraints.
        
        Args:
            sections: List of section dictionaries
            keep_overview_first: Whether to always keep overview as the first section
            
        Returns:
            Randomized list of sections
        """
        if not sections:
            return []
            
        # Make a copy to avoid modifying the original
        sections_copy = sections.copy()
        
        # Apply different randomization strategies with varying probabilities
        strategy = random.choice([
            "full_random",          # Complete randomization (40%)
            "grouped_random",       # Group by type then randomize (30%)
            "priority_jitter",      # Add random jitter to priorities (30%)
        ])
        
        logger.debug(f"Using randomization strategy: {strategy}")
        
        if strategy == "full_random":
            # Full randomization - completely shuffle
            random.shuffle(sections_copy)
            
        elif strategy == "grouped_random":
            # Group sections by type then randomize within groups
            info_sections = []  # Overview, introduction type sections
            technical_sections = []  # Specifications, technical details
            application_sections = []  # Uses, applications
            other_sections = []  # Everything else
            
            # Categorize sections
            for section in sections_copy:
                section_id = section["id"]
                if section_id in ["overview", "introduction"]:
                    info_sections.append(section)
                elif section_id in ["technicalSpecifications", "specifications", "properties"]:
                    technical_sections.append(section)
                elif section_id in ["applications", "uses"]:
                    application_sections.append(section)
                else:
                    other_sections.append(section)
            
            # Shuffle within categories
            random.shuffle(info_sections)
            random.shuffle(technical_sections)
            random.shuffle(application_sections)
            random.shuffle(other_sections)
            
            # Different group ordering options - more variations
            group_orders = [
                [info_sections, technical_sections, application_sections, other_sections],
                [info_sections, application_sections, technical_sections, other_sections],
                [info_sections, other_sections, technical_sections, application_sections],
                [info_sections, application_sections, other_sections, technical_sections],
                [info_sections, technical_sections, other_sections, application_sections],
                # Sometimes insert a technical section before the intro for variety
                [technical_sections, info_sections, application_sections, other_sections],
                [application_sections, info_sections, technical_sections, other_sections],
            ]
            
            # Pick a random group order
            chosen_order = random.choice(group_orders)
            
            # Flatten the groups
            sections_copy = []
            for group in chosen_order:
                sections_copy.extend(group)
                
        else:  # priority_jitter
            # Assign randomized priority scores with higher variability
            for section in sections_copy:
                # Base priority by section type but with less predictability
                base_priority = {
                    "overview": random.randint(0, 40),
                    "introduction": random.randint(10, 50),
                    "applications": random.randint(20, 80),
                    "technicalSpecifications": random.randint(30, 90),
                    "specifications": random.randint(20, 80),
                    "benefits": random.randint(40, 100),
                    "challenges": random.randint(30, 90)
                }.get(section["id"], random.randint(50, 100))
                
                # Add significant random jitter (-30 to +30)
                section["priority"] = base_priority + random.randint(-30, 30)
            
            # Sort by priority
            sections_copy.sort(key=lambda x: x["priority"])
            
            # Remove the temporary priority field
            for section in sections_copy:
                if "priority" in section:
                    del section["priority"]
        
        # Keep overview first only if specifically requested (default to false now)
        if keep_overview_first:
            # Find and remove overview section
            overview = next((s for s in sections_copy if s["id"] == "overview"), None)
            if overview:
                sections_copy.remove(overview)
                sections_copy.insert(0, overview)
        
        return sections_copy