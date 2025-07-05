import os
from typing import Dict


class PromptManager:
    """Centralized loader and cache for all prompt templates."""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.cache: Dict[str, str] = {}

    def load_prompt(self, prompt_name: str, subdir: str = "") -> str:
        key = f"{subdir}/{prompt_name}" if subdir else prompt_name
        if key in self.cache:
            return self.cache[key]
        path = (
            os.path.join(self.base_dir, subdir, prompt_name)
            if subdir
            else os.path.join(self.base_dir, prompt_name)
        )
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                self.cache[key] = content
                return content
        except Exception as e:
            raise FileNotFoundError(f"Prompt not found: {path} ({e})")

    def load_all_prompts(self, subdir: str = "") -> Dict[str, str]:
        dir_path = os.path.join(self.base_dir, subdir) if subdir else self.base_dir
        prompts = {}
        for fname in os.listdir(dir_path):
            if fname.endswith(".txt"):
                prompts[fname] = self.load_prompt(fname, subdir)
        return prompts
