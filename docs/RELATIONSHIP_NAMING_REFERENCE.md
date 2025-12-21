# Relationship Naming Convention - Quick Reference

## 🎯 Pattern

```
{action}_{direction}_{content_type}
```

---

## 📋 All Current Relationship Fields

### By Domain

**Compounds**:
- `produced_from_contaminants` - Created from these contaminants
- `produced_from_materials` - Created from these materials

**Contaminants**:
- `produces_compounds` - This creates these compounds
- `found_on_materials` - Found on these materials

**Materials**:
- `contaminated_by` - Contaminated by these contaminants
- `produces_compounds` - This creates these compounds

**Settings**:
- `optimized_for_materials` - Optimized for these materials
- `removes_contaminants` - This removes these contaminants

---

## 🧭 Directional Prepositions

Use these prepositions to show clear relationship direction:

| Preposition | Use Case | Example |
|-------------|----------|---------|
| **from** | Source/origin | `produced_from_contaminants` |
| **on** | Location/surface | `found_on_materials` |
| **by** | Agent/cause | `contaminated_by` |
| **for** | Purpose/target | `optimized_for_materials` |

---

## ✅ Verb Forms

### Passive Participle + Direction

Pattern: `[verb]_[direction]_[content]`

**Use when**: Showing source, location, or agent
**Examples**:
- `produced_from_` (source)
- `found_on_` (location)
- `contaminated_by_` (agent)
- `derived_from_` (source)
- `detected_on_` (location)

### Active Present Tense

Pattern: `[verb]_[content]`

**Use when**: Showing direct action
**Examples**:
- `produces_compounds`
- `removes_contaminants`
- `creates_compounds`
- `generates_compounds`

### Adjective + For

Pattern: `[adjective]_for_[content]`

**Use when**: Showing purpose or optimization
**Examples**:
- `optimized_for_materials`
- `designed_for_materials`
- `suitable_for_materials`

---

## 🚫 Anti-Patterns (Don't Use)

❌ **Vague adjectives**: `applicable_`, `relevant_`, `related_`
❌ **Mixed tenses**: `produced_by_` + `produces_`
❌ **Unclear direction**: `target_` (ambiguous)
❌ **Gerunds**: `containing_` (use noun form instead)

---

## 🆕 Adding New Relationships

### Process

1. **Identify the action**: What is happening? (produces, removes, contains, etc.)
2. **Determine direction**: Is it source (from), location (on), agent (by), or purpose (for)?
3. **Choose verb form**: Active present or passive participle?
4. **Apply pattern**: `{action}_{direction}_{content_type}`

### Examples

**New relationship**: "This setting is designed for specific materials"
- Action: designed
- Direction: for (purpose)
- Form: adjective + for
- **Result**: `designed_for_materials`

**New relationship**: "This compound is extracted from materials"
- Action: extracted
- Direction: from (source)
- Form: passive + from
- **Result**: `extracted_from_materials`

**New relationship**: "This contaminant damages equipment"
- Action: damages
- Direction: (direct object, no preposition)
- Form: active present
- **Result**: `damages_equipment`

---

## 📖 Full Reference

See `docs/RELATIONSHIP_DATA_SPECIFICATION.md` for:
- Complete naming convention explanation
- Field reference table with patterns
- Examples from all domains
- Common mistakes to avoid

---

**Last Updated**: December 21, 2025
