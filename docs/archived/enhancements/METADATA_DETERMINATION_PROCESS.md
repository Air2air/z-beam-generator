# Material Metadata Determination Process

## 1. Author Assignment (Round-Robin Algorithm)

```python
def assign_round_robin_authors(materials_by_category: Dict[str, List[str]]) -> Dict[str, int]:
    """Assign authors in round-robin fashion across all materials."""
    author_assignments = {}
    author_counter = 1

    # Flatten all materials and assign in round-robin
    all_materials = []
    for category, materials in materials_by_category.items():
        all_materials.extend(materials)

    # Sort materials alphabetically for consistent assignment
    all_materials.sort()

    for material in all_materials:
        author_assignments[material] = author_counter
        author_counter = (author_counter % 4) + 1  # Round-robin through 1-4

    return author_assignments
```

**Process:**
1. **Collect all materials**: Gather 109 materials from all 8 categories
2. **Sort alphabetically**: Ensures consistent assignment across runs
3. **Round-robin assignment**: Cycle through authors 1→2→3→4→1→2...
4. **Perfect distribution**: Results in 28,27,27,27 materials per author

## 2. Complexity Determination

```python
COMPLEXITY_MAPPING = {
    # High-end materials requiring precise control
    "very_high": ["Titanium", "Hafnium", "Rhenium", "Carbon Fiber Reinforced Polymer",
                  "Ceramic Matrix Composites CMCs", "Metal Matrix Composites MMCs"],

    # Technical materials requiring expertise
    "high": ["Stainless Steel", "Inconel", "Hastelloy", "Gallium Arsenide", "Silicon Carbide",
             "Alumina", "Zirconia", "Silicon Nitride", "Marble", "Granite"],

    # Standard industrial materials
    "medium": ["Aluminum", "Copper", "Brass", "Bronze", "Glass", "Borosilicate Glass",
               "Fused Silica", "Quartz Glass", "Lead Crystal", "Oak", "Maple", "Cherry"],

    # Basic materials with straightforward processing
    "low": ["Steel", "Iron", "Pine", "Plywood", "MDF", "Concrete", "Brick", "Mortar"]
}
```

**Classification criteria:**
- **Very High (Score 5)**: Exotic metals, advanced composites requiring ultrafast lasers
- **High (Score 4)**: Technical alloys, ceramics, engineered stones requiring expertise
- **Medium (Score 3)**: Common industrial metals, standard glasses, hardwoods
- **Low (Score 2)**: Basic materials, simple processing requirements

## 3. Chemical Formula Assignment

```python
CHEMICAL_FORMULAS = {
    "Aluminum": "Al", "Copper": "Cu", "Iron": "Fe", "Titanium": "Ti",
    "Steel": "Fe-C", "Stainless Steel": "Fe-Cr-Ni", "Brass": "Cu-Zn",
    "Bronze": "Cu-Sn", "Gold": "Au", "Silver": "Ag", "Platinum": "Pt",
    "Silicon": "Si", "Gallium Arsenide": "GaAs", "Silicon Carbide": "SiC",
    "Alumina": "Al2O3", "Zirconia": "ZrO2", "Silicon Nitride": "Si3N4",
    "Quartz Glass": "SiO2", "Fused Silica": "SiO2", "Borosilicate Glass": "B2O3-SiO2",
    "Limestone": "CaCO3", "Marble": "CaCO3", "Granite": "SiO2-Al2O3-K2O"
}
```

**Source**: Standard chemistry references and materials science databases

## 4. Metadata Structure Generated

For each material, the system creates:

```python
metadata = {
    "name": material_name,                    # From original list
    "author_id": author_id,                  # Round-robin assignment
    "complexity": complexity,                # Classification algorithm
    "difficulty_score": get_difficulty_score(complexity),  # 2-5 numeric scale
    "category": category,                    # From original YAML structure
    "documentation_status": "pending",      # Initial status
    "last_updated": "2025-08-31",          # Migration date
    "formula": "Al2O3",                     # If known from lookup table
    "laser_parameters": {                   # Placeholders for calibration
        "fluence_threshold": "TBD",
        "pulse_duration": "TBD",
        "wavelength_optimal": "TBD"
    },
    "applications": ["TBD"],               # To be researched
    "surface_treatments": ["TBD"],         # To be researched
    "industry_tags": ["TBD"]               # To be researched
}
```

## 5. Quality Assurance Metrics

**Perfect Round-Robin Distribution:**
- Author 1: 28 materials (25.7%)
- Author 2: 27 materials (24.8%)
- Author 3: 27 materials (24.8%)
- Author 4: 27 materials (24.8%)

**Complexity Distribution:**
- Low: 8 materials (7.3%)
- Medium: 85 materials (78.0%)
- High: 10 materials (9.2%)
- Very High: 6 materials (5.5%)

**Data Sources:**
- Original materials.yaml (109 materials, 8 categories)
- Authors.json (4 authors with expertise areas)
- Chemistry reference tables (known formulas)
- Materials science classification (complexity scoring)
- Alphabetical sorting (deterministic assignment)

The system ensures **reproducible, balanced, and scientifically sound** metadata assignment.
