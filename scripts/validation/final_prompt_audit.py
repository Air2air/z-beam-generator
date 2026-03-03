#!/usr/bin/env python3
"""
Audit the exact final prompt assembled right before generator API submission.

This script reuses canonical generation assembly primitives and validates:
- Prompt length/shape via validate_text_prompt
- Separation/coherence via validate_prompt_coherence
- Team-defined requirement checks from one centralized YAML file
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from generation.context.seo_formatter import SEOContextFormatter
from generation.core.generator import Generator
from learning.humanness_optimizer import HumannessOptimizer
from shared.api.client_factory import create_api_client
from shared.text.utils.prompt_builder import PromptBuilder
from shared.validation.content.prompt_coherence_validator import validate_prompt_coherence
from shared.validation.content.prompt_validator import validate_text_prompt


class FinalPromptAuditError(RuntimeError):
    """Raised when configuration or audit execution is invalid."""


@dataclass
class ComponentAuditResult:
    component: str
    passed: bool
    prompt: str
    prompt_chars: int
    prompt_words: int
    variation_seed: int
    validator_summary: str
    validator_is_valid: bool
    validator_issue_count: int
    coherence_summary: str
    coherence_is_valid: bool
    coherence_score: float
    coherence_issue_count: int
    sentence_count: int
    avg_sentence_words: float
    max_sentence_words: int
    custom_failures: List[str]


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise FinalPromptAuditError("Top-level config must be a YAML mapping")
    return data


def _extract_words(text: str) -> List[str]:
    return re.findall(r"\b[\w'-]+\b", text)


def _sentence_stats(text: str) -> Tuple[int, float, int]:
    sentence_chunks = [chunk.strip() for chunk in re.split(r"[.!?]+", text) if chunk.strip()]
    if not sentence_chunks:
        return 0, 0.0, 0

    sentence_word_counts = [len(_extract_words(chunk)) for chunk in sentence_chunks]
    sentence_count = len(sentence_word_counts)
    avg_words = sum(sentence_word_counts) / sentence_count if sentence_count else 0.0
    max_words = max(sentence_word_counts) if sentence_word_counts else 0
    return sentence_count, avg_words, max_words


def _normalize_component_list(config: Dict[str, Any], requested: Optional[List[str]]) -> List[Dict[str, Any]]:
    components = config.get("components")
    if not isinstance(components, list) or not components:
        raise FinalPromptAuditError("Config must include non-empty 'components' list")

    normalized: List[Dict[str, Any]] = []
    requested_set = set(requested or [])

    for entry in components:
        if not isinstance(entry, dict):
            raise FinalPromptAuditError("Each component entry must be a mapping")

        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            raise FinalPromptAuditError("Each component entry requires non-empty 'name'")

        if requested_set and name not in requested_set:
            continue
        if entry.get("enabled", True) is False:
            continue

        normalized.append(entry)

    if not normalized:
        raise FinalPromptAuditError("No enabled components selected for audit")
    return normalized


def _assemble_final_prompt(
    generator: Generator,
    identifier: str,
    component_type: str,
    faq_count: Optional[int],
) -> Tuple[str, int]:
    item_data = generator._get_item_data(identifier)

    seo_components = generator._get_domain_generation_list("seo_components")
    if component_type in seo_components:
        seo_context = SEOContextFormatter.enrich_material_for_seo(item_data, identifier)
        item_data.update(seo_context)

    author_id = generator.adapter.get_author_id(item_data)
    voice = generator._get_persona_by_author_id(author_id)
    facts = generator.data_provider.fetch_real_facts(identifier, component_type=component_type)
    context = generator._build_context(item_data)

    voice_parameters = generator.config.get("voice_parameters")
    if not isinstance(voice_parameters, dict):
        raise FinalPromptAuditError("Missing or invalid config section: voice_parameters")
    if "technical_intensity" not in voice_parameters:
        raise FinalPromptAuditError("Missing required config key: voice_parameters.technical_intensity")

    technical_intensity = voice_parameters["technical_intensity"]
    if not isinstance(technical_intensity, (int, float)):
        raise FinalPromptAuditError(
            "Invalid type for voice_parameters.technical_intensity: "
            f"{type(technical_intensity).__name__}"
        )

    length_target = generator.processing_config.get_component_length(component_type)
    humanness_layer = HumannessOptimizer().generate_humanness_instructions(
        component_type=component_type,
        length_target=length_target,
    )

    normalized_intensity = (technical_intensity - 1) / 2.0
    enrichment_params = {"technical_intensity": normalized_intensity}
    variation_seed = random.SystemRandom().randint(0, 2**31 - 1)

    prompt = PromptBuilder.build_unified_prompt(
        topic=identifier,
        voice=voice,
        length=None,
        facts=facts,
        context=context,
        component_type=component_type,
        domain=generator.domain,
        enrichment_params=enrichment_params,
        variation_seed=variation_seed,
        humanness_layer=humanness_layer,
        faq_count=faq_count,
        item_data=item_data,
    )

    if not isinstance(prompt, str) or not prompt.strip():
        raise FinalPromptAuditError(f"Assembled prompt is empty for component '{component_type}'")

    return prompt, variation_seed


def _run_custom_checks(prompt: str, checks: Dict[str, Any]) -> List[str]:
    failures: List[str] = []
    prompt_words = len(_extract_words(prompt))
    sentence_count, avg_sentence_words, max_sentence_words = _sentence_stats(prompt)

    min_words = checks.get("min_prompt_words")
    if isinstance(min_words, int) and prompt_words < min_words:
        failures.append(f"Prompt words {prompt_words} below min_prompt_words {min_words}")

    max_words = checks.get("max_prompt_words")
    if isinstance(max_words, int) and prompt_words > max_words:
        failures.append(f"Prompt words {prompt_words} above max_prompt_words {max_words}")

    max_avg_sentence_words = checks.get("max_average_sentence_words")
    if isinstance(max_avg_sentence_words, (int, float)) and avg_sentence_words > float(max_avg_sentence_words):
        failures.append(
            "Average sentence words "
            f"{avg_sentence_words:.1f} above max_average_sentence_words {max_avg_sentence_words}"
        )

    max_sentence_words_cfg = checks.get("max_sentence_words")
    if isinstance(max_sentence_words_cfg, int) and max_sentence_words > max_sentence_words_cfg:
        failures.append(
            f"Max sentence words {max_sentence_words} above max_sentence_words {max_sentence_words_cfg}"
        )

    required_contains = checks.get("required_contains", [])
    if isinstance(required_contains, list):
        for marker in required_contains:
            if isinstance(marker, str) and marker and marker not in prompt:
                failures.append(f"Missing required marker: {marker}")

    forbidden_contains = checks.get("forbidden_contains", [])
    if isinstance(forbidden_contains, list):
        for marker in forbidden_contains:
            if isinstance(marker, str) and marker and marker in prompt:
                failures.append(f"Found forbidden marker: {marker}")

    if sentence_count == 0:
        failures.append("Prompt contains zero detectable sentences")

    return failures


def _audit_component(
    generator: Generator,
    identifier: str,
    component_cfg: Dict[str, Any],
    strict_validator: bool,
    strict_coherence: bool,
) -> ComponentAuditResult:
    component_name = component_cfg["name"]
    faq_count = component_cfg.get("faq_count")
    if faq_count is not None and not isinstance(faq_count, int):
        raise FinalPromptAuditError(f"faq_count for component '{component_name}' must be an integer")

    prompt, variation_seed = _assemble_final_prompt(
        generator=generator,
        identifier=identifier,
        component_type=component_name,
        faq_count=faq_count,
    )

    validator_result = validate_text_prompt(prompt)
    coherence_result = validate_prompt_coherence(prompt)
    custom_checks = component_cfg.get("checks", {})
    if not isinstance(custom_checks, dict):
        raise FinalPromptAuditError(f"checks for component '{component_name}' must be a mapping")

    custom_failures = _run_custom_checks(prompt, custom_checks)
    sentence_count, avg_sentence_words, max_sentence_words = _sentence_stats(prompt)

    passed = True
    if strict_validator and not validator_result.is_valid:
        passed = False
    if strict_coherence and not coherence_result.is_coherent:
        passed = False
    if custom_failures:
        passed = False

    return ComponentAuditResult(
        component=component_name,
        passed=passed,
        prompt=prompt,
        prompt_chars=len(prompt),
        prompt_words=len(_extract_words(prompt)),
        variation_seed=variation_seed,
        validator_summary=validator_result.get_summary(),
        validator_is_valid=validator_result.is_valid,
        validator_issue_count=len(validator_result.issues),
        coherence_summary=coherence_result.get_summary(),
        coherence_is_valid=coherence_result.is_coherent,
        coherence_score=coherence_result.separation_score,
        coherence_issue_count=len(coherence_result.issues),
        sentence_count=sentence_count,
        avg_sentence_words=avg_sentence_words,
        max_sentence_words=max_sentence_words,
        custom_failures=custom_failures,
    )


def _write_json_report(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_markdown_report(path: Path, payload: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("# Final Prompt Audit Report")
    lines.append("")
    lines.append(f"- Generated: {payload['generated_at_utc']}")
    lines.append(f"- Domain: {payload['domain']}")
    lines.append(f"- Item: {payload['item']}")
    lines.append(f"- Provider: {payload['provider']}")
    lines.append(f"- Overall: {'PASS' if payload['overall_passed'] else 'FAIL'}")
    lines.append("")
    lines.append("## Component Results")
    lines.append("")
    lines.append("| Component | Pass | Prompt Words | Prompt Chars | Validator | Coherence |")
    lines.append("|---|---:|---:|---:|---|---|")

    for result in payload["results"]:
        lines.append(
            f"| {result['component']} | {'✅' if result['passed'] else '❌'} | "
            f"{result['prompt_words']} | {result['prompt_chars']} | "
            f"{result['validator_summary']} | {result['coherence_summary']} |"
        )

    for result in payload["results"]:
        lines.append("")
        lines.append(f"## {result['component']}")
        lines.append("")
        lines.append(f"- Pass: {'✅' if result['passed'] else '❌'}")
        lines.append(f"- Prompt words: {result['prompt_words']}")
        lines.append(f"- Prompt chars: {result['prompt_chars']}")
        lines.append(f"- Variation seed: {result['variation_seed']}")
        lines.append(f"- Sentence count: {result['sentence_count']}")
        lines.append(f"- Avg sentence words: {result['avg_sentence_words']:.2f}")
        lines.append(f"- Max sentence words: {result['max_sentence_words']}")

        if result["custom_failures"]:
            lines.append("- Custom failures:")
            for failure in result["custom_failures"]:
                lines.append(f"  - {failure}")
        else:
            lines.append("- Custom failures: none")

        lines.append("")
        lines.append("### Final Prompt")
        lines.append("")
        lines.append("```text")
        lines.append(result["prompt"])
        lines.append("```")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit exact final prompt assembled before generator API submission."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/final_prompt_gate.yaml",
        help="Path to centralized audit config YAML (default: config/final_prompt_gate.yaml)",
    )
    parser.add_argument(
        "--component",
        action="append",
        default=None,
        help="Optional component(s) to audit (repeatable), e.g. --component pageDescription",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default=None,
        help="Optional runtime domain override for audit target",
    )
    parser.add_argument(
        "--item",
        type=str,
        default=None,
        help="Optional runtime item override for audit target",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        help="Optional runtime provider override for audit execution",
    )
    return parser.parse_args()


def run_final_prompt_audit(
    config_path: str | Path = "config/final_prompt_gate.yaml",
    components: Optional[List[str]] = None,
    domain: Optional[str] = None,
    item: Optional[str] = None,
    provider: Optional[str] = None,
    api_client: Any = None,
) -> tuple[bool, Dict[str, Any]]:
    """Run final prompt audit in-process and return pass flag + payload."""
    resolved_config_path = (PROJECT_ROOT / str(config_path)).resolve()
    config = _load_yaml(resolved_config_path)

    audit_cfg = config.get("audit")
    if not isinstance(audit_cfg, dict):
        raise FinalPromptAuditError("Config must include 'audit' mapping")

    resolved_provider = provider or audit_cfg.get("provider", "grok")
    resolved_domain = domain or audit_cfg.get("domain")
    resolved_item = item or audit_cfg.get("item")
    strict_validator = bool(audit_cfg.get("fail_on_invalid", True))
    strict_coherence = bool(audit_cfg.get("fail_on_incoherent", True))

    if not isinstance(resolved_domain, str) or not resolved_domain:
        raise FinalPromptAuditError("audit.domain must be a non-empty string")
    if not isinstance(resolved_item, str) or not resolved_item:
        raise FinalPromptAuditError("audit.item must be a non-empty string")

    output_cfg = audit_cfg.get("output")
    if not isinstance(output_cfg, dict):
        raise FinalPromptAuditError("audit.output must be a mapping")

    json_output = PROJECT_ROOT / str(output_cfg.get("json", "tasks/final_prompt_audit_report.json"))
    md_output = PROJECT_ROOT / str(output_cfg.get("md", "tasks/final_prompt_audit_report.md"))

    selected_components = _normalize_component_list(config, components)
    resolved_api_client = api_client or create_api_client(resolved_provider)
    generator = Generator(api_client=resolved_api_client, domain=resolved_domain)

    results: List[ComponentAuditResult] = []
    for component_cfg in selected_components:
        results.append(
            _audit_component(
                generator=generator,
                identifier=resolved_item,
                component_cfg=component_cfg,
                strict_validator=strict_validator,
                strict_coherence=strict_coherence,
            )
        )

    overall_passed = all(result.passed for result in results)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config_path": str(resolved_config_path.relative_to(PROJECT_ROOT)),
        "provider": resolved_provider,
        "domain": resolved_domain,
        "item": resolved_item,
        "overall_passed": overall_passed,
        "results": [
            {
                "component": result.component,
                "passed": result.passed,
                "prompt_chars": result.prompt_chars,
                "prompt_words": result.prompt_words,
                "variation_seed": result.variation_seed,
                "validator_summary": result.validator_summary,
                "validator_is_valid": result.validator_is_valid,
                "validator_issue_count": result.validator_issue_count,
                "coherence_summary": result.coherence_summary,
                "coherence_is_valid": result.coherence_is_valid,
                "coherence_score": result.coherence_score,
                "coherence_issue_count": result.coherence_issue_count,
                "sentence_count": result.sentence_count,
                "avg_sentence_words": result.avg_sentence_words,
                "max_sentence_words": result.max_sentence_words,
                "custom_failures": result.custom_failures,
                "prompt": result.prompt,
            }
            for result in results
        ],
    }

    _write_json_report(json_output, payload)
    _write_markdown_report(md_output, payload)

    print("=" * 80)
    print("FINAL PROMPT AUDIT")
    print("=" * 80)
    print(f"Domain: {resolved_domain}")
    print(f"Item: {resolved_item}")
    print(f"Provider: {resolved_provider}")
    print(f"Overall: {'PASS' if overall_passed else 'FAIL'}")
    print(f"JSON report: {json_output.relative_to(PROJECT_ROOT)}")
    print(f"Markdown report: {md_output.relative_to(PROJECT_ROOT)}")
    print("-" * 80)
    for result in results:
        print(
            f"{result.component}: {'PASS' if result.passed else 'FAIL'} | "
            f"{result.prompt_words} words | {result.prompt_chars} chars | "
            f"validator={result.validator_summary} | coherence={result.coherence_summary}"
        )
        if result.custom_failures:
            for failure in result.custom_failures:
                print(f"  - {failure}")

    return overall_passed, payload


def main() -> int:
    args = parse_args()
    overall_passed, _payload = run_final_prompt_audit(
        config_path=args.config,
        components=args.component,
        domain=args.domain,
        item=args.item,
        provider=args.provider,
    )
    return 0 if overall_passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"❌ final_prompt_audit failed: {exc}")
        raise
