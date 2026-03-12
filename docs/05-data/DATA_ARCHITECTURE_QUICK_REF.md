# Data Architecture Quick Reference

**Last Updated**: December 19, 2025  
**Full Analysis**: `E2E_DATA_ARCHITECTURE_EVALUATION_DEC19_2025.md`  
**Overall Grade**: A- (91/100)

---

## 🎯 At-a-Glance Summary

| Metric | Value | Status |
|--------|-------|--------|
| **Primary Data** | 6.2 MB (5 files) | ✅ Optimal |
| **Total Items** | 438 (153+98+153+34) | ✅ Well-sized |
| **Learning Records** | 16,554 records | ✅ Active |
| **Cross-References** | 2,730 associations | ✅ Bidirectional |
| **Data Completeness** | 94% | ✅ Excellent |
| **Integrity** | 100% (0 broken refs) | ✅ Perfect |
| **Waste Files** | 3.2 MB (cleanup needed) | ⚠️ Action required |

---

## 📂 Core Data Files

```
data/
├── materials/
│   └── Materials.yaml          3.0 MB  153 items  ✅ PRIMARY
├── contaminants/
│   └── Contaminants.yaml       2.0 MB   98 items  ✅ PRIMARY
├── settings/
│   └── Settings.yaml           712 KB  153 items  ✅ PRIMARY
├── compounds/
│   └── Compounds.yaml          200 KB   34 items  ✅ PRIMARY
└── associations/
    └── DomainAssociations.yaml 152 KB 2,730 assocs ✅ PRIMARY
```

---

## 🔄 Data Flow (3 Main Pipelines)

### 1. Text Generation Pipeline
```
Python Text Request → Domain Coordinator → QualityEvaluatedGenerator
→ Materials.yaml (SAVE) → Frontmatter (SYNC) → Learning DB
```

Grok-first source workflows write canonical aggregate YAML upstream of export and are not part of the Python generation path shown above.

### 2. Export Pipeline
```
Deploy Command → FrontmatterExporter → Load Source Data
→ Apply Export Transforms → Order Fields → Write Frontmatter
```

### 3. Research Pipeline
```
Research Script → API Call → Validate → Materials.yaml (SAVE)
→ [Manual Export] → Frontmatter (UPDATE)
```

---

## ✅ Architecture Strengths

1. **Domain Separation** (A+)
   - Materials.yaml = properties ONLY
   - Settings.yaml = machine settings ONLY
   - Zero cross-contamination

2. **Hybrid Contamination** (A+)
   - Contaminants.yaml = source (pattern → materials)
   - Materials.yaml = cached reverse index (material → patterns)
   - O(1) lookup both directions

3. **Bidirectional Relationships** (A+)
   - 2,730 total associations (4 relationship types)
   - Material ↔ Contaminant: 1,063 each direction
   - Contaminant ↔ Compound: 302 each direction
   - Both directions maintained automatically
   - Zero orphaned references

4. **Learning System** (A)
   - 16,554 learning records
   - 3 databases (text, AI detection, image)
   - Sweet spot optimization active

5. **Fail-Fast Validation** (A)
   - Missing data causes immediate errors
   - 313/314 tests passing (99.7%)
   - Zero silent failures

---

## ⚠️ Immediate Actions Needed

### Tonight (40 minutes, 3.2 MB saved)

```bash
# Run cleanup script
./scripts/maintenance/data_architecture_cleanup.sh

# Manual edits:
# 1. Add schema_version: 2.0.0 to Materials.yaml (top of file)
# 2. Fix association count: 635 → 619 in DomainAssociations.yaml
```

**Files to Delete** (2.4 MB):
- `data/materials/tmpoxw4bv9n.yaml` (1.8 MB temp file)
- `data/contaminants/tmp1ussiti8.yaml` (616 KB temp file)
- `data/materials/MachineSettings.yaml` (172 KB legacy)

**Files to Archive** (600 KB):
- `data/compounds/Compounds.yaml.backup`
- `data/compounds/Compounds.yaml.pre-migration-backup`
- `data/associations/ExtractedLinkages.yaml.old`

---

## 🎯 Priority Improvements (This Week)

### 1. Consolidate Learning Databases (2-3 hours)
**Current**: 3 databases (z-beam.db, learning.db, generation_history.db)  
**Proposed**: 1 database (data/learning.db with organized schema)  
**Benefit**: Simpler management, easier backups, cross-learning analysis

### 2. Add Schema Versioning (1 hour)
**Issue**: Materials.yaml missing schema_version, inconsistent field names  
**Fix**: Add schema_version to all files, create versioning policy doc  
**Benefit**: Data governance, migration tracking

### 3. JSON Schema Validation (3-4 hours)
**Issue**: No automated schema validation (type errors caught late)  
**Fix**: Create JSON Schema for each domain, add validation hooks  
**Benefit**: Catch errors at save time, not at runtime

---

## 📊 Data Completeness Status

| Domain | Completeness | Missing/In Progress |
|--------|--------------|---------------------|
| **Materials** | 95%+ | Minor property gaps |
| **Contaminants** | 92%+ | 40% visual appearance data |
| **Settings** | 100% | None |
| **Compounds** | 85% | 15% health effects text |
| **Associations** | 100% | 0% verified (workflow pending) |

---

## 🔍 Quick Validation Commands

```bash
# Check data integrity
python3 -m pytest tests/test_data_integrity.py

# Verify cross-references
python3 scripts/validation/verify_associations.py

# Check for temporary files
find data -name "tmp*.yaml" -o -name "*.backup" -o -name "*.old"

# Count learning records
sqlite3 data/z-beam.db "SELECT COUNT(*) FROM detection_results;"

# Verify dual-write compliance
python3 tests/test_frontmatter_sync.py
```

---

## 📚 Architecture Documents

| Document | Purpose | Status |
|----------|---------|--------|
| `E2E_DATA_ARCHITECTURE_EVALUATION_DEC19_2025.md` | Complete analysis | ✅ CURRENT |
| `docs/02-architecture/DATA_ARCHITECTURE_SEPARATION.md` | Separation policy | ✅ ENFORCED |
| `docs/02-architecture/CONTAMINATION_ARCHITECTURE.md` | Hybrid pattern | ✅ ACTIVE |
| `docs/05-data/CONTAMINANT_APPEARANCE_POLICY.md` | Visual data policy | ✅ ACTIVE |
| `.github/copilot-instructions.md` (Section 3) | Data storage policy | ✅ ACTIVE |

---

## 🚨 Common Issues & Solutions

### Issue: "Materials.yaml and Settings.yaml both have machine_settings"
**Solution**: Check separation policy - this is PROHIBITED. Settings.yaml = machine settings ONLY.

### Issue: "Contaminant lookup is slow"
**Solution**: Use hybrid architecture - Materials.yaml has cached reverse index for O(1) lookups.

### Issue: "Frontmatter out of sync with Materials.yaml"
**Solution**: Run export: `python3 run.py --deploy`. Dual-write should auto-sync but export regenerates all.

### Issue: "Association count doesn't match metadata"
**Solution**: Known issue - metadata says 635, actual count 619. Fix metadata field.

### Issue: "Learning database growing too large"
**Solution**: Consolidate to single learning.db (Phase 4-7 work), implement retention policy.

---

## 💡 Pro Tips

1. **Always dual-write**: Save to Materials.yaml + sync to frontmatter (MANDATORY)
2. **Check hybrid index**: Use Materials.yaml for "what contaminants?" queries (faster)
3. **Validate on save**: Add JSON Schema validation to catch type errors early
4. **Archive backups**: Don't delete backups, move to data/backups/ directory
5. **Version your schemas**: Add schema_version to all data files for migration tracking

---

## 🎓 Key Architectural Patterns

### Pattern 1: Single Source of Truth
```yaml
# ✅ CORRECT
Materials.yaml:     properties (source)
Settings.yaml:      machine_settings (source)
Frontmatter/*.yaml: generated from sources

# ❌ WRONG
Properties in both Materials.yaml AND Settings.yaml
```

### Pattern 2: Hybrid Indexing
```yaml
# Contaminants.yaml (SOURCE)
rust-oxidation:
  valid_materials: [Steel, Iron, Aluminum]

# Materials.yaml (CACHED REVERSE INDEX)
Steel:
  common_contaminants: [rust-oxidation, industrial-oil]
```

### Pattern 3: Dual-Write
```python
# MANDATORY pattern
save_to_materials_yaml(material, field, value)
sync_field_to_frontmatter(material, field, domain='materials')
```

### Pattern 4: Fail-Fast Validation
```python
# ✅ CORRECT
if not material_exists(material_name):
    raise MaterialNotFoundError(f"Material '{material_name}' not found")

# ❌ WRONG
if not material_exists(material_name):
    logger.warning(f"Material not found, using default")
    return default_material
```

---

## 📞 Need Help?

- **Full Analysis**: `E2E_DATA_ARCHITECTURE_EVALUATION_DEC19_2025.md`
- **AI Assistant Guide**: `docs/08-development/AI_ASSISTANT_GUIDE.md`
- **Quick Reference**: `docs/QUICK_REFERENCE.md`
- **Policy Docs**: `docs/08-development/` (20+ policy documents)

---

**Last Review**: December 19, 2025  
**Next Review**: March 2026 (quarterly assessment)  
**Maintenance**: Run cleanup script monthly to remove temp files
