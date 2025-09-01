#!/usr/bin/env python3
"""
Human Authenticity Validation Runner

Test and validate the human authenticity of generated content files.
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from validators.human_authenticity_validator import HumanAuthenticityValidator
from validators.content_post_processor import ContentPostProcessor

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def load_author_info(author_id: int) -> Dict:
    """Load author information from JSON file"""
    try:
        import json
        with open('schemas/author.json', 'r') as f:
            authors_data = json.load(f)
        
        # Find author by ID in the examples
        for author in authors_data.get('examples', []):
            if author.get('id') == author_id:
                return author
        
        # Fallback to default
        return {'id': author_id, 'name': 'Unknown', 'country': 'Unknown'}
    except Exception as e:
        logger.error(f"Failed to load author info: {e}")
        return {'id': author_id, 'name': 'Unknown', 'country': 'Unknown'}

def extract_author_from_frontmatter(content: str) -> Dict:
    """Extract author information from content frontmatter"""
    try:
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                import yaml
                frontmatter = yaml.safe_load(parts[1])
                author = frontmatter.get('author', {})
                
                # Try to match with known authors
                author_name = author.get('name', 'Unknown')
                author_country = author.get('country', 'Unknown')
                
                # Map to author IDs (simplified)
                author_mapping = {
                    'Yi-Chun Lin': 1,
                    'Alessandro Moretti': 2,
                    'Ikmanda Roswati': 3,
                    'Todd Dunning': 4
                }
                
                author_id = author_mapping.get(author_name, 1)
                
                return {
                    'id': author_id,
                    'name': author_name,
                    'country': author_country
                }
    except Exception as e:
        logger.warning(f"Failed to extract author from frontmatter: {e}")
    
    return {'id': 1, 'name': 'Unknown', 'country': 'Unknown'}

def validate_single_file(file_path: Path, validator: HumanAuthenticityValidator) -> Dict:
    """Validate a single content file"""
    try:
        # Read content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract material name from filename
        material_name = file_path.stem.replace('-laser-cleaning', '').replace('-', ' ').title()
        
        # Extract author info from frontmatter
        author_info = extract_author_from_frontmatter(content)
        
        # Run validation
        score = validator.validate_content(content, author_info)
        
        return {
            'file_path': file_path,
            'material_name': material_name,
            'author_info': author_info,
            'score': score,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Failed to validate {file_path}: {e}")
        return {
            'file_path': file_path,
            'material_name': 'Unknown',
            'author_info': {'id': 1, 'name': 'Unknown', 'country': 'Unknown'},
            'score': None,
            'success': False,
            'error': str(e)
        }

def validate_content_directory(content_dir: str = "content/components/content") -> List[Dict]:
    """Validate all content files in directory"""
    
    content_path = Path(content_dir)
    if not content_path.exists():
        logger.error(f"Content directory not found: {content_path}")
        return []
    
    # Find all markdown files
    content_files = list(content_path.glob("*.md"))
    
    if not content_files:
        logger.warning(f"No content files found in {content_path}")
        return []
    
    logger.info(f"🔍 Validating {len(content_files)} content files...")
    
    # Initialize validator
    validator = HumanAuthenticityValidator()
    
    results = []
    for file_path in content_files:
        logger.info(f"   📄 Validating: {file_path.name}")
        result = validate_single_file(file_path, validator)
        results.append(result)
        
        if result['success'] and result['score']:
            score = result['score'].overall
            logger.info(f"      📊 Authenticity Score: {score:.1f}/100")
        else:
            logger.warning(f"      ❌ Validation failed")
    
    return results

def generate_summary_report(results: List[Dict]) -> str:
    """Generate a summary report of all validation results"""
    
    successful_results = [r for r in results if r['success'] and r['score']]
    
    if not successful_results:
        return "❌ No successful validations to report"
    
    # Calculate statistics
    scores = [r['score'].overall for r in successful_results]
    avg_score = sum(scores) / len(scores)
    min_score = min(scores)
    max_score = max(scores)
    
    # Count by score ranges
    excellent = len([s for s in scores if s >= 85])
    good = len([s for s in scores if 75 <= s < 85])
    acceptable = len([s for s in scores if 65 <= s < 75])
    needs_improvement = len([s for s in scores if s < 65])
    
    # Author distribution
    author_scores = {}
    for result in successful_results:
        author_name = result['author_info']['name']
        if author_name not in author_scores:
            author_scores[author_name] = []
        author_scores[author_name].append(result['score'].overall)
    
    # Generate report
    report = f"""
# Human Authenticity Validation Summary Report

## Overall Statistics
- **Total Files Validated:** {len(results)}
- **Successful Validations:** {len(successful_results)}
- **Average Authenticity Score:** {avg_score:.1f}/100
- **Score Range:** {min_score:.1f} - {max_score:.1f}

## Score Distribution
- **Excellent (85-100):** {excellent} files ({excellent/len(successful_results)*100:.1f}%)
- **Good (75-84):** {good} files ({good/len(successful_results)*100:.1f}%)
- **Acceptable (65-74):** {acceptable} files ({acceptable/len(successful_results)*100:.1f}%)
- **Needs Improvement (<65):** {needs_improvement} files ({needs_improvement/len(successful_results)*100:.1f}%)

## Author Performance
"""
    
    for author_name, author_score_list in author_scores.items():
        if author_score_list:
            avg_author_score = sum(author_score_list) / len(author_score_list)
            report += f"- **{author_name}:** {avg_author_score:.1f}/100 (n={len(author_score_list)})\n"
    
    # Top and bottom performers
    sorted_results = sorted(successful_results, key=lambda x: x['score'].overall, reverse=True)
    
    report += f"\n## Top Performers\n"
    for i, result in enumerate(sorted_results[:5], 1):
        score = result['score'].overall
        material = result['material_name']
        author = result['author_info']['name']
        report += f"{i}. **{material}** by {author}: {score:.1f}/100\n"
    
    if len(sorted_results) > 5:
        report += f"\n## Areas for Improvement\n"
        for i, result in enumerate(sorted_results[-3:], 1):
            score = result['score'].overall
            material = result['material_name']
            author = result['author_info']['name']
            report += f"{i}. **{material}** by {author}: {score:.1f}/100\n"
    
    return report

def main():
    """Main validation runner"""
    
    print("🚀 HUMAN AUTHENTICITY VALIDATION RUNNER")
    print("=" * 50)
    
    # Validate all content files
    results = validate_content_directory()
    
    if not results:
        print("❌ No files to validate")
        return
    
    # Generate and display summary report
    report = generate_summary_report(results)
    print("\n" + report)
    
    # Save detailed reports
    output_dir = Path("validation_reports")
    output_dir.mkdir(exist_ok=True)
    
    # Save summary report
    summary_file = output_dir / "authenticity_summary.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📊 Summary report saved to: {summary_file}")
    
    # Save individual detailed reports
    validator = HumanAuthenticityValidator()
    successful_results = [r for r in results if r['success'] and r['score']]
    
    for result in successful_results:
        material_name = result['material_name']
        author_info = result['author_info']
        score = result['score']
        
        detailed_report = validator.generate_report(score, material_name, author_info)
        
        # Clean filename
        clean_name = material_name.lower().replace(' ', '-').replace('(', '').replace(')', '')
        report_file = output_dir / f"{clean_name}_authenticity_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(detailed_report)
    
    print(f"📄 {len(successful_results)} detailed reports saved to: {output_dir}/")
    
    # Final assessment
    successful_count = len([r for r in results if r['success']])
    total_count = len(results)
    
    if successful_count == total_count:
        print(f"\n✅ All {total_count} files validated successfully!")
    else:
        failed_count = total_count - successful_count
        print(f"\n⚠️  {successful_count}/{total_count} files validated ({failed_count} failed)")

if __name__ == "__main__":
    main()
