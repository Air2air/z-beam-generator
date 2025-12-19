"""
Author Voice Post-Processor

A discrete, reusable component that enhances text with author voice markers.
Completely decoupled from content generation - operates purely on text + author.

Enhanced with comprehensive validation to:
- Detect non-English content (Indonesian, Italian translations)
- Identify translation artifacts (reduplication patterns)
- Score voice authenticity (0-100)
- Prevent over-adjustment of already-voiced content

Usage:
    from shared.voice.post_processor import VoicePostProcessor
    
    processor = VoicePostProcessor(api_client)
    
    enhanced_text = processor.enhance(
        text="Original text here",
        author={
            'name': 'Todd Dunning',
            'country': 'United States'
        }
    )
"""

import logging
import re
import statistics
from typing import Any, Dict, List

from shared.voice.orchestrator import VoiceOrchestrator

logger = logging.getLogger(__name__)


class VoicePostProcessor:
    """
    Discrete post-processor for enhancing text with author voice markers.
    
    Design Philosophy:
    - Single Responsibility: Only voice enhancement, nothing else
    - Minimal Interface: text + author → enhanced_text
    - No Dependencies: Doesn't know about materials, FAQs, micros, etc.
    - Reusable: Works with any text from any component
    - Configurable: All behavior controlled by caller
    """
    
    def __init__(self, api_client, temperature: float = 0.4):
        """
        Initialize voice post-processor.
        
        Args:
            api_client: API client for text generation (required)
            temperature: Generation temperature (default 0.4 for controlled enhancement)
        """
        if not api_client:
            raise ValueError("API client is required for voice enhancement")
        
        self.api_client = api_client
        self.temperature = temperature
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect if text is in English or another language.
        
        Prevents voice enhancement on non-English content.
        Detects: Indonesian, Italian, Spanish, French, German, Portuguese, Chinese, and more.
        
        Args:
            text: Text content to analyze
            
        Returns:
            {
                'language': str,  # 'english', 'indonesian', 'italian', 'spanish', 'french', etc.
                'confidence': float,  # 0-1
                'indicators': List[str]  # Words that triggered detection
            }
        """
        # Common Indonesian words (high-frequency function words)
        indonesian_indicators = {
            'yang', 'dengan', 'untuk', 'dari', 'ini', 'dapat', 'sangat',
            'pada', 'adalah', 'atau', 'akan', 'juga', 'dalam', 'tidak',
            'memiliki', 'memerlukan', 'menggunakan', 'sebagai', 'karena',
            'ya', 'sekitar', 'proses', 'aplikasi', 'lapisan', 'tanpa',
            'merusak', 'substrat', 'efektif', 'permukaan', 'kecepatan',
            'oksidasi', 'korosi', 'jika', 'melebihi', 'menjadi', 'warna',
            'akibat', 'atur', 'setelah', 'pembersihan', 'aplikasikan',
            'bening', 'mencegah', 'simpan', 'terkontrol', 'rentan',
            'terhadap', 'kelembapan', 'verifikasi', 'optimal', 'dilakukan',
            'melalui', 'inspeksi', 'harus', 'bebas', 'residu', 'tetap'
        }
        
        # Common Italian words
        italian_indicators = {
            'che', 'con', 'per', 'della', 'questo', 'molto', 'alla',
            'essere', 'anche', 'più', 'quando', 'come', 'quindi',
            'infatti', 'pertanto', 'mediante', 'verso', 'nella', 'degli',
            'sono', 'hanno', 'stato', 'dopo', 'mentre', 'prima'
        }
        
        # Common Spanish words
        spanish_indicators = {
            'que', 'con', 'para', 'por', 'esto', 'muy', 'como',
            'cuando', 'donde', 'quien', 'cual', 'también', 'después',
            'antes', 'durante', 'mediante', 'hasta', 'desde', 'está',
            'son', 'han', 'sido', 'hace', 'hacer', 'puede', 'sin'
        }
        
        # Common French words
        french_indicators = {
            'que', 'avec', 'pour', 'dans', 'sur', 'est', 'sont',
            'ont', 'cette', 'ces', 'aussi', 'très', 'mais', 'comme',
            'quand', 'où', 'qui', 'peut', 'faire', 'après', 'avant',
            'pendant', 'sans', 'sous', 'depuis', 'été', 'être'
        }
        
        # Common German words
        german_indicators = {
            'und', 'mit', 'für', 'von', 'auf', 'ist', 'sind',
            'hat', 'haben', 'wird', 'werden', 'kann', 'muss',
            'soll', 'dieser', 'diese', 'aber', 'oder', 'wenn',
            'wann', 'wie', 'was', 'sehr', 'auch', 'nach', 'bei'
        }
        
        # Common Portuguese words
        portuguese_indicators = {
            'que', 'com', 'para', 'por', 'este', 'esta', 'muito',
            'quando', 'onde', 'como', 'também', 'depois', 'antes',
            'durante', 'mediante', 'até', 'desde', 'está', 'são',
            'tem', 'têm', 'sido', 'fazer', 'pode', 'sem', 'sobre'
        }
        
        # Common Chinese characters (simplified)
        chinese_chars = set('的一是在了不和有我这个们中来上大为国地到以说时要就出会可也你他们她它')
        
        text_lower = text.lower()
        words = set(text_lower.split())
        
        # Count language-specific words
        indonesian_matches = words & indonesian_indicators
        italian_matches = words & italian_indicators
        spanish_matches = words & spanish_indicators
        french_matches = words & french_indicators
        german_matches = words & german_indicators
        portuguese_matches = words & portuguese_indicators
        chinese_char_matches = set(text) & chinese_chars
        
        # Calculate match counts
        indonesian_count = len(indonesian_matches)
        italian_count = len(italian_matches)
        spanish_count = len(spanish_matches)
        french_count = len(french_matches)
        german_count = len(german_matches)
        portuguese_count = len(portuguese_matches)
        chinese_count = len(chinese_char_matches)
        
        # Determine language (prioritize by match count, threshold = 3 matches)
        language_matches = [
            (indonesian_count, 'indonesian', indonesian_matches),
            (italian_count, 'italian', italian_matches),
            (spanish_count, 'spanish', spanish_matches),
            (french_count, 'french', french_matches),
            (german_count, 'german', german_matches),
            (portuguese_count, 'portuguese', portuguese_matches),
            (chinese_count, 'chinese', chinese_char_matches)
        ]
        
        # Sort by count (highest first)
        language_matches.sort(reverse=True, key=lambda x: x[0])
        
        # If top match has >= 3 indicators, it's that language
        if language_matches[0][0] >= 3:
            count, lang, matches = language_matches[0]
            return {
                'language': lang,
                'confidence': min(count / 10.0, 1.0),
                'indicators': list(matches)[:5]
            }
        
        # Check for high proportion of non-ASCII chars (not just scientific symbols)
        # Allow some non-ASCII for scientific notation (μ, °, ², etc.)
        non_ascii_count = sum(1 for c in text if ord(c) > 127 and c not in 'μ°²³¹⁰⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉±×÷≤≥≈')
        total_chars = len(text)
        if total_chars > 0 and (non_ascii_count / total_chars) > 0.15:
            # More than 15% non-ASCII (excluding scientific symbols) suggests non-English language
            return {
                'language': 'unknown_non_english',
                'confidence': 0.7,
                'indicators': ['high-non-ascii-content']
            }
        
        # Check for common English words to confirm it's English
        english_indicators = {
            'the', 'this', 'that', 'these', 'those', 'and', 'or', 'but',
            'for', 'with', 'from', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'under',
            'again', 'further', 'then', 'once', 'here', 'there', 'when',
            'where', 'why', 'how', 'all', 'each', 'other', 'some', 'such'
        }
        
        english_matches = words & english_indicators
        english_count = len(english_matches)
        
        # If we have English indicators and no other language indicators, it's English
        if english_count >= 2:
            return {
                'language': 'english',
                'confidence': 0.9,
                'indicators': []
            }
        
        # Default to English with low confidence (might be technical jargon)
        return {
            'language': 'english',
            'confidence': 0.6,
            'indicators': []
        }
    
    def detect_translation_artifacts(self, text: str) -> Dict[str, Any]:
        """
        Detect translation artifacts that indicate poor voice application.
        
        Problematic patterns:
        - Reduplication: "very-very", "clean-clean", "high-high" (Indonesian-style)
        - Excessive conjunctions: "then...then...then", "so...so...so"
        - Repetitive sentence starters
        
        Args:
            text: Text to analyze
            
        Returns:
            {
                'has_artifacts': bool,
                'artifact_count': int,
                'patterns_found': List[Dict],  # [{type, examples, count}]
                'severity': str  # 'none', 'minor', 'moderate', 'severe'
            }
        """
        artifacts = []
        
        # 1. Detect reduplication patterns (Indonesian-style)
        reduplication = re.findall(r'\b(\w+)-\1\b', text.lower())
        if reduplication:
            artifacts.append({
                'type': 'reduplication',
                'examples': list(set(reduplication))[:5],
                'count': len(reduplication)
            })
        
        # 2. Detect excessive "then" usage
        then_count = len(re.findall(r'\bthen\b', text.lower()))
        sentence_count = len(re.findall(r'[.!?]', text)) or 1
        if then_count / sentence_count > 0.5:  # More than 50% of sentences
            artifacts.append({
                'type': 'excessive_then',
                'examples': [f"{then_count} uses in {sentence_count} sentences"],
                'count': then_count
            })
        
        # 3. Detect excessive "so" usage
        so_count = len(re.findall(r'\bso\b', text.lower()))
        if so_count / sentence_count > 0.5:
            artifacts.append({
                'type': 'excessive_so',
                'examples': [f"{so_count} uses in {sentence_count} sentences"],
                'count': so_count
            })
        
        # 4. Detect repetitive sentence starters
        sentences = re.split(r'[.!?]+', text)
        starters = [s.strip().split()[0].lower() for s in sentences if s.strip() and len(s.strip().split()) > 0]
        
        if len(starters) > 3:
            starter_counts = {}
            for starter in starters:
                starter_counts[starter] = starter_counts.get(starter, 0) + 1
            
            repetitive_starters = [
                starter for starter, count in starter_counts.items()
                if count >= 3
            ]
            
            if repetitive_starters:
                artifacts.append({
                    'type': 'repetitive_starters',
                    'examples': repetitive_starters[:3],
                    'count': len(repetitive_starters)
                })
        
        # Calculate severity
        total_artifacts = sum(a['count'] for a in artifacts)
        if total_artifacts == 0:
            severity = 'none'
        elif total_artifacts <= 2:
            severity = 'minor'
        elif total_artifacts <= 5:
            severity = 'moderate'
        else:
            severity = 'severe'
        
        return {
            'has_artifacts': len(artifacts) > 0,
            'artifact_count': total_artifacts,
            'patterns_found': artifacts,
            'severity': severity
        }
    
    def detect_linguistic_patterns(self, text: str, author: Dict[str, str]) -> Dict[str, Any]:
        """
        Detect deeper linguistic patterns from voice profiles.
        
        Checks country-specific patterns:
        - USA: Phrasal verbs, active voice, American spelling
        - Taiwan: Topic-comment structure, article omissions, systematic markers
        - Italy: Word order inversion, emphatic pronouns, subjunctive influence
        - Indonesia: Demonstrative clusters, serial verbs, paratactic structure
        
        Args:
            text: Text to analyze
            author: Author dict with 'country' key
            
        Returns:
            {
                'pattern_score': float (0-100),
                'patterns_found': List[str],
                'pattern_quality': str,  # 'authentic', 'weak', 'absent'
                'linguistic_issues': List[str]
            }
        """
        country = author.get('country', '').lower()
        text_lower = text.lower()
        patterns_found = []
        issues = []
        score = 50.0  # Start neutral
        
        if 'united states' in country or country == 'usa' or country == 'us':
            # USA patterns: Phrasal verbs, active voice, direct language
            phrasal_verbs = ['set up', 'figure out', 'carry out', 'work out', 'pick up', 'come up with']
            found_phrasal = [pv for pv in phrasal_verbs if pv in text_lower]
            if found_phrasal:
                patterns_found.append(f"phrasal_verbs: {len(found_phrasal)}")
                score += 10
            
            # American spelling
            if 'optimize' in text_lower or 'analyze' in text_lower:
                patterns_found.append("american_spelling")
                score += 5
            
            # Active voice indicators (strong subjects at sentence start)
            active_patterns = ['the process', 'the laser', 'the surface', 'the method', 'this approach']
            found_active = sum(1 for p in active_patterns if p in text_lower)
            if found_active >= 2:
                patterns_found.append("active_voice_structure")
                score += 5
        
        elif 'taiwan' in country:
            # Taiwan patterns: Topic-comment, article omissions, systematic language
            systematic_markers = ['demonstrates', 'reveals', 'indicates', 'establishes', 'systematic', 'precise']
            found_systematic = [m for m in systematic_markers if m in text_lower]
            if found_systematic:
                patterns_found.append(f"systematic_markers: {len(found_systematic)}")
                score += 10
            
            # Topic-comment structure (pronoun after comma)
            if re.search(r',\s*(it|they|this|that)\s+(shows?|demonstrates?|indicates?)', text_lower):
                patterns_found.append("topic_comment_structure")
                score += 10
            
            # Measurement-first phrasing
            if re.search(r'\d+\.?\d*\s*[μm|nm|cm|mm|micrometers?]', text):
                patterns_found.append("measurement_first")
                score += 5
        
        elif 'italy' in country or 'italian' in country:
            # Italy patterns: Word order inversion, emphatic constructions
            emphatic_markers = ['elegant', 'refined', 'remarkable', 'notable', 'exceptional', 'sophisticated']
            found_emphatic = [m for m in emphatic_markers if m in text_lower]
            if found_emphatic:
                patterns_found.append(f"emphatic_style: {len(found_emphatic)}")
                score += 10
            
            # Inverted word order (adjective before noun in unusual positions)
            if re.search(r'\b(remarkable|notable|exceptional)\s+is\s+', text_lower):
                patterns_found.append("word_order_inversion")
                score += 10
            
            # Subjunctive influence ("would seem", "it appears")
            if 'would seem' in text_lower or 'it appears' in text_lower:
                patterns_found.append("subjunctive_influence")
                score += 5
        
        elif 'indonesia' in country:
            # Indonesia patterns: Demonstrative clustering, simple connectors
            demonstratives = ['this process', 'that method', 'this surface', 'that layer', 'this approach']
            found_demo = [d for d in demonstratives if d in text_lower]
            if found_demo:
                patterns_found.append(f"demonstrative_clusters: {len(found_demo)}")
                score += 10
            
            # Simple connectors
            simple_connectors = text_lower.count(' so ') + text_lower.count(' because ')
            if simple_connectors >= 2:
                patterns_found.append("paratactic_connectors")
                score += 5
            
            # Serial verb constructions
            if re.search(r'\b(removes?\s+then\s+\w+|cleans?\s+then\s+\w+)', text_lower):
                patterns_found.append("serial_verb_structure")
                score += 10
        
        # Determine quality
        if score >= 70:
            quality = 'authentic'
        elif score >= 50:
            quality = 'weak'
        else:
            quality = 'absent'
            issues.append("No country-specific linguistic patterns detected")
        
        return {
            'pattern_score': min(100.0, score),
            'patterns_found': patterns_found,
            'pattern_quality': quality,
            'linguistic_issues': issues
        }
    
    def score_voice_authenticity(
        self,
        text: str,
        author: Dict[str, str],
        voice_indicators: list,
        mode: str = 'detection'
    ) -> Dict[str, Any]:
        """
        Score how authentic the voice application is.
        
        Checks for:
        - Language correctness
        - Translation artifacts
        - Voice authenticity scoring
        - Existing marker count
        - Deep linguistic patterns (NEW)
        
        Args:
            text: Text to analyze
            author: Author dict with 'country' key
            voice_indicators: List of expected voice markers for this country
            mode: Scoring mode - 'detection' (strict, for scanning) or 'enhancement' (lenient, for post-AI validation)
            
        Returns:
            {
                'authenticity_score': float (0-100),
                'is_authentic': bool,  # True if score >= 70
                'found_markers': List[str],
                'marker_quality': str,  # 'excellent', 'good', 'fair', 'poor'
                'issues': List[str],
                'recommendation': str,  # 'keep', 'reprocess', 'translate'
                'linguistic_patterns': Dict  # Deep pattern analysis (NEW)
            }
        """
        text_lower = text.lower()
        
        # Start at 100 and deduct for issues
        score = 100.0
        issues = []
        
        # 1. Check language (CRITICAL)
        language = self.detect_language(text)
        if language['language'] != 'english':
            score = 0.0
            issues.append(f"Text is in {language['language']}, not English")
            return {
                'authenticity_score': 0.0,
                'is_authentic': False,
                'found_markers': [],
                'marker_quality': 'poor',
                'issues': issues,
                'recommendation': 'translate'
            }
        
        # 2. Check for translation artifacts (HEAVY PENALTY)
        artifacts = self.detect_translation_artifacts(text)
        if artifacts['has_artifacts']:
            penalty = artifacts['artifact_count'] * 15
            score -= penalty
            artifact_types = ', '.join([a['type'] for a in artifacts['patterns_found']])
            issues.append(
                f"Translation artifacts ({artifacts['severity']}): {artifact_types}"
            )
        
        # 3. Count genuine voice markers
        found_markers = [m for m in voice_indicators if m in text_lower]
        
        # Apply different penalties based on mode
        if mode == 'enhancement':
            # POST-ENHANCEMENT MODE: More lenient - accept 1+ markers as improvement
            if len(found_markers) == 0:
                score -= 50  # Still fail if no markers at all
                issues.append("No voice markers found")
            elif len(found_markers) == 1:
                score -= 15  # Light penalty but passes threshold (score = 85)
                issues.append("Only 1 voice marker (acceptable for short text)")
            elif len(found_markers) >= 2 and len(found_markers) <= 4:
                # Good range - add bonus
                score += 10
            elif len(found_markers) >= 5 and len(found_markers) <= 6:
                # Slightly too many but acceptable
                score -= 5
                issues.append(f"Many markers ({len(found_markers)})")
            elif len(found_markers) > 6:
                # Too many markers - seems forced or double-enhanced
                score -= 15
                issues.append(f"Excessive markers ({len(found_markers)})")
        else:
            # DETECTION MODE: Strict - require 2+ markers for good quality
            if len(found_markers) == 0:
                score -= 50  # Heavy penalty: no markers = not authentic
                issues.append("No voice markers found")
            elif len(found_markers) == 1:
                score -= 35  # Heavy penalty: need at least 2 markers (ensures score <70)
                issues.append("Only 1 voice marker (need 2+)")
            elif len(found_markers) >= 2 and len(found_markers) <= 4:
                # Good range - add bonus
                score += 10
            elif len(found_markers) >= 5 and len(found_markers) <= 6:
                # Slightly too many but acceptable
                score -= 5
                issues.append(f"Many markers ({len(found_markers)})")
            elif len(found_markers) > 6:
                # Too many markers - seems forced or double-enhanced
                score -= 15
                issues.append(f"Excessive markers ({len(found_markers)})")
        
        # 4. Check for marker repetition
        marker_counts = {m: text_lower.count(m) for m in found_markers}
        repeated = [m for m, count in marker_counts.items() if count > 2]
        if repeated:
            score -= len(repeated) * 10
            issues.append(f"Repeated markers: {', '.join(repeated[:3])}")
        
        # 5. Check marker distribution (are they clustered or spread?)
        if found_markers and len(text) > 200:
            positions = []
            for marker in found_markers:
                pos = text_lower.find(marker)
                if pos != -1:
                    positions.append(pos / len(text))  # Normalize to 0-1
            
            if positions and len(positions) > 1:
                try:
                    variance = statistics.variance(positions)
                    if variance < 0.1:  # Markers clustered in one area
                        score -= 10
                        issues.append("Markers clustered (not naturally distributed)")
                except Exception:
                    pass  # Skip if variance calculation fails
        
        # 6. Check deep linguistic patterns (NEW)
        linguistic_patterns = self.detect_linguistic_patterns(text, author)
        
        # Adjust score based on linguistic pattern quality
        if linguistic_patterns['pattern_quality'] == 'authentic':
            score += 10  # Bonus for authentic country-specific patterns
        elif linguistic_patterns['pattern_quality'] == 'absent':
            score -= 10  # Penalty for missing expected patterns
        
        # Add linguistic issues to main issues list
        issues.extend(linguistic_patterns['linguistic_issues'])
        
        # Ensure score stays in range
        score = max(0.0, min(100.0, score))
        
        # Determine quality
        if score >= 85:
            quality = 'excellent'
        elif score >= 70:
            quality = 'good'
        elif score >= 50:
            quality = 'fair'
        else:
            quality = 'poor'
        
        # Determine recommendation
        if score >= 70:
            recommendation = 'keep'
        elif score >= 40:
            recommendation = 'reprocess'
        else:
            recommendation = 'translate'
        
        return {
            'authenticity_score': score,
            'is_authentic': score >= 70,
            'found_markers': found_markers,
            'marker_quality': quality,
            'issues': issues,
            'recommendation': recommendation,
            'linguistic_patterns': linguistic_patterns  # NEW: Deep pattern analysis
        }
    
    def validate_before_enhancement(
        self,
        text: str,
        author: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Comprehensive validation before attempting enhancement.
        
        Determines whether text should be enhanced based on:
        - Language detection (must be English)
        - Translation artifact detection
        - Voice authenticity scoring
        - Existing marker count
        
        Args:
            text: Text to validate
            author: Author dict with 'name' and 'country'
            
        Returns:
            {
                'should_enhance': bool,
                'reason': str,
                'action_required': str,  # 'none', 'enhance', 'reprocess', 'translate'
                'details': Dict  # Full analysis results
            }
        """
        # Validate inputs
        if not text or not text.strip():
            return {
                'should_enhance': False,
                'reason': 'Empty text',
                'action_required': 'none',
                'details': {}
            }
        
        if not author or 'country' not in author:
            return {
                'should_enhance': False,
                'reason': 'Invalid author data',
                'action_required': 'none',
                'details': {}
            }
        
        # Get voice indicators (signature phrases)
        try:
            voice = VoiceOrchestrator(country=author['country'])
            voice_indicators = voice.get_signature_phrases() or []  # Empty list is OK
        except Exception as e:
            logger.error(f"Failed to load voice indicators: {e}")
            return {
                'should_enhance': False,
                'reason': f'Voice system error: {e}',
                'action_required': 'none',
                'details': {}
            }
        
        # Voice indicators are optional - proceed with enhancement even if empty
        # We use the full voice profile (sentence structure, linguistic characteristics)
        # not just signature phrases
        
        # Run comprehensive analysis
        language = self.detect_language(text)
        artifacts = self.detect_translation_artifacts(text)
        authenticity = self.score_voice_authenticity(text, author, voice_indicators)
        
        details = {
            'language': language,
            'artifacts': artifacts,
            'authenticity': authenticity
        }
        
        # Decision logic
        
        # CRITICAL: Wrong language
        if language['language'] != 'english':
            return {
                'should_enhance': False,
                'reason': f"Text is in {language['language']}, needs translation to English",
                'action_required': 'translate',
                'details': details
            }
        
        # HIGH: Severe translation artifacts
        if artifacts['severity'] in ['severe', 'moderate']:
            return {
                'should_enhance': True,
                'reason': f"Translation artifacts detected ({artifacts['severity']}), reprocessing needed",
                'action_required': 'reprocess',
                'details': details
            }
        
        # GOOD: Already authentic
        if authenticity['is_authentic']:
            return {
                'should_enhance': False,
                'reason': f"Voice already authentic (score: {authenticity['authenticity_score']:.1f}/100)",
                'action_required': 'none',
                'details': details
            }
        
        # MEDIUM: Low authenticity score
        if authenticity['authenticity_score'] < 40:
            return {
                'should_enhance': True,
                'reason': f"Low authenticity score ({authenticity['authenticity_score']:.1f}/100)",
                'action_required': 'reprocess',
                'details': details
            }
        
        # DEFAULT: Enhancement needed
        return {
            'should_enhance': True,
            'reason': f"Moderate authenticity ({authenticity['authenticity_score']:.1f}/100), enhancement recommended",
            'action_required': 'enhance',
            'details': details
        }
    
    def _regenerate_in_english(self, text: str, author: Dict[str, str]) -> str:
        """
        Regenerate non-English text in English using AI.
        
        This is a FAIL-FAST approach: If text is not in English, we regenerate it
        entirely using AI rather than attempting translation. This ensures:
        1. Content is factually accurate (not mistranslated)
        2. Text flows naturally in English
        3. Technical terminology is correct
        
        Args:
            text: Non-English text to regenerate
            author: Author dict with country info (for context)
            
        Returns:
            Regenerated English text
            
        Raises:
            ValueError: If regeneration fails
        """
        prompt = f"""The following text was written in a non-English language, but must be in English.
Regenerate this text in clear, professional English while preserving the technical accuracy and meaning.

CRITICAL REQUIREMENTS:
- Output MUST be in English only
- Preserve all technical details, numbers, and specifications
- Maintain professional technical writing style
- Do NOT include any non-English words or phrases
- Keep similar length to original ({len(text.split())} words)

Original text:
{text}

Regenerated English text:"""

        try:
            response = self.api_client.generate_text(
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=len(text.split()) * 3  # Allow flexibility
            )
            
            if not response or not response.strip():
                raise ValueError("API returned empty response")
            
            # Validate the regenerated text is actually English
            validation = self.detect_language(response)
            if validation['language'] != 'english':
                raise ValueError(
                    f"AI regeneration failed: Output is still in {validation['language']}, not English"
                )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to regenerate text in English: {e}")
            raise ValueError(f"English regeneration failed: {e}")
        
    def enhance(
        self,
        text: str,
        author: Dict[str, str],
        min_markers: int = 2,
        max_markers: int = 3,
        preserve_length: bool = True,
        length_tolerance: int = 5,
        voice_intensity: int = 3
    ) -> str:
        """
        Enhance text with author's voice markers.
        
        Args:
            text: Original text to enhance
            author: Author dictionary with 'name' and 'country' keys
            min_markers: Minimum voice markers to inject (default 2)
            max_markers: Maximum voice markers to inject (default 3)
            preserve_length: Whether to maintain similar word count (default True)
            length_tolerance: Word count tolerance in words (default ±5)
            voice_intensity: Author voice intensity level 1-5 (default 3)
                1 = Minimal voice markers, very subtle
                2 = Light voice presence, natural integration
                3 = Moderate voice, balanced authenticity
                4 = Strong voice, distinctive character
                5 = Maximum voice, highly characteristic
            
        Returns:
            Enhanced text with voice markers, or original if enhancement fails
        """
        # Validate inputs
        if not text or not text.strip():
            logger.warning("Empty text provided - returning unchanged")
            return text
            
        if not author or 'country' not in author:
            logger.warning("Invalid author object - returning text unchanged")
            return text
        
        # 🆕 NEW: Comprehensive pre-enhancement validation
        validation = self.validate_before_enhancement(text, author)
        
        if not validation['should_enhance']:
            logger.info(f"✅ Skipping enhancement: {validation['reason']}")
            return text
        
        if validation['action_required'] == 'translate':
            detected_lang = validation['details']['language']['language']
            logger.warning(
                f"⚠️  Text is in {detected_lang}, not English. "
                f"Regenerating in English using AI..."
            )
            logger.info(f"   Detected words: {', '.join(validation['details']['language']['indicators'][:5])}")
            
            # Regenerate text in English using AI
            try:
                text = self._regenerate_in_english(text, author)
                logger.info("✅ Successfully regenerated text in English")
            except Exception as e:
                logger.error(f"❌ Failed to regenerate text in English: {e}")
                raise ValueError(
                    f"Text is in {detected_lang} and automatic translation failed. "
                    f"Manual intervention required."
                )
        
        if validation['action_required'] == 'reprocess':
            logger.warning(
                f"⚠️  Text has quality issues: {validation['reason']}"
            )
            if validation['details']['artifacts']['has_artifacts']:
                artifacts = validation['details']['artifacts']
                logger.warning(f"   Artifacts: {artifacts['severity']} severity, {artifacts['artifact_count']} issues")
            # Continue with enhancement but log the issues
        
        # Log validation details
        if 'details' in validation and 'authenticity' in validation['details']:
            auth = validation['details']['authenticity']
            logger.info(
                f"Voice authenticity: {auth['authenticity_score']:.1f}/100 ({auth['marker_quality']})"
            )
            if auth['issues']:
                logger.info(f"Issues: {'; '.join(auth['issues'][:3])}")
        
        author_name = author.get('name', 'Unknown')
        author_country = author.get('country', 'Unknown')
        
        # Initialize voice orchestrator for this country
        try:
            voice = VoiceOrchestrator(country=author_country)
        except Exception as e:
            logger.error(f"Failed to initialize VoiceOrchestrator for {author_country}: {e}")
            return text
        
        # Get voice indicators (signature phrases) for this country
        voice_indicators = voice.get_signature_phrases()
        
        if not voice_indicators:
            logger.warning(f"No voice indicators found for {author_country} - returning text unchanged")
            return text
        
        # Build enhancement prompt
        word_count = len(text.split())
        
        # Define voice intensity guidance
        intensity_guidance = {
            1: "Inject voice markers VERY SUBTLY - barely noticeable, natural integration only",
            2: "Use voice markers LIGHTLY - natural and understated, keep professional tone",
            3: "Apply MODERATE voice presence - balanced authenticity without overwhelming content",
            4: "Apply STRONG voice character - distinctive and recognizable author presence",
            5: "Apply MAXIMUM voice intensity - highly characteristic, unmistakable author signature"
        }
        
        voice_guidance = intensity_guidance.get(voice_intensity, intensity_guidance[3])
        
        prompt = f"""You are {author_name} from {author_country}, enhancing a technical text to better reflect your authentic voice.

ORIGINAL TEXT:
{text}

CRITICAL TASK: You MUST incorporate AT LEAST {min_markers} different voice markers from YOUR marker list below. This is MANDATORY.

YOUR VOICE MARKERS ({author_country}): {', '.join(voice_indicators[:15])}

VOICE INTENSITY LEVEL {voice_intensity}/5:
{voice_guidance}

🚫 CRITICAL REPETITION RULES:
1. **AVOID OVERUSING** any single voice marker - use each marker at most ONCE
2. **VARY YOUR PHRASING** - don't repeat the same phrases or sentence structures
3. **DISTRIBUTE MARKERS** naturally throughout the text, not clustered
4. **LIMIT MARKER FREQUENCY** - if text has 7+ items, a marker appearing in 60%+ is excessive
5. **PRIORITIZE VARIATION** over voice intensity - better to use fewer markers with variety

MANDATORY REQUIREMENTS:
1. {"Maintain similar length (" + str(word_count) + " words ±" + str(length_tolerance) + ")" if preserve_length else "Adjust length as needed"}
2. **YOU MUST USE AT LEAST {min_markers} DIFFERENT MARKERS** from your list (use each only once)
3. **ANSWER IN ENGLISH ONLY** - regardless of your country
4. Maintain the same technical depth and accuracy as the original
5. **VARY your sentence openings and structures** for uniqueness

⚠️ CRITICAL: If you don't include at least {min_markers} markers, your enhancement will be REJECTED.

Write the enhanced text now (remember: AT LEAST {min_markers} markers required):"""
        
        system_prompt = f"You are {author_name}, a technical expert from {author_country}. Enhance text to reflect your authentic voice. Always write in English."
        
        try:
            # Calculate max_tokens based on text length
            max_tokens = int(word_count * 2) if preserve_length else int(word_count * 3)
            
            # Make API call
            response = self.api_client.generate_simple(
                prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=self.temperature
            )
            
            if not response.success:
                logger.warning(f"Voice enhancement API call failed: {response.error}")
                return text
            
            enhanced = response.content.strip()
            
            # Remove "ENHANCED TEXT" prefix if present (artifact from prompt)
            # Handle various formats: with/without newlines, different spacing
            import re
            enhanced = re.sub(
                r'^ENHANCED TEXT\s*\(incorporating your [^)]+\)\s*:?\s*\n?\s*',
                '',
                enhanced,
                flags=re.IGNORECASE
            ).strip()
            
            # Remove leading slashes and extra line breaks
            enhanced = re.sub(r'^\s*/+\s*', '', enhanced)  # Remove leading slashes
            enhanced = re.sub(r'\n{3,}', '\n\n', enhanced)  # Normalize multiple line breaks to max 2
            enhanced = enhanced.strip()
            
            # Verify enhancement actually added voice markers
            enhanced_lower = enhanced.lower()
            new_markers = [ind for ind in voice_indicators if ind in enhanced_lower]
            
            # Get original marker count from validation details if available
            original_marker_count = 0
            if validation and 'details' in validation and 'authenticity' in validation['details']:
                original_marker_count = len(validation['details']['authenticity'].get('found_markers', []))
            
            # 🆕 POST-ENHANCEMENT QUALITY VALIDATION
            # Check if enhanced text meets quality standards (no excessive duplication)
            # Use 'enhancement' mode for more lenient scoring (accepts 1+ markers)
            quality_check = self.score_voice_authenticity(
                enhanced, author, voice_indicators, mode='enhancement'
            )
            
            quality_score = quality_check['authenticity_score']
            quality_issues = quality_check.get('issues', [])
            
            # Quality threshold: minimum 70 points
            # This catches: repeated markers, excessive markers, clustering, etc.
            if quality_score < 70:
                logger.warning(
                    f"🚨 POST-ENHANCEMENT QUALITY CHECK FAILED: {quality_score:.1f}/100"
                )
                logger.warning("   Issues detected:")
                for issue in quality_issues[:5]:  # Show top 5 issues
                    logger.warning(f"   - {issue}")
                logger.warning("   ⚠️  Rejecting enhanced text due to quality violations")
                logger.warning("   ✅ Keeping original text instead")
                return text
            
            if len(new_markers) > original_marker_count:
                logger.info(f"✅ Voice enhanced: {original_marker_count} → {len(new_markers)} markers")
                logger.info(f"✅ Quality score: {quality_score:.1f}/100 ({quality_check['marker_quality']})")
                return enhanced
            else:
                logger.warning("⚠️  Enhancement didn't add markers - keeping original")
                return text
                
        except Exception as e:
            logger.warning(f"Voice enhancement error: {e} - keeping original")
            return text
    
    def get_voice_score(self, text: str, author: Dict[str, str]) -> Dict:
        """
        Analyze text for voice marker presence AND authenticity.
        
        Enhanced to include language detection, artifact detection, and quality scoring.
        
        Args:
            text: Text to analyze
            author: Author dictionary with 'country' key
            
        Returns:
            Dictionary with comprehensive analysis:
            {
                'marker_count': int,
                'markers_found': [str],
                'country': str,
                'score': float (0-100),  # Simple marker count score
                'authenticity_score': float (0-100),  # Quality-adjusted score
                'authenticity': str,  # 'excellent', 'good', 'fair', 'poor'
                'language': str,  # Detected language
                'artifacts': Dict,  # Translation artifacts
                'recommendation': str  # 'keep', 'enhance', 'reprocess', 'translate'
            }
        """
        if not text or not author or 'country' not in author:
            return {
                'marker_count': 0,
                'markers_found': [],
                'country': 'Unknown',
                'score': 0.0
            }
        
        author_country = author.get('country', 'Unknown')
        
        try:
            voice = VoiceOrchestrator(country=author_country)
            voice_indicators = voice.get_signature_phrases()
            
            text_lower = text.lower()
            found_markers = [ind for ind in voice_indicators if ind in text_lower]
            
            # Calculate score (0-100)
            # 2+ markers = good (70+), 3+ = excellent (85+), 4+ = outstanding (95+)
            marker_count = len(found_markers)
            if marker_count == 0:
                score = 0.0
            elif marker_count == 1:
                score = 50.0
            elif marker_count == 2:
                score = 75.0
            elif marker_count == 3:
                score = 85.0
            elif marker_count == 4:
                score = 95.0
            else:
                score = 100.0
            
            # 🆕 NEW: Run comprehensive authenticity analysis
            language = self.detect_language(text)
            artifacts = self.detect_translation_artifacts(text)
            authenticity_analysis = self.score_voice_authenticity(
                text, author, voice_indicators
            )
            
            return {
                # Existing fields
                'marker_count': marker_count,
                'markers_found': found_markers,
                'country': author_country,
                'score': score,
                # New fields
                'authenticity_score': authenticity_analysis['authenticity_score'],
                'authenticity': authenticity_analysis['marker_quality'],
                'language': language['language'],
                'artifacts': artifacts,
                'recommendation': authenticity_analysis['recommendation']
            }
            
        except Exception as e:
            logger.warning(f"Voice score analysis error: {e}")
            return {
                'marker_count': 0,
                'markers_found': [],
                'country': author_country,
                'score': 0.0,
                'authenticity_score': 0.0,
                'authenticity': 'poor',
                'language': 'unknown',
                'artifacts': {},
                'recommendation': 'none'
            }
    
    def enhance_batch(
        self,
        faq_items: list,
        author: Dict[str, str],
        marker_distribution: str = 'varied',
        preserve_length: bool = True,
        length_tolerance: int = 5,
        voice_intensity: int = 2
    ) -> list:
        """
        Enhance multiple FAQ answers with distributed voice markers.
        
        This method enhances ALL answers in a single API call with global context,
        preventing marker repetition across answers.
        
        Args:
            faq_items: List of FAQ dicts with 'question' and 'answer' keys
            author: Author dictionary with 'name' and 'country' keys
            marker_distribution: Distribution strategy (default 'varied')
                - 'varied': Different markers per answer (recommended)
                - 'balanced': Each marker used approximately once
                - 'sparse': Some answers get no markers (max variation)
            preserve_length: Maintain similar word count per answer
            length_tolerance: Word count tolerance in words (default ±5)
            voice_intensity: Author voice intensity level 1-5 (default 2)
        
        Returns:
            Enhanced FAQ items with distributed voice markers
        """
        # Validate inputs
        if not faq_items:
            logger.warning("Empty FAQ items list - returning unchanged")
            return faq_items
        
        if not author or 'country' not in author:
            logger.warning("Invalid author object - returning FAQ items unchanged")
            return faq_items
        
        author_name = author.get('name', 'Unknown')
        author_country = author.get('country', 'Unknown')
        
        # Initialize voice orchestrator
        try:
            voice = VoiceOrchestrator(country=author_country)
        except Exception as e:
            logger.error(f"Failed to initialize VoiceOrchestrator for {author_country}: {e}")
            return faq_items
        
        # Get voice indicators (signature phrases) for this country
        voice_indicators = voice.get_signature_phrases()
        
        if not voice_indicators:
            logger.warning(f"No voice indicators found for {author_country} - returning unchanged")
            return faq_items
        
        # Build batch prompt
        num_answers = len(faq_items)
        num_markers = len(voice_indicators[:10])  # Use top 10 markers
        
        # Format FAQ items for prompt
        faq_text = ""
        for i, item in enumerate(faq_items, 1):
            faq_text += f"\n{i}. Q: {item['question']}\n"
            faq_text += f"   A: {item['answer']}\n"
        
        # Define intensity guidance
        intensity_guidance = {
            1: "MINIMAL voice markers - barely noticeable, use sparingly",
            2: "LIGHT voice presence - natural and understated",
            3: "MODERATE voice - balanced authenticity",
            4: "STRONG voice - distinctive character",
            5: "MAXIMUM voice - highly characteristic"
        }
        
        voice_guidance = intensity_guidance.get(voice_intensity, intensity_guidance[2])
        
        prompt = f"""You are {author_name} from {author_country}, enhancing {num_answers} FAQ answers with your voice.

YOUR VOICE MARKERS ({author_country}): {', '.join(voice_indicators[:10])}

VOICE INTENSITY LEVEL {voice_intensity}/5:
{voice_guidance}

🚫 CRITICAL DISTRIBUTION RULES (MUST FOLLOW):
1. **USE EACH MARKER AT MOST ONCE** across all {num_answers} answers
2. **DISTRIBUTE MARKERS** - spread them across different answers, not clustered
3. **VARY YOUR PHRASING** - don't repeat sentence structures
4. **AIM FOR BALANCE** - with {num_answers} answers and {num_markers} markers, use each marker 0-1 times
5. **SOME ANSWERS WITHOUT MARKERS** - it's OK if 2-3 answers have zero markers for variety
6. **AVOID REPETITION** - if a marker appears in 60%+ of answers, that's EXCESSIVE

DISTRIBUTION STRATEGY: {marker_distribution}

REQUIREMENTS:
1. {"Maintain similar length per answer (±" + str(length_tolerance) + " words)" if preserve_length else "Adjust length as needed"}
2. **ANSWER IN ENGLISH ONLY** - regardless of your country
3. Maintain technical depth and accuracy
4. Return answers in the EXACT same order
5. Use JSON format with question/answer pairs

FAQ ANSWERS TO ENHANCE:
{faq_text}

Return enhanced FAQ items as JSON array with this structure:
[
  {{"question": "...", "answer": "enhanced answer here"}},
  {{"question": "...", "answer": "enhanced answer here"}},
  ...
]

Generate the enhanced FAQ array now:"""
        
        try:
            # Single API call for all answers
            logger.info(f"🎭 Batch enhancing {num_answers} FAQ answers with {author_country} voice...")
            response = self.api_client.generate_simple(
                prompt,
                max_tokens=6000,  # Larger for batch
                temperature=self.temperature
            )
            
            if not response.success:
                logger.warning(f"Batch voice enhancement API call failed: {response.error}")
                return faq_items
            
            # Parse response
            import json
            import re
            
            content = response.content.strip()
            
            # Extract JSON array from response
            if '```' in content:
                json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
            
            enhanced_items = json.loads(content)
            
            # Validate we got the right number of items
            if len(enhanced_items) != len(faq_items):
                logger.warning(f"Batch enhancement returned {len(enhanced_items)} items, expected {len(faq_items)} - using original")
                return faq_items
            
            # Verify enhancement added markers and didn't over-repeat
            all_answers_text = ' '.join([item['answer'].lower() for item in enhanced_items])
            markers_used = [m for m in voice_indicators if m in all_answers_text]
            
            # Check for over-repetition
            excessive_markers = []
            for marker in markers_used:
                marker_count = sum(1 for item in enhanced_items if marker in item['answer'].lower())
                percentage = (marker_count / num_answers) * 100
                if percentage > 60:
                    excessive_markers.append(f"{marker}({percentage:.0f}%)")
            
            if excessive_markers:
                logger.warning(f"⚠️  Excessive marker repetition detected: {', '.join(excessive_markers)}")
            
            logger.info(f"✅ Batch enhanced: {len(markers_used)} unique markers distributed across {num_answers} answers")
            if excessive_markers:
                logger.warning(f"   ⚠️  BUT {len(excessive_markers)} markers exceed 60% threshold")
            
            return enhanced_items
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse batch enhancement JSON: {e}")
            return faq_items
        except Exception as e:
            logger.error(f"Batch voice enhancement error: {e}")
            return faq_items
    
    def transform_subtitle_structure(
        self,
        subtitle: str,
        material_name: str,
        max_attempts: int = 3
    ) -> Dict[str, Any]:
        """
        Transform subtitle structure for AI detection avoidance.
        
        Applies structural variation patterns programmatically:
        - Varies sentence starters (verb-first, material-first, property-first)
        - Rotates connectors (without, during, via, through, in, with)
        - Changes voice (active/passive)
        - Maintains word count and meaning
        
        Args:
            subtitle: Original subtitle text
            material_name: Material name for context
            max_attempts: Maximum transformation attempts (default 3)
            
        Returns:
            {
                'success': bool,
                'content': str,  # Transformed subtitle
                'attempts': int,
                'ai_score': float,
                'quality_score': float,
                'transformation': str  # Pattern used
            }
        """
        from shared.voice.ai_detection import AIDetector
        
        detector = AIDetector()
        
        # Check original AI score
        original_check = detector.detect_ai_patterns(subtitle)
        
        # Structural transformation templates
        patterns = [
            "verb_material_connector",  # "Preserve [material]'s [property] without [risk]"
            "material_verb_property",    # "[Material] maintains [property] during cleaning"
            "property_preserved_via",    # "[Property] preserved via precise laser control"
            "connector_first",           # "Without damage, restore [material]'s [property]"
            "gerund_focus",              # "Restoring [material] integrity through laser precision"
        ]
        
        for attempt in range(max_attempts):
            pattern = patterns[attempt % len(patterns)]
            
            logger.info(f"🔄 Subtitle transformation attempt {attempt + 1}/{max_attempts} using pattern: {pattern}")
            
            # Build transformation prompt
            prompt = f"""Transform this subtitle using the "{pattern}" pattern while preserving meaning and word count:

Original: "{subtitle}"
Material: {material_name}

Transformation patterns:
- verb_material_connector: "[Verb] [material]'s [property] [connector] [benefit/risk]"
- material_verb_property: "[Material] [verb] [property] [connector] [context]"
- property_preserved_via: "[Property] preserved/maintained via [method]"
- connector_first: "[Connector] [risk/damage], [verb] [material]'s [property]"
- gerund_focus: "[Gerund] [material] [property] through [method]"

Requirements:
- Use pattern: {pattern}
- Same word count (±1 word): {len(subtitle.split())} words
- Preserve core meaning
- Professional tone
- No period at end

Generate transformed subtitle:"""

            from generation.config.dynamic_config import DynamicConfig
            dynamic_config = DynamicConfig()
            
            response = self.api_client.generate_simple(
                prompt=prompt,
                system_prompt="You are a text transformation specialist. Transform structure while preserving meaning.",
                temperature=dynamic_config.calculate_temperature('default'),
                max_tokens=50
            )
            
            if not response.success:
                logger.warning(f"Transformation attempt {attempt + 1} API failed")
                continue
            
            transformed = response.content.strip().strip('"\'')
            
            # Validate
            word_count = len(transformed.split())
            target_count = len(subtitle.split())
            
            if abs(word_count - target_count) > 2:
                logger.warning(f"❌ Word count off: {word_count} vs {target_count} target")
                continue
            
            # Check AI score
            ai_check = detector.detect_ai_patterns(transformed)
            
            logger.info(f"   AI score: {ai_check['ai_score']:.1f} (original: {original_check['ai_score']:.1f})")
            
            # Success if AI score improved or acceptable
            if ai_check['ai_score'] < original_check['ai_score'] or ai_check['ai_score'] < 40:
                return {
                    'success': True,
                    'content': transformed,
                    'attempts': attempt + 1,
                    'ai_score': ai_check['ai_score'],
                    'quality_score': 100 - ai_check['ai_score'],  # Inverse
                    'transformation': pattern,
                    'original_ai_score': original_check['ai_score']
                }
        
        # If all attempts fail, return original
        logger.warning(f"⚠️  All {max_attempts} transformation attempts failed, using original")
        return {
            'success': False,
            'content': subtitle,
            'attempts': max_attempts,
            'ai_score': original_check['ai_score'],
            'quality_score': 100 - original_check['ai_score'],
            'transformation': 'none',
            'original_ai_score': original_check['ai_score']
        }
