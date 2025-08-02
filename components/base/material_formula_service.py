import json
import os
import re

class MaterialFormulaService:
    """Service to provide chemical formulas for materials."""
    
    def __init__(self):
        """Initialize the service by loading the formula database."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        formula_path = os.path.join(base_dir, 'material_formulas.json')
        symbol_path = os.path.join(base_dir, 'material_symbols.json')
        
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
    
    def _generate_symbols(self):
        """Generate symbol mappings from material names."""
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
    
    def get_formula(self, material_name, category=None):
        """
        Get the chemical formula for a material.
        
        Args:
            material_name (str): The name of the material
            category (str, optional): The material category if known
            
        Returns:
            str: The chemical formula or None if not found
        """
        # Try with provided category first
        if category and category in self.formula_data:
            category_data = self.formula_data[category]
            if material_name in category_data:
                return category_data[material_name]
        
        # If category not provided or formula not found, search all categories
        for cat, materials in self.formula_data.items():
            if material_name in materials:
                return materials[material_name]
        
        # If still not found, try fuzzy matching
        material_lower = material_name.lower()
        for cat, materials in self.formula_data.items():
            for mat_name, formula in materials.items():
                if material_lower in mat_name.lower() or mat_name.lower() in material_lower:
                    return formula
        
        # Not found
        return None
    
    def get_symbol(self, material_name, category=None):
        """
        Get the symbol for a material.
        
        Args:
            material_name (str): The name of the material
            category (str, optional): The material category if known
            
        Returns:
            str: The symbol or a default symbol
        """
        # Try with provided category first
        if category and category in self.symbol_data:
            category_data = self.symbol_data[category]
            if material_name in category_data:
                return category_data[material_name]
        
        # If category not provided or symbol not found, search all categories
        for cat, materials in self.symbol_data.items():
            if material_name in materials:
                return materials[material_name]
        
        # If still not found, try fuzzy matching
        material_lower = material_name.lower()
        for cat, materials in self.symbol_data.items():
            for mat_name, symbol in materials.items():
                if material_lower in mat_name.lower() or mat_name.lower() in material_lower:
                    return symbol
        
        # Generate a default symbol from the name
        words = material_name.split()
        if len(words) == 1:
            # Single word, use first two letters
            symbol = words[0][:2]
        else:
            # Multiple words, use first letter of each word (up to 3)
            symbol = ''.join([word[0] for word in words[:3]])
        
        return symbol.upper()
    
    def get_material_type(self, material_name, category=None):
        """
        Determine the material type based on formula and category.
        
        Args:
            material_name (str): The name of the material
            category (str, optional): The material category if known
            
        Returns:
            str: The material type classification
        """
        # Get the formula
        formula = self.get_formula(material_name, category)
        
        # Map categories to material types
        category_to_type = {
            "metal": "element",
            "ceramic": "compound",
            "semiconductor": "element",
            "plastic": "polymer",
            "composite": "composite",
            "glass": "compound",
            "masonry": "compound",
            "stone": "mineral",
            "wood": "composite"
        }
        
        # Special cases based on formula patterns
        if formula:
            if "+" in formula:
                return "composite"
            elif "₁₋ₓ" in formula or "-" in formula and any(metal in formula for metal in ["Cu", "Fe", "Ni", "Al"]):
                return "alloy"
            elif formula in ["C", "Si", "Ge", "Au", "Ag", "Cu", "Fe", "Al", "Ti", "Zn", "Sn", "Pb", "Ni", "Cr", "Mo", "W"]:
                return "element"
            elif "(" in formula and ")" in formula and "ₙ" in formula:
                return "polymer"
            elif any(oxide in formula for oxide in ["O₂", "O₃", "O₄"]):
                return "compound"
        
        # Default to category mapping
        return category_to_type.get(category, "compound")
    
    def get_generic_formula(self, category):
        """
        Get a generic formula representation for a material category.
        
        Args:
            category (str): The material category
            
        Returns:
            str: A generic formula representation
        """
        generic_formulas = {
            "ceramic": "MₓOᵧ (Metal Oxide)",
            "metal": "M (Elemental Metal)",
            "composite": "(CₓHᵧOᵤ)ₙ + fillers",
            "glass": "SiO₂ + modifiers",
            "semiconductor": "MₓNᵧ (Semiconductor Compound)",
            "plastic": "(CₓHᵧ)ₙ (Polymer)",
            "masonry": "Mineral Compounds",
            "stone": "Mineral Oxides and Carbonates",
            "wood": "(C₆H₁₀O₅)ₙ + (C₉H₁₀O₂(OCH₃))ₙ"
        }
        
        return generic_formulas.get(category, "Complex composition")

# Singleton instance for easy import
formula_service = MaterialFormulaService()
