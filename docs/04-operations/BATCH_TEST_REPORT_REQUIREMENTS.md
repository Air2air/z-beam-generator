# Batch Test Report Requirements

**Last Updated**: November 16, 2025  
**Applies To**: All component types (caption, subtitle, FAQ, description, etc.)

---

## Report Format Specification

Batch test reports MUST include three sections in this order:

### 1. Immediate Alerts/Issues Section

**Purpose**: Surface critical problems at the top for quick triage  
**Location**: Before detailed results  
**Display**: Each material/component combination

#### Alert Criteria:
- 🚨 **GENERATION FAILED** - Component generation did not complete
- ⚠️  **LOW HUMAN SCORE** - Winston AI score < 70% human
- ⚠️  **SUBJECTIVE VALIDATION FAILED** - Excessive violations detected
- ✅ **NO ISSUES DETECTED** - All checks passed

#### Format:
```
🚨 ALERT: GENERATION FAILED
Error: [error message]

⚠️  ALERT: LOW HUMAN SCORE
Winston Score: 65.3% (threshold: 70%)

⚠️  ALERT: SUBJECTIVE VALIDATION FAILED
Violations: 8 (max: 6)

✅ NO ISSUES DETECTED
```

---

### 2. Subjective Evaluation (Above Each Text Item)

**Purpose**: Show quality metrics before displaying generated content  
**Location**: Immediately before the generated text  
**Display**: For each successful generation

#### Required Metrics:
1. **Validation Status**: PASS/FAIL with violation count
2. **Winston Score**: Human percentage (if available)
3. **Generation Time**: Elapsed seconds
4. **Violation Details**: (if applicable)
   - Category breakdown
   - Specific words/patterns
   - Comma count (if excessive)

#### Format:
```
📊 SUBJECTIVE EVALUATION:
----------------------------------------------------------------------
✅ PASS - No violations detected
Winston: 91.7% human
Generation Time: 16.2s

OR

❌ FAIL - 7 violations (HIGH severity)
  • conversational: now (2x), but (1x)
  • hedging: around (1x)
  • Excessive commas: 8 (AI pattern)
Winston: 45.2% human
Generation Time: 23.4s
```

---

### 3. Generated Text Item

**Purpose**: Display the actual generated content  
**Location**: After subjective evaluation  
**Display**: Full text as generated

#### Format:
```
📝 GENERATED [COMPONENT_TYPE]:
----------------------------------------------------------------------
[Generated content here - full text]
```

#### Component Type Labels:
- `GENERATED CAPTION` - For captions
- `GENERATED SUBTITLE` - For subtitles
- `GENERATED FAQ` - For FAQs
- `GENERATED DESCRIPTION` - For descriptions
- `GENERATED [TYPE]` - For any other component

---

## Terminal Output Example

```
======================================================================
Aluminum (Author 4)
======================================================================

✅ NO ISSUES DETECTED

📊 SUBJECTIVE EVALUATION:
----------------------------------------------------------------------
✅ PASS - No violations detected
Winston: 99.4% human
Generation Time: 28.1s

📝 GENERATED CAPTION:
----------------------------------------------------------------------
Aluminum powers cars and planes with its light weight, around 2.7 grams 
per cubic centimeter. But grime layers coat the surface, trapping oils 
and particles. At 1000x magnification, those contaminants sprawl like 
stubborn stains, blocking that smooth metallic gleam. Laser at 1064 
nanometer wavelength zaps it clean. Surface emerges bare and ready for 
aerospace use.
```

---

## Markdown Report Requirements

The generated markdown report (e.g., `BATCH_CAPTION_TEST_REPORT.md`) MUST include:

### Executive Summary
- Total materials tested
- Success/failure counts
- Average scores (Winston, subjective)
- Total credits/tokens used

### Quick Results Table
- Material name
- Status (✅ PASS / ❌ FAIL)
- Human %
- AI %
- Notes

### Detailed Reports
For each material:
1. Alert section (if issues)
2. Subjective evaluation metrics
3. Generated text (full content)
4. Performance metrics (time, tokens, credits)

### Recommendations
- Actionable next steps based on results
- Pattern identification
- System health assessment

---

## Implementation Requirements

### Data Extraction
Scripts MUST extract from generation output:
1. ✅ Success/failure status
2. ✅ Winston human score
3. ✅ Winston AI score
4. ✅ Generated text (from Materials.yaml or equivalent)
5. ✅ Subjective validation results
6. ✅ Violation details (count, categories, words)
7. ✅ Generation time (elapsed seconds)

### Report Generation
1. ✅ Display terminal output with 3 sections
2. ✅ Generate markdown file with comprehensive details
3. ✅ Overwrite static report file (e.g., `BATCH_[TYPE]_TEST_REPORT.md`)
4. ✅ Include timestamp in report header
5. ✅ Provide file location and size after generation

---

## Testing Requirements

### Unit Tests
Test files MUST verify:
1. ✅ Alert detection logic (failed generation, low scores, violations)
2. ✅ Text extraction from data files
3. ✅ Subjective evaluation parsing
4. ✅ Report formatting (terminal and markdown)

### Integration Tests
Batch test scripts MUST:
1. ✅ Test all 4 author personas
2. ✅ Extract and display generated text
3. ✅ Show subjective evaluation before text
4. ✅ Surface alerts/issues immediately
5. ✅ Generate markdown report
6. ✅ Complete within reasonable time (< 3 minutes for 4 materials)

---

## File Locations

### Scripts
- `scripts/batch_caption_test.py` - Caption batch test
- `scripts/batch_subtitle_test.py` - Subtitle batch test (future)
- `scripts/batch_faq_test.py` - FAQ batch test (future)

### Reports
- `BATCH_CAPTION_TEST_REPORT.md` - Caption batch report (static filename)
- `BATCH_SUBTITLE_TEST_REPORT.md` - Subtitle batch report (future)
- `BATCH_FAQ_TEST_REPORT.md` - FAQ batch report (future)

### Tests
- `tests/test_batch_report_format.py` - Report format validation
- `tests/test_batch_test_integration.py` - End-to-end batch test

---

## Command-Line Interface

### Run Batch Test
```bash
# Caption batch test
python3 run.py --batch-test

# Future: Component-specific batch tests
python3 run.py --batch-test --component caption
python3 run.py --batch-test --component subtitle
python3 run.py --batch-test --component faq
```

### Expected Output
1. ✅ Terminal progress (each material)
2. ✅ Detailed results (3-section format)
3. ✅ Summary statistics
4. ✅ Report file generation confirmation

---

## Quality Standards

### Alert Thresholds
- **Winston Human Score**: < 70% triggers LOW HUMAN SCORE alert
- **Subjective Violations**: > max threshold triggers VALIDATION FAILED alert
- **Generation Failure**: Any exception or non-zero exit code triggers FAILED alert

### Report Completeness
- ✅ All generated text must be captured and displayed
- ✅ All metrics must be extracted and reported
- ✅ Missing data must show warning (⚠️  Data not captured)
- ✅ Errors must be surfaced in alert section

### Performance Standards
- ✅ Batch test completes within 3 minutes (4 materials)
- ✅ Report generation < 1 second
- ✅ No hanging or timeout issues

---

## Maintenance Notes

### When Adding New Component Types
1. Create batch test script using this format
2. Update run.py with new command flag
3. Add tests for new component type
4. Document component-specific requirements

### When Modifying Report Format
1. Update this documentation first
2. Update all batch test scripts consistently
3. Update tests to match new format
4. Regenerate example reports

---

## References

- **Example Implementation**: `scripts/batch_caption_test.py`
- **Report Classes**: `processing/reports/generation_report.py`
- **Validation**: `processing/validation/subjective_validator.py`
- **Integration**: `run.py` (--batch-test command)
