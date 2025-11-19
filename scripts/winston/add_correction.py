#!/usr/bin/env python3
"""
CLI Tool: Add Human Correction to Winston Feedback Database

This tool allows you to add human corrections to Winston detection results,
building a training dataset for future improvements.

Usage:
    # Add correction by detection ID
    python3 scripts/winston/add_correction.py --id 42 --corrected-text "Human-corrected version..." --type "prompt_refinement" --notes "Added more technical detail"
    
    # Interactive mode (prompts for all fields)
    python3 scripts/winston/add_correction.py --interactive
    
    # Add correction from file
    python3 scripts/winston/add_correction.py --id 42 --file corrected_text.txt --type "manual_edit"
    
Correction Types:
    - prompt_refinement: Improved generation through prompt changes
    - manual_edit: Direct human editing of generated content
    - temperature_adjustment: Temperature/settings tweaks
    - other: Other correction method
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
from generation.config.config_loader import get_config

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def add_correction_interactive(db: WinstonFeedbackDatabase) -> None:
    """Interactive mode for adding corrections."""
    print("\n=== Winston Feedback - Add Correction (Interactive Mode) ===\n")
    
    # Get detection ID
    while True:
        detection_id_str = input("Detection ID (from generation log): ").strip()
        try:
            detection_id = int(detection_id_str)
            break
        except ValueError:
            print("❌ Invalid ID. Please enter a number.")
    
    # Get corrected text
    print("\nEnter corrected text (press Ctrl+D when done):")
    corrected_lines = []
    try:
        while True:
            line = input()
            corrected_lines.append(line)
    except EOFError:
        pass
    corrected_text = '\n'.join(corrected_lines)
    
    if not corrected_text.strip():
        print("❌ Corrected text cannot be empty.")
        return
    
    # Get correction type
    print("\nCorrection Types:")
    print("  1. prompt_refinement (improved prompt)")
    print("  2. manual_edit (direct human editing)")
    print("  3. temperature_adjustment (settings tweaks)")
    print("  4. other")
    
    type_map = {
        '1': 'prompt_refinement',
        '2': 'manual_edit',
        '3': 'temperature_adjustment',
        '4': 'other'
    }
    
    while True:
        type_choice = input("Select type (1-4): ").strip()
        if type_choice in type_map:
            correction_type = type_map[type_choice]
            break
        print("❌ Invalid choice. Please enter 1-4.")
    
    # Get notes
    notes = input("\nNotes (optional): ").strip() or None
    
    # Add to database
    try:
        correction_id = db.add_correction(
            detection_id=detection_id,
            corrected_text=corrected_text,
            correction_type=correction_type,
            notes=notes
        )
        print(f"\n✅ Correction added successfully (ID: {correction_id})")
    except Exception as e:
        print(f"\n❌ Failed to add correction: {e}")


def add_correction_cli(
    db: WinstonFeedbackDatabase,
    detection_id: int,
    corrected_text: Optional[str],
    correction_type: str,
    notes: Optional[str],
    file_path: Optional[Path]
) -> None:
    """Add correction via command-line arguments."""
    
    # Load corrected text from file if specified
    if file_path:
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            sys.exit(1)
        corrected_text = file_path.read_text()
    
    if not corrected_text:
        logger.error("No corrected text provided. Use --corrected-text or --file")
        sys.exit(1)
    
    # Add to database
    try:
        correction_id = db.add_correction(
            detection_id=detection_id,
            corrected_text=corrected_text,
            correction_type=correction_type,
            notes=notes
        )
        logger.info(f"✅ Correction added successfully (ID: {correction_id})")
        
        # Show summary
        print("\n=== Correction Summary ===")
        print(f"Detection ID: {detection_id}")
        print(f"Correction Type: {correction_type}")
        print(f"Text Length: {len(corrected_text)} characters")
        if notes:
            print(f"Notes: {notes}")
        
    except Exception as e:
        logger.error(f"Failed to add correction: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Add human corrections to Winston feedback database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Modes
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help="Interactive mode (prompts for all fields)"
    )
    
    # Required for CLI mode
    parser.add_argument(
        '--id',
        type=int,
        help="Detection ID to add correction for"
    )
    
    parser.add_argument(
        '--corrected-text',
        type=str,
        help="Corrected text (or use --file)"
    )
    
    parser.add_argument(
        '--file', '-f',
        type=Path,
        help="Read corrected text from file"
    )
    
    parser.add_argument(
        '--type', '-t',
        choices=['prompt_refinement', 'manual_edit', 'temperature_adjustment', 'other'],
        default='manual_edit',
        help="Type of correction (default: manual_edit)"
    )
    
    parser.add_argument(
        '--notes', '-n',
        type=str,
        help="Notes about the correction"
    )
    
    # Database
    parser.add_argument(
        '--db-path',
        type=str,
        help="Database path (default: from config.yaml)"
    )
    
    args = parser.parse_args()
    
    # Get database path
    db_path = args.db_path
    if not db_path:
        try:
            config = get_config()
            db_path = config.config.get('winston_feedback_db_path')
            if not db_path:
                logger.error("No database path in config.yaml. Use --db-path")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)
    
    # Initialize database
    try:
        db = WinstonFeedbackDatabase(db_path)
        logger.info(f"Connected to database: {db_path}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)
    
    # Run appropriate mode
    if args.interactive:
        add_correction_interactive(db)
    else:
        if not args.id:
            logger.error("--id required in CLI mode (or use --interactive)")
            sys.exit(1)
        
        add_correction_cli(
            db=db,
            detection_id=args.id,
            corrected_text=args.corrected_text,
            correction_type=args.type,
            notes=args.notes,
            file_path=args.file
        )


if __name__ == '__main__':
    main()
