"""
Table component post-processor for content cleanup and enhancement.
"""
import re
import logging

logger = logging.getLogger(__name__)


def post_process_table(content: str, material_name: str = "") -> str:
    """
    Post-process table content for consistency and quality.
    
    Args:
        content: Generated table content
        material_name: Name of the material being processed
        
    Returns:
        str: Post-processed table content
    """
    if not content or not content.strip():
        return content
    
    lines = content.strip().split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            processed_lines.append('')
            continue
        
        # Clean up table formatting
        if '|' in line:
            # Split by pipes and clean each cell
            cells = line.split('|')
            cleaned_cells = []
            
            for cell in cells:
                cell = cell.strip()
                # Normalize whitespace within cells
                cell = re.sub(r'\s+', ' ', cell)
                # Clean up technical terms
                cell = clean_technical_terms(cell)
                cleaned_cells.append(cell)
            
            line = '| ' + ' | '.join(cleaned_cells[1:-1]) + ' |' if len(cleaned_cells) > 2 else line
        
        processed_lines.append(line)
    
    processed = '\n'.join(processed_lines)
    
    # Material-specific enhancements
    if material_name:
        material_lower = material_name.lower()
        if material_lower in processed.lower() and material_name not in processed:
            processed = re.sub(rf'\b{re.escape(material_lower)}\b', material_name, processed, flags=re.IGNORECASE)
    
    return processed


def clean_technical_terms(text: str) -> str:
    """Clean up technical terminology in table cells."""
    technical_replacements = {
        'laser cleaning': 'laser cleaning',
        'contaminant': 'contaminant',
        'substrate': 'substrate',
        'surface': 'surface',
        'ablation': 'ablation',
        'wavelength': 'wavelength',
        'pulse duration': 'pulse duration',
        'energy density': 'energy density'
    }
    
    for old_term, new_term in technical_replacements.items():
        text = re.sub(rf'\b{re.escape(old_term)}\b', new_term, text, flags=re.IGNORECASE)
    
    return text
