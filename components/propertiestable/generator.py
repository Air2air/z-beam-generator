"""
PropertiesTable generator for Z-Beam Generator.

Generates material properties tables from base component data, combining chemical and composition data.
"""

import logging
from typing import Dict, Any, List
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class PropertiesTableGenerator(BaseComponent):
    """Generator for material properties tables from base component data."""
    
    def _load_prompt_config(self) -> Dict[str, Any]:
        """Override to skip prompt loading since we don't use AI.
        
        Returns:
            Empty dict as we don't need prompt configuration
        """
        return {}
    
    def generate(self) -> str:
        """Generate properties tables directly from base component data without AI.
        
        Returns:
            str: Generated properties tables content
            
        Raises:
            ValueError: If base component data is unavailable
        """
        # Get base component data
        base_data = self.get_template_data()
        
        if not base_data:
            raise ValueError(f"No base component data available for {self.subject}")
        
        # Generate single table combining chemical and composition data
        table_content = self._generate_unified_table(base_data)
        
        if not table_content:
            raise ValueError(f"No table data could be generated for {self.subject}")
        
        return table_content.strip()
    
    def _generate_unified_table(self, data: Dict[str, Any]) -> str:
        """Generate single unified markdown table from base component data.
        
        Args:
            data: Base component data dictionary
            
        Returns:
            str: Single formatted markdown table with 4 most interesting properties
        """
        # Collect all possible properties from both chemical and composition data
        all_properties = self._collect_all_available_properties(data)
        
        # Select the 4 most interesting properties
        selected_properties = self._select_most_interesting_properties(all_properties, data)
        
        # Generate single unified table
        if selected_properties:
            table_lines = []
            table_lines.append("| Property | Value |")
            table_lines.append("|----------|-------|")
            
            for prop_name, prop_value in selected_properties:
                table_lines.append(f"| {prop_name} | {prop_value} |")
            
            return "\n".join(table_lines)
        else:
            return ""
    
    def _collect_all_available_properties(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Collect all available properties from both chemical and composition data.
        
        Args:
            data: Base component data
            
        Returns:
            Dict mapping property names to values
        """
        properties = {}
        
        # Add basic chemical properties
        if data.get('material_formula'):
            properties['Chemical Formula'] = data['material_formula']
        
        if data.get('material_symbol'):
            properties['Material Symbol'] = data['material_symbol']
        
        if data.get('category'):
            properties['Category'] = data['category'].title()
        
        if data.get('material_type'):
            properties['Material Type'] = data['material_type'].title()
        
        # Add category-specific properties
        category = data.get('category', '').lower()
        subject = data.get('subject', '')
        self._add_category_specific_properties_to_dict(properties, data, category, subject)
        
        # Add composition-derived properties
        self._add_composition_properties_to_dict(properties, data)
        
        return properties
    
    def _add_category_specific_properties_to_dict(self, properties: Dict[str, str], data: Dict[str, Any], category: str, subject: str) -> None:
        """Add category-specific properties to the properties dictionary."""
        if category == 'metal':
            self._add_metal_properties_to_dict(properties, data, subject)
        elif category == 'ceramic':
            self._add_ceramic_properties_to_dict(properties, data, subject)
        elif category == 'plastic':
            self._add_plastic_properties_to_dict(properties, data, subject)
        elif category == 'composite':
            self._add_composite_properties_to_dict(properties, data, subject)
        elif category == 'glass':
            self._add_glass_properties_to_dict(properties, data, subject)
        elif category == 'semiconductor':
            self._add_semiconductor_properties_to_dict(properties, data, subject)
        elif category == 'stone':
            self._add_stone_properties_to_dict(properties, data, subject)
        elif category == 'wood':
            self._add_wood_properties_to_dict(properties, data, subject)
        elif category == 'masonry':
            self._add_masonry_properties_to_dict(properties, data, subject)
    
    def _add_composition_properties_to_dict(self, properties: Dict[str, str], data: Dict[str, Any]) -> None:
        """Add composition-derived properties to the properties dictionary."""
        formula = data.get('material_formula', '')
        
        if '+' in formula:
            # Multi-component material
            components = [comp.strip() for comp in formula.split('+')]
            properties['Component Count'] = str(len(components))
            
            # Identify primary component
            if components:
                properties['Primary Component'] = self._get_primary_component_name(components[0])
        
        # Add complexity indicator
        if '·' in formula:
            properties['Structure Type'] = 'Complex compound'
        elif '+' in formula:
            properties['Structure Type'] = 'Composite'
        elif '(' in formula and ')ₙ' in formula:
            properties['Structure Type'] = 'Polymer'
        elif any(char in formula for char in ['₂', '₃', '₄', '₅']):
            properties['Structure Type'] = 'Chemical compound'
        else:
            properties['Structure Type'] = 'Pure element'
    
    def _get_primary_component_name(self, formula: str) -> str:
        """Get a readable name for the primary component."""
        formula_names = {
            'SiO₂': 'Silica',
            'Al₂O₃': 'Alumina', 
            'C': 'Carbon',
            'CaCO₃': 'Calcium Carbonate',
            'Fe₂O₃': 'Iron Oxide',
            'B₂O₃': 'Boric Oxide',
            'Na₂O': 'Sodium Oxide',
            'CaO': 'Calcium Oxide'
        }
        return formula_names.get(formula, formula)
    
    def _select_most_interesting_properties(self, all_properties: Dict[str, str], data: Dict[str, Any]) -> List[tuple]:
        """Select the 4 most interesting properties from all available properties.
        
        Args:
            all_properties: Dictionary of all available properties
            data: Base component data for context
            
        Returns:
            List of (property_name, property_value) tuples (exactly 4)
        """
        # Define priority order for property types
        high_priority = [
            'Chemical Formula',  # Always include if available
            'Tensile Strength', 'Compressive Strength', 'Hardness',  # Mechanical
            'Melting Point', 'Thermal Expansion', 'Thermal Conductivity',  # Thermal  
            'Band Gap', 'Electrical Conductivity', 'Dielectric Strength',  # Electrical
            'Density', 'Crystal Structure', 'Fracture Toughness'  # Physical/Structural
        ]
        
        medium_priority = [
            'Chemical Resistance', 'Corrosion Resistance', 'Biocompatibility',  # Chemical/Bio
            'Elastic Modulus', 'Impact Strength', 'Wear Resistance',  # Mechanical
            'Thermal Shock', 'Temperature Range', 'Glass Transition',  # Thermal
            'Transparency', 'Purity', 'Friction Coefficient'  # Optical/Surface
        ]
        
        low_priority = [
            'Material Symbol', 'Category', 'Material Type', 'Material Class',  # Classification
            'Structure Type', 'Component Count', 'Primary Component',  # Composition
            'Weight', 'Processing', 'Applications', 'Formation'  # General
        ]
        
        selected = []
        
        # First pass: Add high priority properties
        for prop in high_priority:
            if len(selected) >= 4:
                break
            if prop in all_properties:
                selected.append((prop, all_properties[prop]))
        
        # Second pass: Add medium priority properties
        for prop in medium_priority:
            if len(selected) >= 4:
                break
            if prop in all_properties:
                selected.append((prop, all_properties[prop]))
        
        # Third pass: Add low priority properties if needed
        for prop in low_priority:
            if len(selected) >= 4:
                break
            if prop in all_properties:
                selected.append((prop, all_properties[prop]))
        
        # Final pass: Add any remaining properties if we still need more
        for prop, value in all_properties.items():
            if len(selected) >= 4:
                break
            if prop not in [s[0] for s in selected]:
                selected.append((prop, value))
        
        return selected[:4]  # Ensure exactly 4 properties
    
    # Material-specific property methods for dictionary
    def _add_metal_properties_to_dict(self, properties: Dict[str, str], data: Dict[str, Any], subject: str) -> None:
        """Add metal-specific properties to dictionary."""
        if 'aluminum' in subject.lower():
            properties['Crystal Structure'] = 'Face-centered cubic (FCC)'
            properties['Density'] = '2.70 g/cm³'
            properties['Melting Point'] = '660°C'
            properties['Thermal Conductivity'] = '237 W/m·K'
        elif 'steel' in subject.lower() or 'iron' in subject.lower():
            properties['Crystal Structure'] = 'Body-centered cubic (BCC)'
            properties['Density'] = '7.87 g/cm³'
            properties['Tensile Strength'] = '400-550 MPa'
            properties['Magnetic Property'] = 'Ferromagnetic'
        elif 'copper' in subject.lower():
            properties['Crystal Structure'] = 'Face-centered cubic (FCC)'
            properties['Electrical Conductivity'] = '59.6 MS/m'
            properties['Thermal Conductivity'] = '401 W/m·K'
            properties['Density'] = '8.96 g/cm³'
        elif 'titanium' in subject.lower():
            properties['Crystal Structure'] = 'Hexagonal close-packed (HCP)'
            properties['Density'] = '4.51 g/cm³'
            properties['Tensile Strength'] = '240-550 MPa'
            properties['Corrosion Resistance'] = 'Excellent'
        else:
            properties['Material Class'] = 'Metal'
            properties['Electrical Conductivity'] = 'High'
            properties['Thermal Conductivity'] = 'High'
    
    def _add_ceramic_properties_to_dict(self, properties: Dict[str, str], data: Dict[str, Any], subject: str) -> None:
        """Add ceramic-specific properties to dictionary."""
        if 'alumina' in subject.lower():
            properties['Hardness'] = '9 Mohs'
            properties['Melting Point'] = '2072°C'
            properties['Dielectric Strength'] = '35 kV/mm'
            properties['Thermal Conductivity'] = '30 W/m·K'
        elif 'zirconia' in subject.lower():
            properties['Fracture Toughness'] = '7-10 MPa·m½'
            properties['Thermal Expansion'] = '10.8×10⁻⁶/K'
            properties['Biocompatibility'] = 'Excellent'
            properties['Hardness'] = '8.5 Mohs'
        elif 'silicon carbide' in subject.lower():
            properties['Hardness'] = '9.5 Mohs'
            properties['Thermal Conductivity'] = '120 W/m·K'
            properties['Chemical Resistance'] = 'Excellent'
            properties['Melting Point'] = '2730°C'
        else:
            properties['Material Class'] = 'Ceramic'
            properties['Thermal Resistance'] = 'High'
            properties['Electrical Property'] = 'Insulator'
    
    def _add_plastic_properties_to_dict(self, properties: Dict[str, str], data: Dict[str, Any], subject: str) -> None:
        """Add plastic-specific properties to dictionary."""
        if 'ptfe' in subject.lower() or 'teflon' in subject.lower():
            properties['Chemical Resistance'] = 'Exceptional'
            properties['Friction Coefficient'] = '0.05-0.10'
            properties['Temperature Range'] = '-200°C to 260°C'
            properties['Dielectric Strength'] = '60 kV/mm'
        elif 'polycarbonate' in subject.lower():
            properties['Impact Strength'] = 'High (850 J/m)'
            properties['Transparency'] = 'Excellent'
            properties['Glass Transition'] = '147°C'
            properties['Tensile Strength'] = '55-75 MPa'
        elif 'nylon' in subject.lower():
            properties['Tensile Strength'] = '75-85 MPa'
            properties['Elastic Modulus'] = '2.8 GPa'
            properties['Wear Resistance'] = 'Excellent'
            properties['Water Absorption'] = '1.5-3%'
        else:
            properties['Material Class'] = 'Polymer'
            properties['Density'] = '0.9-2.3 g/cm³'
            properties['Processing'] = 'Thermoplastic'
    
    def _add_composite_properties_to_dict(self, properties: Dict[str, str], data: Dict[str, Any], subject: str) -> None:
        """Add composite-specific properties to dictionary."""
        if 'carbon fiber' in subject.lower():
            properties['Tensile Strength'] = '>3000 MPa'
            properties['Elastic Modulus'] = '230 GPa'
            properties['Density'] = '1.6 g/cm³'
            properties['Thermal Expansion'] = 'Near zero'
        elif 'fiberglass' in subject.lower():
            properties['Tensile Strength'] = '200-400 MPa'
            properties['Electrical Property'] = 'Insulator'
            properties['Corrosion Resistance'] = 'Excellent'
            properties['Density'] = '1.8-2.1 g/cm³'
        else:
            properties['Material Class'] = 'Composite'
            properties['Anisotropy'] = 'Directional properties'
    
    def _add_glass_properties_to_dict(self, properties: Dict[str, str], data: Dict[str, Any], subject: str) -> None:
        """Add glass-specific properties to dictionary."""
        if 'borosilicate' in subject.lower():
            properties['Thermal Expansion'] = '3.3×10⁻⁶/K'
            properties['Thermal Shock'] = 'Resistant'
            properties['Chemical Durability'] = 'Excellent'
            properties['Softening Point'] = '820°C'
        elif 'soda-lime' in subject.lower():
            properties['Thermal Expansion'] = '9×10⁻⁶/K'
            properties['Density'] = '2.5 g/cm³'
            properties['Hardness'] = '5.5-6.5 Mohs'
            properties['Transparency'] = 'High'
        else:
            properties['Material Class'] = 'Glass'
            properties['Transparency'] = 'Transparent'
            properties['Brittleness'] = 'High'
    
    def _add_semiconductor_properties_to_dict(self, properties: Dict[str, str], data: Dict[str, Any], subject: str) -> None:
        """Add semiconductor-specific properties to dictionary."""
        if 'silicon' in subject.lower():
            properties['Band Gap'] = '1.12 eV'
            properties['Crystal Structure'] = 'Diamond cubic'
            properties['Purity'] = '>99.999%'
            properties['Electrical Conductivity'] = 'Variable'
        elif 'gallium arsenide' in subject.lower():
            properties['Band Gap'] = '1.42 eV'
            properties['Electron Mobility'] = '8500 cm²/V·s'
            properties['Crystal Structure'] = 'Zinc blende'
            properties['Applications'] = 'High-frequency'
        else:
            properties['Material Class'] = 'Semiconductor'
            properties['Electrical Property'] = 'Variable conductivity'
    
    def _add_stone_properties_to_dict(self, properties: Dict[str, str], data: Dict[str, Any], subject: str) -> None:
        """Add stone-specific properties to dictionary."""
        if 'granite' in subject.lower():
            properties['Compressive Strength'] = '130-200 MPa'
            properties['Density'] = '2.63-2.75 g/cm³'
            properties['Porosity'] = '0.4-1.5%'
            properties['Hardness'] = '6-7 Mohs'
        elif 'marble' in subject.lower():
            properties['Hardness'] = '3-5 Mohs'
            properties['Compressive Strength'] = '70-140 MPa'
            properties['Density'] = '2.7 g/cm³'
            properties['Workability'] = 'Excellent'
        else:
            properties['Material Class'] = 'Natural stone'
            properties['Formation'] = 'Geological'
    
    def _add_wood_properties_to_dict(self, properties: Dict[str, str], data: Dict[str, Any], subject: str) -> None:
        """Add wood-specific properties to dictionary."""
        if 'oak' in subject.lower():
            properties['Density'] = '0.6-0.9 g/cm³'
            properties['Compressive Strength'] = '50-60 MPa'
            properties['Hardness'] = '5.9 kN (Janka)'
            properties['Durability'] = 'Excellent'
        elif 'pine' in subject.lower():
            properties['Density'] = '0.35-0.5 g/cm³'
            properties['Compressive Strength'] = '35-45 MPa'
            properties['Wood Type'] = 'Softwood'
            properties['Growth Rate'] = 'Fast'
        else:
            properties['Material Class'] = 'Organic'
            properties['Renewability'] = 'Renewable'
    
    def _add_masonry_properties_to_dict(self, properties: Dict[str, str], data: Dict[str, Any], subject: str) -> None:
        """Add masonry-specific properties to dictionary."""
        if 'concrete' in subject.lower():
            properties['Compressive Strength'] = '20-40 MPa'
            properties['Density'] = '2.4 g/cm³'
            properties['Curing Time'] = '28 days'
            properties['Thermal Mass'] = 'High'
        elif 'brick' in subject.lower():
            properties['Compressive Strength'] = '10-40 MPa'
            properties['Water Absorption'] = '8-22%'
            properties['Thermal Conductivity'] = '0.6-1.0 W/m·K'
            properties['Firing Temperature'] = '900-1200°C'
        else:
            properties['Material Class'] = 'Construction'
            properties['Compressive Strength'] = 'High'
