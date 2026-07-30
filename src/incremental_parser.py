import re


class IncrementalParser:
    """
    Demonstrates Incremental Re-Parsing for real-time IDE responsiveness.
    Only re-parses modified AST nodes/lines instead of full file re-parsing.
    """

    def __init__(self):
        self.cached_ast = {}

    def parse_full(self, code: str) -> dict:
        lines = code.splitlines()
        self.cached_ast = {i + 1: line.strip() for i, line in enumerate(lines)}
        return {
            "mode": "Full Parse",
            "total_lines_parsed": len(lines),
            "ast_cache_size": len(self.cached_ast),
            "reparsed_lines": list(range(1, len(lines) + 1))
        }

    def parse_incremental(self, old_code: str, new_code: str) -> dict:
        old_lines = old_code.splitlines()
        new_lines = new_code.splitlines()

        modified_line_numbers = []

        max_len = max(len(old_lines), len(new_lines))
        for i in range(max_len):
            old_l = old_lines[i] if i < len(old_lines) else None
            new_l = new_lines[i] if i < len(new_lines) else None

            if old_l != new_l:
                line_no = i + 1
                modified_line_numbers.append(line_no)
                if new_l is not None:
                    self.cached_ast[line_no] = new_l.strip()
                elif line_no in self.cached_ast:
                    del self.cached_ast[line_no]

        return {
            "mode": "Incremental Re-Parse",
            "total_lines": len(new_lines),
            "modified_regions": len(modified_line_numbers),
            "reparsed_lines": modified_line_numbers,
            "status": "Tree-sitter Incremental Update Successful"
        }