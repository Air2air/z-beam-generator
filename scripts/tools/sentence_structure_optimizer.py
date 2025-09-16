#!/usr/bin/env python3
"""
Sentence Structure Analyzer and Optimizer
Ensures proper sentence length distribution for human-like writing
"""

import re
import random
from typing import List, Tuple

class SentenceStructureOptimizer:
    def __init__(self):
        self.target_distribution = {
            'short': 0.20,   # 5-10 words
            'medium': 0.60,  # 11-20 words  
            'long': 0.20     # 21+ words
        }
        
        self.word_ranges = {
            'short': (5, 10),
            'medium': (11, 20),
            'long': (21, 35)
        }

    def analyze_sentence_distribution(self, content: str) -> dict:
        """Analyze current sentence length distribution"""
        sentences = self._split_sentences(content)
        if not sentences:
            return {'short': 0, 'medium': 0, 'long': 0, 'total': 0}
        
        distribution = {'short': 0, 'medium': 0, 'long': 0}
        
        for sentence in sentences:
            word_count = len(sentence.split())
            if word_count <= 10:
                distribution['short'] += 1
            elif word_count <= 20:
                distribution['medium'] += 1
            else:
                distribution['long'] += 1
        
        total = len(sentences)
        distribution['total'] = total
        
        # Convert to percentages
        for key in ['short', 'medium', 'long']:
            distribution[f'{key}_pct'] = (distribution[key] / total) * 100 if total > 0 else 0
        
        return distribution

    def optimize_sentence_structure(self, content: str) -> str:
        """Optimize sentence structure to match target distribution"""
        sentences = self._split_sentences(content)
        if len(sentences) < 3:  # Need at least 3 sentences to optimize
            return content
        
        current_dist = self.analyze_sentence_distribution(content)
        
        # Check if optimization is needed
        needs_optimization = (
            abs(current_dist['short_pct'] - 20) > 10 or
            abs(current_dist['medium_pct'] - 60) > 15 or
            abs(current_dist['long_pct'] - 20) > 10
        )
        
        if not needs_optimization:
            return content
        
        # Optimize sentences
        optimized_sentences = []
        target_counts = self._calculate_target_counts(len(sentences))
        
        # Categorize existing sentences
        categorized = self._categorize_sentences(sentences)
        
        # Redistribute to match targets
        redistributed = self._redistribute_sentences(categorized, target_counts)
        
        return ' '.join(redistributed)

    def _split_sentences(self, content: str) -> List[str]:
        """Split content into sentences"""
        # Clean up the content first
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Split on sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        # Filter out empty sentences and clean up
        return [s.strip() for s in sentences if s.strip()]

    def _categorize_sentences(self, sentences: List[str]) -> dict:
        """Categorize sentences by length"""
        categorized = {'short': [], 'medium': [], 'long': []}
        
        for sentence in sentences:
            word_count = len(sentence.split())
            if word_count <= 10:
                categorized['short'].append(sentence)
            elif word_count <= 20:
                categorized['medium'].append(sentence)
            else:
                categorized['long'].append(sentence)
        
        return categorized

    def _calculate_target_counts(self, total_sentences: int) -> dict:
        """Calculate target sentence counts for each category"""
        return {
            'short': max(1, round(total_sentences * self.target_distribution['short'])),
            'medium': max(1, round(total_sentences * self.target_distribution['medium'])),
            'long': max(1, round(total_sentences * self.target_distribution['long']))
        }

    def _redistribute_sentences(self, categorized: dict, targets: dict) -> List[str]:
        """Redistribute sentences to match target distribution"""
        result = []
        
        # Start with medium sentences (backbone)
        medium_sentences = categorized['medium'][:targets['medium']]
        
        # Add short sentences
        short_sentences = categorized['short'][:targets['short']]
        
        # If we need more short sentences, split some medium ones
        if len(short_sentences) < targets['short'] and medium_sentences:
            additional_short = self._create_short_from_medium(
                medium_sentences, targets['short'] - len(short_sentences)
            )
            short_sentences.extend(additional_short)
        
        # Add long sentences
        long_sentences = categorized['long'][:targets['long']]
        
        # If we need more long sentences, combine some medium ones
        if len(long_sentences) < targets['long'] and len(medium_sentences) > 1:
            additional_long = self._create_long_from_medium(
                medium_sentences, targets['long'] - len(long_sentences)
            )
            long_sentences.extend(additional_long)
        
        # Combine all sentences maintaining logical flow
        all_sentences = short_sentences + medium_sentences + long_sentences
        
        # Shuffle while maintaining some logical order
        return self._intelligent_shuffle(all_sentences, short_sentences, medium_sentences, long_sentences)

    def _create_short_from_medium(self, medium_sentences: List[str], needed: int) -> List[str]:
        """Create short sentences by splitting medium ones"""
        short_sentences = []
        
        for sentence in medium_sentences[:needed]:
            # Try to split at natural break points
            words = sentence.split()
            if len(words) > 12:
                # Split roughly in half
                split_point = len(words) // 2
                first_part = ' '.join(words[:split_point]) + '.'
                if len(first_part.split()) <= 10:
                    short_sentences.append(first_part)
                    if len(short_sentences) >= needed:
                        break
        
        return short_sentences

    def _create_long_from_medium(self, medium_sentences: List[str], needed: int) -> List[str]:
        """Create long sentences by combining medium ones"""
        long_sentences = []
        
        i = 0
        while i < len(medium_sentences) - 1 and len(long_sentences) < needed:
            # Combine two sentences with appropriate connector
            connectors = [', and', ', while', ', which', ', as']
            connector = random.choice(connectors)
            
            first = medium_sentences[i].rstrip('.')
            second = medium_sentences[i + 1]
            
            combined = f"{first}{connector} {second.lower()}"
            if len(combined.split()) >= 21:
                long_sentences.append(combined)
            
            i += 2
        
        return long_sentences

    def _intelligent_shuffle(self, all_sentences: List[str], short: List[str], 
                           medium: List[str], long: List[str]) -> List[str]:
        """Intelligently arrange sentences for natural flow"""
        # Start with a medium sentence for context
        result = []
        
        # Create pools
        short_pool = short.copy()
        medium_pool = medium.copy()
        long_pool = long.copy()
        
        # Alternate between different lengths for natural rhythm
        patterns = ['medium', 'short', 'medium', 'long', 'medium', 'short']
        pattern_index = 0
        
        while short_pool or medium_pool or long_pool:
            if pattern_index < len(patterns):
                preferred = patterns[pattern_index]
            else:
                # Random selection after pattern
                preferred = random.choice(['short', 'medium', 'long'])
            
            # Try preferred type first
            if preferred == 'short' and short_pool:
                result.append(short_pool.pop(0))
            elif preferred == 'medium' and medium_pool:
                result.append(medium_pool.pop(0))
            elif preferred == 'long' and long_pool:
                result.append(long_pool.pop(0))
            else:
                # Fallback to any available
                if medium_pool:
                    result.append(medium_pool.pop(0))
                elif short_pool:
                    result.append(short_pool.pop(0))
                elif long_pool:
                    result.append(long_pool.pop(0))
            
            pattern_index += 1
        
        return result

# Test function
def test_sentence_optimizer():
    """Test the sentence structure optimizer"""
    sample_content = """
    Laser cleaning provides exceptional results for aluminum surfaces. The process eliminates oxidation effectively. 
    This technology represents a significant advancement in surface preparation methodologies, offering precision and control that traditional methods cannot match. 
    Industries worldwide have adopted this approach. The benefits include reduced environmental impact, improved safety protocols, and enhanced operational efficiency.
    Quality improvements are measurable. Cost reductions follow implementation.
    """
    
    optimizer = SentenceStructureOptimizer()
    
    print("Original content:")
    print(sample_content.strip())
    
    print("\nOriginal distribution:")
    original_dist = optimizer.analyze_sentence_distribution(sample_content)
    for key in ['short', 'medium', 'long']:
        print(f"  {key.capitalize()}: {original_dist[key]} ({original_dist[f'{key}_pct']:.1f}%)")
    
    optimized = optimizer.optimize_sentence_structure(sample_content)
    
    print("\nOptimized content:")
    print(optimized)
    
    print("\nOptimized distribution:")
    optimized_dist = optimizer.analyze_sentence_distribution(optimized)
    for key in ['short', 'medium', 'long']:
        print(f"  {key.capitalize()}: {optimized_dist[key]} ({optimized_dist[f'{key}_pct']:.1f}%)")

if __name__ == "__main__":
    test_sentence_optimizer()
