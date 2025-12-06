#!/usr/bin/env python3
"""
Pipeline Stage Verification Tool

Verifies each generation goes through all required stages:
1. Humanness Layer Generation
2. Content Generation 
3. Winston AI Detection
4. Subjective Evaluation (Realism)
5. Database Logging
6. Sweet Spot Learning
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import sys

def main():
    print("=" * 80)
    print("🔍 PIPELINE STAGE VERIFICATION")
    print("=" * 80)
    print()

    # Check if Winston database exists
    db_path = Path('z-beam.db')
    if not db_path.exists():
        print("❌ Database not found at z-beam.db")
        return 1

    print("✅ Database found at z-beam.db")
    print()

    # Connect to database
    conn = sqlite3.connect('z-beam.db')
    cursor = conn.cursor()

    # Get table list
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    print("📊 DATABASE TABLES:")
    for table in tables:
        print(f"   • {table}")
    print()

    # Stage 1: Check Winston detection results (AI detection stage)
    print("🔎 STAGE 1: Winston AI Detection")
    cursor.execute("""
        SELECT material, component_type, timestamp, human_score, ai_score, success
        FROM detection_results 
        ORDER BY timestamp DESC 
        LIMIT 5
    """)
    results = cursor.fetchall()

    if results:
        print(f"   ✅ Found {len(results)} recent detections")
        for mat, comp, ts, human, ai, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   • {mat}/{comp}: {human*100:.1f}% human, {ai*100:.1f}% AI {status}")
    else:
        print("   ⚠️  No detection results found")
    print()

    # Stage 2: Check subjective evaluations (Realism scoring stage)
    print("🎨 STAGE 2: Subjective Evaluation (Realism)")
    cursor.execute("""
        SELECT topic, component_type, timestamp, overall_score, passes_quality_gate
        FROM subjective_evaluations 
        ORDER BY timestamp DESC 
        LIMIT 5
    """)
    results = cursor.fetchall()

    if results:
        print(f"   ✅ Found {len(results)} recent evaluations")
        for topic, comp, ts, score, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   • {topic}/{comp}: {score}/10 {status}")
    else:
        print("   ⚠️  No subjective evaluations found")
    print()

    # Stage 3: Check generation parameters (Parameter tracking stage)
    print("⚙️  STAGE 3: Generation Parameters")
    cursor.execute("""
        SELECT material, component_type, timestamp, temperature, attempt_number
        FROM generation_parameters 
        ORDER BY timestamp DESC 
        LIMIT 5
    """)
    results = cursor.fetchall()

    if results:
        print(f"   ✅ Found {len(results)} parameter records")
        for mat, comp, ts, temp, attempt in results:
            print(f"   • {mat}/{comp}: temp={temp:.3f}, attempt={attempt}")
    else:
        print("   ⚠️  No parameter records found")
    print()

    # Stage 4: Check sweet spot recommendations (Learning stage)
    print("🎯 STAGE 4: Sweet Spot Learning")
    cursor.execute("""
        SELECT component_type, COUNT(*) as samples, confidence_level, last_updated
        FROM sweet_spot_recommendations 
        GROUP BY component_type
        ORDER BY last_updated DESC
    """)
    results = cursor.fetchall()

    if results:
        print(f"   ✅ Found recommendations for {len(results)} component types")
        for comp, samples, confidence, updated in results:
            print(f"   • {comp}: {samples} samples, confidence: {confidence}")
    else:
        print("   ⚠️  No sweet spot recommendations found")
    print()

    # Stage 5: Complete pipeline verification for most recent generation
    print("🔗 STAGE 5: End-to-End Pipeline Verification")
    print("   Checking if most recent generation completed ALL stages:")
    print()

    # Get most recent detection
    cursor.execute("""
        SELECT id, material, component_type, timestamp, success
        FROM detection_results 
        ORDER BY timestamp DESC 
        LIMIT 1
    """)
    detection = cursor.fetchone()

    if detection:
        det_id, material, comp_type, timestamp, success = detection
        print(f"   📍 Latest generation: {material}/{comp_type}")
        print(f"   📅 Timestamp: {timestamp}")
        print(f"   ✅ Stage 1 (Winston): {'PASS' if success else 'FAIL'}")
        
        # Check if subjective evaluation exists
        cursor.execute("""
            SELECT overall_score, passes_quality_gate
            FROM subjective_evaluations 
            WHERE topic = ? AND component_type = ?
            ORDER BY timestamp DESC LIMIT 1
        """, (material, comp_type))
        
        subj = cursor.fetchone()
        if subj:
            score, passed = subj
            print(f"   ✅ Stage 2 (Subjective): {score}/10 {'PASS' if passed else 'FAIL'}")
        else:
            print(f"   ⚠️  Stage 2 (Subjective): NOT FOUND")
        
        # Check if parameters logged
        cursor.execute("""
            SELECT temperature, attempt_number
            FROM generation_parameters 
            WHERE material = ? AND component_type = ?
            ORDER BY timestamp DESC LIMIT 1
        """, (material, comp_type))
        
        params = cursor.fetchone()
        if params:
            temp, attempt = params
            print(f"   ✅ Stage 3 (Parameters): temp={temp:.3f}, attempt={attempt}")
        else:
            print("   ⚠️  Stage 3 (Parameters): NOT FOUND")
        
        # Check if sweet spot updated
        cursor.execute("""
            SELECT COUNT(*) 
            FROM sweet_spot_recommendations 
            WHERE component_type = ?
        """, (comp_type,))
        
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"   ✅ Stage 4 (Sweet Spot): {count} recommendations exist")
        else:
            print(f"   ⚠️  Stage 4 (Sweet Spot): NOT FOUND")
        
        print()
        print("   📊 Pipeline Status:")
        stages_complete = sum([
            success,  # Winston
            subj is not None,  # Subjective
            params is not None,  # Parameters
            count > 0  # Sweet spot
        ])
        print(f"   {stages_complete}/4 stages verified in database")

    else:
        print("   ❌ No generations found in database")

    print()
    
    # Stage 6: Check Humanness Layer Integration
    print("🧠 STAGE 6: Humanness Layer Integration")
    
    # Check Winston patterns
    cursor.execute("SELECT COUNT(*) FROM ai_patterns")
    winston_patterns = cursor.fetchone()[0]
    print(f"   ✅ Winston patterns: {winston_patterns} stored")
    
    # Check if humanness_layer.txt exists
    humanness_template = Path('shared/text/templates/system/humanness_layer.txt')
    if humanness_template.exists():
        print(f"   ✅ Humanness template: {humanness_template}")
    else:
        print(f"   ⚠️  Humanness template: NOT FOUND")
    
    # Check subjective patterns YAML
    subjective_patterns = Path('shared/text/templates/evaluation/learned_patterns.yaml')
    if subjective_patterns.exists():
        print(f"   ✅ Subjective patterns: {subjective_patterns}")
    else:
        print(f"   ⚠️  Subjective patterns: NOT FOUND")
    
    print()
    print("=" * 80)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 80)
    print()
    print("💡 VERIFICATION METHODS:")
    print("   1. Real-time logging: python3 run.py --caption Material 2>&1 | grep '✅\\|🎯\\|Quality Gate'")
    print("   2. Database queries: python3 scripts/verify_pipeline_stages.py")
    print("   3. Integrity checks: python3 run.py --caption Material (without --skip-integrity-check)")
    print("   4. Manual inspection: sqlite3 z-beam.db 'SELECT * FROM detection_results'")
    print()

    conn.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
