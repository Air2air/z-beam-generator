import logging
import random
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class DataFormatter:
    """Format frontmatter data into content-ready text with strong randomization."""

    @staticmethod
    def format_section_data(field_name: str, data: Any, randomize: bool = True) -> str:
        if data is None:
            return ""

        # Randomly choose a formatting style
        styles = ["bullets", "numbered", "inline", "table"]
        style = random.choice(styles) if randomize else "bullets"

        def format_items(items):
            # Randomly omit or emphasize items
            if randomize:
                # 20% chance to drop a random item
                if len(items) > 2 and random.random() < 0.2:
                    items = random.sample(items, k=len(items)-1)
                # 30% chance to duplicate/emphasize a random item
                if len(items) > 1 and random.random() < 0.3:
                    idx = random.randint(0, len(items)-1)
                    items.insert(idx, items[idx] + " (key point)")
                # Shuffle order
                if random.random() < 0.7:
                    random.shuffle(items)
            return items

        if isinstance(data, str):
            return data

        elif isinstance(data, list):
            if not data:
                return ""
            if isinstance(data[0], dict):
                items = []
                for item in data:
                    if "name" in item and "description" in item:
                        entry = f"{item['name']}: {item['description']}"
                    elif "code" in item and "description" in item:
                        entry = f"{item['code']}: {item['description']}"
                    elif "issue" in item and "solution" in item:
                        entry = f"{item['issue']} (Solution: {item['solution']})"
                    elif "name" in item:
                        entry = item["name"]
                    elif "code" in item:
                        entry = item["code"]
                    else:
                        first_key = next(iter(item))
                        entry = f"{first_key}: {item[first_key]}"
                    items.append(entry)
            else:
                items = [str(item) for item in data]

            items = format_items(items)

            if style == "bullets":
                return "\n".join(f"- {i}" for i in items)
            elif style == "numbered":
                return "\n".join(f"{idx+1}. {i}" for idx, i in enumerate(items))
            elif style == "inline":
                return "; ".join(items)
            elif style == "table":
                header = "| Item |\n|------|"
                rows = "\n".join(f"| {i} |" for i in items)
                return f"{header}\n{rows}"
            else:
                return "\n".join(items)

        elif isinstance(data, dict):
            items = [f"{key}: {value}" for key, value in data.items()]
            items = format_items(items)
            if style == "bullets":
                return "\n".join(f"- {i}" for i in items)
            elif style == "numbered":
                return "\n".join(f"{idx+1}. {i}" for idx, i in enumerate(items))
            elif style == "inline":
                return "; ".join(items)
            elif style == "table":
                header = "| Key | Value |\n|-----|-------|"
                rows = "\n".join(f"| {i.split(': ')[0]} | {i.split(': ')[1]} |" if ': ' in i else f"| {i} |" for i in items)
                return f"{header}\n{rows}"
            else:
                return "\n".join(items)

        return str(data)