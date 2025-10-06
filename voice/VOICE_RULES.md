# Voice System Rules

## Core Principles

### 1. No Signature Phrases or Emotives
**PROHIBITED:**
- ❌ Signature catchphrases ("systematic approach enables", "precision meets innovation")
- ❌ Emotional descriptors ("remarkable", "extraordinary", "magnificent", "beautiful")
- ❌ Subjective qualifiers ("truly", "really", "quite", "particularly")
- ❌ Personal excitement markers ("I'm pleased to report", "It's fascinating that")
- ❌ Brand voice catchphrases or marketing language

**REQUIRED:**
- ✅ Neutral, objective technical language
- ✅ Direct observation statements
- ✅ Factual descriptions without embellishment
- ✅ Professional restraint in vocabulary choices

**Example - WRONG:**
```
"What strikes one is the truly remarkable precision of this extraordinary technique, 
creating beautiful results that are quite exceptional."
```

**Example - CORRECT:**
```
"The technique achieves precision control of the contamination removal process 
while preserving substrate integrity."
```

### 2. Reflect Nationality Through Structure Only
**Linguistic authenticity comes from GRAMMAR and SYNTAX, not content references.**

#### Taiwan (Mandarin Influence)
**Structural Patterns:**
- Topic-comment construction: "This surface, it shows contamination"
- Article omission: "Surface shows improvement" (not "The surface")
- Implied subjects: "When measuring, shows 20 microns"
- Number-measurement order: "layer has thickness of 15 micrometers"
- "Very" as intensifier overuse: "very clear", "very important"
- Preposition variations: "depends of" vs "depends on"

**NOT:**
- ❌ References to Taiwan, Asia, or Chinese culture
- ❌ Mentions of systematic approaches as "Asian methodology"
- ❌ Cultural stereotypes or national characteristics

#### Italy (Italian Influence)
**Structural Patterns:**
- Word order inversion for emphasis: "Remarkable is this precision"
- Emphatic pronoun repetition: "The surface, she is clean"
- Infinitive without subject: "To achieve this, requires patience"
- Object fronting: "This method, it works well"
- Preposition from Italian: "different of" vs "different from"
- Article with abstractions: "the precision", "the quality"

**NOT:**
- ❌ References to Italy, Italian heritage, or Mediterranean culture
- ❌ Mentions of "la bella figura" or Italian values
- ❌ Cultural stereotypes about craftsmanship or aesthetics

#### Indonesia (Indonesian/Malay Influence)
**Structural Patterns:**
- Repetition for emphasis: "The quality, the quality is important"
- Simplified clause structure: shorter, more direct
- Direct cause-effect: "X happens, so Y occurs"
- Preposition simplification: "on" used broadly
- Progressive aspect less frequent: "process shows" vs "is showing"
- Reduced article complexity: more "zero article" constructions

**NOT:**
- ❌ References to Indonesia, Southeast Asia, or tropical contexts
- ❌ Mentions of renewable energy focus or environmental consciousness
- ❌ Cultural stereotypes about practicality or sustainability

#### USA (American English)
**Structural Patterns:**
- Direct, confident assertions without hedging
- Active voice preference: "The laser removes" vs "is removed by"
- Shorter sentences with less subordination
- Present perfect less common: "The process improved" vs "has improved"
- Phrasal verbs: "clean up", "break down", "set up"
- Efficiency-focused language: concrete, results-oriented

**NOT:**
- ❌ References to USA, America, or American innovation
- ❌ Mentions of business context, ROI, or market leadership
- ❌ Cultural stereotypes about optimism or entrepreneurship

### 3. No Nationality-Related References
**PROHIBITED:**
- ❌ Explicit country mentions ("In Taiwan, we approach this...")
- ❌ Cultural references ("Italian craftsmanship tradition...")
- ❌ National characteristics ("American innovation leads...")
- ❌ Geographic context ("Southeast Asian environmental concerns...")
- ❌ Heritage or tradition mentions tied to nationality
- ❌ Language references ("In Chinese, we say..." / "The Italian word for...")

**REQUIRED:**
- ✅ Pure technical focus on material and process
- ✅ Universal laser cleaning terminology
- ✅ Industry-standard descriptions
- ✅ Observable, measurable phenomena only
- ✅ Professional neutrality in all contexts

## Voice Profile Structure

### Required Elements
Each voice profile MUST contain ONLY:

1. **Grammatical Patterns**
   - Sentence structure variations from native language influence
   - Article usage patterns (presence/absence/choice)
   - Preposition variations from L1 transfer
   - Word order influenced by native syntax
   - Tense and aspect usage patterns
   - Clause complexity typical of the language background

2. **Vocabulary Constraints**
   - Technical term usage (standard industry terms only)
   - Connector preferences (but, however, therefore, etc.)
   - Hedging patterns (seems, appears, may, might)
   - Measurement description patterns
   - Abstraction level (concrete vs abstract language)

3. **Prosodic Elements**
   - Sentence length distribution
   - Comma usage and clause separation
   - Paragraph organization patterns
   - Information flow (given-new structure)
   - Emphasis through structure (not through adjectives)

### Prohibited Elements
Voice profiles MUST NOT contain:

1. **Signature Phrases**
   - No catchphrases or recurring expressions
   - No branded language or slogans
   - No personality markers in vocabulary
   - No emotional descriptors as identifying markers

2. **Cultural Content**
   - No cultural values statements
   - No heritage or tradition references
   - No national characteristic descriptions
   - No geographic context mentions
   - No cultural communication style descriptions beyond grammar

3. **Emotive Language**
   - No excitement markers
   - No aesthetic appreciation language
   - No subjective quality judgments
   - No personal engagement phrases
   - No rhetorical flourishes

## Implementation Guidelines

### For Profile Authors
When creating or updating voice profiles:

1. **Focus on Transfer Errors**
   - Identify common L1→L2 grammatical transfers
   - Document authentic non-native patterns
   - Avoid stereotypes; use linguistic research

2. **Eliminate Emotional Content**
   - Remove all "remarkable", "beautiful", "excellent" type words
   - Replace subjective with objective descriptions
   - Use neutral technical vocabulary only

3. **Remove Signature Phrases**
   - Delete phrase lists that create recognizable patterns
   - Avoid repeated expressions across content
   - Ensure variety through structure, not catchphrases

4. **Validate Authenticity**
   - Patterns must be linguistically documented
   - Avoid cultural stereotypes or assumptions
   - Test with native speakers if possible

### For Content Generators
When using voice profiles in generation:

1. **Apply Structural Rules**
   ```python
   # Extract grammatical patterns
   sentence_structure = profile['linguistic_characteristics']['sentence_structure']
   grammar_patterns = profile['linguistic_characteristics']['grammar_characteristics']
   
   # Apply to content WITHOUT adding signature phrases
   # Focus on: word order, articles, prepositions, clause structure
   ```

2. **Ignore Emotive Sections**
   ```python
   # SKIP these sections if they exist:
   # - signature_phrases
   # - cultural_values
   # - aesthetic_appreciation
   # - personal_engagement_markers
   ```

3. **Validate Output**
   - Check for unintended signature phrases
   - Verify no cultural references present
   - Confirm technical neutrality maintained
   - Ensure grammatical authenticity only

## Content Generation Rules

### Caption Generation
**Allowed:**
- Observable surface characteristics
- Measurable contamination layers (with specific values)
- Structural changes from laser treatment
- Technical process parameters
- Material property changes

**Prohibited:**
- Aesthetic judgments ("beautiful surface", "elegant solution")
- Emotional responses ("remarkable result", "impressive outcome")
- Cultural framing ("traditional approach", "innovative thinking")
- Personal observations ("one notices", "what strikes me")
- Subjective quality claims without measurement

**Structure Example (Taiwan - Mandarin Influence):**
```
Surface examination shows contamination layer, thickness measures 15-25 micrometers.
Layer composition indicates oxide formation, affects reflectivity by 35-40 percent.
After treatment, surface shows metallic substrate, roughness below 0.8 micrometers.
```
*Note: Article omission, measurement-first structure, direct statements*

**Structure Example (Italy - Italian Influence):**
```
The contamination layer, she shows thickness of 15-25 micrometers on the surface.
Oxide formation affects the reflectivity, reduces by approximately 35-40 percent.
After treatment shows the substrate, metallic surface with roughness below 0.8 micrometers.
```
*Note: Emphatic pronouns, word order inversion, article patterns*

### Technical Description
**Allowed:**
- Process parameters (wavelength, pulse duration, fluence)
- Material specifications (density, thermal conductivity, hardness)
- Measurement protocols and standards
- Equipment configurations
- Safety requirements

**Prohibited:**
- Process quality judgments ("excellent control", "superior results")
- Innovation claims ("cutting-edge", "breakthrough", "revolutionary")
- Efficiency emotives ("remarkably efficient", "surprisingly effective")
- Heritage references ("time-tested", "traditional wisdom", "proven excellence")

## Quality Assurance

### Review Checklist
Before publishing content, verify:

- [ ] No signature phrases present
- [ ] No emotive language (remarkable, beautiful, excellent, etc.)
- [ ] No cultural or national references
- [ ] Structural authenticity only (grammar, syntax, word order)
- [ ] Technical neutrality maintained
- [ ] Observable facts only, no subjective judgments
- [ ] Measurements specific and quantified
- [ ] Professional restraint in vocabulary

### Red Flags
Content needs revision if it contains:

- ⚠️ "Truly", "really", "quite", "particularly", "especially"
- ⚠️ "Remarkable", "extraordinary", "magnificent", "beautiful", "elegant"
- ⚠️ "One can see", "what strikes", "it is evident"
- ⚠️ References to cultural values or heritage
- ⚠️ National or geographic context mentions
- ⚠️ Repeated phrases across multiple pieces
- ⚠️ Aesthetic appreciation of technical results
- ⚠️ Personal engagement or rhetorical questions

## Rationale

### Why No Signature Phrases?
- Creates artificial, recognizable patterns
- Reduces authenticity and human variability
- Increases AI detection scores
- Sounds like branding, not genuine expertise
- Authentic writers vary their expression naturally

### Why Structure Over Content?
- Grammatical patterns are unconscious and persistent
- Vocabulary is conscious and variable
- Native language transfer shows in grammar, not word choice
- Structural patterns are linguistically authentic
- Content stereotypes are culturally reductive

### Why No Cultural References?
- Technical content is universal
- Cultural framing is condescending
- Professional context transcends nationality
- Expertise speaks through technical competence
- Cultural markers distract from technical substance

## Migration Guide

### Updating Existing Profiles

1. **Remove Emotive Vocabulary**
   ```yaml
   # BEFORE:
   preferred_terms:
     - "remarkable"
     - "truly exceptional"
     - "quite beautiful"
   
   # AFTER:
   preferred_terms:
     - "shows"
     - "indicates"
     - "demonstrates"
   ```

2. **Delete Signature Phrases**
   ```yaml
   # BEFORE:
   signature_phrases:
     - "precision meets innovation"
     - "systematic approach enables"
   
   # AFTER:
   # Remove entire signature_phrases section
   ```

3. **Eliminate Cultural References**
   ```yaml
   # BEFORE:
   cultural_values:
     - "Italian craftsmanship tradition"
     - "La bella figura in technical excellence"
   
   # AFTER:
   # Remove cultural_values section
   # Keep only grammatical patterns
   ```

4. **Focus on Grammar**
   ```yaml
   # KEEP and EXPAND:
   grammar_characteristics:
     noticeable_patterns:
       - "Word order inversion (Remarkable is this precision)"
       - "Emphatic pronouns (The surface, she is clean)"
       - "Article patterns (the precision, the quality)"
   ```

### Testing Updates

1. Generate sample content with updated profile
2. Check for signature phrases in output
3. Verify structural authenticity present
4. Confirm no cultural references
5. Validate technical neutrality
6. Compare against checklist above

## Examples

### ❌ WRONG - Violates All Rules
```
"What truly strikes one about this remarkable Italian approach is the beautiful 
precision achieved through systematic methodology. The laser technique demonstrates 
extraordinary elegance, creating magnificent results that reflect our heritage of 
technical excellence and craftsmanship tradition."
```
*Violations: Signature phrases, emotives, cultural references, personal engagement*

### ✅ CORRECT - Taiwan Structure
```
"Surface analysis shows contamination layer with thickness 15-25 micrometers. 
Layer composition indicates oxide formation. Treatment process removes contamination, 
surface roughness measures below 0.8 micrometers after cleaning."
```
*Features: Article omission, measurement-first, direct statements, no emotives*

### ✅ CORRECT - Italy Structure
```
"The contamination layer shows thickness of 15-25 micrometers. This composition, 
she indicates oxide formation on the surface. The treatment removes contamination, 
shows substrate with roughness below 0.8 micrometers."
```
*Features: Emphatic pronouns, word order variations, article patterns, no emotives*

### ✅ CORRECT - Indonesia Structure
```
"Contamination layer shows thickness 15-25 micrometers on surface. Oxide formation 
causes this condition. Treatment removes contamination, surface roughness becomes 
below 0.8 micrometers."
```
*Features: Simplified structure, direct causation, reduced articles, no emotives*

### ✅ CORRECT - USA Structure
```
"Analysis shows a 15-25 micrometer contamination layer. Oxide formation caused 
the buildup. Treatment removed the contamination and brought roughness down to 
0.8 micrometers."
```
*Features: Active voice, phrasal verbs, direct assertions, concrete language*

---

## Summary

**Three Rules:**
1. **No signature phrases or emotives** - Use neutral technical language only
2. **Reflect nationality through structure** - Grammar and syntax, not vocabulary
3. **No nationality-related references** - Pure technical focus, universal context

**Implementation:**
- Voice profiles contain ONLY grammatical patterns and structural tendencies
- Content generation applies structural rules WITHOUT adding personality markers
- Quality assurance removes all emotive language and cultural references

**Result:**
Authentic linguistic variation through unconscious grammatical patterns, not through 
conscious vocabulary choices or cultural content. Technical substance over personality.

---

**Last Updated:** 2025-10-04  
**Status:** Active voice system rules  
**Applies To:** All voice profiles and content generation
