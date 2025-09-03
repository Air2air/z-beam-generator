#!/usr/bin/env python3
"""
Update text component frontmatter with AI detection results
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any
from ai_detection.service import AIDetectionService, AIDetectionResult

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FrontmatterAIDetector:
    """Updates frontmatter with AI detection analysis"""

    def __init__(self):
        self.ai_service = AIDetectionService()
        if not self.ai_service.is_available():
            raise RuntimeError("AI detection service is not available")

    def update_frontmatter_with_ai_detection(self, file_path: str) -> bool:
        """Update frontmatter with AI detection results"""

        try:
            # Read existing file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter and body
            if not content.startswith('---'):
                logger.warning(f"File {file_path} does not have frontmatter")
                return False

            parts = content.split('---', 2)
            if len(parts) < 3:
                logger.warning(f"File {file_path} has malformed frontmatter")
                return False

            frontmatter_text = parts[1]
            body_content = parts[2]

            # Parse existing frontmatter
            frontmatter = yaml.safe_load(frontmatter_text)
            if not frontmatter:
                frontmatter = {}

            # Extract content for AI analysis (skip headers and clean up)
            body_text = self._extract_content_for_analysis(body_content)

            if not body_text or len(body_text.strip()) < 100:
                logger.warning(f"Content too short for AI analysis in {file_path}")
                return False

            # Perform AI detection analysis
            logger.info(f"Analyzing content for AI detection: {Path(file_path).name}")
            ai_result = self.ai_service.analyze_text(body_text)

            # Update frontmatter with AI detection data
            frontmatter['ai_detection_analysis'] = self._build_ai_detection_section(ai_result)

            # Update quality metrics
            if 'quality_metrics' not in frontmatter:
                frontmatter['quality_metrics'] = {}

            frontmatter['quality_metrics'].update(self._build_quality_metrics_update(ai_result))

            # Write updated file
            updated_frontmatter = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False, allow_unicode=True)
            updated_content = f"---\n{updated_frontmatter}---\n{body_content}"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            logger.info(f"✅ Updated frontmatter for {Path(file_path).name}")
            return True

        except Exception as e:
            logger.error(f"❌ Error updating {file_path}: {e}")
            return False

    def _extract_content_for_analysis(self, body_content: str) -> str:
        """Extract clean content for AI analysis"""
        # Remove markdown headers and formatting for cleaner analysis
        lines = body_content.strip().split('\n')
        content_lines = []

        for line in lines:
            line = line.strip()
            # Skip markdown headers, empty lines at start
            if line.startswith('#') or (not content_lines and not line):
                continue
            if line:
                content_lines.append(line)

        return '\n'.join(content_lines)

    def _build_ai_detection_section(self, ai_result: AIDetectionResult) -> Dict[str, Any]:
        """Build the AI detection analysis section"""
        return {
            'enabled': True,
            'provider': ai_result.provider,
            'target_score': 30.0,  # From config
            'final_score': round(ai_result.score, 1),
            'classification': ai_result.classification,
            'confidence': round(ai_result.confidence, 2),
            'processing_time': round(ai_result.processing_time, 2),
            'sentence_level_analysis': {
                'readability_score': ai_result.details.get('readability_score'),
                'credits_used': ai_result.details.get('credits_used', 0),
                'credits_remaining': ai_result.details.get('credits_remaining')
            }
        }

    def _build_quality_metrics_update(self, ai_result: AIDetectionResult) -> Dict[str, Any]:
        """Build quality metrics updates"""
        return {
            'ai_detection_score': round(ai_result.score, 1),
            'ai_classification': ai_result.classification,
            'passes_ai_threshold': ai_result.score <= 30.0
        }

    def update_all_text_components(self, directory: str = "content/components/text") -> Dict[str, int]:
        """Update all text component files with AI detection analysis"""

        text_dir = Path(directory)
        if not text_dir.exists():
            logger.error(f"Directory not found: {directory}")
            return {'total': 0, 'updated': 0, 'failed': 0}

        updated_count = 0
        failed_count = 0
        total_count = 0

        for md_file in text_dir.glob("*.md"):
            total_count += 1
            try:
                success = self.update_frontmatter_with_ai_detection(str(md_file))
                if success:
                    updated_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Failed to update {md_file.name}: {e}")
                failed_count += 1

        results = {
            'total': total_count,
            'updated': updated_count,
            'failed': failed_count
        }

        logger.info("\n📊 AI Detection Frontmatter Update Complete")
        logger.info(f"   Total files: {results['total']}")
        logger.info(f"   Updated: {results['updated']}")
        logger.info(f"   Failed: {results['failed']}")

        return results

def main():
    """Main entry point"""
    try:
        detector = FrontmatterAIDetector()
        results = detector.update_all_text_components()

        if results['updated'] > 0:
            print("🎉 Frontmatter AI detection updates completed successfully!")
        else:
            print("⚠️  No files were updated")

    except Exception as e:
        logger.error(f"Script failed: {e}")
        print(f"❌ Script failed: {e}")

if __name__ == "__main__":
    main()
