#!/usr/bin/env python3
"""
Next.js Context-Aware Frontmatter Organization
Reorganizes frontmatter based on Next.js app component usage patterns.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, '/Users/todddunning/Desktop/Z-Beam/z-beam-generator')

class NextJSAwareFrontmatterOptimizer:
    """Optimizes frontmatter based on Next.js app component usage patterns."""
    
    def __init__(self):
        self.component_purposes = {
            "caption": "Microscopic photo descriptions and technical analysis",
            "table": "Short string data display (overflow from materialProperties/machineSettings)",
            "tags": "Clickable search navigation tags",
            "jsonld": "SEO structured data for search engines",
            "metatags": "HTML meta tags for social media and SEO"
        }
    
    def analyze_current_organization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current frontmatter organization against Next.js usage patterns."""
        
        print("🔍 ANALYZING FRONTMATTER FOR NEXT.JS OPTIMIZATION")
        print("=" * 60)
        
        analysis = {
            "component_alignment": {},
            "data_placement": {},
            "optimization_opportunities": [],
            "nextjs_recommendations": []
        }
        
        # Check componentOutputs structure
        if 'componentOutputs' in data:
            components = data['componentOutputs']
            
            # Analyze Caption component
            if 'caption' in components:
                caption_data = components['caption']
                analysis["component_alignment"]["caption"] = self._analyze_caption_alignment(caption_data)
            
            # Analyze Table needs
            analysis["component_alignment"]["table"] = self._analyze_table_needs(data)
            
            # Analyze Tags component
            if 'tags' in components:
                tags_data = components['tags']
                analysis["component_alignment"]["tags"] = self._analyze_tags_alignment(tags_data)
            
            # Analyze metadata components
            for meta_comp in ['jsonld', 'metatags']:
                if meta_comp in components:
                    analysis["component_alignment"][meta_comp] = self._analyze_metadata_alignment(components[meta_comp], meta_comp)
        
        # Identify optimization opportunities
        analysis["optimization_opportunities"] = self._identify_nextjs_optimizations(data)
        
        # Generate Next.js specific recommendations
        analysis["nextjs_recommendations"] = self._generate_nextjs_recommendations(data, analysis)
        
        return analysis
    
    def _analyze_caption_alignment(self, caption_data: Dict) -> Dict[str, Any]:
        """Analyze caption component alignment with microscopic photo descriptions."""
        
        alignment = {
            "purpose_match": "microscopic_photo_descriptions",
            "current_structure": list(caption_data.keys()) if isinstance(caption_data, dict) else [],
            "optimization_score": 0,
            "issues": [],
            "recommendations": []
        }
        
        # Check for microscopic photo relevant content
        if 'beforeText' in caption_data and 'afterText' in caption_data:
            before_text = caption_data.get('beforeText', '')
            after_text = caption_data.get('afterText', '')
            
            # Check if text is suitable for microscopic descriptions
            microscopic_keywords = ['surface', 'contaminant', 'removal', 'cleaning', 'analysis', 'microscopy']
            before_score = sum(1 for keyword in microscopic_keywords if keyword.lower() in before_text.lower())
            after_score = sum(1 for keyword in microscopic_keywords if keyword.lower() in after_text.lower())
            
            alignment["optimization_score"] = (before_score + after_score) / len(microscopic_keywords) * 100
            
            if alignment["optimization_score"] > 50:
                alignment["recommendations"].append("✅ Caption content well-suited for microscopic descriptions")
            else:
                alignment["issues"].append("Caption content not optimized for microscopic photo context")
                alignment["recommendations"].append("🔧 Enhance caption with microscopic analysis terminology")
        
        # Check for technical analysis section
        if 'technicalAnalysis' in caption_data:
            tech_analysis = caption_data['technicalAnalysis']
            if isinstance(tech_analysis, dict) and tech_analysis:
                alignment["recommendations"].append("✅ Technical analysis present - good for microscopic context")
            else:
                alignment["issues"].append("Technical analysis missing or empty")
                alignment["recommendations"].append("🔧 Add detailed technical analysis for microscopic observations")
        
        return alignment
    
    def _analyze_table_needs(self, data: Dict) -> Dict[str, Any]:
        """Analyze if Table component is needed for overflow data."""
        
        table_analysis = {
            "purpose_match": "short_string_data_overflow",
            "overflow_detected": False,
            "potential_table_data": {},
            "recommendations": []
        }
        
        # Check materialProperties for string data
        if 'materialProperties' in data:
            props = data['materialProperties']
            string_properties = {}
            
            for prop_name, prop_data in props.items():
                if isinstance(prop_data, dict):
                    # Look for string values or complex data
                    if 'value' in prop_data:
                        value = prop_data['value']
                        if isinstance(value, str) and len(value) > 20:
                            string_properties[prop_name] = value
                        elif isinstance(value, (list, dict)):
                            string_properties[prop_name] = str(value)
            
            if string_properties:
                table_analysis["overflow_detected"] = True
                table_analysis["potential_table_data"]["materialProperties"] = string_properties
                table_analysis["recommendations"].append(f"🔧 Consider moving {len(string_properties)} string properties to Table component")
        
        # Check machineSettings for overflow
        if 'machineSettings' in data:
            settings = data['machineSettings']
            if isinstance(settings, dict) and len(settings) > 8:  # Threshold for table display
                table_analysis["overflow_detected"] = True
                table_analysis["potential_table_data"]["machineSettings"] = f"{len(settings)} settings"
                table_analysis["recommendations"].append("🔧 Machine settings may benefit from Table component display")
        
        # Check for other verbose data
        verbose_sections = ['applications', 'processes', 'outcomeMetrics']
        for section in verbose_sections:
            if section in data and isinstance(data[section], list) and len(data[section]) > 5:
                table_analysis["overflow_detected"] = True
                table_analysis["potential_table_data"][section] = f"{len(data[section])} items"
                table_analysis["recommendations"].append(f"🔧 {section} list could be displayed in Table component")
        
        return table_analysis
    
    def _analyze_tags_alignment(self, tags_data: Dict) -> Dict[str, Any]:
        """Analyze tags component alignment with clickable search functionality."""
        
        alignment = {
            "purpose_match": "clickable_search_navigation",
            "current_structure": list(tags_data.keys()) if isinstance(tags_data, dict) else [],
            "search_optimization": 0,
            "recommendations": []
        }
        
        # Check for essential tags
        if 'essentialTags' in tags_data:
            essential_tags = tags_data['essentialTags']
            if isinstance(essential_tags, list):
                # Analyze tag quality for search
                search_quality_score = 0
                
                # Check for material name
                material_tags = [tag for tag in essential_tags if any(material in tag.lower() for material in ['aluminum', 'steel', 'copper', 'glass'])]
                if material_tags:
                    search_quality_score += 25
                
                # Check for category tags
                category_tags = [tag for tag in essential_tags if any(cat in tag.lower() for cat in ['metal', 'glass', 'polymer', 'ceramic'])]
                if category_tags:
                    search_quality_score += 25
                
                # Check for process tags
                process_tags = [tag for tag in essential_tags if any(proc in tag.lower() for proc in ['laser cleaning', 'surface treatment', 'cleaning'])]
                if process_tags:
                    search_quality_score += 25
                
                # Check for application tags
                app_tags = [tag for tag in essential_tags if any(app in tag.lower() for app in ['industrial', 'precision', 'contaminant'])]
                if app_tags:
                    search_quality_score += 25
                
                alignment["search_optimization"] = search_quality_score
                
                if search_quality_score >= 75:
                    alignment["recommendations"].append("✅ Tags well-optimized for search navigation")
                else:
                    alignment["recommendations"].append("🔧 Improve tag coverage for better search functionality")
                    
                # Tag count optimization
                tag_count = len(essential_tags)
                if tag_count == 10:
                    alignment["recommendations"].append("✅ Optimal tag count (10) for clickable interface")
                elif tag_count < 8:
                    alignment["recommendations"].append("🔧 Consider adding more tags for better search coverage")
                elif tag_count > 12:
                    alignment["recommendations"].append("🔧 Consider reducing tags for cleaner clickable interface")
        
        return alignment
    
    def _analyze_metadata_alignment(self, metadata: Dict, component_type: str) -> Dict[str, Any]:
        """Analyze metadata components for SEO and social media optimization."""
        
        alignment = {
            "purpose_match": "seo_and_social_optimization" if component_type == "metatags" else "structured_data_seo",
            "current_structure": list(metadata.keys()) if isinstance(metadata, dict) else [],
            "seo_score": 0,
            "recommendations": []
        }
        
        if component_type == "metatags":
            # Analyze metatags for social media and SEO
            required_sections = ['htmlMeta', 'openGraph', 'twitterCard']
            present_sections = [section for section in required_sections if section in metadata]
            
            alignment["seo_score"] = (len(present_sections) / len(required_sections)) * 100
            
            if alignment["seo_score"] >= 100:
                alignment["recommendations"].append("✅ Complete metatags structure for SEO and social media")
            else:
                missing = [section for section in required_sections if section not in present_sections]
                alignment["recommendations"].append(f"🔧 Missing metatags sections: {', '.join(missing)}")
        
        elif component_type == "jsonld":
            # Analyze JSON-LD for structured data
            if 'structuredData' in metadata:
                structured_data = metadata['structuredData']
                if isinstance(structured_data, dict):
                    required_fields = ['@context', '@type', 'name', 'description']
                    present_fields = [field for field in required_fields if field in structured_data]
                    
                    alignment["seo_score"] = (len(present_fields) / len(required_fields)) * 100
                    
                    if alignment["seo_score"] >= 100:
                        alignment["recommendations"].append("✅ Complete JSON-LD structured data for SEO")
                    else:
                        missing = [field for field in required_fields if field not in present_fields]
                        alignment["recommendations"].append(f"🔧 Missing JSON-LD fields: {', '.join(missing)}")
        
        return alignment
    
    def _identify_nextjs_optimizations(self, data: Dict) -> list:
        """Identify specific optimizations for Next.js app usage."""
        
        optimizations = []
        
        # Component organization optimizations
        if 'componentOutputs' in data:
            components = data['componentOutputs']
            
            # Check for missing Table component
            table_needs = self._analyze_table_needs(data)
            if table_needs["overflow_detected"]:
                optimizations.append({
                    "type": "component_addition",
                    "component": "table",
                    "reason": "Detected overflow data suitable for Table component display",
                    "data_sources": list(table_needs["potential_table_data"].keys())
                })
            
            # Check component organization
            if len(components) > 3:
                optimizations.append({
                    "type": "component_organization",
                    "reason": "Multiple components could benefit from logical grouping",
                    "suggestion": "Group by UI purpose: content (caption, table) vs metadata (jsonld, metatags) vs navigation (tags)"
                })
        
        # Data structure optimizations
        if 'materialProperties' in data:
            props = data['materialProperties']
            if len(props) > 15:
                optimizations.append({
                    "type": "data_restructuring",
                    "reason": "Large property set may impact Next.js rendering performance",
                    "suggestion": "Consider lazy loading or pagination for properties"
                })
        
        return optimizations
    
    def _generate_nextjs_recommendations(self, data: Dict, analysis: Dict) -> list:
        """Generate specific recommendations for Next.js app optimization."""
        
        recommendations = []
        
        # Caption optimization for microscopic photos
        if 'caption' in analysis["component_alignment"]:
            caption_analysis = analysis["component_alignment"]["caption"]
            if caption_analysis["optimization_score"] < 75:
                recommendations.append({
                    "priority": "high",
                    "component": "caption",
                    "action": "Enhance caption content for microscopic photo descriptions",
                    "details": "Add before/after microscopic analysis terminology and technical observations"
                })
        
        # Table component recommendations
        if 'table' in analysis["component_alignment"]:
            table_analysis = analysis["component_alignment"]["table"]
            if table_analysis["overflow_detected"]:
                recommendations.append({
                    "priority": "medium",
                    "component": "table",
                    "action": "Implement Table component for overflow data",
                    "details": f"Move data from: {', '.join(table_analysis['potential_table_data'].keys())}"
                })
        
        # Tags optimization for search
        if 'tags' in analysis["component_alignment"]:
            tags_analysis = analysis["component_alignment"]["tags"]
            if tags_analysis["search_optimization"] < 75:
                recommendations.append({
                    "priority": "high",
                    "component": "tags",
                    "action": "Optimize tags for clickable search navigation",
                    "details": "Ensure coverage of material, category, process, and application tags"
                })
        
        # Performance recommendations
        total_size = len(str(data))
        if total_size > 15000:  # > 15KB
            recommendations.append({
                "priority": "medium",
                "component": "performance",
                "action": "Optimize frontmatter size for Next.js performance",
                "details": "Consider component lazy loading or data pagination"
            })
        
        return recommendations

def analyze_with_nextjs_context():
    """Analyze our optimized frontmatter with Next.js context."""
    
    print("🚀 NEXT.JS CONTEXT-AWARE FRONTMATTER ANALYSIS")
    print("=" * 60)
    
    optimizer = NextJSAwareFrontmatterOptimizer()
    
    # Analyze optimized file
    optimized_file = "aluminum-optimized.yaml"
    
    if Path(optimized_file).exists():
        with open(optimized_file, 'r') as f:
            data = yaml.safe_load(f)
        
        analysis = optimizer.analyze_current_organization(data)
        
        print(f"\\n📊 COMPONENT PURPOSE ALIGNMENT:")
        for component, purpose in optimizer.component_purposes.items():
            print(f"   • {component}: {purpose}")
        
        print(f"\\n🔍 CURRENT STRUCTURE ANALYSIS:")
        for comp_name, comp_analysis in analysis["component_alignment"].items():
            print(f"\\n📦 {comp_name.upper()} Component:")
            if "optimization_score" in comp_analysis:
                score = comp_analysis["optimization_score"]
                print(f"   📊 Optimization Score: {score:.1f}%")
            
            if "recommendations" in comp_analysis:
                for rec in comp_analysis["recommendations"]:
                    print(f"   {rec}")
        
        print(f"\\n💡 NEXT.JS OPTIMIZATION OPPORTUNITIES:")
        for i, opt in enumerate(analysis["optimization_opportunities"], 1):
            print(f"   {i}. {opt['type']}: {opt['reason']}")
            if 'suggestion' in opt:
                print(f"      💡 {opt['suggestion']}")
        
        print(f"\\n🎯 NEXT.JS RECOMMENDATIONS:")
        for i, rec in enumerate(analysis["nextjs_recommendations"], 1):
            priority_emoji = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
            print(f"   {i}. {priority_emoji} {rec['component'].upper()}: {rec['action']}")
            print(f"      📝 {rec['details']}")
        
        return analysis
    else:
        print(f"❌ File not found: {optimized_file}")
        return None

if __name__ == "__main__":
    analysis = analyze_with_nextjs_context()
    
    if analysis:
        print(f"\\n" + "=" * 60)
        print("✅ Next.js context analysis complete!")
        print("🎯 Use recommendations to optimize components for app usage patterns")
    else:
        print("❌ Analysis failed - check file availability")