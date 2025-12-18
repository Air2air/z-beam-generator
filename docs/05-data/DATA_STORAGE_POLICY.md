# Data Storage Policy - Global Rule

**Status**: Active Policy  
**Effective Date**: November 22, 2025 (Updated for Dual-Write Architecture)  
**Applies To**: All code, tests, and documentation

---

## 🎯 Core Principle

**ALL data updates MUST be saved to Materials.yaml or Categories.yaml.**

**Frontmatter files receive IMMEDIATE PARTIAL UPDATES (changed fields only) - never read for data persistence.**

---

## 📋 Policy Statement

### Source of Truth
- ✅ **Materials.yaml** - Single source of truth for all material-specific data
- ✅ **Categories.yaml** - Single source of truth for all category-wide data
- ✅ **Frontmatter YAML files** - Receive immediate field-level updates (write-only mirror)
- ❌ **Frontmatter** - Never read for data persistence or updates

### 🚨 MANDATORY REQUIREMENT: Field Isolation During Generation

**Component generation with flags (--description, --micro, --subtitle, --faq) MUST ONLY update the specified field in frontmatter.**

**FIELD UPDATE RULES:**
- ✅ `--description` → Updates ONLY `description` field (preserves subtitle, micro, faq, author, properties, etc.)
- ✅ `--micro` → Updates ONLY `caption` field (preserves description, subtitle, faq, author, properties, etc.)
- ✅ `--subtitle` → Updates ONLY `subtitle` field (preserves description, micro, faq, author, properties, etc.)
- ✅ `--faq` → Updates ONLY `faq` field (preserves description, micro, subtitle, author, properties, etc.)

**VIOLATIONS:**
- ❌ Overwriting ANY unrelated field during component generation
- ❌ Full frontmatter rewrite when only one field changed
- ❌ Modifying author, metadata, properties, or any non-target field

**ENFORCEMENT:**
- 15 automated tests verify field isolation
- See: `tests/test_frontmatter_partial_field_sync.py`
- All tests must pass before deployment

### Data Flow Direction - Dual-Write Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              DUAL-WRITE: IMMEDIATE FIELD-LEVEL SYNC              │
└─────────────────────────────────────────────────────────────────┘

Step 1: Generation → Dual Write
  Components ──────────► Materials.yaml (FULL WRITE)
  (AI text generation)         ↓
                              ↓
                        Frontmatter/{material}.yaml (FIELD UPDATE ONLY)
                        [Only updated field written, others preserved]

Step 2: Voice Enhancement → Dual Write
  VoicePostProcessor ──► Materials.yaml (OVERWRITE text fields)
  (Reads, enhances)            ↓
                              ↓
                        Frontmatter/{material}.yaml (FIELD UPDATE ONLY)
                        [Only enhanced field written, others preserved]

Data Flow Rules:
  Materials.yaml:        Frontmatter:
  ✅ WRITE: Full update  ✅ WRITE: Changed field only (immediate sync)
  ✅ READ: Yes           ❌ READ: No (for data persistence)
  ✅ UPDATE: Yes         ✅ UPDATE: Yes (field-level automatic sync)
```

---

## 🎯 Critical Architectural Principle

### Frontmatter Export is Trivial

**All complex operations happen on Materials.yaml:**
- ✅ AI text generation (micros, descriptions, etc.) → Materials.yaml
- ✅ Voice enhancement (OVERWRITES text fields) → Materials.yaml
- ✅ Property research and discovery → Materials.yaml
- ✅ Completeness validation → Materials.yaml
- ✅ Quality scoring and thresholds → Materials.yaml
- ✅ Schema validation → Materials.yaml
- ✅ Data integrity checks → Materials.yaml

**Frontmatter export is a simple copy + combine operation:**
- ✅ Read from Materials.yaml (already validated, complete, voice-enhanced)
- ✅ Read from Categories.yaml (metadata only, NO fallback ranges)
- ✅ Combine both sources
- ✅ Write YAML file
- ❌ NO API calls needed (content already generated and enhanced)
- ❌ NO validation needed (already validated)
- ❌ NO completeness checks needed (already complete)
- ❌ NO quality scoring needed (already scored)
- ❌ NO voice enhancement needed (already applied in Materials.yaml)

**Result**: Frontmatter export for 132 materials should take **seconds**, not minutes.

**Workflow Commands:**
```bash
# Step 1: Generate content → Materials.yaml
python3 run.py --micro "Steel"

# Step 2: Apply voice → OVERWRITES fields in Materials.yaml  
python3 scripts/voice/enhance_materials_voice.py --material "Steel"

# Step 3: Manual export → combines Materials.yaml + Categories.yaml → frontmatter
python3 run.py --material "Steel" --data-only
```

### 🚫 Zero Tolerance: No Fallback Ranges

**CRITICAL POLICY**: The system has ZERO fallback ranges anywhere.

- ❌ NO category-level fallback ranges in frontmatter export
- ❌ NO default property values anywhere
- ❌ NO template fallbacks in any component
- ❌ NO "use category range if material missing" logic
- ✅ Materials.yaml MUST have 100% complete data for all materials
- ✅ Export fails if data is incomplete (fail-fast validation)
- ✅ Categories.yaml provides metadata only, NOT fallback values
- ✅ ALL property values come from Materials.yaml only

**Why No Fallbacks**:
1. **Data integrity**: Every material must have its own researched values
2. **Scientific accuracy**: Category ranges are too broad for specific materials
3. **Fail-fast principle**: Missing data is a critical error, not a fallback case
4. **Transparency**: Clear when data is missing vs. using inferior substitutes

```python
# ✅ CORRECT: Export fails if data incomplete
def export_to_frontmatter(material_name):
    material_data = load_materials_yaml(material_name)
    
    # Fail fast if required data missing
    if not material_data.get('properties'):
        raise DataIncompleteError(f"{material_name} missing properties - fix in Materials.yaml")
    
    # Just copy complete data - no fallbacks
    frontmatter = {'properties': material_data['properties']}
    return frontmatter

# ❌ WRONG: Using category fallback ranges
def export_to_frontmatter(material_name):
    material_data = load_materials_yaml(material_name)
    category_data = load_categories_yaml(material_data['category'])
    
    # NEVER DO THIS - no fallback ranges allowed
    for prop in category_data['properties']:
        if prop not in material_data['properties']:
            material_data['properties'][prop] = category_data['properties'][prop]  # ❌ FORBIDDEN
```


def export_to_frontmatter(material_name):
    """Trivial YAML-to-YAML copy. No API, no validation."""
    # Load from source of truth (already validated, complete)
    material_data = load_materials_yaml(material_name)
    
    # Simple field mapping (no generation, no validation)
    frontmatter = {
        'title': material_data['title'],
        'micro': material_data['micro'],  # Already generated in Materials.yaml
        'properties': material_data['properties'],  # Already validated
        'applications': material_data['applications'],  # Already researched
        # ... just copy fields ...
    }
    
    # Write output (instant, no API calls)
    save_frontmatter_yaml(frontmatter)
    return ComponentResult(success=True)
```

**Why This Matters**:
- User expectation: "Frontmatter should be instant, without API calls" ✅ CORRECT
- System design: All expensive operations on Materials.yaml, export is free
- Performance: 132 materials in seconds vs. hours
- Reliability: No API dependencies for export

---

## 🚫 Prohibited Patterns

### ❌ NEVER Do This

```python
# BAD: Reading frontmatter to update Materials.yaml
frontmatter_data = yaml.safe_load(open('frontmatter/aluminum-laser-cleaning.yaml'))
material_data['properties']['density'] = frontmatter_data['properties']['density']

# BAD: Storing new data only in frontmatter
frontmatter['new_property'] = researched_value
# ... save frontmatter only, without updating Materials.yaml

# BAD: Using frontmatter as intermediate storage
if not materials_yaml_has_property:
    check_frontmatter_file()  # Never check frontmatter for missing data

# BAD: Two-way sync
sync_frontmatter_to_materials()  # Only one direction allowed
```

---

## ✅ Correct Patterns

### ✅ ALWAYS Do This

```python
# GOOD: Save to Materials.yaml first, then generate frontmatter
self.persist_researched_properties(material_name, researched_properties)
frontmatter = self.generate_frontmatter(material_name)

# GOOD: Update Materials.yaml, regenerate frontmatter
with open('data/Materials.yaml', 'r+') as f:
    materials = yaml.safe_load(f)
    materials['materials'][material_name]['properties']['density'] = new_value
    f.seek(0)
    yaml.dump(materials, f)
    f.truncate()

# Regenerate frontmatter from updated Materials.yaml
python3 run.py --material "MaterialName"

# GOOD: All research saves to Materials.yaml immediately
def discover_and_research_properties(...):
    # Research properties
    quantitative = self.research_properties(...)
    
    # Save to Materials.yaml IMMEDIATELY
    if quantitative:
        self.persist_researched_properties(material_name, quantitative)
    
    # Return for frontmatter generation
    return ResearchResult(quantitative_properties=quantitative)
```

---

## 📐 Architecture Requirements

### PropertyManager Implementation

**REQUIRED**: All PropertyManager methods must persist to Materials.yaml

```python
class PropertyManager:
    def discover_and_research_properties(...):
        """
        Discover and research missing properties.
        
        CRITICAL: MUST persist all researched properties to Materials.yaml
        before returning results for frontmatter generation.
        """
        # Step 1: Research
        quantitative = self.research_missing_properties(...)
        
        # Step 2: MANDATORY - Persist to Materials.yaml
        if quantitative:
            self.persist_researched_properties(material_name, quantitative)
        
        # Step 3: Return for frontmatter generation
        return ResearchResult(quantitative_properties=quantitative)
    
    def persist_researched_properties(self, material_name, properties):
        """
        Save researched properties to Materials.yaml.
        
        MANDATORY: This method MUST be called for all AI-researched properties.
        Creates timestamped backup before modifying Materials.yaml.
        """
        # Create backup
        backup_file = self.materials_file.with_suffix(
            f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'
        )
        shutil.copy2(self.materials_file, backup_file)
        
        # Update Materials.yaml
        with open(self.materials_file, 'r+') as f:
            materials_data = yaml.safe_load(f)
            # Update material properties
            materials_data['materials'][material_name]['properties'].update(properties)
            f.seek(0)
            yaml.dump(materials_data, f)
            f.truncate()
```

### Frontmatter Generator Implementation

**REQUIRED**: Frontmatter generators must NEVER write data back to Materials.yaml

```python
class StreamlinedFrontmatterGenerator:
    def generate(self, material_name):
        """
        Generate frontmatter OUTPUT from Materials.yaml source data.
        
        CRITICAL: This is ONE-WAY generation only.
        - ✅ READ from Materials.yaml
        - ✅ WRITE to frontmatter file
        - ❌ NEVER write back to Materials.yaml
        """
        # Load source data
        material_data = get_material_by_name(material_name)  # From Materials.yaml
        
        # Generate frontmatter content
        frontmatter = self._generate_from_yaml(material_name, material_data)
        
        # Save frontmatter OUTPUT (never read this back for data)
        self._save_frontmatter(frontmatter)
        
        return ComponentResult(success=True)
```

---

## 🧪 Testing Requirements

### Required Test Coverage

All tests MUST verify the data storage policy:

```python
def test_researched_properties_saved_to_materials_yaml():
    """Verify all AI-researched properties are saved to Materials.yaml"""
    # Research property
    result = property_manager.discover_and_research_properties(
        material_name='TestMaterial',
        material_category='metal',
        existing_properties={}
    )
    
    # CRITICAL: Verify saved to Materials.yaml
    with open('data/Materials.yaml') as f:
        materials = yaml.safe_load(f)
        material_props = materials['materials']['TestMaterial']['properties']
        
        # All researched properties MUST be in Materials.yaml
        for prop_name in result.quantitative_properties:
            assert prop_name in material_props
            assert material_props[prop_name]['source'] == 'ai_research'

def test_frontmatter_never_modifies_materials_yaml():
    """Verify frontmatter generation doesn't modify Materials.yaml"""
    # Get Materials.yaml hash before generation
    import hashlib
    with open('data/Materials.yaml', 'rb') as f:
        hash_before = hashlib.md5(f.read()).hexdigest()
    
    # Generate frontmatter
    generator.generate('Aluminum')
    
    # Verify Materials.yaml unchanged
    with open('data/Materials.yaml', 'rb') as f:
        hash_after = hashlib.md5(f.read()).hexdigest()
    
    assert hash_before == hash_after, "Frontmatter generation modified Materials.yaml!"

def test_no_frontmatter_reads_in_data_pipeline():
    """Verify data pipeline never reads from frontmatter files"""
    # Audit all data loading paths
    from components.frontmatter.services.property_manager import PropertyManager
    
    # PropertyManager should NEVER reference frontmatter directory
    source_code = inspect.getsource(PropertyManager)
    assert 'content/components/frontmatter' not in source_code
    assert '.yaml' not in source_code or 'Materials.yaml' in source_code
```

---

## 📚 Documentation Requirements

### All Documentation Must State

**In every relevant doc file, include:**

```markdown
## Data Storage Policy

**CRITICAL**: All data updates must be saved to Materials.yaml or Categories.yaml.

Frontmatter files are **OUTPUT ONLY** - they are regenerated from Materials.yaml 
and should never be read for data persistence.

Data Flow: Materials.yaml → Frontmatter (one-way only)
```

### Required Doc Updates

- ✅ `.github/copilot-instructions.md` - Add to Core Principles
- ✅ `docs/QUICK_REFERENCE.md` - Add to common questions
- ✅ `docs/DATA_ARCHITECTURE.md` - Add architecture section
- ✅ `docs/architecture/SYSTEM_ARCHITECTURE.md` - Add data flow diagram
- ✅ `components/frontmatter/README.md` - Add warning section
- ✅ All component READMEs - Add policy statement

---

## 🔍 Code Review Checklist

Before merging any code, verify:

- [ ] All AI research saves to Materials.yaml via `persist_researched_properties()`
- [ ] No code reads frontmatter files for data (only for output verification)
- [ ] PropertyManager has no frontmatter file dependencies
- [ ] Frontmatter generators only read from Materials.yaml/Categories.yaml
- [ ] Tests verify Materials.yaml persistence
- [ ] Tests verify frontmatter doesn't modify source data
- [ ] Documentation updated with policy statement

---

## 🎯 Rationale

### Why This Policy Exists

1. **Single Source of Truth**: One place for all data eliminates sync issues
2. **Data Integrity**: Materials.yaml is version controlled and backed up
3. **Regeneration Safety**: Frontmatter can be regenerated anytime from Materials.yaml
4. **Clear Separation**: Source data vs. generated output
5. **Audit Trail**: Git history tracks all Materials.yaml changes
6. **Performance**: No need to parse 124 frontmatter files for data

### What Happens Without This Policy

❌ **Data Inconsistency**: Frontmatter and Materials.yaml drift apart  
❌ **Lost Research**: AI research only in frontmatter, lost on regeneration  
❌ **Sync Complexity**: Need bidirectional sync logic (brittle)  
❌ **Merge Conflicts**: Frontmatter conflicts hard to resolve  
❌ **Slow Queries**: Need to parse all frontmatter to find data  
❌ **No History**: Can't track data changes in git effectively

### What This Policy Ensures

✅ **Data Persistence**: All research saved permanently to Materials.yaml  
✅ **Fast Regeneration**: Frontmatter regenerates from authoritative source  
✅ **Clean Git History**: Only source data changes tracked  
✅ **No Sync Issues**: One-way flow prevents inconsistencies  
✅ **Self-Improving System**: Each generation adds to Materials.yaml knowledge  
✅ **Instant Future Generations**: Researched data reused, no re-research needed

---

## 🚀 Implementation Examples

### Example 1: Property Research Pipeline

```python
def discover_and_research_properties(self, material_name, material_category, existing_properties):
    """Complete research pipeline with mandatory Materials.yaml persistence"""
    
    # Step 1: Identify missing properties
    missing_props = self._identify_missing_properties(existing_properties, material_category)
    
    # Step 2: Research missing properties via AI
    researched = self._research_missing_properties(material_name, missing_props)
    
    # Step 3: MANDATORY - Save to Materials.yaml IMMEDIATELY
    if researched:
        self.logger.info(f"💾 Persisting {len(researched)} researched properties to Materials.yaml...")
        success = self.persist_researched_properties(material_name, researched)
        if not success:
            raise GenerationError(f"Failed to persist researched properties to Materials.yaml")
    
    # Step 4: Return for frontmatter generation (frontmatter is output only)
    return ResearchResult(
        quantitative_properties=researched,
        material_category=material_category
    )
```

### Example 2: Harvest Tool (DEPRECATED Pattern)

```python
# ❌ OLD: harvest_frontmatter_research.py
# This pattern should NOT be needed if policy is followed

# The harvest tool was needed because research wasn't being saved to Materials.yaml
# With proper implementation of this policy, harvest tools become unnecessary
```

### Example 3: Batch Generation

```python
# ✅ CORRECT: Batch generation with automatic persistence
for material in materials_list:
    # PropertyManager.discover_and_research_properties automatically:
    # 1. Researches missing properties
    # 2. Saves to Materials.yaml
    # 3. Returns data for frontmatter generation
    
    generator.generate(material)  # Frontmatter generated from Materials.yaml
    
# Result: Materials.yaml grows with each material
# Future runs are instant (no re-research needed)
```

---

## 📊 Monitoring & Verification

### Automated Checks

```bash
# Check 1: Verify no frontmatter reads in production code
grep -r "content/components/frontmatter" components/frontmatter/services/ && echo "❌ VIOLATION" || echo "✅ PASS"

# Check 2: Verify PropertyManager has persist method
grep -q "persist_researched_properties" components/frontmatter/services/property_manager.py && echo "✅ PASS" || echo "❌ VIOLATION"

# Check 3: Verify Materials.yaml backups exist
ls data/Materials.backup_*.yaml 2>/dev/null | wc -l | grep -q "^[1-9]" && echo "✅ PASS" || echo "⚠️ WARNING"

# Check 4: Run policy compliance test
python3 -m pytest tests/test_data_storage_policy.py -v
```

### Manual Verification

```python
# Verify data persistence in Materials.yaml
import yaml

with open('data/Materials.yaml') as f:
    materials = yaml.safe_load(f)
    
# Check for ai_research source tags
ai_research_count = 0
for material_name, material_data in materials['materials'].items():
    props = material_data.get('properties', {})
    for prop_name, prop_data in props.items():
        if isinstance(prop_data, dict) and prop_data.get('source') == 'ai_research':
            ai_research_count += 1

print(f"✅ {ai_research_count} AI-researched properties persisted in Materials.yaml")
```

---

## 🔄 Migration Guide

### For Existing Code

If you find code that violates this policy:

1. **Identify the violation**
   ```python
   # Example violation
   frontmatter_data = load_frontmatter(material_name)
   materials_data['properties'] = frontmatter_data['properties']  # ❌ Wrong direction
   ```

2. **Fix the data flow**
   ```python
   # Correct implementation
   materials_data = load_materials_yaml(material_name)  # ✅ Source of truth
   frontmatter = generate_frontmatter(materials_data)   # ✅ Output only
   ```

3. **Add persistence**
   ```python
   # Ensure all research saves to Materials.yaml
   if researched_properties:
       persist_researched_properties(material_name, researched_properties)
   ```

4. **Add tests**
   ```python
   def test_policy_compliance():
       """Verify this code follows data storage policy"""
       # Test that Materials.yaml is source of truth
       # Test that frontmatter is output only
   ```

---

## � Complete Unified Workflow with Auto-Remediation

**Command**: `python3 run.py --run "MaterialName"`

### 5-Step Inline Workflow

```
┌────────────────────────────────────────────────────────────────────┐
│  STEP 0: DATA COMPLETENESS VALIDATION + AUTO-REMEDIATION (INLINE) │
└────────────────────────────────────────────────────────────────────┘
1. Validate Material Data in Materials.yaml
   - Check critical sections (properties, machine_settings)
   - Detect null/missing values
   - If incomplete → Trigger PropertyManager.discover_and_research_properties()
   - Auto-remediation saves directly to Materials.yaml

2. Validate Category Ranges in Categories.yaml
   - Check all category_ranges for null min/max
   - If incomplete → Trigger CategoryRangeResearcher.research_property_range()
   - Auto-remediation saves directly to Categories.yaml

Result: Materials.yaml + Categories.yaml = 100% complete

┌────────────────────────────────────────────────────────────────────┐
│  STEP 1: TEXT CONTENT GENERATION → Materials.yaml                 │
└────────────────────────────────────────────────────────────────────┘
- Generate micro (before/after) → Save to Materials.yaml
- Generate subtitle → Save to Materials.yaml
- Generate FAQ (2-8 questions) → Save to Materials.yaml
- Uses UnifiedMaterialsGenerator with prompt templates
- AI-driven, high variability content

Result: Materials.yaml has raw text content (no voice yet)

┌────────────────────────────────────────────────────────────────────┐
│  STEP 2: VOICE ENHANCEMENT → OVERWRITES Materials.yaml TEXT       │
└────────────────────────────────────────────────────────────────────┘
- Load TEXT fields from Materials.yaml (micro, subtitle, FAQ)
- Apply author-specific voice markers (Italian, Korean, Taiwan, India)
- OVERWRITE text fields in Materials.yaml with voice-enhanced versions
- Voice enhancement is PERMANENT in Materials.yaml

Result: Materials.yaml has voice-enhanced content

┌────────────────────────────────────────────────────────────────────┐
│  STEP 3: QUALITY VALIDATION                                        │
└────────────────────────────────────────────────────────────────────┘
- Check voice markers present in micro/subtitle
- Validate word counts (10+ words per micro, 2-8 FAQs)
- Ensure completeness (all required fields present)
- Quality gates: human believability, tone consistency

Result: Content quality verified

┌────────────────────────────────────────────────────────────────────┐
│  STEP 4: FRONTMATTER EXPORT (Trivial Copy Operation)              │
└────────────────────────────────────────────────────────────────────┘
- Read Materials.yaml (already complete, validated, voice-enhanced)
- Read Categories.yaml (metadata only, NO fallback ranges)
- Combine both sources into frontmatter structure
- Write to frontmatter/materials/{material}-laser-cleaning.yaml
- OVERWRITES existing file
- NO API calls, NO validation, NO complex operations
- Should take seconds for 132 materials

Result: Frontmatter files = exact copy of Materials.yaml + Categories.yaml metadata
```

### Auto-Remediation Architecture

**Missing Material Properties**:
```python
# Triggered by: Missing/null properties or machine_settings
PropertyManager.discover_and_research_properties(material_name)
  → Research property values using AI
  → Validate ranges against Categories.yaml
  → Save to Materials.yaml immediately
  → Workflow continues with complete data
```

**Missing Category Ranges**:
```python
# Triggered by: Null min/max in Categories.yaml category_ranges
CategoryRangeResearcher.research_property_range(property_name, category)
  → Use pre-researched ranges (confidence 0.92-0.99)
  → Fallback to default ranges (confidence 0.7)
  → Save to Categories.yaml immediately
  → Workflow continues with complete ranges
```

### Key Architectural Points

1. **All AI operations happen in Steps 0-2** on Materials.yaml
2. **Frontmatter export (Step 4) is instant** - no AI, no validation
3. **Auto-remediation is inline** - no manual intervention needed
4. **Voice enhancement OVERWRITES** text fields in Materials.yaml
5. **Categories.yaml provides metadata only** - NEVER fallback values
6. **100% data completeness enforced** before generation proceeds

### Performance Expectations

- **Step 0 (Validation + Auto-Remediation)**: 5-30 seconds (if research needed)
- **Step 1 (Text Generation)**: 10-30 seconds (3 AI API calls)
- **Step 2 (Voice Enhancement)**: 5-15 seconds (1 AI API call)
- **Step 3 (Quality Validation)**: <1 second (local checks)
- **Step 4 (Frontmatter Export)**: <1 second (simple YAML copy)

**Total Time**: ~20-75 seconds per material (depending on auto-remediation needs)
**132 Materials**: Should complete in 45-165 minutes (with auto-remediation)
**Frontmatter Export Only**: Should complete in <2 minutes (132 × <1s)

---

## 📝 Summary

**The Rule**: Materials.yaml ← Source of Truth → Frontmatter (Output Only)

**The Flow**: Validation + Auto-Remediation → Generation → Voice Enhancement → Quality Check → Frontmatter Export

**The Test**: Can I delete all frontmatter files and regenerate them in <2 minutes? (Answer must be YES)

**The Result**: Self-improving system that accumulates knowledge in Materials.yaml + Categories.yaml

---

**Last Updated**: October 27, 2025  
**Policy Owner**: System Architecture  
**Enforcement**: Automated tests + code review + inline validation
