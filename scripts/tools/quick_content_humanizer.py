#!/usr/bin/env python3
"""
Quick Content Humanizer - Immediate Implementation
Applies human writing patterns to improve AI detection scores
"""

import re
import random

class QuickContentHumanizer:
    def __init__(self):
        self.qualifiers = [
            'typically', 'generally', 'often', 'usually', 'frequently',
            'commonly', 'regularly', 'predominantly', 'largely'
        ]
        
        self.uncertainty_phrases = [
            'appears to', 'tends to', 'seems to', 'can help',
            'may provide', 'often results in', 'typically offers'
        ]
        
        self.experience_signals = [
            'In practice,', 'Field experience shows', 'Industrial applications demonstrate',
            'Real-world implementations reveal', 'Practical studies indicate',
            'Professional experience suggests', 'Industry analysis shows'
        ]
        
        self.transitions = [
            'However,', 'Meanwhile,', 'Furthermore,', 'Additionally,',
            'Interestingly,', 'Notably,', 'In contrast,', 'Consequently,'
        ]

    def humanize_content(self, content):
        """Apply comprehensive human writing patterns to content"""
        # First apply sentence structure optimization
        content = self._optimize_sentence_structure(content)
        
        # Then apply linguistic humanization
        content = self._apply_linguistic_patterns(content)
        
        return content

    def _optimize_sentence_structure(self, content):
        """Apply sentence structure optimization for natural rhythm"""
        try:
            from scripts.tools.sentence_structure_optimizer import SentenceStructureOptimizer
            optimizer = SentenceStructureOptimizer()
            return optimizer.optimize_sentence_structure(content)
        except Exception as e:
            # If optimization fails, continue with original content
            return content

    def _apply_linguistic_patterns(self, content):
        """Apply linguistic humanization patterns"""
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', content.strip())
        
        humanized_sentences = []
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
                
            # Add qualifiers to absolute statements
            sentence = self.add_qualifiers(sentence)
            
            # Add uncertainty to definitive claims
            sentence = self.add_uncertainty(sentence)
            
            # Add experience signals occasionally
            if i > 0 and random.random() < 0.15:  # 15% chance
                experience_signal = random.choice(self.experience_signals)
                sentence = f"{experience_signal} {sentence.lower()}"
            
            # Add transitions occasionally
            if i > 0 and random.random() < 0.20:  # 20% chance
                transition = random.choice(self.transitions)
                sentence = f"{transition} {sentence.lower()}"
            
            humanized_sentences.append(sentence)
        
        return ' '.join(humanized_sentences)
    
    def add_qualifiers(self, sentence):
        """Add qualifiers to make statements less absolute"""
        # Replace absolute verbs with qualified versions
        replacements = {
            r'\bprovides\b': lambda: f"{random.choice(self.qualifiers)} provides",
            r'\bensures\b': 'helps ensure',
            r'\beliminates\b': 'effectively removes',
            r'\bguarantees\b': 'typically ensures',
            r'\ballows\b': lambda: f"{random.choice(['often', 'frequently'])} allows",
            r'\bresults in\b': lambda: f"{random.choice(['typically', 'often'])} results in"
        }
        
        for pattern, replacement in replacements.items():
            if callable(replacement):
                sentence = re.sub(pattern, replacement(), sentence)
            else:
                sentence = re.sub(pattern, replacement, sentence)
        
        return sentence
    
    def add_uncertainty(self, sentence):
        """Add uncertainty expressions to definitive claims"""
        # Replace definitive claims with uncertain ones
        uncertainty_replacements = {
            r'\bis\s+(extremely|highly|very)\s+effective': r'appears to be \1 effective',
            r'\bwill\s+provide': random.choice(self.uncertainty_phrases),
            r'\bis\s+essential': 'is often essential',
            r'\bis\s+critical': 'can be critical',
            r'\bis\s+important': 'is typically important'
        }
        
        for pattern, replacement in uncertainty_replacements.items():
            sentence = re.sub(pattern, replacement, sentence)
        
        return sentence

# Quick test function
def test_humanizer():
    """Test the humanizer with sample technical content"""
    sample_content = """
    Laser cleaning provides exceptional results for aluminum surfaces. 
    The process eliminates oxidation and ensures optimal surface preparation. 
    This technology is essential for aerospace applications and guarantees superior performance.
    """
    
    humanizer = QuickContentHumanizer()
    humanized = humanizer.humanize_content(sample_content)
    
    print("Original:")
    print(sample_content)
    print("\nHumanized:")
    print(humanized)

if __name__ == "__main__":
    test_humanizer()
