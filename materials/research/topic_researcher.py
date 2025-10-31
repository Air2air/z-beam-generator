"""AI-powered researcher for material characteristics.

Performs extensive web research via AI to determine material properties, 
characteristics, and relevance for different use cases.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
import datetime

import yaml

logger = logging.getLogger(__name__)


# Component-specific context for research prompts
COMPONENT_CONTEXTS = {
    "faq": {
        "focus": "common questions, problems, use cases",
        "priorities": ["practical information", "troubleshooting", "best practices"]
    },
    "caption": {
        "focus": "visual characteristics, appearance, texture",
        "priorities": ["visual description", "distinctive features", "recognizability"]
    },
    "description": {
        "focus": "technical properties, composition, applications",
        "priorities": ["material science", "industrial use", "properties"]
    },
    "subtitle": {
        "focus": "concise summary, key benefits",
        "priorities": ["brevity", "impact", "memorability"]
    },
    "metadata": {
        "focus": "categorization, classification, relationships",
        "priorities": ["taxonomy", "associations", "industry standards"]
    }
}


class ResearchResult:
    """Container for material research results"""
    
    def __init__(
        self,
        material_name: str,
        component_type: str,
        scores: Dict[str, int],
        characteristics: List[str],
        reasoning: str,
        success: bool = True,
        error: Optional[str] = None
    ):
        self.material_name = material_name
        self.component_type = component_type
        self.scores = scores
        self.characteristics = characteristics
        self.reasoning = reasoning
        self.success = success
        self.error = error
        self.timestamp = datetime.datetime.now().isoformat() + "Z"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for YAML storage"""
        return {
            "scores": self.scores,
            "key_traits": self.characteristics,
            "reasoning": self.reasoning,
            "researched_date": self.timestamp,
            "research_method": "ai_web_research",
            "component_type": self.component_type
        }


class TopicResearcher:
    """AI-powered researcher for material characteristics"""
    
    def __init__(self, api_client):
        """Initialize with API client"""
        self.api_client = api_client
        self.materials_path = Path("data/Materials.yaml")
    
    def research_material_characteristics(
        self,
        material_name: str,
        component_type: str = "faq"
    ) -> ResearchResult:
        """Perform AI research on material characteristics"""
        try:
            logger.info(f"🔍 Researching {material_name} for {component_type}...")
            
            # Check cache first
            cached = self.load_cached_research(material_name, component_type)
            if cached:
                return ResearchResult(
                    material_name, component_type,
                    cached.get("scores", {}),
                    cached.get("key_traits", []),
                    cached.get("reasoning", "")
                )
            
            # Build prompt
            prompt = self._build_research_prompt(material_name, component_type)
            
            # Call API
            response = self.api_client.generate_simple(
                prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            if not response.success:
                logger.warning(f"API call failed for {material_name}: {response.error}")
                return ResearchResult(
                    material_name, component_type, {}, [], "",
                    success=False, error=response.error
                )
            
            # Parse response
            research_data = self._parse_research_response(response.content, material_name)
            
            if not research_data:
                return ResearchResult(
                    material_name, component_type, {}, [], "",
                    success=False, error="Failed to parse AI response"
                )
            
            # Create result
            result = ResearchResult(
                material_name=material_name,
                component_type=component_type,
                scores=research_data.get("scores", {}),
                characteristics=research_data.get("characteristics", []),
                reasoning=research_data.get("reasoning", "")
            )
            
            logger.info(f"✅ Research complete for {material_name}")
            return result
            
        except Exception as e:
            logger.error(f"Research error for {material_name}: {e}")
            return ResearchResult(
                material_name, component_type, {}, [], "",
                success=False, error=str(e)
            )
    
    def _build_research_prompt(self, material_name: str, component_type: str) -> str:
        """Build component-specific research prompt"""
        context = COMPONENT_CONTEXTS.get(component_type, COMPONENT_CONTEXTS["faq"])
        
        prompt = f"""You are a materials science expert researching "{material_name}" for laser cleaning applications.

TASK: Research and score this material across 7 key categories (0-10 scale):

1. **Industrial Relevance** (0-10):
   - How common/important is this material in industrial applications?
   - Score 10: ubiquitous (stainless steel, aluminum)
   - Score 5-7: specialized but significant use
   - Score 0-3: rare or niche

2. **Cultural/Historical Value** (0-10):
   - Historical artifacts, art, architectural preservation
   - Score 10: extremely valuable for conservation
   - Score 5-7: moderate conservation interest
   - Score 0-3: limited heritage value

3. **Technical Complexity** (0-10):
   - Difficulty of cleaning, special requirements
   - Score 10: extremely challenging (composites, thin films)
   - Score 5-7: moderate complexity
   - Score 0-3: straightforward

4. **Aesthetic Importance** (0-10):
   - Surface appearance, finish quality matters
   - Score 10: critical (jewelry, art, high-end products)
   - Score 5-7: important but not critical
   - Score 0-3: appearance not significant

5. **Environmental Sensitivity** (0-10):
   - Environmental regulations, sustainability concerns
   - Score 10: heavily regulated (lead, chromium)
   - Score 5-7: moderate environmental concerns
   - Score 0-3: minimal environmental impact

6. **Cost Impact** (0-10):
   - Material value, cost of damage/replacement
   - Score 10: extremely expensive (platinum, exotic alloys)
   - Score 5-7: moderate cost
   - Score 0-3: inexpensive

7. **Safety Concerns** (0-10):
   - Worker safety, toxic fumes, hazardous materials
   - Score 10: highly hazardous (beryllium, asbestos)
   - Score 5-7: moderate safety precautions needed
   - Score 0-3: generally safe

Additionally, list 3-5 KEY CHARACTERISTICS this material is most famous for.

Respond ONLY with JSON (no markdown):
{{
  "scores": {{
    "industrial_relevance": 0-10,
    "cultural_historical_value": 0-10,
    "technical_complexity": 0-10,
    "aesthetic_importance": 0-10,
    "environmental_sensitivity": 0-10,
    "cost_impact": 0-10,
    "safety_concerns": 0-10
  }},
  "characteristics": ["trait 1", "trait 2", "trait 3"],
  "reasoning": "Brief explanation of scores"
}}

Focus on: {context["focus"]}
Priorities: {", ".join(context["priorities"])}

IMPORTANT: Vary your phrasing and reasoning for each material. Use real-world examples and avoid formulaic responses."""
        
        return prompt
    
    def _parse_research_response(self, content: str, material_name: str) -> Optional[Dict]:
        """Parse AI research response"""
        try:
            content = content.strip()
            # Try to extract JSON (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if not json_match:
                # Try without code blocks
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1) if json_match.lastindex else json_match.group()
                research_data = json.loads(json_str)
                
                # Validate structure
                if "scores" in research_data and "characteristics" in research_data:
                    return research_data
                else:
                    logger.warning(f"Missing required fields for {material_name}")
                    return None
            else:
                logger.warning(f"Could not find JSON in response for {material_name}")
                return None
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing error for {material_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing response for {material_name}: {e}")
            return None
    
    def save_research_to_materials(
        self,
        material_name: str,
        research_result: ResearchResult
    ) -> bool:
        """Save research results to Materials.yaml"""
        try:
            # Load Materials.yaml
            with open(self.materials_path, "r", encoding="utf-8") as f:
                materials_data = yaml.safe_load(f)
            
            # Navigate to material
            if material_name not in materials_data.get("materials", {}):
                logger.warning(f"Material {material_name} not found in Materials.yaml")
                return False
            
            # Save to appropriate component section
            component = research_result.component_type
            if component not in materials_data["materials"][material_name]:
                materials_data["materials"][material_name][component] = {}
            
            materials_data["materials"][material_name][component]["characteristics"] = research_result.to_dict()
            
            # Write back
            with open(self.materials_path, "w", encoding="utf-8") as f:
                yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"✅ Saved research for {material_name} to Materials.yaml")
            return True
            
        except Exception as e:
            logger.error(f"Error saving research for {material_name}: {e}")
            return False
    
    def load_cached_research(
        self,
        material_name: str,
        component_type: str = "faq"
    ) -> Optional[Dict]:
        """Load cached research from Materials.yaml"""
        try:
            with open(self.materials_path, "r", encoding="utf-8") as f:
                materials_data = yaml.safe_load(f)
            
            material = materials_data.get("materials", {}).get(material_name, {})
            component = material.get(component_type, {})
            characteristics = component.get("characteristics", None)
            
            if characteristics:
                logger.info(f"📦 Using cached research for {material_name} ({component_type})")
                return characteristics
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not load cached research: {e}")
            return None
    
    def research_problems_solutions(
        self,
        material_name: str,
        component_type: str = "faq",
        max_problems: int = 5
    ) -> Optional[Dict]:
        """Research common problems and solutions for a material"""
        try:
            logger.info(f"🔍 Researching common problems/solutions for {material_name} ({component_type})...")
            
            prompt = f"""You are a materials science expert researching common problems and solutions for "{material_name}" in laser cleaning applications.

TASK: Identify up to {max_problems} of the most common, challenging, or important problems encountered when working with {material_name} in laser cleaning, restoration, or surface preparation. For each problem, provide a concise solution or best practice.

Respond ONLY with JSON (no markdown code blocks):
{{
  "common_problems": [
    {{
      "problem": "Description of problem 1",
      "solution": "Best practice or solution for problem 1"
    }},
    ...
  ]
}}

Vary your phrasing and reasoning for each material. Use real-world examples and avoid formulaic responses."""
            
            response = self.api_client.generate_simple(
                prompt,
                max_tokens=1500,
                temperature=0.7
            )
            
            if not response.success:
                logger.warning(f"API call failed for {material_name}: {response.error}")
                return None
            
            # Parse response
            content = response.content.strip()
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if not json_match:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1) if json_match.lastindex else json_match.group()
                problems_data = json.loads(json_str)
                
                if "common_problems" in problems_data:
                    logger.info(f"✅ Found {len(problems_data['common_problems'])} problems for {material_name}")
                    return problems_data
            
            logger.warning(f"Could not parse problems response for {material_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error researching problems for {material_name}: {e}")
            return None
