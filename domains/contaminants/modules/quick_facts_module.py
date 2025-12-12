"""
Quick Facts Module - Generate quick facts section for contamination frontmatter

Per CONTAMINATION_FRONTMATTER_SPEC.md Enhancement #2

Purpose: Above-fold value, immediate decision-making data
Data source: laser_properties.removal_efficiency and process_variables
"""

import logging
from typing import Dict, Optional, List


class QuickFactsModule:
    """Generate quick facts for contamination frontmatter"""
    
    def __init__(self):
        """Initialize quick facts module"""
        self.logger = logging.getLogger(__name__)
    
    def generate(self, contaminant_data: Dict) -> Optional[Dict]:
        """
        Generate quick facts from contaminant data
        
        Args:
            contaminant_data: Contaminant data from Contaminants.yaml
            
        Returns:
            Dictionary with quick_facts or None if insufficient data
        """
        self.logger.info("Generating quick facts")
        
        laser_props = contaminant_data.get('laser_properties')
        if not laser_props:
            self.logger.warning("No laser_properties for quick facts")
            return None
        
        quick_facts = {}
        
        # Removal efficiency (from removal_efficiency section)
        efficiency = laser_props.get('removal_efficiency', {})
        if efficiency:
            single_pass = efficiency.get('single_pass_percentage', 70)
            optimal_passes = efficiency.get('passes_for_complete_removal', 3)
            quick_facts['removal_efficiency'] = f"{single_pass}% single pass, 95%+ in {optimal_passes} passes"
        
        # Process speed (from process_variables)
        process_vars = laser_props.get('process_variables', {})
        if process_vars:
            coverage = process_vars.get('area_coverage_rate_cm2_min')
            if coverage:
                quick_facts['process_speed'] = f"{coverage} cm²/min coverage rate"
        
        # Substrate safety (from surface_integrity)
        surface = laser_props.get('surface_integrity', {})
        if surface:
            damage_risk = surface.get('damage_risk_to_substrate', 'low')
            quick_facts['substrate_safety'] = f"{damage_risk.title()} damage risk"
        
        # Key benefit (generated)
        quick_facts['key_benefit'] = "Zero chemicals, no substrate damage"
        
        # Typical applications (from context_notes or generate)
        context = contaminant_data.get('context_notes', '')
        applications = self._extract_applications(context, contaminant_data)
        if applications:
            quick_facts['typical_applications'] = applications
        
        if not quick_facts:
            self.logger.warning("Could not generate quick facts")
            return None
        
        self.logger.info("✅ Generated quick facts")
        return quick_facts
    
    def _extract_applications(self, context_notes: str, contaminant_data: Dict) -> List[str]:
        """Extract or generate typical applications"""
        # Try to extract from context_notes
        applications = []
        
        # Get contaminant ID to infer applications
        contaminant_id = contaminant_data.get('id', '')
        
        # Generate context-aware applications
        if 'adhesive' in contaminant_id or 'label' in contaminant_id:
            applications = [
                "Label removal from manufactured products",
                "Shipping sticker cleanup",
                "Tape residue after assembly",
                "QC reject sticker removal",
                "Packaging adhesive removal"
            ]
        elif 'rust' in contaminant_id or 'corrosion' in contaminant_id:
            applications = [
                "Surface restoration of metal parts",
                "Pre-coating rust removal",
                "Equipment maintenance",
                "Historical artifact conservation",
                "Structural steel preparation"
            ]
        elif 'paint' in contaminant_id or 'coating' in contaminant_id:
            applications = [
                "Paint stripping for refinishing",
                "Graffiti removal",
                "Coating removal before welding",
                "Aircraft paint stripping",
                "Equipment refurbishment"
            ]
        elif 'oil' in contaminant_id or 'grease' in contaminant_id:
            applications = [
                "Manufacturing equipment cleaning",
                "Mold surface preparation",
                "Pre-bonding surface cleaning",
                "Machinery maintenance",
                "Food processing equipment"
            ]
        else:
            # Generic applications
            applications = [
                "Surface preparation",
                "Industrial cleaning",
                "Equipment maintenance",
                "Quality control preparation",
                "Pre-processing cleaning"
            ]
        
        return applications[:5]  # Limit to 5
