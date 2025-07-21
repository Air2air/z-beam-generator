class OutputFormatter:
    """Standardizes output formatting across all components."""
    
    @staticmethod
    def format_section(title, content, level=2):
        """Format a markdown section with consistent styling."""
        header = "#" * level
        return f"\n{header} {title}\n\n{content}\n"
    
    @staticmethod
    def format_list(items, is_bullet=True):
        """Format a list with consistent styling."""
        prefix = "-" if is_bullet else "1."
        return "\n".join(f"{prefix} {item}" for item in items)
    
    @staticmethod
    def format_table(headers, rows):
        """Format a markdown table with consistent styling."""
        header_row = "| " + " | ".join(headers) + " |"
        separator = "|-" + "-|-".join("-" * len(h) for h in headers) + "-|"
        data_rows = [f"| {' | '.join(str(cell) for cell in row)} |" for row in rows]
        return f"{header_row}\n{separator}\n" + "\n".join(data_rows)