#!/usr/bin/env python3
"""
Quick Text Quality Test

Test any text sample for AI detection, Winston score, and voice quality.

Usage:
    # Test existing field from frontmatter
    python3 scripts/tools/quick_text_test.py

    # Test custom text
    python3 scripts/tools/quick_text_test.py --text "Your text here" --author 2

    # Test from file
    python3 scripts/tools/quick_text_test.py --file path/to/text.txt --author 1
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import argparse
import yaml
from shared.voice.enhanced_ai_detector import EnhancedAIDetector
from shared.voice.quality_analyzer import QualityAnalyzer
from postprocessing.detection.winston_integration import WinstonIntegration


def get_frontmatter_field(material_slug: str, field_path: str) -> str:
    """
    Get a field from frontmatter YAML.
    field_path examples:
        - "laserMaterialInteraction._section.sectionDescription"
        - "components.subtitle"
        - "metaDescription"
    """
    frontmatter_path = f'../z-beam/frontmatter/materials/{material_slug}.yaml'
    
    with open(frontmatter_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Navigate the path
    parts = field_path.split('.')
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    
    return str(current) if current else None


def analyze_text(text: str, author_id: int = 1, component_type: str = 'description'):
    """Run all quality checks on text"""
    
    print("\n" + "="*80)
    print("📊 TEXT QUALITY ANALYSIS")
    print("="*80)
    
    # Display text
    print("\n📝 TEXT SAMPLE:")
    print("-" * 80)
    print(text)
    print("-" * 80)
    print(f"Length: {len(text)} characters, {len(text.split())} words\n")
    
    # 1. AI Detection (Enhanced)
    print("🔍 Running AI Detection...")
    detector = EnhancedAIDetector()
    ai_result = detector.analyze(text, component_type=component_type)
    
    print(f"\n🤖 AI DETECTION (Enhanced):")
    print(f"   Human Score: {ai_result.get('human_score', 0):.1f}%")
    print(f"   Status: {'✅ PASS' if ai_result.get('human_score', 0) >= 90 else '⚠️  WARNING' if ai_result.get('human_score', 0) >= 70 else '❌ FAIL'}")
    
    if ai_result.get('telltale_phrases_found'):
        print(f"   🚨 Telltale AI Phrases: {', '.join(ai_result['telltale_phrases_found'])}")
    
    if ai_result.get('structural_issues'):
        print(f"   ⚠️  Structural Issues: {len(ai_result['structural_issues'])}")
        for issue in ai_result['structural_issues'][:3]:  # Show first 3
            print(f"      - {issue}")
    
    # 2. Winston API
    print(f"\n🔍 Running Winston API...")
    try:
        winston = WinstonIntegration()
        winston_result = winston.check_ai_score(text)
        score = winston_result.get('human_score', 0)
        
        print(f"\n🎯 WINSTON API:")
        print(f"   Score: {score:.1f}% human")
        print(f"   Status: {'✅ PASS' if score >= 69 else '❌ FAIL'}")
        print(f"   Threshold: 69% (required)")
    except Exception as e:
        print(f"\n🎯 WINSTON API:")
        print(f"   ⚠️  Error: {str(e)}")
    
    # 3. Voice Quality
    print(f"\n🔍 Running Voice Quality Analysis...")
    try:
        analyzer = QualityAnalyzer()
        quality = analyzer.analyze_quality(
            text=text,
            author_id=author_id,
            component_type=component_type
        )
        
        print(f"\n🗣️  VOICE QUALITY:")
        print(f"   Voice Authenticity: {quality.get('voice_authenticity', 0):.1f}/100")
        print(f"   Pattern Compliance: {quality.get('pattern_compliance', 'N/A')}")
        print(f"   Tonal Consistency: {quality.get('tonal_consistency', 0):.1f}/100")
        print(f"   Overall Score: {quality.get('overall_score', 0):.1f}/100")
        
        if quality.get('issues'):
            print(f"   ⚠️  Issues Found: {len(quality['issues'])}")
            for issue in quality['issues'][:3]:
                print(f"      - {issue}")
    except Exception as e:
        print(f"\n🗣️  VOICE QUALITY:")
        print(f"   ⚠️  Error: {str(e)}")
    
    print("\n" + "="*80)


def main():
    parser = argparse.ArgumentParser(description='Quick text quality test')
    parser.add_argument('--text', help='Text to analyze')
    parser.add_argument('--file', help='File containing text to analyze')
    parser.add_argument('--material', help='Material slug (e.g., aluminum-laser-cleaning)')
    parser.add_argument('--field', help='Field path (e.g., laserMaterialInteraction._section.sectionDescription)')
    parser.add_argument('--author', type=int, default=1, help='Author ID (1=Taiwan, 2=Italy, 3=Indonesia, 4=USA)')
    parser.add_argument('--component', default='description', help='Component type (description, micro, etc.)')
    
    args = parser.parse_args()
    
    try:
        # Get text from source
        if args.text:
            text = args.text
            print(f"📄 Source: Direct input")
        elif args.file:
            with open(args.file, 'r') as f:
                text = f.read().strip()
            print(f"📄 Source: {args.file}")
        elif args.material and args.field:
            text = get_frontmatter_field(args.material, args.field)
            if not text:
                print(f"❌ Error: Field '{args.field}' not found in {args.material}")
                sys.exit(1)
            print(f"📄 Source: {args.material} -> {args.field}")
        else:
            # Interactive mode
            print("📝 No source specified. Enter text to analyze (Ctrl+D when done):")
            text = sys.stdin.read().strip()
            print(f"📄 Source: stdin")
        
        if not text:
            print("❌ Error: No text to analyze")
            sys.exit(1)
        
        # Analyze
        analyze_text(text, args.author, args.component)
        
        print("✅ Analysis complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
