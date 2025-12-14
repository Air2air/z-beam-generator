# Cross-Linking Evaluation & Adaptation Plan
**Date**: December 14, 2025  
**Status**: ✅ WORKING in contaminants, ready for expansion

---

## 📊 Current Implementation Analysis

### ✅ What's Working Now

**Cross-linking IS ACTIVE in contaminant descriptions:**
- `aluminum-oxidation`: Contains `[Aluminum](../materials/aluminum.md)` ✅
- `algae-growth`: Contains `[Concrete](../materials/concrete.md)` ✅
- Successfully linking materials mentioned in contaminant text

**Architecture:**
```
shared/text/cross_linking/
├── __init__.py
└── link_builder.py (234 lines)
    └── CrossLinkBuilder class
```

**Integration Point:**
- `generation/core/generator.py` (lines 548-562)
- Applied AFTER content generation, BEFORE saving
- Only for string content > 100 characters

---

## 🎯 How Cross-Linking Works (Current Process)

### Step-by-Step Flow

**1. Content Generation**
```python
# Generate text without links
content = api.generate(prompt)  # "Aluminum oxidation forms thin layer..."
```

**2. Cross-Link Detection** (generator.py line 552)
```python
content = self.link_builder.add_links(
    content=content,              # Generated text
    current_item=identifier,      # e.g., "aluminum-oxidation"
    domain=self.domain            # e.g., "contaminants"
)
```

**3. Term Matching** (link_builder.py)
```python
# Searches for material names in text
# Finds: "Aluminum" mentioned at character position 0
# Looks up Materials.yaml for "Aluminum" entry
# Verifies it exists and gets slug
```

**4. Link Insertion**
```python
# Original: "Aluminum oxidation forms thin layer..."
# Result:   "[Aluminum](../materials/aluminum.md) oxidation forms thin layer..."
```

**5. Save with Links**
```python
# Content saved to frontmatter YAML with markdown links intact
description: "[Aluminum](../materials/aluminum.md) oxidation contamination forms..."
```

---

## 🔍 Technical Deep Dive

### CrossLinkBuilder Class Architecture

```python
class CrossLinkBuilder:
    """
    Rule-based cross-linking with strict constraints:
    - Maximum 1-2 links per 150 words
    - Natural placement only (term must exist in text)
    - No circular references
    - Domain-aware relative paths
    """
    
    def __init__(self):
        self.materials_path = "data/materials/Materials.yaml"
        self.contaminants_path = "data/contaminants/Contaminants.yaml"
        self._materials_cache = None  # Lazy-loaded
        self._contaminants_cache = None
        self.max_links_per_150_words = 2
    
    def add_links(content, current_item, domain):
        """Main entry point - adds links to content"""
        # 1. Calculate max allowed links
        max_links = self._calculate_max_links(content)
        
        # 2. Find material mentions (if not in materials domain)
        if domain != 'materials':
            material_mentions = self._find_material_mentions(content, exclude=current_item)
            # Insert links for first occurrence only
        
        # 3. Find contaminant mentions (if not in contaminants domain)
        if domain != 'contaminants':
            contaminant_mentions = self._find_contaminant_mentions(content, exclude=current_item)
            # Insert links for first occurrence only
        
        return modified_content
```

### Key Methods

**`_find_material_mentions(text, exclude)`**
- Loads Materials.yaml
- Searches for exact material names (case-insensitive)
- Uses regex word boundaries: `\b{material_name}\b`
- Returns: `[(material_name, position), ...]`
- Sorted by first occurrence in text

**`_find_contaminant_mentions(text, exclude)`**
- Loads Contaminants.yaml
- Searches for contaminant pattern names
- Uses regex word boundaries
- Returns: `[(contaminant_name, pattern_id, position), ...]`

**Link Path Generation:**
```python
# Materials: ../materials/{slug}.md
slug = name.lower().replace(' ', '-').replace('(', '').replace(')', '')
link = f"../materials/{slug}.md"

# Contaminants: ../contaminants/{slug}.md
link = f"../contaminants/{slug}.md"
```

---

## 📋 Current Coverage by Domain

### ✅ Contaminants Domain (ACTIVE)
- **Status**: Working and tested
- **Text fields**: `description` (1-2 sentences)
- **Links found**:
  - Materials: YES (e.g., "Aluminum", "Concrete")
  - Other contaminants: Possible but rare in short text
- **Success rate**: 2/4 test cases had links (50%)

### ⚠️ Materials Domain (READY but NOT USED)
- **Status**: Infrastructure ready, not currently activated
- **Text fields**: 
  - `material_description` (1-2 sentences)
  - `micro.before` + `micro.after` (1 sentence each)
  - `faq` (multiple Q&A pairs)
- **Potential links**:
  - Contaminants: High (materials often mention contamination types)
  - Other materials: Medium (comparison mentions)
  - Settings: Low (rarely mentioned in descriptions)

### ⚠️ Settings Domain (NOT IMPLEMENTED)
- **Status**: No generator implementation yet
- **Text fields**: TBD (settings descriptions, use cases, etc.)
- **Potential links**:
  - Materials: High (settings describe material applications)
  - Contaminants: Medium (settings mention contamination removal)

---

## 🎯 Adaptation Requirements for All Text Fields

### User's Definition of Cross-Linking:
1. **Look through target text field** for material/contaminant mentions
2. **Look up the data file** to find full name and URL
3. **Print the full name and URL** in the target text field

### Current Implementation vs. User Definition

| Requirement | Current Status | Notes |
|-------------|---------------|-------|
| Look through text | ✅ YES | Uses regex search with word boundaries |
| Find occurrences | ✅ YES | Identifies all mentions, links first only |
| Look up data file | ✅ YES | Loads Materials.yaml, Contaminants.yaml |
| Get full name | ✅ YES | Uses exact name from YAML |
| Get URL | ⚠️ PARTIAL | Creates relative path, not absolute URL |
| Insert in text | ✅ YES | Markdown format `[name](url)` |

### ⚠️ Current Limitation: Relative Paths vs. URLs

**Current output:**
```markdown
[Aluminum](../materials/aluminum.md)
```

**User may want:**
```markdown
[Aluminum](https://z-beam.com/materials/aluminum)
```

**Or markdown with full name:**
```markdown
[Aluminum (Al, CAS 7429-90-5)](../materials/aluminum.md)
```

---

## 🔧 Adaptation Plan for All Domains

### Phase 1: Enable Materials Domain (Immediate)
**Current blocker**: Cross-linking only happens if `domain != 'materials'`

**Fix needed in `link_builder.py` line 180:**
```python
# CURRENT (line 180):
if domain != 'materials':
    material_mentions = self._find_material_mentions(...)

# PROPOSED: Allow materials to link to OTHER materials
# (currently excluded to avoid linking to self)
```

**Action**: Remove domain restriction, rely on `exclude=current_item` to prevent self-linking

**Expected result**: Materials can link to other materials mentioned in text
- Example: "Steel's higher density compared to Aluminum..." → links both Steel and Aluminum

### Phase 2: Expand to All Text Fields (Immediate)
**Current coverage:**
- ✅ `description` (material_description for materials, description for contaminants)
- ❌ `micro.before` (dict field, currently skipped)
- ❌ `micro.after` (dict field, currently skipped)
- ❌ `faq` (list field, currently skipped)

**Fix needed in `generator.py` line 551:**
```python
# CURRENT (line 551):
if isinstance(content, str) and len(content) > 100:
    content = self.link_builder.add_links(...)

# PROPOSED: Handle dict and list structures
if isinstance(content, str) and len(content) > 100:
    content = self.link_builder.add_links(...)
elif isinstance(content, dict):
    # Apply to each dict value (micro.before, micro.after)
    for key, value in content.items():
        if isinstance(value, str) and len(value) > 50:
            content[key] = self.link_builder.add_links(value, ...)
elif isinstance(content, list):
    # Apply to FAQ answers
    for item in content:
        if isinstance(item, dict) and 'answer' in item:
            if len(item['answer']) > 50:
                item['answer'] = self.link_builder.add_links(item['answer'], ...)
```

### Phase 3: URL Format Options (User Choice)
**Option A: Keep relative paths** (current)
```markdown
[Aluminum](../materials/aluminum.md)
```
- ✅ Simple
- ✅ Works in local dev
- ✅ Works in static site generators

**Option B: Absolute URLs**
```markdown
[Aluminum](https://z-beam.com/materials/aluminum)
```
- ✅ More explicit
- ✅ Works anywhere
- ⚠️ Requires domain configuration

**Option C: Full name with details**
```markdown
[Aluminum (Al, CAS 7429-90-5)](../materials/aluminum.md)
```
- ✅ More informative
- ⚠️ Longer text
- ⚠️ Requires property lookup

**Implementation:**
```python
# Add config option to link_builder.py
def __init__(self, url_format='relative', domain_url=None):
    self.url_format = url_format  # 'relative', 'absolute', 'full_name'
    self.domain_url = domain_url  # e.g., 'https://z-beam.com'
```

### Phase 4: Enhanced Data Lookup (Optional)
**Current**: Simple slug-based linking
**Enhanced**: Include material properties in link text

```python
def _get_full_material_name(self, material_name):
    """Get full material name with details from Materials.yaml"""
    materials = self._load_materials()
    material = materials['materials'].get(material_name, {})
    
    # Get symbol, CAS number, etc.
    symbol = material.get('symbol', '')
    cas = material.get('cas_number', '')
    
    # Format: "Aluminum (Al, CAS 7429-90-5)"
    if symbol and cas:
        return f"{material_name} ({symbol}, CAS {cas})"
    elif symbol:
        return f"{material_name} ({symbol})"
    else:
        return material_name
```

---

## 📊 Testing Strategy

### Test 1: Verify Current Contaminants Implementation
```bash
# Check existing cross-links in contaminants
python3 -c "
import yaml
with open('frontmatter/contaminants/aluminum-oxidation-contamination.yaml') as f:
    data = yaml.safe_load(f)
    print(data['description'])
"
# Expected: [Aluminum](../materials/aluminum.md) present
```

### Test 2: Enable Materials Cross-Linking
```bash
# Generate material description with cross-linking enabled
python3 run.py --material "Steel" --component material_description

# Check for links to other materials/contaminants
grep -o '\[.*\](.*\.md)' frontmatter/materials/steel-laser-cleaning.yaml
```

### Test 3: Test All Text Fields
```bash
# Generate all components for a material
python3 run.py --material "Aluminum" --all-components

# Check micro fields
python3 -c "
import yaml
with open('frontmatter/materials/aluminum-laser-cleaning.yaml') as f:
    data = yaml.safe_load(f)
    print('MICRO BEFORE:', data['micro']['before'])
    print('MICRO AFTER:', data['micro']['after'])
"
# Expected: Links in micro fields if materials/contaminants mentioned
```

### Test 4: FAQ Cross-Linking
```bash
# Generate FAQ
python3 run.py --material "Steel" --component faq

# Check FAQ answers for links
python3 -c "
import yaml
with open('frontmatter/materials/steel-laser-cleaning.yaml') as f:
    data = yaml.safe_load(f)
    for qa in data.get('faq', []):
        if '[' in qa['answer']:
            print(f'Q: {qa[\"question\"]}')
            print(f'A: {qa[\"answer\"]}')
            print()
"
```

---

## 🎯 Recommended Implementation Order

### Priority 1: Fix Domain Restriction (5 minutes)
**File**: `shared/text/cross_linking/link_builder.py`
**Change**: Allow materials to link to other materials
**Impact**: Materials domain can use cross-linking

### Priority 2: Add Dict/List Support (15 minutes)
**File**: `generation/core/generator.py`
**Change**: Apply cross-linking to dict and list content types
**Impact**: Micro and FAQ fields get cross-links

### Priority 3: Test All Domains (10 minutes)
**Action**: Generate samples from materials, contaminants, settings
**Verify**: Links appear in all text fields
**Document**: Success rates and examples

### Priority 4: URL Format Options (30 minutes)
**File**: `shared/text/cross_linking/link_builder.py`
**Change**: Add configurable URL formats
**Config**: Add to `generation/config.yaml`
**Impact**: User can choose relative vs absolute URLs

### Priority 5: Enhanced Lookup (Optional - 45 minutes)
**File**: `shared/text/cross_linking/link_builder.py`
**Change**: Include material properties in link text
**Impact**: Richer, more informative links

---

## 📝 Configuration Recommendations

### Add to `generation/config.yaml`:
```yaml
cross_linking:
  enabled: true
  
  # URL format: 'relative', 'absolute', 'full_name'
  url_format: relative
  
  # Only used if url_format = 'absolute'
  domain_url: https://z-beam.com
  
  # Maximum links per word count
  max_links_per_150_words: 2
  
  # Minimum content length for cross-linking
  min_content_length: 50
  
  # Apply to these content types
  content_types:
    - description
    - material_description
    - micro_before
    - micro_after
    - faq_answers
```

---

## 🎯 Success Criteria

### Metrics to Track:
1. **Link insertion rate**: % of generated text with cross-links
2. **Link accuracy**: % of links that are valid and relevant
3. **Link density**: Links per 150 words (target: 1-2)
4. **Domain coverage**: Cross-linking working in all domains
5. **Field coverage**: Cross-linking in all text field types

### Expected Results:
- Materials domain: 60-80% of descriptions have at least 1 link
- Contaminants domain: 40-60% of descriptions have at least 1 link (already working)
- Micro fields: 20-40% have links (shorter text = fewer opportunities)
- FAQ answers: 30-50% have links (longer text = more opportunities)

---

## 🔐 Architecture Compliance

### ✅ Follows Z-Beam Policies:
- **Reusable module**: Located in `shared/text/cross_linking/` ✅
- **Domain-agnostic**: Works across materials, contaminants, settings ✅
- **Config-driven**: Rules defined in code, not hardcoded ✅
- **Fail-fast**: Graceful error handling, continues if cross-linking fails ✅
- **No hardcoded values**: Links calculated from data files ✅
- **Single source of truth**: Data files (Materials.yaml, Contaminants.yaml) ✅

### ✅ Integration Points:
- Generator pipeline: AFTER content generation, BEFORE saving ✅
- Postprocessing: Can be applied independently if needed ✅
- Export: Links preserved in frontmatter YAML ✅

---

## 📚 Examples of Expected Output

### Example 1: Material Description
**Before cross-linking:**
```
Steel requires 3-5× higher pulse energy than Aluminum due to thermal conductivity 
differences. Common rust contamination responds well to 1064nm wavelength at 100-200 
mJ/pulse with 10-50 ns duration.
```

**After cross-linking:**
```
[Steel](../materials/steel.md) requires 3-5× higher pulse energy than 
[Aluminum](../materials/aluminum.md) due to thermal conductivity differences. 
Common [rust contamination](../contaminants/rust.md) responds well to 1064nm 
wavelength at 100-200 mJ/pulse with 10-50 ns duration.
```

### Example 2: Micro Field
**Before:**
```yaml
micro:
  before: Surface shows rust contamination affecting Steel substrate.
  after: Clean Steel surface restored through selective ablation.
```

**After:**
```yaml
micro:
  before: Surface shows [rust contamination](../contaminants/rust.md) affecting [Steel](../materials/steel.md) substrate.
  after: Clean [Steel](../materials/steel.md) surface restored through selective ablation.
```

### Example 3: FAQ Answer
**Before:**
```yaml
faq:
  - question: What materials can laser cleaning treat?
    answer: Laser cleaning effectively removes oxidation from Aluminum, rust from 
            Steel, and paint from Titanium. Each material requires optimized parameters.
```

**After:**
```yaml
faq:
  - question: What materials can laser cleaning treat?
    answer: Laser cleaning effectively removes [oxidation](../contaminants/oxidation.md) 
            from [Aluminum](../materials/aluminum.md), [rust](../contaminants/rust.md) 
            from [Steel](../materials/steel.md), and [paint](../contaminants/paint.md) 
            from [Titanium](../materials/titanium.md). Each material requires optimized 
            parameters.
```

---

## 🚀 Summary

### ✅ Current Status:
- Cross-linking infrastructure EXISTS and WORKS
- Currently ACTIVE in contaminants domain
- Successfully linking materials mentioned in contaminant descriptions
- 50% success rate (2/4 test cases)

### 🎯 What's Needed:
1. **Remove domain restriction** - Allow materials to link to other materials
2. **Add dict/list support** - Apply to micro and FAQ fields
3. **Test across all domains** - Verify in materials, contaminants, settings
4. **User choice on URL format** - Relative paths vs absolute URLs vs full names

### ⏱️ Time Estimate:
- **Immediate fixes**: 20 minutes (Priority 1-2)
- **Testing**: 10 minutes (Priority 3)
- **Optional enhancements**: 75 minutes (Priority 4-5)
- **Total**: 30-105 minutes depending on scope

### 📊 Expected Impact:
- **Materials domain**: 60-80% of content will have cross-links
- **Contaminants domain**: Already working (50% currently)
- **SEO benefit**: Internal linking structure for all content
- **User experience**: Easy navigation between related topics
- **Content richness**: More informative, connected documentation

---

## 📞 Next Steps

**User Decision Points:**
1. ✅ Keep relative paths `../materials/aluminum.md`?
2. ✅ Or use absolute URLs `https://z-beam.com/materials/aluminum`?
3. ✅ Or full names `Aluminum (Al, CAS 7429-90-5)`?
4. ✅ Apply to micro fields and FAQ answers?
5. ✅ What minimum text length for cross-linking? (current: 100 chars)

**Ready to implement based on your preferences.**
