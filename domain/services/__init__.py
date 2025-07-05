"""
Domain services for the Z-Beam content generation system.
These contain core business logic that doesn't belong to a specific entity.
"""

from typing import Dict, List, Tuple
from domain.value_objects import SectionSpec, WordBudget, SectionType
import logging

logger = logging.getLogger(__name__)


class WordBudgetDomainService:
    """Domain service for word budget allocation and management."""
    
    # Standard section weight allocations based on business rules
    DEFAULT_SECTION_WEIGHTS = {
        SectionType.INTRODUCTION: 0.15,      # 15%
        SectionType.COMPARISON: 0.20,        # 20%
        SectionType.CONTAMINANTS: 0.15,      # 15%
        SectionType.SUBSTRATES: 0.15,        # 15%
        SectionType.CHART: 0.10,             # 10%
        SectionType.TABLE: 0.10,             # 10%
        SectionType.MATERIAL_RESEARCH: 0.15, # 15%
        SectionType.CONCLUSION: 0.05,        # 5% (if used)
    }
    
    def calculate_optimal_allocation(
        self, 
        total_words: int, 
        section_specs: List[SectionSpec],
        custom_weights: Dict[str, float] = None
    ) -> WordBudget:
        """
        Calculate optimal word allocation based on section importance and business rules.
        
        Args:
            total_words: Total word budget available
            section_specs: List of section specifications
            custom_weights: Optional custom weights to override defaults
            
        Returns:
            WordBudget with optimized allocations
        """
        if not section_specs:
            raise ValueError("Section specifications cannot be empty")
        
        # Build weight map
        weights = {}
        total_weight = 0.0
        
        for spec in section_specs:
            section_name = spec.name
            section_type = spec.section_type
            
            # Use custom weight if provided, otherwise use default for type
            if custom_weights and section_name in custom_weights:
                weight = custom_weights[section_name]
            else:
                weight = self.DEFAULT_SECTION_WEIGHTS.get(section_type, 0.10)
            
            # Adjust weight based on priority
            weight = self._adjust_weight_for_priority(weight, spec.priority)
            
            weights[section_name] = weight
            total_weight += weight
        
        # Normalize weights to sum to 1.0
        if total_weight > 0:
            weights = {name: weight / total_weight for name, weight in weights.items()}
        
        # Calculate allocations
        allocations = {}
        allocated_words = 0
        
        # Allocate words for all sections except the last one
        section_names = list(weights.keys())
        for section_name in section_names[:-1]:
            words = int(total_words * weights[section_name])
            allocations[section_name] = words
            allocated_words += words
        
        # Give remaining words to the last section
        if section_names:
            last_section = section_names[-1]
            allocations[last_section] = total_words - allocated_words
        
        logger.debug(f"Calculated word allocation: {allocations}")
        return WordBudget(total_words=total_words, section_allocations=allocations)
    
    def _adjust_weight_for_priority(self, base_weight: float, priority: int) -> float:
        """Adjust section weight based on priority."""
        if priority == 1:  # High priority
            return base_weight * 1.2
        elif priority == 3:  # Low priority
            return base_weight * 0.8
        else:  # Medium priority
            return base_weight
    
    def validate_budget_feasibility(
        self, 
        word_budget: WordBudget, 
        section_specs: List[SectionSpec]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that the word budget is feasible for the given section requirements.
        
        Returns:
            Tuple of (is_feasible, list_of_issues)
        """
        issues = []
        
        # Check each section has adequate budget
        for spec in section_specs:
            allocated = word_budget.get_section_budget(spec.name)
            
            # Minimum viable words per section (business rule)
            min_words = self._get_minimum_words_for_section(spec.section_type)
            if allocated < min_words:
                issues.append(
                    f"Section '{spec.name}' allocated {allocated} words, "
                    f"but minimum required is {min_words}"
                )
            
            # Check against section requirements
            if spec.requirements:
                required_words = spec.requirements.get('min_words')
                if required_words and allocated < required_words:
                    issues.append(
                        f"Section '{spec.name}' allocated {allocated} words, "
                        f"but requires {required_words}"
                    )
        
        return len(issues) == 0, issues
    
    def _get_minimum_words_for_section(self, section_type: SectionType) -> int:
        """Get minimum viable word count for a section type."""
        minimums = {
            SectionType.INTRODUCTION: 80,
            SectionType.COMPARISON: 100,
            SectionType.CONTAMINANTS: 80,
            SectionType.SUBSTRATES: 80,
            SectionType.CHART: 50,
            SectionType.TABLE: 50,
            SectionType.MATERIAL_RESEARCH: 100,
            SectionType.CONCLUSION: 30,
        }
        return minimums.get(section_type, 50)
    
    def rebalance_budget(
        self, 
        current_budget: WordBudget, 
        actual_usage: Dict[str, int]
    ) -> WordBudget:
        """
        Rebalance word budget based on actual usage patterns.
        Useful for adaptive budget management.
        """
        # Calculate variance from planned allocation
        variances = {}
        for section, allocated in current_budget.section_allocations.items():
            used = actual_usage.get(section, 0)
            variance = used - allocated
            variances[section] = variance
        
        # Identify sections that consistently over/under-use their budget
        # This is simplified - in practice, you'd use historical data
        adjustments = {}
        for section, variance in variances.items():
            if abs(variance) > current_budget.get_section_budget(section) * 0.2:  # 20% variance
                adjustment = variance * 0.5  # Adjust by half the variance
                adjustments[section] = adjustment
        
        # Apply adjustments while maintaining total budget
        new_allocations = current_budget.section_allocations.copy()
        total_adjustment = sum(adjustments.values())
        
        if total_adjustment != 0:
            # Distribute the adjustment across all sections
            per_section_adjustment = -total_adjustment / len(new_allocations)
            for section in new_allocations:
                if section in adjustments:
                    new_allocations[section] += adjustments[section]
                new_allocations[section] += per_section_adjustment
                new_allocations[section] = max(10, int(new_allocations[section]))  # Minimum 10 words
        
        return WordBudget(
            total_words=current_budget.total_words,
            section_allocations=new_allocations,
            buffer_percentage=current_budget.buffer_percentage
        )


class ContentQualityDomainService:
    """Domain service for content quality assessment and improvement suggestions."""
    
    def assess_content_quality(
        self, 
        content: str, 
        ai_score: float, 
        human_score: float,
        word_target: int
    ) -> Dict[str, any]:
        """
        Assess overall content quality and provide improvement suggestions.
        """
        quality_score = self._calculate_quality_score(ai_score, human_score, content, word_target)
        
        suggestions = []
        issues = []
        
        # Analyze AI detection score
        if ai_score > 30:
            issues.append("High AI detection score")
            suggestions.extend(self._get_ai_score_suggestions(ai_score))
        
        # Analyze human score
        if human_score < 70:
            issues.append("Low human-like score")
            suggestions.extend(self._get_human_score_suggestions(human_score))
        
        # Analyze word count
        word_count = len(content.split())
        word_variance = abs(word_count - word_target) / word_target
        if word_variance > 0.15:  # More than 15% variance
            issues.append(f"Word count variance: {word_variance:.1%}")
            suggestions.append(f"Adjust content length to target {word_target} words")
        
        # Analyze content structure
        structure_issues = self._analyze_content_structure(content)
        issues.extend(structure_issues)
        
        return {
            'quality_score': quality_score,
            'grade': self._get_quality_grade(quality_score),
            'issues': issues,
            'suggestions': suggestions,
            'word_count': word_count,
            'word_target': word_target,
            'ai_score': ai_score,
            'human_score': human_score
        }
    
    def _calculate_quality_score(
        self, 
        ai_score: float, 
        human_score: float, 
        content: str, 
        word_target: int
    ) -> float:
        """Calculate overall quality score (0-100)."""
        # Base quality from detection scores
        detection_quality = (100 - ai_score + human_score) / 2
        
        # Adjust for word count accuracy
        word_count = len(content.split())
        word_accuracy = 1 - min(abs(word_count - word_target) / word_target, 0.5)
        
        # Adjust for content structure
        structure_score = self._assess_structure_quality(content)
        
        # Weighted combination
        quality_score = (
            detection_quality * 0.6 +      # 60% weight on detection scores
            word_accuracy * 100 * 0.2 +    # 20% weight on word accuracy
            structure_score * 0.2           # 20% weight on structure
        )
        
        return min(100, max(0, quality_score))
    
    def _get_quality_grade(self, quality_score: float) -> str:
        """Convert quality score to letter grade."""
        if quality_score >= 90:
            return "A"
        elif quality_score >= 80:
            return "B"
        elif quality_score >= 70:
            return "C"
        elif quality_score >= 60:
            return "D"
        else:
            return "F"
    
    def _get_ai_score_suggestions(self, ai_score: float) -> List[str]:
        """Get suggestions for improving AI detection scores."""
        suggestions = []
        
        if ai_score > 50:
            suggestions.extend([
                "Use more varied sentence structures",
                "Add personal anecdotes or experiences",
                "Include more conversational language"
            ])
        elif ai_score > 30:
            suggestions.extend([
                "Reduce repetitive phrasing",
                "Add more natural transitions",
                "Include industry-specific terminology"
            ])
        
        return suggestions
    
    def _get_human_score_suggestions(self, human_score: float) -> List[str]:
        """Get suggestions for improving human-like scores."""
        suggestions = []
        
        if human_score < 50:
            suggestions.extend([
                "Add more emotional language",
                "Include rhetorical questions",
                "Use more active voice"
            ])
        elif human_score < 70:
            suggestions.extend([
                "Improve flow and readability",
                "Add more descriptive language",
                "Include real-world examples"
            ])
        
        return suggestions
    
    def _analyze_content_structure(self, content: str) -> List[str]:
        """Analyze content structure and identify issues."""
        issues = []
        
        # Check paragraph structure
        paragraphs = content.split('\n\n')
        if len(paragraphs) < 2:
            issues.append("Content lacks paragraph structure")
        
        # Check sentence variety
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_sentence_length > 25:
            issues.append("Sentences are too long on average")
        elif avg_sentence_length < 10:
            issues.append("Sentences are too short on average")
        
        return issues
    
    def _assess_structure_quality(self, content: str) -> float:
        """Assess the structural quality of content (0-100)."""
        score = 100
        
        # Penalize for poor paragraph structure
        paragraphs = content.split('\n\n')
        if len(paragraphs) < 2:
            score -= 20
        
        # Check for good sentence variety
        sentences = content.split('.')
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if sentence_lengths:
            length_variance = len(set(sentence_lengths)) / len(sentence_lengths)
            if length_variance < 0.3:  # Low variety
                score -= 15
        
        return max(0, score)
