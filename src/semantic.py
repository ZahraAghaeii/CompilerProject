from src.ast_nodes import *

class Symbol:
    def __init__(self, name: str, kind: str, type_spec: str, line: int, column: int, signature=None):
        self.name = name
        self.kind = kind          # 'variable', 'function', 'parameter'
        self.type_spec = type_spec
        self.line = line
        self.column = column
        self.signature = signature # برای توابع: پارامترها
        self.is_used = False

class SymbolTable:
    def __init__(self, parent=None, scope_name="Global"):
        self.symbols = {}
        self.parent = parent
        self.scope_name = scope_name
        self.children = []
        if parent:
            parent.children.append(self)

    def define(self, symbol: Symbol) -> bool:
        if symbol.name in self.symbols:
            return False  # Duplicate in same scope
        self.symbols[symbol.name] = symbol
        return True

    def lookup(self, name: str):
        if name in self.symbols:
            return self.symbols[name], self
        if self.parent:
            return self.parent.lookup(name)
        return None, None

class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = SymbolTable(scope_name="Global")
        self.current_scope = self.global_scope
        self.errors = []
        self.warnings = []

    def analyze(self, ast: ProgramNode):
        # Pass 1: ثبت تمام توابع در Global Scope (پشتیبانی از Forward Reference)
        for decl in ast.declarations:
            if isinstance(decl, FunctionDeclNode):
                sym = Symbol(decl.name, 'function', decl.return_type, decl.line, decl.column, signature=[p[0] for p in decl.params])
                if not self.global_scope.define(sym):
                    self.errors.append(f"Semantic Error at {decl.line}:{decl.column}: Duplicate function declaration '{decl.name}'")

        # Pass 2: پیمایش عمیق AST و بررسی Scopeها و Typeها
        self._visit(ast)
        self._check_unused_symbols(self.global_scope)
        return self.errors, self.warnings

    def _visit(self, node):
        if not node:
            return None

        method_name = f"_visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node):
        for attr in dir(node):
            if not attr.startswith('_'):
                val = getattr(node, attr)
                if isinstance(val, list):
                    for item in val:
                        if hasattr(item, 'line'):
                            self._visit(item)
                elif hasattr(val, 'line'):
                    self._visit(val)

    def _visit_ProgramNode(self, node: ProgramNode):
        for decl in node.declarations:
            self._visit(decl)

    def _visit_FunctionDeclNode(self, node: FunctionDeclNode):
        # ایجاد Scope جدید برای تابع
        func_scope = SymbolTable(parent=self.current_scope, scope_name=f"Function_{node.name}")
        self.current_scope = func_scope

        # ثبت پارامترهای ورودی در Scope تابع
        for p_type, p_name in node.params:
            p_sym = Symbol(p_name, 'parameter', p_type, node.line, node.column)
            p_sym.is_used = True
            if not self.current_scope.define(p_sym):
                self.errors.append(f"Semantic Error at {node.line}:{node.column}: Duplicate parameter '{p_name}'")

        self._visit(node.body)
        self._check_unused_symbols(self.current_scope)
        self.current_scope = self.current_scope.parent

    def _visit_VarDeclNode(self, node: VarDeclNode):
        init_type = self._visit(node.init_expr) if node.init_expr else None
        
        if init_type and init_type != node.type_spec and init_type != 'unknown':
            self.errors.append(f"Semantic Error at {node.line}:{node.column}: Type mismatch in assignment to '{node.name}'. Expected {node.type_spec}, got {init_type}")

        # بررسی Shadowing
        existing_sym, existing_scope = self.current_scope.lookup(node.name)
        if existing_sym and existing_scope != self.current_scope:
            self.warnings.append(f"Semantic Warning at {node.line}:{node.column}: Variable '{node.name}' shadows an outer declaration")

        sym = Symbol(node.name, 'variable', node.type_spec, node.line, node.column)
        if not self.current_scope.define(sym):
            self.errors.append(f"Semantic Error at {node.line}:{node.column}: Duplicate variable declaration '{node.name}'")

        node.inferred_type = node.type_spec

    def _visit_BlockNode(self, node: BlockNode):
        block_scope = SymbolTable(parent=self.current_scope, scope_name="Block")
        self.current_scope = block_scope
        for stmt in node.statements:
            self._visit(stmt)
        self._check_unused_symbols(self.current_scope)
        self.current_scope = self.current_scope.parent

    def _visit_AssignmentNode(self, node: AssignmentNode):
        expr_type = self._visit(node.expr)
        sym, _ = self.current_scope.lookup(node.name)
        if not sym:
            self.errors.append(f"Semantic Error at {node.line}:{node.column}: Undefined variable '{node.name}'")
            return 'unknown'

        sym.is_used = True
        if expr_type and expr_type != sym.type_spec and expr_type != 'unknown':
            self.errors.append(f"Semantic Error at {node.line}:{node.column}: Type mismatch in assignment to '{node.name}'. Expected {sym.type_spec}, got {expr_type}")
        return sym.type_spec

    def _visit_BinaryExprNode(self, node: BinaryExprNode):
        left_t = self._visit(node.left)
        right_t = self._visit(node.right)

        if left_t != right_t and 'unknown' not in (left_t, right_t):
            self.errors.append(f"Semantic Error at {node.line}:{node.column}: Type mismatch in binary operation '{node.op}' between {left_t} and {right_t}")

        node.inferred_type = left_t if left_t != 'unknown' else right_t
        return node.inferred_type

    def _visit_CallExprNode(self, node: CallExprNode):
        sym, _ = self.current_scope.lookup(node.callee)
        if not sym or sym.kind != 'function':
            self.errors.append(f"Semantic Error at {node.line}:{node.column}: Undefined function '{node.callee}'")
            return 'unknown'

        sym.is_used = True
        if len(node.args) != len(sym.signature):
            self.errors.append(f"Semantic Error at {node.line}:{node.column}: Function '{node.callee}' expects {len(sym.signature)} arguments, got {len(node.args)}")

        for arg, expected_type in zip(node.args, sym.signature):
            arg_t = self._visit(arg)
            if arg_t != expected_type and arg_t != 'unknown':
                self.errors.append(f"Semantic Error at {node.line}:{node.column}: Argument type mismatch in call to '{node.callee}'. Expected {expected_type}, got {arg_t}")

        node.inferred_type = sym.type_spec
        return sym.type_spec

    def _visit_IdentifierNode(self, node: IdentifierNode):
        sym, _ = self.current_scope.lookup(node.name)
        if not sym:
            self.errors.append(f"Semantic Error at {node.line}:{node.column}: Undefined identifier '{node.name}'")
            return 'unknown'
        sym.is_used = True
        node.inferred_type = sym.type_spec
        return sym.type_spec

    def _visit_LiteralNode(self, node: LiteralNode):
        node.inferred_type = node.literal_type
        return node.literal_type

    def _check_unused_symbols(self, scope: SymbolTable):
        for name, sym in scope.symbols.items():
            if not sym.is_used and sym.kind == 'variable':
                self.warnings.append(f"Semantic Info at {sym.line}:{sym.column}: Unused variable '{name}'")