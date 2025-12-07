"""Show the actual prompt being sent to the API"""
import sys
sys.path.insert(0, '.')

from shared.text.utils.prompt_builder import PromptBuilder
from generation.core.adapters.settings_adapter import SettingsAdapter
import yaml

# Load voice persona
with open('shared/prompts/personas/taiwan.yaml', 'r') as f:
    voice = yaml.safe_load(f)

# Load settings data for Bamboo
adapter = SettingsAdapter()
data = adapter.load_data('Bamboo')

# Build facts string
facts = f"""Material: Bamboo
Properties:
- Thermal conductivity: Low
- Density: Medium  
- Flexibility: High
- Durability: Good
- Moisture resistance: Moderate
"""

# Build prompt (same as generation uses)
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
    humanness_layer=None,  # Disabled currently
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
if 'FORBIDDEN' in prompt.upper() or 'forbidden' in prompt:
    print("✅ Prompt contains forbidden phrase instructions")
    # Find and show the forbidden section
    for line in prompt.split('\n'):
        if 'forbidden' in line.lower():
            print(f"   Found: {line}")
else:
    print("❌ NO forbidden phrase instructions in prompt")
