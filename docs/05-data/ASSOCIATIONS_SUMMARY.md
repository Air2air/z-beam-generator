# Domain Associations Summary

**Quick Reference**: Complete bidirectional association system  
**Updated**: December 19, 2025

---

## At-a-Glance

| Metric | Value |
|--------|-------|
| **Total Associations** | 2,730 |
| **Relationship Types** | 4 (2 bidirectional pairs) |
| **Material ↔ Contaminant** | 1,063 each direction |
| **Contaminant ↔ Compound** | 302 each direction |
| **Coverage** | 94.9% contaminants have compounds |
| **Test Status** | ✅ All tests passing |

---

## Quick Commands

### View association breakdown
\`\`\`bash
python3 << 'PYEOF'
import yaml
with open('data/associations/DomainAssociations.yaml', 'r') as f:
    d = yaml.safe_load(f)
    print(f"Total: {d['metadata']['total_associations']}")
    print(f"Breakdown: {d['metadata']['breakdown']}")
    for rt in d['metadata']['relationship_types']:
        print(f"  • {rt}")
PYEOF
\`\`\`

### Query examples
\`\`\`bash
# What contaminants can affect Steel?
python3 -c "import yaml; d=yaml.safe_load(open('data/associations/DomainAssociations.yaml')); print(len([a for a in d['associations'] if a['source_id']=='steel' and a['relationship_type']=='can_have_contamination']))"

# What materials can Rust contaminate?
python3 -c "import yaml; d=yaml.safe_load(open('data/associations/DomainAssociations.yaml')); print(len([a for a in d['associations'] if 'rust' in a['source_id'] and a['relationship_type']=='can_contaminate']))"

# What produces CO2?
python3 -c "import yaml; d=yaml.safe_load(open('data/associations/DomainAssociations.yaml')); print(len([a for a in d['associations'] if a['source_id']=='carbon-dioxide' and a['relationship_type']=='byproduct_of']))"
\`\`\`

### Regenerate associations
\`\`\`bash
python3 scripts/sync/regenerate_associations.py
\`\`\`

### Test associations
\`\`\`bash
python3 tests/test_bidirectional_associations.py
\`\`\`

---

## Files

- **Data**: \`data/associations/DomainAssociations.yaml\` (152 KB)
- **Script**: \`scripts/sync/regenerate_associations.py\`
- **Tests**: \`tests/test_bidirectional_associations.py\`
- **Docs**: \`docs/05-data/BIDIRECTIONAL_ASSOCIATIONS.md\` (complete guide)

---

## Recent Changes

### December 19, 2025
- ✅ Made all associations bidirectional (+1,365 associations)
- ✅ Added 14 new compounds (20 → 34)
- ✅ Normalized 228 byproduct entries
- ✅ Achieved 94.9% contaminant-compound coverage
- ✅ Created test suite and documentation

---

## See Also

- \`PHASE1_COMPOUND_NORMALIZATION_COMPLETE_DEC19_2025.md\` - Normalization details
- \`E2E_DATA_ARCHITECTURE_EVALUATION_DEC19_2025.md\` - Architecture overview
- \`docs/05-data/DATA_ARCHITECTURE_QUICK_REF.md\` - Quick reference
