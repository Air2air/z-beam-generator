# Visual Appearance Research - Quick Reference

**Date**: November 26, 2025

---

## 🚀 Quick Start

### 1. List Categories
```bash
python3 scripts/research/populate_visual_appearances_all_categories.py --list-categories
```

### 2. Research Single Pattern
```bash
# ALL materials (159 across 10 categories)
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease

# Specific category
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease --category metal

# Multiple categories
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease --category metal,ceramic,glass
```

### 3. Research All Patterns
```bash
# ALL patterns, ALL materials
python3 scripts/research/populate_visual_appearances_all_categories.py --all

# ALL patterns, specific category
python3 scripts/research/populate_visual_appearances_all_categories.py --all --category metal
```

---

## 📊 Material Categories (159 Total)

| Category | Count | Common Examples |
|----------|-------|-----------------|
| metal | 45 | Aluminum, Steel, Copper, Brass, Titanium |
| wood | 21 | Oak, Maple, Pine, Cherry, Walnut |
| stone | 20 | Granite, Marble, Limestone, Sandstone |
| ceramic | 13 | Alumina, Silicon Carbide, Porcelain |
| composite | 13 | Carbon Fiber, Fiberglass, Kevlar |
| plastic | 13 | Acrylic, Polycarbonate, ABS, Nylon |
| glass | 12 | Borosilicate, Tempered, Quartz |
| rare-earth | 8 | Neodymium, Lanthanum, Cerium |
| masonry | 7 | Brick, Concrete, Cement |
| semiconductor | 7 | Silicon, Gallium Arsenide, Germanium |

---

## 💡 Common Use Cases

### Industrial Equipment
```bash
# Oil contamination on machinery parts
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease --category metal
```

### Architectural Restoration
```bash
# Weathering on building materials
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern weathering-oxidation --category stone,masonry
```

### Art Conservation
```bash
# Biological growth on mixed media
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern bio-growth --category wood,stone,metal
```

### Rust Documentation
```bash
# Rust on all metals
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern rust-oxidation --category metal
```

---

## ⚙️ Options

| Flag | Description | Example |
|------|-------------|---------|
| `--pattern` | Single contamination pattern | `--pattern oil-grease` |
| `--all` | All contamination patterns | `--all` |
| `--category` | Filter by category | `--category metal` |
| | Multiple categories | `--category metal,ceramic` |
| | All categories | (omit flag) |
| `--force` | Re-research existing data | `--force` |
| `--api-key` | Provide API key inline | `--api-key "key"` |
| `--list-categories` | Show available categories | `--list-categories` |

---

## 📈 Research Scope

### Single Pattern

| Mode | Materials | API Calls | Time |
|------|-----------|-----------|------|
| Single category | Varies | 7-45 | 2-7 min |
| Multiple categories | Combined | 20-100 | 5-15 min |
| ALL categories | 159 | 159 | 15-20 min |

### All Patterns (15 patterns)

| Mode | Materials | API Calls | Time |
|------|-----------|-----------|------|
| Single category (metal) | 45 | 675 | 1.5 hours |
| ALL categories | 159 | 2,385 | 4-5 hours |

---

## 🎯 Output Format

Each material gets **8 detailed fields**:

1. `description` - Overall appearance
2. `color_variations` - Fresh to aged colors
3. `texture_details` - Surface texture
4. `common_patterns` - Distribution patterns
5. `aged_appearance` - Time-based evolution
6. `lighting_effects` - Lighting behavior
7. `thickness_range` - Measurements (mm)
8. `distribution_factors` - Environmental factors

---

## 🔧 Setup

### API Key
```bash
export GEMINI_API_KEY="your_key_here"
```

### Verify
```bash
echo $GEMINI_API_KEY
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `VISUAL_APPEARANCE_ALL_CATEGORIES_GUIDE.md` | Complete usage guide |
| `VISUAL_APPEARANCE_ALL_CATEGORIES_COMPLETE.md` | Implementation summary |
| `VISUAL_APPEARANCE_RESEARCH_SETUP.md` | API setup & troubleshooting |

---

## ✅ Features

✅ 159 materials across 10 categories  
✅ Dynamic discovery from Materials.yaml  
✅ Category filtering (single/multiple)  
✅ Incremental save (won't lose progress)  
✅ Skip-existing logic (no duplicates)  
✅ Progress tracking (real-time)  
✅ Auto-backup (safe to re-run)  
✅ Force re-research option  

---

## 🎨 Example Output

### Oil on Aluminum (Metal)
```
Dark irregular patches with rainbow iridescence.
Fresh: Amber with sheen. Aged: Nearly black.
Drip marks, fingerprints, pools in crevices.
```

### Oil on Oak (Wood)
```
Deep absorption into grain, significant darkening.
Fresh: Light amber in grain. Aged: Deep brown.
Raised grain texture, concentrates in end grain.
```

### Oil on Granite (Stone)
```
Darker patches emphasizing mineral variations.
Fresh: Slight darkening. Aged: Brown-black staining.
Pools in rough areas, penetrates porous regions.
```

---

**Status**: ✅ Ready to Execute  
**Action**: Set API key and run commands above
