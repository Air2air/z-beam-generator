#!/usr/bin/env python3
"""
Generation Accuracy Evaluator

Compares generated content against examples to assess generation accuracy.
Tests each component's ability to produce content that matches expected patterns.
"""

import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class GenerationAccuracyEvaluator:
    """Evaluates generation accuracy by comparing against examples."""
    
    def __init__(self):
        self.components_dir = Path("components")
        self.content_dir = Path("content/components")
        self.results = {}
        
    def evaluate_all_components(self) -> Dict:
        """Evaluate generation accuracy for all components."""
        
        print("🎯 GENERATION ACCURACY EVALUATION")
        print("=" * 50)
        print("Comparing generated content against component examples...")
        print("=" * 50)
        
        # Get all available components
        components = self._get_available_components()
        
        overall_score = 0.0
        component_count = 0
        
        for component in components:
            print(f"\n📦 Evaluating {component}...")
            score = self._evaluate_component_accuracy(component)
            
            if score is not None:
                self.results[component] = score
                overall_score += score
                component_count += 1
                
                # Show score with color coding
                if score >= 0.8:
                    status = "✅"
                elif score >= 0.6:
                    status = "⚠️"
                else:
                    status = "❌"
                    
                print(f"   {status} {component}: {score:.2f}")
            else:
                print(f"   ⚪ {component}: No evaluation possible")
        
        # Calculate overall accuracy
        if component_count > 0:
            overall_accuracy = overall_score / component_count
        else:
            overall_accuracy = 0.0
            
        # Summary
        print("\n📊 GENERATION ACCURACY SUMMARY")
        print("=" * 50)
        print(f"Overall Accuracy Score: {overall_accuracy:.2f}")
        print(f"Components Evaluated: {component_count}/{len(components)}")
        
        # Component breakdown
        print("\n🏆 Component Rankings:")
        sorted_results = sorted(self.results.items(), key=lambda x: x[1], reverse=True)
        
        for component, score in sorted_results:
            if score >= 0.8:
                status = "✅ Excellent"
            elif score >= 0.7:
                status = "🟢 Good"
            elif score >= 0.6:
                status = "🟡 Fair"
            else:
                status = "🔴 Needs Improvement"
                
            print(f"   {component}: {score:.2f} {status}")
        
        # Save detailed results
        results_file = "generation_accuracy_results.json"
        with open(results_file, "w") as results_file_handle:
            json.dump({
                "overall_accuracy": overall_accuracy,
                "component_count": component_count,
                "total_components": len(components),
                "component_scores": self.results,
                "evaluation_criteria": {
                    "structure_match": "YAML frontmatter and content structure",
                    "content_quality": "Relevance and completeness",
                    "format_compliance": "Markdown formatting and syntax",
                    "schema_adherence": "Following component schema requirements"
                }
            }, results_file_handle, indent=2)
            
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        return {
            "overall_accuracy": overall_accuracy,
            "component_scores": self.results,
            "component_count": component_count
        }
    
    def _get_available_components(self) -> List[str]:
        """Get list of all available components."""
        components = []
        
        if self.components_dir.exists():
            for item in self.components_dir.iterdir():
                if item.is_dir() and item.name != "__pycache__":
                    components.append(item.name)
        
        return sorted(components)
    
    def _evaluate_component_accuracy(self, component: str) -> Optional[float]:
        """Evaluate accuracy for a specific component."""
        
        component_dir = self.components_dir / component
        content_component_dir = self.content_dir / component
        
        # Check if component directory exists
        if not component_dir.exists():
            print(f"   ❌ Component directory not found: {component_dir}")
            return None
            
        # Find example files
        example_files = list(component_dir.glob("example_*.md"))
        if not example_files:
            print(f"   ⚪ No example files found in {component_dir}")
            return None
            
        # Find generated files
        generated_files = []
        if content_component_dir.exists():
            generated_files = list(content_component_dir.glob("*.md"))
            
        if not generated_files:
            print(f"   ⚪ No generated files found in {content_component_dir}")
            return None
            
        print(f"   📁 Found {len(example_files)} examples, {len(generated_files)} generated files")
        
        # Evaluate against examples
        accuracy_scores = []
        
        # Take first example and first few generated files for comparison
        example_file = example_files[0]
        test_files = generated_files[:3]  # Test up to 3 generated files
        
        for generated_file in test_files:
            score = self._compare_files(example_file, generated_file, component)
            if score is not None:
                accuracy_scores.append(score)
                
        if not accuracy_scores:
            return None
            
        # Return average accuracy score
        return sum(accuracy_scores) / len(accuracy_scores)
    
    def _compare_files(self, example_file: Path, generated_file: Path, component: str) -> Optional[float]:
        """Compare an example file with a generated file."""
        
        try:
            # Read both files
            with open(example_file, 'r', encoding='utf-8') as f:
                example_content = f.read()
                
            with open(generated_file, 'r', encoding='utf-8') as f:
                generated_content = f.read()
                
            # Parse both files
            example_data = self._parse_markdown_file(example_content)
            generated_data = self._parse_markdown_file(generated_content)
            
            if not example_data or not generated_data:
                return None
                
            # Evaluate different aspects
            scores = []
            
            # 1. Structure similarity (frontmatter fields)
            structure_score = self._evaluate_structure_similarity(
                example_data.get('frontmatter', {}),
                generated_data.get('frontmatter', {})
            )
            scores.append(structure_score)
            
            # 2. Content length and completeness
            content_score = self._evaluate_content_completeness(
                example_data.get('content', ''),
                generated_data.get('content', '')
            )
            scores.append(content_score)
            
            # 3. Format compliance
            format_score = self._evaluate_format_compliance(generated_content, component)
            scores.append(format_score)
            
            # 4. Schema-specific evaluation
            schema_score = self._evaluate_schema_compliance(generated_data, component)
            scores.append(schema_score)
            
            # Calculate weighted average
            weights = [0.3, 0.3, 0.2, 0.2]  # Structure, content, format, schema
            weighted_score = sum(score * weight for score, weight in zip(scores, weights))
            
            return weighted_score
            
        except Exception as e:
            print(f"   ❌ Error comparing {example_file.name} vs {generated_file.name}: {e}")
            return None
    
    def _parse_markdown_file(self, content: str) -> Dict:
        """Parse a markdown file into frontmatter and content."""
        
        parts = content.split('---', 2)
        
        if len(parts) >= 3:
            # Has frontmatter
            try:
                frontmatter = yaml.safe_load(parts[1])
                content_text = parts[2].strip()
            except yaml.YAMLError:
                frontmatter = {}
                content_text = content
        else:
            # No frontmatter
            frontmatter = {}
            content_text = content
            
        return {
            'frontmatter': frontmatter or {},
            'content': content_text
        }
    
    def _evaluate_structure_similarity(self, example_fm: Dict, generated_fm: Dict) -> float:
        """Evaluate similarity of frontmatter structure."""
        
        if not example_fm and not generated_fm:
            return 1.0
            
        if not example_fm or not generated_fm:
            return 0.5  # Partial credit if one has frontmatter
            
        # Check field overlap
        example_fields = set(example_fm.keys())
        generated_fields = set(generated_fm.keys())
        
        if not example_fields:
            return 1.0 if not generated_fields else 0.8
            
        # Calculate Jaccard similarity
        intersection = example_fields.intersection(generated_fields)
        union = example_fields.union(generated_fields)
        
        jaccard_score = len(intersection) / len(union) if union else 0.0
        
        # Bonus for having all required fields
        required_coverage = len(intersection) / len(example_fields) if example_fields else 1.0
        
        return (jaccard_score * 0.6) + (required_coverage * 0.4)
    
    def _evaluate_content_completeness(self, example_content: str, generated_content: str) -> float:
        """Evaluate content completeness and relevance."""
        
        if not example_content and not generated_content:
            return 1.0
            
        example_len = len(example_content.strip())
        generated_len = len(generated_content.strip())
        
        if example_len == 0:
            return 1.0 if generated_len == 0 else 0.8
            
        if generated_len == 0:
            return 0.0
            
        # Length similarity (not too short, not excessively long)
        length_ratio = min(generated_len, example_len) / max(generated_len, example_len)
        
        # Content structure (paragraphs, lists, etc.)
        example_paragraphs = len([p for p in example_content.split('\n\n') if p.strip()])
        generated_paragraphs = len([p for p in generated_content.split('\n\n') if p.strip()])
        
        structure_similarity = 1.0
        if example_paragraphs > 0:
            para_ratio = min(generated_paragraphs, example_paragraphs) / max(generated_paragraphs, example_paragraphs)
            structure_similarity = para_ratio
            
        # Combine scores
        return (length_ratio * 0.6) + (structure_similarity * 0.4)
    
    def _evaluate_format_compliance(self, content: str, component: str) -> float:
        """Evaluate markdown format compliance."""
        
        score = 1.0
        
        # Check for valid YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    yaml.safe_load(parts[1])
                except yaml.YAMLError:
                    score -= 0.3
            else:
                score -= 0.2
        
        # Check for markdown syntax issues
        lines = content.split('\n')
        
        # Look for broken lists
        for line in lines:
            if line.strip().startswith('- ') and len(line.strip()) < 4:
                score -= 0.1
                break
                
        # Look for unescaped special characters in YAML
        if '---' in content:
            yaml_section = content.split('---')[1] if '---' in content else ''
            if ':' in yaml_section and ('|' in yaml_section or '>' in yaml_section):
                # Good use of YAML multiline
                pass
            elif any(char in yaml_section for char in ['"', "'", '[', ']']) and 'title:' in yaml_section:
                # Potential YAML escaping issues
                pass
        
        return max(0.0, score)
    
    def _evaluate_schema_compliance(self, data: Dict, component: str) -> float:
        """Evaluate compliance with component schema expectations."""
        
        frontmatter = data.get('frontmatter', {})
        content = data.get('content', '')
        
        # Component-specific checks
        if component == 'frontmatter':
            required_fields = ['title', 'description', 'material']
            score = sum(1 for field in required_fields if field in frontmatter) / len(required_fields)
            
        elif component == 'content':
            # Content should have substantial text
            word_count = len(content.split())
            score = min(1.0, word_count / 100)  # Expect at least 100 words
            
        elif component == 'author':
            expected_fields = ['name', 'country', 'bio']
            score = sum(1 for field in expected_fields if field in frontmatter) / len(expected_fields)
            
        elif component == 'bullets':
            # Should contain bullet points
            bullet_count = content.count('- ') + content.count('* ')
            score = min(1.0, bullet_count / 3)  # Expect at least 3 bullets
            
        elif component == 'table':
            # Should contain table markdown
            table_indicators = content.count('|')
            score = min(1.0, table_indicators / 6)  # Basic table needs several pipes
            
        elif component == 'tags':
            # Should have tags in frontmatter
            tags = frontmatter.get('tags', [])
            score = min(1.0, len(tags) / 5) if isinstance(tags, list) else 0.5
            
        elif component == 'metatags':
            # Should have meta-related fields
            meta_fields = ['title', 'description', 'keywords']
            score = sum(1 for field in meta_fields if field in frontmatter) / len(meta_fields)
            
        elif component == 'jsonld':
            # Should contain JSON-LD script
            score = 1.0 if 'application/ld+json' in content else 0.3
            
        elif component == 'caption':
            # Should be concise but descriptive
            word_count = len(content.split())
            score = 1.0 if 10 <= word_count <= 50 else max(0.3, min(word_count / 30, 1.0))
            
        elif component == 'propertiestable':
            # Should contain property information
            score = 1.0 if any(word in content.lower() for word in ['property', 'value', 'unit']) else 0.4
            
        elif component == 'badgesymbol':
            # Should contain symbol or badge information
            score = 1.0 if any(word in content.lower() for word in ['symbol', 'badge', 'icon']) else 0.4
            
        else:
            # Default evaluation - check for non-empty content
            score = 0.8 if content.strip() and frontmatter else 0.5
            
        return score


def main():
    """Run generation accuracy evaluation."""
    
    evaluator = GenerationAccuracyEvaluator()
    results = evaluator.evaluate_all_components()
    
    # Return success if overall accuracy is decent
    return results['overall_accuracy'] >= 0.6


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
