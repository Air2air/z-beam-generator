#!/usr/bin/env python3
"""
File Operations

Centralized file operations for content generation.
Extracted from run.py to reduce bloat and improve testability.
"""

import os
import shutil
from pathlib import Path
from typing import Optional


def save_component_to_file(content: str, filepath: str) -> None:
    """
    Save component content to file with directory creation.
    
    Args:
        content: Content to save
        filepath: Full file path where to save content
        
    Raises:
        OSError: If file cannot be written
    """
    try:
        # Create directory if it doesn't exist
        file_path = Path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        raise OSError(f"Failed to save file {filepath}: {e}")


def save_component_to_file_original(material: str, component_type: str, content: str) -> str:
    """
    Save component content using original file naming convention.
    
    Args:
        material: Material name
        component_type: Component type
        content: Content to save
        
    Returns:
        Path to saved file
        
    Raises:
        OSError: If file cannot be written
    """
    # Create safe filename from material name
    safe_material = material.lower().replace(' ', '-').replace('/', '-')
    filename = f"{safe_material}-laser-cleaning.md"
    
    # Map component types to correct directories
    # Handle legacy "content" component type - should save to "text" directory
    if component_type == "content":
        component_type = "text"
    
    # Create directory structure
    component_dir = Path("content") / "components" / component_type
    component_dir.mkdir(parents=True, exist_ok=True)
    
    # Full file path
    filepath = component_dir / filename
    
    # Save content
    save_component_to_file(content, str(filepath))
    
    return str(filepath)


def clean_content_components() -> dict:
    """
    Clean all generated component content files.
    
    Returns:
        Dictionary with cleanup statistics
    """
    content_dir = Path("content/components")
    
    if not content_dir.exists():
        return {
            'files_removed': 0,
            'directories_removed': 0,
            'errors': [],
            'message': 'No content directory found'
        }
    
    files_removed = 0
    directories_removed = 0
    errors = []
    
    try:
        # Remove all component directories and files
        for item in content_dir.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                    files_removed += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    directories_removed += 1
            except Exception as e:
                errors.append(f"Failed to remove {item}: {e}")
        
        # Remove the components directory if empty
        try:
            if content_dir.exists() and not any(content_dir.iterdir()):
                content_dir.rmdir()
                directories_removed += 1
        except OSError:
            pass  # Directory not empty, that's ok
            
    except Exception as e:
        errors.append(f"General cleanup error: {e}")
    
    return {
        'files_removed': files_removed,
        'directories_removed': directories_removed,
        'errors': errors,
        'message': f'Cleaned {files_removed} files and {directories_removed} directories'
    }


def ensure_output_directory() -> Path:
    """
    Ensure output directory structure exists.
    
    Returns:
        Path to content directory
    """
    content_dir = Path("content")
    content_dir.mkdir(exist_ok=True)
    
    components_dir = content_dir / "components"
    components_dir.mkdir(exist_ok=True)
    
    return content_dir


def get_file_stats(directory: str = "content") -> dict:
    """
    Get statistics about generated files.
    
    Args:
        directory: Directory to analyze
        
    Returns:
        Dictionary with file statistics
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        return {
            'total_files': 0,
            'total_size': 0,
            'by_component': {},
            'error': f'Directory {directory} not found'
        }
    
    stats = {
        'total_files': 0,
        'total_size': 0,
        'by_component': {},
        'by_extension': {}
    }
    
    try:
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                stats['total_files'] += 1
                file_size = file_path.stat().st_size
                stats['total_size'] += file_size
                
                # Component statistics
                if file_path.parent.name != directory:
                    component = file_path.parent.name
                    if component not in stats['by_component']:
                        stats['by_component'][component] = {'files': 0, 'size': 0}
                    stats['by_component'][component]['files'] += 1
                    stats['by_component'][component]['size'] += file_size
                
                # Extension statistics
                ext = file_path.suffix
                if ext not in stats['by_extension']:
                    stats['by_extension'][ext] = {'files': 0, 'size': 0}
                stats['by_extension'][ext]['files'] += 1
                stats['by_extension'][ext]['size'] += file_size
                
    except Exception as e:
        stats['error'] = str(e)
    
    return stats


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
