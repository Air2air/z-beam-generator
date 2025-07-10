"""
Technical Authenticity Optimizer - Simplified
"""
import logging
from typing import Dict, Any
from ..base_optimizer import BaseOptimizer

logger = logging.getLogger(__name__)

class TechnicalAuthenticityOptimizer(BaseOptimizer):
    """Simplified technical enhancement optimizer"""
    
    def __init__(self, config, api_client):
        super().__init__(config, api_client)
        logger.info("🔬 Technical Authenticity Optimizer initialized")
    
    def optimize(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add technical depth with single API call"""
        material = metadata.get("material", "unknown")
        
        # Single, focused technical enhancement prompt
        tech_prompt = f"""Add technical credibility to this {material} laser cleaning article:

CONTENT:
{content}

ENHANCEMENTS NEEDED:
- Add 2-3 specific measurements (wavelengths, power densities, temperatures)
- Include 1-2 industry standards (ASTM, ISO, ANSI numbers)
- Reference 1-2 real equipment manufacturers or models
- Add 1 specific processing parameter or challenge
- Keep casual, readable tone
- Stay under 1200 words total

Return only the enhanced content with technical details naturally integrated."""
        
        enhanced_content = self.api_client.call(tech_prompt, "technical-enhancement")
        
        # Log results
        original_words = len(content.split())
        enhanced_words = len(enhanced_content.split())
        logger.info(f"✅ Technical enhancement: {original_words} → {enhanced_words} words")
        
        return enhanced_content
    
    def optimize_sections(self, sections: list, context: dict, config: dict) -> list:
        """Process sections (legacy compatibility)"""
        # Convert to single content string
        content = "\n\n".join([f"## {section['title']}\n{section['content']}" for section in sections])
        
        # Apply optimization
        enhanced_content = self.optimize(content, context)
        
        # Convert back to sections (simplified)
        enhanced_sections = []
        parts = enhanced_content.split("## ")
        
        for i, part in enumerate(parts[1:], 1):  # Skip first empty part
            lines = part.split("\n", 1)
            if len(lines) >= 2:
                enhanced_sections.append({
                    'title': lines[0].strip(),
                    'content': lines[1].strip(),
                    'order': i
                })
        
        return enhanced_sections