#!/usr/bin/env python3
"""
Backfill FAQ data to collapsible format with complete metadata.

Converts existing FAQ lists to unified collapsible structure with:
- ID generation from questions
- Topic extraction
- Severity classification
- Expert info from author
- Display metadata (_open, order)
- Presentation options

Per Core Principle 0.6: Maximum data population at source.
"""

import argparse
import logging
import sys
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class FAQBackfill:
    """Backfill FAQ data to collapsible format."""
    
    SEVERITY_KEYWORDS = {
        'critical': ['damage', 'safety', 'hazard', 'prevent', 'fragile', 'sensitive'],
        'high': ['suitable', 'ideal', 'restore', 'optimize', 'proper'],
        'medium': ['effective', 'clean', 'remove', 'work', 'use'],
        'low': ['maintain', 'typical', 'common', 'regular']
    }
    
    DOMAIN_CONFIGS = {
        'materials': {
            'path': 'data/materials/Materials.yaml',
            'root_key': 'materials'
        },
        'compounds': {
            'path': 'data/compounds/Compounds.yaml',
            'root_key': 'compounds'
        },
        'contaminants': {
            'path': 'data/contaminants/Contaminants.yaml',
            'root_key': 'contaminants'
        },
        'settings': {
            'path': 'data/settings/Settings.yaml',
            'root_key': 'settings'
        }
    }
    
    def __init__(self, dry_run: bool = True):
        """Initialize backfill."""
        self.dry_run = dry_run
        self.stats = {
            'items_processed': 0,
            'items_converted': 0,
            'items_skipped': 0,
            'items_already_collapsible': 0
        }
    
    def convert_faq_to_collapsible(
        self, 
        faq_data: List[Dict], 
        author_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Convert FAQ list to collapsible format with complete metadata.
        
        Returns:
            Collapsible structure with items, metadata, options
        """
        if not isinstance(faq_data, list):
            return faq_data
        
        # Get expert info from author
        expert_info = None
        if author_data and isinstance(author_data, dict):
            expert_info = {
                'name': author_data.get('name', ''),
                'title': author_data.get('title', ''),
                'expertise': author_data.get('expertise', [])
            }
        
        items = []
        for idx, faq in enumerate(faq_data):
            if not isinstance(faq, dict):
                continue
            
            question = faq.get('question', '')
            answer = faq.get('answer', '')
            
            if not question or not answer:
                continue
            
            # Generate ID from question
            faq_id = question.lower()
            faq_id = ''.join(c if c.isalnum() or c.isspace() else '' for c in faq_id)
            faq_id = '-'.join(faq_id.split()[:6])  # First 6 words
            
            # Extract topic
            topic = question.lower().replace('?', '')
            for word in ['what', 'how', 'why', 'when', 'where', 'does', 'is', 'are', 'can']:
                topic = topic.replace(word, '')
            topic = ' '.join(topic.split()[:5]).strip()
            
            # Classify severity
            text_combined = (question + ' ' + answer).lower()
            severity = 'medium'
            for sev, keywords in self.SEVERITY_KEYWORDS.items():
                if any(keyword in text_combined for keyword in keywords):
                    severity = sev
                    break
            
            # Build item
            item = {
                'id': faq_id,
                'title': question,
                'content': answer,
                'metadata': {
                    'topic': topic,
                    'severity': severity,
                    'acceptedAnswer': True
                },
                '_display': {
                    '_open': idx == 0,
                    'order': idx + 1
                }
            }
            
            # Add expert info if available
            if expert_info:
                item['metadata']['expertInfo'] = expert_info
            
            items.append(item)
        
        return {
            'presentation': 'collapsible',
            'items': items,
            'options': {
                'autoOpenFirst': True,
                'sortBy': 'severity'
            }
        }
    
    def process_domain(self, domain: str) -> None:
        """Process all items in a domain."""
        config = self.DOMAIN_CONFIGS.get(domain)
        if not config:
            logger.error(f"Unknown domain: {domain}")
            return
        
        file_path = Path(config['path'])
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return
        
        logger.info(f"\n{'='*60}")
        logger.info(f"DOMAIN: {domain.upper()}")
        logger.info(f"{'='*60}")
        
        # Load data
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        items = data.get(config['root_key'], {})
        if not items:
            logger.warning(f"No items found in {domain}")
            return
        
        logger.info(f"Processing {len(items)} items...")
        
        modified_count = 0
        
        # Process each item
        for item_id, item_data in items.items():
            self.stats['items_processed'] += 1
            
            # Check if item has FAQ
            if 'faq' not in item_data:
                continue
            
            faq = item_data['faq']
            
            # Skip if already collapsible
            if isinstance(faq, dict) and 'presentation' in faq:
                self.stats['items_already_collapsible'] += 1
                logger.debug(f"  ⏭️  {item_id}: Already collapsible")
                continue
            
            # Skip if not a list
            if not isinstance(faq, list):
                self.stats['items_skipped'] += 1
                logger.warning(f"  ⚠️  {item_id}: FAQ is not a list")
                continue
            
            # Convert to collapsible
            author_data = item_data.get('author', {})
            collapsible_faq = self.convert_faq_to_collapsible(faq, author_data)
            
            # Update item
            item_data['faq'] = collapsible_faq
            modified_count += 1
            self.stats['items_converted'] += 1
            
            # Log conversion
            item_count = len(collapsible_faq['items'])
            has_expert = bool(collapsible_faq['items'][0].get('metadata', {}).get('expertInfo')) if collapsible_faq['items'] else False
            expert_status = "with expert info" if has_expert else "no expert info"
            logger.info(f"  ✅ {item_id}: Converted {item_count} FAQs ({expert_status})")
        
        # Save if not dry run
        if not self.dry_run and modified_count > 0:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            logger.info(f"\n✅ Saved {modified_count} items to {file_path}")
        elif self.dry_run and modified_count > 0:
            logger.info(f"\n🔍 DRY RUN: Would save {modified_count} items")
        else:
            logger.info(f"\n⏭️  No changes needed for {domain}")
    
    def run(self, domains: List[str]) -> None:
        """Run backfill for specified domains."""
        logger.info("FAQ COLLAPSIBLE FORMAT BACKFILL")
        logger.info("Per Core Principle 0.6: Maximum data population at source")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'WRITE'}\n")
        
        for domain in domains:
            self.process_domain(domain)
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info("FINAL SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Items processed: {self.stats['items_processed']}")
        logger.info(f"Items converted: {self.stats['items_converted']}")
        logger.info(f"Already collapsible: {self.stats['items_already_collapsible']}")
        logger.info(f"Skipped (non-list): {self.stats['items_skipped']}")
        
        if self.dry_run:
            logger.info("\n🔍 This was a DRY RUN. Use --no-dry-run to save changes.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Backfill FAQ data to collapsible format')
    parser.add_argument('--domain', choices=['materials', 'compounds', 'contaminants', 'settings', 'all'],
                       default='all', help='Domain to process (default: all)')
    parser.add_argument('--no-dry-run', action='store_true',
                       help='Actually write changes (default: dry run)')
    
    args = parser.parse_args()
    
    # Determine domains
    if args.domain == 'all':
        domains = ['materials', 'compounds', 'contaminants', 'settings']
    else:
        domains = [args.domain]
    
    # Run backfill
    backfill = FAQBackfill(dry_run=not args.no_dry_run)
    backfill.run(domains)


if __name__ == '__main__':
    main()
