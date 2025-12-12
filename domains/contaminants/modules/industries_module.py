"""
Industries Module - Generate industries served section for contamination frontmatter

Per CONTAMINATION_FRONTMATTER_SPEC.md Enhancement #4

Purpose: Lead qualification, SEO long-tail keywords, industry self-identification
"""

import logging
from typing import Dict, List, Optional


class IndustriesModule:
    """Generate industries served for contamination frontmatter"""
    
    # Industry mapping by contamination type
    INDUSTRY_MAPPINGS = {
        'adhesive': [
            {
                'name': 'Manufacturing',
                'use_cases': [
                    'Label removal from finished products',
                    'QC reject sticker removal from production',
                    'Tape residue after masking or assembly'
                ],
                'materials': ['metal', 'plastic', 'glass'],
                'frequency': 'very_high'
            },
            {
                'name': 'Automotive',
                'use_cases': [
                    'VIN sticker removal from windshields',
                    'Masking tape residue from paint operations',
                    'Label removal from parts and assemblies'
                ],
                'materials': ['glass', 'metal', 'plastic'],
                'frequency': 'high'
            },
            {
                'name': 'Shipping & Logistics',
                'use_cases': [
                    'Pallet label removal for reuse',
                    'Shipping tape residue from containers',
                    'Barcode sticker cleanup'
                ],
                'materials': ['metal', 'plastic', 'wood'],
                'frequency': 'high'
            }
        ],
        'rust': [
            {
                'name': 'Manufacturing',
                'use_cases': [
                    'Surface preparation for coating',
                    'Equipment restoration',
                    'Part refurbishment'
                ],
                'materials': ['steel', 'iron', 'metal'],
                'frequency': 'very_high'
            },
            {
                'name': 'Construction',
                'use_cases': [
                    'Structural steel cleaning',
                    'Rebar surface preparation',
                    'Equipment maintenance'
                ],
                'materials': ['steel', 'iron'],
                'frequency': 'high'
            },
            {
                'name': 'Marine',
                'use_cases': [
                    'Hull restoration',
                    'Equipment cleaning',
                    'Corrosion removal'
                ],
                'materials': ['steel', 'aluminum'],
                'frequency': 'high'
            }
        ],
        'paint': [
            {
                'name': 'Automotive',
                'use_cases': [
                    'Paint stripping for refinishing',
                    'Surface preparation',
                    'Defect removal'
                ],
                'materials': ['metal', 'plastic'],
                'frequency': 'very_high'
            },
            {
                'name': 'Aerospace',
                'use_cases': [
                    'Aircraft paint removal',
                    'Component refurbishment',
                    'Maintenance operations'
                ],
                'materials': ['aluminum', 'composites'],
                'frequency': 'high'
            }
        ]
    }
    
    def __init__(self):
        """Initialize industries module"""
        self.logger = logging.getLogger(__name__)
    
    def generate(self, contaminant_data: Dict) -> Optional[List[Dict]]:
        """
        Generate industries served from contaminant data
        
        Args:
            contaminant_data: Contaminant data from Contaminants.yaml
            
        Returns:
            List of industry dictionaries or None
        """
        self.logger.info("Generating industries served")
        
        # Detect contamination type
        contaminant_id = contaminant_data.get('id', '')
        contam_type = self._detect_type(contaminant_id)
        
        # Get industry mappings
        industries = self.INDUSTRY_MAPPINGS.get(contam_type, self._get_generic_industries())
        
        if not industries:
            self.logger.warning("Could not generate industries")
            return None
        
        self.logger.info(f"✅ Generated {len(industries)} industries")
        return industries
    
    def _detect_type(self, contaminant_id: str) -> str:
        """Detect contamination type from ID"""
        id_lower = contaminant_id.lower()
        
        if 'adhesive' in id_lower or 'tape' in id_lower or 'label' in id_lower:
            return 'adhesive'
        elif 'rust' in id_lower or 'corrosion' in id_lower:
            return 'rust'
        elif 'paint' in id_lower or 'coating' in id_lower:
            return 'paint'
        elif 'oil' in id_lower or 'grease' in id_lower:
            return 'oil'
        else:
            return 'generic'
    
    def _get_generic_industries(self) -> List[Dict]:
        """Get generic industry list for unknown types"""
        return [
            {
                'name': 'Manufacturing',
                'use_cases': [
                    'Surface preparation',
                    'Quality control',
                    'Equipment maintenance'
                ],
                'materials': ['metal', 'plastic', 'composite'],
                'frequency': 'high'
            },
            {
                'name': 'Industrial Cleaning',
                'use_cases': [
                    'Equipment cleaning',
                    'Surface restoration',
                    'Maintenance operations'
                ],
                'materials': ['metal', 'stone', 'concrete'],
                'frequency': 'moderate'
            }
        ]
