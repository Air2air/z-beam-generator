#!/usr/bin/env python3
"""
AI-research application relationships with high specificity.

Builds relationships.discovery.relatedMaterials and relationships.interactions.contaminatedBy
in Applications.yaml using:
- Industry guidance (typical materials, requirements, applications)
- Contaminant validMaterials coverage
- AI selection for specificity

This script updates source data only (Applications.yaml).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from shared.api.client_factory import create_api_client
from shared.api.client import GenerationRequest
from shared.utils.yaml_loader import load_yaml_fast as load_yaml
from shared.utils.yaml_loader import dump_yaml_fast as save_yaml
from run import API_PROVIDERS
APPLICATIONS_PATH = PROJECT_ROOT / "data" / "applications" / "Applications.yaml"
MATERIALS_PATH = PROJECT_ROOT / "data" / "materials" / "Materials.yaml"
CONTAMINANTS_PATH = PROJECT_ROOT / "data" / "contaminants" / "Contaminants.yaml"
INDUSTRY_GUIDANCE_PATH = PROJECT_ROOT / "data" / "materials" / "IndustryApplications.yaml"


def _require_mapping(data: Dict[str, Any], key: str, path: Path) -> Dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Expected '{key}' mapping in {path}")
    return value


def _require_field(item: Dict[str, Any], field: str, item_id: str, domain: str) -> Any:
    value = item.get(field)
    if value in (None, ""):
        raise KeyError(f"Missing required field '{field}' for {domain} '{item_id}'")
    return value


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _material_name_lookup(materials: Dict[str, Any]) -> Dict[str, str]:
    lookup: Dict[str, str] = {}
    for material_id, material in materials.items():
        if not isinstance(material, dict):
            continue
        name = material.get("name")
        if isinstance(name, str) and name.strip():
            lookup[_normalize_key(name)] = material_id
    return lookup


def _build_material_item(item_id: str, materials: Dict[str, Any]) -> Dict[str, Any]:
    if item_id not in materials:
        raise KeyError(f"Material '{item_id}' not found in Materials.yaml")
    item = materials[item_id]

    name = _require_field(item, "name", item_id, "material")
    category = _require_field(item, "category", item_id, "material")
    subcategory = _require_field(item, "subcategory", item_id, "material")
    url = _require_field(item, "fullPath", item_id, "material")
    images = _require_field(item, "images", item_id, "material")
    hero = images.get("hero") if isinstance(images, dict) else None
    if not isinstance(hero, dict) or not hero.get("url"):
        raise KeyError(f"Missing images.hero.url for material '{item_id}'")
    description = item.get("pageDescription") or item.get("description")
    if not isinstance(description, str) or not description.strip():
        raise KeyError(f"Missing pageDescription/description for material '{item_id}'")

    return {
        "id": item_id,
        "name": name,
        "category": category,
        "subcategory": subcategory,
        "url": url,
        "image": hero["url"],
        "description": description.strip(),
    }


def _build_contaminant_item(item_id: str, contaminants: Dict[str, Any]) -> Dict[str, Any]:
    if item_id not in contaminants:
        raise KeyError(f"Contaminant '{item_id}' not found in Contaminants.yaml")
    item = contaminants[item_id]

    name = _require_field(item, "name", item_id, "contaminant")
    category = _require_field(item, "category", item_id, "contaminant")
    subcategory = _require_field(item, "subcategory", item_id, "contaminant")
    url = _require_field(item, "fullPath", item_id, "contaminant")
    images = _require_field(item, "images", item_id, "contaminant")
    hero = images.get("hero") if isinstance(images, dict) else None
    if not isinstance(hero, dict) or not hero.get("url"):
        raise KeyError(f"Missing images.hero.url for contaminant '{item_id}'")
    description = item.get("pageDescription") or item.get("description")
    if not isinstance(description, str) or not description.strip():
        raise KeyError(f"Missing pageDescription/description for contaminant '{item_id}'")

    return {
        "id": item_id,
        "name": name,
        "category": category,
        "subcategory": subcategory,
        "url": url,
        "image": hero["url"],
        "description": description.strip(),
    }


def _build_relationship_sections(
    materials: Dict[str, Any],
    contaminants: Dict[str, Any],
    material_ids: List[str],
    contaminant_ids: List[str],
) -> Dict[str, Any]:
    related_materials = [_build_material_item(item_id, materials) for item_id in material_ids]
    common_contaminants = [_build_contaminant_item(item_id, contaminants) for item_id in contaminant_ids]

    return {
        "discovery": {
            "relatedMaterials": {
                "presentation": "card",
                "items": related_materials,
                "_section": {
                    "sectionTitle": "Common Materials",
                    "sectionDescription": "Materials most frequently cleaned in this application context.",
                    "icon": "layers",
                    "order": 30,
                    "variant": "default",
                },
            }
        },
        "interactions": {
            "contaminatedBy": {
                "presentation": "card",
                "items": common_contaminants,
                "_section": {
                    "sectionTitle": "Common Contaminants",
                    "sectionDescription": "Contaminants typically removed in these applications.",
                    "icon": "droplet",
                    "order": 31,
                    "variant": "default",
                },
            }
        },
    }


def _build_request(provider: str, prompt: str) -> GenerationRequest:
    if provider not in API_PROVIDERS:
        raise KeyError(f"Provider '{provider}' not found in API_PROVIDERS")
    provider_config = API_PROVIDERS[provider]
    return GenerationRequest(
        prompt=prompt,
        max_tokens=provider_config["max_tokens"],
        temperature=provider_config["temperature"],
    )


def _parse_json(text: str) -> Dict[str, Any]:
    content = text.strip()
    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Response did not contain JSON object")
    return json.loads(content[start : end + 1])


def _choose_industry_key(
    client,
    provider: str,
    app_data: Dict[str, Any],
    guidance_keys: List[str],
) -> str:
    subcategory = app_data.get("subcategory", "")
    name = app_data.get("name", "")
    normalized_subcategory = _normalize_key(str(subcategory)) if subcategory else ""
    normalized_name = _normalize_key(str(name)) if name else ""

    if normalized_subcategory in guidance_keys:
        return normalized_subcategory
    if normalized_name in guidance_keys:
        return normalized_name

    prompt = (
        "You map application pages to the closest industry guidance key. "
        "Choose exactly one key from the list. "
        "Return JSON only: {\"industry_key\": \"<key>\", \"reason\": \"<short>\"}.\n\n"
        f"Application name: {name}\n"
        f"Application subcategory: {subcategory}\n"
        f"Application description: {app_data.get('pageDescription', '')}\n\n"
        f"Industry guidance keys: {', '.join(sorted(guidance_keys))}"
    )

    request = _build_request(provider, prompt)
    response = client.generate(request)
    if not response.success:
        raise RuntimeError(f"Industry key selection failed: {response.error}")
    payload = _parse_json(response.content)
    industry_key = payload.get("industry_key")
    if not isinstance(industry_key, str):
        raise ValueError("Missing industry_key in response")
    industry_key = _normalize_key(industry_key)
    if industry_key not in guidance_keys:
        raise ValueError(f"Invalid industry_key returned: {industry_key}")
    return industry_key


def _select_materials(
    client,
    provider: str,
    app_data: Dict[str, Any],
    industry_key: str,
    industry_data: Dict[str, Any],
    materials_count: int,
    material_ids: List[str],
    materials_lookup: Dict[str, Any],
) -> List[str]:
    if len(material_ids) <= materials_count:
        return material_ids

    materials_summary = []
    for material_id in material_ids:
        material = materials_lookup.get(material_id, {})
        materials_summary.append(
            f"- {material_id} | {material.get('name', '')} | {material.get('category', '')}/{material.get('subcategory', '')}"
        )

    prompt = (
        "Select the most relevant materials for this application. "
        "Choose exactly the requested count from the candidate list. "
        "Return JSON only: {\"material_ids\": [..], \"reason\": \"<short>\"}.\n\n"
        f"Application name: {app_data.get('name', '')}\n"
        f"Application description: {app_data.get('pageDescription', '')}\n"
        f"Industry guidance key: {industry_key}\n"
        f"Typical applications: {', '.join(industry_data.get('typical_applications', []))}\n"
        f"Critical requirements: {', '.join(industry_data.get('critical_requirements', []))}\n"
        f"Requested count: {materials_count}\n\n"
        "Candidate materials:\n"
        + "\n".join(materials_summary)
    )

    request = _build_request(provider, prompt)
    response = client.generate(request)
    if not response.success:
        raise RuntimeError(f"Material selection failed: {response.error}")
    payload = _parse_json(response.content)
    ids = payload.get("material_ids")
    if not isinstance(ids, list):
        raise ValueError("Missing material_ids in response")

    selected = []
    for material_id in ids:
        if not isinstance(material_id, str):
            continue
        if material_id not in material_ids:
            raise ValueError(f"Invalid material id returned: {material_id}")
        if material_id not in selected:
            selected.append(material_id)

    if len(selected) != materials_count:
        raise ValueError("Material selection did not return required count")

    return selected


def _select_contaminants(
    client,
    provider: str,
    app_data: Dict[str, Any],
    industry_key: str,
    industry_data: Dict[str, Any],
    contaminants_count: int,
    contaminant_candidates: List[Dict[str, Any]],
) -> List[str]:
    if len(contaminant_candidates) <= contaminants_count:
        return [c["id"] for c in contaminant_candidates]

    contaminant_lines = []
    for contaminant in contaminant_candidates:
        contaminant_lines.append(
            f"- {contaminant['id']} | {contaminant['name']} | {contaminant['category']}/{contaminant['subcategory']} | matches={contaminant['match_count']}"
        )

    prompt = (
        "Select the most relevant contaminants for this application. "
        "Choose exactly the requested count from the candidate list. "
        "Return JSON only: {\"contaminant_ids\": [..], \"reason\": \"<short>\"}.\n\n"
        f"Application name: {app_data.get('name', '')}\n"
        f"Application description: {app_data.get('pageDescription', '')}\n"
        f"Industry guidance key: {industry_key}\n"
        f"Typical applications: {', '.join(industry_data.get('typical_applications', []))}\n"
        f"Critical requirements: {', '.join(industry_data.get('critical_requirements', []))}\n"
        f"Requested count: {contaminants_count}\n\n"
        "Candidate contaminants:\n"
        + "\n".join(contaminant_lines)
    )

    request = _build_request(provider, prompt)
    response = client.generate(request)
    if not response.success:
        raise RuntimeError(f"Contaminant selection failed: {response.error}")
    payload = _parse_json(response.content)
    ids = payload.get("contaminant_ids")
    if not isinstance(ids, list):
        raise ValueError("Missing contaminant_ids in response")

    candidate_ids = {c["id"] for c in contaminant_candidates}
    selected: List[str] = []
    for contaminant_id in ids:
        if not isinstance(contaminant_id, str):
            continue
        if contaminant_id not in candidate_ids:
            raise ValueError(f"Invalid contaminant id returned: {contaminant_id}")
        if contaminant_id not in selected:
            selected.append(contaminant_id)

    if len(selected) != contaminants_count:
        raise ValueError("Contaminant selection did not return required count")

    return selected


def _build_contaminant_candidates(
    contaminants: Dict[str, Any],
    material_ids: List[str],
    max_candidates: int,
) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    for contaminant_id, contaminant in contaminants.items():
        if not isinstance(contaminant, dict):
            continue
        valid_materials = contaminant.get("validMaterials")
        if not isinstance(valid_materials, list):
            continue
        match_count = sum(1 for material_id in material_ids if material_id in valid_materials)
        if match_count == 0:
            continue
        candidates.append(
            {
                "id": contaminant_id,
                "name": contaminant.get("name", ""),
                "category": contaminant.get("category", ""),
                "subcategory": contaminant.get("subcategory", ""),
                "match_count": match_count,
            }
        )

    candidates.sort(key=lambda item: (-item["match_count"], item["name"]))
    return candidates[:max_candidates]


def _audit_relationships(application_id: str, current: Dict[str, Any], proposed: Dict[str, Any]) -> None:
    current_materials = {
        item.get("id")
        for item in current.get("discovery", {}).get("relatedMaterials", {}).get("items", [])
        if isinstance(item, dict)
    }
    current_contaminants = {
        item.get("id")
        for item in current.get("interactions", {}).get("contaminatedBy", {}).get("items", [])
        if isinstance(item, dict)
    }
    proposed_materials = {
        item.get("id")
        for item in proposed.get("discovery", {}).get("relatedMaterials", {}).get("items", [])
        if isinstance(item, dict)
    }
    proposed_contaminants = {
        item.get("id")
        for item in proposed.get("interactions", {}).get("contaminatedBy", {}).get("items", [])
        if isinstance(item, dict)
    }

    if current_materials or current_contaminants:
        print(f"\n🔎 Audit: {application_id}")
        removed_materials = sorted(current_materials - proposed_materials)
        added_materials = sorted(proposed_materials - current_materials)
        removed_contaminants = sorted(current_contaminants - proposed_contaminants)
        added_contaminants = sorted(proposed_contaminants - current_contaminants)

        if added_materials:
            print(f"   + materials: {', '.join(added_materials)}")
        if removed_materials:
            print(f"   - materials: {', '.join(removed_materials)}")
        if added_contaminants:
            print(f"   + contaminants: {', '.join(added_contaminants)}")
        if removed_contaminants:
            print(f"   - contaminants: {', '.join(removed_contaminants)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="AI-research application relationships")
    parser.add_argument("--item", action="append", dest="items", help="Application id to update")
    parser.add_argument("--all", action="store_true", help="Update all applications")
    parser.add_argument("--provider", required=True, help="API provider id (e.g., grok)")
    parser.add_argument("--materials-count", type=int, required=True, help="Number of materials to select")
    parser.add_argument("--contaminants-count", type=int, required=True, help="Number of contaminants to select")
    parser.add_argument("--max-contaminant-candidates", type=int, required=True, help="Max contaminant candidates for AI")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    if not args.all and not args.items:
        raise SystemExit("Specify --item <id> or --all")

    applications_data = load_yaml(APPLICATIONS_PATH)
    materials_data = load_yaml(MATERIALS_PATH)
    contaminants_data = load_yaml(CONTAMINANTS_PATH)
    industry_data = load_yaml(INDUSTRY_GUIDANCE_PATH)

    applications = _require_mapping(applications_data, "applications", APPLICATIONS_PATH)
    materials = _require_mapping(materials_data, "materials", MATERIALS_PATH)
    contaminants = _require_mapping(contaminants_data, "contaminants", CONTAMINANTS_PATH)
    industry_guidance = _require_mapping(industry_data, "industryGuidance", INDUSTRY_GUIDANCE_PATH)

    guidance_keys = sorted(industry_guidance.keys())
    material_lookup = _material_name_lookup(materials)

    client = create_api_client(args.provider)

    if args.all:
        targets = list(applications.keys())
    else:
        targets = args.items

    for application_id in targets:
        if application_id not in applications:
            raise KeyError(f"Application '{application_id}' not found in Applications.yaml")

        app_data = applications[application_id]
        if not isinstance(app_data, dict):
            raise ValueError(f"Application '{application_id}' data must be a mapping")

        print(f"\n{'=' * 80}")
        print(f"Researching relationships for {application_id}")
        print(f"{'=' * 80}")

        industry_key = _choose_industry_key(client, args.provider, app_data, guidance_keys)
        industry_info = industry_guidance[industry_key]

        typical_materials = industry_info.get("typical_materials", [])
        if not isinstance(typical_materials, list) or not typical_materials:
            raise ValueError(f"industryGuidance.{industry_key}.typical_materials missing")

        material_ids: List[str] = []
        for material_name in typical_materials:
            if not isinstance(material_name, str):
                continue
            material_id = material_lookup.get(_normalize_key(material_name))
            if material_id:
                material_ids.append(material_id)

        if not material_ids:
            raise ValueError(f"No materials resolved for {application_id} from {industry_key}")

        material_ids = _select_materials(
            client,
            args.provider,
            app_data,
            industry_key,
            industry_info,
            args.materials_count,
            material_ids,
            materials,
        )

        contaminant_candidates = _build_contaminant_candidates(
            contaminants,
            material_ids,
            args.max_contaminant_candidates,
        )
        if not contaminant_candidates:
            raise ValueError(f"No contaminant candidates found for {application_id}")

        contaminant_ids = _select_contaminants(
            client,
            args.provider,
            app_data,
            industry_key,
            industry_info,
            args.contaminants_count,
            contaminant_candidates,
        )

        relationships = _build_relationship_sections(materials, contaminants, material_ids, contaminant_ids)
        _audit_relationships(application_id, app_data.get("relationships", {}), relationships)

        if not args.dry_run:
            app_data["relationships"] = relationships
            print(f"✅ Updated relationships for {application_id}")
        else:
            print(f"🔍 Dry run: relationships prepared for {application_id}")

    if args.dry_run:
        print("\nDry run complete: no changes written")
        return

    save_yaml(applications_data, APPLICATIONS_PATH)
    print(f"\n✅ Saved updates to {APPLICATIONS_PATH}")


if __name__ == "__main__":
    main()
