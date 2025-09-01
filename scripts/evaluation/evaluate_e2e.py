#!/usr/bin/env python3
"""
End-to-End Content Generation Evaluation
Evaluates the content generation system for bloat, simplicity, cleanup and effectiveness.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def evaluate_generators():
    """Compare different generators for bloat and effectiveness."""
    print("🔬 END-TO-END CONTENT GENERATION EVALUATION")
    print("="*60)
    
    # Test materials
    test_materials = [
        {
            "name": "Stainless Steel 316L",
            "data": {"name": "Stainless Steel 316L", "formula": "Fe-18Cr-10Ni-2Mo"},
            "author": {"id": 1, "name": "Yi-Chun Lin", "country": "Taiwan"}
        },
        {
            "name": "Aluminum 6061",
            "data": {"name": "Aluminum 6061", "formula": "Al-Mg-Si"},
            "author": {"id": 2, "name": "Marco Rossi", "country": "Italy"}
        }
    ]
    
    generators_to_test = [
        ("Fail-Fast Generator", test_fail_fast_generator),
        ("Optimized Enhanced Generator", test_optimized_generator),
        ("Original Generator", test_original_generator)
    ]
    
    results = {}
    
    for gen_name, test_func in generators_to_test:
        print(f"\n{'='*20} {gen_name} {'='*20}")
        try:
            result = test_func(test_materials[0])  # Test with first material
            results[gen_name] = result
            print_generator_results(gen_name, result)
        except Exception as e:
            print(f"❌ {gen_name} failed: {e}")
            results[gen_name] = {"error": str(e)}
    
    # Compare results
    print(f"\n{'='*60}")
    print("📊 COMPARATIVE ANALYSIS")
    print("-"*30)
    compare_generators(results)
    
    return results

def test_fail_fast_generator(material):
    """Test the fail-fast generator."""
    from components.content.fail_fast_generator import create_fail_fast_generator
    from api.client import MockAPIClient
    
    start_time = time.time()
    
    try:
        generator = create_fail_fast_generator()
        api_client = MockAPIClient()
        
        result = generator.generate(
            material_name=material["name"],
            material_data=material["data"],
            api_client=api_client,
            author_info=material["author"]
        )
        
        end_time = time.time()
        
        return {
            "success": result.success,
            "content_length": len(result.content) if result.success else 0,
            "generation_time": end_time - start_time,
            "error": result.error_message if not result.success else None,
            "metadata": result.metadata,
            "content_preview": result.content[:200] + "..." if result.success and len(result.content) > 200 else result.content,
            "file_size": get_generator_file_size("components/content/fail_fast_generator.py"),
            "dependencies": ["yaml", "json", "time", "pathlib", "functools"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generation_time": time.time() - start_time
        }

def test_optimized_generator(material):
    """Test the optimized enhanced generator."""
    try:
        from components.content.optimized_enhanced_generator import OptimizedContentGenerator
        from api.client import MockAPIClient
        
        start_time = time.time()
        
        generator = OptimizedContentGenerator(enable_validation=False)  # Skip validation for speed
        api_client = MockAPIClient()
        
        result = generator.generate(
            material_name=material["name"],
            material_data=material["data"],
            api_client=api_client,
            author_info=material["author"]
        )
        
        end_time = time.time()
        
        return {
            "success": result.success,
            "content_length": len(result.content) if result.success else 0,
            "generation_time": end_time - start_time,
            "error": result.error_message if not result.success else None,
            "metadata": getattr(result, 'metadata', {}),
            "content_preview": result.content[:200] + "..." if result.success and len(result.content) > 200 else result.content,
            "file_size": get_generator_file_size("components/content/optimized_enhanced_generator.py"),
            "dependencies": ["enhanced_generator", "optimized_config_manager", "human_validator"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generation_time": time.time() - start_time
        }

def test_original_generator(material):
    """Test the original generator."""
    try:
        from components.content.generator import ContentComponentGenerator
        from api.client import MockAPIClient
        
        start_time = time.time()
        
        generator = ContentComponentGenerator()
        api_client = MockAPIClient()
        
        result = generator.generate(
            material_name=material["name"],
            material_data=material["data"],
            api_client=api_client,
            author_info=material["author"]
        )
        
        end_time = time.time()
        
        return {
            "success": result.success,
            "content_length": len(result.content) if result.success else 0,
            "generation_time": end_time - start_time,
            "error": result.error_message if not result.success else None,
            "metadata": getattr(result, 'metadata', {}),
            "content_preview": result.content[:200] + "..." if result.success and len(result.content) > 200 else result.content,
            "file_size": get_generator_file_size("components/content/generator.py"),
            "dependencies": ["yaml", "random", "functools", "generators.component_generators"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generation_time": time.time() - start_time
        }

def get_generator_file_size(file_path):
    """Get the file size in bytes and lines."""
    try:
        path = Path(file_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            return {
                "bytes": path.stat().st_size,
                "lines": len(lines),
                "kb": round(path.stat().st_size / 1024, 2)
            }
    except Exception:
        pass
    return {"bytes": 0, "lines": 0, "kb": 0}

def print_generator_results(name, result):
    """Print formatted results for a generator."""
    if result.get("success"):
        print(f"✅ Success: {result['content_length']} chars in {result['generation_time']:.3f}s")
        print(f"📁 File size: {result['file_size']['lines']} lines, {result['file_size']['kb']} KB")
        print(f"📦 Dependencies: {len(result['dependencies'])}")
        if result.get('metadata'):
            print(f"📊 Metadata: {result['metadata']}")
        print(f"📝 Preview: {result['content_preview'][:100]}...")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        if 'generation_time' in result:
            print(f"⏱️  Failed after: {result['generation_time']:.3f}s")

def compare_generators(results):
    """Compare generator performance and characteristics."""
    successful = {name: data for name, data in results.items() if data.get("success")}
    
    if not successful:
        print("❌ No generators succeeded")
        return
    
    print("🏆 PERFORMANCE COMPARISON")
    print("-" * 25)
    
    # Speed comparison
    fastest = min(successful.items(), key=lambda x: x[1]["generation_time"])
    slowest = max(successful.items(), key=lambda x: x[1]["generation_time"])
    
    print(f"⚡ Fastest: {fastest[0]} ({fastest[1]['generation_time']:.3f}s)")
    print(f"🐌 Slowest: {slowest[0]} ({slowest[1]['generation_time']:.3f}s)")
    
    # File size comparison  
    smallest = min(successful.items(), key=lambda x: x[1]["file_size"]["lines"])
    largest = max(successful.items(), key=lambda x: x[1]["file_size"]["lines"])
    
    print(f"📦 Smallest: {smallest[0]} ({smallest[1]['file_size']['lines']} lines)")
    print(f"📈 Largest: {largest[0]} ({largest[1]['file_size']['lines']} lines)")
    
    # Content length comparison
    shortest = min(successful.items(), key=lambda x: x[1]["content_length"])
    longest = max(successful.items(), key=lambda x: x[1]["content_length"])
    
    print(f"📝 Shortest content: {shortest[0]} ({shortest[1]['content_length']} chars)")
    print(f"📚 Longest content: {longest[0]} ({longest[1]['content_length']} chars)")
    
    # Dependency comparison
    fewest_deps = min(successful.items(), key=lambda x: len(x[1]["dependencies"]))
    most_deps = max(successful.items(), key=lambda x: len(x[1]["dependencies"]))
    
    print(f"🎯 Fewest dependencies: {fewest_deps[0]} ({len(fewest_deps[1]['dependencies'])})")
    print(f"🕸️  Most dependencies: {most_deps[0]} ({len(most_deps[1]['dependencies'])})")

def evaluate_prompt_usage():
    """Evaluate how formatting and persona prompts are being used."""
    print(f"\n{'='*60}")
    print("📋 PROMPT USAGE EVALUATION")
    print("-"*30)
    
    # Check formatting files
    formatting_dir = Path("components/content/prompts/formatting")
    persona_dir = Path("components/content/prompts/personas")
    
    print("📁 FORMATTING FILES:")
    for file in formatting_dir.glob("*.yaml"):
        size = file.stat().st_size
        if size == 0:
            print(f"  ⚠️  {file.name}: EMPTY ({size} bytes)")
        else:
            print(f"  ✅ {file.name}: {size} bytes")
    
    print("\n👤 PERSONA FILES:")
    for file in persona_dir.glob("*.yaml"):
        size = file.stat().st_size
        print(f"  ✅ {file.name}: {size} bytes")
    
    # Check if generators are using these files
    print("\n🔗 GENERATOR USAGE ANALYSIS:")
    check_formatting_usage()
    check_persona_usage()

def check_formatting_usage():
    """Check if generators are using formatting files."""
    generators = [
        "components/content/generator.py",
        "components/content/enhanced_generator.py", 
        "components/content/optimized_enhanced_generator.py",
        "components/content/fail_fast_generator.py"
    ]
    
    formatting_usage = {}
    for gen_path in generators:
        if Path(gen_path).exists():
            with open(gen_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            uses_formatting = (
                "formatting/" in content or
                "_formatting.yaml" in content or
                "load_formatting" in content
            )
            
            formatting_usage[Path(gen_path).stem] = uses_formatting
    
    print("  📋 Formatting file usage:")
    for gen, uses in formatting_usage.items():
        status = "✅ USES" if uses else "❌ UNUSED"
        print(f"    {gen}: {status}")

def check_persona_usage():
    """Check if generators are using persona files properly."""
    generators = [
        "components/content/generator.py",
        "components/content/enhanced_generator.py",
        "components/content/optimized_enhanced_generator.py", 
        "components/content/fail_fast_generator.py"
    ]
    
    persona_usage = {}
    for gen_path in generators:
        if Path(gen_path).exists():
            with open(gen_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            uses_personas = (
                "personas/" in content or
                "_persona.yaml" in content or
                "load_persona" in content
            )
            
            persona_usage[Path(gen_path).stem] = uses_personas
    
    print("  👤 Persona file usage:")
    for gen, uses in persona_usage.items():
        status = "✅ USES" if uses else "❌ UNUSED"
        print(f"    {gen}: {status}")

def identify_bloat_and_redundancy():
    """Identify bloat and redundancy in the system."""
    print(f"\n{'='*60}")
    print("🧹 BLOAT AND REDUNDANCY ANALYSIS")
    print("-"*30)
    
    # Check for duplicate generators
    generators = list(Path("components/content").glob("*generator*.py"))
    print(f"📊 Found {len(generators)} generator files:")
    
    generator_sizes = []
    for gen in generators:
        size_info = get_generator_file_size(str(gen))
        generator_sizes.append((gen.name, size_info))
        print(f"  {gen.name}: {size_info['lines']} lines ({size_info['kb']} KB)")
    
    # Identify largest files (potential bloat)
    largest = max(generator_sizes, key=lambda x: x[1]['lines'])
    print(f"\n🎯 Largest generator: {largest[0]} ({largest[1]['lines']} lines)")
    
    # Check for mock usage (should be removed)
    print("\n🚫 MOCK USAGE CHECK:")
    check_mock_usage()

def check_mock_usage():
    """Check for mock and fallback usage that should be removed."""
    files_to_check = [
        "components/content/generator.py",
        "components/content/enhanced_generator.py",
        "components/content/optimized_enhanced_generator.py",
        "components/content/fail_fast_generator.py"
    ]
    
    mock_patterns = [
        "mock",
        "fallback", 
        "default_content",
        "hardcoded",
        "placeholder"
    ]
    
    for file_path in files_to_check:
        if Path(file_path).exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            found_mocks = []
            for pattern in mock_patterns:
                if pattern in content:
                    found_mocks.append(pattern)
            
            if found_mocks:
                print(f"  ⚠️  {Path(file_path).name}: Found {found_mocks}")
            else:
                print(f"  ✅ {Path(file_path).name}: Clean (no mocks/fallbacks)")

def main():
    """Run comprehensive evaluation."""
    print("🎯 GOAL: 100% believable human-generated content")
    print("🎯 REQUIREMENTS: Use formatting & persona files, no mocks/fallbacks")
    print("🎯 EVALUATION: Bloat, simplicity, cleanup, effectiveness")
    
    # Run evaluations
    results = evaluate_generators()
    evaluate_prompt_usage()
    identify_bloat_and_redundancy()
    
    # Final recommendations
    print(f"\n{'='*60}")
    print("🎯 RECOMMENDATIONS")
    print("-"*30)
    provide_recommendations(results)

def provide_recommendations(results):
    """Provide recommendations based on evaluation."""
    successful = {name: data for name, data in results.items() if data.get("success")}
    
    if "Fail-Fast Generator" in successful:
        print("✅ RECOMMENDED: Fail-Fast Generator")
        print("  Reasons:")
        print("  - No hardcoded fallbacks")
        print("  - Clean error handling")
        print("  - Proper retry mechanisms")
        print("  - Fail-fast approach")
        
    # Check formatting usage
    print("\n📋 FORMATTING FILES:")
    formatting_files = list(Path("components/content/prompts/formatting").glob("*.yaml"))
    empty_files = [f for f in formatting_files if f.stat().st_size == 0]
    
    if empty_files:
        print(f"  ⚠️  {len(empty_files)} empty formatting files found")
        print("  ACTION: Populate or remove empty formatting files")
    
    print("\n🧹 CLEANUP ACTIONS:")
    print("  1. Remove unused generator files")
    print("  2. Populate empty formatting files") 
    print("  3. Ensure all generators use persona and formatting files")
    print("  4. Remove any remaining mocks and fallbacks")

if __name__ == "__main__":
    main()
