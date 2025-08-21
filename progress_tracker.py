#!/usr/bin/env python3
"""
Minimal Progress Tracker for Z-Beam Generator.
"""

import logging

logger = logging.getLogger(__name__)

# Simple stub implementations
def start_progress_session(total_materials: int):
    """Start progress tracking session."""
    logger.info(f"Started progress session for {total_materials} materials")

def start_material_progress(material_name: str, material_num: int, components: list):
    """Start material progress tracking."""
    logger.info(f"Started material: {material_name} ({material_num}) with components: {components}")

def mark_component_done(component: str):
    """Mark component as done."""
    logger.info(f"Component completed: {component}")

def finish_material_progress(success: bool = True):
    """Finish material progress."""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Material finished: {status}")

def stop_progress_tracking():
    """Stop progress tracking."""
    logger.info("Progress tracking stopped")
