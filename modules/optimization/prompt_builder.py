#!/usr/bin/env python3
"""
Optimization Prompt Builder - Creates bundled prompts with context
"""

import logging

logger = logging.getLogger(__name__)

class OptimizationPromptBuilder:
    """Builds bundled optimization prompts with full context"""
    
    @staticmethod
    def create_bundled_prompt(previous_content, optimization_config, section_context):
        """Create bundled optimization prompt with all necessary context"""
        
        prompt_template = optimization_config.get('prompt', '')
        
        # Build comprehensive variable context
        template_variables = {
            'content': previous_content,
            'material': section_context.get('material', 'Unknown'),
            'section_type': section_context.get('type', 'Unknown'),
            'section_name': section_context.get('name', 'Unknown'),
            'target_words': section_context.get('target_words', 150),
            'previous_steps': ', '.join(section_context.get('previous_steps', [])) or 'None'
        }
        
        # Format the prompt template with available variables
        try:
            formatted_optimization_prompt = prompt_template.format(**template_variables)
        except KeyError as e:
            logger.error(f"❌ Missing template variable in optimization prompt: {e}")
            logger.error(f"💀 Available variables: {list(template_variables.keys())}")
            raise RuntimeError(f"Optimization prompt template error: missing variable {e}")
        
        # Build the complete bundled prompt
        bundled_prompt = f"""OPTIMIZATION TASK: {optimization_config.get('name', 'Unknown Optimization')}

SECTION CONTEXT:
- Section: {section_context['name']} ({section_context['type']})
- Material: {section_context['material']}
- Target words: ~{section_context['target_words']}
- Previous optimizations: {', '.join(section_context['previous_steps']) if section_context['previous_steps'] else 'None'}

CURRENT CONTENT TO OPTIMIZE:
{previous_content}

OPTIMIZATION REQUIREMENTS:
{formatted_optimization_prompt}

CRITICAL OUTPUT REQUIREMENTS:
- Return ONLY the optimized content itself
- Do NOT include any meta-commentary, explanations, or introductory phrases
- Do NOT add "Here's the optimized version" or similar commentary
- Do NOT include separators, dashes, or explanatory text
- Start immediately with the actual content
- End immediately after the content

Your response must begin directly with the content and contain nothing else."""
        
        logger.info(f"📋 Created bundled prompt: {len(bundled_prompt)} characters")
        return bundled_prompt