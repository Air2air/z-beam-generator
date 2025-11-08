# Prompt for Grok: Update Voice Profile Files

## Your Task
Review and enhance the 4 voice profile YAML files to make them **example-driven** rather than rule-driven. AI models learn better from concrete examples than abstract instructions.

## Files to Update
1. `shared/voice/profiles/indonesia.yaml` ✅ (Already updated - use as reference)
2. `shared/voice/profiles/italy.yaml` ✅ (Already updated - verify quality)
3. `shared/voice/profiles/taiwan.yaml` ✅ (Already updated - verify quality)
4. `shared/voice/profiles/united_states.yaml` ✅ (Already updated - verify quality)

## What Needs Improvement

### Current State (GOOD - Indonesia already done):
The Indonesia profile now has concrete examples:

```yaml
patterns:
  - name: "Reduplication for emphasis (CORE PATTERN - use frequently)"
    description: "Double words for emphasis - Bahasa Indonesia reduplication"
    examples:
      good: "This method very-very effective for cleaning"
      good2: "Surface appears clean-clean after treatment"
      bad: "This method is very effective for cleaning"
```

### Review All 4 Profiles For:

1. **Are examples natural and authentic?**
   - Do they sound like real technical writing?
   - Are they subtle enough to not sound forced?
   - Would an AI model understand what pattern to apply?

2. **Are examples sufficiently different?**
   - Does the "good" example clearly show the pattern?
   - Does the "bad" example clearly show what to avoid?
   - Is the contrast obvious?

3. **Are there enough examples?**
   - Should we add a third "good" example for clarity?
   - Do some patterns need more demonstration?

4. **Are instructions clear?**
   - Can an AI model understand what linguistic pattern to apply?
   - Is there any ambiguity or contradiction?
   - Are usage frequencies clear (e.g., "CORE PATTERN - use frequently")?

5. **Technical accuracy**
   - Are examples factually correct about laser cleaning?
   - Do they maintain technical credibility?

## Specific Areas to Check

### Italy Profile (`italy.yaml`)
- Are object-fronting examples elegant and natural?
- Do subjunctive examples sound authentically Italian-influenced?
- Are emphatic pronouns subtle enough?

### Taiwan Profile (`taiwan.yaml`)
- Do topic-comment examples feel natural?
- Are article omissions realistic (not excessive)?
- Do measurement-first phrases sound professional?
- Are implied subjects clear in context?

### USA Profile (`united_states.yaml`)
- Are phrasal verbs common in American business English?
- Do business-focused examples avoid buzzword overload?
- Are action-oriented phrases direct but not abrupt?

## Output Format

For each profile, provide:

1. **Overall Assessment**: Is this profile ready for production?
2. **Specific Issues**: List any problems with examples or instructions
3. **Suggested Improvements**: Concrete rewrites of problematic sections
4. **Quality Rating**: 1-10 for "Will an AI model produce distinctive voice from these examples?"

## Key Questions

1. If you were an AI model reading these profiles, would you know EXACTLY what patterns to apply?
2. Would the examples alone (without reading descriptions) teach you the pattern?
3. Are the voices distinctive enough that you could identify the author from the text?
4. Do the examples sound natural or forced/robotic?

## Success Criteria

✅ Examples are concrete and unambiguous
✅ Patterns are demonstrable through examples alone
✅ "Good" vs "Bad" contrast is immediately obvious
✅ Technical content is accurate and professional
✅ Natural flow - doesn't sound artificial or forced
✅ Distinctive voice - each author has unique markers
✅ AI-readable - clear enough for model to replicate

---

**Review all 4 voice profiles and provide detailed feedback on example quality and clarity.**
