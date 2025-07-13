import re
import logging

logger = logging.getLogger(__name__)

def validate_urls(content):
    """Validate and fix URLs in content."""
    # Find all URLs in content
    urls = re.findall(r'https?://[^\s"\'<>]+', content)
    
    fixed_content = content
    fixes = 0
    
    for url in urls:
        if "example.com" in url or "placeholder.com" in url:
            # Extract the path part
            path_match = re.search(r'https?://[^/]+/(.+)', url)
            if path_match:
                path = path_match.group(1)
                # Create fixed URL
                fixed_url = f"https://www.z-beam.com/{path}"
                # Replace in content
                fixed_content = fixed_content.replace(url, fixed_url)
                fixes += 1
                logger.info(f"Fixed URL: {url} -> {fixed_url}")
    
    if fixes > 0:
        logger.info(f"Fixed {fixes} URLs in content")
        
    return fixed_content