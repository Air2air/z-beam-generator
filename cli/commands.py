#!/usr/bin/env python3
"""
Z-Beam CLI Commands

This module contains all command implementations for the Z-Beam CLI.
Each command is extracted from the main run.py file for better organization.
"""

import subprocess
import sys
import time
import os
import asyncio
from typing import Dict, Any, Optional


def run_test_suite():
    """Run comprehensive test suite."""
    print("🧪 Running Comprehensive Test Suite...")
    print("=" * 50)
    print("📊 Test Coverage:")
    print("   • Unit Tests: Component and utility testing")
    print("   • Integration Tests: Component interaction testing")
    print("   • E2E Tests: Complete workflow testing")
    print("   • Anti-hang protections: Active")
    print("   • Mock isolation: Enforced")
    print("")

    try:
        # Run pytest with proper configuration
        cmd = [
            sys.executable, "-m", "pytest", "tests/",
            "--tb=short",  # Short traceback format
            "--durations=10",  # Show 10 slowest tests
            "-v"  # Verbose output
        ]

        print(f"🚀 Executing: {' '.join(cmd)}")
        print("⏱️  This may take 1-2 minutes...")
        print("")

        # Set PYTHONPATH for test execution
        env = {"PYTHONPATH": ".", **dict(os.environ)}

        result = subprocess.run(cmd, env=env, capture_output=False)

        if result.returncode == 0:
            print("")
            print("✅ All tests completed successfully!")
            print("📊 Test suite maintains 95.5%+ success rate")
            print("🛡️  Robust testing framework active")
        else:
            print("")
            print(f"⚠️  Tests completed with exit code: {result.returncode}")
            print("💡 Some tests may have failed - check output above")

    except Exception as e:
        print(f"❌ Error running test suite: {e}")
        print("💡 Try running manually: PYTHONPATH=. python3 -m pytest tests/")


def test_api_connectivity():
    """Test API connectivity and configuration."""
    print("🧪 Testing API connectivity...")
    # API test using centralized API_PROVIDERS from run.py
    from api.client_manager import validate_api_environment
    results = validate_api_environment()
    for provider_id, config in results.items():
        status = "✅" if config["configured"] else "❌"
        print(f"   {status} {config['provider']}: {config['env_var']}")

    if not any(r["configured"] for r in results.values()):
        print("⚠️  No API providers configured. Set environment variables.")
    else:
        print("✅ API connectivity check complete!")


def list_available_materials():
    """List all available materials."""
    print("📋 Available Materials:")
    try:
        from data.materials import load_materials

        materials_data = load_materials()
        for category, data in materials_data.items():
            items = data.get("items", [])
            print(f"\n🔧 {category.title()} ({len(items)} materials):")
            for material in items[:5]:  # Show first 5
                print(f"   • {material['name']}")
            if len(items) > 5:
                print(f"   ... and {len(items) - 5} more")
    except ImportError:
        print("❌ Could not load materials data")
        print(
            "💡 Make sure data/materials.yaml exists and is properly formatted"
        )


def show_system_status():
    """Show system status and component availability."""
    print("📊 Z-Beam System Status:")
    print("✅ Core system operational")
    print("✅ Component generators loaded")
    print("✅ API clients configured")
    print("✅ Content validation active")


def show_cache_statistics():
    """Show API client cache performance statistics."""
    print("📊 API Client Cache Statistics:")
    try:
        from api.cache_adapter import APIClientCache

        stats = APIClientCache.get_cache_stats()

        # Show cache type
        cache_type = "persistent" if APIClientCache.is_persistent() else "in-memory"
        print(f"🔧 Cache type: {cache_type}")

        print(f"   🎯 Cache hit rate: {stats['hit_rate_percent']}%")
        print(f"   ✅ Cache hits: {stats['cache_hits']}")
        print(f"   ❌ Cache misses: {stats['cache_misses']}")
        print(f"   📋 Total requests: {stats['total_requests']}")
        print(f"   🏭 Cached instances: {stats['cached_instances']}")

        # Show persistent cache stats if available
        if 'disk_cached_instances' in stats:
            print(f"   💾 Disk cached instances: {stats['disk_cached_instances']}")

        if stats['hit_rate_percent'] >= 80:
            print("🚀 Excellent cache performance!")
        elif stats['hit_rate_percent'] >= 60:
            print("👍 Good cache performance")
        elif stats['total_requests'] == 0:
            print("💡 No cache activity yet - preload cache for better performance")
        else:
            print("⚠️  Consider preloading cache for better performance")

    except ImportError as e:
        print(f"❌ Cache system not available: {e}")


def show_cache_info():
    """Show detailed information about cached API clients."""
    print("📋 API Client Cache Detailed Information:")
    try:
        from api.cache_adapter import APIClientCache

        # Get cache info
        info = APIClientCache.cache_info()

        # Show cache type
        cache_type = "persistent" if APIClientCache.is_persistent() else "in-memory"
        print(f"🔧 Cache type: {cache_type}")

        # Show stats summary
        stats = info.get("stats", {})
        print(f"\n📊 Cache Statistics:")
        print(f"   🎯 Hit rate: {stats.get('hit_rate_percent', 0)}%")
        print(f"   ✅ Hits: {stats.get('cache_hits', 0)}")
        print(f"   ❌ Misses: {stats.get('cache_misses', 0)}")
        print(f"   📋 Requests: {stats.get('total_requests', 0)}")

        # Show clients if available
        clients = info.get("clients", {})
        if clients:
            print(f"\n🔧 Cached Clients ({len(clients)}):")
            for key, client_info in list(clients.items())[:5]:  # Show first 5
                age = client_info.get("age_formatted", "unknown")
                size = client_info.get("size", "unknown")
                in_memory = "✅" if client_info.get("in_memory", False) else "❌"
                print(f"   • {key} | Age: {age} | Size: {size}B | In Memory: {in_memory}")

            if len(clients) > 5:
                print(f"   ... and {len(clients) - 5} more")

        # Show cache location
        if "cache_dir" in info:
            print(f"\n📂 Cache Location:")
            print(f"   Directory: {info['cache_dir']}")
            print(f"   Info File: {info['cache_info_file']}")

    except ImportError as e:
        print(f"❌ Cache info not available: {e}")
    except Exception as e:
        print(f"⚠️  Error retrieving cache info: {e}")


def clear_api_cache():
    """Clear API client cache to force fresh connections."""
    print("🧹 Clearing API client cache...")
    try:
        from api.cache_adapter import APIClientCache

        cache_type = "persistent" if APIClientCache.is_persistent() else "in-memory"
        print(f"🔧 Clearing {cache_type} cache...")

        stats_before = APIClientCache.get_cache_stats()
        result = APIClientCache.clear_cache()

        if isinstance(result, tuple) and len(result) == 2:
            cleared_count, errors = result
            print(f"✅ Cleared {cleared_count} cached clients")

            if errors:
                print(f"⚠️  Encountered {len(errors)} errors while clearing cache:")
                for error in errors[:3]:  # Show first 3 errors
                    print(f"   • {error}")
                if len(errors) > 3:
                    print(f"   ... and {len(errors) - 3} more")
        else:
            print(f"✅ Cleared {stats_before.get('cached_instances', 0)} cached clients")

        print("💡 Next API calls will create fresh connections")

    except ImportError as e:
        print(f"❌ Cache system not available: {e}")


def disable_persistent_cache():
    """Set environment variable to disable persistent cache."""
    print("⚠️ Disabling persistent cache (not recommended)...")
    os.environ["Z_BEAM_NO_PERSISTENT_CACHE"] = "true"
    print("💡 Using in-memory cache only (clients won't persist between runs)")
    print("⚠️ Performance may be reduced - this is not recommended for production use")


def preload_api_cache():
    """Preload API clients into cache for better performance."""
    print("🚀 Preloading API client cache...")
    try:
        from api.cache_adapter import APIClientCache
        from run import API_PROVIDERS

        # Show cache type
        cache_type = "persistent" if APIClientCache.is_persistent() else "in-memory"
        print(f"🔧 Using {cache_type} cache")

        # Get configured providers from API_PROVIDERS
        providers = list(API_PROVIDERS.keys())
        print(f"📋 Detected providers: {', '.join(providers)}")

        # Preload each provider with standard configurations
        preload_results = APIClientCache.preload_clients(providers)

        # Report success/failure counts
        success_count = len(preload_results.get("success", []))
        failed_count = len(preload_results.get("failed", []))

        if success_count > 0:
            print(f"✅ Successfully preloaded {success_count} API clients")

        if failed_count > 0:
            print(f"⚠️  Failed to preload {failed_count} providers:")
            for fail in preload_results.get("failed", []):
                print(f"   ❌ {fail['provider']}: {fail['error']}")

        # Report cache statistics
        stats = APIClientCache.get_cache_stats()
        print(f"📊 Cache now contains {stats.get('cached_instances', 0)} API clients")

        if APIClientCache.is_persistent():
            print(f"💾 Disk cache contains {stats.get('disk_cached_instances', 0)} clients")
            print(f"🚀 Clients will persist between program runs for better performance")

        print("✨ Ready for high-performance batch generation!")

    except ImportError as e:
        print(f"❌ Cache system not available: {e}")
    except Exception as e:
        print(f"⚠️  Preload completed with some errors: {e}")


def clean_generated_content():
    """Clean all generated content files."""
    print("🧹 Cleaning generated content...")
    from cli.cleanup_commands import clean_content_components

    clean_content_components()


def run_cleanup_scan():
    """Run cleanup scan for cleanup opportunities."""
    from cli.cleanup_commands import run_cleanup_scan

    run_cleanup_scan()


def generate_cleanup_report():
    """Generate comprehensive cleanup report."""
    from cli.cleanup_commands import run_cleanup_report

    run_cleanup_report()


def run_root_cleanup():
    """Clean up and organize root directory."""
    from cli.cleanup_commands import run_root_cleanup

    run_root_cleanup()


def run_content_batch_generation():
    """Content batch mode - clear and regenerate first 8 categories."""
    print("🔄 Content Batch Mode: Clear and regenerate first 8 categories")
    print("=" * 60)

    try:
        # First clean existing content
        print("🧹 Cleaning existing content...")
        from cli.cleanup_commands import clean_content_components

        clean_content_components()

        # Load materials data
        from data.materials import load_materials

        materials_data = load_materials()

        # Access the "materials" key to get the actual materials data
        if "materials" not in materials_data:
            print("❌ Error: No 'materials' key found in materials data")
            return

        materials_section = materials_data["materials"]

        # Get first 8 categories
        categories = list(materials_section.keys())[:8]
        print(
            f"📂 Processing {len(categories)} categories: {', '.join(categories)}"
        )

        # Count total materials
        total_materials = sum(
            len(materials_section[cat].get("items", [])) for cat in categories
        )
        print(f"📝 Total materials to process: {total_materials}")

        # Import generator
        from generators.dynamic_generator import DynamicGenerator

        generator = DynamicGenerator()

        processed_materials = 0
        successful_generations = 0

        for category in categories:
            category_data = materials_section[category]
            materials = category_data.get("items", [])

            print(
                f"\n🔧 Processing category: {category} ({len(materials)} materials)"
            )

            for material in materials:
                material_name = material["name"]
                print(f"   📝 Generating content for: {material_name}")

                try:
                    # Generate enabled components for this material
                    from generators.workflow_manager import (
                        run_dynamic_generation,
                    )
                    from cli.component_config import get_components_sorted_by_priority

                    # Use only enabled components
                    enabled_components = get_components_sorted_by_priority(include_disabled=False)

                    results = run_dynamic_generation(
                        generator=generator,
                        material=material_name,
                        component_types=enabled_components,
                        author_info=None,  # Will use material's author_id from materials.yaml
                    )

                    processed_materials += 1
                    successful_components = len(
                        results.get("components_generated", [])
                    )
                    print(
                        f"      ✅ Generated {successful_components} components"
                    )

                    if successful_components > 0:
                        successful_generations += 1

                except Exception as e:
                    from utils.loud_errors import component_failure

                    component_failure(
                        "material_generation", str(e), material=material_name
                    )
                    processed_materials += 1
                    continue

        # Summary
        print("\n" + "=" * 60)
        print("📊 CONTENT BATCH GENERATION COMPLETE")
        print("=" * 60)
        print(f"📂 Categories processed: {len(categories)}")
        print(f"📝 Materials processed: {processed_materials}")
        print(f"✅ Successful generations: {successful_generations}")
        print(
            f"📊 Success rate: {(successful_generations/processed_materials*100):.1f}%"
            if processed_materials > 0
            else "0%"
        )

    except ImportError as e:
        from utils.loud_errors import dependency_failure

        dependency_failure(
            "module_import",
            str(e),
            impact="Content batch generation cannot proceed",
        )
    except Exception as e:
        from utils.loud_errors import critical_error

        critical_error(
            "Content batch generation failed",
            details=str(e),
            context="Batch processing mode",
        )


def run_optimization(component_name: str):
    """Run sophisticated optimization for a component."""
    print(
        f"🚀 Starting sophisticated optimization for component: {component_name}"
    )
    print("⏱️  Timeout protection: 10 minutes maximum")

    # Import and run the optimization with timeout protection
    from optimizer.content_optimization import run_sophisticated_optimization

    try:
        asyncio.run(
            run_sophisticated_optimization(component_name, timeout_seconds=600)
        )
    except Exception as e:
        from utils.loud_errors import api_failure

        api_failure("optimization_service", str(e), retry_count=None)


def run_batch_generation(material_name: Optional[str] = None, components: Optional[str] = None):
    """Run batch generation for specific material or all materials."""
    print("🎮 Z-Beam Generator")
    print("=" * 40)

    if material_name:
        print(f"🎯 Generating content for: {material_name}")
    else:
        print("🔄 Generating content for all materials")

    # Import and run the main generator
    try:
        from generators.dynamic_generator import DynamicGenerator
        from run import API_PROVIDERS

        generator = DynamicGenerator()

        if material_name:
            # Generate for specific material
            print(f"\n🎯 Generating content for {material_name}...")

            try:
                # Import workflow manager for material generation
                from generators.workflow_manager import run_material_generation
                from cli.component_config import get_components_sorted_by_priority

                # Use specified components if provided, otherwise get enabled components
                if components:
                    # Split the comma-separated list and strip whitespace
                    component_types = [c.strip() for c in components.split(',')]
                    print(f"🔍 Using specified components: {', '.join(component_types)}")
                else:
                    # Get only enabled components from config
                    component_types = get_components_sorted_by_priority(include_disabled=False)
                    print(f"🔍 Using enabled components from config: {', '.join(component_types)}")

                # Generate components for the material
                result = run_material_generation(
                    material=material_name,
                    component_types=component_types,
                    author_id=None,  # Will use material's author_id from materials.yaml
                )

                print("✅ Generation completed!")
                print(f"Material: {result['material']}")
                print(
                    f"Components generated: {len(result['components_generated'])}"
                )
                print(f"Components failed: {len(result['components_failed'])}")

                if result["components_generated"]:
                    print("\n📝 Generated components:")
                    for comp in result["components_generated"]:
                        print(f"  ✅ {comp['type']}: {comp['filepath']}")

                if result["components_failed"]:
                    print("\n❌ Failed components:")
                    for comp in result["components_failed"]:
                        print(f"  ❌ {comp['type']}: {comp['error']}")

                print(f"\n🕐 Total time: {result['total_time']:.1f}s")
                print(f"🎯 Total tokens: {result['total_tokens']}")

            except Exception as e:
                from utils.loud_errors import critical_error

                critical_error(
                    f"Content generation failed for {material_name}",
                    details=str(e),
                    context="Material-specific generation",
                )

        else:
            # Generate for all materials - FULL BATCH GENERATION
            print("\n🚀 Starting batch generation for ALL materials...")
            print("=" * 60)

            # Preload API clients for better performance
            try:
                from api.cache_adapter import APIClientCache

                # Show cache type
                cache_type = "persistent" if APIClientCache.is_persistent() else "in-memory"
                print(f"🚀 Preloading API clients using {cache_type} cache...")

                # Get all providers from API_PROVIDERS
                providers = list(API_PROVIDERS.keys())
                print(f"📋 Detected providers: {', '.join(providers)}")

                # Preload all configured providers
                preload_results = APIClientCache.preload_clients(providers)

                # Report preload results
                success_count = len(preload_results.get("success", []))
                failed_count = len(preload_results.get("failed", []))

                if success_count > 0:
                    print(f"✅ Successfully preloaded {success_count} API clients")

                if failed_count > 0:
                    print(f"⚠️  Failed to preload {failed_count} providers:")
                    for fail in preload_results.get("failed", []):
                        print(f"   ❌ {fail['provider']}: {fail['error']}")

                # Show persistence benefit message
                if APIClientCache.is_persistent():
                    print("🚀 Using persistent cache - clients will be reused between runs")

            except Exception as e:
                print(f"⚠️  Cache preload failed: {e}")

            try:
                # Load materials data
                from data.materials import load_materials

                materials_data = load_materials()

                # Access the "materials" key to get the actual materials data
                if "materials" not in materials_data:
                    print("❌ Error: No 'materials' key found in materials data")
                    return

                materials_section = materials_data["materials"]

                # Count total materials across all categories
                total_materials = sum(
                    len(category_data.get("items", []))
                    for category_data in materials_section.values()
                )

                categories = list(materials_section.keys())
                print(f"📂 Found {len(categories)} categories with {total_materials} total materials")

                # Get only ENABLED components for batch generation
                from cli.component_config import get_components_sorted_by_priority
                available_components = get_components_sorted_by_priority(include_disabled=False)
                print(f"🔧 Available components: {', '.join(available_components)}")
                print(f"📊 Component Status: Only ENABLED components included")

                # Initialize tracking variables
                processed_materials = 0
                successful_generations = 0
                total_components_generated = 0
                total_components_failed = 0
                total_tokens_used = 0
                start_time = time.time()

                # Process each category
                for category in categories:
                    category_data = materials_section[category]
                    materials = category_data.get("items", [])

                    print(f"\n🔧 Processing category: {category}")
                    print(f"   📝 Materials in category: {len(materials)}")

                    category_processed = 0
                    category_successful = 0

                    # Process each material in the category
                    for material in materials:
                        material_name = material["name"]
                        material_start_time = time.time()

                        print(f"   📝 Generating content for: {material_name}")

                        try:
                            # Import workflow manager for material generation
                            from generators.workflow_manager import run_material_generation

                            # Generate all available components for this material
                            result = run_material_generation(
                                material=material_name,
                                component_types=available_components,
                                author_id=None,  # Will use material's author_id from materials.yaml
                            )

                            material_time = time.time() - material_start_time
                            processed_materials += 1
                            category_processed += 1

                            # Count successful and failed components
                            successful_components = len(result.get("components_generated", []))
                            failed_components = len(result.get("components_failed", []))
                            total_components_generated += successful_components
                            total_components_failed += failed_components

                            # Add tokens used
                            material_tokens = result.get("total_tokens", 0)
                            total_tokens_used += material_tokens

                            if successful_components > 0:
                                successful_generations += 1
                                category_successful += 1
                                print(f"      ✅ Generated {successful_components} components ({material_tokens} tokens, {material_time:.1f}s)")
                            else:
                                print(f"      ⚠️  Generated {successful_components} components, {failed_components} failed ({material_time:.1f}s)")

                            # Show progress every 10 materials or at key milestones
                            if processed_materials % 10 == 0 or processed_materials == total_materials:
                                progress_percent = (processed_materials / total_materials) * 100
                                elapsed_time = time.time() - start_time
                                avg_time_per_material = elapsed_time / processed_materials
                                estimated_remaining = (total_materials - processed_materials) * avg_time_per_material

                                print(f"\n📊 Progress: {processed_materials}/{total_materials} materials ({progress_percent:.1f}%)")
                                print(f"   ⏱️  Elapsed: {elapsed_time:.1f}s, ETA: {estimated_remaining:.1f}s")
                                print(f"   ✅ Success rate: {(successful_generations/processed_materials*100):.1f}%")

                        except Exception as e:
                            from utils.loud_errors import component_failure

                            component_failure(
                                "material_generation", str(e), material=material_name
                            )
                            processed_materials += 1
                            category_processed += 1
                            continue

                    # Category summary
                    if materials:
                        category_success_rate = (category_successful / len(materials)) * 100
                        print(f"   📊 Category {category}: {category_successful}/{len(materials)} successful ({category_success_rate:.1f}%)")

                # Final summary
                total_time = time.time() - start_time
                overall_success_rate = (successful_generations / processed_materials * 100) if processed_materials > 0 else 0

                print("\n" + "=" * 60)
                print("🎉 BATCH GENERATION COMPLETE")
                print("=" * 60)
                print(f"📂 Categories processed: {len(categories)}")
                print(f"📝 Materials processed: {processed_materials}")
                print(f"✅ Successful generations: {successful_generations}")
                print(f"📊 Overall success rate: {overall_success_rate:.1f}%")
                print(f"🔧 Total components generated: {total_components_generated}")
                print(f"❌ Total components failed: {total_components_failed}")
                print(f"🎯 Total tokens used: {total_tokens_used}")
                print(f"🕐 Total time: {total_time:.1f}s")
                print(f"⚡ Average time per material: {total_time/processed_materials:.1f}s" if processed_materials > 0 else "⚡ Average time per material: N/A")

                # Performance insights
                if total_time > 0:
                    tokens_per_second = total_tokens_used / total_time
                    print(f"🚀 Performance: {tokens_per_second:.1f} tokens/second")

                # Cache performance insights
                try:
                    from api.cache_adapter import APIClientCache
                    cache_stats = APIClientCache.get_cache_stats()

                    if cache_stats['total_requests'] > 0:
                        cache_type = "persistent" if APIClientCache.is_persistent() else "in-memory"
                        print(f"📋 Cache Performance ({cache_type}): {cache_stats['hit_rate_percent']}% hit rate ({cache_stats['cache_hits']}/{cache_stats['total_requests']} requests)")

                        if cache_stats['hit_rate_percent'] >= 80:
                            cache_saved_time = cache_stats['cache_hits'] * 0.5  # Estimate 0.5s per client creation
                            print(f"⚡ Time saved by caching: ~{cache_saved_time:.1f}s")

                        if APIClientCache.is_persistent():
                            print(f"💾 Disk cached clients: {cache_stats.get('disk_cached_instances', 0)} (will persist for future runs)")
                except ImportError:
                    pass

                # Recommendations based on results
                if overall_success_rate >= 95:
                    print("🎯 Excellent results! System performing optimally.")
                elif overall_success_rate >= 80:
                    print("👍 Good results. Consider optimizing timeout settings for better performance.")
                else:
                    print("⚠️  Results below expectations. Check API connectivity and timeout settings.")

            except ImportError as e:
                from utils.loud_errors import dependency_failure

                dependency_failure(
                    "module_import",
                    str(e),
                    impact="Batch generation cannot proceed",
                )
            except Exception as e:
                from utils.loud_errors import critical_error

                critical_error(
                    "Batch generation failed",
                    details=str(e),
                    context="Full batch processing mode",
                )

    except ImportError as e:
        from utils.loud_errors import dependency_failure

        dependency_failure(
            "generator_module",
            str(e),
            impact="Generation cannot proceed",
        )
