"""
Debug script for the component registry.
"""

import sys
import os
from pathlib import Path
import logging
import importlib.util

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def check_file_exists(file_path):
    """Check if a file exists and print its status."""
    exists = os.path.exists(file_path)
    logger.info(f"File check: {file_path} - {'EXISTS' if exists else 'MISSING'}")
    return exists

def check_directory_contents(dir_path):
    """List the contents of a directory."""
    if os.path.exists(dir_path):
        logger.info(f"Directory contents of {dir_path}:")
        for item in os.listdir(dir_path):
            logger.info(f"  - {item}")
    else:
        logger.error(f"Directory does not exist: {dir_path}")

def try_import(module_path):
    """Try to import a module and log the result."""
    try:
        module = importlib.import_module(module_path)
        logger.info(f"Successfully imported module: {module_path}")
        return module
    except ImportError as e:
        logger.error(f"Failed to import module {module_path}: {e}")
        return None

def inspect_registry():
    """Inspect the component registry."""
    try:
        # Try to import the registry
        from components.registry import ComponentRegistry
        
        # Create a registry instance
        registry = ComponentRegistry()
        
        # List registered components
        components = registry.list_components()
        
        if components:
            logger.info("Registered components:")
            for name, class_name in components.items():
                logger.info(f"  - {name}: {class_name}")
        else:
            logger.warning("No components registered!")
        
        # Check for specific components
        for component in ['frontmatter', 'content', 'table', 'tags', 'jsonld', 'bullets']:
            component_class = registry.get_component_class(component)
            status = "FOUND" if component_class else "MISSING"
            logger.info(f"Component '{component}': {status}")
            
        return registry
    except Exception as e:
        logger.error(f"Error inspecting registry: {e}")
        return None

def main():
    """Run registry debugging."""
    logger.info("=== Z-Beam Component Registry Debug ===")
    
    # Check key files and directories
    logger.info("\n=== Checking file structure ===")
    check_file_exists(project_root / "components" / "base.py")
    check_file_exists(project_root / "components" / "registry.py")
    check_file_exists(project_root / "components" / "frontmatter" / "generator.py")
    check_file_exists(project_root / "components" / "content" / "generator.py")
    
    # Check component directories
    logger.info("\n=== Checking component directories ===")
    check_directory_contents(project_root / "components")
    
    # Try imports
    logger.info("\n=== Testing imports ===")
    try_import("components.base")
    try_import("components.registry")
    try_import("components.frontmatter.generator")
    try_import("components.content.generator")
    
    # Inspect registry
    logger.info("\n=== Inspecting registry ===")
    registry = inspect_registry()
    
    logger.info("\n=== Debug complete ===")

if __name__ == "__main__":
    main()