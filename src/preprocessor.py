import re

class Preprocessor:
    def __init__(self):
        self.macros = {}

    def process(self, code: str) -> dict:
        """
        Processes #define directives and replaces macro occurrences in the code.
        """
        lines = code.splitlines()
        processed_lines = []
        expanded_sites = []

        # Pass 1: Extract #define macros
        for line in lines:
            define_match = re.match(r'^\s*#define\s+([A-Za-z_][A-Za-z0-9_]*)\s+(.+)$', line)
            if define_match:
                name, value = define_match.groups()
                self.macros[name] = value.strip()
                processed_lines.append(f"// Macro defined: {name} -> {value.strip()}")
            else:
                processed_lines.append(line)

        output_code = "\n".join(processed_lines)

        # Pass 2: Expand macros in the remaining code
        for name, value in self.macros.items():
            pattern = r'("[^"\\]*(?:\\.[^"\\]*)*")|\b' + re.escape(name) + r'\b'

            def replacement_logic(match):
                if match.group(1):
                    return match.group(1)
                return value

            if re.search(r'\b' + re.escape(name) + r'\b', output_code):
                expanded_sites.append(f"Expanded macro '{name}' to '{value}'")
                output_code = re.sub(pattern, replacement_logic, output_code)

        return {
            "expanded_code": output_code,
            "macros_found": self.macros,
            "expansion_notes": expanded_sites
        }