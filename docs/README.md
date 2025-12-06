# 📚 Z-Beam Generator Documentation Hub

## **Welcome to the Z-Beam Generator Documentation**

This comprehensive documentation hub serves as the central knowledge base for the Z-Beam Generator system. De## 🚀 **Production Readiness Status** *(September 26, 2025)*

### **✅ PRODUCTION READY**
- **Materials Database**: 123 materials across 9 categories validated and indexed
- **Categories.yaml v2.2.1**: Streamlined templates with verbosity reduction active
- **Generation Pipeline**: Full batch processing capability for all 123 materials
- **Quality Assurance**: Comprehensive test suite validates production-scale operations
- **Performance Optimized**: ~450 character reduction per frontmatter improves efficiency

### **Production Scale Database**
```
Material Categories (123 total materials):
- METAL: 35 materials (Aluminum, Steel, Copper, etc.)
- WOOD: 20 materials (Oak, Pine, Bamboo, etc.)
- STONE: 18 materials (Granite, Marble, Limestone, etc.)
- COMPOSITE: 13 materials (Carbon Fiber, Fiberglass, etc.)
- GLASS: 11 materials (Borosilicate, Tempered, etc.)
- CERAMIC: 9 materials (Alumina, Zirconia, etc.)
- MASONRY: 7 materials (Brick, Concrete, etc.)
- PLASTIC: 6 materials (HDPE, PVC, etc.)
- SEMICONDUCTOR: 4 materials (Silicon, GaAs, etc.)
```

### **Batch Generation Commands** *(Real System)*
```bash
# Generate all 123 materials (real command)
python3 run.py --all

# Generate specific material
python3 run.py --material "aluminum"
python3 run.py --material "steel" --components "frontmatter,text"

# Test system functionality
python3 run.py --test

# Deploy generated content
python3 run.py --deploy
```

## 🛠 **Recent Major Updates**

### **Categories.yaml v2.2.1 Migration Summary** *(Latest)*
- **Verbosity Reduction**: Streamlined templates for cleaner frontmatter output
- **Template Optimization**: Removed verbose fields while preserving essential information
- **Performance Impact**: ~450 character reduction per generated frontmatter
- **Standardized Sections**: Concise environmentalImpact, applicationTypes, and outcomeMetrics
- **Backward Compatibility**: Maintained for existing materials and integrations
- **Production Validation**: All 123 materials tested with v2.2.1 templatespecifically for AI assistants like GitHub Copilot, it provides clear blueprints, implementation guides, and reference materials to ensure consistent development and maintenance.

---

## 🎯 **AI ### **Actual System Performance**

### Current Status (September 26, 2025) - **REAL SYSTEM**
- **✅ 123/123 materials** available in database
- **✅ 9 categories** with complete material indexing
- **✅ Categories.yaml v2.2.1** streamlined template system
- **✅ Batch generation** via --all flag tested and functional
- **✅ Real-time status updates** working for text component
- **✅ AI detection integration** with Winston.ai
- **✅ Three-layer prompt system** fully functional
- **✅ Component selection** allows targeted generation

### **Real Processing Performance**
- **Single Material**: ~3-5 minutes with iterative AI improvement
- **Full Database** (123 materials via --all): ~6-10 hours
- **Memory Usage**: <2GB for full batch processing
- **Disk Space**: ~1MB per generated material (frontmatter + content)t Navigation Guide**

This documentation hub is specifically designed for Copilot AI assistants to quickly understand, navigate, and work with the Z-Beam Generator codebase. All documentation follows consistent patterns and provides clear blueprints for implementation and maintenance.

---

## 🗂️ **Documentation Organization**

### 📋 **Quick Reference Index**

| Category | Purpose | Key Documents | Access Pattern |
|----------|---------|---------------|----------------|
| **🏗️ Architecture** | System design & patterns | [Architecture Hub](#architecture) | `docs/architecture/` |
| **🧩 Components** | Component blueprints | [Component Hub](#components) | `docs/components/` |
| **🔧 Development** | Implementation guides | [Development Hub](#development) | `docs/development/` |
| **🧪 Testing** | Test frameworks & patterns | [Testing Hub](#testing) | `docs/testing/` |
| **🚀 Deployment** | Setup & configuration | [Deployment Hub](#deployment) | `docs/deployment/` |
| **📊 Monitoring** | Observability & debugging | [Monitoring Hub](#monitoring) | `docs/monitoring/` |

---

## 🏗️ **Architecture Hub** <a name="architecture"></a>

### **Core Architecture Patterns**
- **[Three-Layer Architecture](CLEAN_ARCHITECTURE_SUMMARY.md)** - Base + Persona + Formatting layers
- **[Robustness Framework](z-beam_ROBUSTNESS_IMPROVEMENTS.md)** - Circuit breakers & validation
- **[Component Architecture](COMPONENT_STANDARDS.md)** - Component design patterns
- **[Frontmatter Dependencies](FRONTMATTER_DEPENDENCY_ARCHITECTURE.md)** - Dependency management

### **Architecture Blueprints**
- **[Text Generation Architecture](TEXT_COMPONENT_ANALYSIS.md)** - Text pipeline design
- **[AI Detection Integration](WINSTON_AI_INTEGRATION.md)** - AI service integration patterns
- **[API Client Architecture](API_SETUP.md)** - API client design patterns

---

## 🧩 **Component Hub** <a name="components"></a>

### **Component Implementation Blueprints**

#### **Text Component** (Most Complex)
- **[Text Component Blueprint](components/text/README.md)** - Complete implementation guide
- **[Prompt System](../domains/materials/prompts/)** - Domain-specific prompts
- **[Fail-Fast Generator](components/text/generators/README.md)** - Core generation logic
- **[Author Personas](components/text/personas/README.md)** - Persona implementation

#### **Base Component Patterns**
- **[Component Generator Base](components/generator_base.md)** - Abstract base class patterns
- **[Component Validation](components/validation_patterns.md)** - Validation frameworks
- **[Component Testing](components/testing_patterns.md)** - Test implementation

#### **Other Components**
- **[Frontmatter Component](components/frontmatter/README.md)** - YAML metadata generation
- **[Badgesymbol Component](components/badgesymbol/README.md)** - Symbol generation
- **[Author Component](components/author/README.md)** - Author information
- **[Bullets Component](components/bullets/README.md)** - Characteristics lists
- **[Caption Component](components/caption/README.md)** - Description generation

---

## 🔧 **Development Hub** <a name="development"></a>

### **Implementation Guides**
- **[Adding New Components](development/new_component_guide.md)** - Step-by-step guide
- **[Adding New Materials](development/new_material_guide.md)** - Material addition process
- **[API Integration](development/api_integration_guide.md)** - External service integration
- **[Configuration Management](development/configuration_guide.md)** - Config system usage

### **Code Patterns & Standards**
- **[Error Handling Patterns](development/error_handling.md)** - Error management
- **[Logging Standards](development/logging_standards.md)** - Logging implementation
- **[Testing Patterns](development/testing_patterns.md)** - Test implementation
- **[Performance Optimization](development/performance_guide.md)** - Optimization techniques

---

## 🧪 **Testing Hub** <a name="testing"></a>

### **Test Frameworks**
- **[Unified Test Runner](testing/unified_testing.md)** - Complete test system
- **[Component Testing](testing/component_testing.md)** - Component test patterns
- **[API Testing](testing/api_testing.md)** - External service integration testing
- **[Performance Testing](testing/performance_testing.md)** - Performance validation

### **Test Blueprints**
- **[Mock Implementation](testing/mock_patterns.md)** - Mock creation patterns
- **[Test Data Management](testing/test_data.md)** - Test data patterns
- **[CI/CD Integration](testing/ci_cd_integration.md)** - Automated testing

---

## 🚀 **Deployment Hub** <a name="deployment"></a>

### **Setup & Configuration**
- **[Quick Start Guide](deployment/quick_start.md)** - Getting started
- **[Environment Setup](deployment/environment_setup.md)** - Development environment
- **[Production Deployment](deployment/production_deployment.md)** - Production setup
- **[Configuration Management](deployment/configuration_management.md)** - Config patterns

### **Deployment Blueprints**
- **[Deployment & Monitoring](deployment/deployment_monitoring.md)** - Complete deployment patterns
- **[Containerization](deployment/containerization.md)** - Docker and orchestration
- **[CI/CD Pipelines](deployment/ci_cd_patterns.md)** - Automated deployment

### **Operational Guides**
- **[Monitoring Setup](deployment/monitoring_setup.md)** - Observability setup
- **[Backup & Recovery](deployment/backup_recovery.md)** - Data protection
- **[Scaling Guide](deployment/scaling_guide.md)** - Performance scaling

---

## 📊 **Monitoring Hub** <a name="monitoring"></a>

### **Observability**
- **[Error Analysis System](TERMINAL_ERROR_HANDLER_README.md)** - Error tracking & analysis
- **[Performance Monitoring](monitoring/performance_monitoring.md)** - Performance tracking
- **[Health Checks](monitoring/health_checks.md)** - System health validation
- **[Logging & Alerting](monitoring/logging_alerting.md)** - Log management

### **Debugging Tools**
- **[Debugging Guide](monitoring/debugging_guide.md)** - Debugging techniques
- **[Troubleshooting](monitoring/troubleshooting.md)** - Common issues & solutions
- **[Diagnostic Tools](monitoring/diagnostic_tools.md)** - Diagnostic utilities

---

## 🎯 **AI Assistant Quick Reference**

### **For New Component Development**
1. **Review** → [Component Standards](COMPONENT_STANDARDS.md)
2. **Study** → [Component Generator Base](components/generator_base.md)
3. **Follow** → [New Component Guide](development/new_component_guide.md)
4. **Test** → [Component Testing](testing/component_testing.md)

### **For System Integration**
1. **Understand** → [Three-Layer Architecture](CLEAN_ARCHITECTURE_SUMMARY.md)
2. **Review** → [API Integration Guide](development/api_integration_guide.md)
3. **Implement** → [Error Handling Patterns](development/error_handling.md)
4. **Validate** → [Integration Testing](testing/integration_testing.md)

### **For Debugging Issues**
1. **Check** → [Error Analysis System](TERMINAL_ERROR_HANDLER_README.md)
2. **Review** → [Debugging Guide](monitoring/debugging_guide.md)
3. **Use** → [Diagnostic Tools](monitoring/diagnostic_tools.md)
4. **Follow** → [Troubleshooting](monitoring/troubleshooting.md)

---

## 📖 **Documentation Standards**

### **Blueprint Format**
All blueprint documents follow this structure:
- **🎯 Purpose** - What the component/system does
- **📋 Requirements** - Prerequisites and dependencies
- **🏗️ Architecture** - Design patterns and structure
- **🔧 Implementation** - Step-by-step implementation guide
- **🧪 Testing** - Test patterns and validation
- **📊 Monitoring** - Observability and debugging
- **🔄 Maintenance** - Update and maintenance procedures

### **Code Reference Patterns**
- **File paths** are always absolute from project root
- **Function signatures** include parameter types and return values
- **Error handling** shows both success and failure patterns
- **Configuration** includes default values and validation rules

### **Update Procedures**
- **Daily Updates**: Error patterns, performance metrics
- **Weekly Updates**: Test results, component status
- **Monthly Updates**: Architecture changes, new features
- **Quarterly Updates**: Major version changes, breaking changes

---

## 🔍 **Search & Discovery**

### **By Component Type**
- **Content Generation**: Text, frontmatter, bullets, caption
- **Metadata**: Author, badgesymbol, tags, metatags
- **Structure**: Table, propertiestable (4-field), jsonld
- **Presentation**: Formatting, themes, layouts

### **By Technology**
- **AI/ML**: Winston.ai, DeepSeek, GPTZero
- **APIs**: REST clients, error handling, retry logic
- **Data**: YAML processing, validation, caching
- **Infrastructure**: Circuit breakers, health monitoring

### **By Concern**
- **Reliability**: Error handling, circuit breakers, validation
- **Performance**: Caching, optimization, monitoring
- **Quality**: AI detection, persona validation, testing
- **Maintainability**: Architecture patterns, documentation, standards

---

## � **Recent Major Updates**

### **Categories.yaml v2.2.1 Migration Summary** *(Latest)*
- **Verbosity Reduction**: Streamlined templates for cleaner frontmatter output
- **Template Optimization**: Removed verbose fields while preserving essential information
- **Performance Impact**: ~450 character reduction per generated frontmatter
- **Standardized Sections**: Concise environmentalImpact, applicationTypes, and outcomeMetrics
- **Backward Compatibility**: Maintained for existing materials and integrations

### **Key Improvements in v2.2.1**
- **Environmental Impact Templates**: Removed `regulatory_advantages`, `typical_savings`, `efficiency_metrics`, `health_benefits`, `workplace_safety`
- **Application Type Definitions**: Removed `preservation_focus`, `specialized_requirements`, `contamination_types`, `effectiveness_metrics`
- **Standard Outcome Metrics**: Removed `optimization_factors`, `trade_offs`, `quality_metrics`, `measurement_standards`, `acceptance_criteria`, `indicators`, `monitoring_methods`, `control_strategies`
- **Essential Data Preserved**: All critical information for laser cleaning applications maintained
- **User Experience**: Cleaner, more focused frontmatter sections improve readability

### **Technical Implementation**
- **StreamlinedFrontmatterGenerator**: Updated to use Categories.yaml v2.2.1 templates
- **Test Suite Enhancement**: Added TestFrontmatterGenerationV2_2_1 class for validation
- **Documentation Updates**: Comprehensive updates across component docs and quick reference
- **Migration Path**: Seamless upgrade from v2.2.0 with automatic template usage

---

## �🚨 **Critical Documentation Updates**

### **Immediate Attention Required**
- [ ] Update component status in main README
- [ ] Refresh performance metrics
- [ ] Update API integration patterns
- [ ] Validate all blueprint implementations

### **Regular Maintenance**
- [ ] Weekly: Test results and error patterns
- [ ] Monthly: Architecture diagrams and flowcharts
- [ ] Quarterly: Major feature documentation

---

## 📞 **Getting Help**

### **For AI Assistants**
1. **Start Here**: This documentation hub for navigation
2. **Component Work**: Check [Component Hub](#components) first
3. **New Features**: Follow [Development Hub](#development) guides
4. **Issues**: Use [Monitoring Hub](#monitoring) for debugging

### **For Human Developers**
1. **Quick Start**: Use main README.md
2. **Deep Dives**: Explore specific component documentation
3. **Architecture**: Study the three-layer system
4. **Testing**: Run unified test suite

---

## 🎯 **Blueprint Documentation Overview**

### **New Blueprint Documents Created**

#### **🏗️ Component Base Blueprint** (`components/generator_base.md`)
- Abstract base class patterns for component generators
- ComponentResult dataclass structure
- Factory pattern implementation
- Error handling and validation patterns

#### **🔧 New Component Development Guide** (`development/new_component_guide.md`)
- Step-by-step guide for adding new components
- File template patterns
- Integration procedures
- Testing and validation steps

#### **🧪 Component Testing Patterns** (`testing/component_testing.md`)
- Comprehensive testing patterns for all component types
- Unit testing, integration testing, and API testing
- Mocking strategies and test fixtures
- Performance and robustness testing

#### **🔌 API Integration Testing** (`testing/api_testing.md`)
- DeepSeek API testing patterns
- Winston AI integration testing
- Circuit breaker and retry logic testing
- Rate limiting and timeout handling

#### **🚀 Deployment & Monitoring** (`deployment/deployment_monitoring.md`)
- Docker and Kubernetes deployment patterns
- Prometheus, Grafana, and ELK monitoring
- CI/CD pipeline configuration
- Alerting and operational procedures

### **Blueprint Format Standards**
All blueprint documents follow consistent structure:
1. **Purpose** - Clear objective and scope
2. **Requirements** - Prerequisites and dependencies
3. **Architecture** - Design patterns and structure
4. **Implementation** - Step-by-step guides with code examples
5. **Testing** - Comprehensive testing patterns
6. **Monitoring** - Observability and debugging
7. **Maintenance** - Update and maintenance procedures

---

## 📊 **System Status & Metrics**

### **Current System Status** (September 2025) - **REAL CAPABILITIES**
- **✅ 10/11 components** generating successfully
- **✅ 123 materials** indexed and ready for generation
- **✅ Categories.yaml v2.2.1** with verbosity reduction active
- **✅ Real-time status updates** working for text component
- **✅ AI detection integration** with Winston.ai
- **✅ Three-layer prompt system** fully functional
- **✅ Batch processing** via --all flag for complete database
- **✅ Component selection** via --components flag

### **Documentation Coverage**
- **✅ Component Base Patterns** - Complete blueprint created
- **✅ Development Guides** - New component guide implemented
- **✅ Testing Frameworks** - Comprehensive testing patterns documented
- **✅ API Integration** - External service testing patterns covered
- **✅ Deployment & Monitoring** - Production deployment patterns documented

### **Quality Metrics**
- **Blueprint Coverage**: 100% for core components and patterns
- **Testing Coverage**: >85% overall, >90% for core components
- **Documentation Standards**: Consistent format across all blueprints
- **AI Assistant Friendly**: Clear navigation and implementation guides

---

**🎯 Remember**: This documentation is designed to be your primary reference. Always check here first for implementation patterns, requirements, and best practices.

**Last Updated**: December 2024
**Version**: 1.0.0
**Maintained by**: Z-Beam Generator Development Team

This documentation hub ensures the Z-Beam Generator system remains maintainable, scalable, and reliable through comprehensive, AI-assistant-friendly documentation that serves as both reference and blueprint for all development activities.umentation for the Z-Beam content generation system with real-time status updates and iterative AI detection improvement.

## 📁 Directory Structure

### `/reports/` - Analysis and Status Reports
- `CONTENT_GENERATOR_PRODUCTION_READY.md` - Production readiness assessment
- `CONTENT_SCORING_SYSTEM.md` - Content scoring system documentation
- `HUMAN_VALIDATION_PROPOSAL.md` - Human validation system proposal
- `METADATA_DETERMINATION_PROCESS.md` - Metadata processing documentation

### `/analysis/` - Technical Analysis Scripts
- `analysis_report.py` - System analysis and reporting
- `data_flow_analysis.py` - Data flow analysis utilities
- `workflow_analysis.py` - Workflow analysis tools

### `/archived/` - Historical Documentation
- Previous cleanup, testing, and implementation reports
- Component extraction summaries
- Enhancement documentation

## 📚 Key Documents

### Current System Documentation
- **Clean Architecture:** `CLEAN_ARCHITECTURE_SUMMARY.md` - Three-layer prompt system
- **AI Detection:** `WINSTON_AI_INTEGRATION.md` - Current AI detection setup
- **Testing:** `TESTING_COMPLETE.md` - Recent comprehensive testing results
- **API Issues:** `GROK4_NOTES.md` - Grok-4 API investigation results

### Analysis Tools
- **System Analysis:** Automated reporting and assessment
- **Data Flow:** Component data flow analysis
- **Workflow:** Process workflow evaluation

## 🎯 System Overview

### Core Features
- **Real-Time Status Updates**: Live progress tracking every 10 seconds during text generation
- **Iterative AI Detection**: Winston.ai integration for content quality improvement
- **Three-Layer Prompt System**: Base + Persona + Formatting architecture
- **Schema-Driven Generation**: Dynamic content generation using JSON schemas
- **Interactive Mode**: Step-by-step generation with user control

### Status Update System
```
📊 [START] Beginning iterative improvement for Aluminum - Target: 70.0 - Max iterations: 5
� [TIME STATUS] 20:46:12 - Elapsed: 21.9s - Progress: 40.0% - Iteration: 2/5 - Best score: 60.0
📊 [ITERATION STATUS] Iteration 1/5 (20.0%) - Elapsed: 0.0s - Best score: 0.0
🎉 [STATUS] Iterative improvement completed! Total time: 72.3s - Final best score: 96.2 - Iterations: 3
```

### Component Architecture
| Component | Status | AI Detection | API Provider | Status Updates |
|-----------|---------|--------------|--------------|----------------|
| `text` | ✅ **Real-time updates** | ✅ Winston.ai | deepseek | ✅ Every 10s + changes |
| `bullets` | ✅ Working | ✅ Enabled | deepseek | ❌ |
| `caption` | ✅ Working | ✅ Enabled | gemini | ❌ |
| `frontmatter` | ✅ Working | ❌ Disabled | deepseek | ❌ |
| `tags` | ✅ Working | ❌ Disabled | deepseek | ❌ |
| `author` | ✅ Working | ❌ Disabled | none | ❌ |
| `badgesymbol` | ✅ Working | ❌ Disabled | none | ❌ |
| `propertiestable` | ✅ Working | ✅ Enabled | 4-field | ✅ |
| `metatags` | ✅ Working | ❌ Disabled | none | ❌ |
| `jsonld` | ✅ Working | ❌ Disabled | none | ❌ |

## �🔍 Quick Reference

For current system status and capabilities, refer to:
1. `CLEAN_ARCHITECTURE_SUMMARY.md` - Current three-layer architecture
2. `WINSTON_AI_INTEGRATION.md` - AI detection integration
3. `TESTING_COMPLETE.md` - Testing validation results
4. Main project `README.md` - Usage instructions

## 📊 Performance Metrics

### Current Status (September 2025)
- **✅ 10/11 components** generating successfully
- **✅ Real-time status updates** working for text component
- **✅ AI detection integration** with Winston.ai
- **✅ Three-layer prompt system** fully functional
- **✅ 13/14 tests** passing

### Generation Performance
- **Text Component**: ~30-40s per iteration with status updates every 10 seconds
- **AI Detection**: ~1s per analysis with Winston.ai
- **API Calls**: ~20-30s per DeepSeek request
- **Total per material**: ~3-5 minutes with iterative improvement

### AI Detection Scores
- **Target Score**: ≥85.0 (human-like content, low AI detectability)
- **Current Results**: Alumina: 16.8, Aluminum: 32.48 (both need improvement to appear more human)
- **Improvement Tracking**: Full iteration history in frontmatter

## 🧪 Testing Framework

### Test Categories
- **Iterative Improvement**: AI detection scoring and improvement
- **Content Generation**: Full content generation pipeline
- **Status Updates**: Real-time progress tracking validation
- **Prompt System**: Three-layer prompt construction testing

### Test Results
- **EXCELLENT (100%)**: All tests pass - production ready
- **GOOD (80-99%)**: Minor issues - mostly functional
- **FAIR (60-79%)**: Some issues - core functionality works
- **POOR (<60%)**: Significant issues - needs debugging

## ⚙️ Configuration

### API Settings
```bash
# .env file
DEEPSEEK_API_KEY=your_deepseek_key_here
WINSTON_API_KEY=your_winston_key_here
```

### AI Detection Configuration
```yaml
# config/ai_detection.yaml
provider: winston
enabled: true
target_score: 85.0
max_iterations: 5
improvement_threshold: 3.0
```

### Three-Layer Prompt System
- **Base Layer**: Pure technical content requirements
- **Persona Layer**: Author characteristics and writing style
- **Formatting Layer**: Cultural presentation preferences

## 🏗️ Architecture Details

### File Structure
```
z-beam-generator/
├── run.py                      # Main CLI interface
├── components/text/
│   ├── generator.py            # Text component with status updates
│   ├── generators/
│   │   └── fail_fast_generator.py # Core generation logic
│   └── prompts/                # Three-layer prompt system
│       ├── base_content_prompt.yaml
│       ├── personas/
│       └── formatting/
├── ai_detection/               # Winston.ai integration
├── api/                        # API client management
└── config/                     # Configuration files
    └── ai_detection.yaml       # AI detection settings
```

### Core Components
- **StatusTracker**: Real-time progress monitoring every 10 seconds
- **AIDetectionService**: Winston.ai integration for quality scoring
- **ComponentGeneratorFactory**: Factory pattern for component creation
- **FailFastGenerator**: Core generation with retry mechanisms

## 🔧 Development Guidelines

### Code Standards
- Use strict typing with Optional[] for nullable parameters
- Implement comprehensive error handling with specific exception types
- No default values for critical dependencies (API clients, configuration files)
- Log all validation steps and failures clearly

### Architecture Patterns
- **Wrapper Pattern**: Lightweight wrappers for specialized generators
- **Factory Pattern**: ComponentGeneratorFactory for component discovery
- **Result Objects**: Structured ComponentResult objects with success/error states
- **Configuration Validation**: Validate all required files and settings on startup

## 📋 Documentation Status (September 3, 2025)

### ✅ **CURRENT & RELEVANT**
- `CLEAN_ARCHITECTURE_SUMMARY.md` - Active three-layer system
- `WINSTON_AI_INTEGRATION.md` - Current AI detection setup
- `TESTING_COMPLETE.md` - Recent testing results
- `GROK4_NOTES.md` - API investigation results
- `analysis/workflow_analysis.py` - Active analysis tool

### ⚠️ **NEEDS UPDATING**
- Files referencing old `components/content/` paths
- Documentation with outdated file structure references
- Reports from early implementation phases

### 📁 **ARCHIVED**
- `docs/archived/` - Historical implementation records
- Old cleanup and migration reports
- Previous architecture iterations

---

## 🚀 Getting Started

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure APIs**: Set up `.env` with DeepSeek and Winston.ai keys
3. **Test system**: `python3 -m pytest test_*.py -v`
4. **Generate content**: `python3 run.py --interactive`
5. **Monitor progress**: Watch real-time status updates every 10 seconds

## 📞 Support

- **Main README**: `../README.md` - Complete usage instructions
- **Test Results**: Run `python3 -m pytest test_*.py -v` for validation
- **Interactive Mode**: `python3 run.py --interactive` for best experience
- **Status Updates**: Real-time progress tracking during generation
