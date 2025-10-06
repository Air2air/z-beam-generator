# Priority Materials for industryTags Implementation
## High-Value Materials (Most Common in Industry)

Based on industrial usage frequency and laser cleaning demand, implement industryTags in this order:

### Phase 1A: Common Metals (Top Priority)
**Impact: Aerospace, Automotive, Manufacturing**

- [ ] Aluminum (most common industrial metal)
- [ ] Stainless Steel 304 (food, medical, general)
- [ ] Stainless Steel 316 (marine, chemical, medical)
- [ ] Steel (construction, general manufacturing)
- [ ] Copper (electrical, plumbing, heat exchangers)
- [ ] Brass (plumbing, musical instruments, marine)
- [ ] Bronze (marine, art, bearings)
- [ ] Titanium (aerospace, medical, chemical)
- [ ] Nickel (aerospace, chemical, electronics)
- [ ] Zinc (galvanizing, die casting)

**Estimated Time:** 2-3 hours  
**Savings:** ~10 materials × $0.15/call = $1.50 per batch

### Phase 1B: Common Alloys & High-Performance Metals
**Impact: Aerospace, Defense, Medical**

- [ ] Inconel (aerospace turbines, chemical processing)
- [ ] Monel (marine, chemical processing)
- [ ] Chromium (plating, aerospace)
- [ ] Tungsten (aerospace, defense, electronics)
- [ ] Tungsten Carbide (tooling, wear parts)
- [ ] Titanium Carbide (cutting tools, aerospace)
- [ ] Cobalt (aerospace, medical implants)
- [ ] Molybdenum (aerospace, electronics)

**Estimated Time:** 1-2 hours  
**Savings:** ~8 materials × $0.15/call = $1.20 per batch

### Phase 2A: Common Stones & Building Materials
**Impact: Architecture, Construction, Restoration**

- [ ] Granite (countertops, monuments, architecture)
- [ ] Marble (architecture, art, luxury surfaces)
- [ ] Limestone (construction, architecture)
- [ ] Sandstone (architecture, restoration)
- [ ] Slate (roofing, flooring)
- [ ] Concrete (construction, infrastructure)
- [ ] Brick (construction, restoration)
- [ ] Terracotta (architecture, pottery)

**Estimated Time:** 1-2 hours  
**Savings:** ~8 materials × $0.15/call = $1.20 per batch

### Phase 2B: Common Woods
**Impact: Furniture, Construction, Restoration**

- [ ] Oak (furniture, flooring, wine barrels)
- [ ] Maple (furniture, flooring, food surfaces)
- [ ] Cherry (furniture, cabinetry)
- [ ] Walnut (furniture, gunstocks)
- [ ] Pine (construction, furniture)
- [ ] Cedar (outdoor furniture, closets)
- [ ] Teak (marine, outdoor furniture)
- [ ] Mahogany (luxury furniture, musical instruments)
- [ ] Bamboo (flooring, sustainable construction)
- [ ] Birch (furniture, plywood)

**Estimated Time:** 1-2 hours  
**Savings:** ~10 materials × $0.15/call = $1.50 per batch

### Phase 3A: Advanced Materials
**Impact: Aerospace, Electronics, Medical**

- [ ] Carbon Fiber Reinforced Polymer (aerospace, automotive, sporting goods)
- [ ] Kevlar (aerospace, defense, protective equipment)
- [ ] Silicon (semiconductors, solar)
- [ ] Silicon Carbide (semiconductors, abrasives)
- [ ] Silicon Nitride (bearings, cutting tools)
- [ ] Graphene (electronics, research)
- [ ] Graphite (batteries, lubricants, nuclear)
- [ ] Ceramic Matrix Composites CMCs (aerospace turbines)
- [ ] Glass Reinforced Plastic GRP (marine, construction)
- [ ] Borosilicate Glass (laboratory, pharmaceutical)

**Estimated Time:** 2-3 hours  
**Savings:** ~10 materials × $0.15/call = $1.50 per batch

### Phase 3B: Specialized Materials
**Impact: Various specialized industries**

- [ ] Diamond (tooling, optics, electronics)
- [ ] Sapphire (optics, semiconductors, watches)
- [ ] Ruby (lasers, watches, bearings)
- [ ] Platinum (chemical, medical, jewelry)
- [ ] Gold (electronics, medical, jewelry)
- [ ] Silver (electronics, medical, mirrors)
- [ ] Palladium (automotive catalysts, electronics)
- [ ] Rhodium (catalysts, mirrors)
- [ ] Iridium (aerospace, medical)
- [ ] Ruthenium (electronics, catalysts)

**Estimated Time:** 2-3 hours  
**Savings:** ~10 materials × $0.15/call = $1.50 per batch

### Phase 4: Remaining Materials
**Impact: Niche applications**

All remaining materials (ceramics, specialty alloys, rare stones, etc.)

**Estimated Time:** 3-4 hours  
**Savings:** ~65 materials × $0.15/call = $9.75 per batch

---

## Implementation Strategy

### Quick Start (2 hours)
Focus on Phase 1A only (10 common metals)
- **Savings:** $1.50 per batch
- **ROI:** Break-even after ~8 batches

### Optimal Start (4 hours)
Complete Phase 1A + 1B (18 materials)
- **Savings:** $2.70 per batch
- **ROI:** Break-even after ~9 batches

### Full Implementation (12-15 hours)
Complete all 121 materials
- **Savings:** $18.15 per batch
- **ROI:** Break-even after ~42 batches

### Recommended Approach
1. **Day 1:** Phase 1A (common metals) - immediate 8% savings
2. **Day 2:** Phase 1B + 2A (alloys + stones) - up to 21% savings
3. **Day 3:** Phase 2B + 3A (woods + advanced) - up to 44% savings
4. **Day 4:** Phase 3B + 4 (complete) - full 100% savings

---

## Research Resources

### For industryTags Research:
- Categories.yaml `applicationTypeDefinitions` (primary source)
- Material-specific industry associations
- ASTM standards (indicate industries)
- Existing regulatoryStandards (hint at industries)
- Common laser cleaning applications

### Quality Checks:
- ✅ Each material has 5-10 industryTags
- ✅ Tags match Categories.yaml applicationTypeDefinitions exactly
- ✅ Most relevant industries listed first
- ✅ YAML formatting correct (list with proper indentation)
- ✅ No duplicates within a material

---

## Progress Tracking

**Total Materials:** 121  
**Phase 1A Complete:** 0/10 (0%)  
**Phase 1B Complete:** 0/8 (0%)  
**Phase 2A Complete:** 0/8 (0%)  
**Phase 2B Complete:** 0/10 (0%)  
**Phase 3A Complete:** 0/10 (0%)  
**Phase 3B Complete:** 0/10 (0%)  
**Phase 4 Complete:** 0/65 (0%)  

**Overall Progress:** 0/121 (0%)  
**API Calls Saved:** 0 per batch  
**Cost Saved:** $0 per batch  

---

## Notes

- Start with Phase 1A for quickest ROI
- Test optimization after each phase
- Validate YAML syntax before committing
- Cross-reference with existing Materials.yaml metadata
- Use INDUSTRY_TAGS_EXAMPLES.yaml as formatting guide
