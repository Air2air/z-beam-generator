#!/usr/bin/env python3
"""
data_completeness.py — Source data completeness audit for all domains.

Checks:
  1. Required field presence per domain (CRITICAL if key missing)
  2. Empty / null / blank values on required fields (HIGH)
  3. Sub-structure completeness: faq, eeat, micro, machineSettings,
     images, relationships, components, card (MEDIUM)
  4. Cross-domain referential integrity: author → authors.yaml,
     validMaterials → Materials.yaml (HIGH)
  5. Duplicate ids within a domain (CRITICAL)
  6. datePublished / dateModified ISO-8601 format (LOW)

Output: tasks/data_audit_report.md
Run from repo root: python3 scripts/audit/data_completeness.py
"""

import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "data"
REPORT_PATH = REPO / "tasks" / "data_audit_report.md"

DOMAIN_FILES = {
    "materials":    DATA / "materials"    / "Materials.yaml",
    "contaminants": DATA / "contaminants" / "contaminants.yaml",
    "settings":     DATA / "settings"     / "Settings.yaml",
    "compounds":    DATA / "compounds"    / "Compounds.yaml",
    "applications": DATA / "applications" / "Applications.yaml",
    "authors":      DATA / "authors"      / "Authors.yaml",
}

# Top-level key inside each YAML that holds the item dict
COLLECTION_KEY = {
    "materials":    "materials",
    "contaminants": "contaminants",
    "settings":     "settings",
    "compounds":    "compounds",
    "applications": "applications",
    "authors":      "authors",
}

# ---------------------------------------------------------------------------
# Required fields per domain  (absence → CRITICAL, empty value → HIGH)
# ---------------------------------------------------------------------------
REQUIRED_FIELDS = {
    "materials": [
        "id", "name", "displayName", "category", "subcategory",
        "pageDescription", "author", "fullPath", "slug",
        "datePublished", "dateModified",
        "properties", "micro", "faq", "eeat", "contamination",
        "components", "card", "breadcrumb", "images", "relationships",
    ],
    "contaminants": [
        "id", "name", "displayName", "category", "subcategory",
        "pageDescription", "description",
        "datePublished", "dateModified",
        "breadcrumb", "validMaterials", "images", "relationships",
        # micro is materials-only; not required for contaminants
    ],
    "settings": [
        "id", "name", "displayName", "category", "subcategory",
        "pageDescription", "machineSettings",
        "datePublished", "dateModified",
        "images", "relationships", "card",
    ],
    "compounds": [
        "id", "name", "displayName", "category", "subcategory",
        "pageDescription", "chemicalFormula", "casNumber",
        "molecularWeight", "healthEffects", "exposureGuidelines",
        "detectionMethods",
    ],
    "applications": [
        "id", "name", "displayName", "category", "subcategory",
        "pageDescription", "fullPath", "breadcrumb",
        "datePublished", "dateModified",
    ],
    "authors": [
        "id", "name", "title", "jobTitle", "expertise",
        "affiliation", "credentials", "image", "imageAlt",
    ],
}

# Sub-structure checks: (field, expected_type, min_len)
# expected_type=None means "any non-empty" (presence already checked by required_fields).
# For list: min_len = minimum element count.
# For dict: min_len = minimum key count.
# NOTE: compounds healthEffects/exposureGuidelines/detectionMethods are legitimately
#       plain strings — do NOT type-check them here.
#       materials faq canonical format is dict{presentation,items,options} — NOT a list.
SUBSTRUCTURE_CHECKS = {
    "materials": [
        ("faq",          dict,  1),   # dict with presentation/items/options
        ("eeat",         dict,  1),   # non-empty dict
        ("micro",        dict,  1),   # dict with before/after
        ("contamination",dict,  1),
        ("components",   dict,  1),
        ("card",         dict,  1),
        ("breadcrumb",   list,  2),
        ("images",       dict,  1),
        ("relationships",dict,  1),
        ("properties",   dict,  1),
    ],
    "contaminants": [
        ("micro",        dict,  1),
        ("images",       dict,  1),
        ("relationships",dict,  1),
        ("validMaterials",list, 1),
        ("breadcrumb",   list,  2),
    ],
    "settings": [
        ("machineSettings", dict, 1),
        ("images",       dict,  1),
        ("relationships",dict,  1),
        ("card",         dict,  1),
    ],
    # compounds: healthEffects/exposureGuidelines/detectionMethods are strings by design;
    # emptiness is caught by the required_fields HIGH check.
    "compounds": [],
    "applications": [
        ("breadcrumb",   list,  2),
    ],
    "authors": [],
}

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
DATE_FIELDS = ["datePublished", "dateModified"]

# ---------------------------------------------------------------------------
# Severity helpers
# ---------------------------------------------------------------------------
SEV_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

def sev_key(f):
    return SEV_ORDER.get(f.get("severity", "LOW"), 3)

class Finding:
    __slots__ = ("severity", "domain", "item_id", "field", "message")
    def __init__(self, severity, domain, item_id, field, message):
        self.severity = severity
        self.domain   = domain
        self.item_id  = str(item_id)
        self.field    = field
        self.message  = message


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def is_empty(val):
    """Return True if a value counts as 'missing content'."""
    if val is None:
        return True
    if isinstance(val, str) and val.strip() == "":
        return True
    if isinstance(val, (list, dict)) and len(val) == 0:
        return True
    return False


def load_domain(domain: str):
    path = DOMAIN_FILES[domain]
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    coll_key = COLLECTION_KEY[domain]
    if isinstance(raw, dict):
        collection = raw.get(coll_key, {})
    else:
        collection = raw
    # Normalise list → dict keyed by index
    if isinstance(collection, list):
        collection = {str(i): item for i, item in enumerate(collection)}
    return collection   # dict of {item_key: item_dict}


# ---------------------------------------------------------------------------
# Audit routines
# ---------------------------------------------------------------------------
def audit_required_fields(domain, items):
    findings = []
    req = REQUIRED_FIELDS.get(domain, [])
    for item_key, item in items.items():
        item_id = item.get("id", item_key)
        for field in req:
            if (
                domain == "compounds"
                and field == "molecularWeight"
                and _is_variable_compound_without_deterministic_molecular_weight(item)
            ):
                continue
            if field not in item:
                findings.append(Finding("CRITICAL", domain, item_id, field,
                    "Field missing entirely"))
            elif is_empty(item[field]):
                findings.append(Finding("HIGH", domain, item_id, field,
                    "Field present but empty/null"))
    return findings


def _is_variable_compound_without_deterministic_molecular_weight(item):
    """Return True when a compound is intentionally mixed/variable composition.

    For mixed/variable compounds, molecular weight can be legitimately undefined.
    """
    if not isinstance(item, dict):
        return False

    chemical_formula = item.get("chemicalFormula")
    identifier = str(item.get("id", "")).lower()
    name = str(item.get("name", "")).lower()

    variable_formula_values = {"various", "cxhyoz"}
    if isinstance(chemical_formula, str) and chemical_formula.strip().lower() in variable_formula_values:
        return True

    if "mixed" in identifier or "mixed" in name:
        return True

    return False


def audit_substructures(domain, items):
    """Check sub-field type and minimum size.
    Also flags fields that are raw strings when the canonical format is dict/list
    (indicates generated text that was never parsed into structured form).
    """
    findings = []
    checks = SUBSTRUCTURE_CHECKS.get(domain, [])
    canonical_dict_fields = {"faq", "micro", "eeat", "contamination", "components",
                              "card", "images", "relationships", "properties",
                              "machineSettings", "healthEffects",
                              "exposureGuidelines", "detectionMethods"}
    canonical_list_fields = {"breadcrumb", "validMaterials"}
    for item_key, item in items.items():
        item_id = item.get("id", item_key)
        for field, expected_type, min_len in checks:
            val = item.get(field)
            if val is None:
                continue  # absence already captured by required_fields audit
            if not isinstance(val, expected_type):
                # Only flag str-instead-of-dict/list as MEDIUM (unstructured raw text)
                if isinstance(val, str):
                    if field in canonical_dict_fields or field in canonical_list_fields:
                        findings.append(Finding("MEDIUM", domain, item_id, field,
                            "Unstructured: stored as raw string, expected " +
                            expected_type.__name__))
                else:
                    findings.append(Finding("MEDIUM", domain, item_id, field,
                        "Wrong type: expected " + expected_type.__name__ +
                        " got " + type(val).__name__))
            elif expected_type == list and len(val) < min_len:
                findings.append(Finding("MEDIUM", domain, item_id, field,
                    "List too short: has " + str(len(val)) +
                    " items (min " + str(min_len) + ")"))
            elif expected_type == dict and len(val) < min_len:
                findings.append(Finding("MEDIUM", domain, item_id, field,
                    "Empty dict"))
    return findings


def audit_duplicate_ids(domain, items):
    findings = []
    id_counts = Counter()
    for item in items.values():
        id_val = item.get("id")
        if id_val is not None:
            id_counts[str(id_val)] += 1
    for id_val, count in id_counts.items():
        if count > 1:
            findings.append(Finding("CRITICAL", domain, id_val, "id",
                "Duplicate id appears " + str(count) + " times"))
    return findings


def audit_date_format(domain, items):
    findings = []
    for item_key, item in items.items():
        item_id = item.get("id", item_key)
        for field in DATE_FIELDS:
            val = item.get(field)
            if val is None or (isinstance(val, str) and val.strip() == ""):
                continue
            if not ISO_RE.match(str(val)):
                findings.append(Finding("LOW", domain, item_id, field,
                    "Non-ISO-8601 date: " + repr(val)))
    return findings


def audit_referential_integrity(materials_items, contaminants_items, settings_items):
    """
    Check:
    - materials.author → authors.id
    - contaminants.validMaterials[] → materials.id
    - settings items reference nothing external (nothing to check cross-domain here)
    """
    findings = []
    author_ids = set()
    try:
        auth_items = load_domain("authors")
        author_ids = {v.get("id") for v in auth_items.values() if v.get("id")}
    except Exception as e:
        findings.append(Finding("CRITICAL", "authors", "N/A", "file",
            "Could not load authors: " + str(e)))

    material_ids = {v.get("id") for v in materials_items.values() if v.get("id")}

    # materials → authors
    for item in materials_items.values():
        item_id = item.get("id", "?")
        author_field = item.get("author")
        author_id = author_field if isinstance(author_field, int) else (
            author_field.get("id") if isinstance(author_field, dict) else None
        )
        if author_id and author_id not in author_ids:
            findings.append(Finding("HIGH", "materials", item_id, "author",
                "author '" + str(author_id) + "' not in Authors.yaml"))

    # contaminants → materials (validMaterials list)
    for item in contaminants_items.values():
        item_id = item.get("id", "?")
        valid = item.get("validMaterials")
        if not isinstance(valid, list):
            continue
        for mat_ref in valid:
            ref_id = mat_ref if isinstance(mat_ref, str) else mat_ref.get("id") if isinstance(mat_ref, dict) else None
            if ref_id and ref_id not in material_ids:
                findings.append(Finding("MEDIUM", "contaminants", item_id,
                    "validMaterials", "References unknown material id '" + str(ref_id) + "'"))

    return findings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run_audit():
    all_findings = []
    domain_items = {}

    for domain in DOMAIN_FILES:
        try:
            items = load_domain(domain)
            domain_items[domain] = items
        except Exception as e:
            all_findings.append(Finding("CRITICAL", domain, "N/A", "file",
                "Failed to load: " + str(e)))
            domain_items[domain] = {}
            continue

        all_findings += audit_duplicate_ids(domain, items)
        all_findings += audit_required_fields(domain, items)
        all_findings += audit_substructures(domain, items)
        all_findings += audit_date_format(domain, items)

    # Cross-domain referential integrity
    all_findings += audit_referential_integrity(
        domain_items.get("materials", {}),
        domain_items.get("contaminants", {}),
        domain_items.get("settings", {}),
    )

    return all_findings, domain_items


def build_report(findings, domain_items):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Data Completeness Audit Report",
        "",
        "> Auto-generated by `scripts/audit/data_completeness.py`  ",
        "> Run: " + now,
        "",
    ]

    # Summary table
    counts = Counter((f.severity, f.domain) for f in findings)
    total_by_sev = Counter(f.severity for f in findings)

    lines += [
        "## Summary",
        "",
        "| Severity | Count |",
        "|----------|-------|",
    ]
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        lines.append("| " + sev + " | " + str(total_by_sev.get(sev, 0)) + " |")
    lines += ["", "**Total findings: " + str(len(findings)) + "**", ""]

    # Per-domain item counts
    lines += [
        "## Domain Item Counts",
        "",
        "| Domain | Items |",
        "|--------|-------|",
    ]
    for domain, items in domain_items.items():
        lines.append("| " + domain + " | " + str(len(items)) + " |")
    lines.append("")

    # Findings grouped by severity
    by_sev = defaultdict(list)
    for f in findings:
        by_sev[f.severity].append(f)

    sev_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}

    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        sev_findings = sorted(by_sev[sev], key=lambda f: (f.domain, f.item_id, f.field))
        lines += [
            "---",
            "",
            "## " + sev_emoji.get(sev, "") + " " + sev + " (" + str(len(sev_findings)) + ")",
            "",
        ]
        if not sev_findings:
            lines.append("_None._")
            lines.append("")
            continue

        # Group by domain
        by_domain = defaultdict(list)
        for f in sev_findings:
            by_domain[f.domain].append(f)

        for domain, dfindings in sorted(by_domain.items()):
            lines.append("### " + domain + " (" + str(len(dfindings)) + ")")
            lines.append("")
            lines.append("| Item ID | Field | Message |")
            lines.append("|---------|-------|---------|")
            for f in dfindings:
                lines.append("| `" + f.item_id + "` | `" + f.field + "` | " + f.message + " |")
            lines.append("")

    # Field-frequency summary — which fields are most often missing/empty
    lines += [
        "---",
        "",
        "## Field Frequency Summary (CRITICAL + HIGH only)",
        "",
        "| Field | Domain | Occurrences |",
        "|-------|--------|-------------|",
    ]
    freq = Counter()
    for f in findings:
        if f.severity in ("CRITICAL", "HIGH"):
            freq[(f.field, f.domain)] += 1
    for (field, domain), n in sorted(freq.items(), key=lambda x: -x[1])[:40]:
        lines.append("| `" + field + "` | " + domain + " | " + str(n) + " |")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Running data completeness audit...")
    findings, domain_items = run_audit()

    report = build_report(findings, domain_items)
    REPORT_PATH.write_text(report, encoding="utf-8")

    total_by_sev = Counter(f.severity for f in findings)
    print("Done.")
    print("  CRITICAL : " + str(total_by_sev.get("CRITICAL", 0)))
    print("  HIGH     : " + str(total_by_sev.get("HIGH", 0)))
    print("  MEDIUM   : " + str(total_by_sev.get("MEDIUM", 0)))
    print("  LOW      : " + str(total_by_sev.get("LOW", 0)))
    print("  Total    : " + str(len(findings)))
    print("Report written to " + str(REPORT_PATH))
    sys.exit(0)
