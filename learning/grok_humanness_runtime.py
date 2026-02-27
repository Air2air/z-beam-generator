"""
Runtime Grok humanness evaluator.

Loads the evaluator contract + JSON schema, calls Grok, validates output,
and returns a schema-validated evaluation payload.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import jsonschema
import yaml

from shared.api.client import GenerationRequest
from shared.api.client_factory import create_api_client

logger = logging.getLogger(__name__)


class GrokHumannessRuntimeEvaluator:
    """Runtime evaluator for criterion-level Grok humanness scoring."""

    def __init__(
        self,
        api_client=None,
        contract_path: Optional[Path] = None,
        schema_path: Optional[Path] = None,
    ):
        project_root = Path(__file__).resolve().parents[1]

        self.contract_path = contract_path or project_root / "prompts" / "quality" / "grok_humanness_evaluator_contract.yaml"
        self.schema_path = schema_path or project_root / "data" / "schemas" / "grok_humanness_evaluation.schema.json"

        self.contract = self._load_yaml(self.contract_path)
        self.schema = self._load_json(self.schema_path)
        self.api_client = api_client or create_api_client("grok")

    def evaluate(
        self,
        *,
        candidate_text: str,
        domain: str,
        item_id: str,
        component_type: str,
        author_id: int,
        generation_id: Optional[int],
        retry_session_id: Optional[str],
        attempt: int,
    ) -> Dict[str, Any]:
        system_prompt = self.contract["systemPrompt"]
        user_prompt = self._render_user_prompt(
            domain=domain,
            item_id=item_id,
            component_type=component_type,
            author_id=author_id,
            generation_id=generation_id,
            retry_session_id=retry_session_id,
            attempt=attempt,
            candidate_text=candidate_text,
        )

        request = GenerationRequest(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=self._required_client_config("max_tokens"),
            temperature=self._required_client_config("temperature"),
        )

        response = self.api_client.generate(request)
        if not response.success:
            raise RuntimeError(f"Grok humanness evaluation call failed: {response.error}")

        payload = self._extract_json_payload(response.content)
        payload = self._normalize_payload(
            payload=payload,
            domain=domain,
            item_id=item_id,
            component_type=component_type,
            author_id=author_id,
            generation_id=generation_id,
            retry_session_id=retry_session_id,
            attempt=attempt,
        )
        jsonschema.validate(payload, self.schema)

        return payload

    def _normalize_payload(
        self,
        *,
        payload: Dict[str, Any],
        domain: str,
        item_id: str,
        component_type: str,
        author_id: int,
        generation_id: Optional[int],
        retry_session_id: Optional[str],
        attempt: int,
    ) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise TypeError("Grok evaluator payload must be a JSON object")

        criteria_cfg = self.contract.get("criteria")
        if not isinstance(criteria_cfg, dict):
            raise TypeError("Evaluator contract missing required 'criteria' mapping")

        gating_cfg = self.contract.get("gating")
        if not isinstance(gating_cfg, dict):
            raise TypeError("Evaluator contract missing required 'gating' mapping")

        criterion_keys = list(criteria_cfg.keys())
        criterion_mins = {
            key: criteria_cfg[key]["minScore"]
            for key in criterion_keys
        }
        weights = {
            key: criteria_cfg[key]["weight"]
            for key in criterion_keys
        }

        raw_scores = payload.get("scores")
        if not isinstance(raw_scores, dict):
            raise TypeError("Grok evaluator payload missing required 'scores' object")

        normalized_scores: Dict[str, Dict[str, Any]] = {}
        for key in criterion_keys:
            raw_entry = raw_scores.get(key)
            if raw_entry is None:
                raise KeyError(f"Grok evaluator payload missing scores.{key}")

            if isinstance(raw_entry, (int, float)):
                score_value = float(raw_entry)
                evidence = [f"Score provided without evidence for {key}"]
                issues = []
            elif isinstance(raw_entry, dict):
                if "score" not in raw_entry:
                    raise KeyError(f"Grok evaluator payload missing scores.{key}.score")
                score_value = float(raw_entry["score"])

                evidence = raw_entry.get("evidence", [])
                if isinstance(evidence, str):
                    evidence = [evidence]
                if not isinstance(evidence, list) or not evidence:
                    evidence = [f"No evidence provided for {key}"]

                issues = raw_entry.get("issues", [])
                if isinstance(issues, str):
                    issues = [issues]
                if not isinstance(issues, list):
                    issues = []
            else:
                raise TypeError(f"Grok evaluator scores.{key} must be object or number")

            normalized_scores[key] = {
                "score": score_value,
                "evidence": [str(item) for item in evidence],
                "issues": [str(item) for item in issues],
            }

        raw_evaluator = payload.get("evaluator")
        if not isinstance(raw_evaluator, dict):
            raw_evaluator = {}

        raw_aggregation = payload.get("aggregation")
        if not isinstance(raw_aggregation, dict):
            raw_aggregation = {}

        weighted_score = raw_aggregation.get("weightedScore", payload.get("weightedScore"))
        if weighted_score is None:
            raise KeyError("Grok evaluator payload missing weighted score")

        confidence = raw_aggregation.get("confidence", payload.get("confidence"))
        if confidence is None:
            raise KeyError("Grok evaluator payload missing confidence")

        score_band = raw_aggregation.get("scoreBand", payload.get("scoreBand"))
        if score_band is None:
            raise KeyError("Grok evaluator payload missing scoreBand")

        raw_gates = payload.get("gates")
        if not isinstance(raw_gates, dict):
            raw_gates = {}

        fail_reasons = raw_gates.get("failReasons", [])
        if isinstance(fail_reasons, str):
            fail_reasons = [fail_reasons]
        if not isinstance(fail_reasons, list):
            fail_reasons = []

        raw_actions = payload.get("actions", [])
        normalized_actions = self._normalize_actions(raw_actions)

        return {
            "schemaVersion": self.contract["schemaVersion"],
            "evaluator": {
                "provider": self.contract["provider"],
                "model": str(raw_evaluator.get("model", self._required_client_config("model"))),
                "mode": str(raw_evaluator.get("mode", self.contract["mode"])),
                "promptVersion": str(raw_evaluator.get("promptVersion", self.contract["promptVersion"])),
                "timestamp": str(raw_evaluator.get("timestamp")),
            },
            "context": {
                "domain": domain,
                "itemId": item_id,
                "componentType": component_type,
                "authorId": author_id,
                "generationId": generation_id,
                "retrySessionId": retry_session_id,
                "attempt": attempt,
            },
            "scores": normalized_scores,
            "aggregation": {
                "weights": weights,
                "weightedScore": float(weighted_score),
                "confidence": float(confidence),
                "scoreBand": str(score_band),
            },
            "gates": {
                "pass": bool(raw_gates.get("pass", False)),
                "failReasons": [str(reason) for reason in fail_reasons],
                "thresholds": {
                    "overallMin": float(gating_cfg["overallMin"]),
                    "confidenceMin": float(gating_cfg["confidenceMin"]),
                    "criterionMins": criterion_mins,
                },
            },
            "actions": normalized_actions,
        }

    def _normalize_actions(self, actions: Any) -> list[Dict[str, Any]]:
        if isinstance(actions, str):
            actions = [actions]
        if not isinstance(actions, list) or not actions:
            raise ValueError("Grok evaluator payload must include at least one action")

        normalized: list[Dict[str, Any]] = []
        for index, action in enumerate(actions, start=1):
            if isinstance(action, dict):
                priority = action.get("priority", min(index, 5))
                criterion = action.get("criterion")
                if not isinstance(criterion, str) or not criterion:
                    criterion = self._infer_criterion(str(action))

                issue = str(action.get("issue", "Improve this criterion"))
                recommendation = str(action.get("recommendation", issue))
                example_rewrite = str(action.get("exampleRewrite", recommendation))
            else:
                action_text = str(action)
                criterion = self._infer_criterion(action_text)
                issue = action_text
                recommendation = action_text
                example_rewrite = action_text
                priority = min(index, 5)

            normalized.append(
                {
                    "priority": int(priority),
                    "criterion": criterion,
                    "issue": issue,
                    "recommendation": recommendation,
                    "exampleRewrite": example_rewrite,
                }
            )

        return normalized

    @staticmethod
    def _infer_criterion(action_text: str) -> str:
        lowered = action_text.lower()
        if "lexical" in lowered or "vocabulary" in lowered:
            return "lexicalVariety"
        if "syntax" in lowered or "sentence" in lowered or "rhythm" in lowered:
            return "syntacticRhythm"
        if "coherence" in lowered or "flow" in lowered or "transition" in lowered:
            return "discourseCoherence"
        if "specific" in lowered or "evidence" in lowered or "detail" in lowered:
            return "specificityEvidence"
        if "persona" in lowered or "voice" in lowered or "tone" in lowered:
            return "personaFidelity"
        return "aiPatternSuppression"

    def _render_user_prompt(
        self,
        *,
        domain: str,
        item_id: str,
        component_type: str,
        author_id: int,
        generation_id: Optional[int],
        retry_session_id: Optional[str],
        attempt: int,
        candidate_text: str,
    ) -> str:
        template = self.contract["userPromptTemplate"]
        replacements = {
            "{{domain}}": domain,
            "{{item_id}}": item_id,
            "{{component_type}}": component_type,
            "{{author_id}}": str(author_id),
            "{{generation_id_or_null}}": "null" if generation_id is None else str(generation_id),
            "{{retry_session_id_or_null}}": "null" if retry_session_id is None else json.dumps(retry_session_id),
            "{{attempt_number}}": str(attempt),
            "{{candidate_text}}": candidate_text,
        }

        prompt = template
        for token, value in replacements.items():
            prompt = prompt.replace(token, value)

        return prompt

    def _required_client_config(self, key: str) -> Any:
        if hasattr(self.api_client, "config") and isinstance(self.api_client.config, dict):
            if key not in self.api_client.config:
                raise KeyError(f"API client config missing required key: {key}")
            return self.api_client.config[key]

        if hasattr(self.api_client, "config") and hasattr(self.api_client.config, key):
            return getattr(self.api_client.config, key)

        raise KeyError(f"API client config missing required key: {key}")

    @staticmethod
    def _extract_json_payload(content: str) -> Dict[str, Any]:
        text = content.strip()

        if text.startswith("```"):
            first_newline = text.find("\n")
            last_fence = text.rfind("```")
            if first_newline == -1 or last_fence == -1 or last_fence <= first_newline:
                raise ValueError("Invalid fenced JSON response from Grok evaluator")
            text = text[first_newline + 1:last_fence].strip()

        if not text.startswith("{"):
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise ValueError("Grok evaluator response does not contain JSON object")
            text = text[start:end + 1]

        return json.loads(text)

    @staticmethod
    def _load_yaml(path: Path) -> Dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Required evaluator contract file not found: {path}")
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        if not isinstance(data, dict):
            raise TypeError(f"Evaluator contract must be a dictionary: {path}")
        return data

    @staticmethod
    def _load_json(path: Path) -> Dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Required evaluator schema file not found: {path}")
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise TypeError(f"Evaluator schema must be a JSON object: {path}")
        return data
