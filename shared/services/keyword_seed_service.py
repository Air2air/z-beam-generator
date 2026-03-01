#!/usr/bin/env python3
"""
Keyword Seed Service

Creates a new domain item from a single topic keyword by cloning a domain template
record and normalizing identity fields (id/slug/name/displayName/fullPath/etc.).

This service is domain-agnostic and reusable across all supported domains.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import re
import yaml
from data.authors.registry import assign_random_author


DOMAIN_TITLE_SUFFIX: Dict[str, str] = {
    'materials': 'Laser Cleaning',
    'contaminants': 'Contamination',
    'compounds': 'Compound',
    'settings': 'Settings',
    'applications': 'Laser Cleaning',
}


@dataclass(frozen=True)
class SeedResult:
    item_id: str
    data_path: Path
    used_template_item: str
    created: bool


class KeywordSeedService:
    """Service for creating new domain records from a single keyword."""

    def __init__(self, domain: str):
        self.domain = domain
        self.domain_config_path = Path(f'domains/{domain}/config.yaml')
        if not self.domain_config_path.exists():
            raise FileNotFoundError(f"Domain config not found: {self.domain_config_path}")

        self.domain_config = self._load_yaml(self.domain_config_path)
        self.data_path = Path(self.domain_config['data_path'])
        self.items_key = self.domain_config['data_root_key']
        self.frontmatter_pattern = self.domain_config['frontmatter_pattern']

        if not self.data_path.exists():
            raise FileNotFoundError(f"Domain source file not found: {self.data_path}")

    def seed_from_keyword(
        self,
        keyword: str,
        template_item: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        dry_run: bool = False,
    ) -> SeedResult:
        """Create a new domain item from keyword and persist to source YAML."""
        normalized_keyword = keyword.strip()
        if not normalized_keyword:
            raise ValueError("Keyword cannot be empty")

        topic_slug = self._slugify(normalized_keyword)
        topic_slug = self._normalize_topic_slug(topic_slug)
        if not topic_slug:
            raise ValueError(f"Keyword produced empty slug: {keyword}")

        item_id = self._build_item_id(topic_slug)

        data = self._load_yaml(self.data_path)
        items = data.get(self.items_key)
        if not isinstance(items, dict):
            raise ValueError(
                f"Expected '{self.items_key}' dictionary in {self.data_path}, got {type(items).__name__}"
            )

        if item_id in items:
            raise ValueError(f"Item already exists: {item_id}")

        used_template = template_item or self._select_template_item(items, topic_slug)
        if used_template not in items:
            raise KeyError(f"Template item not found in '{self.items_key}': {used_template}")

        template_data = items[used_template]
        if not isinstance(template_data, dict):
            raise ValueError(f"Template item must be dict: {used_template}")

        new_item = self._build_item_from_template(
            template_item=template_data,
            keyword=topic_slug,
            item_id=item_id,
            category=category,
            subcategory=subcategory,
        )

        self._clear_generated_text_fields(new_item)

        items[item_id] = new_item
        data['lastUpdated'] = datetime.now(timezone.utc).date().isoformat()

        if not dry_run:
            self._write_yaml(self.data_path, data)

        return SeedResult(
            item_id=item_id,
            data_path=self.data_path,
            used_template_item=used_template,
            created=True,
        )

    def _select_template_item(self, items: Dict[str, Any], topic_slug: str) -> str:
        if not items:
            raise ValueError(f"No items available in {self.data_path} for template cloning")

        topic_tokens = [token for token in topic_slug.split('-') if token]
        if not topic_tokens:
            return next(iter(items.keys()))

        best_item = None
        best_score = -1
        for item_id in items.keys():
            item_tokens = set(token for token in item_id.split('-') if token)
            score = sum(1 for token in topic_tokens if token in item_tokens)
            if score > best_score:
                best_score = score
                best_item = item_id

        if best_item is None:
            return next(iter(items.keys()))

        return best_item

    def _build_item_id(self, topic_slug: str) -> str:
        if self.domain == 'applications':
            if 'laser-cleaning' in topic_slug:
                return f"{topic_slug}-applications"
            return f"{topic_slug}-laser-cleaning-applications"

        suffix = self.frontmatter_pattern.replace('{slug}', '').replace('.yaml', '')
        return f"{topic_slug}{suffix}"

    def _build_item_from_template(
        self,
        template_item: Dict[str, Any],
        keyword: str,
        item_id: str,
        category: Optional[str],
        subcategory: Optional[str],
    ) -> Dict[str, Any]:
        item = deepcopy(template_item)

        topic_title = self._to_title(keyword)
        current_category = category or item.get('category')
        current_subcategory = subcategory or item.get('subcategory')
        if self.domain == 'applications' and not subcategory:
            topic_parts = keyword.split('-')
            if topic_parts:
                current_subcategory = topic_parts[0]
        if self.domain != 'applications' and (not current_category or not current_subcategory):
            raise ValueError(
                f"Category/subcategory required for domain '{self.domain}' (provide args or template with values)"
            )

        page_title = self._build_page_title(topic_title)
        full_path = self._build_full_path(item_id, current_category, current_subcategory)

        item['id'] = item_id
        item['slug'] = item_id
        item['name'] = topic_title
        item['displayName'] = page_title
        item['pageTitle'] = page_title
        item['fullPath'] = full_path

        if current_category:
            item['category'] = current_category
        if current_subcategory:
            item['subcategory'] = current_subcategory

        now = datetime.now(timezone.utc)
        item['datePublished'] = now.date().isoformat()
        item['dateModified'] = now.isoformat()

        if isinstance(item.get('card'), dict):
            summary_text = self._build_summary_text(page_title)
            item['card']['title'] = page_title
            item['card']['description'] = summary_text

        item['metaDescription'] = self._build_summary_text(page_title)

        item['keywords'] = self._unique_non_empty([page_title, topic_title])
        self._assign_author(item)
        self._remove_legacy_root_relationship_fields(item)
        self._update_breadcrumb(
            item=item,
            topic_title=topic_title,
            category=current_category,
            subcategory=current_subcategory,
            item_id=item_id,
            full_path=full_path,
        )

        return item

    def _assign_author(self, item: Dict[str, Any]) -> None:
        """Assign author for newly seeded items using canonical random assignment policy."""
        assigned_author = assign_random_author()
        item['author'] = assigned_author
        item['authorId'] = assigned_author['id']

    def _build_page_title(self, topic_title: str) -> str:
        if self.domain == 'applications' and 'laser cleaning' in topic_title.lower():
            return topic_title

        suffix = DOMAIN_TITLE_SUFFIX.get(self.domain)
        if not suffix:
            suffix = self._to_title(self.domain.replace('-', ' '))
        return f"{topic_title} {suffix}"

    def _build_summary_text(self, page_title: str) -> str:
        if self.domain == 'applications':
            return f"{page_title} applications and operational guidance for laser cleaning workflows."

        domain_label = self._to_title(self.domain.replace('-', ' '))
        return f"{page_title} reference information for {domain_label.lower()} laser cleaning workflows."

    def _normalize_topic_slug(self, topic_slug: str) -> str:
        if self.domain == 'applications':
            return re.sub(r'-applications$', '', topic_slug)
        return topic_slug

    def _clear_generated_text_fields(self, item: Dict[str, Any]) -> None:
        """Clear generator-owned text fields so new items never keep template prose."""
        config_path = Path(f'generation/backfill/config/{self.domain}.yaml')
        if not config_path.exists():
            return

        config = self._load_yaml(config_path)
        generators = config.get('generators', [])
        if not isinstance(generators, list):
            return

        field_paths = []
        for generator in generators:
            if not isinstance(generator, dict):
                continue

            if isinstance(generator.get('field'), str):
                field_paths.append(generator['field'])

            fields = generator.get('fields', [])
            if isinstance(fields, list):
                for field_mapping in fields:
                    if isinstance(field_mapping, dict) and isinstance(field_mapping.get('field'), str):
                        field_paths.append(field_mapping['field'])

        for path in self._unique_non_empty(field_paths):
            self._set_nested_field(item, path, '')

    @staticmethod
    def _remove_legacy_root_relationship_fields(item: Dict[str, Any]) -> None:
        """Remove deprecated root-level relationship text containers from cloned templates."""
        for legacy_key in ('relatedMaterials', 'contaminatedBy'):
            if legacy_key in item and isinstance(item[legacy_key], dict):
                del item[legacy_key]

    def _build_full_path(self, item_id: str, category: Optional[str], subcategory: Optional[str]) -> str:
        if self.domain == 'applications':
            return f"/{self.domain}/{item_id}"

        category_path = self._slugify(category or '')
        subcategory_path = self._slugify(subcategory or '')
        if not category_path or not subcategory_path:
            raise ValueError(
                f"Cannot build fullPath for domain '{self.domain}' without category/subcategory"
            )
        return f"/{self.domain}/{category_path}/{subcategory_path}/{item_id}"

    def _update_breadcrumb(
        self,
        item: Dict[str, Any],
        topic_title: str,
        category: Optional[str],
        subcategory: Optional[str],
        item_id: str,
        full_path: str,
    ) -> None:
        domain_label = self.domain.capitalize()
        breadcrumb = [
            {'label': 'Home', 'href': '/'},
            {'label': domain_label, 'href': f'/{self.domain}'},
        ]

        if self.domain == 'applications':
            subcategory_slug = self._slugify(subcategory or '')
            if subcategory_slug:
                parent_slug = self._normalize_topic_slug(subcategory_slug)
                parent_item_id = self._build_item_id(parent_slug)
                if item_id != parent_item_id:
                    breadcrumb.append({
                        'label': self._to_title(subcategory_slug.replace('-', ' ')),
                        'href': f'/applications/{parent_item_id}',
                    })
                breadcrumb.append({'label': topic_title, 'href': f'/applications/{item_id}'})

            item['breadcrumb'] = breadcrumb
            return

        category_slug = self._slugify(category or '')
        subcategory_slug = self._slugify(subcategory or '')

        if category_slug and category_slug != self._slugify(self.domain):
            breadcrumb.append({
                'label': self._to_title(category_slug.replace('-', ' ')),
                'href': f'/{self.domain}/{category_slug}',
            })

        if subcategory_slug:
            if category_slug:
                subcategory_href = f'/{self.domain}/{category_slug}/{subcategory_slug}'
            else:
                subcategory_href = f'/{self.domain}/{subcategory_slug}'
            breadcrumb.append({
                'label': self._to_title(subcategory_slug.replace('-', ' ')),
                'href': subcategory_href,
            })

        breadcrumb.append({'label': topic_title, 'href': full_path})

        item['breadcrumb'] = breadcrumb

    @staticmethod
    def _slugify(value: str) -> str:
        lowered = value.strip().lower()
        cleaned = re.sub(r'[^a-z0-9]+', '-', lowered)
        return cleaned.strip('-')

    @staticmethod
    def _to_title(value: str) -> str:
        parts = re.split(r'[\s\-_/]+', value.strip())
        tokens = [token for token in parts if token]
        return ' '.join(token.capitalize() for token in tokens)

    @staticmethod
    def _unique_non_empty(values):
        result = []
        seen = set()
        for value in values:
            if not isinstance(value, str):
                continue
            normalized = value.strip()
            if not normalized:
                continue
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            result.append(normalized)
        return result

    @staticmethod
    def _set_nested_field(data: Dict[str, Any], path: str, value: Any) -> None:
        parts = path.split('.')
        current = data

        for part in parts[:-1]:
            if part not in current or not isinstance(current.get(part), dict):
                current[part] = {}
            current = current[part]

        current[parts[-1]] = value

    @staticmethod
    def _load_yaml(path: Path) -> Dict[str, Any]:
        with open(path, 'r', encoding='utf-8') as handle:
            data = yaml.safe_load(handle)
        if not isinstance(data, dict):
            raise ValueError(f"Expected YAML mapping at {path}")
        return data

    @staticmethod
    def _write_yaml(path: Path, data: Dict[str, Any]) -> None:
        temp_file = path.with_suffix('.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as handle:
                yaml.safe_dump(
                    data,
                    handle,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    width=120,
                )
            temp_file.replace(path)
        except Exception as exc:
            if temp_file.exists():
                temp_file.unlink()
            raise RuntimeError(f"Failed writing YAML to {path}: {exc}") from exc
