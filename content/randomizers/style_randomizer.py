import random
from typing import Dict, List, Any, Tuple

class StyleRandomizer:
    """Randomizes writing style, tone, phrasing, and section lengths in content generation."""
    
    # Style variations for different tones
    _writing_styles = [
        "technical and precise",
        "clear and educational",
        "authoritative and industry-focused",
        "practical and application-oriented",
        "analytical and detailed",
        "concise and direct",
        "comprehensive and thorough",
        "academic and research-oriented",
        "instructional with practical emphasis",
        "expert consultant perspective"
    ]
    
    # Phrase variations for different sections
    _section_phrases = {
        "overview": [
            "Write a comprehensive overview about {subject} based on this description",
            "Create an introductory overview of {subject} using this information",
            "Provide a thorough introduction to {subject} covering these points",
            "Develop an overview section for {subject} that incorporates this context",
            "Construct a detailed summary about {subject} from these details"
        ],
        "applications": [
            "Detail the applications of {subject} based on these items",
            "Describe how {subject} is applied in these contexts",
            "Explain the various uses of {subject} in these areas",
            "Outline the practical applications of {subject} from this information",
            "Document the key implementation areas for {subject}"
        ],
        "technicalSpecifications": [
            "Explain these technical specifications for {subject}",
            "Detail the technical characteristics of {subject} shown here",
            "Describe the following specifications for {subject}",
            "Elaborate on these technical properties of {subject}",
            "Present these engineering parameters for {subject}"
        ]
    }
    
    # Random conclusion phrases by section
    _conclusion_phrases = {
        "overview": [
            "Expand on the key points, focusing on the importance and general context.",
            "Highlight the significance and context while expanding on these details.",
            "Emphasize why this matters in the broader industry context.",
            "Explain the relevance and importance of these characteristics."
        ],
        "applications": [
            "For each application, explain its significance and specific benefits.",
            "Describe why each application is important and what advantages it offers.",
            "Highlight the unique value proposition for each application area.",
            "Explain what makes each application effective and valuable."
        ]
    }
    
    # Section length multipliers - these control how much longer or shorter sections can be
    _length_profiles = [
        # [min_multiplier, max_multiplier, probability]
        [0.3, 0.5, 0.15],    # Very short section (30-50% of target length) - 15% chance
        [0.5, 0.8, 0.20],    # Short section (50-80% of target length) - 20% chance
        [0.8, 1.2, 0.30],    # Normal section (80-120% of target length) - 30% chance
        [1.2, 1.8, 0.25],    # Long section (120-180% of target length) - 25% chance
        [1.8, 2.5, 0.10]     # Very long section (180-250% of target length) - 10% chance
    ]
    
    @classmethod
    def get_style(cls) -> str:
        """Get a random writing style instruction."""
        return random.choice(cls._writing_styles)
    
    @classmethod
    def get_intro_phrase(cls, section_id: str, subject: str) -> str:
        """Get a randomized introductory phrase for a section."""
        # Get phrases for this section or use generic ones
        phrases = cls._section_phrases.get(section_id, [
            "Write about {subject} based on this information",
            "Create content about {subject} using these details",
            "Develop information about {subject} with this data",
            "Generate a section about {subject} from these points"
        ])
        
        # Format with subject
        return random.choice(phrases).format(subject=subject)
    
    @classmethod
    def get_conclusion_phrase(cls, section_id: str) -> str:
        """Get a randomized conclusion phrase for a section."""
        # Get phrases for this section or use generic ones
        phrases = cls._conclusion_phrases.get(section_id, [
            "Provide comprehensive details and explain their significance.",
            "Highlight the most important aspects while providing context.",
            "Focus on the key implications and practical relevance.",
            "Address the most significant points with supporting details."
        ])
        
        return random.choice(phrases)
    
    @classmethod
    def randomize_word_count(cls, base_count: int) -> int:
        """
        Randomize word count using section length profiles for highly variable content length.
        
        Args:
            base_count: The target word count before randomization
            
        Returns:
            Randomized word count that could be significantly shorter or longer
        """
        # Choose a length profile based on probability distribution
        r = random.random()
        cumulative_prob = 0
        chosen_profile = cls._length_profiles[-1]  # Default to last profile
        
        for profile in cls._length_profiles:
            cumulative_prob += profile[2]  # Add this profile's probability
            if r <= cumulative_prob:
                chosen_profile = profile
                break
        
        # Get min and max multipliers from the chosen profile
        min_multiplier, max_multiplier, _ = chosen_profile
        
        # Apply a random multiplier within the selected range
        multiplier = random.uniform(min_multiplier, max_multiplier)
        return max(50, int(base_count * multiplier))  # Ensure at least 50 words
    
    @classmethod
    def get_section_length_description(cls, words: int) -> str:
        """Get a description of the section length for the prompt."""
        if words < 100:
            return f"Write a very brief section of approximately {words} words."
        elif words < 150:
            return f"Keep this section concise at around {words} words."
        elif words < 250:
            return f"Write approximately {words} words for this section."
        elif words < 400:
            return f"Create a detailed section of about {words} words."
        else:
            return f"Write a comprehensive, in-depth section of approximately {words} words."
    
    @classmethod
    def randomize_content_data(cls, data_items: List[str]) -> List[str]:
        """Randomize the order of data items in lists."""
        if random.random() < 0.7:  # 70% chance to shuffle (increased from 30%)
            shuffled = data_items.copy()
            random.shuffle(shuffled)
            return shuffled
        return data_items
    
    @classmethod
    def should_emphasize_section(cls) -> bool:
        """Randomly determine if a section should be emphasized."""
        return random.random() < 0.4  # 40% chance for emphasis
    
    @classmethod
    def get_emphasis_instruction(cls) -> str:
        """Get a random emphasis instruction for the AI."""
        emphasis_types = [
            "Make this section particularly detailed and technical.",
            "This section should be the most comprehensive in the article.",
            "Focus on providing specific examples and detailed explanations in this section.",
            "Make this section more in-depth than the others, with detailed technical specifics.",
            "This section should be especially thorough, with extensive supporting details."
        ]
        return random.choice(emphasis_types)