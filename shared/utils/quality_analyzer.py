"""
Quality Analysis Utility

Analyzes generated content for voice distinctiveness, length variation,
and AI detection compliance.

Created: January 13, 2026
Purpose: Built-in quality verification for generation system
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class VoiceAnalysis:
    """Results of voice distinctiveness analysis"""
    author_country: str
    patterns_detected: List[str]
    pattern_score: float  # 0.0-1.0
    expected_patterns: List[str]
    missing_patterns: List[str]
    voice_authentic: bool


@dataclass
class LengthAnalysis:
    """Results of length variation analysis"""
    word_count: int
    target_range: tuple  # (min, max)
    within_range: bool
    variation_factor: float
    length_compliant: bool


@dataclass
class AIDetectionAnalysis:
    """Results of AI detection analysis"""
    ai_phrases_detected: List[str]
    ai_score: float  # 0.0-1.0 (higher = more AI-like)
    human_threshold: float
    passes_detection: bool


@dataclass
class QualityAnalysisResult:
    """Complete quality analysis result"""
    content: str
    voice_analysis: VoiceAnalysis
    length_analysis: LengthAnalysis
    ai_analysis: AIDetectionAnalysis
    overall_quality: float  # 0.0-1.0
    recommendations: List[str]
    passes_all_checks: bool


class QualityAnalyzer:
    """Analyzes generated content for quality compliance"""
    
    def __init__(self):
        self.voice_profiles_path = Path("shared/voice/profiles")
        self.generation_config_path = Path("generation/config.yaml")
        
        # Load AI detection patterns
        self.ai_patterns = [
            r"presents?\s+(?:a\s+)?(?:unique|significant|primary|critical)\s+challenge",
            r"critical\s+pitfall",
            r"this\s+(?:property|balance|approach)\s+is\s+essential\s+for",
            r"it'?s\s+important\s+to\s+(?:note|understand|remember)",
            r"furthermore|moreover|additionally",
            r"in\s+conclusion|to\s+summarize",
            r"various\s+(?:factors|aspects|considerations)",
            r"comprehensive\s+(?:approach|analysis|understanding)"
        ]
        
        # Load country-specific voice patterns
        self.voice_patterns = self._load_voice_patterns()
        
    def _load_voice_patterns(self) -> Dict[str, List[str]]:
        """Load voice patterns from persona files"""
        patterns = {}
        
        for profile_file in self.voice_profiles_path.glob("*.yaml"):
            try:
                with open(profile_file, 'r') as f:
                    profile = yaml.safe_load(f)
                    
                country = profile.get('country', '')
                if country:
                    # Extract patterns from core_voice_instruction
                    instruction = profile.get('core_voice_instruction', '')
                    patterns[country] = self._extract_patterns_from_instruction(instruction, country)
                    
            except Exception as e:
                print(f"Warning: Could not load voice profile {profile_file}: {e}")
                
        return patterns
        
    def _extract_patterns_from_instruction(self, instruction: str, country: str) -> List[str]:
        """Extract expected patterns from voice instruction"""
        patterns = []
        
        if country == "United States":
            patterns = [
                r"(?:line|dial|ramp|cut|work)\s+(?:up|in|down|out)",  # Phrasal verbs
                r"(?:by|cuts?|improves?)\s+\d+%",  # Quantified outcomes
                r"(?:turns?\s+out|in\s+practice|overall)",  # Practical transitions
            ]
        elif country == "Taiwan":
            patterns = [
                r"[A-Z][^,]+,\s+it\s+(?:measures?|shows?|exhibits?)",  # Topic-comment
                r"(?:Process|Surface|Method)\s+(?:yields?|shows?)\s+\w+",  # Article omission
                r"(?:After|Following)\s+\w+,\s+\w+",  # Temporal markers
            ]
        elif country == "Italy":
            patterns = [
                r"(?:This|These)\s+\w+,\s+(?:it|they)\s+\w+",  # Cleft structures
                r"It\s+(?:seems|appears)\s+that",  # Subjunctive hedging
                r"(?:tenaciously|manifests?|persists?|exhibits?)",  # Romance cognates
            ]
        elif country == "Indonesia":
            patterns = [
                r"This\s+\w+,\s+it\s+(?:forms?|reduces?|shows?)",  # Topic prominence
                r"(?:already|still|just\s+now)\s+(?:removed|present|detected)",  # Aspectual markers
                r"(?:is|are)\s+(?:observed|detected|obtained)\s+(?:at|on|from)",  # Agentless passives
            ]
            
        return patterns
        
    def analyze_voice(self, content: str, author_country: str) -> VoiceAnalysis:
        """Analyze content for voice authenticity"""
        expected_patterns = self.voice_patterns.get(author_country, [])
        detected_patterns = []
        
        content_lower = content.lower()
        
        for pattern in expected_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                detected_patterns.extend(matches)
                
        pattern_score = len(detected_patterns) / max(len(expected_patterns), 1)
        missing_patterns = [p for p in expected_patterns if not re.search(p, content, re.IGNORECASE)]
        
        # Voice is authentic if at least 60% of patterns detected
        voice_authentic = pattern_score >= 0.6
        
        return VoiceAnalysis(
            author_country=author_country,
            patterns_detected=detected_patterns,
            pattern_score=pattern_score,
            expected_patterns=expected_patterns,
            missing_patterns=missing_patterns,
            voice_authentic=voice_authentic
        )
        
    def analyze_length(self, content: str, target_words: int = 50, variation_percent: int = 50) -> LengthAnalysis:
        """Analyze content for length compliance"""
        word_count = len(content.split())
        
        # Calculate acceptable range based on variation
        variation_factor = variation_percent / 100.0
        min_words = int(target_words * (1 - variation_factor))
        max_words = int(target_words * (1 + variation_factor))
        
        within_range = min_words <= word_count <= max_words
        actual_variation = abs(word_count - target_words) / target_words
        
        return LengthAnalysis(
            word_count=word_count,
            target_range=(min_words, max_words),
            within_range=within_range,
            variation_factor=actual_variation,
            length_compliant=within_range
        )
        
    def analyze_ai_detection(self, content: str, threshold: float = 0.70) -> AIDetectionAnalysis:
        """Analyze content for AI detection compliance"""
        detected_phrases = []
        
        for pattern in self.ai_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                detected_phrases.extend(matches)
                
        # Simple scoring: each AI phrase detected increases AI score
        ai_score = min(len(detected_phrases) * 0.2, 1.0)
        passes_detection = ai_score <= (1 - threshold)  # Invert: high threshold = more AI allowed
        
        return AIDetectionAnalysis(
            ai_phrases_detected=detected_phrases,
            ai_score=ai_score,
            human_threshold=threshold,
            passes_detection=passes_detection
        )
        
    def analyze_content(self, content: str, author_country: str, 
                       target_words: int = 50, variation_percent: int = 50,
                       ai_threshold: float = 0.70) -> QualityAnalysisResult:
        """Perform complete quality analysis"""
        
        voice_analysis = self.analyze_voice(content, author_country)
        length_analysis = self.analyze_length(content, target_words, variation_percent)
        ai_analysis = self.analyze_ai_detection(content, ai_threshold)
        
        # Calculate overall quality score
        voice_score = voice_analysis.pattern_score
        length_score = 1.0 if length_analysis.length_compliant else 0.5
        ai_score = 1.0 if ai_analysis.passes_detection else 0.3
        
        overall_quality = (voice_score * 0.4 + length_score * 0.3 + ai_score * 0.3)
        
        # Generate recommendations
        recommendations = []
        
        if not voice_analysis.voice_authentic:
            recommendations.append(f"Add more {author_country} voice patterns: {voice_analysis.missing_patterns[:2]}")
            
        if not length_analysis.length_compliant:
            target_min, target_max = length_analysis.target_range
            recommendations.append(f"Adjust length: current {length_analysis.word_count} words, target {target_min}-{target_max}")
            
        if not ai_analysis.passes_detection:
            recommendations.append(f"Remove AI phrases: {ai_analysis.ai_phrases_detected[:2]}")
            
        passes_all_checks = (voice_analysis.voice_authentic and 
                           length_analysis.length_compliant and 
                           ai_analysis.passes_detection)
                           
        return QualityAnalysisResult(
            content=content,
            voice_analysis=voice_analysis,
            length_analysis=length_analysis,
            ai_analysis=ai_analysis,
            overall_quality=overall_quality,
            recommendations=recommendations,
            passes_all_checks=passes_all_checks
        )


# Global instance for easy access
quality_analyzer = QualityAnalyzer()