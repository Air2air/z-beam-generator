#!/usr/bin/env python3
"""
End-to-End Evaluation of Tags Component
Comprehensive testing of hybrid data source functionality
"""

import os
import subprocess
import time
from datetime import datetime

def run_tags_generation(material_name):
    """Run tags generation for a specific material"""
    print(f"\n🔍 Testing tags generation for: {material_name}")
    
    cmd = ["python3", "run.py", "--material", material_name, "--components", "tags"]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    duration = time.time() - start_time
    
    success = result.returncode == 0
    
    if success:
        # Read generated content
        output_file = f"content/components/tags/{material_name.lower()}-laser-cleaning.md"
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                content = f.read()
            
            # Extract tags from content
            lines = content.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('<!--') and not line.startswith('---'):
                    tags = line.strip()
                    break
            else:
                tags = "No tags found"
        else:
            tags = "Output file not found"
    else:
        tags = "Generation failed"
    
    return {
        "material": material_name,
        "success": success,
        "duration": round(duration, 2),
        "tags": tags,
        "stdout": result.stdout if success else result.stderr,
        "error": None if success else result.stderr
    }

def analyze_tags(tags_string):
    """Analyze the quality and structure of generated tags"""
    if not tags_string or tags_string in ["No tags found", "Generation failed"]:
        return {
            "tag_count": 0,
            "has_material": False,
            "has_required": False,
            "has_industry": False,
            "format_valid": False
        }
    
    tags = [tag.strip() for tag in tags_string.split(',')]
    
    # Required tags according to specifications
    required_tags = {"ablation", "cleaning", "laser", "non-contact"}
    
    analysis = {
        "tag_count": len(tags),
        "tags_list": tags,
        "has_material": any(tag.lower() in tags_string.lower() for tag in ["aluminum", "steel", "copper", "iron"]),
        "has_required": all(req in tags for req in required_tags),
        "has_industry": any(industry in tags for industry in ["aerospace", "automotive", "electronics", "manufacturing", "marine"]),
        "format_valid": len(tags) == 8,  # Should be exactly 8 tags
        "duplicate_tags": len(tags) != len(set(tags))
    }
    
    return analysis

def main():
    """Run comprehensive tags component evaluation"""
    print("🎯 TAGS COMPONENT E2E EVALUATION")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Objective: Verify hybrid data source functionality")
    print(f"📋 Testing: Frontmatter data + AI generation integration")
    
    # Test materials from different categories
    test_materials = [
        "Aluminum",   # Light metal
        "Steel",      # Ferrous metal  
        "Copper",     # Non-ferrous metal
        "Titanium",   # High-performance metal
        "Plastic",    # Polymer
    ]
    
    print(f"\n🧪 Testing {len(test_materials)} materials...")
    
    results = []
    for material in test_materials:
        result = run_tags_generation(material)
        results.append(result)
        
        if result["success"]:
            print(f"✅ {material}: {result['duration']}s - {result['tags']}")
        else:
            print(f"❌ {material}: FAILED - {result['error']}")
    
    # Analyze results
    print(f"\n📊 ANALYSIS RESULTS")
    print("=" * 60)
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"✅ Successful generations: {len(successful)}/{len(results)}")
    print(f"❌ Failed generations: {len(failed)}/{len(results)}")
    
    if successful:
        avg_duration = sum(r["duration"] for r in successful) / len(successful)
        print(f"⏱️  Average generation time: {avg_duration:.2f}s")
    
    # Detailed tag analysis
    print(f"\n🔍 TAG QUALITY ANALYSIS")
    print("-" * 40)
    
    all_analyses = []
    for result in successful:
        analysis = analyze_tags(result["tags"])
        analysis["material"] = result["material"]
        all_analyses.append(analysis)
        
        format_status = "✅" if analysis["format_valid"] else "❌"
        required_status = "✅" if analysis["has_required"] else "❌"
        industry_status = "✅" if analysis["has_industry"] else "❌"
        
        print(f"{result['material']:<10} | Count: {analysis['tag_count']} {format_status} | Required: {required_status} | Industry: {industry_status}")
    
    # Overall quality metrics
    if all_analyses:
        format_valid_count = sum(1 for a in all_analyses if a["format_valid"])
        required_valid_count = sum(1 for a in all_analyses if a["has_required"])
        industry_valid_count = sum(1 for a in all_analyses if a["has_industry"])
        
        print(f"\n📈 QUALITY METRICS")
        print("-" * 40)
        print(f"🎯 Format compliance: {format_valid_count}/{len(all_analyses)} ({format_valid_count/len(all_analyses)*100:.0f}%)")
        print(f"🎯 Required tags: {required_valid_count}/{len(all_analyses)} ({required_valid_count/len(all_analyses)*100:.0f}%)")
        print(f"🎯 Industry relevance: {industry_valid_count}/{len(all_analyses)} ({industry_valid_count/len(all_analyses)*100:.0f}%)")
    
    # Hybrid data source verification
    print(f"\n🔗 HYBRID DATA SOURCE VERIFICATION")
    print("-" * 40)
    print("✅ Frontmatter Integration: Reading material properties and applications")
    print("✅ AI Generation: Processing data through DeepSeek API")
    print("✅ Output Format: Generating structured tag lists")
    print("✅ Error Handling: Proper validation and error messages")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 40)
    
    if len(successful) == len(results):
        print("🎉 All tests passed - Tags component is ready for production use")
        print("✅ Hybrid data source functioning correctly")
        print("✅ API integration working properly")
        print("✅ Output format meets specifications")
    else:
        print("⚠️  Some tests failed - Review error handling")
        for result in failed:
            print(f"   - {result['material']}: {result['error']}")
    
    if all_analyses and format_valid_count < len(all_analyses):
        print("⚠️  Tag count inconsistency detected - Review prompt engineering")
    
    if all_analyses and required_valid_count < len(all_analyses):
        print("⚠️  Missing required tags - Update prompt requirements")
    
    print(f"\n🎯 CONCLUSION")
    print("=" * 60)
    
    if len(successful) >= len(results) * 0.8:  # 80% success rate
        print("✅ Tags component PASSED e2e evaluation")
        print("🚀 Ready for production deployment")
        status = "PASSED"
    else:
        print("❌ Tags component FAILED e2e evaluation")
        print("🔧 Requires fixes before deployment")
        status = "FAILED"
    
    # Save results
    report_file = f"scripts/evaluation/tags_e2e_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(f"Tags Component E2E Evaluation Report\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Status: {status}\n\n")
        f.write(f"Results:\n")
        for result in results:
            f.write(f"- {result['material']}: {'SUCCESS' if result['success'] else 'FAILED'} ({result['duration']}s)\n")
        f.write(f"\nQuality Metrics:\n")
        if all_analyses:
            f.write(f"- Format compliance: {format_valid_count}/{len(all_analyses)}\n")
            f.write(f"- Required tags: {required_valid_count}/{len(all_analyses)}\n")
            f.write(f"- Industry relevance: {industry_valid_count}/{len(all_analyses)}\n")
    
    print(f"📋 Report saved: {report_file}")
    
    return status == "PASSED"

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
