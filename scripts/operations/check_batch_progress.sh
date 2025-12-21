#!/bin/bash
# Quick batch progress checker for contaminant regeneration

python3 << 'ENDSCRIPT'
import yaml

with open('data/contaminants/Contaminants.yaml', 'r') as f:
    data = yaml.safe_load(f)

patterns = data['contamination_patterns']

# Count by word count ranges
short = []
regenerated = []

for pid, pdata in patterns.items():
    desc = str(pdata.get('description', ''))
    wc = len(desc.split())
    if wc < 50:
        short.append((pid, wc))
    elif wc >= 50 and wc <= 150:
        regenerated.append((pid, wc))

original_target = 58
completed = original_target - len(short)
progress_pct = (completed / original_target) * 100

print(f"📊 BATCH PROGRESS")
print(f"=" * 50)
print(f"✅ Completed: {completed}/{original_target} ({progress_pct:.1f}%)")
print(f"⏳ Remaining: {len(short)}")
print()

if regenerated:
    word_counts = [wc for _, wc in regenerated]
    avg = sum(word_counts) / len(word_counts)
    print(f"📈 Average word count: {avg:.1f} words")
    print(f"📈 Range: {min(word_counts)}-{max(word_counts)} words")

print(f"=" * 50)
ENDSCRIPT
