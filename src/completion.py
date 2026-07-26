class IntellisenseEngine:
    def __init__(self, global_scope):
        self.global_scope = global_scope

    def get_completions_at(self, line: int, column: int, prefix=""):
        """پیشنهاد خودکار آگاه از Scope و موقعیت مکان‌نما (Line + Column)"""
        target_scope = self.global_scope.get_scope_at(line)
        suggestions = []
        curr = target_scope
        visited = set()

        sort_order = 1
        while curr:
            for name, sym in curr.symbols.items():
                if name not in visited and name.startswith(prefix):
                    visited.add(name)
                    suggestions.append({
                        'label': name,
                        'kind': sym.kind,
                        'detail': f"{sym.type_spec}" + (f"({', '.join(sym.signature)})" if sym.signature else ""),
                        'sortOrder': sort_order
                    })
                    sort_order += 1
            curr = curr.parent

        return suggestions