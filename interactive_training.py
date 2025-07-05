#!/usr/bin/env python3
"""
from config.global_config import get_config
Interactive Detection Training Mode

This scri    def run_i    def run_interactive_session(self):
        """Run Natural Voice training session - generate introduction and get user feedback."""
        # Get material from config
        material = self.user_config.get("material", "aluminum").lower()
        
        print("🎓 Natural Voice Training Mode")
        print("="*50)
        print(f"📝 Training for: {material.upper()}")
        print("🎯 Generate Introduction Text & Rate Naturalness")
        print("💡 This will help improve detection for future generations")
        print()
        
        # Always generate introduction section for the configured material
        self.generate_introduction_content(material)e_session(self):
        """Run Natural Voice training session - generate introduction and get user feedback."""
        # Get material from config
        material = self.user_config.get("material", "aluminum").lower()
        
        print("🎓 Natural Voice Training Mode")
        print("="*50)
        print(f"📝 Training for: {material.upper()}")
        print("🎯 Generate Introduction Text & Rate Naturalness")
        print("💡 This will help improve detection for future generations")
        print()
        
        # Always generate introduction section for the configured material
        self.generate_introduction_content(material) you to:
1. See before/after text transformations
2. Run single sections through the detection system
3. Provide feedback to train and adjust prompts
4. Test the separated AI and Natural Voice detection systems
"""

import sys
import os
import json
from typing import Dict, Any, Optional

# Setup paths for imports
import setup_paths

from modules.runner import ApplicationRunner
from config.configurator import build_run_config
from modules.page_generator import ArticleGenerator
from core.domain.models import GenerationContext, TemperatureConfig
from modules.logger import get_logger

logger = get_logger("interactive_training")


class InteractiveDetectionTrainer:
    """Interactive training system for detection prompts using the main application infrastructure."""

    def __init__(self):
        # Use the main application runner and configuration
        self.app_runner = ApplicationRunner()
        self.app_runner.setup_environment()
        
        # Load configuration from root run.py
        try:
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sys.path.insert(0, parent_dir)
            from run import USER_CONFIG
            self.user_config = USER_CONFIG
        except ImportError:
            raise RuntimeError("Could not load configuration from root run.py")
        
        # Build run configuration using the main app's configurator (only takes user_config)
        self.run_config = build_run_config(self.user_config)
        
        # Create generation configuration
        self.generation_config = self.app_runner.create_generation_config(self.run_config)
        
        # Initialize services directly from the DI container
        from core.container import get_container
        from core.application import configure_services
        self.container = get_container()
        configure_services(self.container)
        
        # Get services from container
        from core.interfaces.services import IAPIClient, IPromptRepository
        from core.services.detection_service import DetectionService
        from core.services.content_service import ContentGenerationService
        
        self.api_client = self.container.get(IAPIClient)
        self.prompt_repository = self.container.get(IPromptRepository)
        self.detection_service = DetectionService(self.api_client, self.prompt_repository)
        self.content_service = ContentGenerationService(self.api_client, self.prompt_repository)
        
        # Training data storage
        self.feedback_data = []
        self.session_results = []
        
        logger.info("🎓 Interactive trainer initialized using main application infrastructure")

    def run_interactive_session(self):
        """Run Natural Voice training session - generate introduction and get user feedback."""
        print("🎓 Natural Voice Training Mode")
        print("="*50)
        print("� Generate Introduction Text & Rate Naturalness")
        print()
        
        # Always generate introduction section for different materials
        self.generate_and_rate_naturalness()

    def test_sample_content(self):
        """Test detection on sample content."""
        print("\n🧪 Testing Sample Content")
        print("-" * 30)
        
        # Sample content options
        samples = {
            "1": {
                "name": "Forced Humanization Example",
                "content": "Hey there! Let's dive into aluminum laser cleaning, shall we? You know how aluminum is literally everywhere these days - from your phone to airplanes! But here's the thing that'll blow your mind: traditional cleaning methods are actually damaging this amazing metal. That's where laser cleaning swoops in like a superhero!"
            },
            "2": {
                "name": "Authentic Professional Voice",
                "content": "Aluminum presents unique challenges in laser cleaning applications. The metal's high reflectivity at common laser wavelengths requires careful parameter adjustment. Based on field experience, pulsed fiber lasers at 1064nm work well for oxide removal, though power density must stay below 10 MW/cm² to avoid surface melting."
            },
            "3": {
                "name": "Robotic AI Content",
                "content": "Aluminum laser cleaning is a process that utilizes laser technology to remove contaminants from aluminum surfaces. This method offers several advantages over traditional cleaning methods. The laser cleaning process is environmentally friendly and provides precise control over the cleaning operation."
            },
            "4": {
                "name": "Custom Content",
                "content": None
            }
        }
        
        print("Select sample content:")
        for key, sample in samples.items():
            print(f"{key}. {sample['name']}")
        
        choice = self.safe_input("\nEnter choice (1-4): ", "1")
        
        if choice in samples:
            if choice == "4":
                content = self.safe_input("\nEnter your custom content:\n", "")
                sample_name = "Custom Content"
            else:
                content = samples[choice]["content"]
                sample_name = samples[choice]["name"]
            
            if content:
                self.analyze_content(content, sample_name)
            else:
                print("❌ No content provided.")
        else:
            print("❌ Invalid choice.")

    def generate_and_test_section(self):
        """Generate a single section and test it."""
        print("\n🔧 Generate and Test Section")
        print("-" * 30)
        
        # Get section type
        sections = ["introduction", "comparison", "chart", "contaminants", "substrates", "table"]
        
        print("Available sections:")
        for i, section in enumerate(sections, 1):
            print(f"{i}. {section}")
        
        try:
            choice_input = input("\nEnter section number: ").strip()
            choice = int(choice_input) - 1
            if 0 <= choice < len(sections):
                section_name = sections[choice]
                material = input("Enter material name (default: aluminum): ").strip() or "aluminum"
                
                self.generate_section_content(section_name, material)
            else:
                print("❌ Invalid choice.")
        except (ValueError, EOFError, KeyboardInterrupt):
            print("❌ Please enter a valid number or session interrupted.")

    def generate_section_content(self, section_name: str, material: str):
        """Generate content for a specific section using the main application's content service."""
        print(f"\n🚀 Generating {section_name} section for {material}...")
        
        try:
            # Create generation context (same as main app)
            context = GenerationContext(material=material, content_type="article")
            context.set_variable("section_name", section_name)
            context.set_variable("word_limit", "200")
            
            print("🎯 Generating content using main application content service...")
            
            # Use the main application's content service to generate content
            # This ensures we use the same prompts, temperature, and logic as the main app
            generated_content = self.content_service.generate_section_content(
                section_name=section_name,
                context=context,
                temperature_config=self.temp_config,
                timeout=get_config().get_api_timeout()
            )
            
            print("✅ Content generated!")
            self.analyze_content(generated_content, f"{material} - {section_name}")
            
        except Exception as e:
            print(f"❌ Error generating content: {e}")
            logger.error(f"Content generation failed: {e}")

    def analyze_content(self, content: str, content_name: str):
        """Analyze content with both detection systems."""
        print(f"\n📊 Analyzing: {content_name}")
        print("=" * 50)
        
        # Show original content
        print("📝 ORIGINAL CONTENT:")
        print("-" * 20)
        print(content)
        print()
        
        # Create context for detection
        context = GenerationContext(material="test", content_type="test")
        context.set_variable("section_name", "test")
        
        # Run comprehensive detection
        try:
            print("🔍 Running Detection Analysis...")
            
            temp_config = TemperatureConfig(
                content_temp=0.6,
                detection_temp=0.3,
                improvement_temp=0.7,
                summary_temp=0.4,
                metadata_temp=0.2
            )
            
            detection_results = self.detection_service.run_comprehensive_detection(
                content=content,
                context=context,
                ai_threshold=get_config().get_ai_detection_threshold(),
                natural_voice_threshold=get_config().get_natural_voice_threshold(),
                iteration=1,
                temperature_config=temp_config
            )
            
            # Display results
            self.display_detection_results(detection_results, content_name)
            
            # Get user feedback
            self.collect_user_feedback(content, content_name, detection_results)
            
        except Exception as e:
            print(f"❌ Detection failed: {e}")
            logger.error(f"Detection analysis failed: {e}")

    def display_detection_results(self, results: Dict[str, Any], content_name: str):
        """Display comprehensive detection results."""
        print("\n🎯 DETECTION RESULTS:")
        print("-" * 30)
        
        # AI Detection Results
        ai_result = results["ai_detection"]
        ai_interp = ai_result["interpretation"]
        print(f"🤖 AI Detection:")
        print(f"   Score: {ai_result['score']}% (threshold: ≤{ai_result['threshold']}%)")
        print(f"   Status: {'✅ PASS' if ai_result['passes'] else '❌ FAIL'}")
        print(f"   Category: {ai_interp.category.value.upper()} {ai_interp.emoji}")
        print(f"   Analysis: {ai_interp.description}")
        print()
        
        # Natural Voice Detection Results
        nv_result = results["natural_voice_detection"]
        nv_interp = nv_result["interpretation"]
        print(f"👤 Natural Voice Detection:")
        print(f"   Score: {nv_result['score']}% (threshold: ≤{nv_result['threshold']}%)")
        print(f"   Status: {'✅ PASS' if nv_result['passes'] else '❌ FAIL'}")
        print(f"   Category: {nv_interp.category.value.upper()} {nv_interp.emoji}")
        print(f"   Analysis: {nv_interp.description}")
        print()
        
        # Overall Assessment
        overall = "✅ PASS" if results["overall_status"] == "PASS" else "❌ FAIL"
        print(f"🏁 Overall: {overall}")
        
        # Recommendations
        if results["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in results["recommendations"]:
                print(f"   • {rec}")
        
        # Temperature Strategy
        temp_adj = results.get("temperature_adjustments", {})
        if temp_adj:
            print(f"\n🌡️ Temperature Strategy: {temp_adj.get('strategy', 'N/A')}")

    def collect_user_feedback(self, content: str, content_name: str, detection_results: Dict[str, Any]):
        """Collect user feedback on detection results."""
        print("\n📋 FEEDBACK COLLECTION")
        print("-" * 25)
        print("Please provide your assessment of the detection results:")
        print()
        
        # AI Detection Feedback
        ai_score = detection_results["ai_detection"]["score"]
        print(f"🤖 AI Detection gave this content {ai_score}% (lower = more natural)")
        try:
            ai_feedback = input("Do you agree? (y/n/partially): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ai_feedback = "y"
            print("Using default: y")
        
        ai_comment = ""
        if ai_feedback in ["n", "partially"]:
            try:
                ai_comment = input("What should the AI score be (0-100)? ").strip()
            except (EOFError, KeyboardInterrupt):
                ai_comment = str(ai_score)
                print(f"Using current score: {ai_score}")
        
        # Natural Voice Feedback
        nv_score = detection_results["natural_voice_detection"]["score"]
        print(f"\n👤 Natural Voice gave this content {nv_score}% (15-25% = optimal professional voice)")
        try:
            nv_feedback = input("Do you agree? (y/n/partially): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            nv_feedback = "y"
            print("Using default: y")
        
        nv_comment = ""
        if nv_feedback in ["n", "partially"]:
            try:
                nv_comment = input("What should the Natural Voice score be (0-100)? ").strip()
            except (EOFError, KeyboardInterrupt):
                nv_comment = str(nv_score)
                print(f"Using current score: {nv_score}")
        
        # Overall Content Assessment
        print(f"\n📝 Overall, how would you rate this content?")
        print("1. Excellent professional voice (authentic expertise)")
        print("2. Good professional voice (minor issues)")
        print("3. Acceptable (needs improvement)")
        print("4. Poor (too robotic or forced)")
        print("5. Very poor (completely unnatural)")
        
        try:
            rating_input = input("Enter rating (1-5): ").strip()
            overall_rating = int(rating_input)
            if not (1 <= overall_rating <= 5):
                overall_rating = 3
        except (ValueError, EOFError, KeyboardInterrupt):
            overall_rating = 3
            print("Using default rating: 3")
        
        # Additional comments
        try:
            additional_comments = input("\nAny additional comments about this content?\n").strip()
        except (EOFError, KeyboardInterrupt):
            additional_comments = ""
            print("No additional comments.")
        
        # Store feedback
        feedback_entry = {
            "timestamp": __import__("time").time(),
            "content_name": content_name,
            "content": content[:200] + "..." if len(content) > 200 else content,
            "ai_detection": {
                "score": ai_score,
                "user_agrees": ai_feedback,
                "user_suggested_score": ai_comment,
            },
            "natural_voice_detection": {
                "score": nv_score,
                "user_agrees": nv_feedback,
                "user_suggested_score": nv_comment,
            },
            "overall_user_rating": overall_rating,
            "additional_comments": additional_comments,
        }
        
        self.feedback_data.append(feedback_entry)
        self.session_results.append(feedback_entry)
        
        print("✅ Feedback recorded! This will help improve the detection system.")

    def analyze_existing_content(self):
        """Analyze existing content from a file."""
        print("\n📁 Analyze Existing Content")
        print("-" * 30)
        
        # Look for existing articles
        content_files = []
        posts_dir = "app/(materials)/posts"
        if os.path.exists(posts_dir):
            for file in os.listdir(posts_dir):
                if file.endswith(".mdx"):
                    content_files.append(file)
        
        if content_files:
            print("Available content files:")
            for i, file in enumerate(content_files[:10], 1):  # Limit to 10 files
                print(f"{i}. {file}")
            
            try:
                choice_input = self.safe_input("\nEnter file number (or 0 for custom file): ", "0")
                choice = int(choice_input) - 1
                if choice == -1:
                    file_path = self.safe_input("Enter file path: ", "")
                elif 0 <= choice < len(content_files):
                    file_path = os.path.join(posts_dir, content_files[choice])
                else:
                    print("❌ Invalid choice.")
                    return
                
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract a section for analysis
                    sections = content.split("## ")
                    if len(sections) > 1:
                        print("\nAvailable sections:")
                        for i, section in enumerate(sections[1:6], 1):  # Show first 5 sections
                            section_title = section.split('\n')[0]
                            print(f"{i}. {section_title}")
                        
                        try:
                            sec_choice_input = self.safe_input("Enter section number: ", "1")
                            sec_choice = int(sec_choice_input) - 1
                            if 0 <= sec_choice < min(5, len(sections) - 1):
                                section_content = sections[sec_choice + 1]
                                section_title = section_content.split('\n')[0]
                                # Get just the text content, remove metadata
                                text_content = '\n'.join(section_content.split('\n')[1:])
                                text_content = text_content.strip()
                                
                                if text_content:
                                    self.analyze_content(text_content, f"{file_path} - {section_title}")
                                else:
                                    print("❌ No content found in selected section.")
                            else:
                                print("❌ Invalid section choice.")
                        except ValueError:
                            print("❌ Please enter a valid number.")
                    else:
                        print("❌ No sections found in file.")
                else:
                    print("❌ File not found.")
            except ValueError:
                print("❌ Please enter a valid number.")
        else:
            print("❌ No content files found. You can specify a custom file path.")

    def view_training_feedback(self):
        """View collected training feedback."""
        print("\n📊 Training Feedback Summary")
        print("-" * 35)
        
        if not self.feedback_data:
            print("No feedback data collected yet.")
            return
        
        print(f"Total feedback entries: {len(self.feedback_data)}")
        print()
        
        # Show recent feedback
        recent_feedback = self.feedback_data[-5:]  # Last 5 entries
        
        for i, entry in enumerate(recent_feedback, 1):
            print(f"Entry {i}: {entry['content_name']}")
            print(f"  AI Detection: {entry['ai_detection']['score']}% (User agrees: {entry['ai_detection']['user_agrees']})")
            print(f"  Natural Voice: {entry['natural_voice_detection']['score']}% (User agrees: {entry['natural_voice_detection']['user_agrees']})")
            print(f"  User Rating: {entry['overall_user_rating']}/5")
            if entry['additional_comments']:
                print(f"  Comments: {entry['additional_comments'][:100]}")
            print()

    def export_training_data(self):
        """Export training data to JSON file."""
        if not self.feedback_data:
            print("No training data to export.")
            return
        
        filename = f"detection_training_data_{int(__import__('time').time())}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Training data exported to: {filename}")
            print(f"Total entries: {len(self.feedback_data)}")
            
        except Exception as e:
            print(f"❌ Error exporting data: {e}")


    def run_demo_mode(self):
        """Run a demonstration mode with sample content."""
        print("🎭 Demo Mode - Testing Sample Content")
        print("="*50)
        
        # Test with the authentic professional voice sample
        sample_content = """Aluminum presents unique challenges in laser cleaning applications. The metal's high reflectivity at common laser wavelengths requires careful parameter adjustment. Based on field experience, pulsed fiber lasers at 1064nm work well for oxide removal, though power density must stay below 10 MW/cm² to avoid surface melting."""
        
        print("Testing with authentic professional voice sample...")
        self.analyze_content(sample_content, "Demo - Authentic Professional Voice")
        
        print("\n" + "="*50)
        print("Demo completed! This showed the detection system in action.")

    def generate_and_rate_naturalness(self):
        """Generate introduction content and get naturalness rating."""
        print("🔧 Generate Introduction Text")
        print("-" * 30)
        
        # Get material name
        try:
            material = input("Enter material name (default: aluminum): ").strip() or "aluminum"
            self.generate_introduction_content(material)
        except (EOFError, KeyboardInterrupt):
            print("❌ Session interrupted.")

    def generate_introduction_content(self, material: str):
        """Generate introduction content for rating."""
        print(f"\n🚀 Generating introduction for {material}...")
        
        try:
            # Use the main application's content service
            context = GenerationContext(material=material, content_type="article")
            context.set_variable("section_name", "introduction")
            context.set_variable("word_limit", "200")
            
            temp_config = TemperatureConfig(
                content_temp=0.6,
                detection_temp=0.3,
                improvement_temp=0.7,
                summary_temp=0.4,
                metadata_temp=0.2
            )
            
            print("🎯 Generating content...")
            generated_content = self.content_service.generate_content(
                context=context,
                section_name="introduction",
                temperature_config=temp_config
            )
            
            if generated_content and generated_content.content:
                print("✅ Content generated!")
                self.rate_naturalness(generated_content.content, material)
            else:
                print("❌ No content generated.")
            
        except Exception as e:
            print(f"❌ Error generating content: {e}")

    def rate_naturalness(self, content: str, material: str):
        """Rate the naturalness of generated content."""
        print(f"\n📝 GENERATED INTRODUCTION - {material.upper()}")
        print("=" * 50)
        print(content)
        print("=" * 50)
        
        # Run only Natural Voice detection for comparison
        try:
            context = GenerationContext(material=material, content_type="article")
            context.set_variable("section_name", "introduction")
            
            temp_config = TemperatureConfig(detection_temp=0.3)
            
            # Get Natural Voice score for reference
            nv_score = self.detection_service.natural_voice_service.detect_natural_voice(
                content=content,
                context=context,
                iteration=1,
                temperature_config=temp_config
            )
            
            system_rating = nv_score.score
            
        except Exception as e:
            print(f"⚠️ Could not get system rating: {e}")
            system_rating = None
        
        # Get user naturalness rating
        print(f"\n🎯 RATE THE NATURALNESS:")
        print("How natural does this text sound?")
        print()
        print("1. Very Natural    (sounds like a real expert wrote it)")
        print("2. Mostly Natural  (good, with minor artificial touches)")
        print("3. Somewhat Natural (okay, but clearly generated)")
        print("4. Mostly Fake     (obviously AI-generated)")
        print("5. Very Fake       (robotic, unnatural)")
        
        try:
            rating_input = input("\nEnter your rating (1-5): ").strip()
            user_rating = int(rating_input)
            if not (1 <= user_rating <= 5):
                user_rating = 3
                print("Invalid rating, using 3 (Somewhat Natural)")
        except (ValueError, EOFError, KeyboardInterrupt):
            user_rating = 3
            print("Using default rating: 3 (Somewhat Natural)")
        
        # Get additional feedback
        try:
            feedback = input("\nWhat makes it sound natural or fake? (optional): ").strip()
        except (EOFError, KeyboardInterrupt):
            feedback = ""
        
        # Store the training data
        self.store_naturalness_feedback(content, material, user_rating, feedback, system_rating)
        
        # Ask if they want to generate another
        print(f"\n✅ Feedback recorded!")
        if system_rating:
            print(f"   Your rating: {user_rating}/5 (1=Natural, 5=Fake)")
            print(f"   System gave: {system_rating}% Natural Voice score")
        
        try:
            continue_choice = input("\nGenerate another introduction? (y/n): ").strip().lower()
            if continue_choice in ['y', 'yes', '']:
                # Generate for a different material or same one
                try:
                    next_material = input("Enter material (or Enter for same): ").strip()
                    if not next_material:
                        next_material = material
                    self.generate_introduction_content(next_material)
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Training session ended.")
            else:
                print("👋 Training session completed!")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Training session ended.")

    def store_naturalness_feedback(self, content: str, material: str, user_rating: int, feedback: str, system_rating: int = None):
        """Store naturalness training feedback."""
        import time
        
        # Convert user rating to naturalness description
        rating_descriptions = {
            1: "Very Natural",
            2: "Mostly Natural", 
            3: "Somewhat Natural",
            4: "Mostly Fake",
            5: "Very Fake"
        }
        
        feedback_entry = {
            "timestamp": time.time(),
            "material": material,
            "content": content,
            "user_rating": user_rating,
            "user_description": rating_descriptions[user_rating],
            "user_feedback": feedback,
            "system_nv_score": system_rating,
            "content_length": len(content),
            "section_type": "introduction"
        }
        
        self.feedback_data.append(feedback_entry)
        
        # Save to file for training purposes
        try:
            import json
            filename = "naturalness_training_data.json"
            
            # Load existing data if file exists
            existing_data = []
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except FileNotFoundError:
                pass
            
            # Append new entry
            existing_data.append(feedback_entry)
            
            # Save back to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
                
            print(f"💾 Training data saved to {filename}")
            
        except Exception as e:
            print(f"⚠️ Could not save training data: {e}")

def main():
    """Main entry point for Natural Voice training."""
    import sys
    
    # Check if running in demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print("ℹ️ Demo mode not available in Natural Voice training")
        return
    
    # Run Natural Voice training
    try:
        trainer = InteractiveDetectionTrainer()
        trainer.run_interactive_session()
        
        # After training session, offer to apply insights
        try:
            apply_insights = input("\n🔄 Apply training insights to improve production system? (y/n): ").strip().lower()
            if apply_insights in ['y', 'yes', '']:
                print("\n📈 Applying training insights...")
                from core.services.training_integration_service import integrate_training_improvements
                results = integrate_training_improvements()
                
                if results['updates_applied'] > 0:
                    print(f"✅ Successfully applied {results['updates_applied']} improvements!")
                    print("   Your training feedback is now integrated into the production system.")
                else:
                    print("ℹ️ No immediate improvements applied, but feedback has been recorded.")
                    print("   Continue training to build up more data for automatic improvements.")
                    
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Training session completed without applying insights.")
        except Exception as e:
            print(f"⚠️ Could not apply training insights: {e}")
            
    except KeyboardInterrupt:
        print("\n\n👋 Training session interrupted. Goodbye!")
    except EOFError:
        print("\n\n⚠️ Input stream ended. Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Natural Voice training failed: {e}")


if __name__ == "__main__":
    main()
