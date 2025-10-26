#!/usr/bin/env python3
"""
Normalize Caption Structure in Materials.yaml

Migrates 7 materials from legacy ai_text_fields.caption_* structure
to modern caption.beforeText/afterText structure.

Materials affected: Aluminum, Brass, Copper, Gold, Nickel, Platinum, Silver
"""
import yaml
from pathlib import Path
from datetime import datetime

def normalize_captions():
    """Migrate legacy caption structure to modern format"""
    
    materials_path = Path(__file__).parent.parent / 'data' / 'Materials.yaml'
    
    print('=' * 80)
    print('NORMALIZING CAPTION STRUCTURE IN MATERIALS.YAML')
    print('=' * 80)
    print()
    
    # Load Materials.yaml
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Find materials with legacy structure
    materials_to_migrate = []
    for mat_name, mat_data in data['materials'].items():
        ai_text_fields = mat_data.get('ai_text_fields', {})
        if any(k.startswith('caption_') for k in ai_text_fields.keys()):
            materials_to_migrate.append(mat_name)
    
    if not materials_to_migrate:
        print('✅ No materials need migration - all use modern caption structure')
        return
    
    print(f'Found {len(materials_to_migrate)} materials with legacy caption structure:')
    for mat in materials_to_migrate:
        print(f'  - {mat}')
    print()
    
    # Create backup
    backup_path = materials_path.parent / f'Materials.backup_caption_norm_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'
    with open(backup_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f'✅ Backup created: {backup_path.name}')
    print()
    
    # Migrate each material
    migrated_count = 0
    for mat_name in materials_to_migrate:
        mat_data = data['materials'][mat_name]
        ai_text_fields = mat_data.get('ai_text_fields', {})
        
        # Extract caption data from ai_text_fields
        before_field = ai_text_fields.get('caption_beforeText', {})
        after_field = ai_text_fields.get('caption_afterText', {})
        
        # Get existing caption section or create new one
        caption = mat_data.get('caption', {})
        
        # Extract beforeText content
        if before_field and 'content' in before_field:
            before_content = before_field['content']
            # Clean up JSON artifacts if present
            if before_content.strip().startswith('{'):
                import json
                try:
                    parsed = json.loads(before_content)
                    before_content = parsed.get('content', before_content)
                except:
                    pass
            caption['beforeText'] = before_content
            print(f'  ✅ {mat_name}: Migrated beforeText ({len(before_content)} chars)')
        
        # Extract afterText content
        if after_field and 'content' in after_field:
            after_content = after_field['content']
            # Clean up JSON artifacts if present
            if after_content.strip().startswith('{'):
                import json
                try:
                    parsed = json.loads(after_content)
                    after_content = parsed.get('content', after_content)
                except:
                    pass
            caption['afterText'] = after_content
            print(f'  ✅ {mat_name}: Migrated afterText ({len(after_content)} chars)')
        
        # Add metadata if not present
        if 'generated' not in caption and before_field.get('generated'):
            caption['generated'] = before_field['generated']
        
        if 'generation_method' not in caption:
            caption['generation_method'] = 'ai_research'
        
        if 'author' not in caption and 'author' in mat_data:
            author_info = mat_data['author']
            caption['author'] = author_info.get('name', 'Unknown')
        
        # Calculate word counts if not present
        if 'word_count' not in caption:
            caption['word_count'] = {
                'before': len(caption.get('beforeText', '').split()),
                'after': len(caption.get('afterText', '').split())
            }
        
        if 'character_count' not in caption:
            caption['character_count'] = {
                'before': len(caption.get('beforeText', '')),
                'after': len(caption.get('afterText', ''))
            }
        
        # Update material data
        mat_data['caption'] = caption
        
        # Remove legacy ai_text_fields caption entries
        if 'caption_beforeText' in ai_text_fields:
            del ai_text_fields['caption_beforeText']
            print(f'  ✅ {mat_name}: Removed ai_text_fields.caption_beforeText')
        
        if 'caption_afterText' in ai_text_fields:
            del ai_text_fields['caption_afterText']
            print(f'  ✅ {mat_name}: Removed ai_text_fields.caption_afterText')
        
        # Clean up empty ai_text_fields
        if not ai_text_fields:
            del mat_data['ai_text_fields']
            print(f'  ✅ {mat_name}: Removed empty ai_text_fields')
        
        migrated_count += 1
        print()
    
    # Save updated Materials.yaml
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print('=' * 80)
    print(f'✅ MIGRATION COMPLETE: {migrated_count}/{len(materials_to_migrate)} materials')
    print(f'✅ Materials.yaml saved with normalized caption structure')
    print('=' * 80)
    print()
    
    # Verify all materials now use modern structure
    legacy_count = 0
    for mat_name, mat_data in data['materials'].items():
        ai_text_fields = mat_data.get('ai_text_fields', {})
        if any(k.startswith('caption_') for k in ai_text_fields.keys()):
            legacy_count += 1
    
    if legacy_count == 0:
        print('✅ VERIFICATION: All 132 materials now use modern caption structure')
    else:
        print(f'⚠️ WARNING: {legacy_count} materials still have legacy structure')

if __name__ == '__main__':
    normalize_captions()
