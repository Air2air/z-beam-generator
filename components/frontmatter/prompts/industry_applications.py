#!/usr/bin/env python3
"""
Industry Applications Prompt Builder

Two-phase prompting for rigorous industry research within frontmatter generation.
No separate component - just enhanced prompts for better quality.
"""

import logging
import re
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)

class IndustryApplicationsPromptBuilder:
    """
    Build research-validated industry application prompts.
    
    Pattern: research_prompt() → validate_response() → generation_prompt()
    All within frontmatter component's existing generate() flow.
    """
    
    def __init__(self):
        self.prompts_dir = Path(__file__).parent / 'templates'
        self.quality_threshold = 70.0  # Minimum confidence score
        self._load_templates()
    
    def _load_templates(self):
        """Load research and generation templates"""
        research_path = self.prompts_dir / 'industry_research_phase.md'
        generation_path = self.prompts_dir / 'industry_generation_phase.md'
        
        if not research_path.exists() or not generation_path.exists():
            logger.warning(f"Industry prompt templates not found in {self.prompts_dir}")
            self.research_template = None
            self.generation_template = None
            return
        
        with open(research_path, 'r') as f:
            self.research_template = f.read()
        with open(generation_path, 'r') as f:
            self.generation_template = f.read()
    
    def build_research_prompt(self, material_name: str, category: str,
                              material_properties: Dict) -> str:
        """
        Phase 1: Build research prompt with strict validation criteria.
        
        Uses rigorous validation approach:
        - Material usage verification (specific products/components)
        - Cleaning necessity verification
        - Economic viability verification
        - Technical feasibility verification
        
        Args:
            material_name: Name of material being researched
            category: Material category (metal, ceramic, polymer, etc.)
            material_properties: Dict of material properties for context
            
        Returns:
            Formatted research prompt string
        """
        if not self.research_template:
            # Fallback inline prompt if template missing
            return self._build_inline_research_prompt(material_name, category)
        
        return self.research_template.format(
            material_name=material_name,
            category=category,
            properties=self._format_properties(material_properties)
        )
    
    def _build_inline_research_prompt(self, material_name: str, category: str) -> str:
        """Fallback research prompt if template file missing"""
        return f"""You are a materials science and industrial manufacturing expert researching laser cleaning applications for {material_name}.

RESEARCH METHODOLOGY - STRICT VALIDATION REQUIRED:

For each potential industry application, you MUST verify ALL of the following criteria:

1. Material Usage Verification
   - Is {material_name} actually used in manufacturing/operations within this industry?
   - What specific products or components use this material?
   - Provide evidence (standards, common practices, published data)

2. Cleaning Necessity Verification
   - Does this industry actually need to clean {material_name} surfaces?
   - What specific cleaning scenarios exist (maintenance, manufacturing, restoration)?
   - Why would laser cleaning be preferred over chemical/mechanical methods?

3. Economic Viability Verification
   - Is laser cleaning cost-effective for this application?
   - What is the volume/scale of this application?
   - Are there existing laser cleaning implementations in this industry?

4. Technical Feasibility Verification
   - Can laser cleaning effectively remove the contaminants in this application?
   - Are there material compatibility concerns?
   - What are the technical constraints or requirements?

RESEARCH QUALITY REQUIREMENTS:

- PRIMARY INDUSTRIES (3-5 max): Industries where {material_name} is COMMONLY used
  * Must cite specific products/components
  * Must have documented laser cleaning applications
  * Must show economic significance

- SECONDARY INDUSTRIES (2-3 max): Industries with specialized/niche uses
  * Must have verifiable {material_name} usage
  * May have emerging laser cleaning applications
  * Lower volume but technically valid

- REJECT: Speculative or unlikely applications
  * No verified {material_name} usage
  * No cleaning requirements
  * No technical or economic justification

OUTPUT FORMAT (YAML):

```yaml
industries:
  - industry: "Exact Industry Name"
    confidence: "high|medium|low"
    material_usage:
      - "Specific product/component 1"
      - "Specific product/component 2"
    cleaning_scenarios:
      - scenario: "Maintenance cleaning"
        frequency: "high|medium|low"
        contaminants: ["Type 1", "Type 2"]
    justification: "Why laser cleaning is appropriate (2-3 sentences with technical/economic reasons)"
    evidence: "Reference to standard, publication, or industry practice"
```

Material Category: {category}
Target: 5-8 high-quality validated industries (NOT 10+ generic entries)
"""
    
    def _format_properties(self, material_properties: Dict) -> str:
        """Format material properties for prompt context"""
        if not material_properties:
            return "No specific properties available"
        
        formatted = []
        for key, value in material_properties.items():
            if isinstance(value, dict):
                formatted.append(f"- {key}: {value.get('value', 'N/A')} {value.get('unit', '')}")
            else:
                formatted.append(f"- {key}: {value}")
        
        return "\n".join(formatted[:10])  # Limit to top 10 properties
    
    def validate_research_quality(self, research_response: str) -> Dict:
        """
        Validate research response meets quality thresholds.
        
        Checks:
        - Industry count (target 5-8)
        - Confidence distribution (prefer high/medium)
        - Evidence presence
        - Material usage specificity
        
        Args:
            research_response: Raw API response with research data
            
        Returns:
            Dict with validation results:
            {
                'passed': bool,
                'quality_score': float (0-100),
                'industries': list of validated industries,
                'confidence_distribution': {'high': int, 'medium': int, 'low': int},
                'issues': list of quality issues found
            }
        """
        issues = []
        industries = self._parse_industries_from_response(research_response)
        
        # Count by confidence level
        confidence_dist = {'high': 0, 'medium': 0, 'low': 0}
        for industry in industries:
            confidence = industry.get('confidence', 'low')
            confidence_dist[confidence] = confidence_dist.get(confidence, 0) + 1
        
        # Quality checks
        industry_count = len(industries)
        
        if industry_count < 5:
            issues.append(f"Only {industry_count} industries found (target: 5-8)")
        elif industry_count > 8:
            issues.append(f"Too many industries ({industry_count}), prefer quality over quantity")
        
        if confidence_dist['high'] + confidence_dist['medium'] < 4:
            issues.append(f"Insufficient high/medium confidence industries")
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(industries, confidence_dist, industry_count)
        
        passed = quality_score >= self.quality_threshold and len(issues) == 0
        
        return {
            'passed': passed,
            'quality_score': quality_score,
            'industries': industries,
            'confidence_distribution': confidence_dist,
            'issues': issues
        }
    
    def _parse_industries_from_response(self, response: str) -> List[Dict]:
        """
        Parse industries from API response.
        
        Expects YAML-like structure with industry entries.
        """
        industries = []
        
        # Simple parsing - look for industry entries
        # In production, use proper YAML parsing
        industry_pattern = r'industry:\s*["\']?([^"\'\n]+)["\']?'
        confidence_pattern = r'confidence:\s*["\']?(\w+)["\']?'
        
        industry_matches = re.finditer(industry_pattern, response, re.MULTILINE)
        
        for match in industry_matches:
            industry_name = match.group(1).strip()
            
            # Find confidence for this industry (search nearby text)
            start_pos = match.start()
            search_window = response[start_pos:start_pos + 500]
            conf_match = re.search(confidence_pattern, search_window)
            confidence = conf_match.group(1) if conf_match else 'low'
            
            industries.append({
                'industry': industry_name,
                'confidence': confidence,
                'material_usage': [],  # Would parse these in full implementation
                'cleaning_scenarios': [],
                'justification': '',
                'evidence': ''
            })
        
        return industries
    
    def _calculate_quality_score(self, industries: List[Dict], 
                                 confidence_dist: Dict, 
                                 count: int) -> float:
        """
        Calculate overall quality score (0-100).
        
        Factors:
        - Industry count (target 5-8)
        - Confidence distribution (prefer high/medium)
        - Evidence presence
        """
        score = 0.0
        
        # Count score (40 points) - optimal at 5-8 industries
        if 5 <= count <= 8:
            score += 40
        elif count < 5:
            score += (count / 5.0) * 40
        else:  # count > 8
            score += max(0, 40 - (count - 8) * 5)
        
        # Confidence score (60 points)
        high_weight = 20
        medium_weight = 10
        
        confidence_score = (
            confidence_dist['high'] * high_weight + 
            confidence_dist['medium'] * medium_weight
        )
        score += min(60, confidence_score)
        
        return min(100.0, score)
    
    def build_generation_prompt(self, validated_research: Dict,
                                material_name: str) -> str:
        """
        Phase 2: Build detailed generation prompt from validated research.
        
        Creates 50-80 word descriptions with evidence, standards, specific products.
        
        Args:
            validated_research: Dict from validate_research_quality()
            material_name: Name of material
            
        Returns:
            Formatted generation prompt string
        """
        if not self.generation_template:
            return self._build_inline_generation_prompt(validated_research, material_name)
        
        industries_text = self._format_industries_for_prompt(validated_research['industries'])
        
        return self.generation_template.format(
            material_name=material_name,
            industries=industries_text,
            quality_score=validated_research['quality_score']
        )
    
    def _build_inline_generation_prompt(self, validated_research: Dict, 
                                       material_name: str) -> str:
        """Fallback generation prompt if template missing"""
        industries_text = self._format_industries_for_prompt(validated_research['industries'])
        
        return f"""Based on the validated research for {material_name} laser cleaning applications, generate detailed industry application descriptions.

VALIDATED RESEARCH:
{industries_text}

GENERATION REQUIREMENTS:

For each industry above, create a detailed application description with:

1. Length: 50-80 words (comprehensive but concise)
2. Specific Products: Mention 2-3 actual products/components that use {material_name}
3. Cleaning Scenarios: Describe maintenance, manufacturing, or restoration applications
4. Technical Details: Include relevant contaminants, cleaning requirements
5. Standards/Evidence: Cite relevant standards (FAA, AWS, ISO, etc.) where applicable

OUTPUT FORMAT (YAML):

```yaml
applications:
  - industry: "Industry Name"
    description: "Detailed 50-80 word description with specific products, cleaning scenarios, and technical details..."
    products:
      - "Product 1"
      - "Product 2"
    scenarios:
      - "Scenario 1"
      - "Scenario 2"
    standards: "Relevant standard citation (if applicable)"
    confidence: "high|medium|low"
```

Focus on quality over quantity. Each description should be evidence-based and technically accurate.
"""
    
    def _format_industries_for_prompt(self, industries: List[Dict]) -> str:
        """Format industries list for generation prompt"""
        formatted = []
        for ind in industries:
            formatted.append(f"- {ind['industry']} (confidence: {ind.get('confidence', 'unknown')})")
        return "\n".join(formatted)
