#!/usr/bin/env python3
"""
Z-Beam Interactive Training - Quick Entry Point

Improve detection results by rating content naturalness.
Uses the same material/config as run.py for consistency.
"""

if __name__ == "__main__":
    import sys
    import os
    
    print("🎓 Z-Beam Interactive Training")
    print("=" * 40)
    
    try:
        # Load material from run.py config
        from run import USER_CONFIG
        material = USER_CONFIG.get("material", "Unknown")
        print(f"📝 Training for material: {material}")
        print("🎯 Rate content naturalness to improve detection")
        print()
        
        # Add generator directory to path and run training
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generator'))
        
        # Import and run the interactive trainer
        from interactive_training import main as train_main
        train_main()
        
    except KeyboardInterrupt:
        print("\n\n👋 Training session ended. Goodbye!")
    except Exception as e:
        print(f"❌ Training error: {e}")
        print("\nMake sure:")
        print("1. Generator directory exists")
        print("2. run.py contains valid USER_CONFIG")
        sys.exit(1)
