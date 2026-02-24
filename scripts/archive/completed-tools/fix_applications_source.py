"""Fix Applications.yaml: rename all 10 keys + update id/slug/fullPath to include -applications suffix.

Structure: data['applications'] is a dict with keys like 'aerospace-laser-cleaning'.
Each item has id, slug, fullPath fields that need the '-applications' suffix appended.
"""
import re
from pathlib import Path

path = Path('data/applications/Applications.yaml')
raw = path.read_text()

RENAMES = [
    ('aerospace-laser-cleaning',                'aerospace-laser-cleaning-applications'),
    ('automotive-laser-cleaning',               'automotive-laser-cleaning-applications'),
    ('electronics-laser-cleaning',              'electronics-laser-cleaning-applications'),
    ('medical-devices-laser-cleaning',          'medical-devices-laser-cleaning-applications'),
    ('energy-power-laser-cleaning',             'energy-power-laser-cleaning-applications'),
    ('rail-transport-laser-cleaning',           'rail-transport-laser-cleaning-applications'),
    ('shipbuilding-marine-laser-cleaning',       'shipbuilding-marine-laser-cleaning-applications'),
    ('construction-equipment-laser-cleaning',   'construction-equipment-laser-cleaning-applications'),
    ('food-processing-laser-cleaning',          'food-processing-laser-cleaning-applications'),
    ('defense-laser-cleaning',                  'defense-laser-cleaning-applications'),
]

# Apply renames as exact string replacements.
# Order matters: longer keys first to avoid partial matches.
# Sort by length descending so e.g. 'energy-power-laser-cleaning' is replaced
# before any shorter overlapping substring (there are none here, but be safe).
modified = raw
count = 0
for old_key, new_key in sorted(RENAMES, key=lambda x: -len(x[0])):
    before = modified
    modified = modified.replace(old_key, new_key)
    occurrences = before.count(old_key)
    count += occurrences
    print(f'  {old_key} -> {new_key}  ({occurrences} occurrences replaced)')

path.write_text(modified)
print(f'\nDone. {count} total occurrences replaced in Applications.yaml')
