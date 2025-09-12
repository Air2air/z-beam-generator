# Optimizer Configuration Guide

## Overview
Comprehensive configuration guide for the Z-Beam Optimizer system, covering all configuration files, settings, and customization options.

## Configuration Architecture

### Configuration File Hierarchy
```
optimizer/
├── config/                           # Service configurations
│   ├── optimization_config.yaml     # Main optimization settings
│   ├── api_config.yaml              # API provider settings
│   └── logging_config.yaml          # Logging configuration
├── text_optimization/
│   ├── prompts/                     # Prompt configurations
│   │   ├── personas/                # Author-specific styles
│   │   └── formatting/              # Country-specific formatting
│   └── config/
│       └── enhancement_config.yaml  # Enhancement flag settings
└── services/
    ├── config/                      # Service-specific configs
    └── unified_config.py            # Unified configuration management
```

### Primary Configuration Files
```
components/text/prompts/
├── core/
│   └── ai_detection_core.yaml       # Core AI detection configuration
└── modules/                         # Modular component configurations
    ├── authenticity_enhancements.yaml
    ├── cultural_adaptation.yaml
    ├── detection_avoidance.yaml
    ├── human_characteristics.yaml
    └── structural_improvements.yaml
```

### Runtime Configuration
```
run.py                               # Main API provider configuration
config/runtime_config.py            # Runtime settings
```

## Core Configuration Files

### 1. API Provider Configuration (`run.py`)

#### Complete Configuration Template
```python
API_PROVIDERS = {
    "deepseek": {
        "name": "deepseek",                    # ✅ Required: Provider identifier
        "base_url": "https://api.deepseek.com/v1",  # ✅ Required: API endpoint
        "model": "deepseek-chat",              # ✅ Required: Model name
        "timeout": 30,                         # ✅ Required: Request timeout (seconds)
        "retry_delay": 1.0,                    # ✅ Required: Retry delay (seconds)
        "max_retries": 3,                      # Optional: Maximum retry attempts
        "headers": {                           # Optional: Custom headers
            "User-Agent": "Z-Beam-Optimizer/1.0"
        }
    },
    "winston": {
        "name": "winston",                     # ✅ Required: Provider identifier
        "base_url": "https://api.gowinston.ai", # ✅ Required: API endpoint
        "timeout": 30,                         # Optional: Request timeout
        "verify_ssl": True                     # Optional: SSL verification
    }
}

# Component-specific configurations
COMPONENT_CONFIGS = {
    "text": {
        "max_length": 450,
        "min_length": 250,
        "quality_threshold": 0.7,
        "enhancement_flags": {
            "conversational_boost": True,
            "cultural_adaptation": True,
            "human_elements_emphasis": True
        }
    }
}
```

#### Environment Variable Support
```python
import os

API_PROVIDERS = {
    "deepseek": {
        "name": "deepseek",
        "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        "timeout": int(os.getenv("DEEPSEEK_TIMEOUT", "30")),
        "retry_delay": float(os.getenv("DEEPSEEK_RETRY_DELAY", "1.0"))
    },
    "winston": {
        "name": "winston",
        "base_url": os.getenv("WINSTON_BASE_URL", "https://api.gowinston.ai")
    }
}
```

### 2. AI Detection Core Configuration

#### File: `components/text/prompts/core/ai_detection_core.yaml`
```yaml
# Core AI detection configuration with modular component mapping
modular_components:
  authenticity_enhancements: "modules/authenticity_enhancements.yaml"
  cultural_adaptation: "modules/cultural_adaptation.yaml"
  detection_avoidance: "modules/detection_avoidance.yaml"
  human_characteristics: "modules/human_characteristics.yaml"
  structural_improvements: "modules/structural_improvements.yaml"

# Base AI detection guidance
base_ai_detection_guidance: |
  Generate natural, human-like content that effectively avoids AI detection while maintaining technical accuracy and cultural appropriateness.

# Quality thresholds
quality_thresholds:
  winston_threshold: 0.3        # Maximum acceptable AI detection score
  human_authenticity: 0.7       # Minimum human authenticity score
  technical_accuracy: 0.8       # Minimum technical accuracy score
  cultural_appropriateness: 0.7  # Minimum cultural adaptation score

# Content constraints
content_constraints:
  min_length: 250               # Minimum content length
  max_length: 450               # Maximum content length
  paragraph_count_range: [3, 6] # Paragraph count range
  sentence_per_paragraph: [2, 5] # Sentences per paragraph

# Enhancement priorities
enhancement_priorities:
  high_priority:
    - "human_authenticity"
    - "technical_accuracy"
  medium_priority:
    - "cultural_appropriateness"
    - "detection_avoidance"
  low_priority:
    - "structural_optimization"
```

### 3. Modular Component Configurations

#### Authenticity Enhancements (`modules/authenticity_enhancements.yaml`)
```yaml
authenticity_enhancements:
  conversational_patterns:
    starters:
      - "You know what I've noticed..."
      - "Here's the thing about..."
      - "I've got to say..."
      - "What really gets me is..."
    
    connectors:
      - "And another thing..."
      - "Plus, don't forget..."
      - "Oh, and by the way..."
    
    conclusions:
      - "So there you have it..."
      - "That's pretty much it..."
      - "Hope that helps!"
  
  personal_elements:
    experience_phrases:
      - "In my experience..."
      - "I remember when..."
      - "From what I've seen..."
      - "I've noticed that..."
    
    opinion_markers:
      - "I think..."
      - "In my opinion..."
      - "I believe..."
      - "It seems to me..."
  
  natural_inconsistencies:
    minor_errors:
      - "occasional comma splice"
      - "informal contractions"
      - "sentence fragments for emphasis"
    
    style_variations:
      - "mix formal and informal tone"
      - "vary sentence length significantly"
      - "use parenthetical asides"

  enhancement_flags:
    conversational_boost:
      triggers: ["conversational_patterns", "personal_elements"]
      intensity: "medium"
    
    human_elements_emphasis:
      triggers: ["personal_elements", "natural_inconsistencies"]
      intensity: "high"
```

#### Cultural Adaptation (`modules/cultural_adaptation.yaml`)
```yaml
cultural_adaptation:
  taiwan:
    language_characteristics:
      precision_focus: true
      technical_detail_emphasis: true
      efficiency_oriented: true
    
    expressions:
      - "確實是這樣" # "Indeed this is so"
      - "就是說啊" # "That's right"
      - "沒錯，就是這個意思" # "That's right, that's exactly what I mean"
    
    technical_terminology:
      laser_cleaning: "雷射清潔"
      surface_treatment: "表面處理"
      contamination_removal: "污染清除"
    
    communication_style:
      formality_level: "professional_friendly"
      detail_orientation: "high"
      directness: "moderate"

  italy:
    language_characteristics:
      expressive_technical: true
      craftsmanship_pride: true
      artistic_appreciation: true
    
    expressions:
      - "Ecco, questo è importante" # "Here, this is important"
      - "Come dire..." # "How to say..."
      - "Diciamo che..." # "Let's say that..."
      - "In pratica..." # "In practice..."
    
    technical_terminology:
      laser_cleaning: "pulizia laser"
      surface_treatment: "trattamento superficiale"
      precision_work: "lavoro di precisione"
    
    communication_style:
      formality_level: "expressive_professional"
      passion_level: "high"
      craftsmanship_emphasis: true

  indonesia:
    language_characteristics:
      collaborative_approach: true
      community_oriented: true
      practical_solutions: true
    
    expressions:
      - "Begini ya..." # "So here's how it is..."
      - "Kalau menurut saya..." # "In my opinion..."
      - "Yang penting..." # "What's important..."
    
    communication_style:
      formality_level: "friendly_professional"
      inclusiveness: "high"
      helpfulness: "high"

  usa:
    language_characteristics:
      direct_communication: true
      efficiency_focus: true
      innovation_emphasis: true
    
    expressions:
      - "Here's the deal..."
      - "Bottom line is..."
      - "Let me be straight with you..."
      - "The way I see it..."
    
    communication_style:
      formality_level: "casual_professional"
      directness: "high"
      confidence: "high"

  enhancement_flags:
    cultural_adaptation:
      author_mapping:
        1: "taiwan"
        2: "italy"
        3: "indonesia"
        4: "usa"
      intensity: "high"
```

#### Detection Avoidance (`modules/detection_avoidance.yaml`)
```yaml
detection_avoidance:
  variability_techniques:
    sentence_starters:
      - "Well, to be honest..."
      - "Actually, thinking about it..."
      - "You know what?"
      - "Here's what I've found..."
    
    transition_phrases:
      - "But here's the thing..."
      - "On the other hand..."
      - "What's interesting is..."
      - "Now, don't get me wrong..."
    
    uncertainty_markers:
      - "I think..."
      - "It seems like..."
      - "From what I can tell..."
      - "As far as I know..."
  
  human_inconsistencies:
    natural_errors:
      - "occasional redundancy"
      - "minor grammatical variations"
      - "informal punctuation usage"
    
    style_mixing:
      - "combine technical and casual language"
      - "mix short and long sentences"
      - "include parenthetical thoughts"
  
  flow_disruptions:
    topic_transitions:
      - "natural tangents"
      - "brief personal anecdotes"
      - "contextual elaborations"
    
    rhythm_variations:
      - "varied paragraph lengths"
      - "mixed sentence structures"
      - "natural pauses and emphasis"
  
  enhancement_flags:
    detection_avoidance:
      techniques: ["variability_techniques", "human_inconsistencies", "flow_disruptions"]
      intensity: "high"
    
    sentence_variability:
      focus: ["sentence_starters", "transition_phrases"]
      intensity: "medium"
```

#### Human Characteristics (`modules/human_characteristics.yaml`)
```yaml
human_characteristics:
  emotional_expressions:
    positive_emotions:
      - "I'm really excited about..."
      - "What I love about this is..."
      - "I find it fascinating that..."
      - "It's pretty cool how..."
    
    concern_markers:
      - "What bothers me is..."
      - "I'm a bit worried about..."
      - "One thing that concerns me..."
    
    enthusiasm_indicators:
      - "This is amazing because..."
      - "I can't believe how..."
      - "It's incredible that..."
  
  subjective_statements:
    opinion_expressions:
      - "In my view..."
      - "I personally think..."
      - "My take on this is..."
      - "The way I see it..."
    
    preference_markers:
      - "I prefer..."
      - "I tend to like..."
      - "What works for me is..."
  
  experience_references:
    personal_anecdotes:
      - "I remember when..."
      - "Last time I dealt with this..."
      - "I've seen situations where..."
    
    learning_moments:
      - "I learned that..."
      - "It took me a while to realize..."
      - "I discovered that..."
  
  uncertainty_expressions:
    knowledge_limits:
      - "I'm not entirely sure, but..."
      - "From what I understand..."
      - "I could be wrong, but..."
    
    tentative_statements:
      - "It seems like..."
      - "I think it might be..."
      - "Probably..."
  
  enhancement_flags:
    human_elements_emphasis:
      elements: ["emotional_expressions", "subjective_statements", "experience_references"]
      intensity: "high"
```

#### Structural Improvements (`modules/structural_improvements.yaml`)
```yaml
structural_improvements:
  paragraph_patterns:
    introduction:
      - "Let me start by explaining..."
      - "First, it's important to understand..."
      - "Before we dive in..."
      - "Here's what you need to know..."
    
    body_transitions:
      - "Moving on to..."
      - "This brings us to..."
      - "Another key point is..."
      - "Now, let's talk about..."
    
    emphasis_techniques:
      - "Here's the key thing..."
      - "This is crucial..."
      - "Pay attention to this..."
      - "Don't overlook..."
    
    conclusions:
      - "To sum it up..."
      - "The key takeaway here is..."
      - "In conclusion..."
      - "So, what does this mean?"
  
  information_hierarchy:
    priority_markers:
      high_priority:
        - "Most importantly..."
        - "The critical factor is..."
        - "Essential to understand..."
      
      medium_priority:
        - "Also worth noting..."
        - "Another consideration..."
        - "It's helpful to know..."
      
      supporting_details:
        - "For example..."
        - "Such as..."
        - "Including..."
  
  readability_optimization:
    sentence_length_guidelines:
      short_sentences: 5-10    # words
      medium_sentences: 11-20  # words
      long_sentences: 21-30    # words
      max_sentence_length: 35  # words
    
    paragraph_structure:
      min_sentences: 2
      max_sentences: 5
      ideal_sentences: 3
    
    flow_techniques:
      - "logical progression"
      - "clear topic sentences"
      - "smooth transitions"
      - "consistent terminology"
  
  enhancement_flags:
    structural_optimization:
      focus: ["paragraph_patterns", "information_hierarchy", "readability_optimization"]
      intensity: "medium"
    
    paragraph_enhancement:
      focus: ["paragraph_patterns", "readability_optimization"]
      intensity: "high"
```

## Service Configuration

### 1. Optimization Service Configuration

#### File: `optimizer/config/optimization_config.yaml`
```yaml
optimization_service:
  default_settings:
    max_iterations: 3
    quality_threshold: 0.7
    timeout_seconds: 30
    batch_size: 5
    
  performance_settings:
    cache_ttl: 3600          # Cache time-to-live in seconds
    worker_threads: 4        # Number of worker threads
    memory_limit_mb: 512     # Memory limit in MB
    
  quality_settings:
    winston_threshold: 0.3   # Maximum AI detection score
    min_human_authenticity: 0.7
    min_technical_accuracy: 0.8
    min_cultural_appropriateness: 0.7
    
  retry_settings:
    max_retries: 3
    retry_delay: 1.0
    exponential_backoff: true
    
  enhancement_defaults:
    conversational_boost: true
    cultural_adaptation: true
    human_elements_emphasis: true
    detection_avoidance: false  # Only when needed
    structural_optimization: false
```

### 2. API Configuration

#### File: `optimizer/config/api_config.yaml`
```yaml
api_configuration:
  providers:
    deepseek:
      default_model: "deepseek-chat"
      default_timeout: 30
      max_tokens: 4000
      temperature: 0.7
      retry_policy:
        max_retries: 3
        retry_delay: 1.0
        exponential_backoff: true
      
    winston:
      default_timeout: 30
      analysis_type: "comprehensive"
      response_format: "detailed"
      
  rate_limiting:
    requests_per_minute: 60
    burst_capacity: 10
    cooldown_period: 60
    
  caching:
    enable_response_cache: true
    cache_ttl: 3600
    max_cache_size_mb: 100
```

### 3. Logging Configuration

#### File: `optimizer/config/logging_config.yaml`
```yaml
logging:
  version: 1
  disable_existing_loggers: false
  
  formatters:
    standard:
      format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
      datefmt: "%Y-%m-%d %H:%M:%S"
    
    detailed:
      format: "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
      datefmt: "%Y-%m-%d %H:%M:%S"
  
  handlers:
    console:
      class: logging.StreamHandler
      level: INFO
      formatter: standard
      stream: ext://sys.stdout
    
    file:
      class: logging.handlers.RotatingFileHandler
      level: DEBUG
      formatter: detailed
      filename: logs/optimizer.log
      maxBytes: 10485760  # 10MB
      backupCount: 5
    
    error_file:
      class: logging.handlers.RotatingFileHandler
      level: ERROR
      formatter: detailed
      filename: logs/optimizer_errors.log
      maxBytes: 5242880   # 5MB
      backupCount: 3
  
  loggers:
    optimizer:
      level: DEBUG
      handlers: [console, file, error_file]
      propagate: false
    
    optimizer.text_optimization:
      level: DEBUG
      handlers: [file]
      propagate: true
    
    optimizer.services:
      level: INFO
      handlers: [file]
      propagate: true
  
  root:
    level: WARNING
    handlers: [console]
```

## Environment Configuration

### 1. Environment Variables

#### Required Environment Variables
```bash
# API Keys
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export WINSTON_API_KEY="your_winston_api_key"

# Optional API Configuration
export DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
export DEEPSEEK_MODEL="deepseek-chat"
export DEEPSEEK_TIMEOUT="30"
export WINSTON_BASE_URL="https://api.gowinston.ai"

# Optimizer Settings
export OPTIMIZER_LOG_LEVEL="INFO"
export OPTIMIZER_CACHE_TTL="3600"
export OPTIMIZER_MAX_ITERATIONS="3"
export OPTIMIZER_QUALITY_THRESHOLD="0.7"

# Performance Settings
export OPTIMIZER_WORKER_THREADS="4"
export OPTIMIZER_MEMORY_LIMIT_MB="512"
export OPTIMIZER_BATCH_SIZE="5"
```

#### Environment File Template (`.env`)
```bash
# Z-Beam Optimizer Environment Configuration

# API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
WINSTON_API_KEY=your_winston_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
WINSTON_BASE_URL=https://api.gowinston.ai

# Quality Settings
OPTIMIZER_QUALITY_THRESHOLD=0.7
WINSTON_THRESHOLD=0.3
MIN_HUMAN_AUTHENTICITY=0.7
MIN_TECHNICAL_ACCURACY=0.8

# Performance Settings
OPTIMIZER_MAX_ITERATIONS=3
OPTIMIZER_TIMEOUT=30
OPTIMIZER_CACHE_TTL=3600
OPTIMIZER_WORKER_THREADS=4

# Logging
OPTIMIZER_LOG_LEVEL=INFO
LOG_FILE_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5

# Development Settings
DEBUG_MODE=false
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_DETAILED_LOGGING=false
```

### 2. Configuration Loading

#### Environment Configuration Loader
```python
import os
from typing import Dict, Any

class EnvironmentConfig:
    """Load configuration from environment variables."""
    
    @staticmethod
    def load_api_config() -> Dict[str, Any]:
        """Load API configuration from environment."""
        return {
            "deepseek": {
                "name": "deepseek",
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
                "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                "timeout": int(os.getenv("DEEPSEEK_TIMEOUT", "30")),
                "retry_delay": float(os.getenv("DEEPSEEK_RETRY_DELAY", "1.0"))
            },
            "winston": {
                "name": "winston",
                "api_key": os.getenv("WINSTON_API_KEY"),
                "base_url": os.getenv("WINSTON_BASE_URL", "https://api.gowinston.ai"),
                "timeout": int(os.getenv("WINSTON_TIMEOUT", "30"))
            }
        }
    
    @staticmethod
    def load_optimizer_config() -> Dict[str, Any]:
        """Load optimizer configuration from environment."""
        return {
            "max_iterations": int(os.getenv("OPTIMIZER_MAX_ITERATIONS", "3")),
            "quality_threshold": float(os.getenv("OPTIMIZER_QUALITY_THRESHOLD", "0.7")),
            "timeout_seconds": int(os.getenv("OPTIMIZER_TIMEOUT", "30")),
            "cache_ttl": int(os.getenv("OPTIMIZER_CACHE_TTL", "3600")),
            "worker_threads": int(os.getenv("OPTIMIZER_WORKER_THREADS", "4")),
            "batch_size": int(os.getenv("OPTIMIZER_BATCH_SIZE", "5"))
        }
    
    @staticmethod
    def validate_required_vars() -> bool:
        """Validate required environment variables."""
        required_vars = [
            "DEEPSEEK_API_KEY",
            "WINSTON_API_KEY"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {missing_vars}")
        
        return True

# Usage
config = EnvironmentConfig()
config.validate_required_vars()
api_config = config.load_api_config()
optimizer_config = config.load_optimizer_config()
```

## Configuration Validation

### 1. Configuration Validation Script

#### File: `scripts/validate_configuration.py`
```python
#!/usr/bin/env python3
"""Configuration validation script for Z-Beam Optimizer."""

import os
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Any

class ConfigurationValidator:
    """Validate optimizer configuration files and settings."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.base_path = Path(__file__).parent.parent
    
    def validate_all(self) -> bool:
        """Validate all configuration aspects."""
        print("🔍 Validating Z-Beam Optimizer Configuration...")
        
        # Validate configuration files
        self.validate_yaml_files()
        
        # Validate environment variables
        self.validate_environment()
        
        # Validate API configuration
        self.validate_api_config()
        
        # Validate modular components
        self.validate_modular_components()
        
        # Print results
        self.print_results()
        
        return len(self.errors) == 0
    
    def validate_yaml_files(self):
        """Validate all YAML configuration files."""
        yaml_files = [
            "components/text/prompts/core/ai_detection_core.yaml",
            "components/text/prompts/modules/authenticity_enhancements.yaml",
            "components/text/prompts/modules/cultural_adaptation.yaml",
            "components/text/prompts/modules/detection_avoidance.yaml", 
            "components/text/prompts/modules/human_characteristics.yaml",
            "components/text/prompts/modules/structural_improvements.yaml"
        ]
        
        for yaml_file in yaml_files:
            file_path = self.base_path / yaml_file
            if not file_path.exists():
                self.errors.append(f"Missing YAML file: {yaml_file}")
                continue
            
            try:
                with open(file_path, 'r') as f:
                    yaml.safe_load(f)
                print(f"✅ {yaml_file}")
            except yaml.YAMLError as e:
                self.errors.append(f"Invalid YAML in {yaml_file}: {e}")
            except Exception as e:
                self.errors.append(f"Error reading {yaml_file}: {e}")
    
    def validate_environment(self):
        """Validate environment variables."""
        required_vars = ["DEEPSEEK_API_KEY", "WINSTON_API_KEY"]
        optional_vars = [
            "DEEPSEEK_BASE_URL", "WINSTON_BASE_URL", 
            "OPTIMIZER_LOG_LEVEL", "OPTIMIZER_MAX_ITERATIONS"
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                self.errors.append(f"Missing required environment variable: {var}")
            else:
                print(f"✅ {var} is set")
        
        for var in optional_vars:
            if os.getenv(var):
                print(f"✅ {var} is set")
            else:
                self.warnings.append(f"Optional environment variable not set: {var}")
    
    def validate_api_config(self):
        """Validate API configuration in run.py."""
        try:
            sys.path.append(str(self.base_path))
            from run import API_PROVIDERS
            
            required_deepseek_fields = ["name", "base_url", "model", "timeout", "retry_delay"]
            required_winston_fields = ["name", "base_url"]
            
            if "deepseek" in API_PROVIDERS:
                deepseek_config = API_PROVIDERS["deepseek"]
                for field in required_deepseek_fields:
                    if field not in deepseek_config:
                        self.errors.append(f"Missing DeepSeek config field: {field}")
                print("✅ DeepSeek configuration complete")
            else:
                self.errors.append("Missing DeepSeek configuration in API_PROVIDERS")
            
            if "winston" in API_PROVIDERS:
                winston_config = API_PROVIDERS["winston"]
                for field in required_winston_fields:
                    if field not in winston_config:
                        self.errors.append(f"Missing Winston config field: {field}")
                print("✅ Winston configuration complete")
            else:
                self.errors.append("Missing Winston configuration in API_PROVIDERS")
                
        except ImportError as e:
            self.errors.append(f"Cannot import API_PROVIDERS from run.py: {e}")
        except Exception as e:
            self.errors.append(f"Error validating API configuration: {e}")
    
    def validate_modular_components(self):
        """Validate modular component configuration."""
        core_config_path = self.base_path / "components/text/prompts/core/ai_detection_core.yaml"
        
        if not core_config_path.exists():
            self.errors.append("Missing core AI detection configuration file")
            return
        
        try:
            with open(core_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if "modular_components" not in config:
                self.errors.append("Missing modular_components section in core configuration")
                return
            
            modular_components = config["modular_components"]
            expected_components = [
                "authenticity_enhancements",
                "cultural_adaptation", 
                "detection_avoidance",
                "human_characteristics",
                "structural_improvements"
            ]
            
            for component in expected_components:
                if component not in modular_components:
                    self.errors.append(f"Missing modular component: {component}")
                else:
                    component_path = self.base_path / "components/text/prompts" / modular_components[component]
                    if not component_path.exists():
                        self.errors.append(f"Modular component file not found: {modular_components[component]}")
                    else:
                        print(f"✅ Modular component: {component}")
            
        except Exception as e:
            self.errors.append(f"Error validating modular components: {e}")
    
    def print_results(self):
        """Print validation results."""
        print("\n" + "="*50)
        if self.errors:
            print("❌ Configuration Validation FAILED")
            print("\nErrors:")
            for error in self.errors:
                print(f"  ❌ {error}")
        else:
            print("✅ Configuration Validation PASSED")
        
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        print(f"\nSummary: {len(self.errors)} errors, {len(self.warnings)} warnings")

if __name__ == "__main__":
    validator = ConfigurationValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)
```

### 2. Configuration Testing

#### Unit Tests for Configuration
```python
import unittest
import tempfile
import yaml
from pathlib import Path

class TestConfiguration(unittest.TestCase):
    """Test configuration loading and validation."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
    
    def test_yaml_loading(self):
        """Test YAML configuration loading."""
        config_content = {
            "modular_components": {
                "authenticity_enhancements": "modules/authenticity_enhancements.yaml"
            }
        }
        
        config_file = self.base_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_content, f)
        
        # Test loading
        with open(config_file, 'r') as f:
            loaded_config = yaml.safe_load(f)
        
        self.assertEqual(loaded_config["modular_components"]["authenticity_enhancements"], 
                        "modules/authenticity_enhancements.yaml")
    
    def test_environment_validation(self):
        """Test environment variable validation."""
        import os
        
        # Test required variables
        required_vars = ["DEEPSEEK_API_KEY", "WINSTON_API_KEY"]
        
        for var in required_vars:
            # Temporarily unset
            original_value = os.getenv(var)
            if original_value:
                del os.environ[var]
            
            # Should fail validation
            with self.assertRaises(EnvironmentError):
                EnvironmentConfig.validate_required_vars()
            
            # Restore
            if original_value:
                os.environ[var] = original_value

if __name__ == "__main__":
    unittest.main()
```

## Configuration Best Practices

### 1. Security Best Practices

#### API Key Management
```python
# ✅ Good: Use environment variables
api_key = os.getenv("DEEPSEEK_API_KEY")

# ❌ Bad: Hardcode in configuration files
api_key = "sk-1234567890abcdef"  # Never do this!

# ✅ Good: Validate key presence
if not api_key:
    raise EnvironmentError("DEEPSEEK_API_KEY environment variable required")
```

#### Configuration File Security
```bash
# Set appropriate file permissions
chmod 600 .env
chmod 644 *.yaml

# Add sensitive files to .gitignore
echo ".env" >> .gitignore
echo "config/secrets.yaml" >> .gitignore
```

### 2. Configuration Organization

#### Hierarchical Configuration Loading
```python
class ConfigurationManager:
    """Manage configuration with proper precedence."""
    
    def __init__(self):
        self.config = {}
    
    def load_configuration(self):
        """Load configuration with proper precedence:
        1. Default values
        2. Configuration files
        3. Environment variables
        4. Command line arguments
        """
        # 1. Load defaults
        self.config.update(self.get_defaults())
        
        # 2. Load from files
        self.config.update(self.load_from_files())
        
        # 3. Override with environment
        self.config.update(self.load_from_environment())
        
        # 4. Override with command line
        self.config.update(self.load_from_cli())
        
        return self.config
```

### 3. Configuration Validation

#### Schema Validation
```python
import jsonschema

CONFIGURATION_SCHEMA = {
    "type": "object",
    "properties": {
        "api_providers": {
            "type": "object",
            "properties": {
                "deepseek": {
                    "type": "object",
                    "required": ["name", "base_url", "model", "timeout"],
                    "properties": {
                        "name": {"type": "string"},
                        "base_url": {"type": "string", "format": "uri"},
                        "model": {"type": "string"},
                        "timeout": {"type": "number", "minimum": 1}
                    }
                }
            }
        }
    },
    "required": ["api_providers"]
}

def validate_configuration(config):
    """Validate configuration against schema."""
    jsonschema.validate(config, CONFIGURATION_SCHEMA)
```

## Troubleshooting Configuration Issues

### Common Configuration Problems

1. **Missing modular_components section**
   - Check `ai_detection_core.yaml` has complete modular_components mapping
   - Verify all module files exist in `modules/` directory

2. **API configuration errors**
   - Ensure all required fields are present in `run.py` API_PROVIDERS
   - Validate environment variables are set correctly

3. **YAML syntax errors**
   - Use YAML validators to check syntax
   - Verify proper indentation and structure

4. **Permission errors**
   - Check file permissions for configuration files
   - Ensure read access to all configuration directories

### Diagnostic Commands

```bash
# Validate all configuration
python3 scripts/validate_configuration.py

# Test modular component loading
python3 -c "
from optimizer.text_optimization.utils.modular_loader import ModularLoader
loader = ModularLoader()
config = loader.load_complete_configuration()
print(f'Loaded {len(config)} sections')
"

# Test API configuration
python3 -c "
from run import API_PROVIDERS
print('API Providers configured:')
for name, config in API_PROVIDERS.items():
    print(f'  {name}: {list(config.keys())}')
"
```

This configuration guide provides comprehensive coverage of all configuration aspects of the Z-Beam Optimizer system. Keep this guide updated as new configuration options are added.
