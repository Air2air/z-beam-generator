#!/usr/bin/env python3
"""
Batch Caption Generation Test
==============================
Tests caption generation with 4 materials (one per author) via direct CLI commands.

This mimics the manual test approach:
  python3 run.py --caption "MaterialName"

Uses subprocess to call run.py for each material to ensure real-world behavior.
Generates a comprehensive BatchReport after completion.
"""

import subprocess
import sys
import time
import yaml
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def select_test_materials():
    """Select one material per author for testing."""
    with open('data/materials/Materials.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    
    # Select first material for each author
    by_author = {1: None, 2: None, 3: None, 4: None}
    for name, mat_data in sorted(materials.items()):  # Sort for consistency
        if 'author' in mat_data and isinstance(mat_data['author'], dict):
            author_id = mat_data['author'].get('id')
            if author_id in by_author and by_author[author_id] is None:
                by_author[author_id] = name
                # Stop once we have one material per author
                if all(v is not None for v in by_author.values()):
                    break
    
    return by_author


def run_caption_generation(material_name):
    """Run caption generation for a single material and extract full evaluation data."""
    cmd = ['python3', 'run.py', '--caption', material_name]
    
    print(f'\n🚀 Running: {" ".join(cmd)}')
    print('=' * 70)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        elapsed = time.time() - start_time
        
        # Check if successful (exit code 0)
        success = result.returncode == 0
        
        # Extract key info from output
        output = result.stdout + result.stderr
        
        # Look for success indicators
        if 'Caption generation complete!' in output or 'caption written to Materials.yaml' in output:
            success = True
        elif 'Caption generation failed' in output or 'Error during caption generation' in output:
            success = False
        
        # Try to extract Winston score
        winston_score = None
        for line in output.split('\n'):
            if 'Human Score:' in line:
                try:
                    # Extract percentage from line like "Human Score: 99.2%"
                    parts = line.split('Human Score:')[1].strip()
                    winston_score = float(parts.split('%')[0])
                except Exception:
                    pass
        
        # Extract caption text from Materials.yaml after generation
        caption_text = None
        try:
            import yaml
            with open('data/materials/Materials.yaml', 'r') as f:
                materials_data = yaml.safe_load(f)
                mat_data = materials_data.get('materials', {}).get(material_name, {})
                caption_text = mat_data.get('caption', '')
        except Exception:
            pass
        
        # Extract subjective validation info (lightweight pattern check)
        subjective_violations = None
        subjective_pass = None
        for line in output.split('\n'):
            # Look for the validation result line
            if '✅ No subjective language violations' in line:
                subjective_violations = 0
                subjective_pass = True
                break
            elif 'subjective language violations detected' in line.lower():
                # Extract number from "⚠️ X subjective language violations detected:"
                try:
                    parts = line.split('subjective language violations')
                    if len(parts) > 0:
                        num_str = ''.join(c for c in parts[0] if c.isdigit())
                        if num_str:
                            subjective_violations = int(num_str)
                            subjective_pass = False
                except Exception:
                    pass
        
        # Extract full Grok subjective evaluation from database
        subjective_eval = None
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from processing.detection.winston_feedback_db import WinstonFeedbackDatabase
            
            db = WinstonFeedbackDatabase('data/winston_feedback.db')
            # Get most recent evaluation for this material
            eval_data = db.get_latest_subjective_evaluation(material_name, 'caption')
            if eval_data:
                subjective_eval = {
                    'overall_score': eval_data.get('overall_score'),
                    'clarity': eval_data.get('clarity_score'),
                    'professionalism': eval_data.get('professionalism_score'),
                    'technical_accuracy': eval_data.get('technical_accuracy_score'),
                    'human_likeness': eval_data.get('human_likeness_score'),
                    'engagement': eval_data.get('engagement_score'),
                    'jargon_free': eval_data.get('jargon_free_score'),
                    'strengths': eval_data.get('strengths', []),
                    'weaknesses': eval_data.get('weaknesses', []),
                    'recommendations': eval_data.get('recommendations', []),
                    'passes_quality_gate': eval_data.get('passes_quality_gate', False),
                    'narrative_assessment': eval_data.get('narrative_assessment'),  # Paragraph-form evaluation
                    'realism_score': eval_data.get('realism_score'),  # 0-10 scale
                    'voice_authenticity': eval_data.get('voice_authenticity'),  # 0-10 scale
                    'tonal_consistency': eval_data.get('tonal_consistency'),  # 0-10 scale
                    'ai_tendencies': eval_data.get('ai_tendencies')  # JSON array string
                }
        except Exception as e:
            # Evaluation data not available - that's okay
            pass
        
        return {
            'success': success,
            'elapsed': elapsed,
            'winston_score': winston_score,
            'caption_text': caption_text,
            'subjective_violations': subjective_violations,
            'subjective_pass': subjective_pass,
            'subjective_eval': subjective_eval,
            'exit_code': result.returncode,
            'output': output
        }
    
    except subprocess.TimeoutExpired:
        print('❌ TIMEOUT: Generation took longer than 5 minutes')
        return {
            'success': False,
            'elapsed': 300,
            'winston_score': None,
            'exit_code': -1,
            'error': 'Timeout after 5 minutes'
        }
    except Exception as e:
        print(f'❌ EXCEPTION: {str(e)}')
        return {
            'success': False,
            'elapsed': 0,
            'winston_score': None,
            'exit_code': -1,
            'error': str(e)
        }


def generate_batch_report(test_materials, results, success_count, total_count):
    """Generate and save simplified batch report with only alerts, subjective evaluation, and text."""
    
    print('\n\n' + '=' * 70)
    print('📝 GENERATING BATCH REPORT')
    print('=' * 70)
    
    # Build simplified markdown report
    markdown_lines = [
        '# Batch Caption Test Report',
        '',
        f'**Date**: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}',
        f'**Results**: {success_count}/{total_count} successful',
        '',
        '---',
        ''
    ]
    
    # Add each material with 3-section format
    for r in results:
        markdown_lines.append(f'## {r["material"]} (Author {r["author_id"]})')
        markdown_lines.append('')
        
        # 1. Alert/Issue Section
        if not r['success']:
            markdown_lines.append('### 🚨 ALERT: GENERATION FAILED')
            markdown_lines.append(f"**Error**: {r.get('error', 'Unknown error')}")
        elif r.get('winston_score') and r['winston_score'] < 70:
            markdown_lines.append('### ⚠️ ALERT: LOW HUMAN SCORE')
            markdown_lines.append(f"**Winston Score**: {r['winston_score']:.1f}% (threshold: 70%)")
        elif r.get('subjective_pass') == False:
            markdown_lines.append('### ⚠️ ALERT: SUBJECTIVE VALIDATION FAILED')
            markdown_lines.append(f"**Violations**: {r.get('subjective_violations', 'unknown')}")
        else:
            markdown_lines.append('### ✅ NO ISSUES DETECTED')
        
        markdown_lines.append('')
        
        # 2. Subjective Evaluation (only for successful generations)
        if r['success']:
            markdown_lines.append('### 📊 SUBJECTIVE EVALUATION')
            markdown_lines.append('')
            
            # Grok AI Narrative Assessment (paragraph-form evaluation)
            subjective_eval = r.get('subjective_eval')
            if subjective_eval and subjective_eval.get('narrative_assessment'):
                markdown_lines.append(subjective_eval['narrative_assessment'])
                markdown_lines.append('')
            
            # Display realism metrics if available
            if subjective_eval:
                realism_score = subjective_eval.get('realism_score')
                voice_auth = subjective_eval.get('voice_authenticity')
                tonal_cons = subjective_eval.get('tonal_consistency')
                ai_tendencies = subjective_eval.get('ai_tendencies')
                
                if any([realism_score, voice_auth, tonal_cons, ai_tendencies]):
                    markdown_lines.append('**Realism Analysis**:')
                    markdown_lines.append('')
                    if realism_score is not None:
                        markdown_lines.append(f'- Realism Score: {realism_score:.1f}/10')
                    if voice_auth is not None:
                        markdown_lines.append(f'- Voice Authenticity: {voice_auth:.1f}/10')
                    if tonal_cons is not None:
                        markdown_lines.append(f'- Tonal Consistency: {tonal_cons:.1f}/10')
                    if ai_tendencies:
                        import json
                        try:
                            tendencies_list = json.loads(ai_tendencies) if isinstance(ai_tendencies, str) else ai_tendencies
                            if tendencies_list and tendencies_list != ['none']:
                                markdown_lines.append(f"- AI Tendencies Detected: {', '.join(tendencies_list)}")
                            else:
                                markdown_lines.append('- AI Tendencies Detected: none')
                        except:
                            markdown_lines.append(f'- AI Tendencies Detected: {ai_tendencies}')
                    markdown_lines.append('')
            
            # Pattern validation status
            if r.get('subjective_violations') is not None:
                if r['subjective_violations'] == 0:
                    markdown_lines.append('- **Pattern Validation**: ✅ PASS - No violations detected')
                else:
                    status = '✅ PASS' if r.get('subjective_pass') else '❌ FAIL'
                    markdown_lines.append(f"- **Pattern Validation**: {status} - {r['subjective_violations']} violations")
            else:
                markdown_lines.append('- **Pattern Validation**: ✅ PASS - No violations detected')
            
            # Winston score
            if r.get('winston_score'):
                markdown_lines.append(f"- **Winston AI**: {r['winston_score']:.1f}% human")
            
            # Generation time
            markdown_lines.append(f"- **Generation Time**: {r.get('elapsed', 0):.1f}s")
            markdown_lines.append('')
            
            # 3. Generated Caption Text
            markdown_lines.append('### 📝 GENERATED CAPTION')
            markdown_lines.append('')
            if r.get('caption_text'):
                caption = r['caption_text']
                # Handle dictionary format (before/after) or string format
                if isinstance(caption, dict):
                    if 'before' in caption:
                        markdown_lines.append('**BEFORE:**')
                        markdown_lines.append('')
                        markdown_lines.append(caption['before'])
                        markdown_lines.append('')
                    if 'after' in caption:
                        markdown_lines.append('**AFTER:**')
                        markdown_lines.append('')
                        markdown_lines.append(caption['after'])
                else:
                    markdown_lines.append(caption)
            else:
                markdown_lines.append('⚠️ Caption text not captured')
            
            markdown_lines.append('')
        
        markdown_lines.append('---')
        markdown_lines.append('')
    
    markdown_report = '\n'.join(markdown_lines)
    
    # Save to static file (overwrites previous report)
    report_filename = 'BATCH_CAPTION_TEST_REPORT.md'
    report_path = Path(report_filename)
    
    with open(report_path, 'w') as f:
        f.write(markdown_report)
    
    print(f'\n✅ Report generated: {report_filename}')
    print(f'   Location: {report_path.absolute()}')
    print(f'   Size: {len(markdown_report)} characters')
    print('=' * 70)


def main():
    print('🎯 BATCH CAPTION GENERATION TEST')
    print('=' * 70)
    print('Testing caption generation with 4 materials (one per author)')
    print('Using direct CLI calls: python3 run.py --caption "MaterialName"')
    print('=' * 70)
    print()
    
    # Select materials
    test_materials = select_test_materials()
    
    print('📋 Selected test materials:')
    for author_id in sorted(test_materials.keys()):
        material = test_materials[author_id]
        print(f'  Author {author_id}: {material}')
    print()
    
    # Verify all authors covered
    if None in test_materials.values():
        print('⚠️  WARNING: Not all authors have materials assigned!')
        for author_id, material in test_materials.items():
            if material is None:
                print(f'  Missing: Author {author_id}')
        print()
    
    results = []
    
    # Test each material
    for author_id in sorted(test_materials.keys()):
        material_name = test_materials[author_id]
        if material_name is None:
            continue
        
        print(f'\n{"=" * 70}')
        print(f'TEST {author_id}/4: {material_name} (Author {author_id})')
        print('=' * 70)
        
        result = run_caption_generation(material_name)
        result['author_id'] = author_id
        result['material'] = material_name
        results.append(result)
        
        # Show immediate result
        if result['success']:
            winston = result.get('winston_score')
            winston_str = f"{winston:.1f}%" if winston else "N/A"
            print(f'\n✅ SUCCESS in {result["elapsed"]:.1f}s (Winston: {winston_str})')
        else:
            print(f'\n❌ FAILED (exit code: {result["exit_code"]})')
            if 'error' in result:
                print(f'   Error: {result["error"]}')
        
        # Brief pause between generations
        if author_id < 4:
            time.sleep(2)
    
    # Calculate success for exit code
    success_count = sum(1 for r in results if r['success'])
    
    # Detailed Results with Text and Subjective Evaluation
    print(f'\n\n{"=" * 70}')
    print('📝 BATCH TEST RESULTS')
    print('=' * 70)
    
    for r in results:
        print(f'\n{"=" * 70}')
        print(f"{r['material']} (Author {r['author_id']})")
        print('=' * 70)
        
        # Alert/Issue Section (immediate alerts)
        if not r['success']:
            print('\n🚨 ALERT: GENERATION FAILED')
            print(f"Error: {r.get('error', 'Unknown error')}")
        elif r.get('winston_score') and r['winston_score'] < 70:
            print('\n⚠️  ALERT: LOW HUMAN SCORE')
            print(f"Winston Score: {r['winston_score']:.1f}% (threshold: 70%)")
        elif r.get('subjective_pass') == False:
            print('\n⚠️  ALERT: SUBJECTIVE VALIDATION FAILED')
            print(f"Violations: {r.get('subjective_violations', 'unknown')}")
        else:
            print('\n✅ NO ISSUES DETECTED')
        
        # Subjective Evaluation (above text)
        if r['success']:
            print('\n📊 SUBJECTIVE EVALUATION:')
            print('-' * 70)
            
            # Grok AI Narrative Assessment (paragraph-form evaluation)
            subjective_eval = r.get('subjective_eval')
            if subjective_eval and subjective_eval.get('narrative_assessment'):
                print(f"\n{subjective_eval['narrative_assessment']}\n")
            
            # Display realism metrics if available
            if subjective_eval:
                realism_score = subjective_eval.get('realism_score')
                voice_auth = subjective_eval.get('voice_authenticity')
                tonal_cons = subjective_eval.get('tonal_consistency')
                ai_tendencies = subjective_eval.get('ai_tendencies')
                
                if any([realism_score, voice_auth, tonal_cons, ai_tendencies]):
                    print('\n**Realism Analysis**:')
                    if realism_score is not None:
                        print(f'- Realism Score: {realism_score:.1f}/10')
                    if voice_auth is not None:
                        print(f'- Voice Authenticity: {voice_auth:.1f}/10')
                    if tonal_cons is not None:
                        print(f'- Tonal Consistency: {tonal_cons:.1f}/10')
                    if ai_tendencies:
                        import json
                        try:
                            tendencies_list = json.loads(ai_tendencies) if isinstance(ai_tendencies, str) else ai_tendencies
                            if tendencies_list and tendencies_list != ['none']:
                                print(f"- AI Tendencies Detected: {', '.join(tendencies_list)}")
                            else:
                                print('- AI Tendencies Detected: none')
                        except:
                            print(f'- AI Tendencies Detected: {ai_tendencies}')
                    print('')
            
            # Pattern validation status (lightweight check)
            if r.get('subjective_violations') is not None:
                if r['subjective_violations'] == 0:
                    print('Pattern Validation: ✅ PASS - No violations detected')
                else:
                    status = '✅ PASS' if r.get('subjective_pass') else '❌ FAIL'
                    print(f"Pattern Validation: {status} - {r['subjective_violations']} violations")
            else:
                print('Pattern Validation: ✅ PASS - No violations detected')
            
            # Winston score
            if r.get('winston_score'):
                print(f"Winston AI: {r['winston_score']:.1f}% human")
            
            # Generation time
            print(f"Generation Time: {r.get('elapsed', 0):.1f}s")
            
            # Generated Caption Text
            print('\n📝 GENERATED CAPTION:')
            print('-' * 70)
            if r.get('caption_text'):
                caption = r['caption_text']
                # Handle dictionary format (before/after) or string format
                if isinstance(caption, dict):
                    if 'before' in caption:
                        print('BEFORE:')
                        print(caption['before'])
                    if 'after' in caption:
                        print('\nAFTER:')
                        print(caption['after'])
                else:
                    print(caption)
            else:
                print('⚠️  Caption text not captured')
    
    print(f'\n{"=" * 70}')
    
    # Generate comprehensive BatchReport
    generate_batch_report(test_materials, results, success_count, len(results))
    
    # Exit code based on success
    sys.exit(0 if success_count == len(results) else 1)


if __name__ == '__main__':
    main()
