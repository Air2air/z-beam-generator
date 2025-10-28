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
            "author": {
                "id": 4,
                "name": "Todd Dunning",
                "country": "United States",
                "sex": "m",
                "title": "MA",
                "expertise": "Optical Materials for Laser Systems",
                "image": "/images/author/todd-dunning.jpg"
            }
        },
        "copper": {
            "name": "copper", 
            "formula": "Cu",
            "category": "metal",
            "density": "8.96 g/cm³",
            "melting_point": "1084.6°C",
            "author": {
                "id": 3,
                "name": "Ikmanda Roswati",
                "country": "Indonesia",
                "sex": "m",
                "title": "Ph.D.",
                "expertise": "Ultrafast Laser Physics and Material Interactions",
                "image": "/images/author/ikmanda-roswati.jpg"
            }
        },
        "steel": {
            "name": "steel",
            "formula": "Fe + C",
            "category": "alloy",
            "density": "7.85 g/cm³",
            "melting_point": "1370°C",
            "author": {
                "id": 2,
                "name": "Alessandro Moretti",
                "country": "Italy",
                "sex": "m",
                "title": "Ph.D.",
                "expertise": "Laser-Based Additive Manufacturing",
                "image": "/images/author/alessandro-moretti.jpg"
            }
        }
    },
    "authors": {
        1: {
            "id": 1,
            "name": "Yi-Chun Lin",
            "country": "Taiwan",
            "sex": "f",
            "title": "Ph.D.",
            "expertise": "Laser Materials Processing",
            "image": "/images/author/yi-chun-lin.jpg"
        },
        2: {
            "id": 2,
            "name": "Alessandro Moretti",
            "country": "Italy",
            "sex": "m",
            "title": "Ph.D.",
            "expertise": "Laser-Based Additive Manufacturing",
            "image": "/images/author/alessandro-moretti.jpg"
        },
        3: {
            "id": 3,
            "name": "Ikmanda Roswati",
            "country": "Indonesia",
            "sex": "m",
            "title": "Ph.D.",
            "expertise": "Ultrafast Laser Physics and Material Interactions",
            "image": "/images/author/ikmanda-roswati.jpg"
        },
        4: {
            "id": 4,
            "name": "Todd Dunning",
            "country": "United States",
            "sex": "m",
            "title": "MA",
            "expertise": "Optical Materials for Laser Systems",
            "image": "/images/author/todd-dunning.jpg"
        }
    },
    "test_configs": {
        "default_material": "aluminum",
        "test_batch_size": 3,
        "mock_api_responses": True
    }
}
