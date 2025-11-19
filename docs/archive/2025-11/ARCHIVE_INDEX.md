# Archive Index - November 2025

## Batch Generation Implementation (Nov 18-19, 2025)

**Location**: `docs/archive/2025-11/batch-generation-nov19/`

### Summary
Implementation of multi-material batch generation system to meet Winston AI's 300-character minimum requirement efficiently, achieving 75% cost savings.

### Key Documents (18 files)
- **LEARNED_EVALUATION_INTEGRATION_NOV18_2025.md** - Learned evaluation pipeline with template-based prompts
- **PROCESSING_REUSABILITY_COMPLETE_NOV18_2025.md** - Generic processing module architecture
- **REALISM_GATE_IMPLEMENTATION_NOV18_2025.md** - Realism scoring as quality gate (7.0/10 minimum)
- **REALISM_INTEGRATION_NOV18_2025.md** - Realism optimizer and feedback integration
- **SYSTEM_COMPLIANCE_AND_SWEET_SPOT_FLOW_NOV18_2025.md** - Composite scoring and parameter optimization
- **COMPONENT_SPECIFIC_CODE_VIOLATIONS_NOV18_2025.md** - Prompt purity policy enforcement
- **POLICY_UPDATES_NOV18_2025.md** - Template-only policy and prompt normalization
- **REORGANIZATION_COMPLETE_NOV19_2025.md** - Final system reorganization and batch generation

### Implementation Details

**Batch Generator** (`generation/core/batch_generator.py`)
- Multi-material batch operations (2-5 materials per batch)
- Component eligibility: subtitles (YES), captions (NO - already meet minimum)
- Batch prompt building with `[MATERIAL: Name]` markers
- Winston validation on concatenated text (meets 300-char minimum)
- Individual extraction using regex
- Cost savings: $13.20 → $3.30 (75% reduction)

**Commands Added**
```bash
python3 run.py --batch-subtitle "Material1,Material2,..."
python3 run.py --batch-subtitle --all
python3 run.py --batch-caption "..." # Falls back to individual
```

**Architecture Compliance**
- ✅ Zero hardcoded prompts (Prompt Purity Policy)
- ✅ Template-only content instructions
- ✅ Fail-fast on missing templates
- ✅ No production mocks/fallbacks

### Related Commits
- `9297b714` - Phase 3: Refactor generation loop (stage separation)
- `c179ddab` - Implement batch component generation for Winston 300-char minimum

### Final Status
- Grade: A+ (100/100) - Production-ready
- Quality: Caption 8.0/10, Subtitle 7.0/10, FAQ 8.0/10
- Tests: 487 tests collected, 139 test files
- Prompt Normalization: 98% (production), 87% (including scripts)

---

## Test Results Archive (Nov 15-18, 2025)

**Location**: `docs/archive/2025-11/test-results/`

### Files
- `BATCH_CAPTION_TEST_REPORT.md` - Batch caption testing results
- `batch_test*.log` - Test execution logs
- `batch_test_results.txt` - Summary results
- `E2E_EVALUATION_POST_SELF_LEARNING.txt` - End-to-end evaluation
- `E2E_EVALUATION_REPORT.json` - Structured evaluation data

### Summary
Comprehensive testing of batch generation, learning systems, and quality scoring across multiple materials and component types.

---

## Archive Maintenance

**Created**: November 19, 2025  
**Last Updated**: November 19, 2025  
**Archived By**: Automated cleanup process  
**Retention**: Permanent (reference documentation)
