#!/usr/bin/env python3
"""
Gemini Image Generation Client

Wrapper for Google's Imagen API via Vertex AI to generate images from text prompts.
Uses Vertex AI SDK with service account authentication for billed access.

Author: AI Assistant
Date: October 30, 2025
"""

import base64
import os
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional


class GeminiImageClient:
    """
    Client for Gemini Imagen API via Vertex AI.
    
    Generates photorealistic images from text prompts using Google's
    Imagen 3 model. Supports various aspect ratios and quality settings.
    Requires GOOGLE_APPLICATION_CREDENTIALS environment variable.
    
    Example:
        client = GeminiImageClient()
        image = client.generate_image(
            "Historical photo of San Francisco 1920s",
            aspect_ratio="4:3"
        )
        image.save("output.png")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "imagen-4.0-generate-001",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Gemini image client with Vertex AI.
        
        Args:
            api_key: Unused (kept for compatibility)
            model: Imagen model version (default: imagen-4.0-generate-001 for Imagen 4)
            config: Additional configuration (aspect_ratio, etc.)
            
        Raises:
            RuntimeError: If Vertex AI SDK not installed
            ValueError: If credentials not configured
        """
        # Check for required SDK
        try:
            import vertexai
            from google.cloud import aiplatform
            from vertexai.preview.vision_models import ImageGenerationModel
        except ImportError:
            raise RuntimeError(
                "Vertex AI SDK not installed. "
                "Install with: pip install google-cloud-aiplatform"
            )
        
        # Verify credentials and project
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            raise ValueError(
                "GOOGLE_APPLICATION_CREDENTIALS must be set. "
                "Download service account JSON from: "
                "https://console.cloud.google.com/iam-admin/serviceaccounts"
            )
        
        if not os.path.exists(credentials_path):
            raise ValueError(f"Credentials file not found: {credentials_path}")
        
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "z-beam")
        location = "us-central1"
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        self.model_name = model
        self.model = ImageGenerationModel.from_pretrained(model)
        self.config = config or {}
        self.project_id = project_id
        
        print(f"✅ [GEMINI] Client initialized with Vertex AI model: {model}")
        print(f"📍 [GEMINI] Project: {project_id}, Location: {location}")
    
    def generate_image(
        self,
        prompt: str,
        output_path: Optional[Path] = None,
        aspect_ratio: str = "16:9",
        image_size: str = "1K",
        person_generation: str = "allow_adult",
        negative_prompt: Optional[str] = None,
        guidance_scale: Optional[float] = None,
        safety_filter_level: str = "block_some",
        add_watermark: bool = False,
        seed: Optional[int] = None,
        **kwargs
    ):
        """
        Generate single image from text prompt using Vertex AI.
        
        Args:
            prompt: Text description
            output_path: Optional path to save image
            aspect_ratio: Image ratio (1:1, 3:4, 4:3, 9:16, 16:9)
            image_size: Unused (kept for compatibility)
            person_generation: Allow people (dont_allow, allow_adult, allow_all)
            negative_prompt: What NOT to generate (text, distortions, artifacts)
            guidance_scale: How closely to follow prompt (1.0-20.0, default ~7.5)
            safety_filter_level: block_most, block_some, block_few, block_fewest
            add_watermark: Add Google watermark (default False)
            seed: Random seed for reproducibility
            **kwargs: Additional generation config overrides
            
        Returns:
            PIL Image object
            
        Raises:
            ValueError: If prompt too long or invalid config
            RuntimeError: If generation fails
        """
        # Validate prompt length (optimization already done by prompt_builder)
        IMAGEN_LIMIT = 4096
        
        if len(prompt) > IMAGEN_LIMIT:
            # Emergency truncation - should rarely happen since prompt_builder optimizes
            print(f"🚨 [GEMINI] Prompt over limit: {len(prompt)}/{IMAGEN_LIMIT} chars - truncating")
            prompt = prompt[:IMAGEN_LIMIT - 50] + "\n[Truncated for API limit]"
        elif len(prompt) > 3500:
            print(f"⚠️  [GEMINI] Prompt near limit: {len(prompt)}/{IMAGEN_LIMIT} chars")
        
        print("🎨 [GEMINI] Generating image...")
        print(f"📝 [GEMINI] Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        if negative_prompt:
            print(f"🚫 [GEMINI] Negative: {negative_prompt[:60]}{'...' if len(negative_prompt) > 60 else ''}")
        print(f"⚙️  [GEMINI] Config: aspect_ratio={aspect_ratio}, guidance={guidance_scale}, safety={safety_filter_level}")
        
        try:
            # Build generation parameters
            gen_params = {
                "prompt": prompt,
                "number_of_images": 1,
                "aspect_ratio": aspect_ratio,
                "person_generation": person_generation,
                "add_watermark": add_watermark,
                "safety_filter_level": safety_filter_level,
            }
            
            # Add optional parameters
            if negative_prompt:
                gen_params["negative_prompt"] = negative_prompt
            if guidance_scale is not None:
                gen_params["guidance_scale"] = guidance_scale
            if seed is not None:
                gen_params["seed"] = seed
            
            # Merge with kwargs
            gen_params.update(kwargs)
            
            # Generate image using Vertex AI
            response = self.model.generate_images(**gen_params)
            
            # Get first generated image
            if not response.images:
                raise RuntimeError("No images generated in response")
            
            image = response.images[0]._pil_image
            
            # Save if path provided
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                image.save(output_path)
                print(f"💾 [GEMINI] Saved to: {output_path}")
            
            print("✅ [GEMINI] Image generated successfully")
            return image
            
        except Exception as e:
            print(f"❌ [GEMINI] Generation failed: {e}")
            raise RuntimeError(f"Image generation failed: {e}")
    
    def generate_multiple(
        self,
        prompt: str,
        count: int = 4,
        output_dir: Optional[Path] = None,
        aspect_ratio: str = "16:9",
        **kwargs
    ) -> List:
        """
        Generate multiple image variations from prompt using Vertex AI.
        
        Args:
            prompt: Text description
            count: Number of images (1-4)
            output_dir: Optional directory to save images
            aspect_ratio: Image ratio
            **kwargs: Additional config overrides
            
        Returns:
            List of PIL Image objects
            
        Raises:
            ValueError: If count > 4
            RuntimeError: If generation fails
        """
        if count > 4:
            raise ValueError("Maximum 4 images per request")
        
        print(f"🎨 [GEMINI] Generating {count} variations...")
        print(f"📝 [GEMINI] Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        
        try:
            response = self.model.generate_images(
                prompt=prompt,
                number_of_images=count,
                aspect_ratio=aspect_ratio,
                **kwargs
            )
            
            images = []
            for idx, gen_image in enumerate(response.images):
                image = gen_image._pil_image
                images.append(image)
                
                if output_dir:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_path = output_dir / f"image_{idx+1}.png"
                    image.save(output_path)
                    print(f"💾 [GEMINI] Saved variation {idx+1}: {output_path}")
            
            print(f"✅ [GEMINI] Generated {len(images)} images")
            return images
            
        except Exception as e:
            print(f"❌ [GEMINI] Generation failed: {e}")
            raise RuntimeError(f"Multiple image generation failed: {e}")
    
    def test_connection(self) -> bool:
        """
        Test Vertex AI connection with minimal request.
        
        Returns:
            True if connection successful
        """
        try:
            print("🔍 [GEMINI] Testing Vertex AI connection...")
            test_prompt = "A simple red circle on white background"
            
            response = self.model.generate_images(
                prompt=test_prompt,
                number_of_images=1,
                aspect_ratio="1:1"
            )
            
            if response.images:
                print("✅ [GEMINI] Connection test successful")
                return True
            else:
                print("❌ [GEMINI] Connection test failed: No images returned")
                return False
                
        except Exception as e:
            print(f"❌ [GEMINI] Connection test failed: {e}")
            return False
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """
        Validate generation configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If invalid config
        """
        valid_aspect_ratios = ["1:1", "3:4", "4:3", "9:16", "16:9"]
        valid_image_sizes = ["1K", "2K"]
        valid_person_gen = ["dont_allow", "allow_adult", "allow_all"]
        
        if "aspect_ratio" in config:
            if config["aspect_ratio"] not in valid_aspect_ratios:
                raise ValueError(
                    f"Invalid aspect_ratio: {config['aspect_ratio']}. "
                    f"Must be one of: {valid_aspect_ratios}"
                )
        
        if "image_size" in config:
            if config["image_size"] not in valid_image_sizes:
                raise ValueError(
                    f"Invalid image_size: {config['image_size']}. "
                    f"Must be one of: {valid_image_sizes}"
                )
        
        if "person_generation" in config:
            if config["person_generation"] not in valid_person_gen:
                raise ValueError(
                    f"Invalid person_generation: {config['person_generation']}. "
                    f"Must be one of: {valid_person_gen}"
                )
        
        if "number_of_images" in config:
            num = config["number_of_images"]
            if not isinstance(num, int) or num < 1 or num > 4:
                raise ValueError(
                    f"Invalid number_of_images: {num}. Must be 1-4"
                )
        
        return True


def create_gemini_client(
    api_key: Optional[str] = None,
    **kwargs
) -> GeminiImageClient:
    """
    Factory function to create Gemini image client.
    
    Args:
        api_key: Optional API key override
        **kwargs: Additional client config
        
    Returns:
        GeminiImageClient instance
    """
    return GeminiImageClient(api_key=api_key, **kwargs)
