#!/usr/bin/env python3
"""
FAQ Output Validation Script

Comprehensive validation for FAQ generation output incorporating all project requirements:
- Word count compliance (20-50 words per answer)
- Technical intensity verification (Level 3: moderate technical terms)
- Voice marker analysis (should be 20-40% usage, not 100%)
- Repetition detection (no phrase >50% usage)
- Sentence structure variation
- Material-specific content verification
- Quality scoring and thresholds

Usage:
    python3 scripts/validation/validate_faq_output.py <material_name>
    python3 scripts/validation/validate_faq_output.py Granite
    python3 scripts/validation/validate_faq_output.py Steel --author alessandro-moretti
"""

import sys
import yaml
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple
import argparse


# ============================================================================
# CONFIGURATION - Match project settings
# ============================================================================

# Word count requirements (from FAQ_WORD_COUNT_RANGE)
MIN_WORDS = 20
MAX_WORDS = 50
TARGET_AVG_WORDS = 35  # Middle of range

# Question count requirements (from FAQ_COUNT_RANGE)
MIN_QUESTIONS = 5
MAX_QUESTIONS = 10

# Technical intensity levels (Level 3 = Moderate)
TECHNICAL_LEVELS = {
    1: {'simple': ['clean', 'remove', 'protect', 'safe', 'better', 'damage']},
    2: {'basic': ['coating', 'surface', 'rust', 'thermal', 'process', 'treatment']},
    3: {'moderate': ['substrate', 'corrosion', 'oxidation', 'ablation', 'contamination', 
                     'metallurgical', 'galvanic', 'oxide', 'thermal', 'mill scale', 'pulsed energy']},
    4: {'advanced': ['Fe₂O₃', 'Cr₂O₃', 'ASTM', 'passivation', 'micron-level', 
                     'yield strength', 'chromium-depleted', 'biotite', 'feldspar']},
    5: {'expert': ['ablation threshold', 'J/cm²', 'nm', 'plasma formation', 
                   'laser-induced breakdown spectroscopy', 'threshold fluence']}
}

# Voice marker thresholds
MAX_SINGLE_MARKER_USAGE = 0.50  # 50% - any marker appearing more than this is over-used
IDEAL_MARKER_RANGE = (0.20, 0.40)  # 20-40% is ideal for primary markers
MAX_PHRASE_REPETITION = 0.50  # 50% - identical phrase in >50% of answers is too much

# Voice profiles by country
VOICE_PROFILES = {
    'Italy': {
        'markers': ['meticulous', 'precision', 'finesse', 'artisan', 'craftsmanship', 
                   'refined', 'elegant', 'delicate', 'excellence', 'preserving', 'integrity'],
        'character': 'Craftsmanship-focused, refined execution'
    },
    'Taiwan': {
        'markers': ['systematic', 'methodology', 'research-based', 'framework', 
                   'comprehensive', 'precise', 'calibration', 'ensures', 'rigorous'],
        'character': 'Research-focused, systematic approach'
    },
    'Indonesia': {
        'markers': ['harmonious', 'balanced', 'thoughtful', 'considerate', 
                   'sustainable', 'mindful', 'respectful', 'careful'],
        'character': 'Balance and sustainability-focused'
    },
    'United States': {
        'markers': ['innovative', 'performance', 'advanced', 'cutting-edge', 
                   'breakthrough', 'optimize', 'maximize', 'superior', 'state-of-the-art'],
        'character': 'Innovation and performance-focused'
    }
}

# Quality thresholds
MIN_QUALITY_SCORE = 70  # Out of 100
FAIL_FAST_ON_CRITICAL = True  # Stop on critical errors


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

class ValidationResult:
    """Container for validation results"""
    def __init__(self, passed: bool, score: int, errors: List[str], warnings: List[str], info: Dict):
        self.passed = passed
        self.score = score
        self.errors = errors
        self.warnings = warnings
        self.info = info


def load_faq_from_frontmatter(material_name: str) -> Tuple[List[Dict], Dict]:
    """Load FAQ from frontmatter file"""
    frontmatter_path = Path(f'content/frontmatter/{material_name.lower()}-laser-cleaning.yaml')
    
    if not frontmatter_path.exists():
        raise FileNotFoundError(f"Frontmatter file not found: {frontmatter_path}")
    
    with open(frontmatter_path, 'r') as f:
        data = yaml.safe_load(f)
    
    questions = data.get('faq', {}).get('questions', [])
    metadata = {
        'material': data.get('material'),
        'subtitle': data.get('subtitle'),
        'generated': data.get('faq', {}).get('generated'),
        'question_count': data.get('faq', {}).get('question_count'),
        'total_words': data.get('faq', {}).get('total_words')
    }
    
    return questions, metadata


def validate_word_counts(questions: List[Dict]) -> Tuple[bool, List[str], List[str], Dict]:
    """Validate word counts per answer"""
    errors = []
    warnings = []
    info = {}
    
    word_counts = []
    for i, q in enumerate(questions, 1):
        answer = q.get('answer', '')
        count = len(answer.split())
        word_counts.append(count)
        
        if count < MIN_WORDS:
            errors.append(f"Q{i}: Too short ({count} words, min {MIN_WORDS})")
        elif count > MAX_WORDS:
            errors.append(f"Q{i}: Too long ({count} words, max {MAX_WORDS})")
    
    avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
    
    info = {
        'word_counts': word_counts,
        'min': min(word_counts) if word_counts else 0,
        'max': max(word_counts) if word_counts else 0,
        'avg': round(avg_words, 1),
        'target': TARGET_AVG_WORDS
    }
    
    if abs(avg_words - TARGET_AVG_WORDS) > 10:
        warnings.append(f"Average word count ({avg_words:.1f}) deviates from target ({TARGET_AVG_WORDS})")
    
    passed = len(errors) == 0
    return passed, errors, warnings, info


def validate_question_count(questions: List[Dict]) -> Tuple[bool, List[str], List[str], Dict]:
    """Validate number of questions"""
    errors = []
    warnings = []
    
    count = len(questions)
    info = {
        'count': count,
        'min': MIN_QUESTIONS,
        'max': MAX_QUESTIONS
    }
    
    if count < MIN_QUESTIONS:
        errors.append(f"Too few questions ({count}, min {MIN_QUESTIONS})")
    elif count > MAX_QUESTIONS:
        errors.append(f"Too many questions ({count}, max {MAX_QUESTIONS})")
    
    passed = len(errors) == 0
    return passed, errors, warnings, info


def validate_technical_intensity(questions: List[Dict], target_level: int = 3) -> Tuple[bool, List[str], List[str], Dict]:
    """Validate technical terminology matches target intensity level"""
    errors = []
    warnings = []
    
    target_terms = TECHNICAL_LEVELS[target_level][list(TECHNICAL_LEVELS[target_level].keys())[0]]
    level_4_terms = TECHNICAL_LEVELS[4]['advanced']
    
    tech_counts = []
    advanced_counts = []
    
    for i, q in enumerate(questions, 1):
        answer = q.get('answer', '').lower()
        
        # Count target level terms
        target_found = [t for t in target_terms if t.lower() in answer]
        tech_counts.append(len(target_found))
        
        # Count overly advanced terms (if target is 3, shouldn't have level 4)
        if target_level < 4:
            advanced_found = [t for t in level_4_terms if t in answer]
            advanced_counts.append(len(advanced_found))
    
    avg_tech = sum(tech_counts) / len(tech_counts) if tech_counts else 0
    avg_advanced = sum(advanced_counts) / len(advanced_counts) if advanced_counts else 0
    
    info = {
        'target_level': target_level,
        'avg_terms_per_answer': round(avg_tech, 1),
        'total_target_terms': sum(tech_counts),
        'total_advanced_terms': sum(advanced_counts)
    }
    
    # Level 3 should have 1-2 moderate terms per answer
    if target_level == 3:
        if avg_tech < 1.0:
            warnings.append(f"Low technical content ({avg_tech:.1f} terms/answer, expected 1-2)")
        if avg_advanced > 0.5:
            warnings.append(f"Too many advanced terms ({avg_advanced:.1f}/answer) for Level {target_level}")
    
    passed = len(errors) == 0
    return passed, errors, warnings, info


def validate_voice_markers(questions: List[Dict], author_country: str = None) -> Tuple[bool, List[str], List[str], Dict]:
    """Validate voice marker usage and repetition"""
    errors = []
    warnings = []
    
    if not author_country or author_country not in VOICE_PROFILES:
        return True, [], ["No voice profile specified - skipping voice validation"], {}
    
    profile = VOICE_PROFILES[author_country]
    markers = profile['markers']
    
    # Count marker occurrences
    marker_counts = {marker: 0 for marker in markers}
    total_answers = len(questions)
    
    for q in questions:
        answer = q.get('answer', '').lower()
        for marker in markers:
            if marker.lower() in answer:
                marker_counts[marker] += 1
    
    # Calculate usage percentages
    marker_usage = {marker: (count / total_answers) for marker, count in marker_counts.items()}
    
    # Check for over-used markers
    over_used = []
    for marker, usage_pct in marker_usage.items():
        if usage_pct > MAX_SINGLE_MARKER_USAGE:
            over_used.append(f"{marker} ({usage_pct*100:.0f}%)")
    
    if over_used:
        errors.append(f"❌ CRITICAL: Over-used voice markers: {', '.join(over_used)}")
        errors.append(f"   Maximum allowed: {MAX_SINGLE_MARKER_USAGE*100:.0f}% per marker")
    
    # Check for under-utilized markers (no variation)
    used_markers = [m for m, pct in marker_usage.items() if pct > 0]
    if len(used_markers) < 3:
        warnings.append(f"Limited marker diversity ({len(used_markers)} different markers used)")
    
    info = {
        'country': author_country,
        'character': profile['character'],
        'marker_usage': {m: f"{pct*100:.0f}%" for m, pct in sorted(marker_usage.items(), key=lambda x: x[1], reverse=True)},
        'over_used': over_used,
        'diversity_score': len(used_markers)
    }
    
    passed = len(errors) == 0
    return passed, errors, warnings, info


def validate_repetition(questions: List[Dict]) -> Tuple[bool, List[str], List[str], Dict]:
    """Detect repetitive phrases and sentence structures"""
    errors = []
    warnings = []
    
    # Track repeated phrases (3+ words)
    phrase_counts = Counter()
    sentence_starts = Counter()
    
    for q in questions:
        answer = q.get('answer', '')
        
        # Track sentence opening (first 3-5 words)
        words = answer.split()
        if len(words) >= 3:
            opening = ' '.join(words[:3])
            sentence_starts[opening.lower()] += 1
        
        # Track common phrases
        for phrase in ['systematic methodology', 'while preserving', 'laser cleaning', 
                       'meticulous precision', 'ensures precise', 'through a']:
            if phrase in answer.lower():
                phrase_counts[phrase] += 1
    
    # Check for over-repeated phrases
    total_answers = len(questions)
    repeated_phrases = []
    
    for phrase, count in phrase_counts.items():
        usage_pct = count / total_answers
        if usage_pct > MAX_PHRASE_REPETITION:
            repeated_phrases.append(f"{phrase} ({count}/{total_answers} = {usage_pct*100:.0f}%)")
    
    if repeated_phrases:
        errors.append(f"❌ CRITICAL: Over-repeated phrases:")
        for phrase in repeated_phrases:
            errors.append(f"   • {phrase}")
    
    # Check for monotonous sentence structures
    repeated_starts = []
    for start, count in sentence_starts.items():
        if count > 2:  # Same opening in >2 answers
            repeated_starts.append(f'"{start}..." ({count} times)')
    
    if repeated_starts:
        warnings.append("Repetitive sentence structures detected:")
        for start in repeated_starts:
            warnings.append(f"   • {start}")
    
    info = {
        'repeated_phrases': dict(phrase_counts),
        'repeated_openings': dict(sentence_starts),
        'unique_sentence_starts': len(sentence_starts),
        'variation_score': len(sentence_starts) / total_answers if total_answers > 0 else 0
    }
    
    passed = len(errors) == 0
    return passed, errors, warnings, info


def validate_material_specificity(questions: List[Dict], material_name: str) -> Tuple[bool, List[str], List[str], Dict]:
    """Ensure questions are material-specific, not generic"""
    errors = []
    warnings = []
    
    material_mentions = 0
    generic_questions = []
    
    for i, q in enumerate(questions, 1):
        question = q.get('question', '')
        answer = q.get('answer', '')
        
        # Check if material name appears in question
        if material_name.lower() in question.lower():
            material_mentions += 1
        else:
            generic_questions.append(f"Q{i}: {question[:60]}...")
    
    material_pct = (material_mentions / len(questions)) * 100 if questions else 0
    
    if material_pct < 70:
        warnings.append(f"Only {material_pct:.0f}% of questions mention '{material_name}' specifically")
        warnings.append("Questions should be material-specific, not generic")
    
    if generic_questions:
        info_msg = f"Generic questions ({len(generic_questions)}):"
        for gq in generic_questions[:3]:  # Show first 3
            warnings.append(f"   {gq}")
    
    info = {
        'material': material_name,
        'material_mentions': material_mentions,
        'total_questions': len(questions),
        'specificity_score': round(material_pct, 1)
    }
    
    passed = len(errors) == 0
    return passed, errors, warnings, info


def calculate_overall_score(validation_results: Dict) -> int:
    """Calculate overall quality score (0-100)"""
    score = 100
    
    # Deduct points for errors and warnings
    for category, result in validation_results.items():
        errors = result.get('errors', [])
        warnings = result.get('warnings', [])
        
        # Critical errors: -20 points each
        score -= len(errors) * 20
        
        # Warnings: -5 points each
        score -= len(warnings) * 5
    
    return max(0, min(100, score))


# ============================================================================
# MAIN VALIDATION
# ============================================================================

def validate_faq_output(material_name: str, author_country: str = None, verbose: bool = True) -> ValidationResult:
    """
    Comprehensive FAQ output validation
    
    Args:
        material_name: Name of the material (e.g., 'Granite', 'Steel')
        author_country: Country of the author (e.g., 'Italy', 'Taiwan')
        verbose: Print detailed output
        
    Returns:
        ValidationResult object with pass/fail, score, and details
    """
    
    if verbose:
        print('=' * 70)
        print(f'FAQ OUTPUT VALIDATION: {material_name}')
        print('=' * 70)
        print()
    
    # Load FAQ
    try:
        questions, metadata = load_faq_from_frontmatter(material_name)
    except Exception as e:
        return ValidationResult(
            passed=False,
            score=0,
            errors=[f"Failed to load FAQ: {str(e)}"],
            warnings=[],
            info={}
        )
    
    if verbose:
        print(f"Material: {metadata['material']}")
        print(f"Questions: {len(questions)}")
        print(f"Generated: {metadata.get('generated', 'Unknown')}")
        if author_country:
            print(f"Author Country: {author_country}")
        print()
    
    # Run all validations
    all_results = {}
    all_errors = []
    all_warnings = []
    
    # 1. Question count
    passed, errors, warnings, info = validate_question_count(questions)
    all_results['question_count'] = {'passed': passed, 'errors': errors, 'warnings': warnings, 'info': info}
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # 2. Word counts
    passed, errors, warnings, info = validate_word_counts(questions)
    all_results['word_counts'] = {'passed': passed, 'errors': errors, 'warnings': warnings, 'info': info}
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # 3. Technical intensity
    passed, errors, warnings, info = validate_technical_intensity(questions, target_level=3)
    all_results['technical_intensity'] = {'passed': passed, 'errors': errors, 'warnings': warnings, 'info': info}
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # 4. Voice markers (if author specified)
    if author_country:
        passed, errors, warnings, info = validate_voice_markers(questions, author_country)
        all_results['voice_markers'] = {'passed': passed, 'errors': errors, 'warnings': warnings, 'info': info}
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    
    # 5. Repetition detection
    passed, errors, warnings, info = validate_repetition(questions)
    all_results['repetition'] = {'passed': passed, 'errors': errors, 'warnings': warnings, 'info': info}
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # 6. Material specificity
    passed, errors, warnings, info = validate_material_specificity(questions, material_name)
    all_results['material_specificity'] = {'passed': passed, 'errors': errors, 'warnings': warnings, 'info': info}
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # Calculate overall score
    overall_score = calculate_overall_score(all_results)
    overall_passed = overall_score >= MIN_QUALITY_SCORE and len(all_errors) == 0
    
    # Print results
    if verbose:
        print('─' * 70)
        print('VALIDATION RESULTS')
        print('─' * 70)
        print()
        
        for category, result in all_results.items():
            status = '✅ PASS' if result['passed'] else '❌ FAIL'
            print(f"{category.replace('_', ' ').title()}: {status}")
            
            if result['errors']:
                for error in result['errors']:
                    print(f"  ❌ {error}")
            
            if result['warnings']:
                for warning in result['warnings']:
                    print(f"  ⚠️  {warning}")
            
            if result['info'] and verbose:
                print(f"  ℹ️  Info: {result['info']}")
            
            print()
        
        print('=' * 70)
        print(f"OVERALL SCORE: {overall_score}/100")
        print(f"RESULT: {'✅ PASSED' if overall_passed else '❌ FAILED'}")
        print('=' * 70)
        
        if not overall_passed:
            print()
            print(f"Minimum score required: {MIN_QUALITY_SCORE}/100")
            print(f"Errors: {len(all_errors)}")
            print(f"Warnings: {len(all_warnings)}")
    
    return ValidationResult(
        passed=overall_passed,
        score=overall_score,
        errors=all_errors,
        warnings=all_warnings,
        info=all_results
    )


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Validate FAQ output quality')
    parser.add_argument('material', help='Material name (e.g., Granite, Steel)')
    parser.add_argument('--author', choices=['Italy', 'Taiwan', 'Indonesia', 'United States'],
                       help='Author country for voice validation')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    parser.add_argument('--fail-fast', action='store_true', help='Exit on first error')
    
    args = parser.parse_args()
    
    result = validate_faq_output(
        material_name=args.material,
        author_country=args.author,
        verbose=not args.quiet
    )
    
    # Exit with appropriate code
    if not result.passed:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
