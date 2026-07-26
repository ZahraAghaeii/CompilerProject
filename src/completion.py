class IntellisenseEngine:
    def __init__(self, global_scope):
        self.global_scope = global_scope

    def get_completions(self, scope, prefix=""):
        suggestions = []
        curr = scope
        visited = set()

        while curr:
            for name, sym in curr.symbols.items():
                if name not in visited and name.startswith(prefix):
                    visited.add(name)
                    suggestions.append({
                        'label': name,
                        'kind': sym.kind,
                        'detail': f"{sym.type_spec}" + (f"({', '.join(sym.signature)})" if sym.signature else "")
                    })
            curr = curr.parent

        return sorted(suggestions, key=lambda x: x['label'])