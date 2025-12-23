# Card Restructure Implementation Checklist

**Date:** December 22, 2025  
**Related Spec:** `FRONTMATTER_CARD_RESTRUCTURE_SPEC.md`  
**Status:** Phase 1 & 2 Complete (Source Data), Phase 3 & 4 Pending

---

## Phase Status

✅ **Phase 1:** Card schemas added to all 438 entities (COMPLETE)  
✅ **Phase 2:** 1,061 relationships restructured (COMPLETE)  
✅ **Phase 2.5:** Entity ID suffixes added - All 438 entities now have domain-specific suffixes (COMPLETE)
⏳ **Phase 3:** Frontend component updates (PENDING)  
✅ **Phase 4:** Backend export system - Library enrichment disabled, all exports valid (COMPLETE)  
✅ **Phase 4.5:** Relationship URL cleanup - 3,932 redundant URLs removed (COMPLETE - Dec 23)
✅ **Phase 5:** Export validation - 438/438 files valid (COMPLETE)

---

## Frontend Checklist (Phase 3)

### 🎨 **Card Component Updates**

- [ ] **Update card reading logic** across all card components:
  - [ ] `MaterialCard.tsx` - Read from `card.default.*` instead of `card.*`
  - [ ] `CompoundCard.tsx` - Same update
  - [ ] `ContaminantCard.tsx` - Same update
  - [ ] `SettingCard.tsx` - Same update

- [ ] **Add context-aware card selection**:
  - [ ] Add `context` prop to card components (e.g., `contamination_context`, `material_context`)
  - [ ] Fallback logic: Try `card[context]` → `card.default`
  - [ ] Example: On contaminant page, use `card.contamination_context` if available

- [ ] **Update card field mappings**:
  ```typescript
  // OLD: card.heading
  // NEW: card.default.heading (or card[context].heading)
  
  // OLD: card.subtitle
  // NEW: card.default.subtitle
  
  // OLD: card.badge.text
  // NEW: card.default.badge.text
  
  // OLD: card.metric.value
  // NEW: card.default.metric.value
  ```

### 🔗 **Relationship Component Updates**

- [ ] **Update `RelationshipCard.tsx`**:
  - [ ] Read `presentation` from key level (not from items)
  - [ ] Handle `items` as array (not flat object)
  - [ ] Remove `url` field usage (derive from `full_path` via lookup)

- [ ] **Example structure change**:
  ```typescript
  // OLD:
  relationship.items[0].presentation // "card"
  relationship.items[0].url          // "/path"
  relationship.items[0].name         // "Entity Name"
  
  // NEW:
  relationship.presentation          // "card" (at key level)
  relationship.items                 // Array: [{id: "entity-id", entity_type: "material"}]
  // Name and URL come from entity lookup
  ```

### 🔍 **Entity Lookup System**

- [ ] **Create lookup utilities** (`app/utils/frontmatter.ts` or new `entityLookup.ts`):
  - [ ] `loadEntityById(id: string, type: string): Promise<Entity>` - Load full entity data from frontmatter
  - [ ] `getEntityCard(entity: Entity, context?: string): CardData` - Get card with context fallback
  - [ ] `getEntityUrl(entity: Entity): string` - Derive URL from `full_path`
  - [ ] `getEntityName(entity: Entity): string` - Get display name

- [ ] **Implement caching for entity lookups**:
  - [ ] Cache loaded entities to avoid repeated file reads
  - [ ] Use Map or WeakMap for in-memory cache

- [ ] **Update `RelationshipCard.tsx` to use lookups**:
  ```typescript
  // For each item in relationship.items:
  const entity = await loadEntityById(item.id, item.entity_type);
  const cardData = getEntityCard(entity, currentPageContext);
  const url = getEntityUrl(entity);
  const name = getEntityName(entity);
  ```

### 📦 **Grid Component Updates**

- [ ] **Update `CardGridSSR.tsx`**:
  - [ ] Pass `context` prop to child card components
  - [ ] Handle new relationship structure in grid rendering
  - [ ] Pass parent page type as context (e.g., "contamination" for contaminant pages)

### 🛠️ **TypeScript Type Updates**

- [ ] **Update type definitions**:
  - [ ] Create `CardSchema` interface with `default` + context variants
  - [ ] Create `RelationshipItem` interface: `{id: string, entity_type: string}`
  - [ ] Create `Relationship` interface with `presentation` at top level
  - [ ] Update existing entity interfaces to include `card: CardSchema`

- [ ] **Example types**:
  ```typescript
  interface CardVariant {
    heading: string;
    subtitle: string;
    badge: {
      text: string;
      variant: 'success' | 'warning' | 'danger' | 'info' | 'technical';
    };
    metric: {
      value: string;
      unit?: string;
      legend: string;
    };
    severity: 'critical' | 'high' | 'moderate' | 'low';
    icon?: string;
  }
  
  interface CardSchema {
    default: CardVariant;
    contamination_context?: CardVariant;
    material_context?: CardVariant;
    compound_context?: CardVariant;
    setting_context?: CardVariant;
  }
  
  interface RelationshipItem {
    id: string;
    entity_type: 'material' | 'compound' | 'contaminant' | 'setting';
  }
  
  interface Relationship {
    presentation: 'card' | 'link' | 'table';
    items: RelationshipItem[];
  }
  ```

### ✅ **Frontend Testing Checklist**

- [ ] **Visual regression testing**:
  - [ ] All card types render correctly (Material, Compound, Contaminant, Setting)
  - [ ] Context-specific cards display on appropriate pages
  - [ ] Fallback to default works when context variant missing
  - [ ] Card metrics, badges, severity colors display correctly

- [ ] **Functionality testing**:
  - [ ] Entity lookups resolve correctly for all entity types
  - [ ] URLs derived from `full_path` work and navigate correctly
  - [ ] Relationship cards load entity data properly
  - [ ] Context switching works (same entity shows different card on different pages)

- [ ] **Performance testing**:
  - [ ] Entity lookup caching works (no repeated file reads)
  - [ ] Page load times acceptable with entity lookups
  - [ ] No memory leaks from cached entities

- [ ] **Dev build testing**:
  - [ ] No console errors
  - [ ] No TypeScript errors
  - [ ] Build completes successfully
  - [ ] Hot reload works correctly

**Estimated Time:** 2-3 days
- Day 1: Card component updates + context selection
- Day 2: Relationship restructure + entity lookup system  
- Day 3: Testing and bug fixes

---

## Backend Checklist (Phase 4)

### ✅ **DISCOVERY: Export System Already Compliant - FIXED**

**Analysis Date:** December 22, 2025  
**Fix Date:** December 23, 2025  
**Status:** ✅ COMPLETE - Library enrichment disabled, all files valid  
**Documentation:** `EXPORT_STRUCTURE_PRESERVATION_DEC22_2025.md`

#### **Key Findings:**

1. ✅ **`universal_exporter.py` preserves all structure**:
   - Uses `dict(item_data)` copy in `_build_base_frontmatter()`
   - No flattening of card.* or relationship.* fields
   - All nested structures preserved as-is

2. ✅ **Library enrichment was the issue**:
   - Replaced `presentation` with `_section` 
   - Added `presentation` to items array (backwards incompatible)
   - Solution: Disabled in all 4 domain configs

3. ✅ **Validation confirms fix**:
   - Before: 156/625 files valid (25%)
   - After: 438/438 files valid (100%)
   - Zero issues in exported frontmatter

#### **Changes Made:**

- ✅ Disabled `library_enrichments.enabled` in:
  - `export/config/materials.yaml` (already disabled)
  - `export/config/compounds.yaml` (already disabled)
  - `export/config/settings.yaml` (fixed Dec 23)
  - `export/config/contaminants.yaml` (fixed Dec 23)

- ✅ Re-exported all domains (438 files)
- ✅ Validation passed: 438/438 files valid

#### **Testing Completed:**

- ✅ **Run export for all domains**:
  - ✅ Export materials: `python3 run.py --export materials --force`
  - ✅ Export compounds: `python3 run.py --export compounds --force`
  - ✅ Export contaminants: `python3 run.py --export contaminants --force`
  - ✅ Export settings: `python3 run.py --export settings --force`

- ✅ **Validate exported structure**:
  - ✅ Run: `python3 scripts/validation/validate_export_structure.py`
  - ✅ Result: 438/438 files valid
  - ✅ Spot-check: Manual inspection confirmed correct structure

- ✅ **Verify structure preserved**:
  - ✅ `card.default` exists with all required fields
  - ✅ No flattened fields at top level (heading, subtitle, etc.)
  - ✅ `relationships.{type}.presentation` at key level
  - ✅ `relationships.{type}.items` as array
  - ✅ No `presentation` inside items array
  - ✅ No `_section` replacing `presentation`

---

### ~~📤 Export System Updates~~ (NOT NEEDED)

#### ~~A. Card Schema Export~~ ✅ Already Working

- [x] ~~Verify card schemas pass through export~~ - Confirmed via code review
  - [x] `card` field is included in base frontmatter via `dict(item_data)`
  - [x] All card variants (default + contexts) are preserved
  - [x] Works for all 4 domains (materials, compounds, contaminants, settings)

- [x] ~~Add card validation~~ - Validation tools already exist
  - [x] `validate_card_structure.py` - Validates card.default and required fields
  - [x] `validate_export_structure.py` - NEW - Validates exported frontmatter

#### ~~B. Relationship Structure Export~~ ✅ Already Working

- [x] ~~Update relationship processing~~ - No updates needed
  - [x] `presentation` stays at key level (no code moves it)
  - [x] `items` remains as array (preserved by dict copy)
  - [x] No code re-adds `url` field inappropriately
  - [x] No code re-adds intrinsic properties

- [x] ~~Check library enrichments~~ - No changes needed
  - [x] Library relationships use new structure (dict with presentation + items)
  - [x] No code assumes `presentation` in items
  - [x] No code reads flat items (all handle arrays)

- [x] ~~Update relationship enrichers~~ - Already compliant
  - [x] RelationshipURLEnricher reads key-level structure correctly
  - [x] Only adds `url` to items, doesn't restructure
  - [x] Handles `items` as array

#### ~~C. Field Ordering & Validation~~ ✅ Already Working

- [ ] **Update field order** (`export/core/field_validator.py`):
  - [ ] Ensure `card` appears in correct position in frontmatter
  - [ ] Ensure `relationships` structure validated correctly
  - [ ] Add validation rules for new card schema

- [ ] **Update domain configs** (`export/config/*.yaml`):
  - [ ] Verify no generators try to create old-style card fields
  - [ ] Verify no enrichers expect old relationship structure
  - [ ] Check for any hardcoded card field references

### 🔧 **Data Validation Scripts**

- [ ] **Create validation script** (`scripts/validation/validate_card_structure.py`):
  - [ ] Check all entities have `card.default`
  - [ ] Check all required card fields present
  - [ ] Check card severity and badge variant values are valid
  - [ ] Report any entities with missing or invalid card data

- [ ] **Create relationship validation script** (`scripts/validation/validate_relationship_structure.py`):
  - [ ] Check all relationships have `presentation` at key level
  - [ ] Check all relationships have `items` as array
  - [ ] Check no relationships have `url` in items
  - [ ] Check no relationships have intrinsic properties in items
  - [ ] Report any non-compliant relationships

### 📋 **Export Testing**

- [ ] **Test export with new structure**:
  - [ ] Export materials: `python3 run.py --export materials`
  - [ ] Export compounds: `python3 run.py --export compounds`
  - [ ] Export contaminants: `python3 run.py --export contaminants`
  - [ ] Export settings: `python3 run.py --export settings`

- [ ] **Verify exported frontmatter**:
  - [ ] Check 5-10 random files from each domain
  - [ ] Confirm `card.default` structure present
  - [ ] Confirm `relationships[key].presentation` at key level
  - [ ] Confirm `relationships[key].items` is array
  - [ ] Confirm no `url` field in relationship items
  - [ ] Confirm no intrinsic properties in relationship items

- [ ] **Diff check** (compare before/after export):
  - [ ] Run export to temporary directory
  - [ ] Compare with current frontmatter
  - [ ] Verify ONLY expected changes (card structure + relationship structure)
  - [ ] Verify no data loss

### 🔍 **Entity Lookup Backend Support**

- [ ] **Create lookup utilities** (if needed for export system):
  - [ ] `shared/utils/entity_lookup.py` - Load entity from source YAML
  - [ ] Support all entity types (material, compound, contaminant, setting)
  - [ ] Cache loaded entities for performance

- [ ] **Test cross-domain references**:
  - [ ] Material → Compound relationship resolves
  - [ ] Compound → Material relationship resolves
  - [ ] Contaminant → Material relationship resolves
  - [ ] Setting → Material relationship resolves

### 📊 **Metrics & Reporting**

- [ ] **Generate migration report**:
  - [ ] Count entities with cards vs without
  - [ ] Count relationships with new structure vs old
  - [ ] Report on card context variant usage
  - [ ] Report on relationship presentation type distribution

- [ ] **Size comparison report**:
  - [ ] Measure total frontmatter size before/after
  - [ ] Confirm ~3% reduction as estimated in spec
  - [ ] Breakdown by domain

**Estimated Time:** 2-3 days
- Day 1: Export system updates + validation scripts
- Day 2: Testing exports across all domains
- Day 3: Entity lookup support + reporting

---

## Phase 5: Final Validation & Testing

### ✅ **End-to-End Testing**

- [ ] **Full pipeline test**:
  - [ ] Run export for all domains
  - [ ] Deploy to staging
  - [ ] Test all page types render correctly
  - [ ] Test all relationship cards load properly
  - [ ] Test context-specific cards display correctly

- [ ] **Performance testing**:
  - [ ] Measure page load times (before/after)
  - [ ] Check for entity lookup performance issues
  - [ ] Monitor memory usage

- [ ] **Data integrity testing**:
  - [ ] Run all validation scripts
  - [ ] Verify no data loss during migration
  - [ ] Verify all relationships resolve correctly

### 📝 **Documentation Updates**

- [ ] Update `FRONTMATTER_CARD_RESTRUCTURE_SPEC.md` with final status
- [ ] Document entity lookup patterns for future developers
- [ ] Update component documentation with new props/usage
- [ ] Create migration retrospective document

**Estimated Time:** 1-2 days

---

## Total Timeline

| Phase | Days | Status |
|-------|------|--------|
| Phase 1-2: Source Data Migration | 1 | ✅ COMPLETE |
| Phase 2.5: Entity ID Suffixes | 0.5 | ✅ COMPLETE |
| Phase 3: Frontend Updates | 2-3 | ⏳ PENDING |
| Phase 4: Backend Export Fixes | 0.1 | ✅ COMPLETE |
| Phase 5: Validation & Testing | 0.1 | ✅ COMPLETE |
| **Total** | **3.7-4.7 days** | **60% Complete (Backend Done, Frontend Pending)** |

---

## Prerequisites Before Starting Frontend Work

1. ✅ Source data migration complete (Phase 1-2)
2. ⏳ Frontend developer available for 3 days
3. ⏳ Staging environment for testing
4. ⏳ Backup of current production frontmatter

## Prerequisites Before Export

1. ⏳ Frontend components updated and tested
2. ⏳ Backend export system updated
3. ⏳ All validation scripts passing
4. ⏳ Manual QA on dev build successful

---

## Rollback Plan

If issues discovered after export:

1. **Restore frontmatter from backup**:
   ```bash
   rm -rf frontmatter
   cp -r frontmatter.backup.20251222 frontmatter
   ```

2. **Revert frontend changes** (git revert commits)

3. **Disable new features** in frontend (feature flag)

4. **Debug and fix issues**

5. **Re-attempt export** after fixes validated
