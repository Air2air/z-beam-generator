"""
Enhanced API client with proper interface implementation.
"""

import requests
from typing import Dict, Any, Optional
from core.interfaces.services import IAPIClient
from core.exceptions import APIError
from modules.logger import get_logger

logger = get_logger("api_client")


class APIClient(IAPIClient):
    """Enhanced API client implementing the IAPIClient interface."""

    def __init__(
        self, provider: str, api_key: str, base_config: Optional[Dict[str, Any]] = None
    ):
        self._provider = provider.upper()
        self._api_key = api_key
        # Note: base_config parameter retained for backwards compatibility but unused
        # All configuration now comes from the provider models configuration
        self._setup_provider_config()

    def _setup_provider_config(self) -> None:
        """Setup provider-specific configuration."""
        # Handle test provider first
        if self._provider == "TEST":
            self._provider_config = {
                "model": "test-model",
                "url_template": "http://localhost:8000/test",  # FALLBACK
            }
            return
        
        # For real providers, get config from run.py
        import sys
        import os

        # Add the project root to sys.path to ensure proper import
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        sys.path.insert(0, project_root)

        try:
            from run import PROVIDER_MODELS
            
            if self._provider not in PROVIDER_MODELS:
                # Fallback to global config
                from config.global_config import GlobalConfigManager
                config_manager = GlobalConfigManager.get_instance()
                provider_models = config_manager.get_available_providers()
                
                if self._provider in provider_models:
                    self._provider_config = provider_models[self._provider]
                else:
                    raise APIError(f"Unsupported provider: {self._provider}", self._provider)
            else:
                self._provider_config = PROVIDER_MODELS[self._provider]
                
        except ImportError:
            # Fallback to global config
            from config.global_config import GlobalConfigManager
            config_manager = GlobalConfigManager.get_instance()
            provider_models = config_manager.get_available_providers()
            
            if self._provider in provider_models:
                self._provider_config = provider_models[self._provider]
            else:
                raise APIError(f"Unsupported provider: {self._provider}", self._provider)

    def call_api(
        self,
        prompt: str,
        model: str,
        temperature: float = None,
        max_tokens: int = None,
        timeout: int = None,
        **kwargs,
    ) -> str:
        """Make an API call to the AI provider."""
        if not prompt or not prompt.strip():
            raise APIError("Prompt cannot be empty", self._provider)
            
        # Handle TEST provider for integration testing
        if self._provider == "TEST":
            logger.info("Using TEST provider - returning mock response")
            return self._generate_test_response(prompt)

        # Ensure model is not null - use provider config model if needed
        if not model or model == "unknown-model":
            model = self._provider_config.get("model")
            if not model:
                raise APIError(f"No model configured for provider: {self._provider}", self._provider)

        # Set defaults from config if not provided - NO HARDCODING!
        if temperature is None:
            from config.global_config import get_config
            temperature = get_config().get_content_temperature()
        if timeout is None:
            from config.global_config import get_config
            timeout = get_config().get_api_timeout()
        if max_tokens is None:
            from config.global_config import get_config
            max_tokens = get_config().get_max_api_tokens()

        # Minimal API logging
        try:
            response = self._make_request(
                prompt, model, temperature, max_tokens, timeout, **kwargs
            )

            return response

        except requests.exceptions.RequestException as e:
            raise APIError(
                f"Network error calling {self._provider}: {str(e)}",
                self._provider,
                getattr(e.response, "status_code", None)
                if hasattr(e, "response")
                else None,
            ) from e
        except Exception as e:
            raise APIError(
                f"Unexpected error calling {self._provider}: {str(e)}", self._provider
            ) from e

    def _make_request(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: int,
        **kwargs,
    ) -> str:
        """Make the actual HTTP request based on provider."""
        if self._provider == "GEMINI":
            return self._call_gemini(
                prompt, model, temperature, max_tokens, timeout, **kwargs
            )
        elif self._provider == "XAI":
            return self._call_xai(
                prompt, model, temperature, max_tokens, timeout, **kwargs
            )
        elif self._provider == "DEEPSEEK":
            return self._call_deepseek(
                prompt, model, temperature, max_tokens, timeout, **kwargs
            )
        else:
            raise APIError(f"Provider {self._provider} not implemented", self._provider)

    def _call_gemini(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: int,
        **kwargs,
    ) -> str:
        """Call Google Gemini API."""
        url = self._provider_config["url_template"]

        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        # Add API key as query parameter
        params = {"key": self._api_key}

        response = requests.post(
            url, headers=headers, json=payload, params=params, timeout=timeout
        )

        if response.status_code != 200:
            raise APIError(
                f"Gemini API error: {response.text}",
                self._provider,
                response.status_code,
                response.text,
            )

        try:
            data = response.json()
            candidate = data["candidates"][0]

            # Check if the response was truncated or had issues
            finish_reason = candidate.get("finishReason", "")
            logger.debug(f"Gemini response finishReason: {finish_reason}")

            # Handle different content structures
            content = candidate.get("content", {})

            # Try to get text from parts array (normal case)
            if "parts" in content and content["parts"] and len(content["parts"]) > 0:
                text_content = content["parts"][0].get("text", "")
                if text_content.strip():  # Make sure we have actual content
                    return text_content
                else:
                    logger.warning(
                        f"Gemini returned empty text content, finishReason: {finish_reason}"
                    )

            # Handle various problematic finish reasons
            if finish_reason in ["MAX_TOKEN", "LENGTH"]:
                logger.error(f"Gemini response truncated: {finish_reason}")
                raise APIError(
                    f"Gemini response was truncated ({finish_reason}). Consider reducing prompt size or increasing max_tokens.",
                    self._provider,
                    response.status_code,
                    f"TRUNCATED_{finish_reason}",
                )
            elif finish_reason == "SAFETY":
                logger.error("Gemini response blocked by safety filters")
                raise APIError(
                    "Gemini response was blocked by safety filters. Consider modifying the prompt.",
                    self._provider,
                    response.status_code,
                    "SAFETY_FILTER_BLOCKED",
                )
            elif finish_reason == "RECITATION":
                logger.error("Gemini response blocked due to recitation")
                raise APIError(
                    "Gemini response was blocked due to recitation concerns. Consider modifying the prompt.",
                    self._provider,
                    response.status_code,
                    "RECITATION_BLOCKED",
                )

            # If we get here, we have an unexpected response structure
            logger.error(
                f"Unexpected Gemini response structure: finishReason={finish_reason}, content={content}"
            )
            raise APIError(
                f"Unexpected Gemini response format: missing content parts (finishReason: {finish_reason})",
                self._provider,
                response.status_code,
                response.text,
            )

        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse Gemini response: {response.text}")
            raise APIError(
                f"Failed to parse Gemini response: {str(e)}",
                self._provider,
                response.status_code,
                response.text,
            ) from e

    def _call_xai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: int,
        **kwargs,
    ) -> str:
        """Call xAI Grok API."""
        # NO HARDCODING: Get URL from provider configuration
        url = self._provider_config["url_template"]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }

        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(url, headers=headers, json=payload, timeout=timeout)

        if response.status_code != 200:
            raise APIError(
                f"xAI API error: {response.text}",
                self._provider,
                response.status_code,
                response.text,
            )

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise APIError(
                f"Unexpected xAI response format: {response.text}",
                self._provider,
                response.status_code,
                response.text,
            ) from e

    def _call_deepseek(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: int,
        **kwargs,
    ) -> str:
        """Call DeepSeek API."""
        # Validate model is not null/empty
        if not model or model.strip() == "":
            raise APIError("Model cannot be null or empty for DeepSeek API", self._provider)
        
        # NO HARDCODING: Get URL from provider configuration
        url = self._provider_config["url_template"]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }

        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(
            url, headers=headers, json=payload, timeout=timeout
        )

        if response.status_code != 200:
            raise APIError(
                f"DeepSeek API error: {response.text}",
                self._provider,
                response.status_code,
                response.text,
            )

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise APIError(
                f"Unexpected DeepSeek response format: {response.text}",
                self._provider,
                response.status_code,
                response.text,
            ) from e

    def get_provider_name(self) -> str:
        """Get the name of the AI provider."""
        return self._provider

    def call_ai_api(
        self,
        prompt: str,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        timeout: int = None,
    ) -> str:
        """Legacy method name for backward compatibility."""
        # Set defaults from config if not provided - NO HARDCODING!
        if temperature is None:
            from config.global_config import get_config
            temperature = get_config().get_content_temperature()
        if timeout is None:
            from config.global_config import get_config
            timeout = get_config().get_api_timeout()
        if max_tokens is None:
            from config.global_config import get_config
            max_tokens = get_config().get_max_api_tokens()
        return self.call_api(prompt, model, temperature, max_tokens, timeout)

    def _generate_test_response(self, prompt: str) -> str:
        """Generate a test response for the TEST provider."""
        material = "unknown material"
        if "material:" in prompt.lower():
            # Extract material from prompt
            for line in prompt.split("\n"):
                if "material:" in line.lower():
                    material = line.split(":", 1)[1].strip()
                    break
        
        # Generate material-specific detailed response
        if material.lower() == "bronze":
            return self._generate_bronze_response()
        elif material.lower() == "aluminum" or material.lower() == "aluminium":
            return self._generate_aluminum_response()
        elif material.lower() == "steel":
            return self._generate_steel_response()
        elif material.lower() == "copper":
            return self._generate_copper_response()
        elif material.lower() == "titanium":
            return self._generate_titanium_response()
        else:
            # Generate a generic response for other materials
            response = f"""# {material.title()}: An Essential Material in Modern Industry

## Introduction
{material.title()} has emerged as one of the most versatile and essential materials in modern manufacturing and engineering. With its unique combination of physical and chemical properties, {material.lower()} continues to find new applications across diverse industries from aerospace to medicine, construction to electronics. This article explores the remarkable characteristics that make {material.lower()} indispensable, its historical development, and the cutting-edge applications that are shaping its future.

The story of {material.lower()} represents humanity's ongoing quest to develop materials that can meet increasingly sophisticated technological demands. As we face growing challenges in sustainability, efficiency, and performance, {material.lower()} stands as a testament to human ingenuity and our ability to harness natural resources for remarkable ends. Through scientific advancement and engineering innovation, we continue to discover new potential in this extraordinary material.
"""
        return response

    def _generate_bronze_response(self) -> str:
        """Generate a detailed response about Bronze material."""
        return """# Bronze: The Alloy That Shaped Civilization

## Introduction to Bronze

Bronze, an alloy primarily composed of copper with the addition of tin (typically 12-12.5%), stands as one of humanity's most transformative technological innovations. The discovery of bronze around 3500 BCE marked such a pivotal moment in human development that historians named an entire era—the Bronze Age—after this versatile metal. Bronze's creation represented one of our earliest successful attempts to engineer materials with superior properties than those found in nature.

What made bronze revolutionary was its impressive combination of properties: harder than copper yet less brittle than tin, with excellent castability and resistance to corrosion. This remarkable balance of characteristics enabled early civilizations to create more effective tools, weapons, and artistic works than previously possible with stone or pure copper. From the magnificent bronze sculptures of ancient Greece to the sophisticated astronomical instruments of ancient China, bronze artifacts offer a window into humanity's technological and artistic evolution.

Today, despite the prevalence of steel, aluminum, and modern composites, bronze continues to find specialized applications that leverage its unique properties. Its exceptional corrosion resistance makes it ideal for marine environments, while its low friction coefficient ensures its continued use in bearings and bushings. The warm golden-brown patina that develops on bronze surfaces has also maintained its appeal in architectural elements and fine art, connecting our modern world to a legacy spanning more than five millennia of human creativity and innovation.
"""

    def _generate_aluminum_response(self) -> str:
        """Generate a detailed response about Aluminum material."""
        return """# Aluminum: The Metal of Modernity

## Introduction to Aluminum

Aluminum, despite being the most abundant metallic element in Earth's crust, remained unknown to humanity until the 19th century due to its strong chemical bonds with oxygen. Once extraction methods were developed, this lightweight metal—with a density merely one-third that of steel—revolutionized industries across the globe. Its discovery and subsequent industrialization mark one of the most significant material science achievements in modern history.

What distinguishes aluminum is its remarkable combination of lightness, strength, conductivity, and corrosion resistance. When exposed to air, aluminum rapidly forms a microscopic oxide layer that protects the underlying metal from further oxidation, giving it inherent durability in many environments without additional treatments. This natural protection, combined with its ability to be alloyed with small amounts of elements like copper, magnesium, and silicon, allows engineers to tailor aluminum's properties for specific applications.

From the Wright brothers' first powered flight to today's spacecraft, aluminum has been instrumental in transportation innovation. The metal pervades modern life—in the buildings we inhabit, the vehicles we drive, the packaging that preserves our food, and the electronic devices we rely on daily. As sustainability concerns grow, aluminum's infinite recyclability with minimal quality loss has become increasingly valuable, positioning this versatile metal at the heart of circular economy initiatives worldwide.
"""

    def _generate_steel_response(self) -> str:
        """Generate a detailed response about Steel material."""
        return """# Steel: The Foundation of Modern Infrastructure

## Introduction to Steel

Steel, an alloy of iron and carbon with carefully controlled amounts of other elements, represents humanity's most widely used and versatile engineered material. The development of modern steelmaking processes in the mid-19th century, particularly the Bessemer process, transformed steel from a precious material to one that could be mass-produced, fundamentally altering the trajectory of human civilization. This revolution in material availability enabled unprecedented scales of construction and manufacturing, giving rise to skyscrapers, railways, and the industrial landscapes that define our modern world.

What makes steel exceptional is its remarkable adaptability. By adjusting its chemical composition and processing methods, metallurgists can produce variants with vastly different properties—from ultra-high-strength steels used in automotive safety structures to stainless steels that resist corrosion in aggressive environments. This adaptability extends to steel's mechanical properties, which can be precisely engineered through heat treatment to achieve the optimal balance of strength, ductility, and toughness for specific applications.

In an age increasingly concerned with sustainability, steel's inherent recyclability stands as one of its most valuable attributes. Nearly all steel products can be recycled at the end of their useful life, with minimal loss of properties, making steel production a potential model for circular material economies. As we face the challenges of climate change, innovations in green steelmaking—including hydrogen reduction and electric arc furnaces powered by renewable energy—are poised to reduce the environmental impact of this essential material that continues to form the backbone of global infrastructure.
"""

    def _generate_copper_response(self) -> str:
        """Generate a detailed response about Copper material."""
        return """# Copper: The Ancient Metal of Connectivity

## Introduction to Copper

Copper, with its distinctive reddish-orange luster, holds the distinction of being one of the first metals worked by human hands, with archaeological evidence of copper use dating back to 8000 BCE. This elemental metal played such a pivotal role in early human development that it defined an entire archaeological period—the Copper Age—preceding even the Bronze Age. What made copper revolutionary was its malleability, allowing early metalsmiths to hammer it into useful shapes without fracturing, combined with sufficient durability for practical tools and decorative objects.

The defining characteristic that ensures copper's continued relevance in modern technology is its exceptional electrical conductivity, second only to silver among common metals. This property, coupled with its corrosion resistance and ductility, established copper as the fundamental material for global electrical infrastructure. The worldwide electrification that transformed human civilization in the late 19th and early 20th centuries was built quite literally on copper wiring, and today's digital revolution depends on copper's ability to transmit power and data with minimal loss.

Beyond its electrical applications, copper's antimicrobial properties—the ability to kill bacteria, viruses, and other pathogens on contact—have gained renewed attention in healthcare settings and public spaces. This natural property, known as the oligodynamic effect, makes copper and its alloys valuable for touch surfaces in hospitals and high-traffic facilities. As humanity faces challenges from energy transition to infectious disease control, this ancient metal continues to demonstrate remarkable versatility in addressing contemporary problems.
"""

    def _generate_titanium_response(self) -> str:
        """Generate a detailed response about Titanium material."""
        return """# Titanium: The Space Age Metal

## Introduction to Titanium

Titanium, though discovered in 1791, remained largely a laboratory curiosity until the mid-20th century when the development of the Kroll process finally made commercial production viable. Named after the Titans of Greek mythology, this silvery transition metal has lived up to its powerful namesake through its extraordinary properties. Despite being the ninth most abundant element in Earth's crust, titanium's strong affinity for oxygen made it one of the last industrial metals to be isolated and utilized at scale—a challenge that, once overcome, unleashed revolutionary capabilities across aerospace, medicine, and high-performance applications.

What distinguishes titanium is its unparalleled strength-to-weight ratio—approximately 40% lighter than steel yet comparably strong in many alloy formulations. This mechanical efficiency combines with exceptional corrosion resistance, even in seawater and chlorine environments that would rapidly degrade other structural metals. Titanium naturally forms a stable, self-healing oxide layer when exposed to air, providing inherent protection against many forms of environmental degradation without additional treatments or coatings.

The biocompatibility of titanium represents perhaps its most profound contribution to human well-being. The metal's ability to integrate with human bone and tissue without rejection has revolutionized medical implants, from replacement joints and dental implants to cranial plates and pacemaker casings. As manufacturing technologies advance, particularly additive manufacturing (3D printing), titanium's application scope continues to expand into previously impossible geometries and structures, suggesting that this relatively young industrial metal still holds untapped potential for addressing future engineering challenges.
"""
