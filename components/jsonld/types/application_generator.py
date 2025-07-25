"""
JSON-LD generator for application articles.
"""

import logging
from typing import Dict, Any, List
from components.jsonld.types.base_type_generator import BaseTypeGenerator

logger = logging.getLogger(__name__)

class ApplicationJsonldGenerator(BaseTypeGenerator):
    """Generator for application-specific JSON-LD."""
    
    def generate_jsonld(self, frontmatter: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate JSON-LD for application articles.
        
        Args:
            frontmatter: Article frontmatter data (override instance frontmatter if provided)
            
        Returns:
            JSON-LD structure for application articles
        """
        # Use provided frontmatter or instance frontmatter
        frontmatter = frontmatter or self.frontmatter
        
        # Get common structure
        jsonld = self._get_common_jsonld_structure(frontmatter, "TechnicalArticle")
        
        # Add application-specific fields
        jsonld["applicationCategory"] = "Engineering"
        jsonld["proficiencyLevel"] = "Expert"
        
        # Add about section with enhanced application details
        about_items = self._generate_about_section(frontmatter, 
                                                 jsonld["headline"], 
                                                 jsonld["description"])
        if about_items:
            jsonld["about"] = about_items
        
        # Add mentions section with enhanced technical details
        mentions_items = self._generate_mentions_section(frontmatter)
        if mentions_items:
            jsonld["mentions"] = mentions_items
        
        return jsonld
    
    def _generate_about_section(self, frontmatter: Dict[str, Any], name: str, description: str) -> List[Dict[str, Any]]:
        """Generate enhanced about section with application details.
        
        Args:
            frontmatter: Frontmatter data
            name: Article name
            description: Article description
            
        Returns:
            List of about items
        """
        about_items = []
        
        # Add main subject Thing with enhanced name and description
        about_items.append({
            "@type": "Thing",
            "name": f"{name} in Laser Cleaning",
            "description": f"Techniques for {name.lower()}, using methods like LIBS and dual-wavelength analysis."
        })
        
        # Add Service with applications and enhanced metadata
        applications = self._get_frontmatter_value(frontmatter, "applications", [])
        outcomes = self._get_frontmatter_value(frontmatter, "outcomes", [])
        
        # Get outcome metric for description enhancement
        outcome_metric = ""
        if outcomes and isinstance(outcomes, list) and len(outcomes) > 0:
            if isinstance(outcomes[0], dict):
                metric = outcomes[0].get("metric", "")
                result = outcomes[0].get("result", "")
                if metric and result:
                    outcome_metric = f"{result} {metric}"
        
        # Build the service object
        service = {
            "@type": "Service",
            "serviceType": f"{name} with Laser Cleaning",
            "provider": {
                "@type": "Organization",
                "name": "Z-Beam"
            },
            "description": f"Precision laser cleaning with integrated {name} for aerospace, automotive, and heritage applications" + 
                          (f", achieving {outcome_metric}" if outcome_metric else "."),
            "areaServed": {
                "@type": "Place",
                "name": "Global"
            }
        }
            
        # Add applications as offer catalog
        if applications and len(applications) > 0:
            offers = []
            for app in applications:
                if isinstance(app, dict):
                    app_name = app.get("name", "")
                    app_description = app.get("description", "")
                    if app_name:
                        offers.append({
                            "@type": "Offer",
                            "itemOffered": {
                                "@type": "Service",
                                "name": app_name,
                                "description": app_description
                            }
                        })
            
            if offers:
                service["hasOfferCatalog"] = {
                    "@type": "OfferCatalog",
                    "name": "Laser Cleaning Applications",
                    "itemListElement": offers
                }
        
        about_items.append(service)
        
        return about_items
    
    def _generate_mentions_section(self, frontmatter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate enhanced mentions section with technical details.
        
        Args:
            frontmatter: Frontmatter data
            
        Returns:
            List of mention items
        """
        mentions = []
        
        # Add technical specifications as structured value
        tech_specs = self._get_frontmatter_value(frontmatter, "technicalSpecifications", {})
        if tech_specs and isinstance(tech_specs, dict) and len(tech_specs) > 0:
            # Use the base class method to create structured value
            structured_specs = self._generate_structured_value(tech_specs)
            
            # Add the structured specs to mentions
            mentions.append({
                "@type": "Thing",
                "name": "Technical Specifications",
                "description": structured_specs
            })
        
        # Add regulatory standards
        standards = self._get_frontmatter_value(frontmatter, "regulatoryStandards", [])
        if standards:
            standards_description = "Compliance with "
            if isinstance(standards, list):
                standard_parts = []
                for standard in standards:
                    if isinstance(standard, dict):
                        code = standard.get("code", "")
                        description = standard.get("description", "")
                        if code and description:
                            standard_parts.append(f"{code} ({description})")
                        elif code:
                            standard_parts.append(code)
                    elif isinstance(standard, str):
                        standard_parts.append(standard)
                
                if standard_parts:
                    standards_description += ", ".join(standard_parts) + "."
                    
                    mentions.append({
                        "@type": "Thing",
                        "name": "Regulatory Standards",
                        "description": standards_description
                    })
        
        # Add challenges with enhanced description
        challenges = self._get_frontmatter_value(frontmatter, "challenges", [])
        tech_specs = self._get_frontmatter_value(frontmatter, "technicalSpecifications", {})
        
        if challenges:
            # Generate a more detailed challenge description that incorporates technical specs
            safety_class = self._get_nested_value(tech_specs, "safetyClass", "")
            compliance = self._get_nested_value(tech_specs, "compliance", "")
            
            challenge_parts = []
            for challenge in challenges:
                if isinstance(challenge, dict):
                    issue = challenge.get("issue", "")
                    solution = challenge.get("solution", "")
                    if issue and solution:
                        challenge_parts.append(f"{issue} addressed through {solution}")
                    elif issue:
                        challenge_parts.append(issue)
            
            if challenge_parts or safety_class:
                challenge_description = ""
                if challenge_parts:
                    challenge_description += "; ".join(challenge_parts)
                if safety_class:
                    if challenge_description:
                        challenge_description += f"; operator safety ensured via {safety_class} laser enclosures"
                        if compliance:
                            challenge_description += f" compliant with {compliance}"
                
                mentions.append({
                    "@type": "Thing",
                    "name": "Challenges",
                    "description": challenge_description
                })
        
        # Add outcomes with enhanced formatting
        outcomes = self._get_frontmatter_value(frontmatter, "outcomes", [])
        if outcomes:
            outcome_parts = []
            if isinstance(outcomes, list):
                for outcome in outcomes:
                    if isinstance(outcome, dict):
                        metric = outcome.get("metric", "")
                        result = outcome.get("result", "")
                        if metric and result:
                            outcome_parts.append(f"{result} {metric}")
                    elif isinstance(outcome, str):
                        outcome_parts.append(outcome)
            
            if outcome_parts:
                outcome_description = "; ".join(outcome_parts) + "."
                
                mentions.append({
                    "@type": "Thing",
                    "name": "Outcomes",
                    "description": outcome_description
                })
        
        return mentions