# Text Accuracy System - Complete Documentation

## Overview
Comprehensive text spelling and accuracy system to ensure all visible text in historical images is correctly spelled and properly rendered.

## Question 1: Text Spelling Rigor ✅ ENHANCED

### Positive Prompt Addition
**File**: `regions/image/prompts/city_image_prompts.py`

Added critical text accuracy directive:
```
CRITICAL TEXT ACCURACY: All visible text on signs, storefronts, and buildings MUST be 
correctly spelled with proper letter formation. Each letter must be complete, properly 
proportioned, and clearly legible. Storefront signs must show accurate business names 
with correct spelling and authentic {decade} typography. All words must be real, 
correctly spelled English words appropriate to the era. No gibberish, no malformed 
letters, no missing letter parts, no backwards or upside-down text. Text rendering 
must be historically accurate with period-appropriate fonts and sign painting quality.
```

### Negative Prompts Enhancement
**File**: `regions/image/negative_prompts.py`

Expanded from **19 text accuracy items** to **90+ comprehensive text controls**:

#### Spelling Accuracy (New):
- misspelling, spelling errors, typos
- incorrect spelling, wrong spelling
- misspelled signs, misspelled words
- words spelled wrong, sign text with errors

#### Letter Formation (Expanded):
- malformed letters, deformed letters, distorted letters
- letters with missing parts, incomplete letters, partial letters
- fragmented letters, broken letter strokes, disconnected letter parts
- letters missing serifs, stems, bowls
- warped letters, melted letters, shattered letters
- asymmetric letters, lopsided letters

#### Text Coherence (New):
- gibberish text, nonsense words, fake words
- made-up words, invented words, non-existent words
- random characters, meaningless characters
- incoherent text, scrambled letters, jumbled text
- AI-garbled text, text generation errors

#### Typography Issues (New):
- letters too close together, letters too far apart
- incorrect letter spacing, wrong kerning
- words without spaces, missing spaces between words
- floating letter parts, detached letter segments
- text running together, letters merging incorrectly

#### Rendering Quality (New):
- badly rendered letters, poorly rendered typography
- text artifacts, corrupted signage text
- fake-looking text, artificial-looking letters
- text that looks computer-generated badly
- text with wrong characters

#### Placeholder Prevention (New):
- placeholder text, lorem ipsum, dummy text
- test text, sample text

## Question 2: Street Name Research ✅ CONFIRMED

### Research Process
**File**: `regions/image/prompts/population_researcher.py`

**YES** - A common local street IS retrieved and passed:

#### Research Query:
```python
prompt = f"""Research the historical context of {city_name}, {county_name}, California during the {decade}.

Provide:
1. The approximate population in the middle of the decade
2. The name of the main commercial street or downtown area during that era  # ← Street name
3. Specific details about that street in the {decade}                      # ← Street details
4. Brief character description of the city at that time

Format as JSON with:
- "main_street": "<street name, e.g., 'El Camino Real' or 'Main Street'>"
- "street_details": "<1-2 sentences about the street in {decade}>"
```

#### Data Retrieved:
```python
result = {
    "main_street": data.get("main_street", "downtown"),     # ← Street name
    "street_details": data.get("street_details", "")        # ← Street context
}
```

### Street Name Usage in Prompt
**File**: `regions/image/prompts/city_image_prompts.py`

#### Extraction:
```python
street_name = population_data.get("main_street", "downtown")
street_details = population_data.get("street_details", "")
street_context = f" Specifically {street_name}. {street_details}" if street_details else f" on {street_name}"
```

#### Prompt Injection:
```python
f"{actual_decade} California Bay Area {density} street scene in {city_name}, {county_name}.{street_context}"
```

### Example Output (San Francisco):
```
Research log:
📍 Main street: Market Street
📝 Details: Market Street was the main commercial thoroughfare with grand buildings, 
    streetcars, and major department stores like Emporium and The White House.

Prompt includes:
"1930s California Bay Area high urban density street scene in San Francisco, 
San Francisco County. Specifically Market Street. Market Street was the main 
commercial thoroughfare with grand buildings, streetcars, and major department 
stores like Emporium and The White House."
```

## Combined Effect

### Text Accuracy Flow:
1. **Research** retrieves actual street name (e.g., "El Camino Real", "Market Street")
2. **Prompt** emphasizes that street name with CRITICAL TEXT ACCURACY requirements
3. **Negative prompts** block 90+ ways text can be misspelled or malformed
4. **Result**: Street signs should show correct spelling with proper letter formation

### Quality Gates:
- ✅ Real street names from historical research
- ✅ Explicit "CRITICAL TEXT ACCURACY" directive in positive prompt
- ✅ 90+ negative prompts blocking spelling/rendering errors
- ✅ Era-appropriate typography requirements
- ✅ Letter formation and spacing controls
- ✅ Coherence and readability requirements

## Testing Recommendations

### High-Risk Streets (Should spell correctly):
- San Francisco → "Market Street"
- Belmont → "El Camino Real"
- Oakland → "Broadway"
- San Jose → "The Alameda"

### Validation Points:
1. **Spelling**: Are business names correctly spelled?
2. **Letter formation**: Are all letters complete and properly formed?
3. **Readability**: Is storefront text clearly legible?
4. **Authenticity**: Do signs look period-appropriate?
5. **Typography**: Are fonts consistent with the era?

## Impact Summary

**Before**: Basic text controls, 19 negative prompts
**After**: 
- Comprehensive 90+ text accuracy controls
- Explicit CRITICAL TEXT ACCURACY directive
- Real street names from research
- Multiple quality gates for text rendering

This creates the most rigorous text accuracy system possible within the Imagen API constraints.
