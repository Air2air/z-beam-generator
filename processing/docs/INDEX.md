# Processing System Documentation Index

**Last Updated:** November 14, 2025

---

## 🚀 Getting Started

| Document | Purpose | Audience |
|----------|---------|----------|
| **[QUICKSTART.md](QUICKSTART.md)** | Quick setup and basic usage | New users |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System architecture overview with diagrams | Developers |
| **[INTENSITY_QUICK_REFERENCE.md](INTENSITY_QUICK_REFERENCE.md)** | Cheat sheet for slider controls | All users |

---

## 📖 Core Concepts

### Configuration & Control

| Document | Purpose | Key Topics |
|----------|---------|------------|
| **[CONFIG_CENTRALIZATION.md](CONFIG_CENTRALIZATION.md)** | Slider-driven configuration architecture | Layered calculation, dynamic parameters |
| **[INTENSITY_CONTROLS.md](INTENSITY_CONTROLS.md)** | Complete guide to 10-slider system | Slider details, programmatic usage |
| **[AUTHOR_PROFILES_SYSTEM.md](AUTHOR_PROFILES_SYSTEM.md)** | Author personality offset system | Yi-Chun, Alessandro, Ikmanda, Todd |

### Architecture & Design

| Document | Purpose | Key Topics |
|----------|---------|------------|
| **[ARCHITECTURE_RATIONALE.md](ARCHITECTURE_RATIONALE.md)** | Why specification-driven architecture | Flexibility without redundancy |
| **[FLEXIBLE_ARCHITECTURE_GUIDE.md](FLEXIBLE_ARCHITECTURE_GUIDE.md)** | Component types and content domains | Adding new types, usage examples |
| **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** | What was built and how | Module descriptions, migration path |
| **[CHAIN_VERIFICATION_GUIDE.md](CHAIN_VERIFICATION_GUIDE.md)** | 🆕 Runtime chain completeness verification | Phase tracking, fail-fast, statistics |

---

## 🎯 Quick Navigation by Task

### "I want to adjust content characteristics"
→ **[INTENSITY_QUICK_REFERENCE.md](INTENSITY_QUICK_REFERENCE.md)** - See slider descriptions  
→ **[INTENSITY_CONTROLS.md](INTENSITY_CONTROLS.md)** - Detailed control guide

### "I want to understand the system architecture"
→ **[ARCHITECTURE.md](ARCHITECTURE.md)** - Visual diagrams and data flow  
→ **[ARCHITECTURE_RATIONALE.md](ARCHITECTURE_RATIONALE.md)** - Design decisions  
→ **[CHAIN_VERIFICATION_GUIDE.md](CHAIN_VERIFICATION_GUIDE.md)** - 🆕 Chain completeness verification

### "I want to generate content programmatically"
→ **[QUICKSTART.md](QUICKSTART.md)** - Code examples  
→ **[FLEXIBLE_ARCHITECTURE_GUIDE.md](FLEXIBLE_ARCHITECTURE_GUIDE.md)** - Advanced usage

### "I want to understand how configuration works"
→ **[CONFIG_CENTRALIZATION.md](CONFIG_CENTRALIZATION.md)** - Full explanation  
→ **[ARCHITECTURE.md](ARCHITECTURE.md)** - See data flow diagram

### "I want to differentiate author personalities"
→ **[AUTHOR_PROFILES_SYSTEM.md](AUTHOR_PROFILES_SYSTEM.md)** - Offset system  
→ **[INTENSITY_CONTROLS.md](INTENSITY_CONTROLS.md)** - How offsets interact with sliders

---

## 🔧 CLI Commands Reference

```bash
# View current slider settings
python3 -m processing.intensity.intensity_cli status

# Adjust individual slider (0-100)
python3 -m processing.intensity.intensity_cli set rhythm 70

# Test current settings (see prompt instructions)
python3 -m processing.intensity.intensity_cli test

# Validate configuration
python3 -m processing.config.validate_config

# Compare author personalities
python3 -m processing.config.author_comparison_matrix
```

---

## 📐 System Architecture at a Glance

```
USER (adjusts sliders)
    ↓
config.yaml (10 sliders + infrastructure)
    ↓
config_loader.py (reads YAML)
    ↓
    ├─→ dynamic_config.py (calculates 30+ technical params)
    └─→ author_config_loader.py (applies personality offsets)
         ↓
orchestrator.py (generates content)
    ↓
OUTPUT (human-authentic content)
```

See **[ARCHITECTURE.md](ARCHITECTURE.md)** for detailed diagram.

---

## 🎨 The 10 Control Sliders

| # | Slider | What It Controls | Default |
|---|--------|------------------|---------|
| 1 | `author_voice_intensity` | Regional voice patterns | 50 |
| 2 | `personality_intensity` | Personal opinions | 40 |
| 3 | `engagement_style` | Reader engagement | 35 |
| 4 | `technical_language_intensity` | Technical density | 50 |
| 5 | `context_specificity` | Detail level | 55 |
| 6 | `sentence_rhythm_variation` | Structure variety (KEY) | 80 |
| 7 | `imperfection_tolerance` | Human-like quirks (KEY) | 80 |
| 8 | `structural_predictability` | Template adherence | 45 |
| 9 | `ai_avoidance_intensity` | Pattern variation | 50 |
| 10 | `length_variation_range` | Length flexibility | 50 |

---

## 📚 Document Relationships

```
QUICKSTART.md (entry point)
    ├─→ ARCHITECTURE.md (understanding)
    │    └─→ ARCHITECTURE_RATIONALE.md (deep dive)
    │
    ├─→ INTENSITY_QUICK_REFERENCE.md (quick commands)
    │    └─→ INTENSITY_CONTROLS.md (full details)
    │         └─→ CONFIG_CENTRALIZATION.md (technical explanation)
    │
    └─→ FLEXIBLE_ARCHITECTURE_GUIDE.md (advanced usage)
         └─→ IMPLEMENTATION_SUMMARY.md (internals)
              └─→ AUTHOR_PROFILES_SYSTEM.md (personality system)
```

---

## 🏷️ Tags by Category

### Configuration & Setup
`QUICKSTART` | `CONFIG_CENTRALIZATION` | `INTENSITY_CONTROLS`

### Architecture & Design  
`ARCHITECTURE` | `ARCHITECTURE_RATIONALE` | `FLEXIBLE_ARCHITECTURE_GUIDE`

### User Guides
`INTENSITY_QUICK_REFERENCE` | `AUTHOR_PROFILES_SYSTEM`

### Technical Reference
`IMPLEMENTATION_SUMMARY` | `CONFIG_CENTRALIZATION`

---

## 📝 Documentation Standards

All documentation follows these principles:
1. **Start with "Why"** - Explain purpose before details
2. **Show code examples** - Real, working code snippets
3. **Include CLI commands** - Exact commands users can run
4. **Visual diagrams** - ASCII art for data flow
5. **Keep current** - Update date at top of each file

---

**Need help?** Start with **[QUICKSTART.md](QUICKSTART.md)** or **[ARCHITECTURE.md](ARCHITECTURE.md)**
