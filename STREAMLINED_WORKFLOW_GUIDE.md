# Z-Beam Streamlined Workflow Guide

## Overview

You now have a single entry point (`run.py`) for your complete workflow:

1. **Configure your material/category** in `run.py`
2. **Generate articles** or **test detector improvements**  
3. **Validate output** with external AI detectors

## Usage

### 1. Normal Article Generation

```bash
# Edit USER_CONFIG in run.py for your material/category
python run.py
```

**Configuration in run.py:**
```python
USER_CONFIG = dict(
    material="Silver",                      # Your target material
    category="Material",                    # Article category  
    file_name="laser_cleaning_silver.mdx", # Output filename
    # ... other settings
)
```

### 2. Test Detector Improvements

```bash
# Test the prompt optimization improvements
python run.py --test-detector
```

This mode:
- ✅ **Dynamically discovers** available section templates from `generator/prompts/sections/`
- ✅ Tests 3 different materials with discovered sections
- ✅ Uses strict thresholds (AI ≤20%, Human ≤20%) for validation
- ✅ Uses 6 iterations to test more prompt variations
- ✅ Validates human-like output without try-hard traits
- ✅ Shows prompt optimization performance stats
- ✅ **Adapts automatically** when you add/remove section templates

## Your Workflow

### Step 1: Configure New Material
Edit `USER_CONFIG` in `run.py`:
```python
USER_CONFIG = dict(
    material="YourNewMaterial",              # ← Change this
    category="YourCategory",                 # ← Change this  
    file_name="laser_cleaning_yourmaterial.mdx",  # ← Change this
    ai_detection_threshold=50,               # Lower = more human-like
    human_detection_threshold=50,            # Lower = less try-hard
    iterations_per_section=5,                # More = better optimization
)
```

### Step 2: Generate Article
```bash
python run.py
```

### Step 3: Test Detector Improvements (Optional)
```bash
python run.py --test-detector
```

### Step 4: Validate with External Detectors
- Take the generated `.mdx` file from your output
- Run through external AI detectors 
- Verify it reads as human-written without try-hard traits

## Key Features

### ✅ Prompt Optimization System
- **Performance tracking**: Records which prompts work best
- **Automatic selection**: Chooses optimal prompts based on history
- **Iteration testing**: Tests multiple prompt variations per section
- **Human-like output**: Optimized to avoid AI detection patterns

### ✅ Detection Improvements  
- **Strict thresholds**: AI ≤20%, Human ≤20% for validation
- **Multiple iterations**: 6 attempts to reach thresholds
- **Prompt variety**: Uses different detection prompt variations
- **Performance analytics**: Shows optimization effectiveness

### ✅ Streamlined Interface
- **Single entry point**: Everything through `run.py`
- **Clear configuration**: Edit `USER_CONFIG` section
- **Flexible testing**: Multiple test modes available
- **Comprehensive feedback**: Detailed success/failure reporting

## Output Files

- **Generated articles**: `app/(materials)/[slug]/laser_cleaning_yourmaterial.mdx`
- **Performance data**: `generator/cache/prompt_performance.json`
- **Logs**: `logs/app.log`

## Tips for Best Results

1. **Higher iterations** (5-10) = better optimization but slower
2. **Lower thresholds** (15-25) = more human-like output  
3. **Test detector mode** = validates your optimization improvements
4. **Monitor logs** = see which prompts perform best

## Troubleshooting

### API Quota Issues
- Switch providers: Change `generator_provider` or `detection_provider` 
- Available: `XAI`, `GEMINI`, `DEEPSEEK`

### Poor Detection Scores  
- Run `python run.py --test-detector` to validate improvements
- Lower thresholds in `USER_CONFIG`
- Increase `iterations_per_section`

### Template Errors
- Ensure prompt templates exist in `generator/prompts/content/`
- Check section names match available templates

---

Your workflow is now fully streamlined! Just edit the config, run the command, and validate the output. The prompt optimization system will continuously improve performance based on detection results.
