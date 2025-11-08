#!/usr/bin/env python3
"""
FAQ Topic Enhancement Researcher

Uses Grok AI to enhance FAQ entries with:
1. Topic keywords - Key phrases highlighted in questions
2. Topic statements - Concise answer summaries prepended to answers

Integration: Inline with FAQ generation chain, before voice postprocessing.

Author: AI Assistant
Date: November 6, 2025
"""

import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class FAQTopicResearcher:
    """
    AI-powered FAQ topic enhancement.
    
    Enhances FAQ Q&A pairs with:
    - topic_keyword: 2-4 word key phrase from question
    - topic_statement: 2-5 word concise answer summary
    
    Both fields will go through voice postprocessing for author consistency.
    """
    
    def __init__(self, api_client):
        """
        Initialize with API client.
        
        Args:
            api_client: API client (Grok recommended for cost-effectiveness)
        """
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
    
    def enhance_faq_topics(
        self,
        material_name: str,
        faq_list: List[Dict]
    ) -> List[Dict]:
        """
        Enhance FAQ entries with topic keywords and statements.
        
        Args:
            material_name: Material name for context
            faq_list: List of Q&A dicts with 'question' and 'answer' keys
            
        Returns:
            Enhanced FAQ list with added fields:
            - topic_keyword: str (2-4 words from question)
            - topic_statement: str (2-5 word answer summary)
        """
        if not faq_list:
            self.logger.warning("Empty FAQ list - skipping topic enhancement")
            return faq_list
        
        self.logger.info(f"🔍 Enhancing {len(faq_list)} FAQ entries with topics...")
        
        enhanced_faqs = []
        success_count = 0
        
        for idx, faq_item in enumerate(faq_list, 1):
            question = faq_item.get('question', '')
            answer = faq_item.get('answer', '')
            
            if not question or not answer:
                self.logger.warning(f"   Skipping FAQ {idx}: Missing question or answer")
                enhanced_faqs.append(faq_item)
                continue
            
            try:
                # Research topic keyword and statement
                topics = self._research_single_faq(material_name, question, answer)
                
                if topics:
                    # Add topic fields to FAQ item
                    enhanced_item = faq_item.copy()
                    enhanced_item['topic_keyword'] = topics['topic_keyword']
                    enhanced_item['topic_statement'] = topics['topic_statement']
                    enhanced_faqs.append(enhanced_item)
                    success_count += 1
                    self.logger.info(f"   ✓ FAQ {idx}: '{topics['topic_keyword']}' → '{topics['topic_statement']}'")
                else:
                    # Keep original if enhancement fails
                    enhanced_faqs.append(faq_item)
                    self.logger.warning(f"   ✗ FAQ {idx}: Enhancement failed, keeping original")
                    
            except Exception as e:
                self.logger.error(f"   ✗ FAQ {idx}: Error - {e}")
                enhanced_faqs.append(faq_item)
        
        self.logger.info(f"✅ Enhanced {success_count}/{len(faq_list)} FAQ entries")
        
        return enhanced_faqs
    
    def _research_single_faq(
        self,
        material_name: str,
        question: str,
        answer: str
    ) -> Optional[Dict[str, str]]:
        """
        Research topic keyword and statement for single FAQ.
        
        Args:
            material_name: Material name for context
            question: FAQ question
            answer: FAQ answer
            
        Returns:
            Dict with 'topic_keyword' and 'topic_statement', or None if failed
        """
        prompt = self._build_topic_research_prompt(material_name, question, answer)
        
        try:
            # Generate with Grok
            response = self.api_client.generate_simple(
                prompt,
                max_tokens=200,  # Short response
                temperature=0.3  # Low temp for consistency
            )
            
            if not response.success:
                self.logger.error(f"API call failed: {response.error}")
                return None
            
            # Parse JSON response
            topics = self._parse_topic_response(response.content, question, answer)
            
            return topics
            
        except Exception as e:
            self.logger.error(f"Topic research failed: {e}")
            return None
    
    def _build_topic_research_prompt(
        self,
        material_name: str,
        question: str,
        answer: str
    ) -> str:
        """Build prompt for topic keyword and statement research."""
        return f"""You are analyzing FAQ entries about laser cleaning of {material_name}. Extract the core substance and material-specific qualities.

Your task: Identify what makes this Q&A distinctly about {material_name}'s unique properties, challenges, or behaviors.

TOPIC KEYWORD (2-4 words from question):
- Extract the MOST SPECIFIC technical concept or material property
- Must be exact phrase from the question (case-insensitive match)
- Highlight what's DISTINCTIVE about {material_name}
- Avoid generic terms: "laser cleaning", "material", "process"
- Examples of good keywords:
  • "thermal shock resistance" (not just "damage")
  • "corrosion patina preservation" (not just "cleaning")
  • "crystalline structure integrity" (not just "surface")

TOPIC STATEMENT (2-5 words answer summary):
- Distill the answer to its ESSENTIAL point
- What's the key takeaway or solution?
- Should capture {material_name}'s specific behavior/requirement
- Use precise, technical language
- Examples of good statements:
  • "Requires multi-pass low fluence" (not just "use low power")
  • "Preserves historical patina" (not just "safe cleaning")
  • "Prevents micro-cracking risk" (not just "avoid damage")

Material: {material_name}

Question: {question}

Answer: {answer}

Return ONLY valid JSON:
{{
  "topic_keyword": "exact distinctive phrase from question",
  "topic_statement": "precise material-specific answer essence"
}}"""
    
    def _parse_topic_response(
        self,
        response: str,
        question: str,
        answer: str
    ) -> Optional[Dict[str, str]]:
        """
        Parse and validate topic research response.
        
        Args:
            response: API response string
            question: Original question for validation
            answer: Original answer for validation
            
        Returns:
            Validated dict with topic_keyword and topic_statement, or None
        """
        try:
            # Extract JSON from response
            import re
            
            # Try to find JSON block
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if not json_match:
                self.logger.error("No JSON found in response")
                return None
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # Validate required fields
            if 'topic_keyword' not in data or 'topic_statement' not in data:
                self.logger.error("Missing required fields in JSON")
                return None
            
            topic_keyword = data['topic_keyword'].strip()
            topic_statement = data['topic_statement'].strip()
            
            # Validate topic_keyword
            if not self._validate_topic_keyword(topic_keyword, question):
                self.logger.warning(f"Invalid topic keyword: '{topic_keyword}' not in question")
                return None
            
            # Validate topic_statement
            if not self._validate_topic_statement(topic_statement):
                self.logger.warning(f"Invalid topic statement: '{topic_statement}' doesn't meet criteria")
                return None
            
            return {
                'topic_keyword': topic_keyword,
                'topic_statement': topic_statement
            }
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Parse error: {e}")
            return None
    
    def _validate_topic_keyword(self, keyword: str, question: str) -> bool:
        """
        Validate topic keyword.
        
        Rules:
        - Must be exact substring of question (case-insensitive)
        - Length: 2-4 words
        - Not generic terms
        """
        if not keyword:
            return False
        
        # Check if keyword is in question (case-insensitive)
        if keyword.lower() not in question.lower():
            return False
        
        # Check word count
        word_count = len(keyword.split())
        if word_count < 2 or word_count > 4:
            return False
        
        # Check for generic terms
        generic_terms = ['laser cleaning', 'material', 'process', 'method']
        if any(term in keyword.lower() for term in generic_terms):
            return False
        
        return True
    
    def _validate_topic_statement(self, statement: str) -> bool:
        """
        Validate topic statement.
        
        Rules:
        - Length: 2-5 words
        - Should be actionable or descriptive
        """
        if not statement:
            return False
        
        # Check word count
        word_count = len(statement.split())
        if word_count < 2 or word_count > 5:
            return False
        
        return True
