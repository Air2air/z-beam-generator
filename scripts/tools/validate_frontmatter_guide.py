#!/usr/bin/env python3
"""
Validate Frontmatter Against FRONTMATTER_GENERATION_GUIDE.md

Comprehensive validation of frontmatter files against all guide requirements:
- Schema version, structure, required fields
- Date formats, author profiles, voice metadata
- Content quality (word counts, completeness)
- Domain linkages, regulatory standards
- Material properties coverage
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
import re

class FrontmatterValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.quality_score = 100
        
    def validate_file(self, filepath: Path) -> Tuple[bool, int, List[str], List[str]]:
        """Validate a single frontmatter file"""
        self.errors = []
        self.warnings = []
        self.quality_score = 100
        
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        # Run all validation checks
        self._check_schema(data)
        self._check_required_fields(data)
        self._check_dates(data)
        self._check_author(data)
        self._check_voice_metadata(data)
        self._check_content(data)
        self._check_images(data)
        self._check_faq(data)
        self._check_properties(data)
        self._check_relationships(data)
        self._check_metadata(data)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.quality_score, self.errors, self.warnings
    
    def _check_schema(self, data: Dict[str, Any]):
        """Check schema version and content type"""
        if data.get('schema_version') != '4.0.0':
            self.errors.append(f"Schema version must be 4.0.0, got: {data.get('schema_version')}")
            self.quality_score -= 10
        
        if data.get('content_type') != 'unified_material':
            self.errors.append(f"Content type must be 'unified_material', got: {data.get('content_type')}")
            self.quality_score -= 5
    
    def _check_required_fields(self, data: Dict[str, Any]):
        """Check all mandatory top-level fields"""
        required = ['name', 'slug', 'id', 'category', 'subcategory', 'title', 
                   'description', 'breadcrumb', 'images', 'micro', 'faq',
                   'properties', 'relationships', 'serviceOffering']
        
        for field in required:
            if field not in data or data[field] is None:
                self.errors.append(f"Missing required field: {field}")
                self.quality_score -= 5
    
    def _check_dates(self, data: Dict[str, Any]):
        """Check date fields are ISO 8601 format"""
        for field in ['datePublished', 'dateModified']:
            value = data.get(field)
            if value is None:
                self.errors.append(f"{field} is null (must be ISO 8601 date)")
                self.quality_score -= 10
            elif not isinstance(value, str) or not re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?', value):
                self.warnings.append(f"{field} format may not be ISO 8601: {value}")
                self.quality_score -= 3
    
    def _check_author(self, data: Dict[str, Any]):
        """Check author profile completeness"""
        author = data.get('author', {})
        if not author:
            self.errors.append("Missing author information")
            self.quality_score -= 15
            return
        
        required_fields = ['id', 'name', 'country', 'jobTitle', 'expertise', 
                          'affiliation', 'credentials', 'email']
        missing = [f for f in required_fields if f not in author or author[f] is None]
        
        if missing:
            self.warnings.append(f"Author missing fields: {', '.join(missing)}")
            self.quality_score -= len(missing) * 2
    
    def _check_voice_metadata(self, data: Dict[str, Any]):
        """Check voice metadata exists"""
        metadata = data.get('_metadata', {})
        voice = metadata.get('voice', {})
        
        if not voice.get('voice_applied'):
            self.warnings.append("Voice not marked as applied")
            self.quality_score -= 5
    
    def _check_content(self, data: Dict[str, Any]):
        """Check content quality and word counts"""
        # Material description: 30-50 words
        desc = data.get('description', '')
        word_count = len(desc.split())
        if word_count < 30 or word_count > 50:
            self.warnings.append(f"description word count {word_count} (should be 30-50)")
            self.quality_score -= 3
        
        # Micro before/after: 60-80 words each
        micro = data.get('micro')
        if micro:
            for section in ['before', 'after']:
                text = micro.get(section, '')
                word_count = len(text.split())
                if word_count < 60 or word_count > 80:
                    self.warnings.append(f"micro.{section} word count {word_count} (should be 60-80)")
                    self.quality_score -= 2
        else:
            self.warnings.append("micro section missing")
            self.quality_score -= 5
    
    def _check_images(self, data: Dict[str, Any]):
        """Check image configuration"""
        images = data.get('images', {})
        for img_type in ['hero', 'micro']:
            if img_type not in images:
                self.errors.append(f"Missing {img_type} image")
                self.quality_score -= 5
            else:
                img = images[img_type]
                if not img.get('alt'):
                    self.warnings.append(f"{img_type} image missing alt text")
                    self.quality_score -= 2
                if not img.get('url'):
                    self.errors.append(f"{img_type} image missing url")
                    self.quality_score -= 3
    
    def _check_faq(self, data: Dict[str, Any]):
        """Check FAQ structure and quality"""
        faq = data.get('faq', [])
        
        if not faq:
            self.errors.append("FAQ section is empty")
            self.quality_score -= 10
            return
        
        if len(faq) < 3:
            self.warnings.append(f"FAQ has only {len(faq)} items (typically 3-10)")
            self.quality_score -= 3
        
        for i, item in enumerate(faq):
            if not item.get('question'):
                self.errors.append(f"FAQ item {i+1} missing question")
                self.quality_score -= 3
            
            answer = item.get('answer', '')
            word_count = len(answer.split())
            if word_count < 100 or word_count > 150:
                self.warnings.append(f"FAQ {i+1} answer word count {word_count} (should be 100-150)")
                self.quality_score -= 2
    
    def _check_properties(self, data: Dict[str, Any]):
        """Check material properties completeness"""
        props = data.get('properties', {})
        
        if not props:
            self.errors.append("Material properties missing")
            self.quality_score -= 20
            return
        
        # Check for material_characteristics and laser_material_interaction
        if 'material_characteristics' not in props:
            self.errors.append("Missing material_characteristics section")
            self.quality_score -= 10
        
        if 'laser_material_interaction' not in props:
            self.errors.append("Missing laser_material_interaction section")
            self.quality_score -= 10
    
    def _check_relationships(self, data: Dict[str, Any]):
        """Check domain linkages (related contaminants)"""
        linkages = data.get('relationships', {})
        contaminants = linkages.get('related_contaminants', [])
        
        if len(contaminants) < 4:
            self.warnings.append(f"Only {len(contaminants)} related contaminants (should be 4-6)")
            self.quality_score -= 5
        
        for cont in contaminants:
            required = ['id', 'title', 'url', 'frequency', 'severity']
            missing = [f for f in required if f not in cont or cont[f] is None]
            if missing:
                self.warnings.append(f"Contaminant missing fields: {', '.join(missing)}")
                self.quality_score -= 2
    
    def _check_metadata(self, data: Dict[str, Any]):
        """Check EEAT and material metadata"""
        if data.get('eeat') is None:
            self.errors.append("EEAT data is null")
            self.quality_score -= 10
        
        if data.get('metadata') is None:
            self.errors.append("metadata is null")
            self.quality_score -= 10

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Validate frontmatter files against guide')
    parser.add_argument('--file', help='Validate specific file')
    parser.add_argument('--summary', action='store_true', help='Show summary only')
    parser.add_argument('--min-quality', type=int, default=0, help='Minimum quality score to pass')
    args = parser.parse_args()
    
    validator = FrontmatterValidator()
    
    if args.file:
        files = [Path(args.file)]
    else:
        files = list(Path('frontmatter/materials').glob('*.yaml'))
    
    results = []
    total_score = 0
    
    print(f"{'=' * 80}")
    print(f"FRONTMATTER GUIDE COMPLIANCE VALIDATION")
    print(f"{'=' * 80}\n")
    
    for filepath in sorted(files):
        is_valid, score, errors, warnings = validator.validate_file(filepath)
        results.append((filepath.name, is_valid, score, errors, warnings))
        total_score += score
        
        if not args.summary or not is_valid or score < args.min_quality:
            status = '✅' if is_valid and score >= args.min_quality else '❌'
            print(f"{status} {filepath.name} - Quality: {score}/100")
            
            if errors:
                for error in errors:
                    print(f"  ❌ {error}")
            
            if warnings and not args.summary:
                for warning in warnings:
                    print(f"  ⚠️  {warning}")
            
            if not args.summary:
                print()
    
    # Summary
    avg_score = total_score / len(results) if results else 0
    valid_count = sum(1 for _, is_valid, score, _, _ in results if is_valid and score >= args.min_quality)
    
    print(f"{'=' * 80}")
    print(f"SUMMARY")
    print(f"{'=' * 80}")
    print(f"Files validated: {len(results)}")
    print(f"Passing: {valid_count}/{len(results)} ({(valid_count/len(results))*100:.1f}%)")
    print(f"Average quality score: {avg_score:.1f}/100")
    
    if args.min_quality > 0:
        below_threshold = [(name, score) for name, _, score, _, _ in results if score < args.min_quality]
        if below_threshold:
            print(f"\n{len(below_threshold)} files below quality threshold {args.min_quality}:")
            for name, score in below_threshold[:10]:
                print(f"  {name}: {score}/100")
            if len(below_threshold) > 10:
                print(f"  ... and {len(below_threshold) - 10} more")

if __name__ == '__main__':
    main()
