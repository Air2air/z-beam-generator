#!/usr/bin/env python3
"""
Copilot Quality Grader - Programmatic Interface for Caption Quality Assessment

Provides comprehensive quality scoring and grading for generated captions,
enabling Copilot to read and assess output quality across multiple dimensions.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import re
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class VoiceScore:
    """Voice authenticity scoring results"""
    cultural_markers: int  # 0-100
    linguistic_patterns: int  # 0-100
    vocabulary_authenticity: int  # 0-100
    sentence_structure: int  # 0-100
    overall_authenticity: int  # 0-100
    detected_country: str
    confidence: float  # 0.0-1.0


@dataclass
class AIScore:
    """AI detection avoidance scoring results"""
    formulaic_phrases: int  # 0 = many formulaic, 100 = none
    measurement_naturalness: int  # 0 = perfect decimals, 100 = human ranges
    sentence_variety: int  # 0 = repetitive, 100 = varied
    conversational_elements: int  # 0 = robotic, 100 = conversational
    human_likeness: int  # 0 = obviously AI, 100 = human-like
    detected_issues: List[str]


@dataclass
class TechnicalScore:
    """Technical accuracy scoring results"""
    material_accuracy: int  # 0-100
    cleaning_realism: int  # 0-100
    measurement_plausibility: int  # 0-100
    process_accuracy: int  # 0-100
    overall_technical_quality: int  # 0-100
    technical_issues: List[str]


@dataclass
class StructuralScore:
    """Structural quality scoring results"""
    sentence_count: int
    word_count: int
    sentence_count_compliance: bool
    word_count_compliance: bool
    flow_quality: int  # 0-100
    clarity: int  # 0-100
    overall_structure: int  # 0-100


@dataclass
class CopilotGrade:
    """Complete quality assessment for Copilot consumption"""
    overall_score: int  # 0-100 weighted average
    voice_authenticity: VoiceScore
    ai_detectability: AIScore
    technical_accuracy: TechnicalScore
    structural_quality: StructuralScore
    recommendations: List[str]
    pass_fail_status: str  # "PASS", "FAIL", "NEEDS_IMPROVEMENT"
    production_ready: bool


class VoiceAuthenticityScorer:
    """Scores voice authenticity against country expectations"""
    
    # Country-specific voice markers
    VOICE_MARKERS = {
        'united_states': {
            'cultural': ['bottom line', 'here\'s what', 'key takeaway', 'works out', 'solid performance'],
            'linguistic': ['pretty', 'around', 'roughly', 'about'],
            'vocabulary': ['efficiency', 'results', 'performance', 'optimization', 'productive'],
            'structure_patterns': [r'Here\'s what \w+', r'Bottom line.*', r'The key \w+ is']
        },
        'taiwan': {
            'cultural': ['systematic', 'data suggests', 'analysis shows', 'following our'],
            'linguistic': ['appears to', 'seems to', 'indicates', 'suggests'],
            'vocabulary': ['systematic', 'analysis', 'measurement', 'precision', 'data-driven'],
            'structure_patterns': [r'This \w+ suggests', r'Analysis \w+ that', r'Data indicates']
        },
        'italy': {
            'cultural': ['examining this beautiful', 'one cannot help', 'what strikes me', 'magnificent'],
            'linguistic': ['i must', 'i find', 'it becomes evident', 'captivating'],
            'vocabulary': ['elegant', 'beautiful', 'aesthetic', 'artistry', 'harmony', 'refined'],
            'structure_patterns': [r'I must \w+', r'One cannot help', r'What strikes me']
        },
        'indonesia': {
            'cultural': ['indonesian context', 'our perspective', 'community benefits', 'environmental'],
            'linguistic': ['this material, it', 'these results', 'practical', 'beneficial'],
            'vocabulary': ['sustainable', 'environmental', 'community', 'practical', 'accessible'],
            'structure_patterns': [r'In our \w+ context', r'This \w+, it \w+', r'From.*perspective']
        }
    }
    
    def score_voice_authenticity(self, content: str, expected_country: str) -> VoiceScore:
        """Score voice authenticity against expected country profile"""
        
        content_lower = content.lower()
        expected_markers = self.VOICE_MARKERS.get(expected_country, {})
        
        # Score cultural markers (0-100)
        cultural_markers = self._score_markers(content_lower, expected_markers.get('cultural', []))
        
        # Score linguistic patterns (0-100)
        linguistic_patterns = self._score_markers(content_lower, expected_markers.get('linguistic', []))
        
        # Score vocabulary authenticity (0-100)
        vocabulary_authenticity = self._score_markers(content_lower, expected_markers.get('vocabulary', []))
        
        # Score sentence structure patterns (0-100)
        sentence_structure = self._score_patterns(content, expected_markers.get('structure_patterns', []))
        
        # Detect most likely country
        detected_country, confidence = self._detect_country(content)
        
        # Calculate overall authenticity
        overall_authenticity = int((cultural_markers + linguistic_patterns + vocabulary_authenticity + sentence_structure) / 4)
        
        return VoiceScore(
            cultural_markers=cultural_markers,
            linguistic_patterns=linguistic_patterns,
            vocabulary_authenticity=vocabulary_authenticity,
            sentence_structure=sentence_structure,
            overall_authenticity=overall_authenticity,
            detected_country=detected_country,
            confidence=confidence
        )
    
    def _score_markers(self, content: str, markers: List[str]) -> int:
        """Score presence of specific markers (0-100)"""
        if not markers:
            return 0
        
        found_markers = sum(1 for marker in markers if marker in content)
        score = min(100, (found_markers / len(markers)) * 150)  # Bonus for multiple markers
        return int(score)
    
    def _score_patterns(self, content: str, patterns: List[str]) -> int:
        """Score regex pattern matches (0-100)"""
        if not patterns:
            return 0
        
        found_patterns = sum(1 for pattern in patterns if re.search(pattern, content, re.IGNORECASE))
        score = min(100, (found_patterns / len(patterns)) * 120)
        return int(score)
    
    def _detect_country(self, content: str) -> Tuple[str, float]:
        """Detect most likely country based on voice markers"""
        content_lower = content.lower()
        country_scores = {}
        
        for country, markers in self.VOICE_MARKERS.items():
            score = 0
            total_markers = 0
            
            for category, marker_list in markers.items():
                if category == 'structure_patterns':
                    found = sum(1 for pattern in marker_list if re.search(pattern, content, re.IGNORECASE))
                    score += found
                    total_markers += len(marker_list)
                else:
                    found = sum(1 for marker in marker_list if marker in content_lower)
                    score += found
                    total_markers += len(marker_list)
            
            country_scores[country] = score / max(total_markers, 1)
        
        if not country_scores:
            return "unknown", 0.0
        
        best_country = max(country_scores, key=country_scores.get)
        confidence = country_scores[best_country]
        
        return best_country, confidence


class AIDetectionScorer:
    """Scores AI detectability avoidance"""
    
    # AI detection red flags
    FORMULAIC_PHRASES = [
        'surface analysis reveals',
        'microscopic examination shows',
        'analysis indicates',
        'results demonstrate',
        'examination shows'
    ]
    
    PERFECT_MEASUREMENT_PATTERNS = [
        r'\d+\.\d+ μm',
        r'\d+\.\d+%',
        r'\d+\.\d+ micrometers',
        r'exactly \d+',
        r'precisely \d+'
    ]
    
    CONVERSATIONAL_ELEMENTS = [
        'what i see', 'looking at', 'here\'s what', 'what strikes me',
        'i find', 'seems like', 'appears to be', 'roughly', 'around',
        'about', 'approximately', 'pretty', 'quite'
    ]
    
    def score_ai_detectability(self, content: str) -> AIScore:
        """Score AI detection avoidance (higher = more human-like)"""
        
        content_lower = content.lower()
        
        # Score formulaic phrases (100 = none found, 0 = many found)
        formulaic_count = sum(1 for phrase in self.FORMULAIC_PHRASES if phrase in content_lower)
        formulaic_phrases = max(0, 100 - (formulaic_count * 30))
        
        # Score measurement naturalness (100 = human ranges, 0 = perfect decimals)
        perfect_measurements = sum(1 for pattern in self.PERFECT_MEASUREMENT_PATTERNS 
                                 if re.search(pattern, content))
        measurement_naturalness = max(0, 100 - (perfect_measurements * 25))
        
        # Score sentence variety (0-100)
        sentence_variety = self._score_sentence_variety(content)
        
        # Score conversational elements (0-100)
        conversational_count = sum(1 for element in self.CONVERSATIONAL_ELEMENTS 
                                 if element in content_lower)
        conversational_elements = min(100, conversational_count * 20)
        
        # Calculate overall human-likeness
        human_likeness = int((formulaic_phrases + measurement_naturalness + 
                            sentence_variety + conversational_elements) / 4)
        
        # Detect specific issues
        detected_issues = []
        if formulaic_count > 0:
            detected_issues.append(f"{formulaic_count} formulaic phrases detected")
        if perfect_measurements > 0:
            detected_issues.append(f"{perfect_measurements} perfect measurements detected")
        if conversational_count == 0:
            detected_issues.append("No conversational elements found")
        
        return AIScore(
            formulaic_phrases=formulaic_phrases,
            measurement_naturalness=measurement_naturalness,
            sentence_variety=sentence_variety,
            conversational_elements=conversational_elements,
            human_likeness=human_likeness,
            detected_issues=detected_issues
        )
    
    def _score_sentence_variety(self, content: str) -> int:
        """Score sentence opening variety (0-100)"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        if len(sentences) < 2:
            return 50
        
        # Get first 2-3 words of each sentence
        openings = []
        for sentence in sentences:
            words = sentence.split()
            if len(words) >= 2:
                opening = ' '.join(words[:2]).lower()
                openings.append(opening)
        
        if not openings:
            return 0
        
        # Calculate variety (unique openings / total openings)
        unique_openings = len(set(openings))
        variety_ratio = unique_openings / len(openings)
        
        return int(variety_ratio * 100)


class CopilotQualityGrader:
    """Main quality grader for Copilot integration"""
    
    def __init__(self):
        self.voice_scorer = VoiceAuthenticityScorer()
        self.ai_scorer = AIDetectionScorer()
        # Initialize other scorers...
    
    def grade_caption(
        self,
        material: str,
        before_text: str,
        after_text: str,
        expected_country: str
    ) -> CopilotGrade:
        """Grade caption quality across all dimensions"""
        
        combined_content = f"{before_text} {after_text}"
        
        # Voice authenticity scoring
        voice_score = self.voice_scorer.score_voice_authenticity(combined_content, expected_country)
        
        # AI detection scoring
        ai_score = self.ai_scorer.score_ai_detectability(combined_content)
        
        # Technical accuracy scoring (simplified for now)
        technical_score = self._score_technical_accuracy(combined_content, material)
        
        # Structural scoring
        structural_score = self._score_structure(before_text, after_text)
        
        # Calculate overall score (weighted average)
        overall_score = int(
            (voice_score.overall_authenticity * 0.3) +
            (ai_score.human_likeness * 0.3) +
            (technical_score.overall_technical_quality * 0.25) +
            (structural_score.overall_structure * 0.15)
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(voice_score, ai_score, technical_score, structural_score)
        
        # Determine pass/fail status
        pass_fail_status = self._determine_pass_fail(overall_score, voice_score, ai_score)
        production_ready = pass_fail_status == "PASS"
        
        return CopilotGrade(
            overall_score=overall_score,
            voice_authenticity=voice_score,
            ai_detectability=ai_score,
            technical_accuracy=technical_score,
            structural_quality=structural_score,
            recommendations=recommendations,
            pass_fail_status=pass_fail_status,
            production_ready=production_ready
        )
    
    def _score_technical_accuracy(self, content: str, material: str) -> TechnicalScore:
        """Simplified technical accuracy scoring"""
        # This would be expanded with material-specific validation
        return TechnicalScore(
            material_accuracy=85,  # Placeholder
            cleaning_realism=90,   # Placeholder
            measurement_plausibility=80,  # Placeholder
            process_accuracy=85,   # Placeholder
            overall_technical_quality=85,
            technical_issues=[]
        )
    
    def _score_structure(self, before_text: str, after_text: str) -> StructuralScore:
        """Score structural quality"""
        combined = f"{before_text} {after_text}"
        sentences = [s.strip() for s in re.split(r'[.!?]+', combined) if s.strip()]
        words = combined.split()
        
        sentence_count = len(sentences)
        word_count = len(words)
        
        # Check compliance (6-9 sentences target)
        sentence_count_compliance = 6 <= sentence_count <= 9
        word_count_compliance = 100 <= word_count <= 300  # Approximate target
        
        # Score flow and clarity (simplified)
        flow_quality = 85 if sentence_count_compliance else 60
        clarity = 80  # Placeholder
        
        overall_structure = int((flow_quality + clarity) / 2)
        
        return StructuralScore(
            sentence_count=sentence_count,
            word_count=word_count,
            sentence_count_compliance=sentence_count_compliance,
            word_count_compliance=word_count_compliance,
            flow_quality=flow_quality,
            clarity=clarity,
            overall_structure=overall_structure
        )
    
    def _generate_recommendations(self, voice_score, ai_score, technical_score, structural_score) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if voice_score.overall_authenticity < 70:
            recommendations.append(f"Improve voice authenticity for {voice_score.detected_country}")
        
        if ai_score.human_likeness < 75:
            recommendations.append("Reduce AI detectability patterns")
            if ai_score.detected_issues:
                recommendations.extend([f"Fix: {issue}" for issue in ai_score.detected_issues[:2]])
        
        if not structural_score.sentence_count_compliance:
            recommendations.append(f"Adjust sentence count to 6-9 (current: {structural_score.sentence_count})")
        
        return recommendations
    
    def _determine_pass_fail(self, overall_score: int, voice_score: VoiceScore, ai_score: AIScore) -> str:
        """Determine overall pass/fail status"""
        if overall_score >= 80 and voice_score.overall_authenticity >= 70 and ai_score.human_likeness >= 75:
            return "PASS"
        elif overall_score >= 60:
            return "NEEDS_IMPROVEMENT"
        else:
            return "FAIL"


# CLI Interface for Copilot
def main():
    """Command line interface for caption grading"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Grade caption quality for Copilot")
    parser.add_argument("--material", required=True, help="Material name")
    parser.add_argument("--country", required=True, help="Expected country")
    parser.add_argument("--assess-quality", action="store_true", help="Assess caption quality")
    
    args = parser.parse_args()
    
    if args.assess_quality:
        # Load caption data and grade it
        grader = CopilotQualityGrader()
        
        # Load from Materials.yaml (simplified)
        materials_path = Path("data/Materials.yaml")
        with open(materials_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if args.material in data['materials'] and 'captions' in data['materials'][args.material]:
            captions = data['materials'][args.material]['captions']
            before_text = captions.get('before_text', '')
            after_text = captions.get('after_text', '')
            
            grade = grader.grade_caption(
                material=args.material,
                before_text=before_text,
                after_text=after_text,
                expected_country=args.country
            )
            
            # Output results for Copilot
            print(f"🏆 QUALITY ASSESSMENT: {args.material}")
            print(f"Overall Score: {grade.overall_score}/100")
            print(f"Status: {grade.pass_fail_status}")
            print(f"Production Ready: {grade.production_ready}")
            print(f"Voice Authenticity: {grade.voice_authenticity.overall_authenticity}/100")
            print(f"AI Human-likeness: {grade.ai_detectability.human_likeness}/100")
            print(f"Detected Country: {grade.voice_authenticity.detected_country}")
            
            if grade.recommendations:
                print("\nRecommendations:")
                for rec in grade.recommendations:
                    print(f"  • {rec}")
        else:
            print(f"❌ Caption not found for {args.material}")


if __name__ == "__main__":
    main()