#!/usr/bin/env python3
"""
Content Component Validator

Component-specific validation logic for content components.
Validates technical accuracy, structure, and quality of generated laser cleaning content.
"""

from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


def validate_content_format(content: str, format_rules: Dict[str, Any] = None) -> List[str]:
    """
    Validate content-specific format requirements.
    
    Args:
        content: The content to validate
        format_rules: Optional format rules dictionary
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not content or not content.strip():
        errors.append("Content component cannot be empty")
        return errors
    
    content = content.strip()
    
    # Check minimum length
    if len(content) < 500:
        errors.append(f"Content too short ({len(content)} chars, minimum 500)")
    
    # Check maximum length
    if len(content) > 5000:
        errors.append(f"Content too long ({len(content)} chars, maximum 5000)")
    
    # Check for proper paragraph structure
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    if len(paragraphs) < 3:
        errors.append(f"Content needs better structure (found {len(paragraphs)} paragraphs, minimum 3)")
    
    # Check for proper sentence structure
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) < 10:
        errors.append(f"Content needs more detail (found {len(sentences)} sentences, minimum 10)")
    
    # Check for overly long sentences
    long_sentences = [s for s in sentences if len(s) > 200]
    if long_sentences:
        errors.append(f"Found {len(long_sentences)} overly long sentences (>200 chars)")
    
    return errors


def validate_content_technical(content: str, material_data: Dict[str, Any] = None) -> List[str]:
    """
    Validate technical content requirements for laser cleaning.
    
    Args:
        content: The content to validate
        material_data: Material data for context-specific validation
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Required technical terms for laser cleaning content
    required_terms = [
        r'laser\s*cleaning',
        r'wavelength',
        r'pulse\s*duration',
        r'(fiber|nd:yag|diode)\s*laser',
        r'(surface|material)\s*(contamination|cleaning)',
        r'(industrial|manufacturing)\s*application'
    ]
    
    content_lower = content.lower()
    missing_terms = []
    
    for term_pattern in required_terms:
        if not re.search(term_pattern, content_lower):
            missing_terms.append(term_pattern.replace(r'\s*', ' ').replace(r'(', '').replace(r')', ''))
    
    if missing_terms:
        errors.append(f"Missing required technical terms: {', '.join(missing_terms)}")
    
    # Check for specific technical parameters
    technical_params = [
        r'1064\s*nm',  # Common laser wavelength
        r'nanosecond',  # Pulse duration
        r'class\s*4',   # Laser safety
        r'power\s*density',
        r'absorption\s*(coefficient|characteristic)'
    ]
    
    found_params = sum(1 for param in technical_params if re.search(param, content_lower))
    if found_params < 2:
        errors.append("Content should include more specific technical parameters (wavelength, pulse duration, power, etc.)")
    
    # Material-specific validation
    if material_data:
        material_name = material_data.get('name', '').lower()
        if material_name and material_name not in content_lower:
            errors.append(f"Content should specifically mention the material: {material_name}")
        
        material_formula = material_data.get('chemical_formula', '').lower()
        if material_formula and len(material_formula) > 2 and material_formula not in content_lower:
            errors.append(f"Content should include material formula: {material_formula}")
    
    return errors


def validate_content_structure(content: str) -> List[str]:
    """
    Validate content structure and organization requirements.
    
    Args:
        content: The content to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check for placeholder content
    placeholders = ['TBD', 'TODO', '[INSERT', '[PLACEHOLDER', 'XXXX', '...']
    found_placeholders = [p for p in placeholders if p in content.upper()]
    if found_placeholders:
        errors.append(f"Contains placeholder content: {', '.join(found_placeholders)}")
    
    # Check for proper introduction
    first_paragraph = content.split('\n\n')[0] if '\n\n' in content else content[:200]
    if not any(term in first_paragraph.lower() for term in ['laser cleaning', 'material', 'surface']):
        errors.append("Introduction should establish laser cleaning context")
    
    # Check for applications section
    if not re.search(r'application|use|industry|manufacturing', content.lower()):
        errors.append("Content should include practical applications")
    
    # Check for safety considerations
    if not re.search(r'safety|protection|hazard|precaution', content.lower()):
        errors.append("Content should address safety considerations")
    
    # Check for advantages/benefits
    if not re.search(r'advantage|benefit|superior|efficient|effective', content.lower()):
        errors.append("Content should highlight laser cleaning advantages")
    
    return errors


def validate_content_quality(content: str) -> List[str]:
    """
    Validate content quality and readability requirements.
    
    Args:
        content: The content to validate
        
    Returns:
        List of validation warnings (empty if acceptable)
    """
    warnings = []
    
    # Check for repetitive language
    words = re.findall(r'\b\w+\b', content.lower())
    if len(words) > 0:
        unique_words = len(set(words))
        word_variety = unique_words / len(words)
        if word_variety < 0.3:
            warnings.append(f"Limited vocabulary variety ({word_variety:.1%})")
    
    # Check for technical depth
    technical_indicators = ['parameter', 'specification', 'efficiency', 'wavelength', 'pulse', 'density', 'absorption']
    technical_count = sum(1 for indicator in technical_indicators if indicator in content.lower())
    if technical_count < 3:
        warnings.append("Content could include more technical detail")
    
    # Check for balanced sentence lengths
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    if sentences:
        avg_length = sum(len(s) for s in sentences) / len(sentences)
        if avg_length < 60:
            warnings.append("Sentences could be more detailed (average length low)")
        elif avg_length > 120:
            warnings.append("Sentences could be more concise (average length high)")
    
    # Check for passive voice overuse
    passive_patterns = [r'is\s+\w+ed', r'are\s+\w+ed', r'was\s+\w+ed', r'were\s+\w+ed', r'been\s+\w+ed']
    passive_count = sum(len(re.findall(pattern, content.lower())) for pattern in passive_patterns)
    total_sentences = len(sentences)
    if total_sentences > 0 and passive_count / total_sentences > 0.3:
        warnings.append("Consider reducing passive voice usage")
    
    return warnings


def validate_human_writing_score(content: str, author_info: Dict[str, Any] = None) -> List[str]:
    """
    Validate content for human-like writing characteristics and believability.
    
    Args:
        content: The content to validate
        author_info: Author information for context
        
    Returns:
        List of validation errors (empty if acceptable)
    """
    errors = []
    
    # Check for AI-generated content markers
    ai_markers = [
        r'as an ai\b',
        r'i cannot\b',
        r'i am unable\b',
        r'it is important to note\b',
        r'it should be noted\b',
        r'furthermore\b.*furthermore\b',  # Repetitive transitions
        r'in conclusion\b.*in summary\b',  # Multiple conclusions
        r'comprehensive\s+analysis\b',
        r'cutting-edge\s+technology\b',
        r'state-of-the-art\b.*state-of-the-art\b'  # Repetitive buzzwords
    ]
    
    content_lower = content.lower()
    found_markers = []
    for marker in ai_markers:
        if re.search(marker, content_lower):
            found_markers.append(marker.replace(r'\b', '').replace(r'.*', ' + '))
    
    if found_markers:
        errors.append(f"Content contains AI-generated markers: {', '.join(found_markers[:3])}")
    
    # Check for unnatural repetition patterns
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Look for repetitive sentence structures
    sentence_starts = [s.split()[:3] for s in sentences if len(s.split()) >= 3]
    start_patterns = [' '.join(start) for start in sentence_starts]
    repeated_starts = [pattern for pattern in set(start_patterns) if start_patterns.count(pattern) > 2]
    
    if repeated_starts:
        errors.append(f"Repetitive sentence structures detected: {', '.join(repeated_starts[:2])}")
    
    # Check for overly formal or academic tone inconsistent with technical writing
    overly_formal = [
        r'it is imperative\b',
        r'it is paramount\b',
        r'it is incumbent upon\b',
        r'one must consider\b',
        r'it behoves\b',
        r'notwithstanding\b'
    ]
    
    formal_count = sum(1 for pattern in overly_formal if re.search(pattern, content_lower))
    if formal_count > 1:
        errors.append("Overly formal tone - use more natural technical language")
    
    # Check for human variability in word choice
    technical_synonyms = {
        'effective': ['efficient', 'successful', 'optimal'],
        'process': ['procedure', 'method', 'technique'],
        'material': ['substance', 'element', 'compound'],
        'equipment': ['apparatus', 'system', 'device']
    }
    
    synonym_variety = 0
    for base_word, synonyms in technical_synonyms.items():
        if base_word in content_lower:
            synonym_usage = sum(1 for syn in synonyms if syn in content_lower)
            if synonym_usage > 0:
                synonym_variety += 1
    
    if synonym_variety < 2:
        errors.append("Limited vocabulary variation - consider using more diverse terminology")
    
    return errors


def validate_author_country_style(content: str, author_info: Dict[str, Any] = None) -> List[str]:
    """
    Validate content adherence to author's country-specific writing style.
    
    Args:
        content: The content to validate
        author_info: Author information including country
        
    Returns:
        List of validation errors (empty if acceptable)
    """
    errors = []
    
    if not author_info or 'country' not in author_info:
        return errors
    
    country = author_info['country'].lower()
    content_lower = content.lower()
    
    # Country-specific style patterns
    if country in ['uk', 'united kingdom', 'britain', 'england']:
        # British English patterns
        us_spellings = [
            (r'\bcolor\b', 'colour'), (r'\bhonor\b', 'honour'),
            (r'\blabor\b', 'labour'), (r'\bfavor\b', 'favour'),
            (r'\bcenter\b', 'centre'), (r'\bmeter\b', 'metre'),
            (r'\bliter\b', 'litre'), (r'\bfiber\b', 'fibre'),
            (r'\banalyze\b', 'analyse'), (r'\brealize\b', 'realise')
        ]
        
        found_us = []
        for us_pattern, uk_form in us_spellings:
            if re.search(us_pattern, content_lower):
                found_us.append(f"{us_pattern.replace(r'\\b', '')} (should be {uk_form})")
        
        if found_us:
            errors.append(f"Use British English spelling: {', '.join(found_us[:3])}")
        
        # Check for British technical terminology
        if 'aluminium' not in content_lower and 'aluminum' in content_lower:
            errors.append("Use British spelling: 'aluminium' not 'aluminum'")
    
    elif country in ['usa', 'united states', 'america', 'us']:
        # American English patterns
        uk_spellings = [
            (r'\bcolour\b', 'color'), (r'\bhonour\b', 'honor'),
            (r'\blabour\b', 'labor'), (r'\bfavour\b', 'favor'),
            (r'\bcentre\b', 'center'), (r'\bmetre\b', 'meter'),
            (r'\blitre\b', 'liter'), (r'\bfibre\b', 'fiber'),
            (r'\banalyse\b', 'analyze'), (r'\brealise\b', 'realize')
        ]
        
        found_uk = []
        for uk_pattern, us_form in uk_spellings:
            if re.search(uk_pattern, content_lower):
                found_uk.append(f"{uk_pattern.replace(r'\\b', '')} (should be {us_form})")
        
        if found_uk:
            errors.append(f"Use American English spelling: {', '.join(found_uk[:3])}")
        
        # Check for American technical terminology
        if 'aluminum' not in content_lower and 'aluminium' in content_lower:
            errors.append("Use American spelling: 'aluminum' not 'aluminium'")
    
    elif country in ['germany', 'deutschland', 'de']:
        # German technical writing style tends to be more detailed and systematic
        if len(content.split('.')) < 8:
            errors.append("German technical writing typically includes more detailed explanations")
        
        # Check for systematic structure
        if not re.search(r'(firstly|initially|furthermore|moreover|finally)', content_lower):
            errors.append("German technical style benefits from systematic progression indicators")
    
    elif country in ['japan', 'jp']:
        # Japanese technical writing often emphasizes precision and methodology
        precision_terms = ['precise', 'accurate', 'methodology', 'systematic', 'detailed']
        precision_count = sum(1 for term in precision_terms if term in content_lower)
        if precision_count < 2:
            errors.append("Japanese technical writing typically emphasizes precision and methodology")
    
    return errors


def validate_article_variation(content: str, previous_articles: List[str] = None) -> List[str]:
    """
    Validate content for sufficient variation from previous articles.
    
    Args:
        content: The content to validate
        previous_articles: List of previous article contents for comparison
        
    Returns:
        List of validation errors (empty if acceptable)
    """
    errors = []
    
    if not previous_articles:
        return errors
    
    # Check for repetitive introductory patterns
    content_intro = content[:200].lower()
    intro_patterns = [
        r'^laser cleaning represents',
        r'^the process of laser cleaning',
        r'^laser technology provides',
        r'^industrial laser cleaning'
    ]
    
    for article in previous_articles:
        article_intro = article[:200].lower()
        for pattern in intro_patterns:
            if re.search(pattern, content_intro) and re.search(pattern, article_intro):
                errors.append(f"Introduction too similar to previous articles: {pattern.replace('^', '').replace(r'\\b', '')}")
                break
    
    # Check for structural similarity
    content_sentences = re.split(r'[.!?]+', content)
    content_sentences = [s.strip() for s in content_sentences if s.strip()]
    
    for article in previous_articles:
        article_sentences = re.split(r'[.!?]+', article)
        article_sentences = [s.strip() for s in article_sentences if s.strip()]
        
        # Compare sentence structures (first 3 words)
        content_structures = [' '.join(s.split()[:3]).lower() for s in content_sentences if len(s.split()) >= 3]
        article_structures = [' '.join(s.split()[:3]).lower() for s in article_sentences if len(s.split()) >= 3]
        
        common_structures = set(content_structures) & set(article_structures)
        if len(common_structures) > len(content_structures) * 0.3:
            errors.append("Article structure too similar to previous content - vary sentence beginnings")
            break
    
    # Check for unique technical focus
    technical_focuses = {
        'wavelength': r'wavelength|nm|nanometer',
        'pulse': r'pulse\s+duration|nanosecond|femtosecond',
        'power': r'power\s+density|watt|energy',
        'application': r'automotive|aerospace|medical|manufacturing',
        'safety': r'safety|protection|hazard|class\s+4'
    }
    
    content_focuses = []
    for focus, pattern in technical_focuses.items():
        if re.search(pattern, content.lower()):
            content_focuses.append(focus)
    
    # Compare with previous articles
    for article in previous_articles:
        article_focuses = []
        for focus, pattern in technical_focuses.items():
            if re.search(pattern, article.lower()):
                article_focuses.append(focus)
        
        common_focuses = set(content_focuses) & set(article_focuses)
        if len(common_focuses) == len(content_focuses) and len(content_focuses) > 2:
            errors.append("Technical focus identical to previous article - vary emphasis areas")
            break
    
    return errors


def validate_content_comprehensive(content: str, material_data: Dict[str, Any] = None, 
                                 author_info: Dict[str, Any] = None, 
                                 previous_articles: List[str] = None,
                                 format_rules: Dict[str, Any] = None) -> Dict[str, List[str]]:
    """
    Comprehensive content validation using all available validators.
    
    Args:
        content: The content to validate
        material_data: Material data for technical validation
        author_info: Author information for style validation
        previous_articles: Previous articles for variation checking
        format_rules: Format rules for validation
        
    Returns:
        Dict with validation results categorized by type
    """
    results = {
        'format_errors': [],
        'technical_errors': [],
        'structure_errors': [],
        'quality_warnings': [],
        'human_writing_errors': [],
        'country_style_errors': [],
        'variation_errors': []
    }
    
    # Run all validation functions
    results['format_errors'] = validate_content_format(content, format_rules)
    results['technical_errors'] = validate_content_technical(content, material_data)
    results['structure_errors'] = validate_content_structure(content)
    results['quality_warnings'] = validate_content_quality(content)
    results['human_writing_errors'] = validate_human_writing_score(content, author_info)
    results['country_style_errors'] = validate_author_country_style(content, author_info)
    results['variation_errors'] = validate_article_variation(content, previous_articles)
    
    return results


def get_validation_summary(validation_results: Dict[str, List[str]]) -> Dict[str, int]:
    """
    Get a summary of validation results.
    
    Args:
        validation_results: Results from validate_content_comprehensive
        
    Returns:
        Dict with counts of each validation type
    """
    return {
        category: len(errors) 
        for category, errors in validation_results.items()
    }
