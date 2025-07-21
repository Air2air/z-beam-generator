"""Component configuration for different authors."""

from typing import Dict, Any, Optional

# Component configuration by author
AUTHOR_COMPONENT_CONFIG = {
    # Evelyn Wu - Taiwan style
    1: {
        "content": {
            "paragraphs": 4,
            "min_words": 400,
            "max_words": 600,
            "academic_style": True
        },
        "bullets": {
            "count": 5,
            "style": "scientific",
            "use_sub_bullets": True
        },
        "table": {
            "rows": 6,
            "include_units": True,
            "include_footnotes": True
        }
    },
    
    # Mario Jordan - Italy style
    2: {
        "content": {
            "paragraphs": 3,
            "min_words": 300,
            "max_words": 450,
            "practical_focus": True
        },
        "bullets": {
            "count": 6,
            "style": "practical",
            "action_oriented": True
        },
        "table": {
            "rows": 4,
            "include_units": True,
            "include_examples": True
        }
    },
    
    # Todd Dunning - USA style
    3: {
        "content": {
            "paragraphs": 3,
            "min_words": 350,
            "max_words": 500,
            "industry_focus": True
        },
        "bullets": {
            "count": 4,
            "style": "industrial",
            "include_standards": True
        },
        "table": {
            "rows": 5,
            "include_units": True,
            "include_applications": True
        }
    },
    
    # Ikmanda Roswati - Indonesia style
    4: {
        "content": {
            "paragraphs": 3,
            "min_words": 350,
            "max_words": 500,
            "industry_focus": True
        },
        "bullets": {
            "count": 4,
            "style": "industrial",
            "include_standards": True
        },
        "table": {
            "rows": 5,
            "include_units": True,
            "include_applications": True
        }
    }
}

def get_author_component_config(author_id: int, component: str) -> Dict[str, Any]:
    """Get component configuration for a specific author.
    
    Args:
        author_id: Author identifier
        component: Component name
        
    Returns:
        Component configuration dictionary
    """
    if author_id in AUTHOR_COMPONENT_CONFIG:
        author_config = AUTHOR_COMPONENT_CONFIG[author_id]
        if component in author_config:
            return author_config[component]
    
    # Return empty config if not found
    return {}