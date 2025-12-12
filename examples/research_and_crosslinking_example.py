"""
Example: Using Research and Cross-Linking in Text Generation

Demonstrates how to use SystemDataResearcher and CrossLinkBuilder
during content generation.
"""

from shared.text.research import SystemDataResearcher
from shared.text.cross_linking import CrossLinkBuilder


def example_research():
    """Example: Research material properties during generation."""
    
    researcher = SystemDataResearcher()
    
    # Research a material
    print("=== MATERIAL RESEARCH ===")
    steel_data = researcher.get_material("Steel")
    if steel_data:
        print(f"Material: Steel")
        print(f"Category: {steel_data.get('category')}")
        print(f"Hardness: {researcher.get_material_property('Steel', 'hardness')}")
    
    # Find related materials
    print("\n=== RELATED MATERIALS ===")
    related = researcher.get_related_materials("Steel", limit=3)
    print(f"Related to Steel: {', '.join(related)}")
    
    # Research common contaminants
    print("\n=== COMMON CONTAMINANTS ===")
    contaminants = researcher.get_material_contaminants("Steel", limit=5)
    for c in contaminants:
        print(f"  - {c['name']} (commonality: {c['commonality']})")


def example_cross_linking():
    """Example: Add cross-links to generated text."""
    
    link_builder = CrossLinkBuilder()
    
    # Example generated text
    content = """
    Steel requires higher laser power compared to Aluminum due to its greater 
    thermal conductivity. When removing rust oxide contamination, pulse duration 
    becomes critical. Similar challenges appear with stainless steel and 
    titanium alloys in industrial applications.
    """
    
    print("=== ORIGINAL TEXT ===")
    print(content)
    
    print("\n=== WITH CROSS-LINKS ===")
    linked_content = link_builder.add_links(
        content=content,
        current_item="Steel",
        domain="materials"
    )
    print(linked_content)


def example_integrated_workflow():
    """Example: Complete workflow with research and cross-linking."""
    
    researcher = SystemDataResearcher()
    link_builder = CrossLinkBuilder()
    
    # 1. Research context before generation
    print("=== STEP 1: RESEARCH ===")
    material_name = "Aluminum"
    
    # Get material properties for accurate content
    hardness = researcher.get_material_property(material_name, "hardness")
    category = researcher.get_material(material_name).get('category')
    related_materials = researcher.get_related_materials(material_name, limit=2)
    
    print(f"Researched {material_name}:")
    print(f"  Hardness: {hardness}")
    print(f"  Category: {category}")
    print(f"  Related: {', '.join(related_materials)}")
    
    # 2. Generate content (simulated)
    print("\n=== STEP 2: GENERATE ===")
    generated_text = f"""
    {material_name} presents unique challenges due to its {hardness} hardness.
    Unlike harder metals such as {related_materials[0]}, this material requires
    precise pulse control. Common surface contamination includes oxide layers
    that respond well to nanosecond pulses.
    """
    print(generated_text)
    
    # 3. Add cross-links
    print("\n=== STEP 3: CROSS-LINK ===")
    final_text = link_builder.add_links(
        content=generated_text,
        current_item=material_name,
        domain="materials"
    )
    print(final_text)


if __name__ == "__main__":
    print("=" * 70)
    print("TEXT GENERATION: RESEARCH & CROSS-LINKING EXAMPLES")
    print("=" * 70)
    
    print("\n\n")
    example_research()
    
    print("\n\n")
    example_cross_linking()
    
    print("\n\n")
    example_integrated_workflow()
    
    print("\n" + "=" * 70)
    print("COMPLETE - See code for implementation details")
    print("=" * 70)
