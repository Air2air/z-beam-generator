"""
Quality Improvement System - Advanced Content Enhancement

Provides multi-tiered quality improvement strategies beyond basic threshold checking.

Features:
    1. Technical Accuracy Analysis - Domain-specific quality checks
    2. Comparative Benchmarking - Compare against category best examples
    3. Iterative Refinement - Targeted improvements for near-threshold content
    4. Human Feedback Integration - Learn from manual reviews
    5. Cross-Material Consistency - Ensure style consistency within categories
    6. Freshness Detection - Identify outdated content patterns

Architecture:
    QualityAnalyzer (base metrics) → QualityImprovements (advanced strategies)
    
Usage:
    from shared.commands.quality_improvements import QualityImprovementSystem
    
    improver = QualityImprovementSystem(domain='materials', field='description')
    result = improver.evaluate_for_improvement(text, item_data, quality_analysis)
    
    if result['needs_improvement']:
        improved_text = improver.refine_content(text, result['improvement_strategy'])
"""

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class QualityImprovementSystem:
    """
    Advanced quality improvement system with multiple enhancement strategies.
    
    Goes beyond basic pass/fail to provide targeted improvement paths.
    """
    
    def __init__(
        self,
        domain: str,
        field: str,
        learning_db_path: str = 'z-beam.db',
        quality_analyzer=None
    ):
        """
        Initialize quality improvement system.
        
        Args:
            domain: Domain name (materials, contaminants, settings)
            field: Field type (description, micro, etc.)
            learning_db_path: Path to learning database
            quality_analyzer: QualityAnalyzer instance (optional)
        """
        self.domain = domain
        self.field = field
        self.learning_db_path = learning_db_path
        self.quality_analyzer = quality_analyzer
        
        logger.info(f"QualityImprovementSystem initialized for {domain}.{field}")
    
    def evaluate_for_improvement(
        self,
        text: str,
        item_data: Dict[str, Any],
        base_quality: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation to determine if and how content should be improved.
        
        Args:
            text: Current content
            item_data: Material/item data dict
            base_quality: Base quality analysis from QualityAnalyzer
            
        Returns:
            {
                'needs_improvement': bool,
                'improvement_strategy': str,  # 'regenerate', 'refine', 'keep'
                'reasons': List[str],
                'priority_areas': List[str],
                'benchmark_gap': float,  # How far below category best
                'technical_issues': List[str]
            }
        """
        base_score = base_quality.get('overall_score', 0)
        category = item_data.get('category', 'unknown')
        
        # Initialize result
        result = {
            'needs_improvement': False,
            'improvement_strategy': 'keep',
            'reasons': [],
            'priority_areas': [],
            'benchmark_gap': 0,
            'technical_issues': []
        }
        
        # 1. Technical Accuracy Check (new quality dimension)
        if self.quality_analyzer:
            technical_analysis = self.quality_analyzer.analyze_technical_accuracy(
                text, item_data
            )
            
            if technical_analysis['score'] < 70:
                result['needs_improvement'] = True
                result['reasons'].append(f"Technical accuracy low: {technical_analysis['score']:.0f}/100")
                result['technical_issues'] = technical_analysis['issues']
                result['priority_areas'].append('technical_specificity')
        
        # 2. Comparative Benchmarking
        category_benchmark = self._get_category_benchmark(category)
        if category_benchmark:
            benchmark_gap = category_benchmark - base_score
            result['benchmark_gap'] = benchmark_gap
            
            # If more than 15 points below category best, needs improvement
            if benchmark_gap > 15:
                result['needs_improvement'] = True
                result['reasons'].append(
                    f"Score {base_score:.0f} is {benchmark_gap:.0f} points below "
                    f"category benchmark ({category_benchmark:.0f})"
                )
                result['priority_areas'].append('match_category_quality')
        
        # 3. Consistency Check
        if self.quality_analyzer:
            consistency_analysis = self.quality_analyzer.analyze_consistency_with_category(
                text, category, self.domain
            )
            
            if consistency_analysis.get('consistency_score') and consistency_analysis['consistency_score'] < 70:
                result['needs_improvement'] = True
                result['reasons'].append(
                    f"Style inconsistent with category: {consistency_analysis['consistency_score']:.0f}/100"
                )
                result['priority_areas'].extend(['style_consistency'] + consistency_analysis.get('deviations', []))
        
        # 4. Freshness Check
        voice_version = item_data.get('voice_version', 0)
        current_voice_version = self._get_current_voice_version(item_data.get('author', {}).get('id'))
        
        if voice_version and current_voice_version and voice_version < current_voice_version:
            result['needs_improvement'] = True
            result['reasons'].append(
                f"Content uses outdated voice profile v{voice_version} "
                f"(current: v{current_voice_version})"
            )
            result['priority_areas'].append('voice_update')
        
        # Determine improvement strategy
        if result['needs_improvement']:
            if base_score < 60:
                # Very low quality: full regeneration
                result['improvement_strategy'] = 'regenerate'
            elif 60 <= base_score < 85:
                # Moderate quality: targeted refinement
                result['improvement_strategy'] = 'refine'
            else:
                # High quality but specific issues: keep with note
                result['improvement_strategy'] = 'keep_with_note'
        
        return result
    
    def _get_category_benchmark(self, category: str) -> Optional[float]:
        """Get 90th percentile quality score for category"""
        try:
            conn = sqlite3.connect(self.learning_db_path)
            cursor = conn.cursor()
            
            # Try to get from quality evaluations
            cursor.execute('''
                SELECT overall_score FROM quality_evaluations
                WHERE category = ? AND domain = ? AND overall_score IS NOT NULL
                ORDER BY overall_score DESC
            ''', (category, self.domain))
            
            scores = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if len(scores) < 10:  # Need at least 10 samples
                return None
            
            # 90th percentile
            scores.sort()
            index = int(len(scores) * 0.9)
            return scores[index]
            
        except Exception as e:
            logger.debug(f"Could not get category benchmark: {e}")
            return None
    
    def _get_current_voice_version(self, author_id: Optional[int]) -> Optional[int]:
        """Get current voice profile version for author"""
        if not author_id:
            return None
        
        try:
            # Check voice profile metadata for version
            voice_file = Path(f"shared/voice/profiles/author_{author_id}.yaml")
            if voice_file.exists():
                import yaml
                with open(voice_file, 'r') as f:
                    profile = yaml.safe_load(f)
                    return profile.get('version', 1)
        except Exception as e:
            logger.debug(f"Could not get voice version: {e}")
        
        return None
    
    def build_refinement_prompt(
        self,
        existing_content: str,
        priority_areas: List[str],
        technical_issues: List[str]
    ) -> str:
        """
        Build targeted refinement prompt based on identified issues.
        
        Args:
            existing_content: Current content to refine
            priority_areas: List of areas needing improvement
            technical_issues: Specific technical problems found
            
        Returns:
            Refinement prompt string
        """
        improvement_instructions = []
        
        # Map priority areas to specific instructions
        if 'technical_specificity' in priority_areas:
            improvement_instructions.append(
                "- Add more specific technical details and quantitative data"
            )
        
        if 'match_category_quality' in priority_areas:
            improvement_instructions.append(
                "- Enhance overall quality to match best examples in this category"
            )
        
        if 'style_consistency' in priority_areas:
            improvement_instructions.append(
                "- Adjust writing style to match other materials in this category"
            )
        
        if 'voice_update' in priority_areas:
            improvement_instructions.append(
                "- Update voice patterns to current author profile standards"
            )
        
        # Add technical issue fixes
        if technical_issues:
            improvement_instructions.append(
                f"- Address these technical gaps: {', '.join(technical_issues)}"
            )
        
        prompt = f"""CONTENT REFINEMENT TASK

EXISTING CONTENT:
{existing_content}

IMPROVEMENT AREAS:
{chr(10).join(improvement_instructions)}

INSTRUCTIONS:
- Keep the core message and factual accuracy
- Maintain the same approximate length
- Apply the improvements listed above
- Preserve author voice while enhancing quality
- Output ONLY the refined content (no explanations)
"""
        
        return prompt
    
    def log_human_feedback(
        self,
        item_name: str,
        feedback_type: str,
        feedback_text: str,
        reviewer: str = 'user'
    ):
        """
        Log human feedback for learning system.
        
        Args:
            item_name: Name of material/item reviewed
            feedback_type: Type of feedback (generic, technical, readability, etc.)
            feedback_text: Detailed feedback text
            reviewer: Name of reviewer
        """
        try:
            conn = sqlite3.connect(self.learning_db_path)
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS human_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    domain TEXT,
                    field TEXT,
                    item_name TEXT,
                    feedback_type TEXT,
                    feedback_text TEXT,
                    reviewer TEXT
                )
            ''')
            
            cursor.execute('''
                INSERT INTO human_feedback 
                (domain, field, item_name, feedback_type, feedback_text, reviewer)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.domain, self.field, item_name, feedback_type, feedback_text, reviewer))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Human feedback logged for {item_name}: {feedback_type}")
            
        except Exception as e:
            logger.error(f"Failed to log human feedback: {e}")
    
    def get_feedback_patterns(self, item_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve human feedback patterns for learning.
        
        Args:
            item_name: Optional specific item to get feedback for
            
        Returns:
            List of feedback records
        """
        try:
            conn = sqlite3.connect(self.learning_db_path)
            cursor = conn.cursor()
            
            if item_name:
                cursor.execute('''
                    SELECT timestamp, feedback_type, feedback_text, reviewer
                    FROM human_feedback
                    WHERE domain = ? AND field = ? AND item_name = ?
                    ORDER BY timestamp DESC
                ''', (self.domain, self.field, item_name))
            else:
                cursor.execute('''
                    SELECT item_name, timestamp, feedback_type, feedback_text, reviewer
                    FROM human_feedback
                    WHERE domain = ? AND field = ?
                    ORDER BY timestamp DESC
                    LIMIT 50
                ''', (self.domain, self.field))
            
            rows = cursor.fetchall()
            conn.close()
            
            if item_name:
                return [
                    {
                        'timestamp': row[0],
                        'feedback_type': row[1],
                        'feedback_text': row[2],
                        'reviewer': row[3]
                    }
                    for row in rows
                ]
            else:
                return [
                    {
                        'item_name': row[0],
                        'timestamp': row[1],
                        'feedback_type': row[2],
                        'feedback_text': row[3],
                        'reviewer': row[4]
                    }
                    for row in rows
                ]
        
        except Exception as e:
            logger.error(f"Failed to retrieve feedback patterns: {e}")
            return []
