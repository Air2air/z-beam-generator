#!/usr/bin/env python3
"""
Gemini Image Generation Client

Uses Gemini's native image generation capability instead of Imagen.
This provides an alternative when Imagen is rate-limited or unavailable.

Supported models (in order of preference):
- gemini-3-pro-image-preview (latest, best quality)
- gemini-2.5-flash-image (fast, good quality)
- gemini-2.0-flash-exp (legacy)

Key differences from Imagen:
- Uses generate_content with response_modalities=['IMAGE', 'TEXT']
- No negative_prompt support (use prompt instructions instead)
- No guidance_scale (model handles this internally)
- Generally faster and more available than Imagen

Author: AI Assistant
Date: December 1, 2025
"""

import os
import base64
from typing import Dict, Any, List, Optional
from pathlib import Path
from io import BytesIO
from PIL import Image


class GeminiFlashImageClient:
    """
    Client for Gemini image generation via Vertex AI.
    
    Generates images using Gemini's multimodal capabilities instead of Imagen.
    Better availability but different characteristics than Imagen.
    
    Supports:
    - gemini-3-pro-image-preview (default, latest)
    - gemini-2.5-flash-image
    - gemini-2.0-flash-exp (legacy)
    
    Example:
        client = GeminiFlashImageClient()
        image = client.generate_image(
            "Photorealistic image of a red apple",
        )
        image.save("output.png")
    """
    
    def __init__(
        self,
        model: str = "gemini-2.5-flash-image",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Gemini Flash client with Vertex AI.
        
        Args:
            model: Gemini model (default: gemini-2.0-flash-exp)
            config: Additional configuration
            
        Raises:
            RuntimeError: If SDK not installed
            ValueError: If credentials not configured
        """
        try:
            from google import genai
            from google.genai import types
            from google.oauth2 import service_account
        except ImportError:
            raise RuntimeError(
                "Google GenAI SDK not installed. "
                "Install with: pip install google-genai"
            )
        
        # Verify credentials
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            raise ValueError(
                "GOOGLE_APPLICATION_CREDENTIALS must be set."
            )
        
        if not os.path.exists(credentials_path):
            raise ValueError(f"Credentials file not found: {credentials_path}")
        
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "z-beam")
        location = "us-central1"
        
        # Load credentials from service account
        creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Initialize client
        self.client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
            credentials=creds
        )
        
        self.model_name = model
        self.config = config or {}
        self.project_id = project_id
        self._types = types
        
        print(f"✅ [GEMINI FLASH] Client initialized with model: {model}")
        print(f"📍 [GEMINI FLASH] Project: {project_id}, Location: {location}")
    
    def generate_image(
        self,
        prompt: str,
        output_path: Optional[Path] = None,
        aspect_ratio: str = "16:9",
        negative_prompt: Optional[str] = None,
        guidance_scale: Optional[float] = None,
        **kwargs
    ):
        """
        Generate image using Gemini 2.0 Flash.
        
        Args:
            prompt: Text description of the image
            output_path: Optional path to save image
            aspect_ratio: Desired aspect ratio (hint only, not enforced)
            negative_prompt: Ignored (use prompt instructions instead)
            guidance_scale: Ignored (Gemini handles internally)
            **kwargs: Additional config (ignored)
            
        Returns:
            PIL Image object
            
        Raises:
            RuntimeError: If generation fails
        """
        # Build enhanced prompt with aspect ratio hint
        enhanced_prompt = prompt
        if aspect_ratio == "16:9":
            enhanced_prompt = f"Generate a wide landscape-format image (16:9 aspect ratio). {prompt}"
        elif aspect_ratio == "9:16":
            enhanced_prompt = f"Generate a tall portrait-format image (9:16 aspect ratio). {prompt}"
        elif aspect_ratio == "1:1":
            enhanced_prompt = f"Generate a square image (1:1 aspect ratio). {prompt}"
        
        # Incorporate negative prompt into instructions (Gemini doesn't have negative_prompt)
        if negative_prompt:
            # Extract key terms from negative prompt
            avoid_terms = negative_prompt.split(',')[:10]  # First 10 terms
            avoid_str = ', '.join(t.strip() for t in avoid_terms)
            enhanced_prompt += f"\n\nIMPORTANT: Do NOT include any of these in the image: {avoid_str}"
        
        print("🎨 [GEMINI FLASH] Generating image...")
        print(f"📝 [GEMINI FLASH] Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        if negative_prompt:
            print(f"🚫 [GEMINI FLASH] Avoid: {negative_prompt[:60]}{'...' if len(negative_prompt) > 60 else ''}")
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=enhanced_prompt,
                config=self._types.GenerateContentConfig(
                    response_modalities=['IMAGE', 'TEXT']
                )
            )
            
            # Extract image from response
            image = None
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Decode image data
                        image_data = part.inline_data.data
                        if isinstance(image_data, str):
                            image_data = base64.b64decode(image_data)
                        image = Image.open(BytesIO(image_data))
                        break
            
            if image is None:
                raise RuntimeError("No image in response")
            
            # Crop to exact aspect ratio if needed
            image = self._crop_to_aspect_ratio(image, aspect_ratio)
            
            # Save if path provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                image.save(output_path)
                size_kb = output_path.stat().st_size / 1024
                print(f"✅ Image saved to: {output_path}")
                print(f"   • Size: {size_kb:.1f} KB")
            
            print("✅ [GEMINI FLASH] Image generated successfully")
            return image
            
        except Exception as e:
            print(f"❌ [GEMINI FLASH] Generation failed: {e}")
            raise RuntimeError(f"Image generation failed: {e}")
    
    def _crop_to_aspect_ratio(self, image: Image.Image, aspect_ratio: str) -> Image.Image:
        """
        Crop image to exact aspect ratio (center crop).
        
        Args:
            image: PIL Image
            aspect_ratio: Target ratio ("16:9", "9:16", "1:1")
            
        Returns:
            Cropped PIL Image
        """
        # Parse aspect ratio
        if aspect_ratio == "16:9":
            target_ratio = 16 / 9
        elif aspect_ratio == "9:16":
            target_ratio = 9 / 16
        elif aspect_ratio == "1:1":
            target_ratio = 1.0
        else:
            return image  # Unknown ratio, return as-is
        
        width, height = image.size
        current_ratio = width / height
        
        # Check if already correct (within 1% tolerance)
        if abs(current_ratio - target_ratio) / target_ratio < 0.01:
            return image
        
        if current_ratio > target_ratio:
            # Image is too wide, crop width
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            box = (left, 0, left + new_width, height)
        else:
            # Image is too tall, crop height
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            box = (0, top, width, top + new_height)
        
        cropped = image.crop(box)
        print(f"📐 [GEMINI FLASH] Cropped to {aspect_ratio}: {width}x{height} → {cropped.size[0]}x{cropped.size[1]}")
        return cropped
    
    def generate_multiple(
        self,
        prompt: str,
        count: int = 4,
        output_dir: Optional[Path] = None,
        **kwargs
    ) -> List:
        """
        Generate multiple images (sequential calls).
        
        Gemini Flash generates one image at a time, so this makes
        multiple calls for variations.
        
        Args:
            prompt: Text description
            count: Number of images (1-4)
            output_dir: Optional directory to save images
            **kwargs: Additional config
            
        Returns:
            List of PIL Image objects
        """
        print(f"🎨 [GEMINI FLASH] Generating {count} variations...")
        
        images = []
        for i in range(count):
            print(f"   Generating image {i+1}/{count}...")
            
            # Add variation hint
            variation_prompt = f"{prompt}\n\n(Variation {i+1} of {count} - create a unique interpretation)"
            
            image = self.generate_image(variation_prompt, **kwargs)
            images.append(image)
            
            # Save if directory provided
            if output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                image.save(output_dir / f"variation_{i+1}.png")
        
        print(f"✅ [GEMINI FLASH] Generated {len(images)} images")
        return images


# Factory function to get the right client
def get_image_client(use_flash: bool = False):
    """
    Get the appropriate image generation client.
    
    Args:
        use_flash: If True, use Gemini 2.0 Flash. If False, use Imagen.
        
    Returns:
        Image client instance
    """
    if use_flash:
        return GeminiFlashImageClient()
    else:
        from shared.api.gemini_image_client import GeminiImageClient
        return GeminiImageClient()
