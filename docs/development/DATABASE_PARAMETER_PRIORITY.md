# Database Parameter Priority System

**Status**: ✅ OPERATIONAL  
**Date**: November 15, 2025  
**Policy**: Database is PRIMARY source for all generation parameters

---

## 🎯 Core Principle

**ALL generation parameters MUST come from the database as the primary source.**

Configuration files (`processing/config.yaml`) should contain ONLY:
- Word count targets and ranges
- Static infrastructure settings (paths, file locations)
- Non-generation parameters

---

## 📊 Parameter Sources

### Priority Order (MANDATORY)

```
1. DATABASE (Primary - Always checked first)
   ↓
   Query: generation_parameters table
   Filters: material + component_type + success=1 + human_score>=20
   Order: human_score DESC
   Returns: temperature, frequency_penalty, presence_penalty, voice_params, enrichment_params

2. CALCULATED FALLBACK (Only when NO database history)
   ↓
   Warning: "⚠️  No database history for X Y - calculating from scratch"
   Source: dynamic_config.py methods
   Usage: First generation only, then saved to database
```

---

## 🚫 What Should NOT Be in Config

### Removed from config.yaml
- ❌ `generation_temperature` - Now in database
- ❌ `max_tokens` - Calculated dynamically
- ❌ `frequency_penalty` - Now in database
- ❌ `presence_penalty` - Now in database
- ❌ API generation parameters - All in database

### What SHOULD Remain in Config
- ✅ `min_words_before`, `max_words_before` - Word count targets
- ✅ `min_words_after`, `max_words_after` - Word count ranges
- ✅ `word_count_tolerance` - Acceptable variance
- ✅ `default` - Default word count
- ✅ File paths and infrastructure settings

---

## 🔄 Complete Data Flow

### First Generation (No History)
```
User Request: python3 run.py --caption "NewMaterial"
↓
1. Query Database
   SELECT * FROM generation_parameters 
   WHERE material='NewMaterial' AND component_type='caption'
   RESULT: None (no history)
   
2. Log Warning
   ⚠️  No database history for NewMaterial caption - calculating from scratch
   
3. Calculate Fallback
   temperature = dynamic_config.calculate_temperature('caption')
   frequency_penalty = dynamic_config.calculate_penalties()
   presence_penalty = dynamic_config.calculate_penalties()
   voice_params = dynamic_config.calculate_voice_parameters()
   enrichment_params = dynamic_config.calculate_enrichment_params()
   
4. Generate Content
   API call with calculated parameters
   
5. Save to Database
   INSERT INTO generation_parameters (
     material='NewMaterial',
     component_type='caption',
     temperature=0.95,
     frequency_penalty=0.45,
     presence_penalty=0.45,
     voice_params='{"imperfection_tolerance": 0.8}',
     enrichment_params='{"technical_intensity": 2}',
     detection_result_id=<link to Winston result>
   )
   ✅ Saved for next generation
```

### Second+ Generation (With History)
```
User Request: python3 run.py --caption "NewMaterial"
↓
1. Query Database
   SELECT * FROM generation_parameters p
   JOIN detection_results r ON p.detection_result_id = r.id
   WHERE p.material='NewMaterial' 
     AND p.component_type='caption'
     AND r.success=1
     AND r.human_score>=20
   ORDER BY r.human_score DESC
   LIMIT 1
   
   RESULT: {
     temperature: 0.95,
     frequency_penalty: 0.45,
     presence_penalty: 0.45,
     voice_params: {"imperfection_tolerance": 0.8},
     enrichment_params: {"technical_intensity": 2},
     human_score: 67.3
   }
   
2. Log Reuse
   ✓ Reusing proven successful parameters (human_score=67.3%):
      • temperature=0.950 (was 0.628)
      • frequency_penalty=0.450 (was 0.000)
      • presence_penalty=0.450 (was 0.000)
   
3. Apply Database Parameters
   All parameters copied from database record
   
4. Generate Content
   API call with database parameters
   
5. Update Database
   INSERT new record if better results achieved
```

### Retry Attempts
```
Attempt 1: Use database parameters (if available)
Attempt 2: Start with database parameters + adaptive adjustments
Attempt 3: Start with database parameters + more aggressive adjustments

Log: "🔄 Retry 2: Starting with DB params (temp=0.950, score=67.3%)"
```

---

## 💻 Implementation

### Code Location
- **File**: `processing/unified_orchestrator.py`
- **Method**: `_get_adaptive_parameters()`
- **Lines**: 676-779

### Key Logic
```python
def _get_adaptive_parameters(
    self,
    identifier: str,
    component_type: str,
    attempt: int = 1,
    last_winston_result: Optional[Dict] = None
) -> Dict[str, Any]:
    """Get generation parameters with database-first priority."""
    
    # MANDATORY: Always try database first
    previous_params = self._get_best_previous_parameters(identifier, component_type)
    
    if previous_params:
        # Found in database - use these
        if attempt == 1:
            # First attempt: Apply DB params with logging
            return self._apply_database_params(previous_params)
        else:
            # Retry: Start with DB + adjustments
            return self._apply_database_params_with_adjustments(previous_params)
    else:
        # No history - calculate fallback
        self.logger.warning(
            f"⚠️  No database history for {identifier} {component_type} "
            f"- calculating from scratch"
        )
        return self._calculate_fallback_params(component_type)
```

### Schema Validation
```python
def _validate_parameter_schema(self, params: Dict[str, Any]) -> bool:
    """Validate database parameters before use."""
    required = ['temperature', 'frequency_penalty', 'presence_penalty']
    
    # Check all required fields exist
    if not all(key in params for key in required):
        return False
    
    # Validate ranges
    if not (0.0 <= params['temperature'] <= 2.0):
        return False
    if not (-2.0 <= params['frequency_penalty'] <= 2.0):
        return False
    if not (-2.0 <= params['presence_penalty'] <= 2.0):
        return False
    
    return True
```

---

## 🧪 Testing

### Test Cases

#### Test 1: Config Contains Only Word Counts
```python
def test_config_contains_only_word_counts():
    config = yaml.safe_load(open('processing/config.yaml'))
    caption_config = config['component_lengths']['caption']
    
    # Should only have word-related keys
    allowed_keys = ['default', 'min_words_before', 'max_words_before',
                    'min_words_after', 'max_words_after', 'word_count_tolerance']
    
    for key in caption_config.keys():
        assert key in allowed_keys, f"Non-word-count key found: {key}"
    
    # Should NOT have generation params
    assert 'generation_temperature' not in caption_config
    assert 'max_tokens' not in caption_config
```

#### Test 2: Database Queried First
```python
def test_database_queried_first():
    orchestrator = UnifiedOrchestrator(api_client=api_client)
    
    # Mock database to track calls
    with patch.object(orchestrator, '_get_best_previous_parameters') as mock_db:
        mock_db.return_value = None
        
        params = orchestrator._get_adaptive_parameters('TestMaterial', 'caption', attempt=1)
        
        # Verify database was called FIRST
        mock_db.assert_called_once_with('TestMaterial', 'caption')
```

#### Test 3: Fallback Only When No History
```python
def test_fallback_only_when_no_history():
    orchestrator = UnifiedOrchestrator(api_client=api_client)
    
    # Clear any existing history
    with patch.object(orchestrator, '_get_best_previous_parameters', return_value=None):
        params = orchestrator._get_adaptive_parameters('NewMaterial', 'caption')
        
        # Should log warning about no history
        assert "No database history" in caplog.text
        
        # Should have calculated parameters
        assert 'api_params' in params
        assert 'temperature' in params['api_params']
```

#### Test 4: Database Params Used on All Attempts
```python
def test_database_params_used_all_attempts():
    orchestrator = UnifiedOrchestrator(api_client=api_client)
    
    db_params = {
        'temperature': 0.85,
        'frequency_penalty': 0.3,
        'presence_penalty': 0.3,
        'human_score': 75.0
    }
    
    with patch.object(orchestrator, '_get_best_previous_parameters', return_value=db_params):
        # Attempt 1
        params1 = orchestrator._get_adaptive_parameters('Material', 'caption', attempt=1)
        assert params1['api_params']['temperature'] == 0.85
        
        # Attempt 2 (retry)
        params2 = orchestrator._get_adaptive_parameters('Material', 'caption', attempt=2)
        assert params2['api_params']['temperature'] == 0.85  # Still starts with DB
```

---

## 📈 Benefits

### Material-Specific Learning
Each material learns its own optimal parameters:
- Aluminum: temperature=0.95, penalties=0.45
- Steel: temperature=0.88, penalties=0.40
- Brass: temperature=0.92, penalties=0.48

### Continuous Improvement
System improves with each generation:
```
Gen 1: temp=0.628 (fallback) → human_score=45%
Gen 2: temp=0.628 (from DB)  → human_score=67% ⬆️
Gen 3: temp=0.628 (from DB)  → human_score=72% ⬆️
```

### Consistency
Same material always starts with proven best parameters, ensuring consistent quality.

---

## 🔍 Monitoring

### Log Messages to Watch

**Success Indicators**:
```
✓ Reusing proven successful parameters (human_score=67.3%)
   • temperature=0.950 (was 0.628)
   • frequency_penalty=0.450 (was 0.000)
```

**First Generation**:
```
⚠️  No database history for NewMaterial caption - calculating from scratch
```

**Retry Behavior**:
```
🔄 Retry 2: Starting with DB params (temp=0.950, score=67.3%)
```

### Database Queries
```sql
-- Check parameter history for material
SELECT 
    p.temperature,
    p.frequency_penalty,
    p.presence_penalty,
    r.human_score,
    r.timestamp
FROM generation_parameters p
JOIN detection_results r ON p.detection_result_id = r.id
WHERE p.material = 'Aluminum'
  AND p.component_type = 'caption'
  AND r.success = 1
ORDER BY r.human_score DESC;
```

---

## ✅ Compliance Checklist

### Configuration
- [ ] `processing/config.yaml` contains ONLY word counts
- [ ] No `generation_temperature` in config
- [ ] No `max_tokens` in config
- [ ] No API generation parameters in config

### Code
- [ ] `_get_best_previous_parameters()` called FIRST
- [ ] Database checked on ALL attempts (not just attempt 1)
- [ ] Fallback only used when `previous_params` is None
- [ ] Schema validation before using database params

### Logging
- [ ] Warning logged when no database history
- [ ] Success message with specific param changes
- [ ] Retry messages show DB params as starting point

### Testing
- [ ] Tests verify config contains only word counts
- [ ] Tests verify database queried first
- [ ] Tests verify fallback only when needed
- [ ] Tests verify retries use database params

---

## 📚 Related Documentation

- **Implementation**: `MANDATORY_REQUIREMENTS_COMPLETE.md`
- **Parameter Logging**: `docs/development/PARAMETER_LOGGING_QUICK_START.md`
- **Database Schema**: `docs/development/DATABASE_PARAMETER_STORAGE.md`
- **Config Structure**: `processing/config.yaml`
- **Orchestrator Code**: `processing/unified_orchestrator.py`

---

**Last Updated**: November 15, 2025  
**Policy Owner**: System Architecture Team
