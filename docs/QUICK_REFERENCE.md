# Quick Reference for AI Assistants

**🤖 Optimized for AI assistant navigation and problem resolution**

---

## 🎯 Most Common User Questions → Direct Solutions

### "API not working" / "Connection failed"
**→ Immediate Response**: Check [API Error Handling](api/ERROR_HANDLING.md#winston-ssl-issues)
**→ Quick Fix**: `python3 scripts/tools/api_terminal_diagnostics.py winston`
**→ Root Cause**: Likely Winston SSL error - endpoint changed to `api.gowinston.ai`

### "Content incomplete" / "Text cuts off"
**→ Immediate Response**: API failure during generation
**→ Quick Fix**: `python3 run.py --material "MaterialName" --components "text"`
**→ Root Cause**: Winston API timeout - check [Content Impact Analysis](api/ERROR_HANDLING.md#content-impact)

### "How do I set up API keys?"
**→ Immediate Response**: [API Configuration Guide](setup/API_CONFIGURATION.md)
**→ Quick Fix**: Copy `.env.example` to `.env` and add keys
**→ Validation**: `python3 run.py --check-env`

### "Winston API SSL error"
**→ Immediate Response**: Known SSL certificate issue
**→ Quick Fix**: Configuration updated to use `https://api.gowinston.ai`
**→ Details**: [SSL Error Resolution](api/ERROR_HANDLING.md#winston-ssl-errors)

### "How to generate content?"
**→ Immediate Response**: [Content Generation Guide](operations/CONTENT_GENERATION.md)
**→ Quick Fix**: `python3 run.py --material "Steel"`
**→ Batch**: `python3 run.py` (generates all materials)

## 📍 File Location Quick Map for AI

### User needs setup help → Look in:
- `setup/API_CONFIGURATION.md` - API keys and providers
- `setup/TROUBLESHOOTING.md` - Common setup issues
- `README.md` - Basic installation

### User has API problems → Look in:
- `api/ERROR_HANDLING.md` - Error patterns and terminal diagnostics
- `API_SETUP.md` - Provider configuration (legacy, see api/ directory)
- `API_TERMINAL_DIAGNOSTICS.md` - Terminal output analysis (legacy)

### User needs component help → Look in:
- `components/text/docs/README.md` - Text generation (comprehensive)
- `components/frontmatter/README.md` - YAML frontmatter
- `components/[component]/README.md` - Component-specific guides

### User has generation issues → Look in:
- `operations/CONTENT_GENERATION.md` - How content generation works
- `BATCH_GENERATION_PRODUCTION_READY.md` - Batch operations (legacy)
- `components/text/docs/CONTENT_GENERATION_ARCHITECTURE.md` - Detailed architecture

### User needs troubleshooting → Look in:
- `api/ERROR_HANDLING.md` - API and connection issues
- `setup/TROUBLESHOOTING.md` - Setup and configuration issues
- `components/[component]/README.md` - Component-specific issues

## 🔧 Essential Commands for AI to Recommend

### System Health Checks
```bash
# Check overall system health
python3 run.py --check-env

# Test all API connections
python3 run.py --test-api

# Diagnose specific API issues
python3 scripts/tools/api_terminal_diagnostics.py winston
```

### Content Generation
```bash
# Generate all materials (batch mode)
python3 run.py

# Generate specific material
python3 run.py --material "Steel"

# Generate specific components only
python3 run.py --material "Copper" --components "frontmatter,text"

# Clean and regenerate
python3 run.py --clean
```

### Troubleshooting
```bash
# Validate environment
python3 run.py --check-env

# Test API connectivity with detailed output
python3 -c "from api.client_manager import test_api_connectivity; test_api_connectivity('winston')"

# Check for incomplete content
find content/components -name "*.md" -exec grep -l "before significant" {} \;
```

## 🚨 Critical Known Issues (AI Should Be Aware Of)

### 1. Winston API SSL Certificate Issue
**Symptom**: `[SSL: TLSV1_UNRECOGNIZED_NAME] tlsv1 unrecognized name`
**Status**: FIXED - Updated to `https://api.gowinston.ai`
**Impact**: Caused content generation to cut off mid-sentence
**Files Affected**: Any text component generation using Winston
**Solution**: Configuration already updated in `run.py`

### 2. Nested YAML Property Generation Bug
**Symptom**: Properties like `name: {name: "Value"}` instead of `name: "Value"`
**Status**: FIXED - Tool created to detect and correct
**Impact**: Blocked TypeScript builds due to malformed YAML
**Tool**: `scripts/tools/fix_nested_yaml_properties.py`
**Files Fixed**: `phenolic-resin-composites-laser-cleaning.md`, `thermoplastic-elastomer-laser-cleaning.md`

### 3. Terminal Output Required for API Diagnostics
**Issue**: API response objects show `error: None` but terminal has actual errors
**Solution**: Always use `get_terminal_output()` after API tests
**Tool**: `scripts/tools/api_terminal_diagnostics.py`
**Documentation**: [Terminal Diagnostics](api/ERROR_HANDLING.md#terminal-reading)

## 📋 AI Assistant Response Patterns

### When User Reports Error Messages
1. **Ask for terminal output**: "Can you run this command and share the terminal output?"
2. **Use diagnostic tools**: Recommend `api_terminal_diagnostics.py`
3. **Check known issues**: Reference the critical issues above
4. **Point to specific docs**: Use the file location map above

### When User Needs Setup Help
1. **Start with environment check**: `python3 run.py --check-env`
2. **Guide through API setup**: Point to `setup/API_CONFIGURATION.md`
3. **Validate with tests**: `python3 run.py --test-api`
4. **Provide quick commands**: Use the essential commands above

### When User Has Generation Issues
1. **Check API connectivity first**: Use diagnostic tools
2. **Identify component type**: Direct to appropriate component docs
3. **Check for known patterns**: Reference content impact issues
4. **Provide regeneration commands**: Use content generation commands

## 🗺️ Documentation Navigation for AI

### Primary Entry Points
1. **This file** (`docs/QUICK_REFERENCE.md`) - For immediate problem resolution
2. **Index** (`docs/INDEX.md`) - For comprehensive navigation
3. **Component docs** (`components/[name]/README.md`) - For component-specific help

### Legacy Files (Still Valid but Being Reorganized)
- `API_SETUP.md` - Moving to `api/PROVIDERS.md`
- `API_TERMINAL_DIAGNOSTICS.md` - Moving to `api/ERROR_HANDLING.md`
- `BATCH_GENERATION_PRODUCTION_READY.md` - Moving to `operations/BATCH_OPERATIONS.md`

### File Naming Patterns
- `README.md` - Overview of directory/component
- `[TOPIC].md` - Specific topic documentation
- `[COMPONENT]/README.md` - Component-specific guide
- `[CATEGORY]/[SPECIFIC].md` - Categorized documentation

## 🎯 AI Assistant Success Checklist

When helping users, ensure:
- [ ] Provided specific file references with exact paths
- [ ] Recommended appropriate diagnostic commands
- [ ] Checked against known critical issues
- [ ] Offered terminal output analysis when relevant
- [ ] Pointed to both immediate fixes and comprehensive documentation

---

**📅 Last Updated**: September 11, 2025
**🤖 AI Optimization**: This document is structured specifically for AI assistant parsing and quick reference
**📍 Location**: Primary quick reference for all AI assistants working with Z-Beam Generator
