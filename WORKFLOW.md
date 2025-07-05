# 🚀 Z-Beam Workflow Guide

## Your Simple 2-Step Process

### 1. Generate Content
```bash
python3 run.py
```
- Edit material/settings in `run.py` 
- Generates article with AI detection
- Creates `.mdx` file in `app/(materials)/posts/`

### 2. Train & Improve  
```bash
python3 train.py
```
- Uses same material from `run.py`
- Rate content naturalness (1-5 scale)
- Improves detection for future generations

## Alternative Commands

### All-in-One Workflow
```bash
python3 workflow.py generate    # Same as: python3 run.py
python3 workflow.py train      # Same as: python3 train.py  
python3 workflow.py test       # Test detection improvements
```

### Test Detection Improvements
```bash
python3 run.py --test-detector
```

## Configuration

All settings in **`run.py`**:
- `material`: What to write about (e.g., "Bronze", "Aluminum")
- `generator_provider`: AI provider (DEEPSEEK, GEMINI, XAI)  
- `ai_detection_threshold`: How strict AI detection is (25 = strict)
- `iterations_per_section`: How many attempts to improve (5 = thorough)

## Training Tips

- **Rate naturalness honestly**: 1=Natural Expert Voice, 5=Obviously AI
- **Focus on professional tone**: Not too casual, not too robotic
- **Train regularly**: After generating new content
- **Look for patterns**: What makes content sound authentic vs artificial

## File Structure

```
/
├── run.py          # 🎯 Main config & generation
├── train.py        # 🎓 Quick training entry  
├── workflow.py     # 🔧 All-in-one commands
├── generator/      # 🏗️ Core system (don't edit)
└── app/           # 📄 Generated articles
```

**Focus on `run.py` for all your configuration needs!**
