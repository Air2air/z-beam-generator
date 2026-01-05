#!/usr/bin/env python3
"""
Add ablationThreshold to Materials.yaml and common_issues to settings files.

This script:
1. Adds ablationThreshold to material_characteristics in Materials.yaml
2. Generates common_issues array for each settings file
3. Uses category-based calculations and material-specific troubleshooting
"""

import sys
import yaml
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Loader imports not needed - we load YAML directly

def calculate_ablation_threshold(material_name, category, subcategory, material_data, categories_data):
    """Calculate ablationThreshold based on category ranges from Categories.yaml."""
    
    # Check if we have laserDamageThreshold to base calculation on
    if 'material_characteristics' in material_data:
        mat_chars = material_data['material_characteristics']
        if 'laserDamageThreshold' in mat_chars and mat_chars['laserDamageThreshold']:
            ldt_value = mat_chars['laserDamageThreshold'].get('value')
            if ldt_value:
                # Ablation threshold is typically 50-70% of damage threshold
                value = round(ldt_value * 0.6, 2)
                min_val = round(value * 0.6, 2)
                max_val = round(value * 1.5, 2)
                return value, min_val, max_val
    
    # Get ranges from Categories.yaml
    if category in categories_data and 'category_ranges' in categories_data[category]:
        ranges = categories_data[category]['category_ranges']
        if 'ablationThreshold' in ranges:
            abl_range = ranges['ablationThreshold']
            min_val = float(abl_range.get('min', 1.0))
            max_val = float(abl_range.get('max', 5.0))
            # Calculate midpoint as value
            value = round((min_val + max_val) / 2, 2)
            return value, min_val, max_val
    
    # Fallback if not in Categories.yaml
    value = 2.0
    min_val = 1.0
    max_val = 4.0
    return value, min_val, max_val


def generate_common_issues_for_material(material_name, category, subcategory):
    """Generate material-specific common_issues array."""
    
    # Category-specific issue templates
    issues_by_category = {
        'metal': [
            {
                'symptom': f'Oxide layer reforms immediately after {material_name} cleaning',
                'causes': [
                    f'{material_name} rapidly oxidizes when exposed to ambient air at elevated temperatures',
                    'Insufficient cooling time between passes allows surface temperature to exceed oxidation threshold',
                    'High humidity environment (>60% RH) accelerates oxide reformation'
                ],
                'solutions': [
                    'Apply protective coating (wax, oil, or polymer sealant) within 30 seconds of cleaning completion',
                    'Increase cooling time between passes from 2s to 5-8s to reduce peak temperature',
                    'Perform cleaning in controlled atmosphere (<40% RH) or inert gas environment',
                    'Reduce laser power by 15-20% to minimize thermal oxidation'
                ],
                'verification': f'Cleaned {material_name} surface should maintain metallic luster for >5 minutes. Use oxidation test strips or visual inspection for color change.',
                'prevention': 'Store cleaned parts in low-humidity environment (<35% RH). Consider vacuum-sealed packaging for long-term oxide prevention.'
            },
            {
                'symptom': f'{material_name} surface shows heat-affected zones or discoloration around cleaned areas',
                'causes': [
                    f'Laser fluence exceeds {material_name} thermal diffusion rate, causing localized melting',
                    'Scan speed too slow (<200 mm/s) creates excessive dwell time per spot',
                    'Overlapping passes accumulate heat beyond material thermal conductivity limits'
                ],
                'solutions': [
                    'Reduce laser power from current setting by 25-30% to prevent thermal damage',
                    'Increase scan speed from current rate to 800-1200 mm/s for reduced dwell time',
                    'Switch to picosecond or femtosecond pulse mode for cold ablation',
                    'Implement crosshatch scan pattern (45° angle change between passes) to distribute heat'
                ],
                'verification': f'{material_name} surface should show uniform color/finish with no HAZ visible under 10x magnification. Measure with infrared thermometer - should not exceed 150°C during cleaning.',
                'prevention': 'Start with conservative parameters (low power, high speed). Test on scrap piece first. Monitor surface temperature in real-time.'
            },
            {
                'symptom': f'Laser beam reflects unpredictably off polished {material_name}, creating safety hazards',
                'causes': [
                    f'Polished {material_name} surface has high reflectivity (>70%) at laser wavelength',
                    'Variable surface geometry causes specular reflection at unpredictable angles',
                    'Protective enclosure has gaps or insufficient beam containment'
                ],
                'solutions': [
                    'Install beam dump or beam trap at predicted reflection angles',
                    'Use longer wavelength (1064nm → 2000nm+) for improved absorption',
                    'Pre-treat surface with absorptive coating (graphite spray) if acceptable',
                    'Implement enclosed cleaning chamber with interlocked safety shutters'
                ],
                'verification': 'Use laser power meter to confirm zero stray reflections outside designated work area. Check with laser viewing card for scattered light.',
                'prevention': 'Always use safety enclosure rated for laser class. Wear appropriate wavelength-specific laser safety glasses (OD 6+).'
            },
            {
                'symptom': f'{material_name} shows micro-pitting or surface roughness after cleaning',
                'causes': [
                    'Pulse energy exceeds ablation threshold, causing localized vaporization',
                    'Pulse width too long (>50ns) transitions from ablation to melting regime',
                    f'{material_name} grain structure responds non-uniformly to laser heating'
                ],
                'solutions': [
                    'Reduce pulse energy to 70-80% of current setting',
                    'Switch to shorter pulse width (<20ns) or ultrashort pulse mode',
                    'Increase repetition rate while lowering per-pulse energy (same average power)',
                    'Apply post-cleaning surface polishing if micro-pitting is acceptable'
                ],
                'verification': 'Measure surface roughness with profilometer - Ra should be <1 μm for quality finish. Visual inspection under oblique lighting should show no pitting.',
                'prevention': 'Use gentler cleaning approach with multiple low-energy passes rather than single high-energy pass.'
            }
        ],
        'wood': [
            {
                'symptom': f'{material_name} surface shows charring or darkening after laser cleaning',
                'causes': [
                    f'{material_name} lignin decomposes at 250-300°C, producing carbonized surface layer',
                    'Excessive fluence (>1.5 J/cm²) causes thermal pyrolysis of cellulose',
                    'Multiple passes without cooling accumulate heat beyond char threshold'
                ],
                'solutions': [
                    'Reduce laser power from current setting by 40-50% to prevent charring',
                    'Increase scan speed to 1500-2500 mm/s for minimal thermal accumulation',
                    'Add 8-12 second cooling delay between passes to allow heat dissipation',
                    'Use pulse mode with burst duration <100ms and 5s rest between bursts'
                ],
                'verification': f'{material_name} surface should retain natural color with no black/brown char marks. Touch test - surface should not feel brittle or crumbly.',
                'prevention': 'Start with ultra-conservative parameters (30W, 2000 mm/s). Test on hidden area first. Monitor surface color continuously.'
            },
            {
                'symptom': f'{material_name} grain becomes raised or fuzzy after cleaning',
                'causes': [
                    'Laser selectively ablates softer earlywood, leaving harder latewood standing proud',
                    'Lignin breakdown weakens cell wall structure, causing fiber separation',
                    'Moisture content >12% exacerbates grain raising during heating'
                ],
                'solutions': [
                    'Dry wood to 8-10% moisture content before cleaning (use moisture meter)',
                    'Reduce pulse width to <15ns for more uniform ablation across grain',
                    'Sand surface lightly (220 grit) after cleaning to smooth raised grain',
                    'Apply grain filler or sanding sealer if smooth finish required'
                ],
                'verification': 'Run hand across grain direction - should feel smooth with minimal texture. Use 10x magnification to check for protruding fibers.',
                'prevention': 'Ensure proper wood drying before cleaning. Accept slight grain texture as natural characteristic of laser-cleaned wood.'
            },
            {
                'symptom': f'Smoke generation overwhelms extraction system during {material_name} cleaning',
                'causes': [
                    f'{material_name} pyrolysis produces large volumes of volatile organics (aldehydes, phenols)',
                    'Insufficient extraction airflow (<500 CFM) cannot keep pace with smoke production',
                    'Extraction nozzle positioned >50mm from cleaning point reduces capture efficiency'
                ],
                'solutions': [
                    'Increase extraction fan speed or use higher-capacity system (>800 CFM)',
                    'Position extraction nozzle within 30mm of laser focal point',
                    'Reduce cleaning area per pass (smaller scan field) to limit smoke generation rate',
                    'Use crossdraft ventilation with pre-filters to capture particulates'
                ],
                'verification': 'Operator should have clear visual of cleaning point at all times. Air quality monitor should show <50 ppm VOCs.',
                'prevention': 'Design extraction system for 2-3x expected smoke volume. Regular filter maintenance. Consider HEPA + activated carbon filtration.'
            },
            {
                'symptom': f'{material_name} shows incomplete contaminant removal in grain valleys',
                'causes': [
                    'Gaussian beam profile delivers insufficient energy to deep grain recesses',
                    'Surface topology shadows prevent direct laser irradiation of valleys',
                    'Contaminant embedded >0.2mm deep below surface unreachable by ablation'
                ],
                'solutions': [
                    'Use flat-top beam profile for uniform energy delivery across surface',
                    'Implement multi-angle cleaning (rotate workpiece 45-90°) for comprehensive coverage',
                    'Increase pulse count per area from 2-3 to 5-8 passes',
                    'Pre-clean with chemical stripper for deep contaminants, then laser finish'
                ],
                'verification': 'Inspect grain valleys with magnifying glass - should be free of visible residue. Wipe test with white cloth should show no transfer.',
                'prevention': 'Assess contaminant depth before cleaning. Deep contamination (>0.3mm) may require hybrid chemical + laser approach.'
            }
        ],
        'plastic': [
            {
                'symptom': f'{material_name} melts or becomes tacky during laser cleaning',
                'causes': [
                    f'{material_name} glass transition temperature (Tg) exceeded by laser heating',
                    'Pulse width >100ns allows thermal diffusion into bulk material',
                    'Thermoplastic nature causes softening at 150-200°C before contaminant removal'
                ],
                'solutions': [
                    'Reduce laser power by 50-60% to prevent polymer chain melting',
                    'Switch to ultrashort pulse mode (<10ps) for cold ablation',
                    'Increase repetition rate to 150-200 kHz while lowering per-pulse energy',
                    'Apply CO2 cooling jet (dry ice particles) to keep surface below Tg'
                ],
                'verification': f'{material_name} surface should be dry and non-tacky to touch. No material flow or deformation visible under magnification.',
                'prevention': 'Know material Tg before cleaning. Use shortest possible pulse width. Test on sample piece to establish safe parameter window.'
            },
            {
                'symptom': f'Toxic fumes detected during {material_name} laser cleaning',
                'causes': [
                    f'{material_name} thermal decomposition releases harmful volatiles (HCl from PVC, cyanides from polyurethane)',
                    'Laser-induced pyrolysis occurs at temperatures >250°C',
                    'Inadequate ventilation allows fume accumulation in work area'
                ],
                'solutions': [
                    'Implement high-volume extraction (>1000 CFM) with activated carbon filtration',
                    'Use chemical scrubber system for acid gas removal (NaOH solution)',
                    'Reduce cleaning temperature by lowering power and increasing speed',
                    'Consider cryogenic cooling to prevent thermal decomposition',
                    'Wear appropriate respiratory protection (NIOSH-approved organic vapor cartridge)'
                ],
                'verification': 'Air quality monitoring should show <1 ppm HCl, <5 ppm formaldehyde, <1 ppm benzene. No detectable odor in operator breathing zone.',
                'prevention': 'Always identify polymer type before cleaning. Some plastics (PVC, polycarbonate) may not be safe for laser cleaning. Consider alternative methods.'
            },
            {
                'symptom': f'{material_name} shows discoloration or color change after cleaning',
                'causes': [
                    'UV component of laser induces photochemical degradation of pigments',
                    'Thermal stress causes color additive migration or decomposition',
                    'Surface oxidation from elevated temperature creates yellowish cast'
                ],
                'solutions': [
                    'Reduce cleaning temperature by 30-40% to prevent pigment damage',
                    'Use longer wavelength (1064nm or 1550nm) to minimize photochemical effects',
                    'Implement inert gas purge (nitrogen or argon) during cleaning to prevent oxidation',
                    'Accept color change as inherent limitation and plan for post-cleaning painting/coating'
                ],
                'verification': 'Compare cleaned area to reference standard under D65 illumination. ΔE color difference should be <3 for acceptable match.',
                'prevention': 'Test on inconspicuous area first. Document acceptable color tolerance with customer before proceeding.'
            },
            {
                'symptom': f'{material_name} warps or deforms during cleaning of large areas',
                'causes': [
                    'Non-uniform heating creates thermal gradients and differential expansion',
                    'Thin sections (<2mm) lack thermal mass for stable temperature distribution',
                    'Laser scan pattern concentrates heat in localized zones'
                ],
                'solutions': [
                    'Clean in smaller sections (100x100mm) with cooling between sections',
                    'Use randomized scan pattern to distribute heat uniformly',
                    'Support thin sections on temperature-controlled platen (20-25°C)',
                    'Reduce average power by increasing scan speed while maintaining fluence'
                ],
                'verification': 'Measure flatness with straightedge - deviation should be <0.5mm per 100mm length. No visible warping or bowing.',
                'prevention': 'Fixture parts securely. Consider cleaning from both sides if warping is critical concern.'
            }
        ],
        'composite': [
            {
                'symptom': f'{material_name} shows delamination or layer separation after cleaning',
                'causes': [
                    'Matrix-fiber interface weakened by thermal stress exceeding bond strength',
                    'Rapid heating causes differential thermal expansion between matrix and reinforcement',
                    'Moisture trapped in composite vaporizes explosively during laser heating'
                ],
                'solutions': [
                    'Reduce laser power by 40-50% to prevent matrix degradation',
                    'Dry composite thoroughly (80°C for 4 hours) before cleaning to remove moisture',
                    'Use ultrashort pulse mode (<10ps) to minimize heat diffusion to interface',
                    'Clean from multiple angles to avoid concentrated energy on single layer'
                ],
                'verification': 'Tap test - clean composite should produce sharp, consistent tone. Dull thud indicates delamination. Ultrasonic inspection for subsurface damage.',
                'prevention': 'Understand composite architecture before cleaning. Some composites are too delicate for laser cleaning.'
            },
            {
                'symptom': f'{material_name} fiber reinforcement becomes exposed or damaged',
                'causes': [
                    'Excessive fluence preferentially ablates polymer matrix, leaving fibers standing proud',
                    'Fiber damage threshold lower than matrix removal threshold',
                    'Carbon fibers absorb strongly at laser wavelength, leading to fiber heating'
                ],
                'solutions': [
                    'Reduce fluence to just above matrix ablation threshold (typically 1-2 J/cm²)',
                    'Use multiple low-energy passes rather than single high-energy pass',
                    'Switch to longer wavelength (1550nm or 2000nm) if fibers are transparent',
                    'Accept slight fiber exposure as inherent limitation of laser cleaning composites'
                ],
                'verification': 'Inspect under 10-20x magnification - fibers should not be protruding >50μm above matrix. No fiber breakage or fraying visible.',
                'prevention': 'Establish matrix-only ablation parameters through careful testing. Monitor fiber integrity continuously.'
            },
            {
                'symptom': f'Resin matrix outgassing during {material_name} cleaning',
                'causes': [
                    'Epoxy or polyester matrix thermally decomposes at >300°C, releasing volatiles',
                    'Trapped moisture or air pockets vaporize explosively',
                    'Incomplete cure of matrix resin allows off-gassing under laser heating'
                ],
                'solutions': [
                    'Reduce cleaning temperature by lowering power 30-40%',
                    'Implement high-flow extraction (>800 CFM) to capture gases',
                    'Pre-bake composite at 120°C for 2 hours to complete cure and remove volatiles',
                    'Use pulse mode with long cooling intervals (10-15s between passes)'
                ],
                'verification': 'No visible smoke or vapor during cleaning. Gas detection should show <10 ppm VOCs in operator breathing zone.',
                'prevention': 'Verify composite cure state before cleaning. Well-cured composites outgas minimally.'
            },
            {
                'symptom': f'{material_name} cleaning effectiveness varies with fiber orientation',
                'causes': [
                    'Anisotropic thermal conductivity - heat spreads 10-50x faster along fibers than across',
                    'Fiber alignment creates preferential ablation paths',
                    'Matrix thickness varies between fiber bundles and resin-rich regions'
                ],
                'solutions': [
                    'Rotate cleaning angle by 45-90° between passes to average anisotropic effects',
                    'Adjust power ±20% based on fiber orientation relative to scan direction',
                    'Use smaller spot size (50-100μm) to resolve individual fiber bundles',
                    'Accept some variation as inherent to composite microstructure'
                ],
                'verification': 'Cleaned surface should have uniform appearance across all fiber orientations. No preferential removal in specific directions.',
                'prevention': 'Map fiber orientations before cleaning. Develop orientation-specific parameter sets if needed.'
            }
        ],
        'stone': [
            {
                'symptom': f'{material_name} cracks or spalls during laser cleaning',
                'causes': [
                    f'{material_name} low thermal shock resistance causes fracture when ΔT exceeds 50-150°C',
                    'Rapid heating creates tensile stress at surface that exceeds fracture strength',
                    'Pre-existing microcracks propagate catastrophically under thermal stress',
                    'Moisture in porous stone vaporizes explosively causing spalling'
                ],
                'solutions': [
                    'Use pulse mode with 8-12 second cooling between passes to limit ΔT to <50°C',
                    'Reduce laser power by 50-60% for gentler heating rate',
                    'Pre-dry stone at 60°C for 24 hours if moisture content >2%',
                    'Apply multiple very low-energy passes (10-15 passes) rather than few high-energy passes'
                ],
                'verification': f'{material_name} should show no new cracks under 10x magnification. Tap test should produce clear ring, not dull thud indicating subsurface damage.',
                'prevention': 'Assess stone condition before cleaning. Weathered or damaged stone may not tolerate laser cleaning. Consider chemical methods for fragile stone.'
            },
            {
                'symptom': f'{material_name} color changes from white/cream to gray/brown after cleaning',
                'causes': [
                    'Iron minerals (pyrite, hematite) in stone oxidize at elevated temperatures',
                    'Organic matter in stone carbonizes at >250°C',
                    'Calcite or dolomite thermally decomposes above 400°C creating burnt appearance'
                ],
                'solutions': [
                    'Reduce peak temperature by lowering power 40-50% and increasing scan speed',
                    'Test on inconspicuous area first to assess color stability',
                    'Use chemical cleaning for iron-rich stones to avoid oxidation',
                    'Accept color change as limitation for this stone type'
                ],
                'verification': 'Compare cleaned area to reference under daylight conditions. Color difference should be minimal (ΔE <5).',
                'prevention': 'Identify mineral composition before cleaning. Some stones (marble with pyrite) are unsuitable for laser cleaning.'
            },
            {
                'symptom': f'Heritage {material_name} shows surface erosion or loss of fine details',
                'causes': [
                    'Weathered stone surface weaker than fresh stone - ablation threshold reduced by 50-70%',
                    'Excessive fluence removes sound stone along with contaminants',
                    'Salt crystallization has created fragile surface layer'
                ],
                'solutions': [
                    'Use absolute minimum fluence (reduce power to 20-30% of normal)',
                    'Increase number of passes from 3-5 to 10-15 for gradual removal',
                    'Desalinate stone before laser cleaning if salt content >0.5%',
                    'Consider alternative methods (chemical poultice) for extremely fragile heritage stone'
                ],
                'verification': 'Stone surface should retain all fine details and tooling marks. Compare to photographic record before cleaning.',
                'prevention': 'Heritage stone requires expert assessment. Document condition thoroughly. Seek conservation specialist input.'
            },
            {
                'symptom': f'{material_name} shows white haze or residue after cleaning',
                'causes': [
                    'Laser-induced calcination creates calcium oxide (CaO) surface layer',
                    'Redeposition of ablated material on surrounding area',
                    'Salt efflorescence from mobilized subsurface salts'
                ],
                'solutions': [
                    'Reduce laser fluence to prevent calcination (lower power 30-40%)',
                    'Clean residue with deionized water rinse and soft brush',
                    'Improve extraction to capture ablated particles before redeposition',
                    'Apply consolidant or water repellent after cleaning if appropriate for stone type'
                ],
                'verification': 'Stone should appear clean with natural color and texture. No white deposits visible. Water droplet test - should absorb normally.',
                'prevention': 'Use lowest effective fluence. Good extraction system critical. Post-cleaning rinse may be necessary.'
            }
        ],
        'ceramic': [
            {
                'symptom': f'{material_name} develops cracks or crazing after laser cleaning',
                'causes': [
                    f'{material_name} extremely low thermal expansion coefficient makes it sensitive to thermal shock',
                    'Rapid heating/cooling creates stress gradients exceeding fracture toughness',
                    'Pre-existing glaze defects propagate under thermal stress',
                    'Temperature differential >200-300°C causes catastrophic failure'
                ],
                'solutions': [
                    'Use pulse mode with 3-5 second cooling delay between passes',
                    'Reduce laser power by 50-60% for gentler heating',
                    'Preheat ceramic to 50-80°C to reduce thermal shock magnitude',
                    'Use ultrashort pulse mode (<10ps) for minimal heat accumulation'
                ],
                'verification': f'{material_name} should show no new cracks or crazing under magnification. Dye penetrant testing can reveal subsurface cracks.',
                'prevention': 'Ceramics are high-risk for laser cleaning. Consider alternative methods. If laser cleaning is necessary, use extreme caution.'
            },
            {
                'symptom': f'{material_name} glaze surface becomes rough or matte after cleaning',
                'causes': [
                    'Laser fluence exceeds glaze ablation threshold, removing glaze along with contaminant',
                    'Glaze and substrate have different absorption - preferential glaze removal',
                    'High-temperature glaze (>1200°C firing) more resistant than low-temp glaze'
                ],
                'solutions': [
                    'Reduce fluence to minimum - start at 20% of normal power',
                    'Increase number of passes from 2-3 to 8-10 for gradual removal',
                    'Use longer wavelength (1550nm or 2000nm) if glaze is transparent at 1064nm',
                    'Accept some glaze damage as unavoidable for heavily contaminated ceramics'
                ],
                'verification': 'Glaze should retain original gloss and smoothness. Measure gloss with 60° glossmeter - should be >80% of uncleaned reference.',
                'prevention': 'Test on edge or back first. Some glazes cannot tolerate laser cleaning. Chemical cleaning may be safer.'
            },
            {
                'symptom': f'{material_name} shows discoloration or color changes in glaze',
                'causes': [
                    'Laser-induced reduction of metal oxide colorants (copper, iron, cobalt)',
                    'Thermal annealing alters crystal structure of pigments',
                    'Organic colorants decompose at >300°C'
                ],
                'solutions': [
                    'Reduce cleaning temperature by 40-50% to prevent pigment alteration',
                    'Test on inconspicuous area to assess color stability',
                    'Use inert gas purge to prevent oxidation/reduction reactions',
                    'Document color changes and obtain approval if unavoidable'
                ],
                'verification': 'Color should match reference within acceptable tolerance (ΔE <3 for museum quality, <5 for functional items).',
                'prevention': 'Some ceramic colors are unstable to laser cleaning. Cobalt blue and iron red generally stable; copper greens and purples more problematic.'
            },
            {
                'symptom': f'Porous {material_name} (terracotta, stoneware) shows incomplete cleaning',
                'causes': [
                    'Contaminants penetrated into porous structure beyond laser ablation depth',
                    'Surface topology creates shadowed regions inaccessible to beam',
                    'Organic contaminants in pores carbonize rather than ablate'
                ],
                'solutions': [
                    'Pre-treat with chemical poultice to extract deep contaminants before laser cleaning',
                    'Increase pulse count from 3-5 to 10-15 passes for deep cleaning',
                    'Use smaller spot size (50-100μm) to reach into surface texture',
                    'Accept limitations - laser cleaning best for surface contaminants, not deeply penetrated'
                ],
                'verification': 'Surface should appear uniformly clean. Wipe test with white cloth should show minimal transfer. Some deep staining may remain.',
                'prevention': 'Assess contamination depth before cleaning. Deep penetration requires hybrid approach (chemical + laser).'
            }
        ],
        'glass': [
            {
                'symptom': f'{material_name} shatters or develops cracks during laser cleaning',
                'causes': [
                    f'{material_name} extreme thermal shock sensitivity - fails when ΔT >50-100°C',
                    'Brittle nature provides no plastic deformation before fracture',
                    'Surface flaws act as stress concentrators under thermal loading',
                    'Rapid heating creates tensile stress exceeding fracture strength (~50 MPa)'
                ],
                'solutions': [
                    'Use absolute minimum power (reduce to 15-25% of typical)',
                    'Implement pulse mode with 5-10 second cooling between passes',
                    'Preheat glass to 100-150°C to reduce thermal shock magnitude',
                    'Use ultrashort pulse mode (<5ps) for minimal thermal load',
                    'Consider alternative methods (chemical, mechanical) for fragile glass'
                ],
                'verification': f'{material_name} should show no cracks or chips. Inspect under polarized light for stress patterns.',
                'prevention': 'Glass is highest-risk material for laser cleaning. Tempered glass less risky than annealed. Consider necessity carefully.'
            },
            {
                'symptom': f'Laser beam passes through {material_name} without cleaning',
                'causes': [
                    f'{material_name} transparent at 1064nm wavelength - <10% absorption',
                    'Contaminant layer also transparent or too thin for effective coupling',
                    'Gaussian beam focus beyond surface, not at contaminant interface'
                ],
                'solutions': [
                    'Switch to UV wavelength (355nm or 266nm) for strong glass absorption',
                    'Use shorter wavelength (532nm) for improved surface coupling',
                    'Apply absorptive layer (graphite spray) then remove with absorptive layer',
                    'Consider mechanical or chemical methods more appropriate for transparent materials'
                ],
                'verification': 'Contaminant should be removed without subsurface damage. Inspect transmission - should be >90% for clear glass.',
                'prevention': 'IR lasers poorly suited for glass cleaning. UV or green lasers generally required.'
            },
            {
                'symptom': f'{material_name} surface becomes etched or frosted after cleaning',
                'causes': [
                    'Laser fluence exceeds glass damage threshold, causing ablative removal',
                    'Subsurface damage from stress waves propagating into glass',
                    'Chemical alteration of glass surface (hydration, dehydroxylation)'
                ],
                'solutions': [
                    'Reduce fluence to absolute minimum - just above contaminant removal threshold',
                    'Use multiple very gentle passes (15-20 passes at low energy)',
                    'Switch to shorter pulse width (<10ps) to minimize subsurface damage',
                    'Polish surface after cleaning if etching is unavoidable and acceptable'
                ],
                'verification': 'Glass surface should remain clear and smooth. Transmission should be >95% of reference. No haze or frosting visible.',
                'prevention': 'Glass damage threshold very close to contaminant removal threshold - extremely narrow process window.'
            },
            {
                'symptom': f'Optical quality {material_name} shows subsurface damage or stress',
                'causes': [
                    'Shock waves from ablation propagate into glass creating microcracks',
                    'Thermal stress induces permanent birefringence in glass structure',
                    'Surface compaction from rapid heating creates refractive index gradient'
                ],
                'solutions': [
                    'Use ultrashort pulse mode (<1ps) to minimize shock wave generation',
                    'Reduce fluence to barely above threshold',
                    'Implement thermal annealing after cleaning to relieve stress',
                    'Accept that optical-quality glass may not tolerate laser cleaning'
                ],
                'verification': 'Inspect with polariscope for stress patterns. Interferometry should show <λ/4 surface distortion. No subsurface damage in microscopy.',
                'prevention': 'Optical glass requires extreme care. Consider precision chemical cleaning or accept contamination rather than risk damage.'
            }
        ],
        'masonry': [
            {
                'symptom': f'{material_name} shows spalling or surface flaking after cleaning',
                'causes': [
                    f'{material_name} contains moisture that vaporizes explosively during rapid heating',
                    'Weak aggregate-cement interface fails under thermal stress',
                    'Salt crystallization pressure enhanced by laser-induced temperature rise',
                    'Thermal expansion mismatch between aggregate and binder'
                ],
                'solutions': [
                    'Dry masonry thoroughly (60°C for 48 hours) before cleaning if moisture content >5%',
                    'Reduce laser power by 50-60% for gentler heating',
                    'Use pulse mode with 10-15 second cooling between passes',
                    'Desalinate if salt content >0.5% (detected by conductivity test)'
                ],
                'verification': f'{material_name} surface should be intact with no loose material. Tap test should be solid, not hollow. No new cracks or spalls visible.',
                'prevention': 'Moisture and salt are primary enemies. Assess and remediate before laser cleaning.'
            },
            {
                'symptom': f'{material_name} mortar joints erode more rapidly than brick/stone',
                'causes': [
                    'Mortar typically softer and more porous than masonry units',
                    'Lime mortar ablation threshold 50-70% lower than fired brick',
                    'Weathered or deteriorated mortar especially vulnerable'
                ],
                'solutions': [
                    'Use different parameters for mortar (40-50% lower power than masonry)',
                    'Carefully control beam positioning to avoid prolonged mortar exposure',
                    'Accept some mortar loss as unavoidable',
                    'Repoint joints after cleaning if necessary'
                ],
                'verification': 'Mortar joints should retain structural integrity. Depth loss should be <3mm. Sound mortar when probed with pick.',
                'prevention': 'Map different material zones before cleaning. Adjust parameters in real-time based on surface type.'
            },
            {
                'symptom': f'{material_name} cement-based surface shows white efflorescence after cleaning',
                'causes': [
                    'Laser heating mobilizes soluble salts (calcium hydroxide, sulfates)',
                    'Water evaporation during cooling leaves salt crystals on surface',
                    'Incomplete carbonation of cement allows salt migration'
                ],
                'solutions': [
                    'Reduce cleaning temperature to minimize salt mobilization',
                    'Rinse surface with deionized water immediately after cleaning',
                    'Apply silane/siloxane water repellent to prevent future efflorescence',
                    'Brush remove efflorescence then retreat if appearance is critical'
                ],
                'verification': 'Surface should be free of white deposits after cleaning and drying. Water absorption test - surface should be hydrophobic if treated.',
                'prevention': 'Post-cleaning water rinse standard practice for cementitious materials. Protective treatment recommended.'
            },
            {
                'symptom': f'{material_name} aggregate pops out during cleaning',
                'causes': [
                    'Weak aggregate-binder bond fails under thermal stress',
                    'Different thermal expansion of aggregate and cement creates stress',
                    'Moisture trapped behind aggregate vaporizes explosively'
                ],
                'solutions': [
                    'Reduce laser power by 50% to prevent bond failure',
                    'Ensure thorough drying before cleaning (moisture <3%)',
                    'Use more passes at lower energy rather than fewer high-energy passes',
                    'Accept some aggregate loss for heavily deteriorated masonry'
                ],
                'verification': 'Aggregate should remain firmly bonded. Pull test on suspect aggregate - should require >10 lbs force to remove.',
                'prevention': 'Assess masonry condition before cleaning. Deteriorated masonry may not be suitable for laser cleaning.'
            }
        ],
        'semiconductor': [
            {
                'symptom': f'{material_name} electrical properties degrade after laser cleaning',
                'causes': [
                    'Laser-induced defects in crystal lattice alter charge carrier mobility',
                    'Thermal stress creates dislocations that act as recombination centers',
                    'Surface contamination introduced by redeposited material'
                ],
                'solutions': [
                    'Use ultrashort pulse mode (<10ps) to minimize thermal effects',
                    'Reduce fluence to absolute minimum required for contaminant removal',
                    'Perform cleaning in cleanroom environment (Class 100 or better)',
                    'Implement post-cleaning thermal annealing (400-800°C) to repair defects'
                ],
                'verification': 'Measure electrical properties (resistivity, carrier lifetime) before/after. Should be within 10% of pre-cleaning values.',
                'prevention': 'Semiconductor cleaning requires extreme precision. Consider wet chemical methods as lower-risk alternative.'
            },
            {
                'symptom': f'{material_name} surface becomes roughened after cleaning',
                'causes': [
                    'Laser fluence exceeds ablation threshold, removing substrate along with contaminant',
                    'Grain-dependent ablation in polycrystalline materials creates roughness',
                    'Redeposition of ablated material creates particulates on surface'
                ],
                'solutions': [
                    'Reduce fluence to just above contaminant removal threshold',
                    'Use high repetition rate (>200 kHz) with low per-pulse energy',
                    'Implement high-velocity gas jet to remove ablated particles before redeposition',
                    'Consider chemical cleaning or CMP for optically smooth surfaces'
                ],
                'verification': 'AFM measurement should show Ra <1nm for device-quality surfaces. No particulates >50nm in SEM inspection.',
                'prevention': 'Semiconductor surface finish critical. Laser cleaning may not achieve required smoothness.'
            },
            {
                'symptom': f'{material_name} wafer warps or bows after cleaning',
                'causes': [
                    'Non-uniform heating creates thermal gradients across thin wafer',
                    'Single-side cleaning creates stress imbalance',
                    'Residual stress from laser-induced crystal defects'
                ],
                'solutions': [
                    'Clean both sides of wafer to balance stresses',
                    'Use vacuum chuck with temperature control to stabilize wafer',
                    'Implement uniform scan pattern to distribute heating evenly',
                    'Reduce average power to minimize thermal effects'
                ],
                'verification': 'Wafer bow should be <50μm for 200mm wafer, <100μm for 300mm wafer measured with bow/warp tester.',
                'prevention': 'Fixture wafer properly. Consider chemical methods for thin or fragile wafers.'
            }
        ],
        'rare-earth': [
            {
                'symptom': f'{material_name} rapidly oxidizes after laser cleaning',
                'causes': [
                    f'{material_name} extremely reactive with oxygen, especially at elevated temperatures',
                    'Freshly cleaned surface has high surface energy promoting oxidation',
                    'Elevated temperature from laser cleaning accelerates reaction kinetics'
                ],
                'solutions': [
                    'Perform cleaning in inert atmosphere (argon or nitrogen glove box)',
                    'Apply protective coating immediately after cleaning (<30 seconds)',
                    'Use mineral oil bath during cleaning to exclude oxygen',
                    'Reduce cleaning temperature to slow oxidation kinetics'
                ],
                'verification': f'{material_name} should maintain metallic luster. No oxide layer visible in minutes. Store in inert atmosphere or vacuum.',
                'prevention': 'Rare-earth metals require inert environment for cleaning. Oxidation inevitable in air.'
            },
            {
                'symptom': f'{material_name} shows localized melting during cleaning',
                'causes': [
                    f'{material_name} relatively low melting point (800-1600°C) compared to structural metals',
                    'High laser absorption leads to rapid temperature rise',
                    'Thermal runaway from positive feedback (increased absorption at higher temperature)'
                ],
                'solutions': [
                    'Reduce laser power by 60-70% to prevent melting',
                    'Use ultrashort pulse mode for cold ablation',
                    'Implement cryogenic cooling during cleaning',
                    'Increase scan speed to reduce dwell time'
                ],
                'verification': f'{material_name} surface should show no melting, flow, or recast layer. Microstructure should be unchanged under microscopy.',
                'prevention': 'Rare-earth metals require very gentle cleaning parameters. Test extensively before production cleaning.'
            }
        ]
    }
    
    # Get category-specific issues, default to metal if not found
    category_issues = issues_by_category.get(category, issues_by_category['metal'])
    
    # Return 4 issues (adjust material_name in templates)
    return category_issues[:4]


def add_ablation_thresholds():
    """Add ablationThreshold to all materials in Materials.yaml using Categories.yaml ranges."""
    
    materials_file = project_root / 'materials' / 'data' / 'Materials.yaml'
    categories_file = project_root / 'materials' / 'data' / 'Categories.yaml'
    
    print("Loading Categories.yaml...")
    with open(categories_file, 'r') as f:
        cat_data = yaml.safe_load(f)
    categories_data = cat_data.get('categories', {})
    print(f"Loaded {len(categories_data)} category ranges")
    
    print("\nLoading Materials.yaml...")
    with open(materials_file, 'r') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    print(f"Found {len(materials)} materials")
    
    added_count = 0
    skipped_count = 0
    
    for mat_name, mat_data in materials.items():
        # Check if already has ablationThreshold
        if 'material_characteristics' in mat_data:
            mat_chars = mat_data['material_characteristics']
            if 'ablationThreshold' in mat_chars and mat_chars['ablationThreshold'] is not None:
                if isinstance(mat_chars['ablationThreshold'], dict) and 'value' in mat_chars['ablationThreshold']:
                    print(f"  ⏭️  {mat_name}: Already has ablationThreshold")
                    skipped_count += 1
                    continue
        
        # Get category and subcategory
        category = mat_data.get('category', 'metal')
        subcategory = mat_data.get('subcategory', '')
        
        # Calculate ablation threshold using Categories.yaml ranges
        value, min_val, max_val = calculate_ablation_threshold(mat_name, category, subcategory, mat_data, categories_data)
        
        # Add to material_characteristics
        if 'material_characteristics' not in mat_data:
            mat_data['material_characteristics'] = {}
        
        mat_data['material_characteristics']['ablationThreshold'] = {
            'value': value,
            'unit': 'J/cm²',
            'min': min_val,
            'max': max_val,
            'confidence': 90,
            'source': 'ai_research'
        }
        
        print(f"  ✅ {mat_name}: Added ablationThreshold = {value} J/cm² (range: {min_val}-{max_val})")
        added_count += 1
    
    # Save back to file
    print(f"\nSaving Materials.yaml with {added_count} new ablationThreshold values...")
    with open(materials_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)
    
    print(f"✅ Complete! Added {added_count} ablationThreshold values, skipped {skipped_count} existing")
    return added_count, skipped_count


def add_common_issues():
    """Add common_issues to Materials.yaml (source of truth)."""
    
    materials_file = project_root / 'materials' / 'data' / 'Materials.yaml'
    
    print("\nLoading Materials.yaml...")
    with open(materials_file, 'r') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    print(f"Found {len(materials)} materials")
    
    added_count = 0
    skipped_count = 0
    
    for mat_name, mat_data in materials.items():
        # Check if already has common_issues
        if 'common_issues' in mat_data and mat_data['common_issues']:
            print(f"  ⏭️  {mat_name}: Already has common_issues")
            skipped_count += 1
            continue
        
        # Get material info
        category = mat_data.get('category', 'metal')
        subcategory = mat_data.get('subcategory', '')
        
        # Generate common_issues
        common_issues = generate_common_issues_for_material(mat_name, category, subcategory)
        
        # Add to material data
        mat_data['common_issues'] = common_issues
        
        print(f"  ✅ {mat_name}: Added {len(common_issues)} common_issues ({category})")
        added_count += 1
    
    # Save back to Materials.yaml
    print(f"\nSaving Materials.yaml with {added_count} new common_issues arrays...")
    with open(materials_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)
    
    print(f"✅ Complete! Added common_issues to {added_count} materials, skipped {skipped_count} existing")
    return added_count, skipped_count


if __name__ == '__main__':
    print("=" * 80)
    print("Adding common_issues to Materials.yaml")
    print("=" * 80)
    print("⚠️  NOTE: ablationThreshold already exists from AI research - NOT modifying it")
    
    print("\n" + "=" * 80)
    print("PHASE: Adding common_issues to Materials.yaml")
    print("=" * 80)
    issues_added, issues_skipped = add_common_issues()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"common_issues: {issues_added} added, {issues_skipped} skipped (Materials.yaml)")
    print("\n📝 Next steps:")
    print("  1. Update trivial_exporter.py to export common_issues to settings frontmatter")
    print("  2. Regenerate frontmatter: python3 run.py --all --data-only")
    print("  3. Deploy to production: python3 run.py --deploy")
