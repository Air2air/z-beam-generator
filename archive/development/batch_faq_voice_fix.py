#!/usr/bin/env python3
"""
Batch FAQ Regeneration for Voice Consistency Fix

Regenerates FAQs for materials with voice accuracy issues identified in the
FAQ Human Variation & Enhancement Report.

Priority: Taiwan, Italy, and USA materials with <50% voice accuracy
"""

import yaml
import sys
import subprocess
import time
from pathlib import Path
from collections import defaultdict

def load_materials():
    """Load materials and check voice assignments"""
    with open('data/Materials.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data.get('materials', {})

def analyze_voice_accuracy():
    """Analyze current voice accuracy by author"""
    materials = load_materials()
    
    # Voice indicators for detection
    voice_indicators = {
        'Taiwan': ['systematic', 'methodology', 'precisely', 'comprehensive', 'framework', 'structured', 
                   'rigorous', 'empirical', 'theoretical'],
        'Italy': ['sophisticated', 'elegant', 'refined', 'excellence', 'meticulous', 'artisan', 'mastery',
                  'finesse', 'craftsmanship'],
        'Indonesia': ['practical', 'efficient', 'sustainable', 'effective', 'reliable', 'accessible', 
                      'straightforward', 'cost-effective', 'versatile'],
        'United States': ['innovative', 'performance', 'advanced', 'cutting-edge', 'breakthrough', 
                          'state-of-the-art', 'optimize', 'revolutionary', 'next-generation']
    }
    
    materials_by_author = defaultdict(list)
    voice_mismatches = defaultdict(list)
    
    for material_name, material_data in materials.items():
        if 'faq' not in material_data or not material_data['faq']:
            continue
        
        # Get author country
        author_country = None
        if 'author' in material_data and isinstance(material_data['author'], dict):
            author_country = material_data['author'].get('country', '').split('(')[0].strip()
        
        if not author_country:
            continue
        
        materials_by_author[author_country].append(material_name)
        
        # Check voice consistency
        faqs = material_data['faq']
        all_text = " ".join([f"{item.get('question', '')} {item.get('answer', '')}" for item in faqs])
        text_lower = all_text.lower()
        
        # Count voice indicators
        voice_counts = {}
        for voice, indicators in voice_indicators.items():
            count = sum(1 for word in indicators if word in text_lower)
            if count > 0:
                voice_counts[voice] = count
        
        # Determine if voice matches
        if voice_counts:
            detected_voice = max(voice_counts, key=voice_counts.get)
            if detected_voice != author_country:
                voice_mismatches[author_country].append({
                    'material': material_name,
                    'expected': author_country,
                    'detected': detected_voice,
                    'faq_count': len(faqs)
                })
        else:
            # No voice detected
            voice_mismatches[author_country].append({
                'material': material_name,
                'expected': author_country,
                'detected': 'None',
                'faq_count': len(faqs)
            })
    
    return materials_by_author, voice_mismatches

def main():
    """Main regeneration workflow"""
    print("=" * 80)
    print("FAQ VOICE CONSISTENCY BATCH REGENERATION")
    print("=" * 80)
    print()
    
    # Analyze current state
    print("📊 Analyzing current voice accuracy...")
    materials_by_author, voice_mismatches = analyze_voice_accuracy()
    
    print()
    print("=" * 80)
    print("VOICE ACCURACY ANALYSIS")
    print("=" * 80)
    
    for author in sorted(materials_by_author.keys()):
        total = len(materials_by_author[author])
        mismatches = len(voice_mismatches.get(author, []))
        accuracy = ((total - mismatches) / total * 100) if total > 0 else 0
        
        status = "✅" if accuracy >= 70 else "❌"
        print(f"{status} {author}: {total - mismatches}/{total} ({accuracy:.1f}% accuracy)")
    
    print()
    print("=" * 80)
    print("REGENERATION PRIORITIES")
    print("=" * 80)
    print()
    
    # Priority 1: Taiwan materials (6.6% accuracy)
    taiwan_mismatches = voice_mismatches.get('Taiwan', [])
    print(f"🔴 CRITICAL: Taiwan materials - {len(taiwan_mismatches)} need regeneration")
    
    # Priority 2: Italy materials (3.2% accuracy)
    italy_mismatches = voice_mismatches.get('Italy', [])
    print(f"🔴 CRITICAL: Italy materials - {len(italy_mismatches)} need regeneration")
    
    # Priority 3: USA materials (3.7% accuracy)
    usa_mismatches = voice_mismatches.get('United States', [])
    print(f"🔴 CRITICAL: USA materials - {len(usa_mismatches)} need regeneration")
    
    # Indonesia is good (79% accuracy)
    indonesia_mismatches = voice_mismatches.get('Indonesia', [])
    print(f"✅ MAINTAIN: Indonesia materials - {len(indonesia_mismatches)} need regeneration (minor fixes)")
    
    print()
    total_regenerations = len(taiwan_mismatches) + len(italy_mismatches) + len(usa_mismatches)
    print(f"📊 TOTAL REGENERATIONS NEEDED: {total_regenerations} materials")
    print()
    
    # Ask for confirmation
    response = input("🚀 Start batch regeneration? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cancelled by user")
        return
    
    print()
    print("=" * 80)
    print("BATCH REGENERATION STARTED")
    print("=" * 80)
    print()
    
    # Process in priority order
    all_mismatches = []
    all_mismatches.extend([(m, 'Taiwan') for m in taiwan_mismatches])
    all_mismatches.extend([(m, 'Italy') for m in italy_mismatches])
    all_mismatches.extend([(m, 'United States') for m in usa_mismatches])
    
    success_count = 0
    error_count = 0
    
    for idx, (mismatch, author) in enumerate(all_mismatches, 1):
        material_name = mismatch['material']
        detected = mismatch['detected']
        
        print(f"\n[{idx}/{len(all_mismatches)}] Regenerating: {material_name}")
        print(f"   Author: {author} | Previous voice: {detected}")
        
        try:
            # Run FAQ regeneration
            cmd = ['python3', 'run.py', '--faq', material_name]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"   ✅ Success - FAQ regenerated with {author} voice")
                success_count += 1
            else:
                print(f"   ❌ Failed - Error code {result.returncode}")
                print(f"   Error: {result.stderr[-200:]}")  # Last 200 chars
                error_count += 1
        
        except subprocess.TimeoutExpired:
            print(f"   ⏱️  Timeout after 5 minutes")
            error_count += 1
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            error_count += 1
        
        # Brief pause between materials
        if idx < len(all_mismatches):
            time.sleep(2)
    
    print()
    print("=" * 80)
    print("BATCH REGENERATION COMPLETE")
    print("=" * 80)
    print()
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {error_count}")
    print(f"📊 Total processed: {success_count + error_count}/{len(all_mismatches)}")
    print()
    
    if success_count > 0:
        print("🎯 NEXT STEPS:")
        print("1. Run analysis again to verify voice accuracy improvement")
        print("2. Export updated FAQs to frontmatter: python3 -m components.frontmatter.core.trivial_exporter")
        print("3. Deploy to production: python3 run.py --deploy")
        print()

if __name__ == '__main__':
    main()
