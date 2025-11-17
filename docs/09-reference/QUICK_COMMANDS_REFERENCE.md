# Quick Commands Reference

## Two Simple Commands for Common Use Cases

### 1. 📊 Data Refresh (No AI Cost)
**Command**: `python3 scripts/refresh_data.py <material>`

```bash
# Refresh single material data from Materials.yaml
python3 scripts/refresh_data.py Aluminum

# Refresh all materials data (batch)
python3 scripts/refresh_data.py --all

# Preview what would be refreshed
python3 scripts/refresh_data.py Steel --dry-run
```

**What it does**:
- ✅ Updates 20+ data fields from Materials.yaml
- ✅ Zero API calls, zero cost
- ✅ Perfect for frequent data updates
- ✅ Preserves existing text content

---

### 2. 📝 Generate Text Content (AI with Grok)  
**Command**: `python3 scripts/generate_text.py <material>`

```bash
# Generate text content for single material
python3 scripts/generate_text.py Aluminum

# Generate text for all materials (batch)
python3 scripts/generate_text.py --all

# Preview what would be generated
python3 scripts/generate_text.py Titanium --dry-run

# Force refresh existing text
python3 scripts/generate_text.py Steel --force-refresh
```

**What it does**:
- ✅ Refreshes data from Materials.yaml (like #1)
- ✅ Generates high-quality text with Grok AI
- ✅ Updates 11+ text fields (subtitle, descriptions, notes)
- ✅ Best balance of speed/cost/quality

---

## Advanced: Full Control Command

For complete control, use the full hybrid CLI:

```bash
# All 4 modes available
python3 scripts/hybrid_frontmatter_cli.py --material Aluminum --mode data-only
python3 scripts/hybrid_frontmatter_cli.py --material Aluminum --mode text-only  
python3 scripts/hybrid_frontmatter_cli.py --material Aluminum --mode hybrid
python3 scripts/hybrid_frontmatter_cli.py --material Aluminum --mode full

# Get smart recommendations
python3 scripts/hybrid_frontmatter_cli.py --material Aluminum --recommendations
```

---

## Quick Decision Guide

**Need to refresh data after Materials.yaml changes?**
→ Use `refresh_data.py` (fast, free)

**Need better text content or new material?**  
→ Use `generate_text.py` (balanced, recommended)

**Need complete control over generation?**
→ Use `hybrid_frontmatter_cli.py` with specific `--mode`

---

## Test Results Summary

Both commands are working correctly:

### ✅ `refresh_data.py` Test Results
- Mode: data-only
- Fields populated: 20
- AI fields generated: 0
- Cost: Free
- Status: ✅ Success

### ✅ `generate_text.py` Test Results  
- Mode: hybrid (data + text)
- Fields populated: 21
- AI fields generated: 11
- Text fields: subtitle, descriptions, notes, labels
- API: Grok (high quality)
- Status: ✅ Success