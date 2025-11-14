#!/usr/bin/env python3
"""
Intensity Control CLI - Simple 4-slider control system

Usage:
    python3 processing/intensity_cli.py status
    python3 processing/intensity_cli.py set voice 75
    python3 processing/intensity_cli.py set technical 40
    python3 processing/intensity_cli.py set length 60
    python3 processing/intensity_cli.py set ai 80
    python3 processing/intensity_cli.py test
"""

import sys
import argparse
from pathlib import Path
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from processing.intensity_manager import IntensityManager


class IntensityCLI:
    """Command-line interface for 4-slider intensity management"""
    
    def __init__(self):
        self.manager = IntensityManager()
        self.config_path = self.manager.config_path
    
    def status(self):
        """Show current intensity settings"""
        print(self.manager.get_summary())
        print("\n" + "="*60)
        print("To change settings:")
        print("  python3 processing/intensity_cli.py set <slider> <value>")
        print("\nAvailable sliders:")
        print("  voice, technical, length, ai, rhythm, imperfection,")
        print("  personality, context, structural, engagement")
    
    def set_slider(self, slider_name: str, value: int):
        """Change a slider value (0-100)"""
        try:
            value = int(value)
            
            slider_map = {
                'voice': ('author_voice_intensity', self.manager.set_author_voice, 'Author voice'),
                'technical': ('technical_language_intensity', self.manager.set_technical_language, 'Technical language'),
                'length': ('length_variation_range', self.manager.set_length_variation, 'Length variation'),
                'ai': ('ai_avoidance_intensity', self.manager.set_ai_avoidance, 'AI avoidance'),
                'rhythm': ('sentence_rhythm_variation', self.manager.set_sentence_rhythm, 'Sentence rhythm'),
                'imperfection': ('imperfection_tolerance', self.manager.set_imperfection_tolerance, 'Imperfection tolerance'),
                'personality': ('personality_intensity', self.manager.set_personality_intensity, 'Personality'),
                'context': ('context_specificity', self.manager.set_context_specificity, 'Context specificity'),
                'structural': ('structural_predictability', self.manager.set_structural_predictability, 'Structural predictability'),
                'engagement': ('engagement_style', self.manager.set_engagement_style, 'Engagement style')
            }
            
            if slider_name not in slider_map:
                print(f"❌ Unknown slider: {slider_name}")
                print("   Valid sliders: voice, technical, length, ai, rhythm,")
                print("                  imperfection, personality, context,")
                print("                  structural, engagement")
                sys.exit(1)
            
            config_key, setter_func, display_name = slider_map[slider_name]
            
            # Set value
            setter_func(value)
            self._update_config(config_key, value)
            print(f"✅ {display_name} intensity set to: {value}/100")
            
            # Show new bar
            self._show_bar(slider_name, value)
            
        except ValueError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def test(self):
        """Show what the intensity instructions look like"""
        print("="*60)
        print("TEST: Intensity Instructions for AI Prompt")
        print("="*60)
        print()
        print(self.manager.build_intensity_instruction())
        print()
        print("="*60)
        print("These instructions would be prepended to generation prompts")
    
    def _update_config(self, key: str, value: int):
        """Update config.yaml file on disk"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            config[key] = value
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
        except Exception as e:
            print(f"⚠️  Warning: Could not update config file: {e}")
    
    def _show_bar(self, slider_name: str, value: int):
        """Show a visual bar for the slider"""
        filled = int((value / 100) * 40)
        bar = '█' * filled + '░' * (40 - filled)
        print(f"\n[{bar}] {value}/100")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Intensity Control - Simple 4-slider system (0-100)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show current settings
  python3 processing/intensity_cli.py status
  
  # Change sliders (0-100)
  python3 processing/intensity_cli.py set voice 75
  python3 processing/intensity_cli.py set rhythm 80
  python3 processing/intensity_cli.py set personality 60
  
  # Test current settings
  python3 processing/intensity_cli.py test

10-Slider System (0-100 scale):
  1. voice        - Author voice characteristics (regional patterns)
  2. technical    - Technical language density (jargon, measurements)
  3. length       - Length variation tolerance (±% from target)
  4. ai           - AI avoidance intensity (pattern detection)
  5. rhythm       - Sentence rhythm variation (length diversity)
  6. imperfection - Imperfection tolerance (human-like quirks)
  7. personality  - Personality intensity (opinions, preferences)
  8. context      - Context specificity (concrete vs. abstract)
  9. structural   - Structural predictability (template vs. organic)
  10. engagement  - Engagement style (detached vs. conversational)

Ranges:
  0-30:  Low intensity (minimal effect)
  31-60: Moderate intensity (balanced, default ~50)
  61-100: High intensity (pronounced effect)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Status command
    subparsers.add_parser('status', help='Show current slider values')
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Change a slider value')
    set_parser.add_argument('slider', 
                           choices=['voice', 'technical', 'length', 'ai', 'rhythm', 
                                   'imperfection', 'personality', 'context', 
                                   'structural', 'engagement'],
                           help='Which slider to adjust')
    set_parser.add_argument('value', type=int, help='Value 0-100')
    
    # Test command
    subparsers.add_parser('test', help='Test current settings (show prompt instructions)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = IntensityCLI()
    
    if args.command == 'status':
        cli.status()
    elif args.command == 'set':
        cli.set_slider(args.slider, args.value)
    elif args.command == 'test':
        cli.test()


if __name__ == '__main__':
    main()
