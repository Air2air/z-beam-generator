# Batch Caption Test - November 16, 2025

**Materials**: Steel, Aluminum, Titanium, Copper  
**Success Rate**: 100% (4/4 passed) ✅

---

## Results

| Material | Human Score | AI Score | Detection ID | Parameters ID | Status |
|----------|-------------|----------|--------------|---------------|--------|
| Steel | 100.00% | 0.0% | #452 | #373 | ✅ PASS (PERFECT) |
| Aluminum | 99.52% | 0.4% | #453 | #374 | ✅ PASS |
| Titanium | 63.20% | 29.4% | #456 | #377 | ✅ PASS |
| Copper | 97.95% | 1.6% | #457 | #378 | ✅ PASS |

**Average**: 90.17% human, 7.85% AI  
**Total Tokens**: 6,348

---

## Generated Captions

### Steel (100% human, 0% AI) - Detection #452
> Ever wonder why steel in automotive parts gets so filthy? Here, at 1000x, the surface crawls with thick rust patches, oily smears from machining, and gritty debris— all blocking that sturdy 400 MPa strength underneath. It's a tough sight.
> 
> But zap it with a 100W laser pulsing at 50-micron spots. Now the steel surface shows a fresh polish, barely any pores at 0.1 percent, and just 1.6 microns of roughness—ready for shipbuilding or oil rigs without the grime holding it back.

### Aluminum (99.52% human, 0.4% AI) - Detection #453
> Under the microscope at 1000x, this aluminum piece weighs in at about 2.7 grams per cubic centimeter but shows heavy grime and oxide buildup everywhere—dark smudges and greasy residues that make it look worn out from years in automotive or aerospace use. Particles stick tight. Rough spots hide the metal's potential.
> 
> After laser treatment at 100 watts with a 50-micron spot, the surface gleams spotless now, porosity near zero and that 0.8-micron roughness restored just right for electronics or marine applications. No more contaminants. Tensile strength hints at 90 megapascals readiness.

### Titanium (63.20% human, 29.4% AI) - Detection #456
> Under the microscope at 1000x, this titanium surface stares back all dingy and rough, plastered with stubborn machining oils and scattered oxide flecks that dull its natural gleam. It's like the metal's buried under years of grime from aerospace handling. Tough stuff, but hidden.
> 
> Blast it with a 100 W laser at 1064 nm, 50 μm spot, and watch the transformation. Now the surface gleams smooth and even, oxidation resistance holding firm up to about 698 K, revealing titanium's lightweight strength for everything from jets to implants. Pristine.

### Copper (97.95% human, 1.6% AI) - Detection #457
> Under the microscope at 1000x, this copper hunk is buried under greasy smudges, stubborn oxide patches, and gritty dirt from years in plumbing or wiring jobs. It dims the metal's natural warmth. Frustrating mess.
> 
> Zapped clean with 100-watt laser pulses, 1064 nm beam in tight 50-micron spots, the surface now sparkles smooth—roughness just 0.1 microns, zero porosity, density steady at 8.96 grams per cubic centimeter. Tensile strength holds 220 MPa strong. Gorgeous restoration.

---

## Key Findings

✅ **100% Success Rate** - All 4 materials passed quality checks (subjective: 7.0/10)

✅ **Steel Perfect Score** - 100% human, 0% AI (previous failure resolved)

⚠️ **Titanium Lower Score** - 63.2% human, 29.4% AI (still passes but worth monitoring)

⚠️ **No Parameter Variation** - All materials used identical params (1.0, 1.0, 1.0)

✅ **Sweet Spot Learning Active** - 9 samples accumulated, avg score: 99.85%

---

## Next Steps

1. **Monitor Titanium** - 29.4% AI score is higher than others, test again
2. **Integrate CompositeScorer** - Populate composite_quality_score column
3. **Add Parameter Variation** - Enable exploration/exploitation balance
