# Troubleshooting Guide

**Quick solutions to common Z-Beam Generator issues**

---

## 🔥 Critical Issues

### Generation Fails Completely

**Symptoms**: `python3 run.py --caption "Material"` exits with error

**Diagnosis**:
```bash
# Check integrity
python3 run.py --integrity-check

# Test APIs
python3 run.py --test-api
```

**Solutions**:
1. Verify API keys in `.env`
2. Check material exists in `data/materials/Materials.yaml`
3. Review terminal output for specific error
4. Check `docs/api/ERROR_HANDLING.md` for API-specific issues

---

## 🔌 API Connection Issues

### Winston.ai SSL Errors

**Error**: `SSL: CERTIFICATE_VERIFY_FAILED` or connection refused

**Solution**: ✅ **FIXED** - System now uses `https://api.gowinston.ai`

If still failing:
```bash
# Test Winston connection
python3 scripts/tools/api_terminal_diagnostics.py winston

# Check API key
grep WINSTON_API_KEY .env
```

### DeepSeek/Grok Timeouts

**Error**: Request timeout or rate limit exceeded

**Solution**:
1. Check rate limits in API dashboard
2. Reduce batch size
3. Add delays between requests:
   ```python
   import time
   time.sleep(1)  # Add to batch loops
   ```

### API Key Not Found

**Error**: `API key not configured for [provider]`

**Solution**:
```bash
# Verify .env file exists
ls -la .env

# Check keys are set
cat .env | grep API_KEY

# Copy from example if needed
cp .env.example .env
# Then edit with your keys
```

---

## 📊 Data Issues

### Material Not Found

**Error**: `Material 'XYZ' not found in Materials.yaml`

**Solution**:
```bash
# List all materials
python3 -c "
import yaml
with open('data/materials/Materials.yaml') as f:
    materials = yaml.safe_load(f)
    print('\n'.join(materials.keys()))
"

# Check exact spelling (case-sensitive)
```

### Property Values Missing

**Error**: Null or missing property values

**Solution**:
```bash
# Check data completeness
python3 run.py --data-completeness-report

# View data gaps
python3 run.py --data-gaps

# Research missing properties
python3 run.py --research-property "thermal_conductivity" "Aluminum"
```

### Range Validation Fails

**Error**: Value outside allowed range

**Solution**:
1. Check `data/materials/Categories.yaml` for category ranges
2. Verify material-specific ranges in `Materials.yaml`
3. See `docs/05-data/data-architecture.md` for range propagation logic

---

## 🎯 Quality Issues

### Low Winston.ai Scores

**Symptoms**: Human score < 45%, generation marked as failed

**Diagnosis**:
```bash
# Check recent scores
sqlite3 data/winston_feedback.db "
SELECT material, component_type, human_score, ai_score 
FROM detection_results 
ORDER BY timestamp DESC 
LIMIT 10
"
```

**Solutions**:
1. Adjust voice parameters in `processing/config.yaml`
2. Check banned patterns in `processing/parameters/presets/structural_predictability.yaml`
3. Review sweet spot recommendations:
   ```bash
   sqlite3 data/winston_feedback.db "
   SELECT * FROM sweet_spot_recommendations
   WHERE material = 'YourMaterial'
   "
   ```

### Repetitive Content

**Symptoms**: Similar openings, patterns across generations

**Solution**: See `docs/prompts/OPENING_VARIATION_SYSTEM.md`

Check banned patterns:
```bash
grep -A 10 "banned_patterns:" processing/parameters/presets/structural_predictability.yaml
```

### Subjective Evaluation Fails

**Error**: `CachedAPIClient.generate() got unexpected keyword argument`

**Solution**: ✅ **FIXED** - System now uses `GenerationRequest` object

If still failing, see `docs/api/SUBJECTIVE_EVALUATION_API_FIX.md`

---

## 🧪 Testing Issues

### Tests Fail

**Error**: pytest failures

**Diagnosis**:
```bash
# Run specific test
pytest tests/test_specific.py -v

# Check test output
pytest tests/ -v --tb=short
```

**Common Fixes**:
1. Missing dependencies: `pip install -r requirements.txt`
2. API keys not set for tests
3. Database not initialized: `python3 run.py --caption "Aluminum"` (creates DB)

### Integrity Check Failures

**Error**: Integrity check reports FAIL status

**Solution**:
```bash
# Run full integrity check
python3 run.py --integrity-check

# Check specific issue from output
# Example: Database not found
ls -lh data/winston_feedback.db
```

Fix patterns:
- **Database missing**: Generate any content to create it
- **Config invalid**: Check `processing/config.yaml` syntax
- **Hardcoded values**: See violation details, fix in code

---

## 💾 Performance Issues

### Slow Generation

**Symptoms**: Takes > 60 seconds per component

**Solutions**:
1. Check API response times:
   ```bash
   python3 scripts/tools/api_terminal_diagnostics.py deepseek
   ```
2. Reduce max_tokens in `processing/config.yaml`
3. Use faster API provider (DeepSeek is fastest)

### Memory Issues

**Symptoms**: Out of memory errors

**Solutions**:
1. Clear cache: `rm -rf .cache/`
2. Reduce batch size
3. Run generations serially, not in parallel

---

## 🗂️ File System Issues

### Permission Denied

**Error**: Cannot write to `frontmatter/` or `data/`

**Solution**:
```bash
# Fix permissions
chmod -R u+w frontmatter/ data/

# Check ownership
ls -la frontmatter/ data/
```

### Disk Space

**Error**: No space left on device

**Solution**:
```bash
# Check space
df -h

# Clean Python cache
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# Clean old logs
rm -f batch_test_output.log
```

---

## 🔄 Generation Workflow Issues

### Post-Generation Checks Fail

**Symptoms**: Warnings after generation completes

**Check**: `docs/system/POST_GENERATION_INTEGRITY.md`

Common warnings:
- **Parameters not logged**: Database write failed
- **Sweet spot not updated**: < 5 samples needed
- **Subjective eval fallback**: Grok API unavailable

**Solutions**: Most warnings are informational, check specific message

### Frontmatter Export Incomplete

**Symptoms**: Missing fields in YAML output

**Solution**:
1. Check source data in `Materials.yaml`
2. Verify exporter logic in `components/frontmatter/core/trivial_exporter.py`
3. See `docs/05-data/DATA_STORAGE_POLICY.md`

---

## 🆘 Emergency Recovery

### System Won't Start

```bash
# 1. Check Python version
python3 --version  # Must be 3.12+

# 2. Reinstall dependencies
pip install -r requirements.txt

# 3. Verify environment
python3 run.py --check-env

# 4. Check git status
git status
git diff  # See what changed
```

### Reset to Clean State

```bash
# ⚠️ WARNING: This deletes all generated content

# Backup first
cp -r frontmatter/ frontmatter_backup/
cp data/winston_feedback.db data/winston_feedback.db.bak

# Clean slate
rm -rf frontmatter/materials/*.yaml
rm -rf frontmatter/settings/*.yaml
rm -f data/winston_feedback.db

# Regenerate
python3 run.py --material "Aluminum" --deploy
```

---

## 📞 Get More Help

### Documentation
- **Quick Reference**: `docs/QUICK_REFERENCE.md`
- **API Errors**: `docs/api/ERROR_HANDLING.md`
- **Full Index**: `docs/INDEX.md`

### Diagnostic Tools
```bash
# API diagnostics
python3 scripts/tools/api_terminal_diagnostics.py [provider]

# Data completeness
python3 run.py --data-completeness-report

# System health
python3 run.py --integrity-check
```

### Common Command Patterns
```bash
# Test before generating
python3 run.py --test-api && python3 run.py --caption "Material"

# Full diagnostic run
python3 run.py --integrity-check && \
python3 run.py --data-completeness-report && \
python3 run.py --caption "Aluminum"
```

---

**Last Updated**: November 16, 2025  
**Version**: 2.0  
**Coverage**: Common issues from 6 months production use
