#!/usr/bin/env python3
"""
Content component post-processor for content cleanup and enhancement.
Handles technical formatting, structure improvement, and quality enhancements.
"""
import re
import logging

logger = logging.getLogger(__name__)


def post_process_content(content: str, material_name: str = "", material_data: dict = None, author_info: dict = None) -> str:
    """
    Post-process content for consistency, formatting, and technical accuracy.
    
    Args:
        content: Generated content to process
        material_name: Name of the material being processed
        material_data: Additional material data for context
        author_info: Author information including country for style adaptation
        
    Returns:
        str: Post-processed content
    """
    if not content or not content.strip():
        return content
    
    # Basic cleanup
    content = _clean_basic_formatting(content)
    
    # Apply author country-specific style corrections
    if author_info:
        content = _apply_country_style(content, author_info)
    
    # Fix technical terminology
    content = _standardize_technical_terms(content)
    
    # Enhance material-specific content
    if material_name or material_data:
        content = _enhance_material_context(content, material_name, material_data)
    
    # Improve paragraph structure
    content = _improve_paragraph_structure(content)
    
    # Fix common grammar and style issues
    content = _fix_grammar_and_style(content)
    
    # Enhance human-like writing characteristics
    content = _enhance_human_writing_style(content)
    
    return content.strip()


def _clean_basic_formatting(content: str) -> str:
    """Clean basic formatting issues."""
    # Remove excessive whitespace
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    content = re.sub(r' +', ' ', content)
    
    # Fix spacing around punctuation
    content = re.sub(r'\s+([,.;:])', r'\1', content)
    content = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', content)
    
    # Remove trailing whitespace from lines
    lines = [line.rstrip() for line in content.split('\n')]
    content = '\n'.join(lines)
    
    return content


def _standardize_technical_terms(content: str) -> str:
    """Standardize technical terminology and formatting."""
    # Standardize laser wavelength notation
    content = re.sub(r'(\d+)\s*nanometers?', r'\1 nm', content, flags=re.IGNORECASE)
    content = re.sub(r'(\d+)\s*nm\b', r'\1 nm', content)
    
    # Standardize pulse duration notation
    content = re.sub(r'nanoseconds?', 'nanosecond', content, flags=re.IGNORECASE)
    content = re.sub(r'(\d+)-(\d+)\s*ns', r'\1-\2 ns', content)
    
    # Standardize laser types
    content = re.sub(r'\bnd:yag\b', 'Nd:YAG', content, flags=re.IGNORECASE)
    content = re.sub(r'\bfiber\s+laser\b', 'fiber laser', content, flags=re.IGNORECASE)
    
    # Standardize units and measurements
    content = re.sub(r'\bclass\s*4\s*laser', 'Class 4 laser', content, flags=re.IGNORECASE)
    content = re.sub(r'\bw/cm2\b', 'W/cm²', content, flags=re.IGNORECASE)
    content = re.sub(r'\bum\b', 'μm', content)
    
    # Standardize common laser cleaning terms
    content = re.sub(r'\blaser\s*cleaning\b', 'laser cleaning', content, flags=re.IGNORECASE)
    content = re.sub(r'\bsurface\s*contamination\b', 'surface contamination', content, flags=re.IGNORECASE)
    
    return content


def _enhance_material_context(content: str, material_name: str, material_data: dict) -> str:
    """Enhance content with material-specific context."""
    if not material_name and not material_data:
        return content
    
    # Ensure material name consistency
    if material_name:
        # Find variations of the material name and standardize
        name_variations = [
            material_name,
            material_name.lower(),
            material_name.title(),
            material_name.upper()
        ]
        
        for variation in name_variations:
            if variation != material_name and variation in content:
                content = content.replace(variation, material_name)
    
    # Add chemical formula context if available
    if material_data and 'chemical_formula' in material_data:
        formula = material_data['chemical_formula']
        # If formula is mentioned separately, ensure it's properly formatted
        if formula in content and f'({formula})' not in content:
            content = content.replace(formula, f'({formula})', 1)
    
    # Enhance density information formatting
    if material_data and 'density' in material_data:
        density = material_data['density']
        # Standardize density notation
        content = re.sub(r'density[:\s]*(\d+\.?\d*)\s*g/cm3?', 
                        f'density of {density} g/cm³', content, flags=re.IGNORECASE)
    
    return content


def _improve_paragraph_structure(content: str) -> str:
    """Improve paragraph structure and flow."""
    paragraphs = content.split('\n\n')
    improved_paragraphs = []
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # Ensure paragraphs start with capital letters
        if paragraph and not paragraph[0].isupper():
            paragraph = paragraph[0].upper() + paragraph[1:]
        
        # Ensure paragraphs end with proper punctuation
        if paragraph and paragraph[-1] not in '.!?':
            paragraph += '.'
        
        improved_paragraphs.append(paragraph)
    
    return '\n\n'.join(improved_paragraphs)


def _fix_grammar_and_style(content: str) -> str:
    """Fix common grammar and style issues."""
    # Fix common article issues
    content = re.sub(r'\ba\s+([aeiou])', r'an \1', content, flags=re.IGNORECASE)
    content = re.sub(r'\ban\s+([bcdfghjklmnpqrstvwxyz])', r'a \1', content, flags=re.IGNORECASE)
    
    # Fix common verb tense issues in technical writing
    content = re.sub(r'\blaser cleaning provide\b', 'laser cleaning provides', content, flags=re.IGNORECASE)
    content = re.sub(r'\blaser cleaning offer\b', 'laser cleaning offers', content, flags=re.IGNORECASE)
    
    # Improve technical flow
    content = re.sub(r'\bIn addition,?\s+', 'Additionally, ', content)
    content = re.sub(r'\bFurthermore,?\s+', 'Moreover, ', content)
    
    # Fix common technical writing redundancies
    content = re.sub(r'\bvery effective\b', 'highly effective', content, flags=re.IGNORECASE)
    content = re.sub(r'\bvery efficient\b', 'highly efficient', content, flags=re.IGNORECASE)
    
    # Improve transition between technical concepts
    content = re.sub(r'\.\s*This\s+', '. This approach ', content)
    content = re.sub(r'\.\s*These\s+', '. These methods ', content)
    
    return content


def enhance_technical_accuracy(content: str, material_data: dict = None) -> str:
    """
    Additional technical accuracy enhancements.
    
    Args:
        content: Content to enhance
        material_data: Material-specific data for accuracy
        
    Returns:
        str: Enhanced content with improved technical accuracy
    """
    if not material_data:
        return content
    
    # Enhance based on material properties
    if 'absorption_coefficient' in material_data:
        # Ensure absorption discussion is technically accurate
        content = re.sub(r'absorption\s+coefficient', 
                        f'absorption coefficient ({material_data["absorption_coefficient"]})', 
                        content, count=1, flags=re.IGNORECASE)
    
    if 'melting_point' in material_data:
        # Add context about thermal considerations
        melting_point = material_data['melting_point']
        if 'thermal' in content.lower() and str(melting_point) not in content:
            content = re.sub(r'(thermal\s+considerations?)', 
                           f'\\1 (melting point: {melting_point}°C)', 
                           content, count=1, flags=re.IGNORECASE)
    
    return content


def _apply_country_style(content: str, author_info: dict) -> str:
    """Apply country-specific writing style corrections."""
    if not author_info or 'country' not in author_info:
        return content
    
    country = author_info['country'].lower()
    
    if country in ['uk', 'united kingdom', 'britain', 'england']:
        # Convert to British English
        us_to_uk = {
            r'\bcolor\b': 'colour', r'\bhonor\b': 'honour',
            r'\blabor\b': 'labour', r'\bfavor\b': 'favour',
            r'\bcenter\b': 'centre', r'\bmeter\b': 'metre',
            r'\bliter\b': 'litre', r'\bfiber\b': 'fibre',
            r'\banalyze\b': 'analyse', r'\brealize\b': 'realise',
            r'\baluminum\b': 'aluminium'
        }
        
        for us_pattern, uk_spelling in us_to_uk.items():
            content = re.sub(us_pattern, uk_spelling, content, flags=re.IGNORECASE)
    
    elif country in ['usa', 'united states', 'america', 'us']:
        # Convert to American English
        uk_to_us = {
            r'\bcolour\b': 'color', r'\bhonour\b': 'honor',
            r'\blabour\b': 'labor', r'\bfavour\b': 'favor',
            r'\bcentre\b': 'center', r'\bmetre\b': 'meter',
            r'\blitre\b': 'liter', r'\bfibre\b': 'fiber',
            r'\banalyse\b': 'analyze', r'\brealise\b': 'realize',
            r'\baluminium\b': 'aluminum'
        }
        
        for uk_pattern, us_spelling in uk_to_us.items():
            content = re.sub(uk_pattern, us_spelling, content, flags=re.IGNORECASE)
    
    elif country in ['germany', 'deutschland', 'de']:
        # German technical style tends to be more systematic
        # Add systematic transitions if missing
        if not re.search(r'\b(firstly|initially|furthermore|moreover)\b', content, re.IGNORECASE):
            # Insert systematic progression at paragraph breaks
            paragraphs = content.split('\n\n')
            if len(paragraphs) >= 3:
                paragraphs[1] = 'Furthermore, ' + paragraphs[1].lstrip()
                if len(paragraphs) >= 4:
                    paragraphs[2] = 'Moreover, ' + paragraphs[2].lstrip()
                content = '\n\n'.join(paragraphs)
    
    return content


def _enhance_human_writing_style(content: str) -> str:
    """Enhance content to be more human-like and less AI-generated."""
    
    # Remove overly formal AI-like phrases
    ai_phrases = {
        r'\bit is important to note that\b': '',
        r'\bit should be noted that\b': '',
        r'\bit is worth noting that\b': '',
        r'\bit is imperative to\b': 'it is essential to',
        r'\bcomprehensive analysis\b': 'detailed examination',
        r'\bcutting-edge technology\b': 'advanced technology'
    }
    
    for phrase, replacement in ai_phrases.items():
        content = re.sub(phrase, replacement, content, flags=re.IGNORECASE)
    
    # Add slight variations to repetitive structures
    if content.count('The process') > 1:
        content = content.replace('The process', 'This method', 1)
    
    if content.count('This technology') > 1:
        content = content.replace('This technology', 'The technique', 1)
    
    # Vary sentence beginnings
    repetitive_starts = [
        ('Laser cleaning', ['This cleaning method', 'The laser process']),
        ('The laser', ['This laser', 'Laser technology']),
        ('Industrial applications', ['Commercial uses', 'Practical applications'])
    ]
    
    for original, alternatives in repetitive_starts:
        if content.count(original) > 1:
            # Replace second occurrence with alternative
            parts = content.split(original, 2)
            if len(parts) >= 3:
                content = parts[0] + original + parts[1] + alternatives[0] + parts[2]
    
    # Add natural flow connectors
    content = re.sub(r'\.\s*Additionally,', '. In addition,', content)
    content = re.sub(r'\.\s*Furthermore,', '. What\'s more,', content)
    
    # Fix overly repetitive technical terms
    if content.count('wavelength') > 3:
        content = content.replace('wavelength', 'laser frequency', 1)
    
    if content.count('efficient') > 2:
        content = content.replace('efficient', 'effective', 1)
    
    return content
