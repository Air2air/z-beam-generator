#!/usr/bin/env python3
"""
"""AI Detection Snapshot Tool

Captures current config state + generates test batch + records results.
Makes it easy to:
1. Generate batch of captions with current settings
2. Record config snapshot with outputs
3. Compare different config combinations systematically
4. Track which settings produce best AI detection results

Usage:
    python3 scripts/snapshot_ai_test.py --materials "Titanium,Copper,Steel,Aluminum" --name "test_name"
    
    # Then manually test in phrasely.ai and update the YAML with scores
"""

import argparse
import datetime
import subprocess
import yaml
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def get_git_hash():
    """Get current git commit hash."""
    result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                          capture_output=True, text=True)
    return result.stdout.strip()

def load_current_config():
    """Load current config.yaml settings."""
    config_path = Path(__file__).parent.parent / 'processing' / 'config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return {
        'author_voice_intensity': config['author_voice_intensity'],
        'personality_intensity': config['personality_intensity'],
        'engagement_style': config['engagement_style'],
        'emotional_intensity': config['emotional_intensity'],
        'technical_language_intensity': config['technical_language_intensity'],
        'context_specificity': config['context_specificity'],
        'sentence_rhythm_variation': config['sentence_rhythm_variation'],
        'imperfection_tolerance': config['imperfection_tolerance'],
        'structural_predictability': config['structural_predictability'],
        'ai_avoidance_intensity': config['ai_avoidance_intensity'],
        'length_variation_range': config['length_variation_range'],
    }

def get_sentence_variation():
    """Get current sentence_calculator variation_pct."""
    calc_path = Path(__file__).parent.parent / 'processing' / 'generation' / 'sentence_calculator.py'
    
    if not calc_path.exists():
        return None
    
    with open(calc_path, 'r') as f:
        for line in f:
            if 'variation_pct =' in line:
                # Extract value like: variation_pct = 0.50
                parts = line.split('=')
                if len(parts) >= 2:
                    value = parts[1].strip().split('#')[0].strip()
                    return float(value)
    return None

def get_prompt_version():
    """Determine prompt version from caption.txt content."""
    prompt_path = Path(__file__).parent.parent / 'prompts' / 'components' / 'caption.txt'
    with open(prompt_path, 'r') as f:
        content = f.read()
    
    if 'PRIMARY industrial advantage' in content:
        if 'BANNED OPENING PATTERNS' in content:
            return "primary_advantage_with_banned_patterns"
        else:
            return "primary_advantage_v1"
    elif 'Legacy Caption Prompt' in content:
        return "simple_legacy"
    else:
        return "unknown"

def generate_caption(material):
    """Generate caption for material and capture output + AI detection score."""
    result = subprocess.run(
        ['python3', 'run.py', '--caption', material],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    # Extract word count, AI score, and generated text from output
    lines = result.stdout.split('\n')
    word_count = None
    ai_score = None
    output_text = None
    
    for i, line in enumerate(lines):
        if 'Word count:' in line:
            word_count = int(line.split(':')[1].strip().split()[0])
        if 'AI Score:' in line or 'AI score:' in line:
            # Extract score like "AI Score: 0.234"
            parts = line.split(':')
            if len(parts) >= 2:
                score_str = parts[1].strip().split()[0]
                try:
                    ai_score = float(score_str)
                except ValueError:
                    pass
        if '📝 FULL GENERATED TEXT:' in line:
            # Text is a few lines after this marker
            for j in range(i+1, len(lines)):
                if lines[j].strip() and not lines[j].startswith('─'):
                    output_text = lines[j].strip()
                    break
    
    # Count sentences (simple heuristic)
    sentence_count = 0
    if output_text:
        sentence_count = output_text.count('.') + output_text.count('!') + output_text.count('?')
        if sentence_count == 0:
            sentence_count = 1  # At least one sentence if no punctuation
    
    return {
        'material': material,
        'word_count': word_count,
        'sentence_count': sentence_count,
        'output': output_text,
        'pipeline_ai_score': round(ai_score, 3) if ai_score else None,
        'phrasely_ai_score': 'TBD',
        'human_readable': None,
        'notes': ''
    }

def create_snapshot(name, materials):
    """Create a new test snapshot."""
    timestamp = datetime.datetime.now().isoformat()
    commit_hash = get_git_hash()
    config = load_current_config()
    sentence_var = get_sentence_variation()
    prompt_ver = get_prompt_version()
    
    print(f"\n🔬 Creating AI Detection Snapshot: {name}")
    print(f"📝 Commit: {commit_hash}")
    print(f"⚙️  Config: {config}")
    print(f"📊 Sentence variation: {sentence_var}")
    print(f"📄 Prompt version: {prompt_ver}")
    print(f"\n🧪 Generating test batch for: {', '.join(materials)}\n")
    
    test_results = []
    for material in materials:
        print(f"  Generating {material}...")
        result = generate_caption(material)
        test_results.append(result)
        print(f"    ✓ {result['word_count']}w, {result['sentence_count']} sent")
        print(f"    → {result['output'][:80]}...\n")
    
    snapshot = {
        f'snapshot_{datetime.datetime.now().strftime("%Y_%m_%d")}_{name}': {
            'timestamp': timestamp,
            'commit_hash': commit_hash,
            'config': config,
            'sentence_calculator': {
                'variation_pct': sentence_var
            },
            'prompt_version': prompt_ver,
            'test_results': test_results,
            'summary': {
                'total_tested': len(materials),
                'passed': None,
                'failed': None,
                'pass_rate': None
            },
            'verdict': 'TBD',
            'notes': 'Fill in after phrasely.ai testing'
        }
    }
    
    # Append to snapshots file
    snapshot_path = Path(__file__).parent.parent / 'tests' / 'ai_detection_snapshots.yaml'
    
    with open(snapshot_path, 'a') as f:
        f.write('\n# ' + '='*78 + '\n')
        f.write(f'# SNAPSHOT: {name}\n')
        f.write('# ' + '='*78 + '\n')
        yaml.dump(snapshot, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n✅ Snapshot saved to: {snapshot_path}")
    print(f"\n📋 Next steps:")
    print(f"   1. Test outputs in phrasely.ai")
    print(f"   2. Update snapshot YAML with:")
    print(f"      - phrasely_ai_score: 'X/Y AI-like'")
    print(f"      - human_readable: true/false")
    print(f"      - summary.passed/failed/pass_rate")
    print(f"      - verdict: 'BEST'/'FAILED'/'MIXED'")
    print(f"      - notes: observations\n")

def main():
    parser = argparse.ArgumentParser(description='Create AI detection test snapshot')
    parser.add_argument('--materials', required=True, 
                       help='Comma-separated list of materials to test')
    parser.add_argument('--name', required=True,
                       help='Short name for this test (e.g., "high_personality")')
    
    args = parser.parse_args()
    materials = [m.strip() for m in args.materials.split(',')]
    
    create_snapshot(args.name, materials)

if __name__ == '__main__':
    main()
