# Setup Troubleshooting Guide

**📋 Complete troubleshooting guide for Z-Beam Generator setup issues**  
**🎯 Scope**: Installation, configuration, and initial setup problems  
**⏱️ Average Resolution Time**: 5-15 minutes per issue  

---

## 🚀 Quick Diagnostics

### System Health Check
```bash
# Run complete system diagnostic
python3 run.py --check-env

# Expected healthy output:
# 🔑 Successfully loaded 4 API keys from .env file
# ✅ Environment configuration valid
# ✅ All required dependencies installed
# ✅ Material data loaded successfully
```

### API Connectivity Test
```bash
# Test all API connections
python3 run.py --test-api

# Expected healthy output:
# ✅ [CLIENT MANAGER] deepseek: Connected successfully
# ✅ [CLIENT MANAGER] grok: Connected successfully  
# ✅ [CLIENT MANAGER] winston: Connected successfully
```

### Quick Fix Commands
```bash
# Reinstall dependencies
pip3 install -r requirements.txt --force-reinstall

# Reset environment file
cp .env.example .env

# Clear cache and restart
rm -rf __pycache__ && python3 run.py --check-env
```

---

## 🔧 Installation Issues

### Python Version Problems

#### Symptom: `python3: command not found`
**Platforms**: macOS, Linux  
**Root Cause**: Python 3 not installed or not in PATH

**Solutions**:

**macOS**:
```bash
# Install with Homebrew (recommended)
brew install python@3.11

# Verify installation
python3 --version  # Should show 3.8+

# If still not found, add to PATH
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Ubuntu/Debian**:
```bash
# Update package list
sudo apt update

# Install Python 3
sudo apt install python3 python3-pip

# Verify installation
python3 --version
```

**CentOS/RHEL**:
```bash
# Install Python 3.9+
sudo dnf install python39 python39-pip

# Create symlink if needed
sudo ln -s /usr/bin/python3.9 /usr/bin/python3
```

#### Symptom: Python version too old (< 3.8)
**Error**: `Python 3.8+ required, found 3.6`

**Solutions**:
```bash
# Check current version
python3 --version

# macOS - upgrade with Homebrew
brew upgrade python@3.11

# Ubuntu - install newer version
sudo apt install python3.11
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Verify upgrade
python3 --version
```

### Dependency Installation Issues

#### Symptom: `pip3: command not found`
**Root Cause**: pip not installed with Python

**Solutions**:
```bash
# macOS
brew install python3-pip

# Ubuntu/Debian
sudo apt install python3-pip

# CentOS/RHEL
sudo dnf install python3-pip

# Manual installation (all platforms)
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

#### Symptom: Permission denied during pip install
**Error**: `ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied`

**Solutions**:
```bash
# Option 1: User installation (recommended)
pip3 install --user -r requirements.txt

# Option 2: Fix permissions (Linux/macOS)
sudo chown -R $USER:$USER ~/.local/

# Option 3: Virtual environment (isolated)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

#### Symptom: Package installation fails
**Error**: `ERROR: Failed building wheel for [package]`

**Solutions**:
```bash
# Update pip and setuptools
pip3 install --upgrade pip setuptools wheel

# Install build dependencies (Ubuntu/Debian)
sudo apt install build-essential python3-dev

# Install build dependencies (CentOS/RHEL)
sudo dnf groupinstall "Development Tools"
sudo dnf install python3-devel

# Retry installation
pip3 install -r requirements.txt
```

### Repository Clone Issues

#### Symptom: Git clone fails
**Error**: `fatal: repository not found` or `Permission denied`

**Solutions**:
```bash
# Check Git installation
git --version

# Install Git if missing
# macOS
brew install git

# Ubuntu/Debian
sudo apt install git

# Clone with HTTPS (if SSH fails)
git clone https://github.com/your-org/z-beam-generator.git

# Check repository URL
git remote -v
```

#### Symptom: Repository structure incomplete
**Error**: Missing directories like `components/`, `api/`, etc.

**Solutions**:
```bash
# Verify complete clone
ls -la

# Expected structure:
# components/  api/  data/  config/  docs/  requirements.txt  run.py

# If incomplete, re-clone
rm -rf z-beam-generator
git clone https://github.com/your-org/z-beam-generator.git
cd z-beam-generator

# Check for hidden files
ls -la
```

---

## 🔑 API Configuration Issues

### Environment File Problems

#### Symptom: `.env file not found`
**Error**: `FileNotFoundError: .env`

**Solutions**:
```bash
# Check if .env.example exists
ls -la .env*

# Copy template
cp .env.example .env

# Verify creation
ls -la .env
```

#### Symptom: API keys not loading
**Error**: `❌ No API keys loaded` or `Environment configuration invalid`

**Solutions**:
```bash
# Check .env file content
cat .env

# Expected format:
# DEEPSEEK_API_KEY=sk-your_key_here
# GROK_API_KEY=gsk_your_key_here
# WINSTON_API_KEY=winston-your_key_here

# Verify no extra spaces or quotes
# CORRECT: DEEPSEEK_API_KEY=sk-abc123
# WRONG:   DEEPSEEK_API_KEY = "sk-abc123"

# Check file permissions
ls -la .env  # Should be readable

# Fix permissions if needed
chmod 644 .env
```

### API Key Format Issues

#### Symptom: Invalid API key format
**Error**: `❌ [CLIENT MANAGER] deepseek: Failed - 401 Unauthorized`

**API Key Formats**:
```bash
# DeepSeek: starts with 'sk-'
DEEPSEEK_API_KEY=sk-1234567890abcdef1234567890abcdef

# Grok: starts with 'gsk_'
GROK_API_KEY=gsk_1234567890abcdef1234567890abcdef1234567890abcdef

# Winston.ai: starts with 'winston-'
WINSTON_API_KEY=winston-1234567890abcdef1234567890abcdef
```

**Validation**:
```bash
# Check key format
echo $DEEPSEEK_API_KEY | grep "^sk-"  # Should match
echo $GROK_API_KEY | grep "^gsk_"     # Should match
echo $WINSTON_API_KEY | grep "^winston-"  # Should match
```

### API Provider Issues

#### Symptom: DeepSeek connection fails
**Error**: `❌ [CLIENT MANAGER] deepseek: Failed - None`

**Diagnostic Steps**:
```bash
# Test DeepSeek API directly
python3 -c "
from api.client_manager import test_api_connectivity
test_api_connectivity('deepseek')
"

# Check terminal output for details
python3 scripts/tools/api_terminal_diagnostics.py deepseek
```

**Common Solutions**:
```bash
# 1. Verify API key is active
curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     https://api.deepseek.com/v1/models

# 2. Check account quota/billing
# Visit https://platform.deepseek.com/usage

# 3. Try alternative provider
python3 run.py --provider grok --material "Steel"
```

#### Symptom: Winston.ai SSL errors
**Error**: `[SSL: TLSV1_UNRECOGNIZED_NAME] tlsv1 unrecognized name`

**Status**: ✅ FIXED in current version  
**Solution**: Configuration automatically updated to `https://api.gowinston.ai`

**Verification**:
```bash
# Should work without SSL errors
python3 -c "
from api.client_manager import test_api_connectivity
test_api_connectivity('winston')
"
```

---

## 🌐 Network & Firewall Issues

### Corporate Network Problems

#### Symptom: Connection timeouts
**Error**: `requests.exceptions.ConnectTimeout`

**Solutions**:
```bash
# Check basic connectivity
curl -I https://api.deepseek.com
curl -I https://api.gowinston.ai

# Test with proxy (if required)
export https_proxy=http://proxy.company.com:8080
python3 run.py --test-api

# Configure proxy in requests (add to .env)
HTTPS_PROXY=http://proxy.company.com:8080
```

#### Symptom: SSL certificate verification fails
**Error**: `SSLError: certificate verify failed`

**Solutions**:
```bash
# Check certificate bundle
python3 -c "
import ssl
import certifi
print(certifi.where())
print(ssl.get_default_verify_paths())
"

# Update certificates (macOS)
/Applications/Python\ 3.x/Install\ Certificates.command

# Update certificates (Ubuntu)
sudo apt update && sudo apt install ca-certificates

# Temporary bypass (not recommended for production)
export PYTHONHTTPSVERIFY=0
```

### Firewall Configuration

#### Symptom: Connections blocked by firewall
**Error**: `ConnectionError: Failed to establish connection`

**Required Endpoints**:
```bash
# Allow these domains in firewall:
api.deepseek.com          # Port 443 (HTTPS)
console.groq.com          # Port 443 (HTTPS)  
api.gowinston.ai          # Port 443 (HTTPS)
```

**Testing Connectivity**:
```bash
# Test each endpoint
telnet api.deepseek.com 443
telnet console.groq.com 443
telnet api.gowinston.ai 443

# Should connect successfully
```

---

## 💾 File System Issues

### Permission Problems

#### Symptom: Cannot create output files
**Error**: `PermissionError: [Errno 13] Permission denied: 'content/components/'`

**Solutions**:
```bash
# Check directory permissions
ls -la content/

# Fix permissions
chmod -R 755 content/
sudo chown -R $USER:$USER content/

# Create directories if missing
mkdir -p content/components/{frontmatter,text,table,author,bullets,metatags,jsonld,tags,micro}
```

#### Symptom: Cannot write to logs
**Error**: `PermissionError: logs/z-beam.log`

**Solutions**:
```bash
# Create logs directory
mkdir -p logs

# Fix permissions
chmod 755 logs/
touch logs/z-beam.log
chmod 644 logs/z-beam.log
```

### Disk Space Issues

#### Symptom: No space left on device
**Error**: `OSError: [Errno 28] No space left on device`

**Solutions**:
```bash
# Check disk usage
df -h

# Check directory sizes
du -sh content/
du -sh logs/

# Clean cache files
rm -rf __pycache__
find . -name "*.pyc" -delete

# Clean old log files
find logs/ -name "*.log.*" -mtime +7 -delete
```

---

## 🐛 Application-Specific Issues

### Material Data Problems

#### Symptom: Material not found
**Error**: `❌ Material 'XYZ' not found in materials database`

**Solutions**:
```bash
# List available materials
python3 run.py --list-materials

# Check materials database
python3 -c "
from data.materials import get_all_materials
materials = get_all_materials()
print(f'Total materials: {len(materials)}')
for name in sorted(materials.keys())[:10]:
    print(f'  - {name}')
"

# Use exact material name (case-sensitive)
python3 run.py --material "Stainless Steel"  # Not "stainless steel"
```

#### Symptom: Material data corrupted
**Error**: `ValueError: Invalid material data structure`

**Solutions**:
```bash
# Validate materials database
python3 -c "
import yaml
with open('data/Materials.yaml', 'r') as f:
    data = yaml.safe_load(f)
print('Materials database valid')
"

# Restore from backup if corrupted
cp data/Materials.yaml.backup data/Materials.yaml

# Re-clone repository if needed
git checkout data/Materials.yaml
```

### Component Generation Issues

#### Symptom: Component not found
**Error**: `❌ Component 'xyz' not found`

**Solutions**:
```bash
# List available components
python3 run.py --list-components

# Check component structure
ls -la components/

# Expected components:
# frontmatter, text, table, author, bullets, metatags, jsonld, tags, micro

# Use correct component names
python3 run.py --material "Steel" --components "frontmatter,text"
```

#### Symptom: Frontmatter dependency missing
**Error**: `❌ Author component requires frontmatter data`

**Solutions**:
```bash
# Generate frontmatter first
python3 run.py --material "Steel" --components "frontmatter"

# Then generate dependent components
python3 run.py --material "Steel" --components "author"

# Or generate all at once (frontmatter generated first automatically)
python3 run.py --material "Steel"
```

---

## 🔍 Advanced Diagnostics

### System Information Collection

```bash
# Complete system diagnostic
python3 -c "
import sys
import platform
import os
print(f'Python version: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'Working directory: {os.getcwd()}')
print(f'Python path: {sys.executable}')
"

# Package versions
pip3 list | grep -E "(requests|pyyaml|click)"

# Environment variables
env | grep -E "(DEEPSEEK|GROK|WINSTON)"
```

### Log Analysis

```bash
# Check recent errors
tail -50 logs/z-beam.log | grep "ERROR"

# Check API call history
tail -20 logs/api_calls.log

# Monitor real-time logs
tail -f logs/z-beam.log
```

### Performance Diagnostics

```bash
# Check system resources
top | head -15  # Linux/macOS
htop            # If available

# Check network latency
ping -c 5 api.deepseek.com
ping -c 5 api.gowinston.ai

# Test API response times
time python3 run.py --test-api
```

---

## 📞 Getting Additional Help

### Self-Service Resources

1. **Documentation**: Check [operations/CONTENT_GENERATION.md](../operations/CONTENT_GENERATION.md)
2. **API Issues**: See [api/ERROR_HANDLING.md](../api/ERROR_HANDLING.md)
3. **Installation**: Review [INSTALLATION.md](INSTALLATION.md)

### Diagnostic Tools

```bash
# Run complete system diagnostic
python3 scripts/tools/system_diagnostic.py

# Generate troubleshooting report
python3 scripts/tools/generate_troubleshooting_report.py

# Check environment health
python3 scripts/tools/health_check.py
```

### Support Channels

1. **GitHub Issues**: Report bugs with diagnostic output
2. **Documentation Updates**: Suggest improvements
3. **Community Support**: Join Discord/Slack for real-time help

### When Reporting Issues

Include this information:
```bash
# System information
python3 --version
uname -a  # Linux/macOS
echo $SHELL

# Error output
python3 run.py --check-env 2>&1
python3 run.py --test-api 2>&1

# Log files
tail -50 logs/z-beam.log
```

---

## ✅ Preventive Measures

### Regular Maintenance

```bash
# Weekly checks
python3 run.py --check-env
python3 run.py --test-api

# Monthly updates
pip3 install -r requirements.txt --upgrade
git pull origin main

# Clean old files
find logs/ -name "*.log.*" -mtime +30 -delete
```

### Environment Validation

```bash
# Create validation script
cat > validate_setup.sh << 'EOF'
#!/bin/bash
echo "🔍 Validating Z-Beam Generator setup..."

# Check Python
python3 --version || exit 1

# Check repository
ls run.py >/dev/null 2>&1 || exit 1

# Check environment
python3 run.py --check-env || exit 1

# Check APIs
python3 run.py --test-api || exit 1

echo "✅ Setup validation complete"
EOF

chmod +x validate_setup.sh
./validate_setup.sh
```

---

**🎯 Most Issues Resolved**: 90%+ of setup issues covered  
**⏱️ Average Resolution**: 5-15 minutes per issue  
**📋 Next Steps**: If issue persists, check [api/ERROR_HANDLING.md](../api/ERROR_HANDLING.md) or report on GitHub
