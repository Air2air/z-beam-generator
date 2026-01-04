# Collapsible Normalization Implementation Plan
**Date:** January 3, 2026  
**Scope:** expert_answers & prevention sections  
**Schema:** docs/COLLAPSIBLE_NORMALIZATION_SCHEMA-2.md  
**Status:** Ready for Implementation

---

## 🎯 Implementation Overview

Based on analysis of existing data structures, we need to implement TWO new collapsible sections:

| Section | Source Data | Domain | Status |
|---------|-------------|--------|--------|
| **industry_applications** | applications field | Materials | ✅ COMPLETE (Jan 3, 2026) |
| **expert_answers** | faq field | Materials | 🟡 DATA FOUND - Needs Transformation |
| **prevention** | challenges field | Settings | 🟡 DATA FOUND - Needs Transformation |

---

## 📊 Data Discovery Summary

### Materials.yaml - FAQ → expert_answers
```yaml
# CURRENT STRUCTURE (Materials.yaml)
faq:
- question: "How does laser cleaning safely remove dirt from alabaster sculptures?"
  answer: "Laser cleaning employs precise, non-contact ablation..."
  topic_keyword: "safely remove dirt"
  topic_statement: "Precise non-contact ablation"
- question: "..."
  answer: "..."
  ...

# REQUIRED TRANSFORMATION → expert_answers collapsible format
expert_answers:
  presentation: collapsible
  sectionMetadata:
    section_title: "Expert Q&A"
    section_description: "Common questions answered by laser cleaning specialists"
    icon: "user-tie"
    order: 4
  items:
  - question: "How does laser cleaning safely remove dirt from alabaster sculptures?"
    answer: "Laser cleaning employs precise, non-contact ablation..."
    expert:
      name: "Todd Dunning"  # From author field
      credentials: "Technical authority, Certified Laser Safety Officer (CLSO)"
    severity: "medium"
    acceptedAnswer: true
    category: "safely remove dirt"  # From topic_keyword
  options:
    autoOpenFirst: true
    autoOpenAccepted: true
    sortBy: "severity"
```

**Data Status:**
- ✅ 153 materials have `faq` field (list of 4-8 Q&A items per material)
- ✅ Structure includes: question, answer, topic_keyword, topic_statement
- ⚠️ Missing: expert info, severity, acceptedAnswer
- 📋 Enrichment needed: Add expert from author, infer severity from topic

---

### Settings.yaml - challenges → prevention
```yaml
# CURRENT STRUCTURE (Settings.yaml)
challenges:
  thermal_management:
  - challenge: "Thermal shock and microcracking"
    severity: "critical"
    threshold_temperature: "ΔT > 50-150°C rapid cooling"
    impact: "Natural stone contains microfissures that propagate under rapid thermal stress..."
    solutions:
    - "Use pulse mode with 8-12 second cooling intervals"
    - "Reduce power density by 40-50% for initial passes"
    - "Pre-heat surface to 30-40°C before cleaning"
    - "Monitor for audible cracking sounds"
    - "Apply protective consolidants for severely weathered stone"
  surface_characteristics:
  - challenge: "Surface texture preservation"
    severity: "high"
    ...
  contamination_challenges:
  - challenge: "Biological growth removal"
    severity: "medium"
    ...

operational:
  common_challenges:
    presentation: descriptive  # ❌ NEEDS: "collapsible"
    items:
      - thermal_management: [...]
        contamination_challenges: [...]
    _section:  # ❌ NEEDS: "sectionMetadata"
      section_title: "Common Challenges"
      description: "Technical challenges and optimization strategies..."
      icon: "triangle-exclamation"

# REQUIRED TRANSFORMATION → prevention collapsible format
prevention:
  presentation: collapsible
  sectionMetadata:
    section_title: "Challenges & Prevention"
    section_description: "Common issues and how to prevent them"
    icon: "shield-halved"
    order: 5
  items:
  - category: "Thermal Management"
    challenge: "Thermal shock and microcracking"
    description: "Natural stone contains microfissures that propagate under rapid thermal stress..."
    severity: "critical"
    threshold: "ΔT > 50-150°C rapid cooling"
    solutions:
    - "Use pulse mode with 8-12 second cooling intervals"
    - "Reduce power density by 40-50% for initial passes"
    - "Pre-heat surface to 30-40°C before cleaning"
    prevention:
    - "Monitor for audible cracking sounds"
    - "Apply protective consolidants for severely weathered stone"
  - category: "Surface Characteristics"
    challenge: "Surface texture preservation"
    severity: "high"
    ...
  options:
    autoOpenFirst: true
    sortBy: "severity"
```

**Data Status:**
- ✅ 14 settings have `challenges` field (dict with 3 categories)
- ✅ Structure includes: challenge, severity, impact, solutions
- ✅ Also has `operational.common_challenges` (already wrapped, wrong presentation)
- ⚠️ Missing: prevention tips (separate from solutions)
- 📋 Transformation needed:
  1. Top-level `challenges` dict → collapsible array
  2. Fix `operational.common_challenges`: descriptive → collapsible, _section → sectionMetadata

---

## 🛠️ Implementation Tasks

### Phase 1: Materials expert_answers (Priority 1)

**Task 1.1:** Create `normalize_expert_answers` in UniversalContentGenerator
```python
def normalize_expert_answers(self, item_data: Dict, domain: str, settings: Dict) -> Dict:
    """
    Transform FAQ data to expert_answers collapsible structure.
    
    Transformation:
    - faq[] → expert_answers.items[]
    - Add expert info from author field
    - Infer severity from topic_keyword
    - Set acceptedAnswer based on quality
    - Add collapsible presentation
    """
    faq_items = item_data.get('faq', [])
    if not faq_items:
        return None
    
    # Get author info for expert credentials
    author = item_data.get('author', {})
    expert_info = {
        'name': author.get('name', 'Unknown'),
        'credentials': f"{author.get('title', '')}, {', '.join(author.get('expertise', []))}"
    }
    
    # Transform each FAQ to expert_answer format
    items = []
    for faq in faq_items:
        item = {
            'question': faq.get('question'),
            'answer': faq.get('answer'),
            'expert': expert_info,
            'severity': self._infer_severity(faq.get('topic_keyword', '')),
            'acceptedAnswer': True,  # All FAQ items are accepted answers
            'category': faq.get('topic_keyword', 'General')
        }
        items.append(item)
    
    return {
        'presentation': 'collapsible',
        'sectionMetadata': {
            'section_title': 'Expert Q&A',
            'section_description': 'Common questions answered by laser cleaning specialists',
            'icon': 'user-tie',
            'order': 4
        },
        'items': items,
        'options': {
            'autoOpenFirst': True,
            'autoOpenAccepted': True,
            'sortBy': 'severity'
        }
    }

def _infer_severity(self, topic: str) -> str:
    """Infer severity from topic keywords."""
    critical_keywords = ['damage', 'failure', 'hazard', 'danger']
    high_keywords = ['important', 'significant', 'critical']
    
    topic_lower = topic.lower()
    if any(kw in topic_lower for kw in critical_keywords):
        return 'critical'
    elif any(kw in topic_lower for kw in high_keywords):
        return 'high'
    else:
        return 'medium'
```

**Task 1.2:** Add task to export/config/materials.yaml
```yaml
generation_tasks:
  - task: normalize_expert_answers
    source_field: faq
    target_field: expert_answers
    presentation: collapsible
    options:
      autoOpenFirst: true
      autoOpenAccepted: true
      sortBy: severity
```

**Task 1.3:** Test with materials export
```bash
python3 run.py --export --domain materials --limit 5
# Verify frontmatter/materials/*.yaml has expert_answers collapsible structure
```

---

### Phase 2: Settings prevention (Priority 2)

**Task 2.1:** Create `normalize_prevention` in UniversalContentGenerator
```python
def normalize_prevention(self, item_data: Dict, domain: str, settings: Dict) -> Dict:
    """
    Transform challenges data to prevention collapsible structure.
    
    Handles TWO structures:
    1. Top-level challenges dict (categorized)
    2. operational.common_challenges (already wrapped)
    """
    challenges_dict = item_data.get('challenges', {})
    if not challenges_dict:
        return None
    
    # Transform categorized challenges to flat array
    items = []
    for category, challenge_list in challenges_dict.items():
        category_name = self._format_category_name(category)
        
        for challenge_obj in challenge_list:
            item = {
                'category': category_name,
                'challenge': challenge_obj.get('challenge'),
                'description': challenge_obj.get('impact', ''),
                'severity': challenge_obj.get('severity', 'medium'),
                'threshold': challenge_obj.get('threshold_temperature', ''),
                'solutions': challenge_obj.get('solutions', [])
            }
            
            # Extract prevention tips (last 1-2 solutions are usually preventive)
            if len(item['solutions']) > 3:
                item['prevention'] = item['solutions'][-2:]
                item['solutions'] = item['solutions'][:-2]
            
            items.append(item)
    
    return {
        'presentation': 'collapsible',
        'sectionMetadata': {
            'section_title': 'Challenges & Prevention',
            'section_description': 'Common issues and how to prevent them',
            'icon': 'shield-halved',
            'order': 5
        },
        'items': items,
        'options': {
            'autoOpenFirst': True,
            'sortBy': 'severity'
        }
    }

def _format_category_name(self, category_key: str) -> str:
    """Convert snake_case to Title Case."""
    return ' '.join(word.capitalize() for word in category_key.split('_'))
```

**Task 2.2:** Fix `operational.common_challenges` structure
```python
def fix_operational_challenges(self, item_data: Dict) -> Dict:
    """
    Fix operational.common_challenges structure:
    - presentation: descriptive → collapsible
    - _section → sectionMetadata
    """
    operational = item_data.get('operational', {})
    common_challenges = operational.get('common_challenges', {})
    
    if not common_challenges:
        return None
    
    # Fix presentation
    common_challenges['presentation'] = 'collapsible'
    
    # Rename _section to sectionMetadata
    if '_section' in common_challenges:
        section = common_challenges.pop('_section')
        common_challenges['sectionMetadata'] = {
            'section_title': section.get('section_title', section.get('title', '')),
            'section_description': section.get('description', ''),
            'icon': section.get('icon', 'triangle-exclamation'),
            'order': section.get('order', 3)
        }
    
    return common_challenges
```

**Task 2.3:** Add tasks to export/config/settings.yaml
```yaml
generation_tasks:
  - task: normalize_prevention
    source_field: challenges
    target_field: prevention
    presentation: collapsible
    options:
      autoOpenFirst: true
      sortBy: severity
  
  - task: fix_operational_challenges
    source_field: operational.common_challenges
    target_field: operational.common_challenges
    in_place: true
```

**Task 2.4:** Test with settings export
```bash
python3 run.py --export --domain settings --limit 5
# Verify frontmatter/settings/*.yaml has prevention collapsible structure
```

---

## 🧪 Testing Strategy

### Unit Tests (export/tests/)
```python
def test_normalize_expert_answers():
    """Test FAQ → expert_answers transformation."""
    generator = UniversalContentGenerator()
    
    input_data = {
        'faq': [
            {
                'question': 'How does laser cleaning work?',
                'answer': 'Laser cleaning uses...',
                'topic_keyword': 'safety',
                'topic_statement': 'Safe cleaning process'
            }
        ],
        'author': {
            'name': 'Todd Dunning',
            'title': 'Technical Lead',
            'expertise': ['Laser Systems', 'Safety']
        }
    }
    
    result = generator.normalize_expert_answers(input_data, 'materials', {})
    
    assert result['presentation'] == 'collapsible'
    assert 'sectionMetadata' in result
    assert len(result['items']) == 1
    assert result['items'][0]['expert']['name'] == 'Todd Dunning'
    assert result['items'][0]['acceptedAnswer'] == True

def test_normalize_prevention():
    """Test challenges → prevention transformation."""
    generator = UniversalContentGenerator()
    
    input_data = {
        'challenges': {
            'thermal_management': [
                {
                    'challenge': 'Thermal shock',
                    'severity': 'critical',
                    'impact': 'Causes cracking...',
                    'solutions': ['Use pulse mode', 'Reduce power']
                }
            ]
        }
    }
    
    result = generator.normalize_prevention(input_data, 'settings', {})
    
    assert result['presentation'] == 'collapsible'
    assert 'sectionMetadata' in result
    assert len(result['items']) == 1
    assert result['items'][0]['category'] == 'Thermal Management'
    assert result['items'][0]['severity'] == 'critical'
```

### Integration Tests
```bash
# Test materials expert_answers
python3 run.py --export --domain materials --limit 5
grep -A 20 "expert_answers:" frontmatter/materials/*.yaml

# Test settings prevention
python3 run.py --export --domain settings --limit 5
grep -A 20 "prevention:" frontmatter/settings/*.yaml

# Verify collapsible structure
python3 scripts/validation/validate_collapsible_structure.py
```

---

## 📈 Success Criteria

### expert_answers (Materials)
- [ ] 153/153 materials have expert_answers field
- [ ] presentation = "collapsible" (100%)
- [ ] sectionMetadata includes: section_title, icon, order
- [ ] items[] include: question, answer, expert, severity, acceptedAnswer
- [ ] expert.credentials derived from author field
- [ ] options include: autoOpenFirst, autoOpenAccepted, sortBy

### prevention (Settings)
- [ ] 14/14 settings have prevention field
- [ ] presentation = "collapsible" (100%)
- [ ] sectionMetadata includes: section_title, icon, order
- [ ] items[] include: category, challenge, description, severity, solutions
- [ ] operational.common_challenges fixed: presentation=collapsible, sectionMetadata
- [ ] options include: autoOpenFirst, sortBy

### Code Quality
- [ ] Unit tests pass (2 new tests)
- [ ] Integration tests pass
- [ ] No hardcoded values (use config)
- [ ] Follows existing normalize_applications pattern
- [ ] Documentation updated

---

## 📝 Documentation Updates

After implementation:
1. Update docs/COLLAPSIBLE_NORMALIZATION_SCHEMA-2.md status to IMPLEMENTED
2. Add entry to CHANGELOG.md
3. Update export/README.md with new tasks
4. Create implementation-collapsible-normalization-2026-01-03.md summary

---

## 🚀 Timeline

| Phase | Task | Estimate | Status |
|-------|------|----------|--------|
| **Phase 1** | normalize_expert_answers | 30 min | 🟡 Ready |
| | Add to materials.yaml config | 5 min | 🟡 Ready |
| | Test materials export | 10 min | 🟡 Ready |
| **Phase 2** | normalize_prevention | 45 min | 🟡 Ready |
| | fix_operational_challenges | 15 min | 🟡 Ready |
| | Add to settings.yaml config | 5 min | 🟡 Ready |
| | Test settings export | 10 min | 🟡 Ready |
| **Testing** | Unit tests | 20 min | 🟡 Ready |
| | Integration tests | 15 min | 🟡 Ready |
| | Documentation | 15 min | 🟡 Ready |
| **TOTAL** | | **2.5 hours** | 🟡 Ready to Start |

---

## 🎯 Next Actions

1. **START HERE**: Implement `normalize_expert_answers` for Materials
2. Add task to export/config/materials.yaml
3. Test with 5 materials
4. Implement `normalize_prevention` for Settings
5. Test with 5 settings
6. Run full export for both domains
7. Verify collapsible structure compliance
8. Update documentation

---

**Status:** All data discovery complete. Ready to implement transformations.
