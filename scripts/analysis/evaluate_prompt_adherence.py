#!/usr/bin/env python3
"""
Evaluate prompt adherence to topic/context across domains.

Uses live AI evaluation to score how strictly each prompt enforces
entry-topic relevance and context-specificity.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from shared.api.client import GenerationRequest
from shared.api.client_factory import create_api_client
from shared.config.settings import get_api_providers
from generation.core.adapters.domain_adapter import DomainAdapter

SUPPORTED_DOMAINS = [
    "materials",
    "contaminants",
    "compounds",
    "settings",
    "applications",
]

SUPPORTED_FIELDS = ["pageDescription", "micro", "faq"]

SECTION_INLINE_PROMPTS_PATH = PROJECT_ROOT / "prompts" / "shared" / "section_inline_prompts.yaml"


class PromptEvaluationError(RuntimeError):
    """Raised when evaluation fails or returns invalid output."""


def _load_inline_prompts() -> Dict[str, str]:
    if not SECTION_INLINE_PROMPTS_PATH.exists():
        raise FileNotFoundError(f"Missing inline prompt registry: {SECTION_INLINE_PROMPTS_PATH}")

    with open(SECTION_INLINE_PROMPTS_PATH, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ValueError("Inline prompts YAML must be a mapping")

    prompts = data.get("section_prompts")
    if not isinstance(prompts, dict):
        raise ValueError("Inline prompts YAML missing section_prompts mapping")

    normalized = {}
    for key, value in prompts.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Inline prompt '{key}' must be a non-empty string")
        normalized[str(key)] = value.strip()

    return normalized


def _load_domain_prompt(domain: str, field: str, inline_prompts: Dict[str, str]) -> str:
    if field == "pageDescription":
        path = PROJECT_ROOT / "prompts" / domain / "pageDescription.txt"
        if not path.exists():
            raise FileNotFoundError(f"Prompt file missing: {path}")
        return path.read_text(encoding="utf-8").strip()

    if field == "micro":
        if "micro" not in inline_prompts:
            raise KeyError("Inline prompt missing key: micro")
        return inline_prompts["micro"]

    if field == "faq":
        if "faq" not in inline_prompts:
            raise KeyError("Inline prompt missing key: faq")
        return inline_prompts["faq"]

    raise ValueError(f"Unsupported field: {field}")


def _build_simple_context(item_data: Dict[str, Any]) -> str:
    parts = []
    for key in ("category", "subcategory", "name", "displayName"):
        value = item_data.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(f"{key}: {value}")
    return "\n".join(parts)


def _select_sample_item(domain: str) -> Tuple[str, Dict[str, Any], str]:
    config_path = PROJECT_ROOT / "domains" / domain / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing domain config: {config_path}")

    with open(config_path, "r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    adapter_cfg = config.get("data_adapter")
    if isinstance(adapter_cfg, dict):
        data_path = adapter_cfg.get("data_path")
        data_root_key = adapter_cfg.get("data_root_key")
        context_keys = adapter_cfg.get("context_keys", [])
    else:
        data_path = config.get("data_path")
        data_root_key = config.get("data_root_key")
        context_keys = []

    if not data_path or not data_root_key:
        raise ValueError(f"Domain '{domain}' missing data_path/data_root_key in config")

    data_file = PROJECT_ROOT / data_path
    if not data_file.exists():
        raise FileNotFoundError(f"Domain data file not found: {data_file}")

    with open(data_file, "r", encoding="utf-8") as handle:
        all_data = yaml.safe_load(handle) or {}

    items = all_data.get(data_root_key)
    if not isinstance(items, dict) or not items:
        alias_map = {
            "contamination_patterns": ["contaminants"],
            "contaminants": ["contamination_patterns"],
        }
        for alias in alias_map.get(data_root_key, []):
            alias_items = all_data.get(alias)
            if isinstance(alias_items, dict) and alias_items:
                items = alias_items
                break

    if not isinstance(items, dict) or not items:
        raise ValueError(f"No items found for domain '{domain}'")

    sample_id = sorted(items.keys())[0]
    item_data = items[sample_id]

    if context_keys:
        context_parts = []
        for key in context_keys:
            value = item_data.get(key) if isinstance(item_data, dict) else None
            if value:
                context_parts.append(f"{key}: {value}")
        context = "\n".join(context_parts)
    else:
        context = _build_simple_context(item_data)

    return sample_id, item_data, context


def _build_eval_prompt(
    domain: str,
    field: str,
    prompt_text: str,
    sample_id: str,
    item_data: Dict[str, Any],
    context: str,
) -> str:
    summary_context = {
        "id": sample_id,
        "name": item_data.get("name", ""),
        "category": item_data.get("category", ""),
        "subcategory": item_data.get("subcategory", ""),
    }

    eval_payload = {
        "domain": domain,
        "field": field,
        "prompt": prompt_text,
        "sample": summary_context,
        "context": context,
    }

    return (
        "You are a strict prompt-adherence auditor.\n"
        "Evaluate whether the prompt enforces close adherence to the entry topic and context.\n"
        "Return STRICT JSON only with the schema below.\n\n"
        "Schema:\n"
        "{\n"
        "  \"topic_adherence_score\": 0-100,\n"
        "  \"context_specificity_score\": 0-100,\n"
        "  \"domain_anchor_score\": 0-100,\n"
        "  \"constraint_strength_score\": 0-100,\n"
        "  \"risks\": [\"...\"],\n"
        "  \"strengths\": [\"...\"],\n"
        "  \"verdict\": \"PASS\" or \"NEEDS_REVISION\"\n"
        "}\n\n"
        "Evaluation data (JSON):\n"
        f"{json.dumps(eval_payload, ensure_ascii=True)}"
    )


def _parse_eval_response(content: str) -> Dict[str, Any]:
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise PromptEvaluationError(f"Invalid JSON response: {exc}\nResponse: {content}") from exc

    required_keys = {
        "topic_adherence_score",
        "context_specificity_score",
        "domain_anchor_score",
        "constraint_strength_score",
        "risks",
        "strengths",
        "verdict",
    }
    missing = required_keys - set(data.keys())
    if missing:
        raise PromptEvaluationError(f"Missing required keys in response: {sorted(missing)}")

    return data


def _evaluate_prompt(api_client, provider_cfg: Dict[str, Any], eval_prompt: str) -> Dict[str, Any]:
    max_tokens = provider_cfg.get("max_tokens")
    temperature = provider_cfg.get("temperature")

    if max_tokens is None or temperature is None:
        raise ValueError("Provider config missing required max_tokens or temperature")

    request = GenerationRequest(
        prompt=eval_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    response = api_client.generate(request)
    if not response.success:
        raise PromptEvaluationError(f"API generation failed: {response.error}")

    return _parse_eval_response(response.content)


def _collect_targets(domains: List[str], fields: List[str]) -> List[Tuple[str, str]]:
    targets = []
    for domain in domains:
        if domain not in SUPPORTED_DOMAINS:
            raise ValueError(f"Unsupported domain: {domain}")
        for field in fields:
            if field not in SUPPORTED_FIELDS:
                raise ValueError(f"Unsupported field: {field}")
            targets.append((domain, field))
    return targets


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate prompt adherence with AI scoring")
    parser.add_argument(
        "--domains",
        default=",".join(SUPPORTED_DOMAINS),
        help="Comma-separated domains (default: all)",
    )
    parser.add_argument(
        "--fields",
        default=",".join(SUPPORTED_FIELDS),
        help="Comma-separated fields (default: pageDescription,micro,faq)",
    )
    parser.add_argument(
        "--provider",
        default="grok",
        help="API provider to use for evaluation (default: grok)",
    )

    args = parser.parse_args()

    domains = [d.strip() for d in args.domains.split(",") if d.strip()]
    fields = [f.strip() for f in args.fields.split(",") if f.strip()]

    inline_prompts = _load_inline_prompts()

    providers = get_api_providers()
    if args.provider not in providers:
        raise ValueError(f"Provider '{args.provider}' not configured in API_PROVIDERS")

    provider_cfg = providers[args.provider]
    api_client = create_api_client(args.provider)

    results = []
    targets = _collect_targets(domains, fields)

    for domain, field in targets:
        sample_id, item_data, context = _select_sample_item(domain)
        prompt_text = _load_domain_prompt(domain, field, inline_prompts)
        eval_prompt = _build_eval_prompt(domain, field, prompt_text, sample_id, item_data, context)

        print("=" * 80)
        print(f"Evaluating {domain}.{field} (sample: {sample_id})")

        evaluation = _evaluate_prompt(api_client, provider_cfg, eval_prompt)
        evaluation["domain"] = domain
        evaluation["field"] = field
        evaluation["sample_id"] = sample_id
        results.append(evaluation)

        print(
            f"Scores: topic={evaluation['topic_adherence_score']}, "
            f"context={evaluation['context_specificity_score']}, "
            f"domain={evaluation['domain_anchor_score']}, "
            f"constraints={evaluation['constraint_strength_score']}"
        )
        print(f"Verdict: {evaluation['verdict']}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    sorted_results = sorted(
        results,
        key=lambda r: (
            r["topic_adherence_score"],
            r["context_specificity_score"],
            r["domain_anchor_score"],
            r["constraint_strength_score"],
        ),
    )

    for entry in sorted_results:
        print(
            f"{entry['domain']}.{entry['field']} → "
            f"topic {entry['topic_adherence_score']}, "
            f"context {entry['context_specificity_score']}, "
            f"domain {entry['domain_anchor_score']}, "
            f"constraints {entry['constraint_strength_score']} "
            f"({entry['verdict']})"
        )

    print("\nTOP ISSUES")
    for entry in sorted_results[:5]:
        risks = entry.get("risks", [])
        risks_text = "; ".join(risks[:3]) if isinstance(risks, list) else str(risks)
        print(f"- {entry['domain']}.{entry['field']}: {risks_text}")


if __name__ == "__main__":
    main()
