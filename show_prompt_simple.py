"""Show the actual prompt being sent to the API - simplified version"""
import sys
sys.path.insert(0, '.')

from shared.text.utils.prompt_builder import PromptBuilder
import yaml

# Load voice persona
with open('shared/prompts/personas/taiwan.yaml', 'r') as f:
    voice = yaml.safe_load(f)

# Build facts string (simplified)
facts = """Material: Bamboo
Properties:
- Thermal conductivity: Low (natural insulator)
- Flexibility: High (bends without breaking)
- Durability: Good for lightweight applications
- Moisture resistance: Moderate
"""

# Build prompt (exactly as generation uses it)
prompt = PromptBuilder.build_unified_prompt(
    topic='Bamboo',
    voice=voice,
    length=150,  # Default for settings_description  
    facts=facts,
    context='',
    component_type='settings_description',
    domain='settings',
    voice_params=None,
    enrichment_params={'technical_intensity': 0.5},
    humanness_layer=None,  # Currently disabled
    faq_count=None
)

print("="*80)
print("ACTUAL PROMPT SENT TO GROK API")
print("="*80)
print(prompt)
print("\n" + "="*80)
print(f"PROMPT LENGTH: {len(prompt)} characters, ~{len(prompt.split())} words")
print("="*80)

# Check for forbidden phrase instructions
forbidden_found = []
for line in prompt.split('\n'):
    if 'forbidden' in line.lower():
        forbidden_found.append(line.strip())

if forbidden_found:
    print("\n✅ Prompt contains forbidden phrase instructions:")
    for line in forbidden_found:
        print(f"   {line}")
else:
    print("\n❌ WARNING: NO forbidden phrase instructions found in prompt!")
