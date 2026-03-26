#!/usr/bin/env python3
"""
Populate Related Items — unified batch relationship matcher.

Uses shared/matching/entity_matcher.py to score and write cross-domain
relationship slugs into source YAML files.  Covers all relationship types:

  - Host=materials/contaminants/compounds/applications → Target=videos
  - Host=videos → Target=materials/contaminants/compounds/applications
  - Any other valid host→target pair (materials↔contaminants, etc.)

Relationship key written under host item's `relationships` block.

Usage
-----
  # Populate relatedVideos for ALL materials:
  python3 scripts/research/populate_related_items.py \\
      --host materials --target videos \\
      --rel-key relationships.discovery.relatedVideos \\
      --all

  # Populate relatedVideos for a single material:
  python3 scripts/research/populate_related_items.py \\
      --host materials --target videos \\
      --rel-key relationships.discovery.relatedVideos \\
      --items steel-laser-cleaning aluminum-laser-cleaning

  # Populate relatedMaterials for ALL contaminants:
  python3 scripts/research/populate_related_items.py \\
      --host contaminants --target materials \\
      --rel-key relationships.discovery.relatedMaterials \\
      --all

  # Dry-run preview (no writes):
  python3 scripts/research/populate_related_items.py \\
      --host materials --target videos \\
      --rel-key relationships.discovery.relatedVideos \\
      --all --dry-run

  # Skip items that already have the key populated:
  python3 scripts/research/populate_related_items.py \\
      --host materials --target videos \\
      --rel-key relationships.discovery.relatedVideos \\
      --all --skip-existing

Flags
-----
  --min-score FLOAT   Minimum match score (default 8.0).
  --max-results INT   Max related items per host item (default 3).
  --force             Overwrite existing relationship data.
  --dry-run           Print matches without writing.
  --skip-existing     Skip host items that already have the rel-key.
  --video-dir PATH    Path to video frontmatter YAMLs
                      (default: ../z-beam/frontmatter/videos relative to project root).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from shared.matching.entity_matcher import (
    CandidateEntity,
    EntityMatcher,
    HostEntity,
    MatchConfig,
)
from shared.utils.yaml_utils import load_yaml_fast as load_yaml, dump_yaml_fast as save_yaml

# ---------------------------------------------------------------------------
# Domain config — maps domain name → (source file, items key, keywords field)
# ---------------------------------------------------------------------------

DOMAIN_CONFIG: Dict[str, Dict[str, str]] = {
    "materials": {
        "source_file": "data/materials/Materials.yaml",
        "items_key": "materials",
        "name_field": "name",
        "keywords_field": "keywords",
    },
    "contaminants": {
        "source_file": "data/contaminants/Contaminants.yaml",
        "items_key": "contaminants",
        "name_field": "name",
        "keywords_field": "keywords",
    },
    "compounds": {
        "source_file": "data/compounds/Compounds.yaml",
        "items_key": "compounds",
        "name_field": "name",
        "keywords_field": "keywords",
    },
    "applications": {
        "source_file": "data/applications/Applications.yaml",
        "items_key": "applications",
        "name_field": "name",
        "keywords_field": "keywords",
    },
}

# Videos live in the frontend repo's frontmatter directory
DEFAULT_VIDEO_DIR = PROJECT_ROOT.parent / "z-beam" / "frontmatter" / "videos"


# ---------------------------------------------------------------------------
# Entity loaders
# ---------------------------------------------------------------------------

def _extract_association_slugs(item: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Pull authored association slug lists from a source YAML item.

    Checks both the conventions used in domain source YAMLs:
      - relationships.discovery.relatedMaterials → items[].id
      - relationships.interactions.contaminatedBy → items[].id
      - associations.related_materials → items[] (plain slugs in videos frontmatter)
    """
    result: Dict[str, List[str]] = {
        "materials": [],
        "contaminants": [],
        "compounds": [],
        "applications": [],
        "videos": [],
    }

    # Pattern 1: domain source YAML relationships block
    relationships = item.get("relationships", {})
    discovery = relationships.get("discovery", {})
    interactions = relationships.get("interactions", {})

    for section in [discovery, interactions]:
        for key, data in section.items():
            if not isinstance(data, dict):
                continue
            items = data.get("items", [])
            if not isinstance(items, list):
                continue
            # Map relationship key → domain
            if "material" in key.lower():
                for it in items:
                    slug = it.get("id") if isinstance(it, dict) else None
                    if slug:
                        result["materials"].append(slug)
            elif "contaminant" in key.lower() or "contaminatedby" in key.lower():
                for it in items:
                    slug = it.get("id") if isinstance(it, dict) else None
                    if slug:
                        result["contaminants"].append(slug)
            elif "compound" in key.lower():
                for it in items:
                    slug = it.get("id") if isinstance(it, dict) else None
                    if slug:
                        result["compounds"].append(slug)
            elif "application" in key.lower():
                for it in items:
                    slug = it.get("id") if isinstance(it, dict) else None
                    if slug:
                        result["applications"].append(slug)
            elif "video" in key.lower():
                for it in items:
                    slug = it if isinstance(it, str) else it.get("id") if isinstance(it, dict) else None
                    if slug:
                        result["videos"].append(slug)

    # Pattern 2: video frontmatter associations block (plain slug lists)
    associations = item.get("associations", {})
    for key, data in associations.items():
        if not isinstance(data, dict):
            continue
        items_list = data.get("items", [])
        if not isinstance(items_list, list):
            continue
        if "material" in key:
            result["materials"].extend(s for s in items_list if isinstance(s, str))
        elif "contaminant" in key:
            result["contaminants"].extend(s for s in items_list if isinstance(s, str))
        elif "compound" in key:
            result["compounds"].extend(s for s in items_list if isinstance(s, str))
        elif "application" in key:
            result["applications"].extend(s for s in items_list if isinstance(s, str))
        elif "video" in key:
            result["videos"].extend(s for s in items_list if isinstance(s, str))

    # Deduplicate
    return {k: list(dict.fromkeys(v)) for k, v in result.items()}


def load_domain_entities(
    domain: str, item_ids: Optional[List[str]] = None
) -> List[HostEntity]:
    """Load domain source items as HostEntity objects."""
    if domain == "videos":
        raise ValueError("Use load_video_entities() to load video entities as hosts.")

    cfg = DOMAIN_CONFIG[domain]
    source = PROJECT_ROOT / cfg["source_file"]
    data = load_yaml(str(source))
    items: Dict[str, Any] = data[cfg["items_key"]]

    entities = []
    for item_id, item in items.items():
        if not isinstance(item, dict):
            continue
        if item_ids and item_id not in item_ids:
            continue
        slug = item.get("id") or item_id
        entities.append(
            HostEntity(
                slug=slug,
                domain=domain,
                subject=item.get(cfg["name_field"], ""),
                page_title=item.get("pageTitle", item.get("displayName", item.get("name", ""))),
                page_description=item.get("pageDescription", ""),
                keywords=item.get("keywords", []) or [],
                category=item.get("category", ""),
                subcategory=item.get("subcategory", ""),
                association_slugs=_extract_association_slugs(item),
            )
        )
    return entities


def load_video_entities(video_dir: Path) -> List[CandidateEntity]:
    """Load video frontmatter files as CandidateEntity objects."""
    if not video_dir.exists():
        raise FileNotFoundError(f"Video directory not found: {video_dir}")

    entities = []
    for yaml_file in sorted(video_dir.glob("*.yaml")):
        try:
            item = load_yaml(str(yaml_file))
        except Exception as exc:
            print(f"  ⚠️  Skipping {yaml_file.name}: {exc}")
            continue
        if not isinstance(item, dict):
            continue
        slug = item.get("slug", yaml_file.stem)
        entities.append(
            CandidateEntity(
                slug=slug,
                domain="videos",
                subject=item.get("subject", ""),
                page_title=item.get("pageTitle", ""),
                page_description=item.get("pageDescription", ""),
                keywords=item.get("keywords", []) or [],
                authored_associations=_extract_association_slugs(item),
            )
        )
    return entities


def load_candidate_entities(domain: str, video_dir: Path) -> List[CandidateEntity]:
    """Load candidates of any domain as CandidateEntity objects."""
    if domain == "videos":
        return load_video_entities(video_dir)

    cfg = DOMAIN_CONFIG[domain]
    source = PROJECT_ROOT / cfg["source_file"]
    data = load_yaml(str(source))
    items: Dict[str, Any] = data[cfg["items_key"]]

    entities = []
    for item_id, item in items.items():
        if not isinstance(item, dict):
            continue
        slug = item.get("id") or item_id
        entities.append(
            CandidateEntity(
                slug=slug,
                domain=domain,
                subject=item.get(cfg["name_field"], ""),
                page_title=item.get("pageTitle", item.get("displayName", item.get("name", ""))),
                page_description=item.get("pageDescription", ""),
                keywords=item.get("keywords", []) or [],
                category=item.get("category", ""),
                subcategory=item.get("subcategory", ""),
                authored_associations=_extract_association_slugs(item),
            )
        )
    return entities


# ---------------------------------------------------------------------------
# Relationship key writer
# ---------------------------------------------------------------------------

def _get_nested(data: Dict, keys: List[str]) -> Any:
    """Navigate nested dict using a list of keys, returning None if missing."""
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _set_nested(data: Dict, keys: List[str], value: Any) -> None:
    """Set a nested dict value, creating intermediate dicts as needed."""
    current = data
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value


def key_exists_and_populated(item: Dict[str, Any], rel_key: str) -> bool:
    """Return True if rel_key already has at least one item slug."""
    keys = rel_key.split(".")
    node = _get_nested(item, keys)
    if not isinstance(node, dict):
        return False
    items = node.get("items", [])
    return isinstance(items, list) and len(items) > 0


# ---------------------------------------------------------------------------
# Slug hydration
# ---------------------------------------------------------------------------

def _hydrate_slug(slug: str, domain: str, items_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a full relationship object for a single slug from its domain source data.

    Mirrors the builder pattern in scripts/research/research_application_relationships.py
    (see _build_material_item / _build_contaminant_item), extended generically to all
    DOMAIN_CONFIG domains.

    Raises KeyError if required fields are missing — intentional fail-fast per project policy.
    """
    if slug not in items_dict:
        raise KeyError(f"{domain} slug '{slug}' not found in source data")
    item = items_dict[slug]
    if not isinstance(item, dict):
        raise KeyError(f"{domain} slug '{slug}' has invalid source data entry")

    name = item.get("name")
    if not name:
        raise KeyError(f"Missing 'name' for {domain} '{slug}'")
    category = item.get("category")
    if not category:
        raise KeyError(f"Missing 'category' for {domain} '{slug}'")
    subcategory = item.get("subcategory", "")
    url = item.get("fullPath")
    if not url:
        raise KeyError(f"Missing 'fullPath' for {domain} '{slug}'")
    images = item.get("images", {})
    hero = images.get("hero") if isinstance(images, dict) else None
    if not isinstance(hero, dict) or not hero.get("url"):
        raise KeyError(f"Missing images.hero.url for {domain} '{slug}'")
    description = item.get("pageDescription") or item.get("description")
    if not isinstance(description, str) or not description.strip():
        raise KeyError(f"Missing pageDescription/description for {domain} '{slug}'")

    return {
        "id": slug,
        "name": name,
        "category": category,
        "subcategory": subcategory,
        "url": url,
        "image": hero["url"],
        "description": description.strip(),
    }


def write_relationship(
    item: Dict[str, Any],
    rel_key: str,
    matched_items: List[Any],
    target_domain: str,
) -> None:
    """
    Write matched_items into item under rel_key.

    matched_items is either:
      - a list of slug strings  (output_mode='slugs', e.g. videos)
      - a list of full dicts    (output_mode='full-objects', other domains)

    The value shape is:
        _section:
          sectionTitle: ...
          icon: ...
        items: [...]  (slugs or dicts)
    """
    keys = rel_key.split(".")
    _SECTION_DEFAULTS: Dict[str, Dict[str, str]] = {
        "videos": {
            "sectionTitle": "Related Videos",
            "sectionDescription": "Subject-related laser cleaning video demonstrations from the Z-Beam channel.",
            "icon": "video",
        },
        "materials": {
            "sectionTitle": "Related Materials",
            "sectionDescription": "Materials most relevant to this page topic.",
            "icon": "layers",
        },
        "contaminants": {
            "sectionTitle": "Related Contaminants",
            "sectionDescription": "Contaminants most relevant to this page topic.",
            "icon": "droplet",
        },
        "compounds": {
            "sectionTitle": "Related Compounds",
            "sectionDescription": "Chemical compounds relevant to this page topic.",
            "icon": "flask-conical",
        },
        "applications": {
            "sectionTitle": "Related Applications",
            "sectionDescription": "Application areas relevant to this page topic.",
            "icon": "briefcase",
        },
    }
    section = _SECTION_DEFAULTS.get(target_domain, {"sectionTitle": "Related Items", "icon": "link"})
    _set_nested(item, keys, {"_section": section, "items": matched_items})


# ---------------------------------------------------------------------------
# Main matching loop
# ---------------------------------------------------------------------------

def run(
    host_domain: str,
    target_domain: str,
    rel_key: str,
    item_ids: Optional[List[str]],
    config: MatchConfig,
    dry_run: bool,
    skip_existing: bool,
    force: bool,
    video_dir: Path,
    output_mode: str,
) -> None:
    print(f"\n🔍 populate_related_items")
    print(f"   Host domain  : {host_domain}")
    print(f"   Target domain: {target_domain}")
    print(f"   Rel key      : {rel_key}")
    print(f"   Min score    : {config.min_score}  Max results: {config.max_results}")
    print(f"   Output mode  : {output_mode}")
    print(f"   Mode         : {'DRY-RUN' if dry_run else 'WRITE'}")

    # Load host entities
    print(f"\n📂 Loading {host_domain} source data...")
    host_entities = load_domain_entities(host_domain, item_ids)
    print(f"   Loaded {len(host_entities)} host entities")

    # Load candidate entities
    print(f"📂 Loading {target_domain} candidates...")
    candidates = load_candidate_entities(target_domain, video_dir)
    print(f"   Loaded {len(candidates)} candidates")

    if not host_entities:
        print("⚠️  No host entities to process.")
        return
    if not candidates:
        print("⚠️  No candidates found.")
        return

    matcher = EntityMatcher()

    # Load source YAML for write-back (only needed for non-video hosts)
    cfg = DOMAIN_CONFIG[host_domain]
    source_path = PROJECT_ROOT / cfg["source_file"]
    source_data = load_yaml(str(source_path))
    items_dict: Dict[str, Any] = source_data[cfg["items_key"]]

    # Load target items dict for full-object hydration
    target_items_dict: Optional[Dict[str, Any]] = None
    if output_mode == "full-objects" and target_domain != "videos":
        target_cfg = DOMAIN_CONFIG[target_domain]
        target_source = PROJECT_ROOT / target_cfg["source_file"]
        target_data = load_yaml(str(target_source))
        target_items_dict = target_data[target_cfg["items_key"]]
        print(f"📂 Loaded target source data for hydration ({target_domain})")

    matched_count = 0
    empty_count = 0
    skipped_count = 0

    for host in host_entities:
        # Find the raw item in source data
        raw_item = items_dict.get(host.slug)
        if raw_item is None:
            # Try matching by slug stored inside item
            raw_item = next(
                (v for v in items_dict.values() if isinstance(v, dict) and v.get("id") == host.slug),
                None,
            )
        if not isinstance(raw_item, dict):
            print(f"  ⚠️  {host.slug}: not found in source data, skipping")
            continue

        # Skip if already populated (unless --force)
        if not force and skip_existing and key_exists_and_populated(raw_item, rel_key):
            skipped_count += 1
            continue

        # Run matching
        ranked = matcher.rank_candidates(host, candidates, config)
        slugs = [slug for slug, _score, _diag in ranked]

        # Hydrate to full objects if required
        if output_mode == "full-objects" and target_items_dict is not None:
            matched_items: List[Any] = []
            for slug in slugs:
                try:
                    matched_items.append(_hydrate_slug(slug, target_domain, target_items_dict))
                except KeyError as exc:
                    print(f"  ⚠️  {host.slug}: hydration failed for '{slug}': {exc}")
        else:
            matched_items = slugs  # plain slug strings (videos)

        if matched_items:
            matched_count += 1
            if not dry_run:
                write_relationship(raw_item, rel_key, matched_items, target_domain)
            diag_line = ", ".join(
                f"{s} ({sc:.1f})" for s, sc, _ in ranked
            )
            print(f"  ✅ {host.slug}: {diag_line}")
        else:
            empty_count += 1
            if not dry_run:
                # Write empty list so the key exists (prevents re-running forever)
                write_relationship(raw_item, rel_key, [], target_domain)
            print(f"  ○  {host.slug}: no match")

    # Write back if not dry-run
    if not dry_run:
        save_yaml(str(source_path), source_data)
        print(f"\n💾 Saved → {source_path}")

    print(
        f"\n📊 Summary: {matched_count} matched, {empty_count} no-match, "
        f"{skipped_count} skipped, {len(host_entities)} total"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

VALID_DOMAINS = list(DOMAIN_CONFIG.keys()) + ["videos"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--host",
        required=True,
        choices=VALID_DOMAINS,
        help="Domain of the pages being annotated.",
    )
    parser.add_argument(
        "--target",
        required=True,
        choices=VALID_DOMAINS,
        help="Domain of the related items to find.",
    )
    parser.add_argument(
        "--rel-key",
        required=True,
        metavar="DOT.PATH",
        help="Dot-separated path to write results into host item, e.g. relationships.discovery.relatedVideos",
    )

    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--all", action="store_true", help="Process all host items.")
    scope.add_argument(
        "--items",
        nargs="+",
        metavar="SLUG",
        help="Process specific host item slugs only.",
    )

    parser.add_argument("--min-score", type=float, default=8.0)
    parser.add_argument("--max-results", type=int, default=3)
    parser.add_argument(
        "--dry-run", action="store_true", help="Print matches without writing."
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip host items that already have a non-empty rel-key.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing relationship data (ignored if --skip-existing).",
    )
    parser.add_argument(
        "--video-dir",
        type=Path,
        default=DEFAULT_VIDEO_DIR,
        help="Path to video frontmatter YAML directory.",
    )
    parser.add_argument(
        "--output-mode",
        choices=["slugs", "full-objects"],
        default=None,
        help=(
            "Shape of written items. 'slugs' writes a list of strings; "
            "'full-objects' writes fully hydrated dicts {id,name,category,subcategory,url,image,description}. "
            "Default: 'slugs' when target=videos, 'full-objects' otherwise."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.host == "videos":
        print("Error: --host videos is not yet supported (video source data is read-only frontmatter).")
        sys.exit(1)

    if args.target == args.host:
        print("Error: --host and --target must be different domains.")
        sys.exit(1)

    # Auto-infer output mode: plain slugs for videos, full objects for structural domains
    output_mode = args.output_mode
    if output_mode is None:
        output_mode = "slugs" if args.target == "videos" else "full-objects"

    config = MatchConfig(min_score=args.min_score, max_results=args.max_results)
    item_ids = None if args.all else args.items

    run(
        host_domain=args.host,
        target_domain=args.target,
        rel_key=args.rel_key,
        item_ids=item_ids,
        config=config,
        dry_run=args.dry_run,
        skip_existing=args.skip_existing,
        force=args.force,
        video_dir=args.video_dir,
        output_mode=output_mode,
    )


if __name__ == "__main__":
    main()
