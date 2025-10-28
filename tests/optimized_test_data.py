#!/usr/bin/env python3
"""
Optimized Test Data

Provides pre-loaded test data for improved test performance.
"""

_OPTIMIZED_DATA = {
    "materials": {
        "aluminum": {
            "name": "aluminum",
            "formula": "Al",
            "category": "metal",
            "density": "2.70 g/cm³",
            "melting_point": "660.3°C",
            "author_id": "US_AUTHOR"
        },
        "copper": {
            "name": "copper", 
            "formula": "Cu",
            "category": "metal",
            "density": "8.96 g/cm³",
            "melting_point": "1084.6°C",
            "author_id": "CA_AUTHOR"
        },
        "steel": {
            "name": "steel",
            "formula": "Fe + C",
            "category": "alloy",
            "density": "7.85 g/cm³",
            "melting_point": "1370°C",
            "author_id": "ITALY_AUTHOR"
        }
    },
    "authors": {
        "US_AUTHOR": {
            "name": "John Smith",
            "country": "US",
            "expertise": "Industrial cleaning"
        },
        "ITALY_AUTHOR": {
            "name": "Alessandro Moretti",
            "country": "Italy",
            "expertise": "Laser materials engineering"
        },
        "INDONESIA_AUTHOR": {
            "name": "Ikmanda Roswati",
            "country": "Indonesia",
            "expertise": "Industrial laser applications"
        }
    },
    "test_configs": {
        "default_material": "aluminum",
        "test_batch_size": 3,
        "mock_api_responses": True
    }
}
