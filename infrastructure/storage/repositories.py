"""
File-based repositories for prompts and cache.
"""

import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from generator.core.domain.models import PromptTemplate, CacheEntry
from generator.core.interfaces.services import IPromptRepository, ICacheRepository
from generator.core.exceptions import FileOperationError
from generator.modules.logger import get_logger

logger = get_logger("file_repositories")


class FilePromptRepository(IPromptRepository):
    """File-based repository for prompt templates."""

    def __init__(self, prompts_dir: Path):
        self._prompts_dir = Path(prompts_dir)
        if not self._prompts_dir.exists():
            raise FileOperationError(
                f"Prompts directory does not exist: {prompts_dir}",
                str(prompts_dir),
                "initialize_repository",
            )

    def get_prompt(self, name: str, category: str) -> Optional[PromptTemplate]:
        """Retrieve a prompt template by name and category."""
        try:
            file_path = self._prompts_dir / category / f"{name}.txt"
            if not file_path.exists():
                logger.debug(f"Prompt file not found: {file_path}")
                return None

            content = file_path.read_text(encoding="utf-8")
            if not content.strip():
                logger.warning(f"Empty prompt file: {file_path}")
                return None

            # Extract variables from the template (simple approach)
            import re

            variables = re.findall(r"{(\w+)}", content)

            return PromptTemplate(
                name=name,
                category=category,
                content=content,
                variables=list(set(variables)),
            )

        except Exception as e:
            logger.error(f"Failed to read prompt {name} from {category}: {str(e)}")
            raise FileOperationError(
                f"Failed to read prompt file: {str(e)}",
                str(file_path) if "file_path" in locals() else None,
                "read_prompt",
            ) from e

    def list_prompts(self, category: Optional[str] = None) -> List[PromptTemplate]:
        """List available prompt templates."""
        prompts = []
        try:
            if category:
                categories = [category]
            else:
                categories = [d.name for d in self._prompts_dir.iterdir() if d.is_dir()]

            for cat in categories:
                cat_dir = self._prompts_dir / cat
                if not cat_dir.exists():
                    continue

                for file_path in cat_dir.glob("*.txt"):
                    prompt = self.get_prompt(file_path.stem, cat)
                    if prompt:
                        prompts.append(prompt)

            return prompts

        except Exception as e:
            logger.error(f"Failed to list prompts: {str(e)}")
            raise FileOperationError(
                f"Failed to list prompts: {str(e)}",
                str(self._prompts_dir),
                "list_prompts",
            ) from e

    def save_prompt(self, prompt: PromptTemplate) -> None:
        """Save a prompt template."""
        try:
            category_dir = self._prompts_dir / prompt.category
            category_dir.mkdir(parents=True, exist_ok=True)

            file_path = category_dir / f"{prompt.name}.txt"
            file_path.write_text(prompt.content, encoding="utf-8")

            logger.info(f"Saved prompt: {prompt.name} in {prompt.category}")

        except Exception as e:
            logger.error(f"Failed to save prompt {prompt.name}: {str(e)}")
            raise FileOperationError(
                f"Failed to save prompt: {str(e)}",
                str(file_path) if "file_path" in locals() else None,
                "save_prompt",
            ) from e


class FileCacheRepository(ICacheRepository):
    """File-based repository for content caching."""

    def __init__(self, cache_dir: Path):
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self._cache_dir / "cache_index.json"
        self._load_index()

    def _load_index(self) -> None:
        """Load the cache index."""
        try:
            if self._index_file.exists():
                self._index = json.loads(self._index_file.read_text(encoding="utf-8"))
            else:
                self._index = {}
        except Exception as e:
            logger.warning(f"Failed to load cache index, starting fresh: {str(e)}")
            self._index = {}

    def _save_index(self) -> None:
        """Save the cache index."""
        try:
            self._index_file.write_text(
                json.dumps(self._index, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"Failed to save cache index: {str(e)}")

    def get(self, key: str) -> Optional[CacheEntry]:
        """Retrieve a cache entry by key."""
        try:
            if key not in self._index:
                return None

            entry_info = self._index[key]
            cache_file = self._cache_dir / f"{key}.txt"

            if not cache_file.exists():
                # Clean up stale index entry
                del self._index[key]
                self._save_index()
                return None

            content = cache_file.read_text(encoding="utf-8")

            return CacheEntry(
                key=key,
                content=content,
                timestamp=entry_info["timestamp"],
                metadata=entry_info.get("metadata", {}),
            )

        except Exception as e:
            logger.error(f"Failed to get cache entry {key}: {str(e)}")
            return None

    def set(
        self, key: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store a cache entry."""
        try:
            cache_file = self._cache_dir / f"{key}.txt"
            cache_file.write_text(content, encoding="utf-8")

            self._index[key] = {"timestamp": time.time(), "metadata": metadata or {}}
            self._save_index()

            logger.debug(f"Cached content with key: {key}")

        except Exception as e:
            logger.error(f"Failed to cache content {key}: {str(e)}")
            raise FileOperationError(
                f"Failed to cache content: {str(e)}",
                str(cache_file) if "cache_file" in locals() else None,
                "cache_set",
            ) from e

    def delete(self, key: str) -> None:
        """Delete a cache entry."""
        try:
            cache_file = self._cache_dir / f"{key}.txt"
            if cache_file.exists():
                cache_file.unlink()

            if key in self._index:
                del self._index[key]
                self._save_index()

            logger.debug(f"Deleted cache entry: {key}")

        except Exception as e:
            logger.error(f"Failed to delete cache entry {key}: {str(e)}")

    def clear_expired(self, max_age_seconds: float) -> int:
        """Clear expired cache entries and return count of deleted entries."""
        deleted_count = 0
        current_time = time.time()
        keys_to_delete = []

        try:
            for key, entry_info in self._index.items():
                if (current_time - entry_info["timestamp"]) > max_age_seconds:
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                self.delete(key)
                deleted_count += 1

            if deleted_count > 0:
                logger.info(f"Cleared {deleted_count} expired cache entries")

            return deleted_count

        except Exception as e:
            logger.error(f"Failed to clear expired cache entries: {str(e)}")
            return deleted_count
