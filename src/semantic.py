from src.ast_nodes import (
    FunctionDeclNode, VarDeclNode, CallExprNode, IdentifierNode, AssignmentNode,
    BlockNode, IfStmtNode, WhileStmtNode, ForStmtNode, ReturnStmtNode,
    BinaryExprNode, LiteralNode, BreakStmtNode, ContinueStmtNode
)


class Symbol:
    def __init__(self, name: str, kind: str, type_spec: str, line: int = 1, col: int = 1, signature=None,
                 file_name="semantic_test.c"):
        self.name = name
        self.kind = kind
        self.type_spec = type_spec
        self.line = line
        self.col = col
        self.signature = signature or []
        self.file_name = file_name
        self.is_used = False
        self.is_initialized = False
        self.definition_loc = {"file": file_name, "line": line, "column": col}
        self.references = []

    def add_reference(self, file_name: str, line: int, col: int):
        self.references.append({"file": file_name, "line": line, "col": col})


class Scope:
    def __init__(self, scope_name: str, parent=None):
        self.scope_name = scope_name
        self.parent = parent
        self.symbols = {}
        self.children = []
        if parent:
            parent.children.append(self)

    def define(self, symbol):
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
        self.current_function = None

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
                self.log_diagnostic("Info", f"Unused variable '{sym.name}'", sym.line, sym.col, len(sym.name))

    def analyze(self, ast):
        if not ast or not hasattr(ast, 'declarations'):
            return
        for decl in ast.declarations:
            self.visit(decl)
        self._check_unused_in_scope(self.global_scope)

    def _is_compatible(self, expected, actual):
        if expected == actual:
            return True
        numeric_types = ['int', 'float', 'double']
        if expected in numeric_types and actual in numeric_types:
            return True
        return False

    def visit(self, node):
        if not node:
            return None

        if isinstance(node, FunctionDeclNode):
            if node.name in self.current_scope.symbols:
                self.log_diagnostic("Error", f"Duplicate declaration of function '{node.name}'", node.line, node.column,
                                    len(node.name))

            sig = []
            params_list = getattr(node, 'params', []) or []

            for p in params_list:
                if isinstance(p, tuple):
                    sig.append(p[0])
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
            sym.is_initialized = True
            self.current_scope.define(sym)
            self.current_function = sym

            self.enter_scope(f"Function_{node.name}")

            for param in params_list:
                p_type = param[0] if isinstance(param, tuple) else getattr(param, 'type_spec', 'int')
                p_name = param[1] if isinstance(param, tuple) else getattr(param, 'name', '')

                if p_name in self.current_scope.symbols:
                    self.log_diagnostic("Error", f"Duplicate parameter name '{p_name}'", node.line, node.column,
                                        len(p_name))

                p_sym = Symbol(name=p_name, kind='parameter', type_spec=p_type, line=node.line, col=node.column,
                               file_name=self.file_name)
                p_sym.is_initialized = True
                self.current_scope.define(p_sym)

            if hasattr(node, 'body') and node.body:
                self.visit(node.body)

            self.exit_scope()
            self.current_function = None
            return sym.type_spec

        elif isinstance(node, VarDeclNode):
            if node.name in self.current_scope.symbols:
                self.log_diagnostic("Error", f"Duplicate declaration of variable '{node.name}'", node.line, node.column,
                                    len(node.name))
            elif self.current_scope.parent:
                outer_sym, _ = self.current_scope.parent.lookup(node.name)
                if outer_sym:
                    self.log_diagnostic("Warning", f"Variable '{node.name}' shadows outer declaration", node.line,
                                        node.column, len(node.name))

            sym = Symbol(name=node.name, kind='variable', type_spec=node.type_spec, line=node.line, col=node.column,
                         file_name=self.file_name)
            self.current_scope.define(sym)

            if hasattr(node, 'init_expr') and node.init_expr:
                sym.is_initialized = True
                init_type = self.visit(node.init_expr)
                if init_type and not self._is_compatible(sym.type_spec, init_type):
                    self.log_diagnostic("Error", f"Type mismatch: Cannot assign '{init_type}' to '{sym.type_spec}'",
                                        node.line, node.column, len(node.name))
            return None

        elif isinstance(node, AssignmentNode):
            sym, _ = self.current_scope.lookup(node.name)
            if sym:
                sym.is_used = True
                sym.is_initialized = True
                sym.add_reference(self.file_name, node.line, node.column)
            else:
                self.log_diagnostic("Error", f"Undefined variable '{node.name}'", node.line, node.column,
                                    len(node.name))

            if hasattr(node, 'expr') and node.expr:
                expr_type = self.visit(node.expr)
                if sym and expr_type and not self._is_compatible(sym.type_spec, expr_type):
                    self.log_diagnostic("Error", f"Type mismatch: Cannot assign '{expr_type}' to '{sym.type_spec}'",
                                        node.line, node.column, len(node.name))
            return None

        elif isinstance(node, CallExprNode):
            sym, _ = self.current_scope.lookup(node.callee)
            arg_types = []

            for arg in getattr(node, 'args', []) or []:
                arg_types.append(self.visit(arg))

            if sym:
                sym.is_used = True
                sym.add_reference(self.file_name, node.line, node.column)
                if len(arg_types) != len(sym.signature):
                    self.log_diagnostic("Error",
                                        f"Function '{node.callee}' expects {len(sym.signature)} arguments, got {len(arg_types)}",
                                        node.line, node.column, len(node.callee))
                else:
                    for i, (expected, actual) in enumerate(zip(sym.signature, arg_types)):
                        if actual and not self._is_compatible(expected, actual):
                            self.log_diagnostic("Error",
                                                f"Argument {i + 1} type mismatch in call to '{node.callee}': expected '{expected}', got '{actual}'",
                                                node.line, node.column, len(node.callee))
            else:
                self.log_diagnostic("Error", f"Undefined function '{node.callee}'", node.line, node.column,
                                    len(node.callee))

            return sym.type_spec if sym else None

        elif isinstance(node, IdentifierNode):
            sym, _ = self.current_scope.lookup(node.name)
            if sym:
                sym.is_used = True
                sym.add_reference(self.file_name, node.line, node.column)
                if not sym.is_initialized:
                    self.log_diagnostic("Warning", f"Use of uninitialized variable '{node.name}'", node.line,
                                        node.column, len(node.name))
                return sym.type_spec
            else:
                self.log_diagnostic("Error", f"Undefined variable '{node.name}'", node.line, node.column,
                                    len(node.name))
                return None

        elif isinstance(node, LiteralNode):
            return node.literal_type

        elif isinstance(node, BinaryExprNode):
            left_type = self.visit(node.left)
            right_type = self.visit(node.right)
            if left_type == right_type:
                return left_type
            if left_type in ['float', 'double'] or right_type in ['float', 'double']:
                return 'float'
            return left_type


        elif isinstance(node, BlockNode):
            self.enter_scope("Block")
            for stmt in node.statements:
                self.visit(stmt)
            self.exit_scope()
            return None

        elif isinstance(node, IfStmtNode):
            self.visit(node.condition)
            self.visit(node.then_branch)
            if node.else_branch: self.visit(node.else_branch)
            return None

        elif isinstance(node, WhileStmtNode):
            self.visit(node.condition)
            self.visit(node.body)
            return None

        elif isinstance(node, ForStmtNode):
            if node.init: self.visit(node.init)
            if node.condition: self.visit(node.condition)
            if node.step: self.visit(node.step)
            if node.body: self.visit(node.body)
            return None

        elif isinstance(node, ReturnStmtNode):
            if node.expr:
                expr_type = self.visit(node.expr)
                if self.current_function and expr_type and not self._is_compatible(self.current_function.type_spec,
                                                                                   expr_type):
                    self.log_diagnostic("Error",
                                        f"Return type mismatch: expected '{self.current_function.type_spec}', got '{expr_type}'",
                                        node.line, node.column, 6)
            return None

        elif isinstance(node, (BreakStmtNode, ContinueStmtNode)):
            return None
