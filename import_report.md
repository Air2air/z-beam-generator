# Absolute Import Migration Report
Project: .
Files scanned: 258
Issues found: 46

## High Confidence Fixes
Count: 4
- api/client.py:76
  `from .config import get_default_config`
  → `from config import get_default_config`
- api/client_manager.py:26
  `from .config import API_PROVIDERS`
  → `from config import API_PROVIDERS`
- api/deepseek.py:12
  `from .config import get_default_config`
  → `from config import get_default_config`
- optimizer/text_optimization/dynamic_prompt_system/__init__.py:20
  `from .dynamic_prompt_generator import DynamicPromptGenerator`
  → `from optimizer.text_optimization.dynamic_prompt_generator import DynamicPromptGenerator`

## Medium Confidence Fixes
Count: 0

## Low Confidence Fixes
Count: 42
These may need manual review
