"""
Badge symbol component post-processor for content cleanup and enhancement.
"""
import re
import logging

logger = logging.getLogger(__name__)


def post_process_badgesymbol(content: str, material_name: str = "") -> str:
    """
    Post-process badge symbol content for consistency and quality.
    
    Args:
        content: Generated badge symbol content
        material_name: Name of the material being processed
        
    Returns:
        str: Post-processed badge symbol content
    """
    if not content or not content.strip():
        return content
    
    # Clean up badge/symbol content
    processed = content.strip()
    
    # Handle different badge formats
    if processed.startswith('<') and processed.endswith('>'):
        # HTML/XML format (like SVG or HTML badges)
        processed = clean_html_badge(processed)
    elif processed.startswith('![') and '](' in processed:
        # Markdown image format
        processed = clean_markdown_badge(processed)
    elif processed.startswith('http') or processed.startswith('www'):
        # URL format
        processed = clean_badge_url(processed)
    else:
        # Text or symbol format
        processed = clean_text_badge(processed)
    
    # Material-specific enhancements
    if material_name:
        material_lower = material_name.lower()
        if material_lower in processed.lower() and material_name not in processed:
            processed = re.sub(rf'\b{re.escape(material_lower)}\b', material_name, processed, flags=re.IGNORECASE)
    
    return processed


def clean_html_badge(content: str) -> str:
    """Clean HTML/SVG badge content."""
    # Normalize whitespace within HTML
    content = re.sub(r'\s+', ' ', content)
    
    # Clean up common HTML badge attributes
    content = re.sub(r'(\w+)=([^"\s]+)', r'\1="\2"', content)  # Quote unquoted attributes
    
    # Clean up alt text and title attributes
    alt_match = re.search(r'alt="([^"]*)"', content)
    if alt_match:
        alt_text = clean_badge_text(alt_match.group(1))
        content = content.replace(alt_match.group(0), f'alt="{alt_text}"')
    
    title_match = re.search(r'title="([^"]*)"', content)
    if title_match:
        title_text = clean_badge_text(title_match.group(1))
        content = content.replace(title_match.group(0), f'title="{title_text}"')
    
    return content


def clean_markdown_badge(content: str) -> str:
    """Clean Markdown badge format."""
    # Extract alt text and URL
    match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', content)
    if match:
        alt_text = clean_badge_text(match.group(1))
        url = clean_badge_url(match.group(2))
        return f"![{alt_text}]({url})"
    
    return content


def clean_badge_url(url: str) -> str:
    """Clean badge URL."""
    url = url.strip()
    
    # Ensure proper URL format
    if not url.startswith(('http://', 'https://')):
        if url.startswith('www.'):
            url = 'https://' + url
        elif '.' in url and not url.startswith('/'):
            url = 'https://' + url
    
    # Clean up common badge service URLs
    badge_services = {
        'shields.io': 'img.shields.io',
        'badge.fury.io': 'badge.fury.io',
        'travis-ci.org': 'travis-ci.org',
        'github.com': 'github.com'
    }
    
    for service, canonical in badge_services.items():
        if service in url and canonical not in url:
            url = url.replace(service, canonical)
    
    return url


def clean_text_badge(content: str) -> str:
    """Clean text-based badge content."""
    content = content.strip()
    
    # Normalize whitespace
    content = re.sub(r'\s+', ' ', content)
    
    # Clean up common badge text
    content = clean_badge_text(content)
    
    return content


def clean_badge_text(text: str) -> str:
    """Clean badge text content."""
    if not text:
        return text
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Clean up common badge terminology
    badge_replacements = {
        'laser cleaning': 'Laser Cleaning',
        'build passing': 'Build Passing',
        'build failing': 'Build Failing',
        'coverage': 'Coverage',
        'license': 'License',
        'version': 'Version',
        'stable': 'Stable',
        'beta': 'Beta',
        'alpha': 'Alpha'
    }
    
    text_lower = text.lower()
    for old_term, new_term in badge_replacements.items():
        if old_term in text_lower:
            text = re.sub(rf'\b{re.escape(old_term)}\b', new_term, text, flags=re.IGNORECASE)
            break
    
    return text
