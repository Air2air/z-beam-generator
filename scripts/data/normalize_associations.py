#!/usr/bin/env python3
"""
Normalize DomainAssociations.yaml and populate missing compound byproduct data.

Actions:
  1. Strip '-laser-cleaning' suffix from material source_ids/target_ids in flat list
  2. Strip '-compound' suffix from compound source_ids/target_ids in flat list
  3. Add generates_byproduct + byproduct_of associations for known laser cleaning chemistry
  4. Update metadata breakdown and total
  5. Rebuild lookup indexes from normalized flat list

Run from project root:
  python3 scripts/data/normalize_associations.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# Known laser-cleaning byproduct chemistry
# contaminant_id (full, with -contamination) → list of compound bare IDs
# ---------------------------------------------------------------------------
CONTAMINANT_TO_COMPOUNDS: dict[str, list[str]] = {
    # Carbon-based
    "carbon-buildup-contamination": [
        "carbon-monoxide", "carbon-dioxide", "carbon-particulates", "carbon-ash"
    ],
    "carbon-soot-contamination": [
        "carbon-monoxide", "carbon-dioxide", "carbon-particulates"
    ],
    # Organic residues (oils, greases)
    "industrial-oil-contamination": [
        "carbon-monoxide", "carbon-dioxide", "formaldehyde", "acrolein"
    ],
    "quench-oil-contamination": [
        "carbon-monoxide", "carbon-dioxide", "formaldehyde", "acrolein"
    ],
    "grease-oil-contamination": [
        "carbon-monoxide", "carbon-dioxide", "formaldehyde", "acrolein", "pahs"
    ],
    # Adhesives, coatings, paints
    "adhesive-residue-contamination": [
        "carbon-monoxide", "formaldehyde", "benzene"
    ],
    "paint-residue-contamination": [
        "benzene", "toluene", "formaldehyde", "hydrogen-chloride", "pahs"
    ],
    "uv-chalking-contamination": [
        "formaldehyde", "carbon-monoxide", "carbon-dioxide"
    ],
    # Plastics and rubber
    "plastic-residue-contamination": [
        "hydrogen-chloride", "benzene", "styrene", "formaldehyde"
    ],
    "rubber-residue-contamination": [
        "benzene", "formaldehyde", "carbon-monoxide", "carbon-dioxide"
    ],
    # Biological
    "biological-contamination": [
        "carbon-monoxide", "carbon-dioxide", "formaldehyde"
    ],
    "fungal-contamination": [
        "carbon-monoxide", "carbon-dioxide", "formaldehyde"
    ],
    "mold-mildew-contamination": [
        "carbon-monoxide", "carbon-dioxide", "formaldehyde"
    ],
    # Chemical residues
    "flux-residue-contamination": [
        "hydrogen-chloride", "formaldehyde", "benzene", "pahs"
    ],
    "chemical-stains-contamination": [
        "hydrogen-chloride", "formaldehyde", "carbon-dioxide"
    ],
    "solvent-residue-contamination": [
        "benzene", "toluene", "formaldehyde", "carbon-monoxide"
    ],
    "medical-disinfectant-contamination": [
        "formaldehyde", "benzene", "hydrogen-chloride"
    ],
    # Fire / thermal damage
    "fire-damage-contamination": [
        "carbon-monoxide", "carbon-dioxide", "pahs", "carbon-particulates", "carbon-ash"
    ],
    "heat-discoloration-contamination": [
        "carbon-monoxide", "carbon-dioxide", "carbon-particulates"
    ],
    # Other organic
    "food-contamination": [
        "carbon-monoxide", "carbon-dioxide", "formaldehyde", "acrolein"
    ],
    "organic-residue-contamination": [
        "carbon-monoxide", "carbon-dioxide", "formaldehyde"
    ],
}


def strip_material_suffix(material_id: str) -> str:
    """Strip -laser-cleaning suffix from material IDs."""
    if material_id.endswith("-laser-cleaning"):
        return material_id[: -len("-laser-cleaning")]
    return material_id


def strip_compound_suffix(compound_id: str) -> str:
    """Strip -compound suffix from compound IDs."""
    if compound_id.endswith("-compound"):
        return compound_id[: -len("-compound")]
    return compound_id


def normalize_association(assoc: dict) -> dict:
    """Normalize an association's IDs based on domain."""
    out = dict(assoc)
    if out.get("source_domain") == "materials":
        out["source_id"] = strip_material_suffix(out.get("source_id", ""))
    elif out.get("source_domain") == "compounds":
        out["source_id"] = strip_compound_suffix(out.get("source_id", ""))

    if out.get("target_domain") == "materials":
        out["target_id"] = strip_material_suffix(out.get("target_id", ""))
    elif out.get("target_domain") == "compounds":
        out["target_id"] = strip_compound_suffix(out.get("target_id", ""))
    return out


def build_byproduct_associations(
    valid_contaminant_ids: set[str],
    valid_compound_bare_ids: set[str],
) -> list[dict]:
    """Build generates_byproduct + byproduct_of association pairs."""
    forward: list[dict] = []  # contaminant → compound (generates_byproduct)
    reverse: list[dict] = []  # compound → contaminant (byproduct_of)

    seen_forward: set[tuple[str, str]] = set()

    for contaminant_id, compound_list in CONTAMINANT_TO_COMPOUNDS.items():
        # Skip contaminants not in the actual data
        if contaminant_id not in valid_contaminant_ids:
            continue

        for compound_bare in compound_list:
            if compound_bare not in valid_compound_bare_ids:
                continue
            pair = (contaminant_id, compound_bare)
            if pair in seen_forward:
                continue
            seen_forward.add(pair)

            forward.append({
                "source_domain": "contaminants",
                "source_id": contaminant_id,
                "target_domain": "compounds",
                "target_id": compound_bare,
                "relationship_type": "generates_byproduct",
                "verified": True,
                "verification_source": "chemistry:laser_cleaning_byproducts",
            })
            reverse.append({
                "source_domain": "compounds",
                "source_id": compound_bare,
                "target_domain": "contaminants",
                "target_id": contaminant_id,
                "relationship_type": "byproduct_of",
                "verified": True,
                "verification_source": "chemistry:laser_cleaning_byproducts",
            })

    return forward + reverse


def rebuild_indexes(associations: list[dict]) -> dict:
    """Rebuild all lookup index dictionaries from normalized flat list."""
    m2c: dict[str, list[str]] = defaultdict(list)   # material (bare) → [contaminant_ids]
    c2m: dict[str, list[str]] = defaultdict(list)   # contaminant_id → [material_bare_ids]

    seen_m2c: dict[str, set[str]] = defaultdict(set)
    seen_c2m: dict[str, set[str]] = defaultdict(set)

    for a in associations:
        rt = a.get("relationship_type")
        src = a.get("source_id", "")
        tgt = a.get("target_id", "")

        if rt == "can_have_contamination":
            # src = material (bare), tgt = contaminant
            if tgt not in seen_m2c[src]:
                seen_m2c[src].add(tgt)
                m2c[src].append(tgt)
        elif rt == "can_contaminate":
            # src = contaminant, tgt = material (bare)
            if tgt not in seen_c2m[src]:
                seen_c2m[src].add(tgt)
                c2m[src].append(tgt)

    return {
        "material_to_contaminant": dict(m2c),
        "material_to_compound": {},         # not yet populated
        "material_to_setting": {},           # not yet populated
        "contaminant_to_material": dict(c2m),
        "compound_to_material": {},          # not yet populated
        "setting_to_material": {},           # not yet populated
    }


def main() -> None:
    assoc_file = PROJECT_ROOT / "data" / "associations" / "DomainAssociations.yaml"
    contaminants_file = PROJECT_ROOT / "data" / "contaminants" / "Contaminants.yaml"
    compounds_file = PROJECT_ROOT / "data" / "compounds" / "Compounds.yaml"

    print("Loading files...")
    with open(assoc_file) as f:
        data = yaml.safe_load(f)
    with open(contaminants_file) as f:
        contaminants_data = yaml.safe_load(f)
    with open(compounds_file) as f:
        compounds_data = yaml.safe_load(f)

    valid_contaminant_ids: set[str] = set(contaminants_data["contaminants"].keys())
    # Compound bare IDs = strip '-compound' suffix from keys
    valid_compound_bare_ids: set[str] = {
        strip_compound_suffix(k) for k in compounds_data["compounds"].keys()
    }

    print(f"  {len(valid_contaminant_ids)} contaminants loaded")
    print(f"  {len(valid_compound_bare_ids)} compound bare IDs loaded")

    # 1. Normalize existing flat associations
    print("Normalizing flat associations list...")
    original_count = len(data["associations"])
    normalized = [normalize_association(a) for a in data["associations"]]
    
    # Deduplicate after normalization (some laser-cleaning IDs may overlap)
    seen: set[tuple] = set()
    deduped: list[dict] = []
    for a in normalized:
        key = (
            a.get("source_id"), a.get("target_id"),
            a.get("relationship_type"), a.get("source_domain"), a.get("target_domain")
        )
        if key not in seen:
            seen.add(key)
            deduped.append(a)
    print(f"  {original_count} → {len(deduped)} after normalize+dedup")

    # 2. Remove old duplicate entries with -laser-cleaning suffix that the
    #    original file had alongside their normalized counterparts
    cleaned = [
        a for a in deduped
        if not (
            a.get("source_id", "").endswith("-laser-cleaning") or
            a.get("target_id", "").endswith("-laser-cleaning") or
            a.get("source_id", "").endswith("-compound") or
            a.get("target_id", "").endswith("-compound")
        )
    ]
    print(f"  {len(cleaned)} after removing residual suffixed entries")

    # 3. Add byproduct associations
    print("Building compound byproduct associations...")
    byproducts = build_byproduct_associations(valid_contaminant_ids, valid_compound_bare_ids)
    fwd = [b for b in byproducts if b["relationship_type"] == "generates_byproduct"]
    rev = [b for b in byproducts if b["relationship_type"] == "byproduct_of"]
    print(f"  {len(fwd)} generates_byproduct + {len(rev)} byproduct_of associations")

    final_associations = cleaned + byproducts

    # 4. Count by type
    mat_cont = sum(1 for a in final_associations if a["relationship_type"] == "can_have_contamination")
    cont_mat = sum(1 for a in final_associations if a["relationship_type"] == "can_contaminate")
    cont_comp = sum(1 for a in final_associations if a["relationship_type"] == "generates_byproduct")
    comp_cont = sum(1 for a in final_associations if a["relationship_type"] == "byproduct_of")
    total = mat_cont + cont_mat + cont_comp + comp_cont
    breakdown = f"{mat_cont}+{cont_mat}+{cont_comp}+{comp_cont}"
    print(f"\nAssociation counts: {breakdown} = {total}")

    # 5. Update metadata
    data["metadata"]["total_associations"] = total
    data["metadata"]["breakdown"] = breakdown

    # 6. Rebuild indexes
    print("Rebuilding lookup indexes...")
    indexes = rebuild_indexes(final_associations)
    for key, val in indexes.items():
        if isinstance(val, dict):
            print(f"  {key}: {len(val)} entries")

    # 7. Assemble output (drop unused material_to_contaminants plural form)
    out = {
        "metadata": data["metadata"],
        "associations": final_associations,
    }
    out.update(indexes)

    # 8. Write back
    print(f"\nWriting {assoc_file} ...")
    with open(assoc_file, "w") as f:
        yaml.dump(out, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print("Done.")


if __name__ == "__main__":
    main()
