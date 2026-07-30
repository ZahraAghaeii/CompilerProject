import re

class PythonPlugin:
    """
    A lightweight parser plugin for Python snippets to demonstrate Multi-Language Support.
    Extracts structure, function definitions, and variables without altering C/C++ core.
    """
    def parse(self, code: str) -> dict:
        lines = code.splitlines()
        functions = []
        variables = []

        for line in lines:
            line_str = line.strip()
            # Detect function definitions (def func_name(...):)
            func_match = re.match(r'^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', line_str)
            if func_match:
                functions.append(func_match.group(1))

            # Detect variable assignments (var = value)
            var_match = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*[^=]', line_str)
            if var_match and var_match.group(1) not in ['if', 'while', 'for', 'def']:
                variables.append(var_match.group(1))

        return {
            "language": "Python",
            "functions": list(set(functions)),
            "variables": list(set(variables)),
            "total_lines": len(lines)
        }