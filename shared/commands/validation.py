def generate_content_validation_report(output_file: str) -> bool:
    """
    Generate comprehensive content quality validation report for all materials.
    
    Validates FAQ, Caption, and Subtitle quality using ContentValidationService.
    Produces detailed multi-dimensional scoring and recommendations.
    
    Args:
        output_file: Path to save the validation report
        
    Returns:
        True if report generated successfully
    """
    from pathlib import Path
    from datetime import datetime
    from shared.validation.integration import validate_generated_content, get_dimension_scores_dict
    from domains.materials.materials_cache import load_materials, get_material_by_name
    from export.utils.author_manager import get_author_info_for_material
    
    print("📊 Generating Content Quality Validation Report")
    print("=" * 80)
    
    # Load materials
    materials_data = load_materials()
    
    # Collect validation results
    validation_results = []
    total_materials = 0
    materials_with_content = 0
    
    for material_name in materials_data.get('materials', {}).keys():
        total_materials += 1
        material_info = get_material_by_name(material_name, materials_data)
        
        if not material_info:
            continue
        
        # Get author info
        author_info = get_author_info_for_material(material_info)
        if not author_info:
            author_info = {'name': 'Unknown', 'country': 'Unknown'}
        
        # Check for FAQ, Caption, Subtitle content
        has_content = False
        material_results = {
            'material_name': material_name,
            'author': author_info.get('name'),
            'country': author_info.get('country'),
            'faq': None,
            'micro': None,
            'subtitle': None
        }
        
        # Validate FAQ if exists
        faq_questions = material_info.get('questions', [])
        if faq_questions:
            has_content = True
            try:
                result = validate_generated_content(
                    content={'questions': faq_questions},
                    component_type='faq',
                    material_name=material_name,
                    author_info=author_info,
                    log_report=False
                )
                material_results['faq'] = {
                    'success': result.success,
                    'overall_score': result.overall_score,
                    'grade': result.grade,
                    'dimensions': get_dimension_scores_dict(result),
                    'issues': result.critical_issues,
                    'warnings': result.warnings,
                    'recommendations': result.recommendations
                }
            except Exception as e:
                material_results['faq'] = {'error': str(e)}
        
        # Validate Caption if exists
        micro_data = material_info.get('micro', {})
        if isinstance(micro_data, dict):
            before_text = micro_data.get('before')
            after_text = micro_data.get('after')
            if before_text or after_text:
                has_content = True
                try:
                    result = validate_generated_content(
                        content={'before': before_text or '', 'after': after_text or ''},
                        component_type='micro',
                        material_name=material_name,
                        author_info=author_info,
                        log_report=False
                    )
                    material_results['micro'] = {
                        'success': result.success,
                        'overall_score': result.overall_score,
                        'grade': result.grade,
                        'dimensions': get_dimension_scores_dict(result),
                        'issues': result.critical_issues,
                        'warnings': result.warnings,
                        'recommendations': result.recommendations
                    }
                except Exception as e:
                    material_results['micro'] = {'error': str(e)}
        
        # Validate Subtitle if exists
        subtitle = material_info.get('subtitle')
        if subtitle:
            has_content = True
            try:
                result = validate_generated_content(
                    content=subtitle,
                    component_type='subtitle',
                    material_name=material_name,
                    author_info=author_info,
                    log_report=False
                )
                material_results['subtitle'] = {
                    'success': result.success,
                    'overall_score': result.overall_score,
                    'grade': result.grade,
                    'dimensions': get_dimension_scores_dict(result),
                    'issues': result.critical_issues,
                    'warnings': result.warnings,
                    'recommendations': result.recommendations
                }
            except Exception as e:
                material_results['subtitle'] = {'error': str(e)}
        
        if has_content:
            materials_with_content += 1
            validation_results.append(material_results)
            print(f"✅ Validated {material_name}: FAQ={material_results['faq'] is not None}, Caption={material_results['micro'] is not None}, Subtitle={material_results['subtitle'] is not None}")
    
    # Generate report
    print(f"\n📝 Generating report to {output_file}")
    
    with open(output_file, 'w') as f:
        f.write("# Content Quality Validation Report\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Materials**: {total_materials}\n")
        f.write(f"**Materials with Content**: {materials_with_content}\n\n")
        f.write("---\n\n")
        
        # Summary statistics
        total_scores = {'faq': [], 'micro': [], 'subtitle': []}
        total_grades = {'faq': {}, 'micro': {}, 'subtitle': {}}
        
        for result in validation_results:
            for component in ['faq', 'micro', 'subtitle']:
                if result[component] and 'overall_score' in result[component]:
                    total_scores[component].append(result[component]['overall_score'])
                    grade = result[component]['grade']
                    total_grades[component][grade] = total_grades[component].get(grade, 0) + 1
        
        f.write("## Summary Statistics\n\n")
        for component in ['FAQ', 'Caption', 'Subtitle']:
            comp_key = component.lower()
            if total_scores[comp_key]:
                avg_score = sum(total_scores[comp_key]) / len(total_scores[comp_key])
                f.write(f"### {component}\n")
                f.write(f"- **Count**: {len(total_scores[comp_key])}\n")
                f.write(f"- **Average Score**: {avg_score:.1f}/100\n")
                f.write(f"- **Grade Distribution**: {', '.join(f'{g}: {c}' for g, c in sorted(total_grades[comp_key].items()))}\n\n")
        
        f.write("---\n\n")
        f.write("## Detailed Validation Results\n\n")
        
        # Detailed results per material
        for result in validation_results:
            f.write(f"### {result['material_name']}\n\n")
            f.write(f"**Author**: {result['author']} ({result['country']})\n\n")
            
            for component in ['FAQ', 'Caption', 'Subtitle']:
                comp_key = component.lower()
                comp_result = result[comp_key]
                
                if comp_result is None:
                    continue
                
                f.write(f"#### {component}\n\n")
                
                if 'error' in comp_result:
                    f.write(f"❌ **Error**: {comp_result['error']}\n\n")
                    continue
                
                status = "✅ PASSED" if comp_result['success'] else "⚠️ FAILED"
                f.write(f"{status} - **Score**: {comp_result['overall_score']:.1f}/100 - **Grade**: {comp_result['grade']}\n\n")
                
                # Dimension scores
                f.write("**Dimension Scores**:\n")
                dims = comp_result['dimensions']
                f.write(f"- Author Voice: {dims.get('author_voice', 0):.1f}\n")
                f.write(f"- Variation: {dims.get('variation', 0):.1f}\n")
                f.write(f"- Human Characteristics: {dims.get('human_characteristics', 0):.1f}\n")
                f.write(f"- AI Avoidance: {dims.get('ai_avoidance', 0):.1f}\n\n")
                
                # Issues
                if comp_result['issues']:
                    f.write("**Critical Issues**:\n")
                    for issue in comp_result['issues']:
                        f.write(f"- {issue}\n")
                    f.write("\n")
                
                # Warnings
                if comp_result['warnings']:
                    f.write("**Warnings**:\n")
                    for warning in comp_result['warnings']:
                        f.write(f"- {warning}\n")
                    f.write("\n")
                
                # Recommendations
                if comp_result['recommendations']:
                    f.write("**Recommendations**:\n")
                    for rec in comp_result['recommendations']:
                        f.write(f"- {rec}\n")
                    f.write("\n")
            
            f.write("---\n\n")
    
    print(f"\n✅ Report generated: {output_file}")
    print(f"   Validated {materials_with_content} materials with content")
    return True


