#!/usr/bin/env python3
"""
Author Info Debug Test
Debug what author information is being passed to the scoring system
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def debug_author_info_scoring():
    """Debug the exact author info being passed to scoring"""
    logger.info("🔍 Debugging author info scoring...")
    
    try:
        from components.content.validation.content_scorer import ContentQualityScorer
        
        # Test content
        test_content = """# Laser Cleaning of Alumina: Technical Analysis

**Alessandro Moretti, Ph.D. - Italy**

# Laser Cleaning of Alumina (Al2O3) for Advanced Applications

## Material Overview and Properties
Alumina (Al2O3) is a high-performance technical ceramic distinguished by its exceptional hardness, high melting point (~2072°C), and excellent chemical inertness. The engineering precision required for laser cleaning this material demands sophisticated understanding of thermal dynamics and optical interactions.

## Industrial Applications
Alumina finds extensive use in aerospace applications (insulating substrates, sensor housings), automotive systems (spark plug insulators, wear-resistant components), and heritage preservation (cleaning archaeological ceramics without abrasion). The precision manufacturing processes used in these industries require innovation in cleaning methodologies.

## Laser Cleaning Interaction and Parameters
The engineering challenges of laser cleaning Al2O3 require methodical analysis due to its high ablation threshold. Advanced pulsed laser systems, typically operating at 1064nm wavelength, provide the precision necessary for contaminant removal without substrate damage.
"""
        
        # Test different author_info configurations
        test_cases = [
            # Case 1: Minimal info (what's currently being passed)
            {'id': 2},
            
            # Case 2: With country  
            {'id': 2, 'country': 'italy'},
            
            # Case 3: With name
            {'id': 2, 'name': 'Alessandro Moretti'},
            
            # Case 4: With both name and country
            {'id': 2, 'name': 'Alessandro Moretti', 'country': 'italy'},
            
            # Case 5: With proper country capitalization
            {'id': 2, 'name': 'Alessandro Moretti', 'country': 'Italy'},
            
            # Case 6: Complete author info
            {'id': 2, 'name': 'Alessandro Moretti', 'country': 'Italy', 'title': 'Ph.D.'}
        ]
        
        scorer = ContentQualityScorer()
        
        for i, author_info in enumerate(test_cases, 1):
            logger.info(f"\n📋 TEST CASE {i}: {author_info}")
            
            # Calculate author authenticity score
            auth_score = scorer._score_author_authenticity(test_content, author_info)
            logger.info(f"🎯 Author authenticity score: {auth_score}/100")
            
            # Break down the scoring
            content_lower = test_content.lower()
            author_country = author_info.get('country', '').lower()
            
            # Map country to marker key
            country_mapping = {
                'taiwan': 'taiwan',
                'italy': 'italy', 
                'indonesia': 'indonesia',
                'united states': 'usa',
                'united states (california)': 'usa'
            }
            
            marker_key = country_mapping.get(author_country, 'usa')
            expected_markers = scorer.author_markers.get(marker_key, [])
            
            logger.info(f"  📍 Country from info: '{author_country}'")
            logger.info(f"  🗝️  Marker key: '{marker_key}'")
            logger.info(f"  📋 Expected markers: {expected_markers}")
            
            # Check markers
            markers_found = sum(1 for marker in expected_markers if marker in content_lower)
            if expected_markers:
                marker_ratio = markers_found / len(expected_markers)
                marker_points = marker_ratio * 40
                logger.info(f"  ✅ Markers found: {markers_found}/{len(expected_markers)} = {marker_ratio:.1%}")
                logger.info(f"  📊 Marker points: {marker_points:.1f}/40")
            else:
                marker_points = 0
                logger.info(f"  ❌ No expected markers for key '{marker_key}'")
            
            # Check author name
            author_name = author_info.get('name', '')
            name_in_content = author_name and author_name in test_content
            name_points = 30 if name_in_content else 0
            logger.info(f"  👤 Author name '{author_name}' in content: {name_in_content} = {name_points}/30")
            
            # Check country attribution  
            country_display = author_info.get('country', '')
            country_in_content = country_display and country_display in test_content
            country_points = 30 if country_in_content else 0
            logger.info(f"  🌍 Country '{country_display}' in content: {country_in_content} = {country_points}/30")
            
            # Total calculation
            total_calculated = marker_points + name_points + country_points
            logger.info(f"  🧮 Manual calculation: {marker_points:.1f} + {name_points} + {country_points} = {total_calculated:.1f}")
            logger.info(f"  🎯 Scorer result: {auth_score:.1f}")
            
            if abs(total_calculated - auth_score) > 0.1:
                logger.warning(f"  ⚠️  Calculation mismatch!")
        
    except Exception as e:
        logger.error(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

def check_current_author_info_usage():
    """Check how author_info is currently being passed in the generator"""
    logger.info("🔍 Checking current author_info usage...")
    
    try:
        # Look at how the generator creates author_info
        from components.content.generator import ContentComponentGenerator
        
        logger.info("📋 Examining ContentComponentGenerator.generate() method...")
        
        # Check the generated content files to see what author info was used
        content_files = {
            'content/alumina-laser-cleaning.md': 'Italy/Alessandro Moretti',
            'content/porcelain-laser-cleaning.md': 'Indonesia/Ikmanda Roswati', 
            'content/silicon-nitride-laser-cleaning.md': 'Taiwan/Yi-Chun Lin'
        }
        
        for file_path, expected_author in content_files.items():
            logger.info(f"\n📄 Analyzing {file_path}")
            logger.info(f"🎯 Expected: {expected_author}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter author info
            import re
            country_match = re.search(r'country:\s*"([^"]+)"', content)
            author_match = re.search(r'author:\s*"([^"]+)"', content)
            
            if country_match and author_match:
                country = country_match.group(1)
                author = author_match.group(1)
                logger.info(f"  📍 Frontmatter country: '{country}'")
                logger.info(f"  👤 Frontmatter author: '{author}'")
                
                # Check if these appear in content body
                if '---' in content:
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        body_content = parts[2].strip()
                        country_in_body = country in body_content
                        author_in_body = author in body_content
                        logger.info(f"  🌍 Country in body: {country_in_body}")
                        logger.info(f"  👤 Author in body: {author_in_body}")
            else:
                logger.warning(f"  ⚠️  Could not extract author info from frontmatter")
        
    except Exception as e:
        logger.error(f"❌ Check failed: {e}")

def main():
    """Run author info debugging"""
    logger.info("🚀 Starting author info debugging")
    logger.info("="*60)
    
    # Test 1: Debug scoring with different author info
    logger.info("\n1️⃣ TESTING AUTHOR INFO SCORING")
    debug_author_info_scoring()
    
    # Test 2: Check current usage
    logger.info("\n2️⃣ CHECKING CURRENT USAGE")
    check_current_author_info_usage()
    
    logger.info("\n" + "="*60)
    logger.info("🎯 AUTHOR INFO DEBUGGING COMPLETE")

if __name__ == "__main__":
    main()
