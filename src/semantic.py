from src.ast_nodes import FunctionDeclNode, VarDeclNode, CallExprNode, IdentifierNode, AssignmentNode

class Symbol:
    def __init__(self, name: str, kind: str, type_spec: str, line: int = 1, col: int = 1, signature=None, file_name="semantic_test.c"):
        self.name = name
        self.kind = kind            # 'variable', 'function', 'parameter'
        self.type_spec = type_spec  # 'int', 'string', 'void', etc.
        self.line = line
        self.col = col
        self.signature = signature or []
        self.file_name = file_name
        self.is_used = False
        self.definition_loc = {"file": file_name, "line": line, "column": col}
        self.references = []

    def add_reference(self, file_name: str, line: int, col: int):
        self.references.append({"file": file_name, "line": line, "col": col})


class Scope:
    def __init__(self, scope_name: str, parent=None):
        self.scope_name = scope_name
        self.parent = parent
        self.symbols = {}

    def define(self, symbol: Symbol):
        self.symbols[symbol.name] = symbol

    def lookup(self, name: str):
        if name in self.symbols:
            return self.symbols[name], self
        if self.parent:
            return self.parent.lookup(name)
        return None, None


class SemanticAnalyzer:
    def __init__(self, file_name="semantic_test.c"):
        self.file_name = file_name
        self.global_scope = Scope("Global")
        self.current_scope = self.global_scope
        self.diagnostics = []

    def log_diagnostic(self, level: str, message: str, line: int, col: int, length: int):
        self.diagnostics.append({
            "level": level,
            "message": message,
            "file": self.file_name,
            "line": line,
            "col": col,
            "length": length
        })

    def enter_scope(self, scope_name: str):
        self.current_scope = Scope(scope_name, parent=self.current_scope)

    def exit_scope(self):
        self._check_unused_in_scope(self.current_scope)
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent

    def _check_unused_in_scope(self, scope: Scope):
        for sym in scope.symbols.values():
            if sym.kind == 'variable' and not sym.is_used:
                self.log_diagnostic(
                    "Info",
                    f"Unused variable '{sym.name}'",
                    sym.line,
                    sym.col,
                    len(sym.name)
                )

    def analyze(self, ast):
        if not ast or not hasattr(ast, 'declarations'):
            return

        for decl in ast.declarations:
            self.visit(decl)

        self._check_unused_in_scope(self.global_scope)

    def visit(self, node):
        if not node:
            return

        if isinstance(node, FunctionDeclNode):
            # استخراج امضا و پارامترها با پشتیبانی از هر دو حالت تاپل و ناود
            sig = []
            params_list = getattr(node, 'params', []) or []
            
            for p in params_list:
                if isinstance(p, tuple):
                    sig.append(p[0])  # حالت ('int', 'n')
                elif hasattr(p, 'type_spec'):
                    sig.append(p.type_spec)
                else:
                    sig.append('int')

            sym = Symbol(
                name=node.name,
                kind='function',
                type_spec=node.return_type,
                line=node.line,
                col=node.column,
                signature=sig,
                file_name=self.file_name
            )
            self.current_scope.define(sym)

            self.enter_scope(f"Function_{node.name}")
            
            for param in params_list:
                if isinstance(param, tuple):
                    p_type, p_name = param[0], param[1]
                    p_sym = Symbol(
                        name=p_name,
                        kind='parameter',
                        type_spec=p_type,
                        line=node.line,
                        col=node.column,
                        file_name=self.file_name
                    )
                    self.current_scope.define(p_sym)
                elif hasattr(param, 'name'):
                    p_sym = Symbol(
                        name=param.name,
                        kind='parameter',
                        type_spec=getattr(param, 'type_spec', 'int'),
                        line=getattr(param, 'line', node.line),
                        col=getattr(param, 'column', node.column),
                        file_name=self.file_name
                    )
                    self.current_scope.define(p_sym)

            if hasattr(node, 'body') and node.body:
                stmts = getattr(node.body, 'statements', []) if hasattr(node.body, 'statements') else []
                for stmt in stmts:
                    self.visit(stmt)

            self.exit_scope()

        elif isinstance(node, VarDeclNode):
            sym = Symbol(
                name=node.name,
                kind='variable',
                type_spec=node.type_spec,
                line=node.line,
                col=node.column,
                file_name=self.file_name
            )
            self.current_scope.define(sym)
            if hasattr(node, 'initializer') and node.initializer:
                self.visit(node.initializer)

        elif isinstance(node, AssignmentNode):
            sym, _ = self.current_scope.lookup(node.target)
            if sym:
                sym.is_used = True
                sym.add_reference(self.file_name, node.line, node.column)
            else:
                self.log_diagnostic("Error", f"Undefined variable '{node.target}'", node.line, node.column, len(node.target))
            if hasattr(node, 'value'):
                self.visit(node.value)

        elif isinstance(node, CallExprNode):
            sym, _ = self.current_scope.lookup(node.callee)
            if sym:
                sym.is_used = True
                sym.add_reference(self.file_name, node.line, node.column)
                args = getattr(node, 'args', []) or []
                if len(args) != len(sym.signature):
                    self.log_diagnostic(
                        "Error",
                        f"Function '{node.callee}' expects {len(sym.signature)} arguments, got {len(args)}",
                        node.line, node.column, len(node.callee)
                    )
            else:
                self.log_diagnostic("Error", f"Undefined function '{node.callee}'", node.line, node.column, len(node.callee))

            for arg in getattr(node, 'args', []) or []:
                self.visit(arg)

        elif isinstance(node, IdentifierNode):
            sym, _ = self.current_scope.lookup(node.name)
            if sym:
                sym.is_used = True
                sym.add_reference(self.file_name, node.line, node.column)