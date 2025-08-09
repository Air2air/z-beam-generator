"""
PropertiesTable generator for Z-Beam Generator.

Generates material properties tables from base component data, focusing on chemicalProperties and composition.
"""

import logging
from typing import Dict, Any
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
        
        # Generate tables from base component data only
        tables_content = self._generate_tables_from_base_data(base_data)
        
        if not tables_content:
            raise ValueError(f"No table data could be generated for {self.subject}")
        
        return tables_content.strip()
    
    def _generate_tables_from_base_data(self, data: Dict[str, Any]) -> str:
        """Generate markdown tables from base component data.
        
        Args:
            data: Base component data dictionary
            
        Returns:
            str: Formatted markdown tables
        """
        tables = []
        
        # Generate Chemical Properties table from material data
        chemical_table = self._create_chemical_properties_table(data)
        if chemical_table:
            tables.append(chemical_table)
        
        # Generate Composition table from material data
        composition_table = self._create_composition_table(data)
        if composition_table:
            tables.append(composition_table)
        
        # Join tables with spacing
        return "\n\n\n".join(tables) if tables else ""
    
    def _create_chemical_properties_table(self, data: Dict[str, Any]) -> str:
        """Create a chemical properties table from base component data.
        
        Args:
            data: Base component data
            
        Returns:
            str: Formatted markdown table
        """
        table_lines = []
        table_lines.append("| Property | Value |")
        table_lines.append("|----------|-------|")
        
        # Add material symbol if available
        if data.get('material_symbol'):
            table_lines.append(f"| Material Symbol | {data['material_symbol']} |")
        
        # Add chemical formula if available
        if data.get('material_formula'):
            table_lines.append(f"| Chemical Formula | {data['material_formula']} |")
        
        # Add material type if available
        if data.get('material_type'):
            table_lines.append(f"| Material Type | {data['material_type']} |")
        
        # Add category if available
        if data.get('category'):
            table_lines.append(f"| Category | {data['category']} |")
        
        # Only return table if we have data rows beyond header
        if len(table_lines) > 2:
            return "\n".join(table_lines)
        else:
            return ""
    
    def _create_composition_table(self, data: Dict[str, Any]) -> str:
        """Create a composition table from base component data.
        
        Args:
            data: Base component data
            
        Returns:
            str: Formatted markdown table
        """
        # Check if we have composition data from material formulas
        if not data.get('material_formula'):
            return ""
        
        formula = data['material_formula']
        category = data.get('category', 'material')
        
        # Create a simple composition breakdown based on the formula
        table_lines = []
        table_lines.append("| Component | Formula | Type |")
        table_lines.append("|-----------|---------|------|")
        
        # Add the main material entry
        material_name = data.get('subject', 'Material')
        table_lines.append(f"| {material_name} | {formula} | {category} |")
        
        # For composites, try to break down the formula if it contains + signs
        if '+' in formula:
            components = [comp.strip() for comp in formula.split('+')]
            # Clear the table and recreate with components
            table_lines = []
            table_lines.append("| Component | Formula | Type |")
            table_lines.append("|-----------|---------|------|")
            
            for i, comp in enumerate(components):
                comp_type = self._determine_component_type(comp, category)
                comp_name = self._determine_component_name(comp, i)
                table_lines.append(f"| {comp_name} | {comp} | {comp_type} |")
        
        return "\n".join(table_lines)
    
    def _determine_component_type(self, formula: str, category: str) -> str:
        """Determine the type of a component based on its formula and category.
        
        Args:
            formula: Chemical formula
            category: Material category
            
        Returns:
            str: Component type
        """
        if 'polymer' in formula.lower() or '(C' in formula and ')ₙ' in formula:
            return 'polymer'
        elif any(char in formula for char in ['₂', '₃', '₄', '₅']):
            return 'compound'
        elif category == 'composite':
            return 'reinforcement'
        else:
            return 'element'
    
    def _determine_component_name(self, formula: str, index: int) -> str:
        """Determine a readable name for a component based on its formula.
        
        Args:
            formula: Chemical formula
            index: Component index
            
        Returns:
            str: Component name
        """
        # Simple mapping for common formulas
        formula_names = {
            'C': 'Carbon',
            'SiO₂': 'Silica',
            'Al₂O₃': 'Alumina',
            'CaCO₃': 'Calcium Carbonate',
            'Fe₂O₃': 'Iron Oxide',
            'MgO': 'Magnesium Oxide',
            'K₂O': 'Potassium Oxide',
            'Na₂O': 'Sodium Oxide',
        }
        
        if formula in formula_names:
            return formula_names[formula]
        elif 'polymer' in formula.lower():
            return 'Polymer Matrix'
        elif '(C' in formula and ')ₙ' in formula:
            return 'Polymer Component'
        else:
            return f'Component {index + 1}'
