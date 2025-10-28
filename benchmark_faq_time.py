#!/usr/bin/env python3
"""Benchmark FAQ generation time for a single material"""

import sys
import time
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from components.faq.generators.faq_generator import FAQComponentGenerator

def benchmark_faq_generation():
    print("⏱️  FAQ Generation Time Benchmark\n")
    
    # Initialize generator
    print("🔧 Initializing FAQ generator...")
    start_init = time.time()
    faq_gen = FAQComponentGenerator()
    init_time = time.time() - start_init
    print(f"   Initialization: {init_time:.2f}s\n")
    
    # Load materials
    materials_file = Path("data/Materials.yaml")
    with open(materials_file, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    test_material = "Titanium"
    
    print(f"📊 Benchmarking: {test_material}")
    print("="*60)
    
    # Time breakdown
    start_total = time.time()
    
    # Step 1: Load data
    start_step = time.time()
    material_data = materials_data['materials'][test_material]
    material_data['name'] = test_material
    
    frontmatter_data = faq_gen._load_frontmatter_data(test_material)
    categories_data = faq_gen._load_categories_data()
    step1_time = time.time() - start_step
    print(f"1. Data Loading: {step1_time:.2f}s")
    
    # Step 2: Determine question count
    start_step = time.time()
    question_count = faq_gen._determine_question_count(material_data, test_material)
    step2_time = time.time() - start_step
    print(f"2. Question Count Calculation: {step2_time:.3f}s")
    
    # Step 3: Generate questions (intelligent scoring)
    start_step = time.time()
    questions = faq_gen._generate_material_questions(
        test_material,
        material_data,
        frontmatter_data,
        categories_data,
        question_count
    )
    step3_time = time.time() - start_step
    print(f"3. Question Generation (Scoring): {step3_time:.3f}s")
    print(f"   - Questions selected: {len(questions)}")
    
    # Step 4: Generate answers (API calls)
    print(f"\n4. Answer Generation (API calls):")
    api_times = []
    for i, q in enumerate(questions, 1):
        start_api = time.time()
        
        # Simulate what happens in generate() method
        prompt = faq_gen._build_faq_answer_prompt(
            test_material,
            q['template'],
            q['focus'],
            frontmatter_data,
            material_data,
            categories_data,
            target_words=40
        )
        
        api_time = time.time() - start_api
        api_times.append(api_time)
        
        if i <= 3 or i == len(questions):
            print(f"   Q{i}: {api_time:.3f}s (prompt building)")
    
    step4_time = sum(api_times)
    print(f"   Total prompt building: {step4_time:.3f}s")
    print(f"   Average per question: {step4_time/len(questions):.3f}s")
    
    # Estimate actual API call time
    estimated_api_time = len(questions) * 2.5  # ~2-3s per API call typical
    print(f"\n   Estimated API call time: {estimated_api_time:.1f}s")
    print(f"   (Based on {len(questions)} questions × ~2.5s per call)")
    
    total_time = time.time() - start_total
    total_with_api = total_time - step4_time + estimated_api_time
    
    print(f"\n{'='*60}")
    print(f"📊 TIME BREAKDOWN:")
    print(f"{'='*60}")
    print(f"Data Loading:           {step1_time:6.2f}s  ({step1_time/total_with_api*100:4.1f}%)")
    print(f"Question Counting:      {step2_time:6.3f}s  ({step2_time/total_with_api*100:4.1f}%)")
    print(f"Intelligent Scoring:    {step3_time:6.3f}s  ({step3_time/total_with_api*100:4.1f}%)")
    print(f"Prompt Building:        {step4_time:6.3f}s  ({step4_time/total_with_api*100:4.1f}%)")
    print(f"API Calls (estimated):  {estimated_api_time:6.1f}s  ({estimated_api_time/total_with_api*100:4.1f}%)")
    print(f"YAML Export:            ~0.1s  (  0.3%)")
    print(f"{'='*60}")
    print(f"TOTAL (estimated):      {total_with_api:6.1f}s")
    print(f"{'='*60}")
    
    print(f"\n⏱️  GENERATION TIME PER MATERIAL:")
    print(f"   Best case (cached):      ~{total_with_api*0.5:4.1f}s  (faster API)")
    print(f"   Typical:                 ~{total_with_api:4.1f}s")
    print(f"   Worst case (rate limit): ~{total_with_api*1.5:4.1f}s  (slower API)")
    
    print(f"\n📈 BATCH GENERATION ESTIMATES:")
    print(f"   10 materials:   ~{total_with_api*10/60:5.1f} minutes")
    print(f"   50 materials:   ~{total_with_api*50/60:5.1f} minutes")
    print(f"   132 materials:  ~{total_with_api*132/60:5.1f} minutes ({total_with_api*132/3600:.1f} hours)")
    
    print(f"\n💡 OPTIMIZATION NOTES:")
    print(f"   - API calls dominate: {estimated_api_time/total_with_api*100:.0f}% of total time")
    print(f"   - Intelligent scoring is fast: {step3_time:.3f}s ({step3_time/total_with_api*100:.1f}%)")
    print(f"   - Can parallelize with multiple API keys")
    print(f"   - Response caching would reduce repeat generations")

if __name__ == "__main__":
    benchmark_faq_generation()
