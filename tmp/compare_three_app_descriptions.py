import math
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

ITEMS = [
    "defense-laser-cleaning-applications",
    "aerospace-laser-cleaning-applications",
    "automotive-laser-cleaning-applications",
]
FRONTMATTER_DIR = Path(
    "/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/applications"
)


def iter_descriptions(data: Any, path: List[str]) -> List[Tuple[str, str]]:
    found: List[Tuple[str, str]] = []
    if isinstance(data, dict):
        for key, value in data.items():
            key_str = str(key)
            next_path = path + [key_str]
            lower_key = key_str.lower()
            is_description_key = lower_key.endswith("description") or lower_key in {
                "meta_description",
                "page_description",
            }
            if is_description_key and isinstance(value, str) and value.strip():
                found.append((".".join(next_path), value.strip()))
            found.extend(iter_descriptions(value, next_path))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            found.extend(iter_descriptions(item, path + [str(idx)]))
    return found


def tokenize_words(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9']+", text)


def split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def sentence_lengths(words_by_sentence: List[List[str]]) -> List[int]:
    return [len(words) for words in words_by_sentence if words]


def lexical_diversity(words: List[str]) -> float:
    if not words:
        return 0.0
    return len(set(w.lower() for w in words)) / len(words)


def stddev(values: List[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(variance)


def analyze_text(text: str) -> Dict[str, float]:
    words = tokenize_words(text)
    sentences = split_sentences(text)
    words_by_sentence = [tokenize_words(s) for s in sentences]
    sent_lengths = sentence_lengths(words_by_sentence)

    word_count = len(words)
    sent_mean = sum(sent_lengths) / len(sent_lengths) if sent_lengths else 0.0
    sent_std = stddev([float(v) for v in sent_lengths]) if len(sent_lengths) > 1 else 0.0
    lex_div = lexical_diversity(words)

    return {
        "word_count": float(word_count),
        "sentence_mean": sent_mean,
        "sentence_std": sent_std,
        "lex_diversity": lex_div,
    }


def summarize(metrics_list: List[float]) -> Tuple[float, float, float]:
    if not metrics_list:
        return (0.0, 0.0, 0.0)
    return (min(metrics_list), sum(metrics_list) / len(metrics_list), max(metrics_list))


def fmt(val: float) -> str:
    return f"{val:.2f}"


def main() -> None:
    all_rows = []
    per_item = {}

    for item in ITEMS:
        path = FRONTMATTER_DIR / f"{item}.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        descriptions = iter_descriptions(data, [])
        rows = []
        for field_path, text in descriptions:
            metrics = analyze_text(text)
            rows.append((field_path, metrics))
            all_rows.append((item, field_path, metrics))
        per_item[item] = rows

    print("Per-item summary:")
    for item, rows in per_item.items():
        word_counts = [r[1]["word_count"] for r in rows]
        sent_stds = [r[1]["sentence_std"] for r in rows]
        lex_divs = [r[1]["lex_diversity"] for r in rows]

        wc_min, wc_avg, wc_max = summarize(word_counts)
        ss_min, ss_avg, ss_max = summarize(sent_stds)
        ld_min, ld_avg, ld_max = summarize(lex_divs)

        print(f"- {item}:")
        print(f"  - word_count min/avg/max: {int(wc_min)}/{fmt(wc_avg)}/{int(wc_max)}")
        print(f"  - sentence_std min/avg/max: {fmt(ss_min)}/{fmt(ss_avg)}/{fmt(ss_max)}")
        print(f"  - lexical_diversity min/avg/max: {fmt(ld_min)}/{fmt(ld_avg)}/{fmt(ld_max)}")

    all_word_counts = [r[2]["word_count"] for r in all_rows]
    all_sent_stds = [r[2]["sentence_std"] for r in all_rows]
    all_lex_divs = [r[2]["lex_diversity"] for r in all_rows]

    wc_min, wc_avg, wc_max = summarize(all_word_counts)
    ss_min, ss_avg, ss_max = summarize(all_sent_stds)
    ld_min, ld_avg, ld_max = summarize(all_lex_divs)

    print("\nCombined summary (all three items):")
    print(f"- word_count min/avg/max: {int(wc_min)}/{fmt(wc_avg)}/{int(wc_max)}")
    print(f"- sentence_std min/avg/max: {fmt(ss_min)}/{fmt(ss_avg)}/{fmt(ss_max)}")
    print(f"- lexical_diversity min/avg/max: {fmt(ld_min)}/{fmt(ld_avg)}/{fmt(ld_max)}")

    sorted_rows = sorted(all_rows, key=lambda r: r[2]["word_count"])
    shortest = sorted_rows[:5]
    longest = sorted_rows[-5:]

    print("\nOutliers (shortest):")
    for item, field_path, metrics in shortest:
        print(f"- {item} :: {field_path} = {int(metrics['word_count'])} words")

    print("\nOutliers (longest):")
    for item, field_path, metrics in longest:
        print(f"- {item} :: {field_path} = {int(metrics['word_count'])} words")


if __name__ == "__main__":
    main()
