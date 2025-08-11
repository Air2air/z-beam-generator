#!/usr/bin/env python3
"""
Content Validator Module

Validates generated markdown content for quality and completeness.
Provides component-specific validation rules and quality scoring.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass
from enum import Enum

class ComponentStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed" 
    EMPTY = "empty"
    INVALID = "invalid"
    MISSING = "missing"

@dataclass
class ComponentResult:
    component: str
    subject: str
    status: ComponentStatus
    file_path: str
    size_bytes: int
    content_lines: int
    issues: List[str]
    quality_score: float

class ContentValidator:
    """Validates generated markdown content for quality and completeness."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.min_content_sizes = {
            'frontmatter': 100,    # Minimum YAML content
            'metatags': 150,       # Several meta tags
            'table': 200,         # At least one table
            'bullets': 100,       # Multiple bullet points
            'caption': 50,        # Brief caption
            'propertiestable': 80, # Basic properties
            'tags': 30,           # Several tags
            'jsonld': 100,        # Basic JSON-LD structure
            'content': 500        # Main content if exists
        }
    
    def validate_markdown_file(self, file_path: str, component: str) -> ComponentResult:
        """Validate a single markdown file for a component."""
        issues = []
        quality_score = 0.0
        
        if not os.path.exists(file_path):
            return ComponentResult(
                component=component,
                subject="unknown",
                status=ComponentStatus.MISSING,
                file_path=file_path,
                size_bytes=0,
                content_lines=0,
                issues=["File does not exist"],
                quality_score=0.0
            )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            size_bytes = len(content.encode('utf-8'))
            content_lines = len(content.splitlines())
            
            # Extract subject from filename
            subject = Path(file_path).stem.replace('-laser-cleaning', '').replace('-', ' ').title()
            
            # Basic validations
            status, issues, quality_score = self._analyze_content(content, component, size_bytes)
            
            return ComponentResult(
                component=component,
                subject=subject,
                status=status,
                file_path=file_path,
                size_bytes=size_bytes,
                content_lines=content_lines,
                issues=issues,
                quality_score=quality_score
            )
            
        except Exception as e:
            return ComponentResult(
                component=component,
                subject="unknown",
                status=ComponentStatus.FAILED,
                file_path=file_path,
                size_bytes=0,
                content_lines=0,
                issues=[f"Error reading file: {e}"],
                quality_score=0.0
            )
    
    def _analyze_content(self, content: str, component: str, size_bytes: int) -> Tuple[ComponentStatus, List[str], float]:
        """Analyze content quality and return status, issues, and quality score."""
        issues = []
        quality_score = 0.0
        
        # Check if content is empty or minimal
        if size_bytes < 10:
            return ComponentStatus.EMPTY, ["File is empty"], 0.0
        
        # Check for empty frontmatter (just delimiters)
        if content.strip() == "---\n---" or content.strip() == "---":
            return ComponentStatus.EMPTY, ["Contains only empty frontmatter delimiters"], 0.0
        
        # Check minimum size requirements
        min_size = self.min_content_sizes.get(component, 50)
        if size_bytes < min_size:
            issues.append(f"Content too small ({size_bytes} bytes, minimum {min_size})")
            quality_score -= 30
        else:
            quality_score += 20
        
        # Component-specific validations
        if component == 'frontmatter':
            quality_score += self._validate_frontmatter(content, issues)
        elif component == 'metatags':
            quality_score += self._validate_metatags(content, issues)
        elif component == 'table':
            quality_score += self._validate_table(content, issues)
        elif component == 'bullets':
            quality_score += self._validate_bullets(content, issues)
        elif component == 'jsonld':
            quality_score += self._validate_jsonld(content, issues)
        elif component == 'tags':
            quality_score += self._validate_tags(content, issues)
        else:
            quality_score += self._validate_generic_markdown(content, issues)
        
        # Determine overall status
        if quality_score >= 70:
            status = ComponentStatus.SUCCESS
        elif quality_score >= 40:
            status = ComponentStatus.INVALID
        else:
            status = ComponentStatus.FAILED
        
        return status, issues, max(0.0, min(100.0, quality_score))
    
    def _validate_frontmatter(self, content: str, issues: List[str]) -> float:
        """Validate YAML frontmatter content."""
        score = 0.0
        
        try:
            # Extract YAML between delimiters
            if '---' in content:
                parts = content.split('---')
                if len(parts) >= 3:
                    yaml_content = parts[1].strip()
                    if yaml_content:
                        data = yaml.safe_load(yaml_content)
                        if isinstance(data, dict):
                            score += 30
                            # Check for required fields
                            required_fields = ['name', 'description', 'category']
                            for field in required_fields:
                                if field in data:
                                    score += 10
                                else:
                                    issues.append(f"Missing required field: {field}")
                        else:
                            issues.append("YAML does not parse to dictionary")
                    else:
                        issues.append("Empty YAML content between delimiters")
                else:
                    issues.append("Invalid frontmatter delimiter structure")
            else:
                issues.append("No YAML frontmatter delimiters found")
        except yaml.YAMLError as e:
            issues.append(f"Invalid YAML syntax: {e}")
        
        return score
    
    def _validate_table(self, content: str, issues: List[str]) -> float:
        """Validate markdown table content."""
        score = 0.0
        
        # Count tables (lines with | characters)
        table_lines = [line for line in content.splitlines() if '|' in line and line.count('|') >= 2]
        
        if table_lines:
            score += 30
            # Check for table headers (## sections)
            if '##' in content:
                score += 20
            # Check for proper table structure
            if len(table_lines) >= 3:  # Header, separator, at least one row
                score += 20
            else:
                issues.append("Tables appear incomplete (need header, separator, data rows)")
        else:
            issues.append("No markdown tables found")
        
        return score
    
    def _validate_bullets(self, content: str, issues: List[str]) -> float:
        """Validate bullet point content."""
        score = 0.0
        
        # Count bullet points
        bullet_lines = [line for line in content.splitlines() if line.strip().startswith(('*', '-', '+'))]
        
        if bullet_lines:
            score += 30
            if len(bullet_lines) >= 3:
                score += 20
            else:
                issues.append(f"Only {len(bullet_lines)} bullet points found (expected 3+)")
            
            # Check for bold formatting
            if '**' in content:
                score += 10
        else:
            issues.append("No bullet points found")
        
        return score
    
    def _validate_jsonld(self, content: str, issues: List[str]) -> float:
        """Validate JSON-LD content."""
        score = 0.0
        
        # Look for JSON-LD structure
        if '@context' in content or '@type' in content:
            score += 30
        else:
            issues.append("No JSON-LD structure markers found")
        
        return score
    
    def _validate_tags(self, content: str, issues: List[str]) -> float:
        """Validate tags content."""
        score = 0.0
        
        # Clean content and count tags
        clean_content = content.strip()
        if clean_content:
            tags = [tag.strip() for tag in clean_content.split(',')]
            if len(tags) >= 3:
                score += 40
            else:
                issues.append(f"Only {len(tags)} tags found (expected 3+)")
        else:
            issues.append("No tags content found")
        
        return score
    
    def _validate_metatags(self, content: str, issues: List[str]) -> float:
        """Validate metatags content."""
        score = 0.0
        
        # Look for meta tag patterns
        meta_patterns = ['<meta', 'name=', 'content=', 'property=']
        found_patterns = sum(1 for pattern in meta_patterns if pattern in content)
        
        if found_patterns >= 2:
            score += 30
        else:
            issues.append("Insufficient meta tag structure found")
        
        return score
    
    def _validate_generic_markdown(self, content: str, issues: List[str]) -> float:
        """Validate generic markdown content."""
        score = 0.0
        
        if content.strip():
            score += 30
            # Check for markdown elements
            if any(marker in content for marker in ['#', '*', '**', '`']):
                score += 10
        
        return score
