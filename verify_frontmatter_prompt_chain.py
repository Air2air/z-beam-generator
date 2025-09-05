#!/usr/bin/env python3
"""
Frontmatter Prompt Chain Verification Script

Verifies that generated frontmatter contains proper prompt chain verification metadata.
"""

import sys
import os
import yaml
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def verify_frontmatter_prompt_chain(frontmatter_file: str) -> Dict[str, Any]:
    """
    Verify that frontmatter contains complete prompt chain verification metadata.

    Args:
        frontmatter_file: Path to the frontmatter markdown file

    Returns:
        Dict containing verification results
    """
    results = {
        "file": frontmatter_file,
        "verified": False,
        "issues": [],
        "metadata": {}
    }

    try:
        # Read the frontmatter file
        with open(frontmatter_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract YAML frontmatter (between --- markers)
        if not content.startswith('---'):
            results["issues"].append("File does not start with YAML frontmatter marker (---)")
            return results

        # Find the end of frontmatter
        end_marker = content.find('\n---', 3)
        if end_marker == -1:
            results["issues"].append("No closing YAML frontmatter marker found")
            return results

        # Extract YAML content
        yaml_content = content[3:end_marker + 1]
        frontmatter = yaml.safe_load(yaml_content)

        results["metadata"] = frontmatter

        # Check for prompt chain verification section
        if "prompt_chain_verification" not in frontmatter:
            results["issues"].append("Missing 'prompt_chain_verification' section in frontmatter")
            return results

        verification = frontmatter["prompt_chain_verification"]

        # Required verification fields
        required_fields = [
            "base_config_loaded",
            "persona_config_loaded",
            "formatting_config_loaded",
            "ai_detection_config_loaded",
            "persona_country",
            "author_id",
            "verification_timestamp",
            "prompt_components_integrated",
            "human_authenticity_focus",
            "cultural_adaptation_applied"
        ]

        missing_fields = []
        for field in required_fields:
            if field not in verification:
                missing_fields.append(field)

        if missing_fields:
            results["issues"].append(f"Missing verification fields: {', '.join(missing_fields)}")
            return results

        # Validate field values
        if not verification["base_config_loaded"]:
            results["issues"].append("Base configuration was not loaded")

        if not verification["persona_config_loaded"]:
            results["issues"].append("Persona configuration was not loaded")

        if not verification["formatting_config_loaded"]:
            results["issues"].append("Formatting configuration was not loaded")

        if not verification["ai_detection_config_loaded"]:
            results["issues"].append("AI detection configuration was not loaded")

        if verification["prompt_components_integrated"] != 4:
            results["issues"].append(f"Expected 4 prompt components, found {verification['prompt_components_integrated']}")

        if not verification["human_authenticity_focus"]:
            results["issues"].append("Human authenticity focus was not applied")

        if not verification["cultural_adaptation_applied"]:
            results["issues"].append("Cultural adaptation was not applied")

        # Validate persona country
        valid_countries = ["Taiwan", "Italy", "Indonesia", "USA"]
        if verification["persona_country"] not in valid_countries:
            results["issues"].append(f"Invalid persona country: {verification['persona_country']}")

        # Validate author_id
        if not isinstance(verification["author_id"], int) or verification["author_id"] < 1 or verification["author_id"] > 4:
            results["issues"].append(f"Invalid author_id: {verification['author_id']}")

        # Validate timestamp format
        import re
        timestamp_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        if not re.match(timestamp_pattern, verification["verification_timestamp"]):
            results["issues"].append(f"Invalid timestamp format: {verification['verification_timestamp']}")

        # If no issues, verification passed
        if not results["issues"]:
            results["verified"] = True

        return results

    except Exception as e:
        results["issues"].append(f"Error parsing frontmatter: {str(e)}")
        return results

def verify_directory(directory: str) -> List[Dict[str, Any]]:
    """
    Verify all frontmatter files in a directory.

    Args:
        directory: Directory containing frontmatter files

    Returns:
        List of verification results for each file
    """
    results = []
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"Directory not found: {directory}")
        return results

    # Find all markdown files
    for md_file in dir_path.glob("*.md"):
        result = verify_frontmatter_prompt_chain(str(md_file))
        results.append(result)

    return results

def main():
    """Main verification function."""
    print("🔍 Frontmatter Prompt Chain Verification")
    print("=" * 50)

    if len(sys.argv) < 2:
        print("Usage: python verify_frontmatter_prompt_chain.py <frontmatter_file_or_directory>")
        print("\nExamples:")
        print("  python verify_frontmatter_prompt_chain.py content/components/author/stoneware-laser-cleaning.md")
        print("  python verify_frontmatter_prompt_chain.py content/components/author/")
        sys.exit(1)

    target = sys.argv[1]
    target_path = Path(target)

    if target_path.is_file():
        # Verify single file
        result = verify_frontmatter_prompt_chain(target)

        print(f"📄 Verifying: {result['file']}")
        print(f"✅ Verified: {result['verified']}")

        if result["issues"]:
            print("\n❌ Issues found:")
            for issue in result["issues"]:
                print(f"   - {issue}")
        else:
            print("\n✅ All verification checks passed!")
            print(f"   👤 Author ID: {result['metadata'].get('prompt_chain_verification', {}).get('author_id', 'N/A')}")
            print(f"   🌍 Persona Country: {result['metadata'].get('prompt_chain_verification', {}).get('persona_country', 'N/A')}")
            print(f"   📅 Verification Time: {result['metadata'].get('prompt_chain_verification', {}).get('verification_timestamp', 'N/A')}")

    elif target_path.is_dir():
        # Verify directory
        results = verify_directory(target)

        if not results:
            print(f"No markdown files found in {target}")
            return

        total_files = len(results)
        verified_files = sum(1 for r in results if r["verified"])
        failed_files = total_files - verified_files

        print(f"📁 Verified {total_files} files in {target}")
        print(f"✅ Passed: {verified_files}")
        print(f"❌ Failed: {failed_files}")

        if failed_files > 0:
            print("\n❌ Files with issues:")
            for result in results:
                if not result["verified"]:
                    print(f"   📄 {Path(result['file']).name}:")
                    for issue in result["issues"]:
                        print(f"      - {issue}")

        if verified_files > 0:
            print("\n✅ Successfully verified files:")
            for result in results:
                if result["verified"]:
                    verification = result["metadata"].get("prompt_chain_verification", {})
                    print(f"   📄 {Path(result['file']).name}")
                    print(f"      👤 Author ID: {verification.get('author_id', 'N/A')}")
                    print(f"      🌍 Country: {verification.get('persona_country', 'N/A')}")

    else:
        print(f"Path not found: {target}")

if __name__ == "__main__":
    main()
