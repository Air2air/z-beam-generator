#!/usr/bin/env python3
"""
Quick Integration: Apply Composite Scoring to Current Content
===========================================================

This script demonstrates how to quickly apply composite scoring to your current
content files without modifying the core system architecture.
"""

import json
import re
from pathlib import Path
from winston_composite_scorer import WinstonCompositeScorer

def apply_composite_scoring_to_content():
    """Apply composite scoring to all current content files and show results"""
    
    content_dir = Path("content/components/text")
    if not content_dir.exists():
        print(f"❌ Content directory not found: {content_dir}")
        return
    
    scorer = WinstonCompositeScorer()
    
    print("🧮 WINSTON.AI COMPOSITE SCORING - QUICK INTEGRATION")
    print("=" * 70)
    print("Applying bias-corrected scoring to current content files...")
    print("=" * 70)
    
    results = []
    
    for md_file in content_dir.glob("*.md"):
        print(f"\n📄 Processing: {md_file.name}")
        
        try:
            # Read file content
            with open(md_file, 'r') as f:
                content = f.read()
            
            # Extract Winston.ai score from metadata
            score_match = re.search(r'score: ([\d.]+)', content)
            if not score_match:
                print("  ⚠️  No Winston.ai score found in metadata")
                continue
                
            original_score = float(score_match.group(1))
            
            # Extract actual text content
            start_marker = '<!-- CONTENT START -->'
            end_marker = '<!-- CONTENT END -->'
            
            start_idx = content.find(start_marker)
            end_idx = content.find(end_marker)
            
            if start_idx == -1 or end_idx == -1:
                print("  ⚠️  Could not find content markers")
                continue
                
            text_content = content[start_idx + len(start_marker):end_idx].strip()
            
            # Create Winston.ai response structure for composite scoring
            winston_response = {
                "score": original_score,
                "details": {
                    "input": text_content,
                    "readability_score": 50.0,  # Default since not always stored
                    "sentences": [],  # Simplified for demo
                    "attack_detected": {"zero_width_space": False, "homoglyph_attack": False},
                    "failing_patterns": {
                        "contains_repetition": False,
                        "uniform_structure": False, 
                        "technical_density": 0.2
                    }
                }
            }
            
            # Calculate composite score
            composite_result = scorer.calculate_composite_score(winston_response)
            
            improvement = composite_result.composite_score - original_score
            
            # Determine status
            if composite_result.composite_score >= 80:
                status = "✅ EXCELLENT"
                status_color = "🟢"
            elif composite_result.composite_score >= 60:
                status = "🟡 GOOD"
                status_color = "🟡"
            elif composite_result.composite_score >= 40:
                status = "🟠 FAIR"
                status_color = "🟠"
            else:
                status = "❌ POOR"
                status_color = "🔴"
            
            print(f"  📊 Winston Raw Score: {original_score:.1f}% human")
            print(f"  🧮 Composite Score: {composite_result.composite_score:.1f}% human")
            print(f"  📈 Improvement: {improvement:+.1f} points")
            print(f"  {status_color} Status: {status}")
            
            # Show technical content adjustment if significant
            tech_adj = composite_result.bias_adjustments.get('technical_bias_correction', 0)
            if tech_adj > 10:
                print(f"  🔧 Technical Bias Correction: +{tech_adj:.1f} points")
            
            results.append({
                'file': md_file.stem,
                'original': original_score,
                'composite': composite_result.composite_score,
                'improvement': improvement,
                'status': status,
                'technical_adjustment': tech_adj
            })
            
        except Exception as e:
            print(f"  ❌ Error processing file: {e}")
    
    # Summary report
    if results:
        print("\n" + "=" * 70)
        print("📊 COMPOSITE SCORING SUMMARY")
        print("=" * 70)
        
        total_files = len(results)
        avg_original = sum(r['original'] for r in results) / total_files
        avg_composite = sum(r['composite'] for r in results) / total_files
        avg_improvement = sum(r['improvement'] for r in results) / total_files
        
        print(f"📁 Files Processed: {total_files}")
        print(f"📈 Average Original Score: {avg_original:.1f}% human")
        print(f"📈 Average Composite Score: {avg_composite:.1f}% human")
        print(f"📈 Average Improvement: {avg_improvement:+.1f} points")
        
        # Count status distribution
        excellent = sum(1 for r in results if r['composite'] >= 80)
        good = sum(1 for r in results if 60 <= r['composite'] < 80)
        fair = sum(1 for r in results if 40 <= r['composite'] < 60)
        poor = sum(1 for r in results if r['composite'] < 40)
        
        print(f"\n🎯 Quality Distribution:")
        print(f"  ✅ Excellent (≥80%): {excellent}/{total_files} ({excellent/total_files*100:.1f}%)")
        print(f"  🟡 Good (60-79%): {good}/{total_files} ({good/total_files*100:.1f}%)")
        print(f"  🟠 Fair (40-59%): {fair}/{total_files} ({fair/total_files*100:.1f}%)")
        print(f"  ❌ Poor (<40%): {poor}/{total_files} ({poor/total_files*100:.1f}%)")
        
        # Identify files with biggest improvements
        biggest_improvement = max(results, key=lambda x: x['improvement'])
        print(f"\n🏆 Biggest Improvement: {biggest_improvement['file']}")
        print(f"   {biggest_improvement['original']:.1f}% → {biggest_improvement['composite']:.1f}% "
              f"({biggest_improvement['improvement']:+.1f} points)")
        
        # Identify files still needing work
        needs_work = [r for r in results if r['composite'] < 60]
        if needs_work:
            print(f"\n⚠️  Files Still Needing Optimization:")
            for file_result in needs_work:
                print(f"   • {file_result['file']}: {file_result['composite']:.1f}% human")
        
        # Technical bias correction summary
        high_tech_adj = [r for r in results if r['technical_adjustment'] > 20]
        if high_tech_adj:
            print(f"\n🔧 Significant Technical Bias Corrections:")
            for file_result in high_tech_adj:
                print(f"   • {file_result['file']}: +{file_result['technical_adjustment']:.1f} points")
        
        print(f"\n💡 Next Steps:")
        if avg_composite >= 80:
            print("   ✅ All content scoring well with composite method")
            print("   🔄 Consider integrating composite scoring into optimization workflow")
        elif avg_composite >= 60:
            print("   🟡 Good results, consider fine-tuning composite algorithm")
            print("   🔧 Focus optimization on files scoring below 60%")
        else:
            print("   🟠 Additional optimization needed even with composite scoring")
            print("   🔍 Review technical keyword detection and bias correction factors")

def export_composite_scores():
    """Export composite scores to JSON for integration with other tools"""
    # This could be extended to save results for integration
    pass

if __name__ == "__main__":
    apply_composite_scoring_to_content()
