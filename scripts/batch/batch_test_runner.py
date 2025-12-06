#!/usr/bin/env python3
"""
Direct Batch Test Runner with Real-Time Output

Runs batch caption generation with immediate, unbuffered output.
No hanging, no buffering issues, progress visible immediately.
"""

import sys
import subprocess
import time

# Unbuffered output
sys.stdout = open(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = open(sys.stderr.fileno(), 'w', buffering=1)

print("🚀 BATCH CAPTION TEST - DIRECT RUNNER")
print("=" * 70)
print()

# Test materials (matching --batch-test)
materials = ["Bamboo", "Alabaster", "Breccia", "Aluminum"]

print(f"📋 Testing {len(materials)} materials:")
for i, mat in enumerate(materials, 1):
    print(f"   {i}. {mat}")
print()

results = []
start_time = time.time()

for i, material in enumerate(materials, 1):
    print("=" * 70)
    print(f"TEST {i}/{len(materials)}: {material}")
    print("=" * 70)
    print()
    
    test_start = time.time()
    
    # Run caption generation with real-time output
    cmd = ["python3", "run.py", "--caption", material]
    
    print(f"🚀 Running: {' '.join(cmd)}")
    print()
    
    try:
        # Use unbuffered output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        # Stream output in real-time
        for line in process.stdout:
            print(line, end='', flush=True)
        
        process.wait()
        exit_code = process.returncode
        
        test_elapsed = time.time() - test_start
        
        if exit_code == 0:
            print(f"\n✅ {material}: SUCCESS ({test_elapsed:.1f}s)")
            results.append((material, "SUCCESS", test_elapsed))
        else:
            print(f"\n❌ {material}: FAILED (exit code {exit_code}, {test_elapsed:.1f}s)")
            results.append((material, "FAILED", test_elapsed))
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrupted during {material}")
        results.append((material, "INTERRUPTED", time.time() - test_start))
        break
    except Exception as e:
        print(f"\n💥 ERROR during {material}: {e}")
        results.append((material, "ERROR", time.time() - test_start))
    
    print()

# Summary
total_elapsed = time.time() - start_time

print()
print("=" * 70)
print("📊 BATCH TEST SUMMARY")
print("=" * 70)
print()

success_count = sum(1 for _, status, _ in results if status == "SUCCESS")
fail_count = sum(1 for _, status, _ in results if status == "FAILED")
error_count = sum(1 for _, status, _ in results if status in ["ERROR", "INTERRUPTED"])

for material, status, elapsed in results:
    icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "⚠️"
    print(f"{icon} {material}: {status} ({elapsed:.1f}s)")

print()
print(f"Total: {success_count} success, {fail_count} failed, {error_count} errors")
print(f"Time: {total_elapsed:.1f}s ({total_elapsed/60:.1f}m)")
print()

# Exit with appropriate code
if success_count == len(materials):
    print("✅ All tests passed!")
    sys.exit(0)
elif success_count > 0:
    print("⚠️  Partial success")
    sys.exit(1)
else:
    print("❌ All tests failed")
    sys.exit(2)
