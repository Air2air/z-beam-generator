#!/usr/bin/env python3
"""
Prompt Evolution Manager

Manages the evolution history and statistics for the dynamic prompt system.
Tracks improvements, versions, and provides analytics for prompt evolution.
"""

import logging
import json
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class PromptEvolutionManager:
    """
    Manages the evolution history and provides analytics for prompt improvements.
    """

    def __init__(self, prompts_path: str):
        """
        Initialize the evolution manager.

        Args:
            prompts_path: Path to the prompts file for tracking
        """
        self.prompts_path = Path(prompts_path)
        self.history_file = self.prompts_path.parent / "evolution_history.json"
        self.evolution_history = self._load_history()

    def record_evolution(self, winston_result: Dict[str, Any],
                        improvements: Dict[str, Any], applied: bool) -> None:
        """
        Record a prompt evolution event.

        Args:
            winston_result: The Winston analysis that triggered evolution
            improvements: The improvements that were generated
            applied: Whether the improvements were actually applied
        """
        evolution_record = {
            'timestamp': datetime.now().isoformat(),
            'winston_score': winston_result.get('overall_score', 0),
            'winston_classification': winston_result.get('classification', 'unknown'),
            'improvements_generated': len(improvements) if improvements else 0,
            'improvements_applied': applied,
            'target_sections': list(improvements.keys()) if improvements else [],
            'version': len(self.evolution_history) + 1
        }

        self.evolution_history.append(evolution_record)
        self._save_history()

        logger.info(f"📝 Recorded evolution: Score {evolution_record['winston_score']}, "
                   f"Applied: {applied}, Sections: {len(evolution_record['target_sections'])}")

    def get_history(self) -> List[Dict[str, Any]]:
        """Get the complete evolution history."""
        return self.evolution_history.copy()

    def get_recent_evolutions(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get the most recent evolution records."""
        return self.evolution_history[-count:] if self.evolution_history else []

    def get_evolution_stats(self) -> Dict[str, Any]:
        """Get statistics about the evolution process."""
        if not self.evolution_history:
            return {
                'total_evolutions': 0,
                'average_score': 0,
                'success_rate': 0,
                'most_targeted_sections': []
            }

        total_evolutions = len(self.evolution_history)
        applied_evolutions = len([e for e in self.evolution_history if e['improvements_applied']])
        success_rate = applied_evolutions / total_evolutions if total_evolutions > 0 else 0

        scores = [e['winston_score'] for e in self.evolution_history]
        average_score = sum(scores) / len(scores) if scores else 0

        # Count section targeting frequency
        section_counts = {}
        for evolution in self.evolution_history:
            for section in evolution['target_sections']:
                section_counts[section] = section_counts.get(section, 0) + 1

        most_targeted = sorted(section_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'total_evolutions': total_evolutions,
            'applied_evolutions': applied_evolutions,
            'success_rate': round(success_rate * 100, 1),
            'average_score': round(average_score, 1),
            'most_targeted_sections': most_targeted,
            'score_trend': self._calculate_score_trend()
        }

    def get_evolution_by_section(self, section_name: str) -> List[Dict[str, Any]]:
        """Get evolution history for a specific section."""
        return [e for e in self.evolution_history if section_name in e['target_sections']]

    def get_score_improvements(self) -> List[Dict[str, Any]]:
        """Get evolutions that resulted in score improvements."""
        improvements = []
        sorted_history = sorted(self.evolution_history, key=lambda x: x['timestamp'])

        for i in range(1, len(sorted_history)):
            current = sorted_history[i]
            previous = sorted_history[i-1]

            if current['winston_score'] > previous['winston_score']:
                improvement = {
                    'evolution': current,
                    'score_improvement': current['winston_score'] - previous['winston_score'],
                    'previous_score': previous['winston_score']
                }
                improvements.append(improvement)

        return improvements

    def _calculate_score_trend(self) -> str:
        """Calculate the overall score trend."""
        if len(self.evolution_history) < 2:
            return "insufficient_data"

        scores = [e['winston_score'] for e in self.evolution_history[-10:]]  # Last 10 evolutions
        if len(scores) < 2:
            return "insufficient_data"

        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]

        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)

        if second_avg > first_avg + 2:
            return "improving"
        elif second_avg < first_avg - 2:
            return "declining"
        else:
            return "stable"

    def _load_history(self) -> List[Dict[str, Any]]:
        """Load evolution history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.warning(f"Failed to load evolution history: {e}")
            return []

    def _save_history(self) -> None:
        """Save evolution history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.evolution_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save evolution history: {e}")

    def clear_history(self) -> None:
        """Clear the evolution history."""
        self.evolution_history = []
        self._save_history()
        logger.info("🗑️ Evolution history cleared")

    def export_history(self, filepath: str) -> bool:
        """Export evolution history to a specified file."""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'prompts_file': str(self.prompts_path),
                'total_evolutions': len(self.evolution_history),
                'evolution_history': self.evolution_history,
                'statistics': self.get_evolution_stats()
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"📤 Evolution history exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export evolution history: {e}")
            return False
