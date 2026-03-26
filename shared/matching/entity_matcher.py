"""
Entity Matcher — reusable keyword/token scoring for cross-domain relationship population.

Mirrors the scoring logic in app/utils/relatedVideosContent.ts so that relationships
populated here produce the same results the frontend would derive at runtime, but stored
as authored slugs (tier 1 priority).

ALGORITHM PARITY: This module is the canonical Python mirror of the scoring logic in
  z-beam/app/utils/relatedVideosContent.ts  (analyzeVideoMatch / isEligibleDerivedMatch).
If you change MatchConfig score weights here, apply the same change to the corresponding
numeric constants in that TypeScript file — and vice versa.

Supports any pair of host ↔ candidate domains:
  - materials, contaminants, compounds, applications, videos

Usage
-----
    from shared.matching.entity_matcher import EntityMatcher, MatchConfig

    matcher = EntityMatcher()
    scores = matcher.rank_candidates(host_entity, candidates, config=MatchConfig())
    for slug, score, diag in scores:
        if score >= config.min_score:
            print(slug, score)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Stop-word / generic-term filter lists — kept in sync with TS counterparts
# ---------------------------------------------------------------------------

STOP_WORDS: Set[str] = {
    "with", "this", "that", "from", "they", "their", "which", "have", "been",
    "will", "more", "also", "when", "than", "then", "into", "onto", "upon",
    "over", "under", "between", "through", "during", "before", "after", "about",
    "above", "below", "such", "each", "both", "some", "most", "other", "while",
    "these", "those", "very", "just", "only", "even", "well", "back", "where",
}

GENERIC_TERMS: Set[str] = {
    "laser", "cleaning", "laser cleaning", "surface", "process", "method",
    "technique", "application", "applications", "treatment", "removal",
    "preparation", "coating", "performance", "material", "materials",
    "contaminant", "contaminants", "compound", "compounds", "system", "systems",
    "technology", "technologies", "industrial", "industry", "professional",
    "equipment", "results", "operations", "standard", "standards", "general",
    "based", "type", "types", "form", "forms", "level", "levels", "case",
}

BROAD_PROCESS_TERMS: Set[str] = {
    "paint", "rust", "oxidation", "corrosion", "contamination", "residue",
    "coating", "oxide", "scale", "deposit", "buildup", "layer", "film",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class MatchConfig:
    """Tuning parameters for the matcher — defaults match the TS isEligibleDerivedMatch."""
    min_score: float = 8.0
    """Minimum composite score to emit a candidate."""

    direct_association_weight: float = 30.0
    """Score per direct (same-domain) association slug overlap."""

    supporting_association_weight: float = 10.0
    """Score per supporting (cross-domain) association slug overlap."""

    exact_subject_weight: float = 12.0
    exact_title_weight: float = 7.0
    exact_category_weight: float = 4.0
    exact_subcategory_weight: float = 4.0
    slug_subject_weight: float = 6.0
    keyword_phrase_weight: float = 6.0
    """Weight for multi-word keyword match."""
    keyword_token_weight: float = 3.0
    """Weight for single-word keyword match."""
    token_overlap_weight: float = 1.5
    """Weight per shared token."""

    max_results: int = 3
    require_primary_phrase: bool = True
    """If True, enforce that at least one primary phrase signal exists for weak matches."""


@dataclass
class MatchDiagnostics:
    score: float = 0.0
    direct_association_matches: int = 0
    supporting_association_matches: int = 0
    exact_subject_match: bool = False
    exact_title_match: bool = False
    exact_category_match: bool = False
    exact_subcategory_match: bool = False
    slug_subject_match: bool = False
    exact_keyword_matches: int = 0
    token_overlap_count: int = 0
    long_token_overlap_count: int = 0


@dataclass
class HostEntity:
    """
    The page being matched FOR (e.g. a material page that needs related videos).

    association_slugs maps domain → list of related slugs that are already
    authored on this page (used for direct/supporting association scoring).
    """
    slug: str
    domain: str
    subject: str = ""
    page_title: str = ""
    page_description: str = ""
    keywords: List[str] = field(default_factory=list)
    category: str = ""
    subcategory: str = ""
    association_slugs: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class CandidateEntity:
    """
    A page that might be related to the host (e.g. a video, a material, a contaminant).

    authored_associations maps domain → list of slugs already authored on this
    candidate (used in reverse — the candidate claims to relate to those slugs).
    """
    slug: str
    domain: str
    subject: str = ""
    page_title: str = ""
    page_description: str = ""
    keywords: List[str] = field(default_factory=list)
    category: str = ""
    subcategory: str = ""
    authored_associations: Dict[str, List[str]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def _sanitize(text: str) -> str:
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"www\.\S+", " ", text)
    text = re.sub(r"[#*_`>|]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> List[str]:
    """Produce deduplicated lowercase tokens from text, filtering noise."""
    tokens = re.split(r"[^a-z0-9]+", _sanitize(text).lower())
    seen: Set[str] = set()
    result = []
    for t in tokens:
        if (
            len(t) >= 4
            and t not in STOP_WORDS
            and t not in GENERIC_TERMS
            and t not in BROAD_PROCESS_TERMS
            and t not in seen
        ):
            seen.add(t)
            result.append(t)
    return result


def _normalize_phrase(text: str) -> str:
    return _sanitize(text).lower()


def _is_specific_phrase(text: str) -> bool:
    return len(tokenize(text)) >= 2


def _specific_keywords(keywords: List[str]) -> List[str]:
    seen: Set[str] = set()
    result = []
    for kw in keywords:
        n = _normalize_phrase(kw)
        if not n or n in seen or n in GENERIC_TERMS:
            continue
        if _is_specific_phrase(n) or any(len(t) >= 8 for t in tokenize(n)):
            seen.add(n)
            result.append(n)
    return result


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------

class EntityMatcher:
    """
    Scores a list of CandidateEntity objects against a HostEntity.

    All logic is pure Python; no API calls.
    """

    def _count_overlap(self, a: List[str], b: Set[str]) -> int:
        return sum(1 for x in a if x in b)

    def score(
        self,
        host: HostEntity,
        candidate: CandidateEntity,
        config: MatchConfig,
    ) -> Tuple[float, MatchDiagnostics]:
        """Return (score, diagnostics) for one host↔candidate pair."""
        diag = MatchDiagnostics()

        # --- Build candidate's searchable text and token set ---
        candidate_fragments = [
            candidate.slug,
            candidate.subject,
            candidate.page_title,
            candidate.page_description,
            *candidate.keywords,
        ]
        haystack = _sanitize(" ".join(f for f in candidate_fragments if f)).lower()
        candidate_tokens = set(tokenize(haystack))

        # --- Build host's token set ---
        host_fragments = [
            host.subject,
            host.page_title,
            host.page_description,
            host.category,
            host.subcategory,
            *host.keywords,
        ]
        host_tokens = set(tokenize(" ".join(f for f in host_fragments if f)))
        host_keywords = _specific_keywords(host.keywords)

        # --- Association scoring ---
        # Direct: candidate claims to relate to host's own domain slugs
        host_direct_slugs = set(host.association_slugs.get(host.domain, []) + [host.slug])
        candidate_direct = candidate.authored_associations.get(host.domain, [])
        diag.direct_association_matches = self._count_overlap(candidate_direct, host_direct_slugs)

        # Supporting: candidate's other-domain associations overlap with host's associations
        for domain, host_slugs in host.association_slugs.items():
            if domain == host.domain:
                continue
            candidate_related = candidate.authored_associations.get(domain, [])
            diag.supporting_association_matches += self._count_overlap(candidate_related, set(host_slugs))

        diag.score += diag.direct_association_matches * config.direct_association_weight
        diag.score += diag.supporting_association_matches * config.supporting_association_weight

        # --- Phrase matching ---
        subject_norm = _normalize_phrase(host.subject)
        title_norm = _normalize_phrase(host.page_title)
        category_norm = _normalize_phrase(host.category)
        subcategory_norm = _normalize_phrase(host.subcategory)
        slug_subject = subject_norm.replace(" ", "-")

        diag.exact_subject_match = bool(subject_norm) and _is_specific_phrase(subject_norm) and subject_norm in haystack
        diag.exact_title_match = bool(title_norm) and _is_specific_phrase(title_norm) and title_norm in haystack
        diag.exact_category_match = bool(category_norm) and _is_specific_phrase(category_norm) and category_norm in haystack
        diag.exact_subcategory_match = bool(subcategory_norm) and _is_specific_phrase(subcategory_norm) and subcategory_norm in haystack
        diag.slug_subject_match = bool(slug_subject) and slug_subject in candidate.slug

        if diag.exact_subject_match:
            diag.score += config.exact_subject_weight
        if diag.exact_title_match:
            diag.score += config.exact_title_weight
        if diag.exact_category_match:
            diag.score += config.exact_category_weight
        if diag.exact_subcategory_match:
            diag.score += config.exact_subcategory_weight
        if diag.slug_subject_match:
            diag.score += config.slug_subject_weight

        # --- Keyword matching ---
        for kw in host_keywords:
            if kw in haystack:
                diag.exact_keyword_matches += 1
                weight = config.keyword_phrase_weight if " " in kw else config.keyword_token_weight
                diag.score += weight

        # --- Token overlap ---
        for token in candidate_tokens:
            if token in host_tokens:
                diag.token_overlap_count += 1
                if len(token) >= 7:
                    diag.long_token_overlap_count += 1
                diag.score += config.token_overlap_weight

        return diag.score, diag

    def is_eligible(self, diag: MatchDiagnostics, config: MatchConfig) -> bool:
        """Mirrors isEligibleDerivedMatch from relatedVideosContent.ts."""
        if diag.direct_association_matches > 0:
            return True

        has_primary_phrase = (
            diag.exact_subject_match
            or diag.exact_title_match
            or diag.slug_subject_match
        )
        has_specific_keyword = diag.exact_keyword_matches > 0
        has_strong_tokens = (
            diag.token_overlap_count >= 5 and diag.long_token_overlap_count >= 3
        )

        threshold = config.min_score + (2.0 if diag.supporting_association_matches > 0 else 0.0)

        if not config.require_primary_phrase:
            return diag.score >= threshold

        return diag.score >= threshold and (
            has_primary_phrase or (has_specific_keyword and has_strong_tokens)
        )

    def rank_candidates(
        self,
        host: HostEntity,
        candidates: List[CandidateEntity],
        config: Optional[MatchConfig] = None,
    ) -> List[Tuple[str, float, MatchDiagnostics]]:
        """
        Score and rank all candidates against the host.

        Returns list of (slug, score, diagnostics) for eligible matches,
        sorted by score descending, limited to config.max_results.
        """
        if config is None:
            config = MatchConfig()

        scored = []
        for candidate in candidates:
            score, diag = self.score(host, candidate, config)
            if self.is_eligible(diag, config):
                scored.append((candidate.slug, score, diag))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[: config.max_results]
