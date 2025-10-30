#!/usr/bin/env python3
"""
Fix thermal diffusivity calculation errors.

Thermal diffusivity formula: α = k / (ρ × Cp)
where:
- α = thermal diffusivity (mm²/s)
- k = thermal conductivity (W/(m·K))
- ρ = density (g/cm³) → convert to kg/m³ by × 1000
- Cp = specific heat (J/(kg·K))

Result in mm²/s: α = (k / (ρ × Cp)) × 10^6
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime
import shutil

def backup_files(files_to_backup):
    """Create backup of files"""
    if not files_to_backup:
        return None
        
    backup_dir = Path("backups/thermal_diffusivity_fixes_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    for file_path in files_to_backup:
        file_path = file_path.resolve()
        cwd = Path.cwd().resolve()
        
        relative_path = file_path.relative_to(cwd)
        backup_path = backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(file_path, backup_path)
    
    return backup_dir

def calculate_thermal_diffusivity(conductivity, density, specific_heat):
    """
    Calculate thermal diffusivity from material properties.
    
    Args:
        conductivity: W/(m·K)
        density: g/cm³
        specific_heat: J/(kg·K)
    
    Returns:
        Thermal diffusivity in mm²/s
    """
    # Convert density from g/cm³ to kg/m³
    density_kg_m3 = density * 1000
    
    # Calculate: α = k / (ρ × Cp) in m²/s, then convert to mm²/s
    alpha_m2_s = conductivity / (density_kg_m3 * specific_heat)
    alpha_mm2_s = alpha_m2_s * 1e6
    
    return alpha_mm2_s

def fix_thermal_diffusivity(file_path, dry_run=False, error_threshold=20.0):
    """Fix thermal diffusivity if calculation error exceeds threshold"""
    
    with open(file_path) as f:
        data = yaml.safe_load(f)
    
    if not data or 'materialProperties' not in data:
        return None
    
    laser_props = data['materialProperties'].get('laser_material_interaction', {}).get('properties', {})
    char_props = data['materialProperties'].get('material_characteristics', {}).get('properties', {})
    
    diffusivity_data = laser_props.get('thermalDiffusivity', {})
    conductivity = laser_props.get('thermalConductivity', {}).get('value')
    specific_heat = laser_props.get('specificHeat', {}).get('value')
    density = char_props.get('density', {}).get('value')
    
    measured_diffusivity = diffusivity_data.get('value')
    
    if any(v is None for v in [measured_diffusivity, conductivity, specific_heat, density]):
        return None
    
    # Convert to float
    measured = float(measured_diffusivity)
    k = float(conductivity)
    rho = float(density)
    cp = float(specific_heat)
    
    # Calculate expected diffusivity
    calculated = calculate_thermal_diffusivity(k, rho, cp)
    
    # Calculate error percentage
    error = abs(calculated - measured) / calculated * 100 if calculated > 0 else float('inf')
    
    material = file_path.stem.replace('-laser-cleaning', '')
    category = data.get('category', 'unknown')
    
    # Only fix if error exceeds threshold
    if error < error_threshold:
        return {
            'material': material,
            'category': category,
            'measured': measured,
            'calculated': calculated,
            'error': error,
            'changed': False,
            'status': 'OK'
        }
    
    # Apply fix
    if not dry_run:
        # Round to 2 decimal places
        new_value = round(calculated, 2)
        diffusivity_data['value'] = new_value
        
        # Add metadata
        if 'metadata' not in diffusivity_data:
            diffusivity_data['metadata'] = {}
        
        diffusivity_data['metadata']['last_verified'] = datetime.now().isoformat()
        diffusivity_data['metadata']['verification_source'] = 'automatic_fix'
        diffusivity_data['metadata']['fix_reason'] = f'Recalculated: {k} / ({rho} × {cp}) = {new_value} mm²/s'
        diffusivity_data['metadata']['previous_value'] = measured
        
        # Write back
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    return {
        'material': material,
        'category': category,
        'measured': measured,
        'calculated': round(calculated, 2),
        'error': error,
        'changed': True,
        'k': k,
        'rho': rho,
        'cp': cp
    }

def main():
    dry_run = '--dry-run' in sys.argv
    error_threshold = 20.0  # Only fix if error > 20%
    
    print("=" * 80)
    print("THERMAL DIFFUSIVITY FIX")
    print("=" * 80)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE FIX'}")
    print(f"Error threshold: {error_threshold}%")
    print()
    
    frontmatter_dir = Path("content/frontmatter")
    files = list(frontmatter_dir.glob("*.yaml"))
    
    results = []
    files_to_backup = []
    
    for file_path in sorted(files):
        result = fix_thermal_diffusivity(file_path, dry_run=dry_run, error_threshold=error_threshold)
        if result:
            results.append(result)
            if result['changed']:
                files_to_backup.append(file_path)
    
    # Create backup
    if files_to_backup and not dry_run:
        backup_dir = backup_files(files_to_backup)
        print(f"✅ Backup created: {backup_dir}")
        print()
    
    # Separate results
    changed = [r for r in results if r['changed']]
    unchanged = [r for r in results if not r['changed']]
    
    # Print changes
    if changed:
        print(f"\n{'DRY RUN - WOULD CHANGE' if dry_run else 'CHANGED'}: {len(changed)} materials")
        print("-" * 80)
        for r in sorted(changed, key=lambda x: x['error'], reverse=True):
            print(f"{r['material']:<30} ({r['category']:<10}) "
                  f"Error: {r['error']:>10.1f}%  "
                  f"Measured: {r['measured']:>10.2f} → Calculated: {r['calculated']:>10.2f} mm²/s")
    
    print(f"\n✅ UNCHANGED (<{error_threshold}% error): {len(unchanged)} materials")
    
    # Summary by category
    if changed:
        print("\n" + "=" * 80)
        print("SUMMARY BY CATEGORY")
        print("=" * 80)
        
        by_category = {}
        for r in changed:
            cat = r['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(r)
        
        for cat, items in sorted(by_category.items()):
            avg_error = sum(i['error'] for i in items) / len(items)
            print(f"{cat}: {len(items)} materials fixed (avg error: {avg_error:.1f}%)")
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Total materials analyzed: {len(results)}")
    print(f"Materials fixed: {len(changed)}")
    print(f"Materials OK: {len(unchanged)}")
    
    if dry_run:
        print("\n⚠️  This was a DRY RUN - no files were modified")
        print("Run without --dry-run to apply fixes")
    else:
        print(f"\n✅ Fixes applied to {len(changed)} files")
        if files_to_backup:
            print("✅ Backup created in backups/ directory")

if __name__ == '__main__':
    main()
