# Recovery System and Component Configuration

## Component Enabled/Disabled Behavior

The recovery system **automatically respects** the `enabled` settings in `run.py` BATCH_CONFIG.

### Current BATCH_CONFIG Status

```python
BATCH_CONFIG = {
    "components": {
        "frontmatter": {"enabled": True},      # ✅ Will be validated
        "content": {"enabled": False},         # ❌ Ignored by recovery system  
        "bullets": {"enabled": True},          # ✅ Will be validated
        "table": {"enabled": True},            # ✅ Will be validated
        "tags": {"enabled": False},            # ❌ Ignored by recovery system
        "caption": {"enabled": True},          # ✅ Will be validated
        "jsonld": {"enabled": True},           # ✅ Will be validated
        "metatags": {"enabled": True},         # ✅ Will be validated
        "propertiestable": {"enabled": True},  # ✅ Will be validated
    }
}
```

### Recovery System Behavior

**✅ Components with `enabled: True`:**
- Are included in validation reports
- Count toward success/failure rates
- Generate recovery suggestions if they fail
- Can be recovered using the recovery commands

**❌ Components with `enabled: False`:**
- Are completely ignored by the recovery system
- Do not appear in validation reports
- Do not count toward success/failure rates  
- Will not generate recovery suggestions
- Cannot be recovered (recovery will skip them)

### Example Impact

**Before Fix (Incorrect Behavior):**
```
📊 Validation Report: Tempered Glass
Success Rate: 2/8 (25.0%)
❌ Failed Components: frontmatter, metatags, caption, propertiestable, tags, jsonld
```

**After Fix (Correct Behavior):**
```
📊 Validation Report: Tempered Glass  
Success Rate: 2/7 (28.6%)
❌ Failed Components: frontmatter, metatags, caption, propertiestable, jsonld
```

Notice:
- `tags` is no longer listed as failed (it's disabled)
- Success rate improved because disabled components don't count
- Only 7 components checked instead of 8

### Verification

You can verify which components are being checked:

```python
from recovery import MaterialRecoverySystem
recovery = MaterialRecoverySystem()
print("Components being validated:", recovery.components)
```

Output:
```
Components being validated: ['frontmatter', 'bullets', 'table', 'caption', 'jsonld', 'metatags', 'propertiestable']
```

### Benefits

1. **Accurate Reporting** - Success rates reflect only components you actually want to generate
2. **Focused Recovery** - No wasted effort trying to recover disabled components
3. **Configuration Consistency** - Recovery system matches your generation configuration
4. **Cleaner Output** - Reports only show relevant component status

### Manual Override

If you want to validate disabled components for testing purposes, you would need to:

1. Temporarily enable them in BATCH_CONFIG
2. Run the validation/recovery
3. Disable them again

**Important:** The recovery system always reads the current BATCH_CONFIG, so any changes to enabled settings will be immediately reflected in the next validation run.
