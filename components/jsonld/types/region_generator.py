"""
JSON-LD generator for region articles.
"""

import logging
from typing import Dict, Any, List
from components.jsonld.types.base_type_generator import BaseTypeGenerator

logger = logging.getLogger(__name__)

class RegionJsonldGenerator(BaseTypeGenerator):
    """Generator for region-specific JSON-LD."""
    
    def generate_jsonld(self, frontmatter: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate JSON-LD for region articles.
        
        Args:
            frontmatter: Article frontmatter data (override instance frontmatter if provided)
            
        Returns:
            JSON-LD structure for region articles
        """
        # Use provided frontmatter or instance frontmatter
        frontmatter = frontmatter or self.frontmatter
        
        # Get common structure
        jsonld = self._get_common_jsonld_structure(frontmatter, "Article")
        
        # Add geographic specialization data
        region_data = self._generate_region_data(frontmatter)
        if region_data:
            jsonld.update(region_data)
        
        # Add about section with regional details
        about_items = self._generate_about_section(frontmatter, jsonld["name"])
        if about_items:
            jsonld["about"] = about_items
            
        # Add mentions section with regional insights
        mentions_items = self._generate_mentions_section(frontmatter)
        if mentions_items:
            jsonld["mentions"] = mentions_items
        
        # Get name from frontmatter and capitalize first letter
        name = self._get_frontmatter_value(frontmatter, "name", self.subject)
        name = name[0].upper() + name[1:] if name else ""
        
        return jsonld
        
    def _generate_region_data(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """Generate region-specific data.
        
        Args:
            frontmatter: Frontmatter data
            
        Returns:
            Dict with region data
        """
        region_data = {}
        
        # Add geographic coverage
        geo_coverage = self._get_frontmatter_value(frontmatter, "geographicCoverage", {})
        if geo_coverage and isinstance(geo_coverage, dict):
            region_name = geo_coverage.get("name", "")
            region_type = geo_coverage.get("type", "")
            
            if region_name and region_type:
                region_data["spatialCoverage"] = {
                    "@type": region_type,
                    "name": region_name
                }
                
                # Add geo coordinates if available
                latitude = geo_coverage.get("latitude")
                longitude = geo_coverage.get("longitude")
                if latitude and longitude:
                    region_data["spatialCoverage"]["geo"] = {
                        "@type": "GeoCoordinates",
                        "latitude": latitude,
                        "longitude": longitude
                    }
        
        return region_data
        
    def _generate_about_section(self, frontmatter: Dict[str, Any], name: str) -> List[Dict[str, Any]]:
        """Generate about section with regional details.
        
        Args:
            frontmatter: Frontmatter data
            name: Region name
            
        Returns:
            List of about items
        """
        about_items = []
        
        # Add main subject Thing with regional focus
        about_items.append({
            "@type": "Thing",
            "name": f"Laser Cleaning in {name}",
            "description": self._normalize_unicode(f"Specialized laser cleaning techniques and applications used in the {name} region, addressing local industrial needs and environmental regulations.")
        })
        
        # Add industries served in the region
        industries = self._get_frontmatter_value(frontmatter, "industries", [])
        if industries and isinstance(industries, list):
            industry_items = []
            for industry in industries:
                if isinstance(industry, dict):
                    industry_name = industry.get("name", "")
                    industry_description = industry.get("description", "")
                    
                    if industry_name:
                        industry_item = {
                            "@type": "Thing",
                            "name": industry_name
                        }
                        
                        if industry_description:
                            industry_item["description"] = self._normalize_unicode(industry_description)
                            
                        industry_items.append(industry_item)
            
            if industry_items:
                about_items.append({
                    "@type": "Thing",
                    "name": f"Industries Served in {name}",
                    "description": f"Key industries utilizing laser cleaning technology in the {name} region.",
                    "mentions": industry_items
                })
        
        # Add service providers in the region
        providers = self._get_frontmatter_value(frontmatter, "serviceProviders", [])
        if providers and isinstance(providers, list):
            provider_items = []
            for provider in providers:
                if isinstance(provider, dict):
                    provider_name = provider.get("name", "")
                    provider_url = provider.get("url", "")
                    provider_location = provider.get("location", "")
                    
                    if provider_name:
                        provider_item = {
                            "@type": "Organization",
                            "name": provider_name
                        }
                        
                        if provider_url:
                            provider_item["url"] = provider_url
                            
                        if provider_location:
                            provider_item["location"] = {
                                "@type": "Place",
                                "name": provider_location
                            }
                            
                        provider_items.append(provider_item)
            
            if provider_items:
                about_items.append({
                    "@type": "Thing",
                    "name": f"Laser Cleaning Providers in {name}",
                    "description": f"Companies and organizations offering laser cleaning services in the {name} region.",
                    "mentions": provider_items
                })
        
        return about_items
        
    def _generate_mentions_section(self, frontmatter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mentions section with regional insights.
        
        Args:
            frontmatter: Frontmatter data
            
        Returns:
            List of mention items
        """
        mentions = []
        
        # Add regulatory information
        regulations = self._get_frontmatter_value(frontmatter, "regulations", [])
        if regulations and isinstance(regulations, list):
            regulation_parts = []
            for regulation in regulations:
                if isinstance(regulation, dict):
                    code = regulation.get("code", "")
                    description = regulation.get("description", "")
                    
                    if code and description:
                        regulation_parts.append(f"{code}: {description}")
                    elif code:
                        regulation_parts.append(code)
            
            if regulation_parts:
                mentions.append({
                    "@type": "Thing",
                    "name": "Regional Regulations",
                    "description": self._normalize_unicode("; ".join(regulation_parts) + ".")
                })
        
        # Add regional challenges
        challenges = self._get_frontmatter_value(frontmatter, "challenges", [])
        if challenges and isinstance(challenges, list):
            challenge_parts = []
            for challenge in challenges:
                if isinstance(challenge, dict):
                    issue = challenge.get("issue", "")
                    solution = challenge.get("solution", "")
                    
                    if issue and solution:
                        challenge_parts.append(f"{issue} addressed by {solution}")
                    elif issue:
                        challenge_parts.append(issue)
            
            if challenge_parts:
                mentions.append({
                    "@type": "Thing",
                    "name": "Regional Challenges",
                    "description": self._normalize_unicode("; ".join(challenge_parts) + ".")
                })
        
        # Add case studies
        case_studies = self._get_frontmatter_value(frontmatter, "caseStudies", [])
        if case_studies and isinstance(case_studies, list):
            case_parts = []
            for case in case_studies:
                if isinstance(case, dict):
                    company = case.get("company", "")
                    project = case.get("project", "")
                    outcome = case.get("outcome", "")
                    
                    if company and project:
                        case_desc = f"{company}: {project}"
                        if outcome:
                            case_desc += f" resulting in {outcome}"
                        case_parts.append(case_desc)
            
            if case_parts:
                mentions.append({
                    "@type": "Thing",
                    "name": "Regional Case Studies",
                    "description": self._normalize_unicode("; ".join(case_parts) + ".")
                })
        
        return mentions