import os
import requests
import logging

logger = logging.getLogger("zbeam.api")

class APIClient:
    def __init__(self):
        self.provider = os.getenv("PROVIDER", "openai")
        self.model = os.getenv("MODEL", "gpt-4")
        self.api_keys = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "deepseek": os.getenv("DEEPSEEK_API_KEY"),
            "gemini": os.getenv("GEMINI_API_KEY"),
            "xai": os.getenv("XAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY")
        }

    def call_llm(self, prompt: str) -> str:
        if self.provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_keys['openai']}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1024
            }
            logger.info("Sending request to OpenAI API...")
            response = requests.post(url, headers=headers, json=data)
            logger.info("OpenAI response status: %s", response.status_code)
            response.raise_for_status()
            result = response.json()
            logger.debug("OpenAI raw response: %s", result)
            return result["choices"][0]["message"]["content"]

        elif self.provider == "deepseek":
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_keys['deepseek']}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1024
            }
            logger.info("Sending request to DeepSeek API...")
            response = requests.post(url, headers=headers, json=data)
            logger.info("DeepSeek response status: %s", response.status_code)
            response.raise_for_status()
            result = response.json()
            logger.debug("DeepSeek raw response: %s", result)
            return result["choices"][0]["message"]["content"]

        elif self.provider == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_keys['gemini']}"
            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            logger.info("Sending request to Gemini API...")
            response = requests.post(url, headers=headers, json=data)
            logger.info("Gemini response status: %s", response.status_code)
            response.raise_for_status()
            result = response.json()
            logger.debug("Gemini raw response: %s", result)
            # Gemini's response structure may vary; adjust as needed
            return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

        elif self.provider == "xai":
            url = "https://api.xai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_keys['xai']}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1024
            }
            logger.info("Sending request to XAI API...")
            response = requests.post(url, headers=headers, json=data)
            logger.info("XAI response status: %s", response.status_code)
            response.raise_for_status()
            result = response.json()
            logger.debug("XAI raw response: %s", result)
            return result["choices"][0]["message"]["content"]

        elif self.provider == "anthropic":
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": self.api_keys["anthropic"],
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            data = {
                "model": self.model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}]
            }
            logger.info("Sending request to Anthropic API...")
            response = requests.post(url, headers=headers, json=data)
            logger.info("Anthropic response status: %s", response.status_code)
            response.raise_for_status()
            result = response.json()
            logger.debug("Anthropic raw response: %s", result)
            # Adjust extraction based on Claude's response format
            return result.get("content", "")

        else:
            logger.error("Unsupported provider: %s", self.provider)
            raise ValueError(f"Unsupported provider: {self.provider}")