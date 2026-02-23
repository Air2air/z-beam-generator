# Z-Beam Generator Installation Guide

**📋 Complete setup guide for Z-Beam Generator**  
**⏱️ Setup Time**: 15-20 minutes  
**💻 Requirements**: Python 3.8+, Git, API keys  

---

## 🚀 Quick Start

### Prerequisites Check
```bash
# Check Python version (3.8+ required)
python3 --version

# Check Git installation
git --version

# Check pip installation
pip3 --version
```

### 1-Minute Setup
```bash
# Clone repository
git clone https://github.com/your-org/z-beam-generator.git
cd z-beam-generator

# Install dependencies
pip3 install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env

# Test installation
python3 run.py --check-env
```

---

## 📦 Detailed Installation

### Step 1: System Requirements

#### Required Software
- **Python**: 3.8 or higher
- **Git**: For repository cloning
- **Text Editor**: nano, vim, or VS Code for configuration

#### Operating System Support
- ✅ **macOS**: 10.15+ (tested)
- ✅ **Linux**: Ubuntu 18.04+, CentOS 7+ (tested)
- ✅ **Windows**: Windows 10+ with WSL (tested)

#### Hardware Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for API calls

### Step 2: Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/your-org/z-beam-generator.git

# Navigate to directory
cd z-beam-generator

# Verify repository structure
ls -la
```

**Expected Structure**:
```
z-beam-generator/
├── components/          # Component generators
├── api/                # API client management
├── data/               # Material data
├── config/             # Configuration files
├── docs/               # Documentation
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
└── run.py             # Main application
```

### Step 3: Install Dependencies

#### Option A: pip (Recommended)
```bash
# Install all required packages
pip3 install -r requirements.txt

# Verify installation
pip3 list | grep -E "(requests|pyyaml|click)"
```

#### Option B: Virtual Environment (Isolated)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Common Dependencies
- `requests`: HTTP client for API calls
- `pyyaml`: YAML parsing and generation
- `click`: Command line interface
- `pathlib`: File path operations
- `python-dotenv`: Environment variable management

### Step 4: API Configuration

#### Copy Environment Template
```bash
# Copy template
cp .env.example .env

# Open for editing
nano .env
```

#### Required API Keys

##### DeepSeek (Content Generation)
1. Visit [https://platform.deepseek.com](https://platform.deepseek.com)
2. Create account and generate API key
3. Add to `.env`:
```env
DEEPSEEK_API_KEY=sk-your_deepseek_key_here
```

##### Grok (Alternative Content Generation)
1. Visit [https://console.groq.com](https://console.groq.com)
2. Generate API key
3. Add to `.env`:
```env
GROK_API_KEY=gsk_your_grok_key_here
```

##### AI Detection (Local System)
**Note**: We use a local pattern-based AI detection system.
- **Module**: `postprocessing/detection/winston_analyzer.py`
- **Patterns**: prompt catalog entry `prompts/ai_detection_patterns.txt` in `prompts/registry/prompt_catalog.yaml`
- **No API keys required** for AI detection
- See `docs/QUICK_REFERENCE.md` for usage details

#### Complete .env Example
```env
# Content Generation Providers
DEEPSEEK_API_KEY=sk-your_deepseek_key_here
GROK_API_KEY=gsk_your_grok_key_here

# AI Detection: Local system (no API keys needed)
# Detection configured in prompt catalog entry prompts/ai_detection_patterns.txt
```

### Step 5: Verification & Testing

#### Environment Check
```bash
# Verify environment configuration
python3 run.py --check-env
```

**Expected Output**:
```
🔑 Successfully loaded 4 API keys from .env file
✅ Environment configuration valid
✅ All required dependencies installed
✅ Material data loaded successfully
```

#### API Connectivity Test
```bash
# Test all API connections
python3 run.py --test-api
```

**Expected Output**:
```
🔧 Testing API connectivity...
✅ [CLIENT MANAGER] deepseek: Connected successfully
✅ [CLIENT MANAGER] grok: Connected successfully  
✅ [CLIENT MANAGER] winston: Connected successfully
🎯 All API providers operational
```

#### First Content Generation Test
```bash
# Generate test content
python3 run.py --material "Steel" --components "frontmatter"
```

**Expected Output**:
```
🚀 Generating frontmatter for Steel
✅ frontmatter generated successfully → content/components/frontmatter/steel-laser-cleaning.md
```

---

## 🔧 Configuration Options

### Basic Configuration

#### Material Selection
```bash
# Generate specific material
python3 run.py --material "Aluminum"

# Generate all materials (batch mode)
python3 run.py

# List available materials
python3 run.py --list-materials
```

#### Component Selection
```bash
# Generate specific components
python3 run.py --material "Steel" --components "frontmatter,text"

# Generate all components
python3 run.py --material "Steel"

# List available components
python3 run.py --list-components
```

### Advanced Configuration

#### API Provider Selection
```bash
# Use specific content provider
python3 run.py --provider deepseek --material "Copper"

# Use specific AI detector
python3 run.py --ai-detector winston --material "Aluminum"
```

#### Output Configuration
```bash
# Custom output directory
python3 run.py --output-dir "custom/output/path"

# Clean previous output
python3 run.py --clean

# Verbose logging
python3 run.py --verbose
```

---

## 🛠️ Troubleshooting Installation

### Common Issues

#### Python Version Issues
**Symptom**: `python3: command not found` or version < 3.8
**Solutions**:
```bash
# macOS with Homebrew
brew install python@3.9

# Ubuntu/Debian
sudo apt update && sudo apt install python3.9

# CentOS/RHEL
sudo yum install python39

# Verify installation
python3 --version
```

#### Permission Issues
**Symptom**: `Permission denied` during installation
**Solutions**:
```bash
# Use user installation
pip3 install --user -r requirements.txt

# Or fix permissions (Linux/macOS)
sudo chown -R $USER:$USER ~/.local/
```

#### API Key Issues
**Symptom**: `❌ [CLIENT MANAGER] provider: Failed - None`
**Solutions**:
```bash
# Check .env file exists
ls -la .env

# Verify API key format
cat .env | grep API_KEY

# Test specific provider
python3 -c "
from api.client_manager import test_api_connectivity
test_api_connectivity('deepseek')
"
```

#### Network/Firewall Issues
**Symptom**: `Connection timeout` or `SSL certificate verification failed`
**Solutions**:
```bash
# Test internet connectivity
curl -I https://api.deepseek.com

# Check firewall settings
# Corporate networks may block API endpoints

# Test with verbose output
python3 run.py --test-api --verbose
```

### Getting Help

#### Self-Diagnosis Tools
```bash
# Complete system diagnostic
python3 scripts/tools/system_diagnostic.py

# API-specific diagnostics
python3 scripts/tools/api_terminal_diagnostics.py winston

# Environment validation
python3 scripts/tools/validate_environment.py
```

#### Log Files
- **Application Logs**: `logs/z-beam.log`
- **Error Logs**: `logs/errors.log`
- **API Logs**: `logs/api_calls.log`

#### Support Resources
- **Documentation**: `docs/troubleshooting/`
- **GitHub Issues**: Report bugs and get help
- **Community Discord**: Real-time support

---

## 🎯 Next Steps

### After Installation
1. **Generate Your First Content**: `python3 run.py --material "Steel"`
2. **Explore Components**: Try different `--components` options
3. **Read Documentation**: Check `docs/operations/CONTENT_GENERATION.md`
4. **Optimize Content**: Learn about `--optimize` flag

### Recommended Reading
- [Content Generation Guide](../operations/CONTENT_GENERATION.md)
- [API Configuration Details](API_CONFIGURATION.md)
- [Component Overview](../components/README.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

### Production Setup
- [Batch Operations](../operations/BATCH_OPERATIONS.md)
- [Performance Optimization](../operations/OPTIMIZATION.md)
- [Monitoring & Maintenance](../operations/MAINTENANCE.md)

---

**✅ Installation Complete!**  
**🎯 Next**: [Generate your first content](../operations/CONTENT_GENERATION.md)  
**📖 Support**: [Troubleshooting Guide](TROUBLESHOOTING.md)
