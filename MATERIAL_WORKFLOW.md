# Material Generation Workflow

**Complete pipeline from research to production deployment**

---

## 📋 Quick Commands Reference

```bash
# STEP 1: Create new material
python3 run.py --material "MaterialName"

# STEP 2: Validate and enhance with voice
python3 scripts/voice/enhance_materials_voice.py --material MaterialName

# STEP 3: Export to frontmatter
python3 run.py --all --data-only

# STEP 4: Deploy to production
python3 run.py --deploy
```

---

## 🔄 Complete Workflow

### **STEP 1: Research & Generate Material Entry**

Generate complete material data with AI research and content generation.

```bash
# Generate single material (recommended for new materials)
python3 run.py --material "MaterialName"

# Generate multiple materials
python3 run.py --material "Material1" --material "Material2"

# Generate all materials (use with caution)
python3 run.py --all
```

**What this does:**
- ✅ AI research for missing property values
- ✅ Generate caption, subtitle, FAQ content
- ✅ Validate data completeness
- ✅ Save to `materials/data/Materials.yaml`

**Output location:** `materials/data/Materials.yaml`

---

### **STEP 2: Validation & Voice Post-Processing**

Apply author voice patterns to generated content.

```bash
# Enhance single material with voice
python3 scripts/voice/enhance_materials_voice.py --material MaterialName

# Enhance multiple materials
python3 scripts/voice/enhance_materials_voice.py --materials Calcite Alumina Basalt

# Enhance all materials (use with caution)
python3 scripts/voice/enhance_materials_voice.py --all
```

**What this does:**
- ✅ Apply author-specific voice patterns
- ✅ Inject linguistic characteristics (Indonesian, Italian, Taiwan, USA)
- ✅ Enhance caption, subtitle, FAQ fields
- ✅ Update `Materials.yaml` with voice-enhanced content

**Output location:** `materials/data/Materials.yaml` (updated in place)

**Voice markers by author:**
- **Indonesia (Ikmanda Roswati)**: "This process", "practical", "efficiently"
- **Italy (Alessandro Moretti)**: "notably", "notable", elegant language
- **Taiwan (Yi-Chun Lin)**: "particularly", "specifically", "thus"
- **USA (Todd Dunning)**: "Yeah", "pretty", "typically"

---

### **STEP 3: Export to Frontmatter**

Generate frontmatter YAML files from Materials.yaml for Next.js site.

```bash
# Export all materials to frontmatter (FAST - takes seconds)
python3 run.py --all --data-only

# Alternative: Run exporter directly
python3 -m components.frontmatter.core.trivial_exporter
```

**What this does:**
- ✅ Read `materials/data/Materials.yaml` (source of truth)
- ✅ Add category metadata from `Categories.yaml`
- ✅ Enrich properties with min/max ranges
- ✅ Format FAQ with topic highlighting
- ✅ Generate frontmatter YAML files

**Output location:** `frontmatter/materials/*.yaml` (132 files)

**Performance:** ~2-3 seconds for all 132 materials

---

### **STEP 4: Deploy to Production**

Copy frontmatter files to Next.js production site.

```bash
# Deploy all frontmatter to production
python3 run.py --deploy
```

**What this does:**
- ✅ Copy `frontmatter/` directory to Next.js site
- ✅ Preserve directory structure
- ✅ Update existing files
- ✅ Create new files as needed

**Output location:** Next.js production site (configured in deployment settings)

---

## 🎯 Common Workflows

### **New Material (Full Workflow)**

```bash
# 1. Generate
python3 run.py --material "NewMaterial"

# 2. Enhance with voice
python3 scripts/voice/enhance_materials_voice.py --material NewMaterial

# 3. Export to frontmatter
python3 run.py --all --data-only

# 4. Deploy
python3 run.py --deploy
```

### **Update Existing Material Content**

```bash
# 1. Regenerate specific component (caption, subtitle, or FAQ)
python3 run.py --caption "MaterialName"
# OR
python3 run.py --subtitle "MaterialName"
# OR
python3 run.py --faq "MaterialName"

# 2. Enhance with voice
python3 scripts/voice/enhance_materials_voice.py --material MaterialName

# 3. Export to frontmatter
python3 run.py --all --data-only

# 4. Deploy
python3 run.py --deploy
```

### **Batch Voice Enhancement (Existing Materials)**

```bash
# 1. Enhance multiple materials
python3 scripts/voice/enhance_materials_voice.py --materials Aluminum Steel Copper

# 2. Export to frontmatter
python3 run.py --all --data-only

# 3. Deploy
python3 run.py --deploy
```

### **Data Completeness Check**

```bash
# Check what data is missing
python3 run.py --data-completeness-report

# See research priorities
python3 run.py --data-gaps
```

---

## 🚨 Important Notes

### **Data Storage Policy**
- **Materials.yaml** = Single source of truth (ALL generation happens here)
- **Frontmatter files** = Trivial export copies (NO generation, NO validation)
- **NEVER** edit frontmatter files directly - changes will be overwritten
- **ALWAYS** make changes in Materials.yaml, then export

### **Workflow Order Matters**
1. ✅ Generate → Materials.yaml
2. ✅ Enhance → Materials.yaml (updated)
3. ✅ Export → frontmatter/*.yaml
4. ✅ Deploy → production

❌ **DON'T**: Skip Step 3 and deploy directly (deploys OLD frontmatter)  
✅ **DO**: Always export before deploying (ensures latest Materials.yaml content)

### **Voice Enhancement**
- Voice is applied as **post-processing** (separate step after generation)
- Voice patterns saved to Materials.yaml immediately
- Must export to frontmatter to see voice in production

### **Performance**
- Generation (Step 1): ~30-60 seconds per material (AI research + content)
- Voice enhancement (Step 2): ~5-10 seconds per material
- Export (Step 3): ~2-3 seconds for all 132 materials
- Deployment (Step 4): ~5-10 seconds

---

## 📊 Verification Commands

### **Check Materials.yaml Content**
```bash
# View specific material
python3 -c "import yaml; data=yaml.safe_load(open('materials/data/Materials.yaml')); print(data['materials']['MaterialName'])"

# Check FAQ count
python3 -c "import yaml; data=yaml.safe_load(open('materials/data/Materials.yaml')); print(f\"FAQs: {len(data['materials']['MaterialName']['faq'])}\")"
```

### **Check Frontmatter Content**
```bash
# View exported frontmatter
python3 -c "import yaml; data=yaml.safe_load(open('frontmatter/materials/material-name-laser-cleaning.yaml')); print(data)"

# Check FAQ count
python3 -c "import yaml; data=yaml.safe_load(open('frontmatter/materials/material-name-laser-cleaning.yaml')); print(f\"FAQs: {len(data['faq'])}\")"
```

### **Compare Source vs Export**
```bash
# Compare FAQ counts
python3 << 'EOF'
import yaml

material_name = "Calcite"  # Change this
slug = material_name.lower().replace(' ', '-')

# Load both files
materials = yaml.safe_load(open('materials/data/Materials.yaml'))
frontmatter = yaml.safe_load(open(f'frontmatter/materials/{slug}-laser-cleaning.yaml'))

source_faq = len(materials['materials'][material_name].get('faq', []))
export_faq = len(frontmatter.get('faq', []))

print(f"Materials.yaml: {source_faq} FAQs")
print(f"Frontmatter: {export_faq} FAQs")
print(f"Match: {'✅' if source_faq == export_faq else '❌'}")
EOF
```

---

## 🔧 Troubleshooting

### **Problem: Frontmatter has old content**
**Solution:** Run Step 3 (export) before deploying
```bash
python3 run.py --all --data-only
python3 run.py --deploy
```

### **Problem: Voice patterns not appearing**
**Solution:** Make sure you ran voice enhancement (Step 2) and export (Step 3)
```bash
python3 scripts/voice/enhance_materials_voice.py --material MaterialName
python3 run.py --all --data-only
```

### **Problem: Data incomplete errors**
**Solution:** Check what's missing and regenerate
```bash
python3 run.py --data-completeness-report
python3 run.py --material "MaterialName"  # Regenerate
```

### **Problem: FAQ count mismatch**
**Solution:** Materials.yaml is source of truth - export again
```bash
python3 run.py --all --data-only
```

---

## 📁 Key File Locations

```
z-beam-generator/
├── materials/data/
│   ├── Materials.yaml          # SOURCE OF TRUTH
│   └── Categories.yaml         # Category metadata
├── frontmatter/materials/      # EXPORT TARGET
│   └── *.yaml                  # 132 frontmatter files
├── scripts/voice/
│   └── enhance_materials_voice.py  # Voice post-processor
├── components/frontmatter/core/
│   └── trivial_exporter.py     # Export engine
└── run.py                      # Main CLI
```

---

## 🎓 Best Practices

1. **Generate one material at a time** - Easier to verify quality
2. **Always enhance with voice** - Maintains author authenticity
3. **Export before deploy** - Ensures latest content goes to production
4. **Verify after each step** - Use verification commands above
5. **Check Materials.yaml first** - It's the source of truth
6. **Don't edit frontmatter directly** - Changes will be overwritten

---

**Last Updated:** November 6, 2025  
**Version:** 1.0
