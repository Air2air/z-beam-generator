#!/usr/bin/env python3
"""
Populate missing fields in Compounds.yaml:
- formula: Display formula (use existing chemical_formula or research if missing)
- molecular_weight: Research missing values (7 compounds)
- faq: Generate FAQ entries for all compounds
"""

import yaml
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.api.client_factory import APIClientFactory
from shared.api.client import GenerationRequest
import time
import re

def load_compounds():
    """Load Compounds.yaml"""
    with open('data/compounds/Compounds.yaml', 'r') as f:
        return yaml.safe_load(f)

def save_compounds(data):
    """Save Compounds.yaml"""
    with open('data/compounds/Compounds.yaml', 'w') as f:
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

def research_molecular_weight(compound_name, cas_number, api_client):
    """Research molecular weight using AI"""
    prompt = f"""What is the molecular weight of {compound_name} (CAS: {cas_number})?

Provide ONLY the numeric value in g/mol (e.g., "28.01" or "44.01").
No explanation, just the number."""

    try:
        request = GenerationRequest(
            prompt=prompt,
            temperature=0.3,
            max_tokens=50
        )
        response = api_client.generate(request)
        text = response.content.strip()
        # Extract number
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            return float(match.group(1))
    except Exception as e:
        print(f"  ❌ Error researching molecular weight: {e}")
    return None

def generate_faq(compound_data, api_client):
    """Generate FAQ entry for compound"""
    name = compound_data.get('display_name', compound_data.get('name'))
    formula = compound_data.get('chemical_formula', '')
    cas = compound_data.get('cas_number', '')
    health = compound_data.get('health_effects', '')
    category = compound_data.get('category', '')
    
    # Extract first sentence of health effects for context
    health_summary = health[:150] + '...' if len(health) > 150 else health
    
    prompt = f"""Generate ONE practical FAQ question and answer about {name} ({formula}, CAS: {cas}) exposure during laser cleaning.

Category: {category}
Health context: {health_summary}

Format as:
Q: [Practical question from an operator's perspective]
A: [2-3 sentence answer with specific guidance]

Focus on: detection, exposure limits, or protection methods."""

    try:
        request = GenerationRequest(
            prompt=prompt,
            temperature=0.7,
            max_tokens=200
        )
        response = api_client.generate(request)
        text = response.content.strip()
        
        # Parse Q&A
        if 'Q:' in text and 'A:' in text:
            parts = text.split('A:', 1)
            question = parts[0].replace('Q:', '').strip()
            answer = parts[1].strip()
            
            return [{
                'question': question,
                'answer': answer
            }]
    except Exception as e:
        print(f"  ❌ Error generating FAQ: {e}")
    return None

def main():
    print("🔬 Populating Compound Data Gaps\n")
    
    api_client = APIClientFactory.create_client('grok')
    data = load_compounds()
    compounds = data['compounds']
    
    updated_count = 0
    
    for comp_id, comp_data in compounds.items():
        comp_name = comp_data.get('display_name', comp_data.get('name', comp_id))
        print(f"\n📋 {comp_name}")
        
        changes = []
        
        # 1. Formula: Copy from chemical_formula if not present
        if not comp_data.get('formula') and comp_data.get('chemical_formula'):
            comp_data['formula'] = comp_data['chemical_formula']
            changes.append("formula")
        
        # 2. Molecular weight: Research if missing
        if not comp_data.get('molecular_weight'):
            print(f"  🔍 Researching molecular weight...")
            mw = research_molecular_weight(
                comp_name,
                comp_data.get('cas_number', ''),
                api_client
            )
            if mw:
                comp_data['molecular_weight'] = mw
                changes.append(f"molecular_weight ({mw} g/mol)")
                print(f"  ✅ Molecular weight: {mw} g/mol")
        
        # 3. FAQ: Generate if missing
        if not comp_data.get('faq'):
            print(f"  💭 Generating FAQ...")
            faq = generate_faq(comp_data, api_client)
            if faq:
                comp_data['faq'] = faq
                changes.append("faq")
                print(f"  ✅ FAQ: {faq[0]['question'][:50]}...")
        
        if changes:
            updated_count += 1
            print(f"  ✨ Updated: {', '.join(changes)}")
    
    # Save changes
    if updated_count > 0:
        print(f"\n💾 Saving {updated_count} updated compounds...")
        save_compounds(data)
        print("✅ Complete!")
    else:
        print("\n✅ No updates needed - all fields populated!")

if __name__ == '__main__':
    main()
