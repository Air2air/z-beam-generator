#!/usr/bin/env python3
"""
Material Schema - Schema for material articles
"""
import logging
from typing import Dict, Any, List
from .base_schema import BaseSchema

logger = logging.getLogger(__name__)

class MaterialSchema(BaseSchema):
    """Schema for material-type articles"""
    
    def __init__(self):
        super().__init__("material")
    
    # ... rest of the class implementation