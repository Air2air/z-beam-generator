#!/usr/bin/env python3
"""
Contaminants Laser Properties Research Script

Researches complete laser property profiles for all contamination patterns.
Uses LaserPropertiesResearcher with Grok API to gather scientific data.

Usage:
    python3 research_contaminants.py --all                    # Research all patterns
    python3 research_contaminants.py --pattern rust_oxidation # Research specific pattern
    python3 research_contaminants.py --dry-run               # Preview without saving
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from shared.data.loader_factory import ContaminantsDataLoader

# Initialize loader - PatternDataLoader alias
PatternDataLoader = ContaminantsDataLoader
from domains.contaminants.research.laser_properties_researcher import (
    LaserPropertiesResearcher,
    ContaminationResearchSpec
)
from shared.api.client_factory import create_api_client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class ContaminantsResearchOrchestrator:
    """Orchestrates research for all contamination patterns."""
    
    def __init__(self, api_client, dry_run: bool = False):
        self.api_client = api_client
        self.dry_run = dry_run
        self.loader = PatternDataLoader()
        
    def research_pattern(self, pattern_id: str) -> bool:
        """
        Research complete laser properties for a single pattern.
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("=" * 80)
            logger.info(f"🔬 RESEARCHING PATTERN: {pattern_id}")
            logger.info("=" * 80)
            
            # Get pattern data
            pattern = self.loader.get_pattern(pattern_id)
            if not pattern:
                logger.error(f"❌ Pattern '{pattern_id}' not found")
                return False
            
            pattern_name = pattern.get('name', pattern_id)
            logger.info(f"📋 Pattern: {pattern_name}")
            logger.info(f"🆔 ID: {pattern_id}\n")
            
            # Research all property types
            research_types = [
                'optical_properties',
                'thermal_properties',
                'removal_characteristics',
                'layer_properties',
                'laser_parameters',
                'safety_data',
                'selectivity_ratios'
            ]
            
            results = {}
            for research_type in research_types:
                logger.info(f"\n📊 Researching: {research_type}")
                logger.info("-" * 80)
                
                # Create research spec
                composition = pattern.get('composition', [])
                material_context = composition[0] if composition else None
                
                spec = ContaminationResearchSpec(
                    pattern_id=pattern_id,
                    research_type=research_type,
                    material_context=material_context
                )
                
                # Create researcher directly
                researcher = LaserPropertiesResearcher(self.api_client)
                
                # Perform research
                try:
                    result = researcher.research(pattern_id, spec)
                    
                    if result.success:
                        logger.info(f"✅ Success: {research_type}")
                        logger.info(f"   Confidence: {result.confidence:.2%}")
                        logger.info(f"   Data points: {len(result.data)}")
                        results[research_type] = result.data
                    else:
                        logger.warning(f"⚠️  Partial: {research_type}")
                        logger.warning(f"   Issues: {', '.join(result.issues)}")
                        results[research_type] = result.data
                        
                except Exception as e:
                    logger.error(f"❌ Failed: {research_type}")
                    logger.error(f"   Error: {str(e)}")
                    results[research_type] = None
            
            # Save results
            if not self.dry_run:
                logger.info("\n" + "=" * 80)
                logger.info("💾 SAVING RESULTS")
                logger.info("=" * 80)
                
                # Update pattern with researched data
                updated_pattern = pattern.copy()
                for research_type, data in results.items():
                    if data:
                        updated_pattern[research_type] = data
                
                # Save to Contaminants.yaml
                self.loader.save_pattern(pattern_id, updated_pattern)
                logger.info(f"✅ Saved to data/contaminants/Contaminants.yaml")
            else:
                logger.info("\n🔍 DRY RUN - Results not saved")
            
            logger.info("\n" + "=" * 80)
            logger.info(f"✅ COMPLETED: {pattern_id}")
            logger.info("=" * 80 + "\n")
            
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"❌ FAILED: {pattern_id}")
            logger.error(f"   Error: {str(e)}")
            logger.error(f"   Traceback:\n{traceback.format_exc()}")
            return False
    
    def research_all_patterns(self) -> Dict[str, bool]:
        """
        Research all contamination patterns.
        
        Returns:
            Dict mapping pattern_id to success status
        """
        pattern_ids = self.loader.get_all_patterns()
        
        logger.info("🚀 STARTING BULK RESEARCH")
        logger.info("=" * 80)
        logger.info(f"📋 Patterns to research: {len(pattern_ids)}")
        logger.info(f"🔬 Research types per pattern: 7")
        logger.info(f"📊 Total research operations: {len(pattern_ids) * 7}")
        logger.info("=" * 80 + "\n")
        
        results = {}
        for i, pattern_id in enumerate(pattern_ids, 1):
            logger.info(f"\n{'=' * 80}")
            logger.info(f"PATTERN {i}/{len(pattern_ids)}")
            logger.info('=' * 80 + "\n")
            
            results[pattern_id] = self.research_pattern(pattern_id)
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 RESEARCH SUMMARY")
        logger.info("=" * 80)
        
        successful = sum(1 for success in results.values() if success)
        failed = len(results) - successful
        
        logger.info(f"✅ Successful: {successful}/{len(results)}")
        logger.info(f"❌ Failed: {failed}/{len(results)}")
        
        if failed > 0:
            logger.info("\n❌ Failed patterns:")
            for pattern_id, success in results.items():
                if not success:
                    logger.info(f"   - {pattern_id}")
        
        logger.info("=" * 80 + "\n")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description='Research laser properties for contamination patterns'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Research all patterns'
    )
    parser.add_argument(
        '--pattern',
        type=str,
        help='Research specific pattern by ID'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview research without saving'
    )
    
    args = parser.parse_args()
    
    if not args.all and not args.pattern:
        parser.print_help()
        print("\n❌ Error: Must specify --all or --pattern <pattern_id>")
        sys.exit(1)
    
    # Get API client
    try:
        api_client = create_api_client('grok')
        logger.info("✅ Grok API client initialized\n")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Grok API client: {e}")
        sys.exit(1)
    
    # Create orchestrator
    orchestrator = ContaminantsResearchOrchestrator(api_client, dry_run=args.dry_run)
    
    # Execute research
    if args.all:
        results = orchestrator.research_all_patterns()
        success = all(results.values())
    else:
        success = orchestrator.research_pattern(args.pattern)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
