"""
Ultra-Compact Sentence Analysis Logger

Provides essential sentence-level AI detection feedback for optimization
while eliminating verbosity and focusing on actionable data.
"""

from typing import Any, Dict, List, Optional


def extract_compact_sentence_analysis(winston_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract only essential sentence analysis metrics for optimization decisions.
    
    Args:
        winston_details: Full Winston API response details
        
    Returns:
        Compact dictionary with actionable sentence metrics
    """
    if "sentences" not in winston_details or not winston_details["sentences"]:
        return {}
    
    sentences = winston_details["sentences"]
    
    # Extract scores and lengths only (no full text)
    sentence_scores = []
    sentence_lengths = []
    failing_indices = []
    
    for i, sentence in enumerate(sentences):
        if isinstance(sentence, dict):
            score = sentence.get("score", 100)
            length = sentence.get("length", 0)
            
            sentence_scores.append(score)
            sentence_lengths.append(length)
            
            # Mark failing sentences (score < 30 = AI-like)
            if score < 30:
                failing_indices.append(i)
    
    if not sentence_scores:
        return {}
    
    # Calculate essential metrics
    total_sentences = len(sentence_scores)
    failing_count = len(failing_indices)
    failing_percentage = (failing_count / total_sentences) * 100 if total_sentences > 0 else 0
    
    # Score distribution analysis
    very_low_scores = sum(1 for s in sentence_scores if s < 10)  # Definitely AI
    low_scores = sum(1 for s in sentence_scores if 10 <= s < 30)  # Likely AI
    unclear_scores = sum(1 for s in sentence_scores if 30 <= s < 70)  # Unclear
    good_scores = sum(1 for s in sentence_scores if s >= 70)  # Human-like
    
    # Compact result
    compact_analysis = {
        "total_sentences": total_sentences,
        "failing_count": failing_count,
        "failing_percentage": round(failing_percentage, 1),
        "score_distribution": {
            "very_low": very_low_scores,  # < 10
            "low": low_scores,           # 10-29
            "unclear": unclear_scores,   # 30-69
            "good": good_scores          # 70+
        },
        "failing_indices": failing_indices[:5],  # Only first 5 failing sentences
        "avg_failing_length": round(
            sum(sentence_lengths[i] for i in failing_indices) / len(failing_indices)
            if failing_indices else 0, 1
        ),
        "score_range": {
            "min": min(sentence_scores),
            "max": max(sentence_scores),
            "avg": round(sum(sentence_scores) / len(sentence_scores), 1)
        }
    }
    
    return compact_analysis


def format_compact_sentence_log(compact_analysis: Dict[str, Any]) -> str:
    """
    Format compact sentence analysis as minimal YAML for MD files.
    
    Args:
        compact_analysis: Compact sentence metrics from extract_compact_sentence_analysis
        
    Returns:
        Minimal YAML string for logging
    """
    if not compact_analysis:
        return ""
    
    lines = ["sentence_analysis:"]
    
    # Basic counts
    lines.append(f"  total: {compact_analysis['total_sentences']}")
    lines.append(f"  failing: {compact_analysis['failing_count']} ({compact_analysis['failing_percentage']}%)")
    
    # Score distribution
    dist = compact_analysis['score_distribution']
    lines.append(f"  distribution: very_low:{dist['very_low']}, low:{dist['low']}, unclear:{dist['unclear']}, good:{dist['good']}")
    
    # Key metrics
    score_range = compact_analysis['score_range']
    lines.append(f"  scores: min:{score_range['min']}, avg:{score_range['avg']}, max:{score_range['max']}")
    
    # Failing sentence info (without full text)
    if compact_analysis['failing_indices']:
        indices = compact_analysis['failing_indices']
        indices_str = ",".join(map(str, indices))
        if len(compact_analysis['failing_indices']) == 5:
            indices_str += "..."
        lines.append(f"  failing_indices: [{indices_str}]")
        lines.append(f"  avg_failing_length: {compact_analysis['avg_failing_length']}")
    
    return "\n".join(lines)


def update_content_with_compact_sentences(content: str, winston_details: Dict[str, Any]) -> str:
    """
    Replace verbose sentence logging with ultra-compact analysis.
    
    Args:
        content: Original markdown content
        winston_details: Winston API response details
        
    Returns:
        Updated content with compact sentence analysis
    """
    lines = content.split('\n')
    updated_lines = []
    
    # Extract compact analysis
    compact_analysis = extract_compact_sentence_analysis(winston_details)
    compact_log = format_compact_sentence_log(compact_analysis)
    
    # Remove existing verbose sentence logs
    skip_lines = False
    in_details = False
    
    for line in lines:
        # Start of details section
        if line.strip() == "details:" or line.strip().startswith("details:"):
            in_details = True
            updated_lines.append(line)
            continue
            
        # Skip verbose sentence arrays
        if in_details and ("sentences:" in line or skip_lines):
            if "sentences:" in line:
                skip_lines = True
                # Insert compact sentence analysis instead
                if compact_log:
                    for log_line in compact_log.split('\n'):
                        updated_lines.append(f"    {log_line}")
                continue
            elif skip_lines and (line.strip().startswith("]") or 
                               line.strip().startswith("failing_sentences_count:") or
                               line.strip().startswith("failing_sentences_percentage:")):
                skip_lines = False
                # Don't add this line, continue to next
                continue
            elif skip_lines:
                # Skip this line (part of verbose sentence array)
                continue
        
        # End of details section
        if in_details and line.strip().startswith("---"):
            in_details = False
            skip_lines = False
        
        updated_lines.append(line)
    
    return '\n'.join(updated_lines)


# Example usage
if __name__ == "__main__":
    # Example Winston response with sentences
    winston_details = {
        "sentences": [
            {"length": 129, "score": 0, "text": "First sentence..."},
            {"length": 157, "score": 0, "text": "Second sentence..."},
            {"length": 174, "score": 0, "text": "Third sentence..."},
            {"length": 192, "score": 51.6, "text": "Fourth sentence..."},
            {"length": 88, "score": 51.6, "text": "Fifth sentence..."},
            {"length": 221, "score": 51.6, "text": "Sixth sentence..."},
            {"length": 247, "score": 0, "text": "Seventh sentence..."},
        ]
    }
    
    # Extract compact analysis
    compact_analysis = extract_compact_sentence_analysis(winston_details)
    print("Compact Analysis:")
    for key, value in compact_analysis.items():
        print(f"{key}: {value}")
    
    print("\nCompact Log:")
    compact_log = format_compact_sentence_log(compact_analysis)
    print(compact_log)
