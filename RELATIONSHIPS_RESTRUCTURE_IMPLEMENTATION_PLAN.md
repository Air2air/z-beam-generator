# Relationships Restructure - Full Implementation Plan
**Date**: December 23, 2025  
**Decision**: ✅ APPROVED - Prioritize best UX regardless of effort  
**Estimated Timeline**: 3-4 weeks  
**Risk Level**: MEDIUM (breaking changes with careful migration)

---

## Executive Decision

After review, we're implementing the **full hierarchical restructure** because:

✅ **UX Value > Development Effort**
- Engineers can scan technical specs without safety noise
- Safety officers find compliance requirements instantly
- Facility managers get operational guidance separated from specs
- Reduced cognitive load with clear categories

✅ **Alignment with Target Audience**
- Engineers: Need technical compatibility fast
- Safety officers: Need compliance data grouped
- Facility managers: Need time/cost estimates
- Technicians: Need troubleshooting guidance

✅ **Future-Proofing**
- Scales better as we add more relationship types
- Cleaner architecture for maintenance
- Easier to add new fields within existing groups

---

## What We've Already Completed

From our Phase 1 & 2 work (Dec 23, 2025):

✅ **Phase 1 Changes**:
- valid_materials converted to ID format (98 patterns, 1,016 references)
- materials relationship removed from contaminants (export config)
- regulatory_standards naming standardized
- applications migrated to relationships.industry_applications (132 materials)

✅ **Phase 2 Changes**:
- workplace_exposure merged into exposure_limits (19 compounds)
- invalid_materials → caution_materials (4 patterns)

**Status**: 131 frontmatter files already regenerated with Phase 1-2 changes

---

## Full Implementation Phases

### Phase 3: Complete Field Renaming (Week 1, Days 1-2)
**Effort**: 1-2 days  
**Files**: ~400 frontmatter files + 4 export configs

#### Changes:
1. `found_on_materials` → `affects_materials` (97 contaminants)
2. `optimized_for_materials` → `works_on_materials` (153 settings)
3. `prohibited_materials` → `incompatible_materials` (multiple domains)
4. `challenges` → `common_challenges` (if exists)

#### Implementation:
```python
# Source data changes
# data/contaminants/Contaminants.yaml - rename found_on_materials
# data/settings/Settings.yaml - rename optimized_for_materials

# Export config changes
# export/config/contaminants.yaml - update section_metadata + move_to_relationships
# export/config/settings.yaml - update section_metadata + duplicate_fields
# export/config/materials.yaml - update prohibited_materials if exists
# export/config/compounds.yaml - update prohibited_materials if exists
```

**Deliverable**: All field names consistent with frontend spec

---

### Phase 4: Hierarchical Restructure (Week 1-2, Days 3-7)
**Effort**: 5 days  
**Files**: 403 frontmatter files + all export configs + enrichers

#### 4.1 Update Export Configs (Day 3)
Add grouping metadata to all domain configs:

```yaml
# export/config/contaminants.yaml
relationship_groups:
  technical:
    - affects_materials
    - produces_compounds
  safety:
    - regulatory_standards
    - caution_materials
  operational:
    - common_challenges
    - industry_applications

# Similar for materials.yaml, settings.yaml, compounds.yaml
```

#### 4.2 Create Group Enricher (Day 3-4)
New file: `export/enrichers/relationships/group_enricher.py`

```python
class RelationshipGroupEnricher:
    """Groups flat relationships into technical/safety/operational categories."""
    
    def enrich(self, entity, config):
        relationships = entity.get('relationships', {})
        grouped = {
            'technical': {},
            'safety': {},
            'operational': {}
        }
        
        groups_config = config.get('relationship_groups', {})
        
        for group_name, field_names in groups_config.items():
            for field in field_names:
                if field in relationships:
                    grouped[group_name][field] = relationships[field]
        
        # Remove empty groups
        grouped = {k: v for k, v in grouped.items() if v}
        
        return {'relationships': grouped}
```

#### 4.3 Integrate with UniversalExporter (Day 4)
Add group enricher to pipeline in `export/core/universal_exporter.py`:

```python
enrichers = [
    DomainLinkagesEnricher(),
    SectionMetadataEnricher(),
    RelationshipGroupEnricher(),  # NEW - Run after section metadata
    UniversalRestructureEnricher(),
    BreadcrumbEnricher()
]
```

#### 4.4 Update Schema (Day 5)
Create `data/schemas/frontmatter-v6.0.0.json`:

```json
{
  "relationships": {
    "type": "object",
    "properties": {
      "technical": {
        "type": "object",
        "properties": {
          "affects_materials": {"$ref": "#/definitions/relationship_block"},
          "works_on_materials": {"$ref": "#/definitions/relationship_block"},
          "incompatible_materials": {"$ref": "#/definitions/relationship_block"},
          "removes_contaminants": {"$ref": "#/definitions/relationship_block"},
          "produces_compounds": {"$ref": "#/definitions/relationship_block"}
        }
      },
      "safety": {
        "type": "object",
        "properties": {
          "regulatory_standards": {"$ref": "#/definitions/relationship_block"},
          "ppe_requirements": {"$ref": "#/definitions/relationship_block"},
          "caution_materials": {"$ref": "#/definitions/relationship_block"},
          "exposure_limits": {"$ref": "#/definitions/relationship_block"}
        }
      },
      "operational": {
        "type": "object",
        "properties": {
          "common_challenges": {"$ref": "#/definitions/relationship_block"},
          "industry_applications": {"$ref": "#/definitions/relationship_block"},
          "difficulty_level": {
            "type": "string",
            "enum": ["easy", "medium", "hard", "expert"]
          }
        }
      }
    }
  }
}
```

#### 4.5 Export All Domains (Day 5-6)
```bash
python3 run.py --export --domain materials
python3 run.py --export --domain contaminants  
python3 run.py --export --domain settings
python3 run.py --export --domain compounds
```

#### 4.6 Validation (Day 7)
```bash
# Verify hierarchical structure
python3 scripts/validation/validate_relationship_structure.py

# Check no flat relationships remain (except allowed ones)
grep -r "relationships:" frontmatter/ | grep -v "technical\|safety\|operational"

# Schema validation
python3 scripts/validation/validate_frontmatter_schema.py --schema v6.0.0
```

**Deliverable**: All 403 frontmatter files with hierarchical relationship structure

---

### Phase 5: Add Operational Fields (Week 2-3, Days 8-14)
**Effort**: 7 days  
**Files**: All domains (focus on materials + contaminants)

#### 5.1 Add difficulty_level (Day 8-9)
**Calculated from existing challenges data**:

```python
# export/enrichers/operational/difficulty_calculator.py
class DifficultyCalculator:
    def calculate(self, entity):
        challenges = entity.get('relationships', {}).get('operational', {}).get('common_challenges', {}).get('items', [])
        
        if not challenges:
            return 'easy'
        
        critical = sum(1 for c in challenges if c.get('severity') == 'critical')
        high = sum(1 for c in challenges if c.get('severity') == 'high')
        
        if critical >= 2 or high >= 3:
            return 'expert'
        elif critical >= 1 or high >= 2:
            return 'hard'
        elif high >= 1 or len(challenges) >= 3:
            return 'medium'
        return 'easy'
```

Add to enricher pipeline, export all domains.

**Deliverable**: All entities have difficulty_level in operational group

#### 5.2 Add typical_time_per_sqm (Day 10-12)
**Requires expert review + AI estimation**:

1. **AI Generation** (Day 10):
   ```python
   # Use Gemini to estimate based on:
   # - Material hardness
   # - Contamination thickness  
   # - Surface complexity
   # - Typical laser power
   
   prompt = f"""
   Estimate laser cleaning time for:
   Material: {material_name}
   Contamination: {contamination_type}
   Thickness: {thickness}
   
   Provide range in format: "X-Y min/m²"
   """
   ```

2. **Manual Review** (Day 11-12):
   - Export estimates to CSV
   - Subject matter expert reviews and adjusts
   - Import back to source data

**Deliverable**: 90%+ entities have time estimates (verified by expert)

#### 5.3 Add equipment_required (Day 13)
**Extract from existing data + standard requirements**:

```python
# Standard equipment by domain
STANDARD_EQUIPMENT = {
    'materials': [
        {'id': 'fiber-laser', 'specification': '1064nm, 100-500W', 'necessity': 'mandatory'},
        {'id': 'fume-extractor', 'specification': 'HEPA filtration, 500+ CFM', 'necessity': 'mandatory'},
        {'id': 'laser-safety-goggles', 'specification': 'OD 7+ at 1064nm', 'necessity': 'mandatory'}
    ],
    'contaminants': [...],
    'settings': [...]
}

# Add material-specific equipment from challenges/notes
# e.g., "requires surface preparation" → add surface-preparation-tools
```

**Deliverable**: All entities have equipment_required list

#### 5.4 Add best_practices (Day 14)
**Extract from FAQs + descriptions + AI generation**:

```python
# Extract from existing FAQs
faq_items = entity.get('faq', [])
practices = []

for item in faq_items:
    if 'how to' in item['question'].lower() or 'best' in item['question'].lower():
        # Extract actionable advice from answer
        practices.append(extract_practice(item['answer']))

# Add AI-generated practices based on properties
ai_practices = generate_practices(entity)

# Combine and deduplicate
all_practices = practices + ai_practices
```

**Deliverable**: 80%+ entities have 3-5 best practices

---

### Phase 6: Testing & Validation (Week 3-4, Days 15-19)
**Effort**: 5 days

#### 6.1 Automated Tests (Day 15-16)
```python
# tests/export/test_relationship_structure.py
def test_hierarchical_structure():
    """Verify all relationships are grouped."""
    for domain in ['materials', 'contaminants', 'settings', 'compounds']:
        files = glob.glob(f'frontmatter/{domain}/*.yaml')
        for file in files:
            data = yaml.safe_load(open(file))
            rels = data.get('relationships', {})
            
            # Should have groups, not flat fields
            assert 'technical' in rels or 'safety' in rels or 'operational' in rels
            
            # Should NOT have flat fields
            flat_fields = ['affects_materials', 'contaminated_by', 'works_on_materials']
            for field in flat_fields:
                assert field not in rels, f"Flat field {field} found in {file}"

def test_difficulty_levels():
    """Verify all entities have difficulty_level."""
    # Check all materials, contaminants have difficulty in operational group
    
def test_time_estimates():
    """Verify 90%+ have time estimates."""
    
def test_equipment_required():
    """Verify all have equipment lists."""
    
def test_best_practices():
    """Verify 80%+ have best practices."""
```

#### 6.2 Schema Validation (Day 17)
```bash
python3 scripts/validation/validate_frontmatter_schema.py --schema v6.0.0 --strict
```

Expected: 100% pass rate

#### 6.3 Link Integrity (Day 17)
```bash
python3 scripts/validation/link_integrity_validator.py --all-domains
```

Expected: 0 broken links

#### 6.4 Manual Spot Checks (Day 18-19)
- [ ] Load 10 material pages - verify technical group displays
- [ ] Load 10 contaminant pages - verify safety prominent
- [ ] Load 10 settings pages - verify operational guidance clear
- [ ] Check difficulty badges render
- [ ] Verify time estimates make sense
- [ ] Test equipment lists complete
- [ ] Check best practices actionable
- [ ] Mobile responsiveness
- [ ] Performance (page load times)

**Deliverable**: All tests passing, manual validation complete

---

### Phase 7: Documentation & Deployment (Week 4, Days 20-21)
**Effort**: 2 days

#### 7.1 Update Documentation (Day 20)
- [ ] `docs/FRONTMATTER_GENERATION_GUIDE.md` - Add hierarchical structure
- [ ] `docs/01-core/frontmatter/STRUCTURE.md` - Update examples
- [ ] `examples/aluminum-unified-frontmatter.yaml` - Show new structure
- [ ] `CHANGELOG.md` - Document v6.0.0 changes
- [ ] Create `docs/migrations/RELATIONSHIPS-V6-MIGRATION.md`

#### 7.2 Deployment (Day 21)
1. **Backup**: Create `frontmatter-backup-20251223/`
2. **Deploy to staging**: Test full site
3. **Monitor**: Check error logs, user feedback
4. **Deploy to production**: Coordinated with frontend
5. **Monitor**: Performance, user engagement metrics

**Deliverable**: v6.0.0 deployed with full documentation

---

## Timeline Summary

| Week | Days | Phase | Deliverable |
|------|------|-------|-------------|
| 1 | 1-2 | Field Renaming | All fields renamed consistently |
| 1-2 | 3-7 | Hierarchical Restructure | 403 files with grouped relationships |
| 2-3 | 8-14 | Operational Fields | difficulty, time, equipment, practices added |
| 3-4 | 15-19 | Testing & Validation | 100% pass rate, manual validation |
| 4 | 20-21 | Documentation & Deploy | v6.0.0 live in production |

**Total**: 21 working days (~4 weeks calendar time)

---

## Success Metrics

### Technical
- ✅ Zero instances of flat relationships (except allowed)
- ✅ 100% schema validation pass rate
- ✅ All relationship IDs resolve
- ✅ All automated tests passing

### User Experience
- ✅ 90%+ entities have difficulty_level
- ✅ 90%+ have time estimates
- ✅ 100% have equipment lists
- ✅ 80%+ have best practices
- ✅ Page load time ≤ current baseline

### Business
- ✅ Improved engagement (time on page)
- ✅ Reduced support queries
- ✅ Positive user feedback

---

## Risk Mitigation

### Risk 1: Schema breaking changes
**Mitigation**: Version bump to v6.0.0, maintain v5.0.0 compatibility during transition

### Risk 2: Frontend not ready
**Mitigation**: Use feature flag, serve v5.0.0 structure until frontend deployed

### Risk 3: Time estimates inaccurate
**Mitigation**: Expert review required, mark as "estimated" with ±20% variance

### Risk 4: Migration bugs
**Mitigation**: Atomic commits, full backups, staged rollout

---

## Next Steps

**IMMEDIATE** (Today):
1. ✅ Get approval from user (THIS DECISION)
2. Start Phase 3: Field renaming

**THIS WEEK**:
- Complete Phase 3 (field renaming)
- Start Phase 4 (hierarchical restructure)

**WEEKS 2-3**:
- Complete Phase 4
- Complete Phase 5 (operational fields)

**WEEK 4**:
- Testing, validation, deployment

---

**Status**: ✅ APPROVED - Proceeding with full implementation  
**Priority**: HIGH  
**Risk**: MEDIUM (mitigated with careful planning)  
**Value**: HIGH (significantly improved UX for target audience)
