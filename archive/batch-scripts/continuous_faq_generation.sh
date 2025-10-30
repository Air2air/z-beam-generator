#!/bin/bash
# Continuous FAQ Generation Script
# Generates FAQs in batches of 5 until all materials have them

echo "🚀 Starting continuous FAQ generation..."
echo "======================================"

batch_count=0

while true; do
    batch_count=$((batch_count + 1))
    echo ""
    echo "📦 Batch #$batch_count"
    echo "======================================"
    
    # Run the 5-material generator
    python3 generate_5_faqs.py 2>&1 | grep -E "(🎯|•|^\[|✅|❌|Batch)"
    
    # Check exit status
    if [ $? -ne 0 ]; then
        echo "❌ Generation failed, stopping..."
        break
    fi
    
    # Check how many materials still need FAQs
    remaining=$(python3 << 'EOF'
import yaml
with open('data/Materials.yaml', 'r') as f:
    data = yaml.safe_load(f)
materials = data['materials']
without_faq = sum(1 for mat in materials.values() if 'faq' not in mat or not mat['faq'])
print(without_faq)
EOF
)
    
    echo "📊 Remaining: $remaining materials"
    
    # If none remain, we're done
    if [ "$remaining" -eq "0" ]; then
        echo ""
        echo "🎉 ALL MATERIALS HAVE FAQs!"
        break
    fi
    
    # Brief pause between batches
    sleep 3
done

echo ""
echo "======================================"
echo "✅ Generation complete!"
echo "======================================"
