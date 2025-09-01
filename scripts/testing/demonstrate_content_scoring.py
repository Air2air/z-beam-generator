#!/usr/bin/env python3
"""
Content Scoring System Demonstration
Shows how to properly report scores for each content component generation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from components.content.generators.fail_fast_generator import create_fail_fast_generator
from api.client import MockAPIClient

def demonstrate_content_scoring():
    """Demonstrate comprehensive content scoring for all authors."""
    print("📊 Content Component Generation Scoring System")
    print("=" * 60)
    
    # Initialize generator with scoring enabled
    generator = create_fail_fast_generator(
        max_retries=3,
        retry_delay=1.0,
        enable_scoring=True,
        human_threshold=75.0
    )
    
    api_client = MockAPIClient()
    
    # Test all 4 authors with rich material data
    authors = [
        {'id': 1, 'name': 'Dr. Li Wei', 'country': 'Taiwan'},
        {'id': 2, 'name': 'Dr. Marco Rossi', 'country': 'Italy'},
        {'id': 3, 'name': 'Dr. Sari Dewi', 'country': 'Indonesia'},
        {'id': 4, 'name': 'Dr. Sarah Johnson', 'country': 'United States (California)'}
    ]
    
    # Rich material and frontmatter data for comprehensive testing
    material_data = {
        'name': '316L Stainless Steel',
        'formula': 'Fe-18Cr-10Ni-2Mo',
        'category': 'Austenitic Stainless Steel'
    }
    
    frontmatter_data = {
        'title': 'Advanced 316L Stainless Steel Processing',
        'description': 'Comprehensive laser cleaning analysis for medical grade applications',
        'properties': {
            'corrosion_resistance': 'Excellent in chloride environments',
            'surface_finish': 'Mirror-like finish achievable',
            'hardness': '200-250 HV',
            'thermal_conductivity': '16.2 W/m·K'
        },
        'laser_cleaning': {
            'wavelength': '1064nm Nd:YAG',
            'pulse_duration': '10-100ns',
            'power_density': '10^8-10^9 W/cm²',
            'repetition_rate': '1-100 kHz'
        },
        'applications': ['Medical implants', 'Food processing equipment', 'Marine hardware'],
        'contaminants': ['Oxide layers', 'Oil residues', 'Surface contamination']
    }
    
    print(f"🧪 Testing Material: {material_data['name']} ({material_data['formula']})")
    print(f"📋 Frontmatter Elements: {len(frontmatter_data)} categories")
    print()
    
    all_results = []
    
    for i, author in enumerate(authors, 1):
        print(f"👨‍🔬 Author {i}: {author['name']} ({author['country']})")
        print("-" * 40)
        
        try:
            result = generator.generate(
                material_name=material_data['name'],
                material_data=material_data,
                api_client=api_client,
                author_info=author,
                frontmatter_data=frontmatter_data
            )
            
            if result.success:
                print("✅ Generation: SUCCESS")
                
                # Basic metrics from metadata
                metadata = result.metadata
                print(f"📏 Content Length: {metadata.get('word_count', len(result.content.split()))} words")
                print(f"⚡ Generation Method: {metadata.get('generation_method', 'unknown')}")
                
                # Quality scores if available
                if result.quality_score:
                    score = result.quality_score
                    print(f"\n📊 QUALITY SCORES:")
                    print(f"  🎯 Overall Score: {score.overall_score:.1f}/100")
                    print(f"  👤 Human Believability: {score.human_believability:.1f}/100")
                    print(f"  🔬 Technical Accuracy: {score.technical_accuracy:.1f}/100")
                    print(f"  ✍️  Author Authenticity: {score.author_authenticity:.1f}/100")
                    print(f"  📖 Readability: {score.readability_score:.1f}/100")
                    print(f"  📝 Formatting Quality: {score.formatting_quality:.1f}/100")
                    
                    print(f"\n📈 DETAILED METRICS:")
                    print(f"  📄 Sentences: {score.sentence_count}")
                    print(f"  📋 Paragraphs: {score.paragraph_count}")
                    print(f"  📏 Avg Sentence Length: {score.avg_sentence_length:.1f} words")
                    print(f"  🎨 Vocabulary Diversity: {score.vocabulary_diversity:.2f}")
                    print(f"  🔬 Technical Density: {score.technical_density:.2f}")
                    
                    print(f"\n✅ VALIDATION STATUS:")
                    print(f"  🎯 Required Elements: {'✅' if score.has_required_elements else '❌'}")
                    print(f"  👤 Human Threshold: {'✅' if score.passes_human_threshold else '❌'} ({score.human_believability:.1f} >= 75.0)")
                    print(f"  🔄 Retry Recommended: {'❌ Yes' if score.retry_recommended else '✅ No'}")
                    
                    # Detailed breakdown
                    if hasattr(score, 'scoring_breakdown') and score.scoring_breakdown:
                        print(f"\n🔍 DETAILED BREAKDOWN:")
                        
                        # Formatting details
                        fmt_details = score.scoring_breakdown.get('formatting', {}).get('details', {})
                        if fmt_details:
                            print(f"  📝 Formatting:")
                            print(f"    - Title: {'✅' if fmt_details.get('has_title') else '❌'}")
                            print(f"    - Sections: {'✅' if fmt_details.get('has_sections') else '❌'}")
                            print(f"    - Bold Text: {'✅' if fmt_details.get('has_bold_text') else '❌'}")
                            print(f"    - Author Byline: {'✅' if fmt_details.get('has_author_byline') else '❌'}")
                        
                        # Technical details
                        tech_details = score.scoring_breakdown.get('technical_accuracy', {}).get('details', {})
                        if tech_details:
                            print(f"  🔬 Technical:")
                            print(f"    - Formula Present: {'✅' if tech_details.get('formula_present') else '❌'}")
                            print(f"    - Technical Terms: {tech_details.get('technical_term_count', 0)}")
                            print(f"    - Technical Density: {tech_details.get('technical_density', 0):.3f}")
                        
                        # Authenticity details
                        auth_details = score.scoring_breakdown.get('author_authenticity', {}).get('details', {})
                        if auth_details:
                            print(f"  ✍️  Authenticity:")
                            print(f"    - Author Name: {'✅' if auth_details.get('author_name_present') else '❌'}")
                            print(f"    - Country: {'✅' if auth_details.get('country_present') else '❌'}")
                            found_markers = auth_details.get('found_linguistic_markers', [])
                            print(f"    - Linguistic Markers: {len(found_markers)} found")
                            if found_markers:
                                print(f"      {', '.join(found_markers[:3])}{'...' if len(found_markers) > 3 else ''}")
                
                # Show content sample
                print(f"\n📄 CONTENT SAMPLE (first 200 chars):")
                sample = result.content[:200].replace('\n', ' ')
                print(f"  \"{sample}{'...' if len(result.content) > 200 else ''}\"")
                
                all_results.append(result)
                
            else:
                print("❌ Generation: FAILED")
                print(f"💥 Error: {result.error_message}")
            
        except Exception as e:
            print(f"💥 Exception: {e}")
        
        print("\n" + "=" * 60)
        print()
    
    # Summary report
    if all_results:
        print("📋 SUMMARY REPORT")
        print("=" * 60)
        
        successful_generations = len([r for r in all_results if r.success])
        print(f"✅ Successful Generations: {successful_generations}/{len(authors)}")
        
        if all_results[0].quality_score:
            # Average scores
            overall_scores = [r.quality_score.overall_score for r in all_results if r.quality_score]
            human_scores = [r.quality_score.human_believability for r in all_results if r.quality_score]
            tech_scores = [r.quality_score.technical_accuracy for r in all_results if r.quality_score]
            
            print(f"\n📊 AVERAGE SCORES:")
            print(f"  🎯 Overall: {sum(overall_scores)/len(overall_scores):.1f}/100")
            print(f"  👤 Human Believability: {sum(human_scores)/len(human_scores):.1f}/100")
            print(f"  🔬 Technical Accuracy: {sum(tech_scores)/len(tech_scores):.1f}/100")
            
            # Pass rates
            human_passes = sum(1 for r in all_results if r.quality_score and r.quality_score.passes_human_threshold)
            print(f"\n✅ PASS RATES:")
            print(f"  👤 Human Threshold (≥75): {human_passes}/{len(all_results)} ({human_passes/len(all_results)*100:.1f}%)")
            
            # Content metrics
            word_counts = [r.quality_score.word_count for r in all_results if r.quality_score]
            print(f"\n📏 CONTENT METRICS:")
            print(f"  📝 Average Length: {sum(word_counts)/len(word_counts):.0f} words")
            print(f"  📏 Length Range: {min(word_counts)}-{max(word_counts)} words")
        
        print(f"\n🎉 Content scoring system demonstration complete!")
        print(f"🚀 All {successful_generations} authors producing scored, human-believable content!")

if __name__ == "__main__":
    demonstrate_content_scoring()
