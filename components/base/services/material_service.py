"""
Material formula service for Z-Beam Generator.

Provides access to chemical formulas and symbols for materials.
"""

import json
import os
from typing import Optional, Dict

class MaterialFormulaService:
    """Service to provide chemical formulas for materials."""
    
    def __init__(self):
        """Initialize the service by loading the formula database."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        formula_path = os.path.join(base_dir, 'data', 'material_formulas.json')
        symbol_path = os.path.join(base_dir, 'data', 'material_symbols.json')
        
        with open(formula_path, 'r') as f:
            self.formula_data = json.load(f)
            
        # Load symbols if file exists, otherwise create symbol mapping
        try:
            with open(symbol_path, 'r') as f:
                self.symbol_data = json.load(f)
        except FileNotFoundError:
            self.symbol_data = self._generate_symbols()
            # Save for future use
            with open(symbol_path, 'w') as f:
                json.dump(self.symbol_data, f, indent=2)
    
    def _generate_symbols(self) -> Dict[str, Dict[str, str]]:
        """Generate symbol mappings from material names.
        
        Returns:
            Dict[str, Dict[str, str]]: Generated symbol mappings by category
        """
        symbols = {}
        for category, materials in self.formula_data.items():
            symbols[category] = {}
            for material_name, formula in materials.items():
                # Generate symbol from first letters
                words = material_name.split()
                if len(words) == 1:
                    # Single word, use first two letters
                    symbol = words[0][:2]
                else:
                    # Multiple words, use first letter of each word (up to 3)
                    symbol = ''.join([word[0] for word in words[:3]])
                
                # Capitalize
                symbol = symbol.upper()
                symbols[category][material_name] = symbol
                
        return symbols
    
    def get_formula(self, material_name: str, category: Optional[str] = None) -> Optional[str]:
        """Get the chemical formula for a material.
        
        Args:
            material_name: Name of the material
            category: Material category (metal, ceramic, etc.)
            
        Returns:
            Optional[str]: Chemical formula or None if not found
        """
        # Try with specified category first
        if category and category in self.formula_data:
            if material_name in self.formula_data[category]:
                return self.formula_data[category][material_name]
                
        # If category not specified or material not found in category, search all categories
        for cat, materials in self.formula_data.items():
            if material_name in materials:
                return materials[material_name]
                
        # Not found
        return None
    
    def get_symbol(self, material_name: str, category: Optional[str] = None) -> Optional[str]:
        """Get the symbol for a material.
        
        Args:
            material_name: Name of the material
            category: Material category (metal, ceramic, etc.)
            
        Returns:
            Optional[str]: Material symbol or None if not found
        """
        # Try with specified category first
        if category and category in self.symbol_data:
            if material_name in self.symbol_data[category]:
                return self.symbol_data[category][material_name]
                
        # If category not specified or material not found in category, search all categories
        for cat, materials in self.symbol_data.items():
            if material_name in materials:
                return materials[material_name]
                
        # Not found
        return None
    
    def get_material_type(self, material_name: str, category: Optional[str] = None) -> Optional[str]:
        """Get the material type (category) for a material.
        
        Args:
            material_name: Name of the material
            category: Material category hint (metal, ceramic, etc.)
            
        Returns:
            Optional[str]: Material type or None if not found
        """
        # Try with specified category first
        if category and category in self.formula_data:
            if material_name in self.formula_data[category]:
                return category
                
        # If category not specified or material not found in category, search all categories
        for cat, materials in self.formula_data.items():
            if material_name in materials:
                return cat
                
        # Not found
        return None
    
    def get_generic_formula(self, category: str) -> Optional[str]:
        """Get a generic formula for a material category.
        
        Args:
            category: Material category (metal, ceramic, etc.)
            
        Returns:
            Optional[str]: Generic formula or None if category not supported
        """
        generic_formulas = {
            "metal": "M",
            "ceramic": "MxOy",
            "composite": "M + R",
            "glass": "SiO2",
            "masonry": "CaCO3",
            "plastic": "CnH2n",
            "semiconductor": "Si",
            "stone": "SiO2",
            "wood": "C6H10O5"
        }
        
        return generic_formulas.get(category)

# Create a singleton instance
formula_service = MaterialFormulaService()
