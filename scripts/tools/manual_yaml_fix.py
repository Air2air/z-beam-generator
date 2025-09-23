#!/usr/bin/env python3
"""
Manual YAML Fix - Targeted fixes for specific frontmatter parsing issues.
"""

from pathlib import Path

def fix_pyrex_file():
    """Fix the specific YAML issues in pyrex file"""
    file_path = Path("content/components/frontmatter/pyrex-laser-cleaning.md")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the broken formula on lines 12-13
    content = content.replace(
        '  formula: "Approx. 80.6% SiO₂, 12.6% B₂O₃, 4.2% Na₂O, 2.2% Al₂"\n    O₃, 0.04% Fe₂O₃, 0.1% CaO, 0.05% MgO, 0.01% K₂O"',
        '  formula: "Approx. 80.6% SiO₂, 12.6% B₂O₃, 4.2% Na₂O, 2.2% Al₂O₃, 0.04% Fe₂O₃, 0.1% CaO, 0.05% MgO, 0.01% K₂O"'
    )
    
    # Fix the broken chemicalFormula on lines 78-79
    content = content.replace(
        '  chemicalFormula: "Complex oxide mixture (primarily SiO₂-B₂O₃-Na₂"\n    O)"',
        '  chemicalFormula: "Complex oxide mixture (primarily SiO₂-B₂O₃-Na₂O)"'
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed pyrex file")

def fix_stoneware_file():
    """Fix the specific YAML issues in stoneware file"""
    file_path = Path("content/components/frontmatter/stoneware-laser-cleaning.md")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the broken formula
    content = content.replace(
        '  formula: "Variable composition (primarily SiO₂-Al₂O₃-K₂O-Na₂"\n    O-CaO system)"',
        '  formula: "Variable composition (primarily SiO₂-Al₂O₃-K₂O-Na₂O-CaO system)"'
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed stoneware file")

def fix_terracotta_file():
    """Fix the specific YAML issues in terracotta file"""
    file_path = Path("content/components/frontmatter/terracotta-laser-cleaning.md")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the broken formula
    content = content.replace(
        'symbol: N/A (composite material)\n  formula: "Clay (Al₂O₃-SiO₂), Fe₂O₃ (colorant), SiO₂ (sand temper\n    )"',
        'symbol: "N/A (composite material)"\n  formula: "Clay (Al₂O₃-SiO₂), Fe₂O₃ (colorant), SiO₂ (sand temper)"'
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed terracotta file")

if __name__ == "__main__":
    print("🔧 Applying manual YAML fixes to critical files...")
    fix_pyrex_file()
    fix_stoneware_file() 
    fix_terracotta_file()
    print("🎉 Manual fixes complete!")
