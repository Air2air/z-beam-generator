#!/bin/bash
# Quick status check for Phase 3 association research

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔬 PHASE 3 QUICK STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if process is running
if ps aux | grep -q "[c]ontaminant_association_researcher"; then
    echo "✅ Research process: RUNNING"
    PID=$(ps aux | grep "[c]ontaminant_association_researcher" | awk '{print $2}')
    echo "   PID: $PID"
else
    echo "⏹️  Research process: STOPPED"
fi

echo ""
python3 scripts/research/monitor_association_progress.py

echo ""
echo "📋 Commands:"
echo "   Watch progress:  watch -n 10 python3 scripts/research/monitor_association_progress.py"
echo "   View log:        tail -f association_research.log"
echo "   Stop process:    kill $PID"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
