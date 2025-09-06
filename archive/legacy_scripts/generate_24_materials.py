#!/usr/bin/env python3
"""
Generate the first 24 materials with their assigned authors and word count limits.
Each author has different word count constraints:
- Taiwan (Author 1): 380 words max
- Italy (Author 2): 450 words max
- Indonesia (Author 3): 250 words max
- USA (Author 4): 320 words max
"""

import subprocess
import sys
import time
from pathlib import Path

# First 24 materials with their assigned authors
MATERIALS_TO_GENERATE = [
    ("Alumina", 2),  # Italy - 450 words
    ("Porcelain", 3),  # Indonesia - 250 words
    ("Silicon Carbide", 1),  # Taiwan - 380 words
    ("Stoneware", 4),  # USA - 320 words
    ("Zirconia", 2),  # Italy - 450 words
    ("Pyrex", 1),  # Taiwan - 380 words
    ("Borosilicate Glass", 3),  # Indonesia - 250 words
    ("Fused Silica", 4),  # USA - 320 words
    ("Quartz Glass", 2),  # Italy - 450 words
    ("Float Glass", 1),  # Taiwan - 380 words
    ("Lead Crystal", 3),  # Indonesia - 250 words
    ("Tempered Glass", 4),  # USA - 320 words
    ("Soda-lime Glass", 2),  # Italy - 450 words
    ("Fiberglass", 1),  # Taiwan - 380 words
    ("Carbon Fiber Reinforced Polymer", 3),  # Indonesia - 250 words
    ("Glass Fiber Reinforced Polymers (GFRP)", 4),  # USA - 320 words
    ("Kevlar Reinforced Polymer", 2),  # Italy - 450 words
    ("Epoxy Resin Composites", 1),  # Taiwan - 380 words
    ("Polyester Resin Composites", 3),  # Indonesia - 250 words
    ("Phenolic Resin Composites", 4),  # USA - 320 words
    ("Urethane Composites", 2),  # Italy - 450 words
    ("Fiber Reinforced Polyurethane (FRPU)", 1),  # Taiwan - 380 words
    ("Metal Matrix Composites (MMCs)", 3),  # Indonesia - 250 words
    ("Ceramic Matrix Composites (CMCs)", 4),  # USA - 320 words
]

AUTHOR_LIMITS = {
    1: ("Taiwan", 380),
    2: ("Italy", 450),
    3: ("Indonesia", 250),
    4: ("USA", 320),
}


def run_generation(material_name, author_id):
    """Run content generation for a single material."""
    author_country, word_limit = AUTHOR_LIMITS[author_id]

    print(f"\n🔧 Generating: {material_name}")
    print(f"👤 Author {author_id} ({author_country}) - {word_limit} word limit")
    print("=" * 80)

    try:
        # Run the generation command
        cmd = [
            "python3",
            "run.py",
            "--material",
            material_name,
            "--components",
            "content",
            "--author",
            str(author_id),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            print(f"✅ SUCCESS: {material_name}")
            # Extract word count from output if available
            for line in result.stdout.split("\n"):
                if "Generated content:" in line and "words" in line:
                    print(f"📝 {line.strip()}")
                    break
            return True
        else:
            print(f"❌ FAILED: {material_name}")
            print(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏱️ TIMEOUT: {material_name} (exceeded 120 seconds)")
        return False
    except Exception as e:
        print(f"💥 ERROR: {material_name} - {e}")
        return False


def main():
    """Generate all 24 materials."""
    print("🚀 GENERATING FIRST 24 MATERIALS")
    print("=" * 80)
    print("Author Word Count Limits:")
    for author_id, (country, limit) in AUTHOR_LIMITS.items():
        print(f"  Author {author_id} ({country}): {limit} words maximum")
    print("=" * 80)

    # Clear content directory first
    content_dir = Path("content/components/content")
    if content_dir.exists():
        print(f"\n🧹 Clearing {content_dir}...")
        for file in content_dir.glob("*.md"):
            file.unlink()
        print("✅ Content directory cleared")

    successful = 0
    failed = 0

    start_time = time.time()

    for i, (material_name, author_id) in enumerate(MATERIALS_TO_GENERATE, 1):
        print(f"\n📊 Progress: {i}/24 materials")

        if run_generation(material_name, author_id):
            successful += 1
        else:
            failed += 1

        # Small delay between generations
        if i < len(MATERIALS_TO_GENERATE):
            time.sleep(2)

    end_time = time.time()
    duration = end_time - start_time

    # Final summary
    print("\n" + "=" * 80)
    print("📋 GENERATION SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(MATERIALS_TO_GENERATE)}")
    print(f"⏱️ Duration: {duration:.1f} seconds")
    print(f"📈 Success Rate: {(successful/len(MATERIALS_TO_GENERATE)*100):.1f}%")

    if failed > 0:
        print(f"\n⚠️ {failed} materials failed. Check logs above for details.")
        return 1
    else:
        print(f"\n🎉 All {successful} materials generated successfully!")
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Generation interrupted by user")
        sys.exit(1)
