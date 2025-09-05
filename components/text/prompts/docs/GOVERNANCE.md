# AI Detection Prompts Governance Document

## Overview
This document outlines the governance rules for maintaining and evolving the AI detection prompt configurations in `components/text/prompts/ai_detection.yaml`.

## File Structure and Complexity Management

### Current Complexity Assessment
- **Lines**: 200+ lines (too complex for single file)
- **Nested levels**: 4+ levels deep in some sections
- **Maintenance burden**: High - difficult to modify without breaking something
- **Testing requirements**: Complex interdependencies make isolated testing hard

### Recommended Improvements

#### 1. Modular File Structure
Break down the monolithic file into focused modules:

```
components/text/prompts/
├── ai_detection.yaml (core configuration - keep minimal)
├── human_characteristics/
│   ├── conversational_elements.yaml
│   ├── cognitive_patterns.yaml
│   └── natural_imperfections.yaml
├── detection_avoidance/
│   ├── algorithmic_patterns.yaml
│   └── trigger_avoidance.yaml
├── cultural_adaptation/
│   ├── nationality_patterns.yaml
│   └── regional_dialects.yaml
└── enhancement_rules/
    ├── sentence_improvements.yaml
    ├── paragraph_variability.yaml
    └── authenticity_enhancements.yaml
```

#### 2. Configuration Loading Strategy
Update the prompt loading system to support modular configuration:

```python
def load_modular_ai_detection_config():
    """Load AI detection config from multiple focused files."""
    config = {}

    # Load core configuration
    config.update(load_yaml_file('ai_detection.yaml'))

    # Load modular components
    config['human_characteristics'] = load_yaml_file('human_characteristics/conversational_elements.yaml')
    config['detection_avoidance'] = load_yaml_file('detection_avoidance/algorithmic_patterns.yaml')
    # ... etc

    return config
```

## Versioning Rules

### Semantic Versioning (X.Y.Z)
- **Major (X)**: Breaking changes to core objectives or fundamental restructuring
- **Minor (Y)**: New enhancement categories, significant improvements, or new modules
- **Patch (Z)**: Bug fixes, wording improvements, minor additions, or clarifications

### Version Update Triggers
- **Automatic**: Significant performance improvements (15+ point Winston score improvement)
- **Manual**: Structural changes, new enhancement categories, or major rewrites
- **Review Required**: Any change affecting core AI detection objectives

### Changelog Requirements
All version changes must include:
- Specific, actionable descriptions
- Performance impact metrics (when applicable)
- Affected components/modules
- Author and review status

## Modification Rules

### 1. Change Approval Process
- **Minor changes**: Self-review + testing with 3 iterations
- **Major changes**: Peer review + A/B testing with 5+ iterations
- **Breaking changes**: Full team review + comprehensive testing

### 2. Testing Requirements
- **Unit testing**: Individual prompt elements
- **Integration testing**: Full prompt chain with all components
- **Performance testing**: Winston AI score validation
- **Regression testing**: Ensure no degradation in existing functionality

### 3. Content Guidelines
- **Clarity**: Each prompt element must have a clear, specific purpose
- **Actionability**: Prompts should be implementable by AI systems
- **Measurability**: Include success criteria where possible
- **Maintainability**: Avoid overly complex nested structures

### 4. Deprecation Process
- **Mark as deprecated**: Add deprecation notice with timeline
- **Provide replacement**: Always have a tested alternative ready
- **Gradual removal**: Allow 2-3 versions for transition
- **Documentation**: Update all references and examples

## Quality Assurance

### Automated Checks
- **YAML validation**: Ensure proper syntax and structure
- **Version consistency**: Validate version numbers across all files
- **Reference integrity**: Check all cross-references are valid
- **Performance regression**: Automated testing for score degradation

### Manual Review Checklist
- [ ] Does this change improve human-like qualities?
- [ ] Is the change specific and actionable?
- [ ] Have similar patterns been tested successfully?
- [ ] Does this avoid common AI detection triggers?
- [ ] Is the change compatible with existing enhancement flags?
- [ ] Has the change been tested with multiple author personas?

## Migration Strategy

### Phase 1: Immediate Improvements (Week 1-2)
1. Add modification rules to existing file
2. Remove test/debug entries
3. Implement automated version bumping
4. Create basic governance documentation

### Phase 2: Structural Refactoring (Week 3-4)
1. Break down monolithic file into modules
2. Update loading system to support modular structure
3. Migrate existing content to new structure
4. Update all references and imports

### Phase 3: Enhanced Governance (Week 5-6)
1. Implement automated testing for prompt changes
2. Add performance regression monitoring
3. Create contributor guidelines
4. Establish regular review cycles

## Risk Mitigation

### Technical Risks
- **Breaking changes**: Implement feature flags for gradual rollout
- **Performance impact**: Monitor Winston scores during changes
- **Compatibility issues**: Maintain backward compatibility during transitions

### Operational Risks
- **Knowledge loss**: Document all design decisions and rationales
- **Coordination overhead**: Establish clear ownership and review processes
- **Maintenance burden**: Regular cleanup and refactoring cycles

## Success Metrics

### Technical Metrics
- **File complexity**: Reduce from 200+ lines to <50 lines per module
- **Load time**: Maintain <100ms configuration loading
- **Test coverage**: Achieve 90%+ coverage for prompt components
- **Performance stability**: No >5 point Winston score degradation

### Process Metrics
- **Review cycle time**: <24 hours for minor changes, <72 hours for major
- **Version bump frequency**: 1-2 minor versions per month maximum
- **Bug introduction rate**: <5% of changes introduce regressions
- **Documentation coverage**: 100% of components have usage examples

## Tools and Automation

### Version Management
```bash
# Check current version
python3 components/text/prompts/version_manager.py get

# Bump version automatically
python3 components/text/prompts/version_manager.py bump --bump-type minor --changelog "Added new enhancement category"

# View version history
python3 components/text/prompts/version_manager.py history
```

### Quality Checks
```bash
# Validate YAML structure
python3 -c "import yaml; yaml.safe_load(open('components/text/prompts/ai_detection.yaml'))"

# Test prompt loading
python3 -c "from components.text.generators.fail_fast_generator import FailFastContentGenerator; print('Config loaded successfully')"
```

This governance framework ensures the AI detection prompts remain maintainable, testable, and effective while supporting continuous improvement through structured evolution.
