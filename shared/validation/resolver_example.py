"""
Simple Domain Resolver Example

Shows how generators fetch link info directly from source files.
No central registry - just read what you need when you need it.
"""

from shared.validation.domain_resolver import DomainResolver

def example_materials_generator():
    """Example: Materials generator fetching contaminant links"""
    
    print("="*80)
    print("📦 Materials Generator - Fetching Contaminant Links")
    print("="*80)
    
    resolver = DomainResolver()
    
    # Material needs to reference some contaminants
    contaminant_ids = [
        'rust-contamination',
        'oil-contamination',
        'paint-residue-contamination',
    ]
    
    print(f"\n🔍 Looking up {len(contaminant_ids)} contaminants...")
    
    # Get full link info for each
    for cont_id in contaminant_ids:
        info = resolver.get_link_info('contaminants', cont_id)
        
        if info.exists:
            print(f"\n✅ {info.name}")
            print(f"   ID: {info.id}")
            print(f"   URL: {info.url}")
            print(f"   Title: {info.title}")
            print(f"   Category: {info.category}")
            if info.image:
                print(f"   Image: {info.image}")
        else:
            print(f"\n❌ {cont_id} - NOT FOUND")
    
    print("\n" + "="*80)


def example_get_all_relationships():
    """Example: Get all relationship links for an item"""
    
    print("="*80)
    print("📋 Get All Relationship Links for Aluminum")
    print("="*80)
    
    resolver = DomainResolver()
    
    # Get all contaminants related to aluminum
    links = resolver.get_relationship_links(
        'materials',
        'aluminum-laser-cleaning',
        'related_contaminants'
    )
    
    print(f"\n✅ Found {len(links)} related contaminants:")
    
    for link in links[:5]:  # Show first 5
        print(f"\n   {link.name}")
        print(f"      URL: {link.url}")
        print(f"      Exists: {link.exists}")
    
    if len(links) > 5:
        print(f"\n   ... and {len(links) - 5} more")
    
    print("\n" + "="*80)


def example_validate_before_use():
    """Example: Validate reference before using it"""
    
    print("="*80)
    print("🔍 Validate References Before Using")
    print("="*80)
    
    resolver = DomainResolver()
    
    test_ids = [
        'rust-contamination',  # Valid
        'rust',  # Invalid - missing suffix
        'nonexistent-contamination',  # Invalid - doesn't exist
    ]
    
    print("\n🔍 Testing contaminant IDs...")
    
    for test_id in test_ids:
        exists = resolver.validate_reference('contaminants', test_id)
        
        if exists:
            print(f"\n✅ {test_id} - VALID")
            # Safe to get link info
            info = resolver.get_link_info('contaminants', test_id)
            print(f"   URL: {info.url}")
        else:
            print(f"\n❌ {test_id} - INVALID")
            # Don't use this reference
    
    print("\n" + "="*80)


def example_generator_integration():
    """Example: How a real generator would use this"""
    
    print("="*80)
    print("🔧 Real Generator Integration")
    print("="*80)
    
    resolver = DomainResolver()
    
    # Simulated: Generator creating material data
    material_data = {
        'name': 'Steel',
        'category': 'metal',
        'relationships': {
            'related_contaminants': [
                {'id': 'rust-contamination'},
                {'id': 'oil-contamination'},
                {'id': 'paint-residue-contamination'},
            ]
        }
    }
    
    print("\n🔄 Processing relationships...")
    
    # Enrich contaminant references with full link data
    contaminants = material_data['relationships']['related_contaminants']
    
    for cont_ref in contaminants:
        cont_id = cont_ref['id']
        
        # Get full link info from contaminants source
        info = resolver.get_link_info('contaminants', cont_id)
        
        if info.exists:
            # Add complete link data
            cont_ref.update({
                'id': info.id,
                'title': info.title,
                'url': info.url,
                'name': info.name,
            })
            if info.image:
                cont_ref['image'] = info.image
            
            print(f"   ✅ {info.name} → {info.url}")
        else:
            print(f"   ❌ {cont_id} - invalid reference, skipping")
    
    # Remove invalid references
    material_data['relationships']['related_contaminants'] = [
        ref for ref in contaminants 
        if resolver.validate_reference('contaminants', ref['id'])
    ]
    
    print(f"\n✅ Final: {len(material_data['relationships']['related_contaminants'])} valid contaminant links")
    print("\n" + "="*80)


if __name__ == '__main__':
    example_materials_generator()
    print("\n")
    example_get_all_relationships()
    print("\n")
    example_validate_before_use()
    print("\n")
    example_generator_integration()
