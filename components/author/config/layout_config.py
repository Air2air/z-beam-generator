"""Layout configuration for different authors."""

from typing import Dict, Any, List

# Component order by author ID
AUTHOR_COMPONENT_ORDERS = {
    # Evelyn Wu (Taiwan)
    1: [
        "frontmatter",
        "content", 
        "table",
        "bullets",
        "tags",
        "jsonld"
    ],
    
    # Mario Jordan (Italy)
    2: [
        "frontmatter",
        "bullets",
        "content", 
        "table",
        "tags",
        "jsonld"
    ],
    
    # Todd Dunning (USA)
    3: [
        "frontmatter", 
        "content",
        "bullets",
        "table",
        "tags",
        "jsonld"
    ],
    
    # Ikmanda Roswati (Indonesia)
    4: [
        "frontmatter", 
        "content",
        "bullets",
        "table",
        "tags",
        "jsonld"
    ]
}

def get_component_order(author_id: int) -> List[str]:
    """Get component order for an author."""
    if author_id in AUTHOR_COMPONENT_ORDERS:
        return AUTHOR_COMPONENT_ORDERS[author_id]
    
    # Default component order
    return ["frontmatter", "content", "bullets", "table", "tags", "jsonld"]