#!/usr/bin/env python3
"""
Manual Image Feedback Tool

Capture manual feedback on generated images and log to SQLite for learning.
Automatically REWRITES feedback into Imagen 4-effective visual language.

Usage:
    python3 domains/materials/image/tools/add_feedback.py --material Steel --feedback "Rotation angle too small"
    python3 domains/materials/image/tools/add_feedback.py --material Steel --category physics --feedback "Object floating"
    python3 domains/materials/image/tools/add_feedback.py --image public/images/materials/Steel.png --feedback "Wrong background"
    python3 domains/materials/image/tools/add_feedback.py --list  # Show recent feedback
    python3 domains/materials/image/tools/add_feedback.py --search "rotation"  # Search feedback
    python3 domains/materials/image/tools/add_feedback.py --no-rewrite  # Skip auto-rewrite

Author: AI Assistant
Date: November 29, 2025
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from shared.image.learning import create_logger
from domains.materials.image.learning.feedback_rewriter import FeedbackRewriter


# Feedback categories for classification
FEEDBACK_CATEGORIES = [
    'physics',       # Gravity, lighting, shadows wrong
    'rotation',      # Horizontal rotation issues
    'contamination', # Wrong type, distribution, thickness
    'object',        # Wrong shape, material appearance
    'background',    # Setting/environment issues
    'composition',   # Layout, split-view problems
    'realism',       # General unrealistic appearance
    'text',          # Unwanted text/labels in image
    'other'          # Anything else
]


def add_manual_feedback(
    logger,
    material: str,
    feedback_text: str,
    category: str = 'other',
    image_path: str = None,
    score_override: int = None
):
    """
    Add manual feedback to the learning database.
    
    Creates a special entry in generation_attempts with source='manual_feedback'.
    """
    import sqlite3
    from datetime import datetime
    
    conn = sqlite3.connect(logger.db_path)
    cursor = conn.cursor()
    
    timestamp = datetime.utcnow().isoformat()
    attempt_id = f"manual_{timestamp.replace(':', '-').replace('.', '-')}"
    
    # Insert manual feedback as a special generation attempt
    cursor.execute("""
        INSERT INTO generation_attempts (
            id, timestamp, material, category,
            feedback_applied, feedback_text, feedback_category, feedback_source,
            passed, realism_score, notes, image_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        attempt_id,
        timestamp,
        material,
        'manual_feedback',  # Special category marker
        True,  # feedback_applied
        feedback_text,
        category,
        'user_manual',  # Source identifier
        False if score_override is None else (score_override >= 75),
        score_override or 0,
        f"Manual feedback added via CLI",
        image_path
    ))
    
    conn.commit()
    conn.close()
    
    return attempt_id


def list_recent_feedback(logger, limit: int = 10):
    """List recent manual feedback entries."""
    import sqlite3
    
    conn = sqlite3.connect(logger.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT timestamp, material, feedback_category, feedback_text, image_path
        FROM generation_attempts
        WHERE feedback_source = 'user_manual'
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows


def search_feedback(logger, search_term: str):
    """Search feedback entries by text."""
    import sqlite3
    
    conn = sqlite3.connect(logger.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT timestamp, material, feedback_category, feedback_text, realism_score, passed
        FROM generation_attempts
        WHERE feedback_text LIKE ?
        ORDER BY timestamp DESC
        LIMIT 20
    """, (f"%{search_term}%",))
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows


def get_feedback_stats(logger):
    """Get statistics on feedback by category."""
    import sqlite3
    
    conn = sqlite3.connect(logger.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT feedback_category, COUNT(*) as count
        FROM generation_attempts
        WHERE feedback_category IS NOT NULL AND feedback_category != ''
        GROUP BY feedback_category
        ORDER BY count DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Add manual feedback on generated images for learning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Add feedback for a material:
    python3 add_feedback.py --material Steel --feedback "Rotation angle too small"
    
  Add categorized feedback:
    python3 add_feedback.py --material Aluminum --category physics --feedback "Shadow direction wrong"
    
  Add feedback with image path:
    python3 add_feedback.py --image public/images/materials/Steel.png --feedback "Background too bright"
    
  List recent feedback:
    python3 add_feedback.py --list
    
  Search feedback:
    python3 add_feedback.py --search "rotation"
    
  View feedback statistics:
    python3 add_feedback.py --stats

Categories: """ + ", ".join(FEEDBACK_CATEGORIES)
    )
    
    # Feedback input options
    parser.add_argument('--material', '-m', type=str, help='Material name (e.g., Steel, Aluminum)')
    parser.add_argument('--feedback', '-f', type=str, help='Feedback text describing the issue')
    parser.add_argument('--category', '-c', type=str, choices=FEEDBACK_CATEGORIES, default='other',
                       help='Feedback category for classification')
    parser.add_argument('--image', '-i', type=str, help='Path to the image file')
    parser.add_argument('--score', '-s', type=int, help='Optional quality score override (0-100)')
    parser.add_argument('--no-rewrite', action='store_true', 
                       help='Skip automatic feedback rewriting (use original text)')
    parser.add_argument('--material-category', type=str, default=None,
                       help='Material category for better rewriting (wood, metal, stone, etc.)')
    
    # Query options
    parser.add_argument('--list', '-l', action='store_true', help='List recent manual feedback')
    parser.add_argument('--search', type=str, help='Search feedback by text')
    parser.add_argument('--stats', action='store_true', help='Show feedback statistics by category')
    parser.add_argument('--limit', type=int, default=10, help='Number of results to show (default: 10)')
    
    args = parser.parse_args()
    
    # Create logger
    logger = create_logger()
    
    # Handle list command
    if args.list:
        print("\n📋 RECENT MANUAL FEEDBACK")
        print("=" * 70)
        
        rows = list_recent_feedback(logger, args.limit)
        if not rows:
            print("\n   No manual feedback recorded yet.")
        else:
            for row in rows:
                ts, material, cat, text, img = row
                ts_short = ts[:16] if ts else "?"
                print(f"\n   [{ts_short}] {material or 'Unknown'} ({cat or 'other'})")
                print(f"   → {text[:80]}{'...' if len(text or '') > 80 else ''}")
                if img:
                    print(f"   📷 {img}")
        print("\n" + "=" * 70)
        return
    
    # Handle search command
    if args.search:
        print(f"\n🔍 SEARCHING FEEDBACK FOR: '{args.search}'")
        print("=" * 70)
        
        rows = search_feedback(logger, args.search)
        if not rows:
            print(f"\n   No feedback found containing '{args.search}'")
        else:
            for row in rows:
                ts, material, cat, text, score, passed = row
                ts_short = ts[:16] if ts else "?"
                status = "✅" if passed else "❌"
                print(f"\n   [{ts_short}] {material or 'Unknown'} - {score}/100 {status}")
                print(f"   Category: {cat or 'other'}")
                print(f"   → {text[:100]}{'...' if len(text or '') > 100 else ''}")
        print("\n" + "=" * 70)
        return
    
    # Handle stats command
    if args.stats:
        print("\n📊 FEEDBACK STATISTICS BY CATEGORY")
        print("=" * 70)
        
        rows = get_feedback_stats(logger)
        if not rows:
            print("\n   No feedback recorded yet.")
        else:
            total = sum(r[1] for r in rows)
            print(f"\n   Total feedback entries: {total}\n")
            for cat, count in rows:
                pct = count / total * 100 if total > 0 else 0
                bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                print(f"   {cat or 'uncategorized':<15} {bar} {count:4} ({pct:.1f}%)")
        print("\n" + "=" * 70)
        return
    
    # Adding new feedback requires material and feedback text
    if not args.feedback:
        parser.error("--feedback is required when adding new feedback")
    
    # Get material from image path if not provided
    material = args.material
    if not material and args.image:
        # Try to extract material from image filename
        img_path = Path(args.image)
        material = img_path.stem.split('_')[0]  # e.g., "Steel_outdoor.png" -> "Steel"
    
    if not material:
        parser.error("--material or --image is required")
    
    # Rewrite feedback for Imagen 4 effectiveness (unless --no-rewrite)
    original_feedback = args.feedback
    rewritten_feedback = args.feedback
    rewrite_changes = []
    
    if not args.no_rewrite:
        rewriter = FeedbackRewriter()
        # Use provided category or try to infer from material
        mat_category = args.material_category
        if not mat_category:
            # Common material-to-category mappings
            mat_lower = material.lower()
            if any(w in mat_lower for w in ['oak', 'pine', 'maple', 'walnut', 'wood', 'lumber', 'timber']):
                mat_category = 'wood'
            elif any(w in mat_lower for w in ['steel', 'aluminum', 'copper', 'iron', 'brass', 'metal', 'bronze']):
                mat_category = 'metal'
            elif any(w in mat_lower for w in ['granite', 'marble', 'concrete', 'stone', 'brick']):
                mat_category = 'stone'
            elif any(w in mat_lower for w in ['glass', 'window']):
                mat_category = 'glass'
            else:
                mat_category = 'default'
        
        rewritten_feedback, rewrite_changes = rewriter.rewrite(original_feedback, mat_category)
        
        # Show the rewrite report
        if rewrite_changes:
            report = rewriter.format_rewrite_report(
                original_feedback, rewritten_feedback, rewrite_changes, mat_category
            )
            print(report)
    
    # Add the feedback (use rewritten version)
    attempt_id = add_manual_feedback(
        logger,
        material=material,
        feedback_text=rewritten_feedback,  # Use rewritten version
        category=args.category,
        image_path=args.image,
        score_override=args.score
    )
    
    print("\n✅ FEEDBACK RECORDED")
    print("=" * 70)
    print(f"   Material: {material}")
    print(f"   Category: {args.category}")
    if rewrite_changes:
        print(f"   Original: {original_feedback}")
        print(f"   Rewritten: {rewritten_feedback}")
    else:
        print(f"   Feedback: {rewritten_feedback}")
    if args.image:
        print(f"   Image: {args.image}")
    if args.score:
        print(f"   Score: {args.score}/100")
    print(f"   ID: {attempt_id}")
    print("\n   This feedback will be used for learning and analytics.")
    print("   View with: python3 add_feedback.py --list")
    print("=" * 70)


if __name__ == "__main__":
    main()
