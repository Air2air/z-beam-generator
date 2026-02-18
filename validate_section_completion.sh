#!/bin/bash
# Validate that all relationship blocks have complete _section metadata

cd ../z-beam/frontmatter

echo "=== VALIDATION: _section Completeness ==="
echo ""

for domain in materials contaminants compounds settings applications; do
    echo "=== $domain domain ==="
    
    total_relationships=0
    complete_sections=0
    
    for file in $domain/*.yaml; do
        # Count relationships (excluding non-relationship fields)
        rels=$(awk '/^relationships:/,/^[a-z_]+:/ {
            if ($0 ~ /^  [a-z_]+:/ && $0 !~ /^    /) {
                print
            }
        }' "$file" | grep -v "relationships:" | wc -l | tr -d ' ')
        
        # Count complete _section blocks (has all 5 fields)
        secs=$(awk '/^relationships:/,/^[a-z_]+:/ {print}' "$file" | \
               awk '/_section:/{found=1; fields=0; next} 
                    found && /^      (title|description|icon|order|variant):/ {fields++} 
                    found && fields==5 {print; fields=0; found=0}' | wc -l | tr -d ' ')
        
        total_relationships=$((total_relationships + rels))
        complete_sections=$((complete_sections + secs))
    done
    
    echo "  Total relationships: $total_relationships"
    echo "  Complete _sections: $complete_sections"
    if [ "$total_relationships" -eq "$complete_sections" ]; then
        echo "  ✅ STATUS: COMPLETE (100%)"
    else
        pct=$((complete_sections * 100 / total_relationships))
        echo "  ⚠️  STATUS: ${pct}% complete"
    fi
    echo ""
done
