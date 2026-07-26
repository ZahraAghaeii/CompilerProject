from src.ast_nodes import *

class Diagnostic:
    def __init__(self, severity: str, message: str, file: str, line: int, column: int, length: int):
        self.severity = severity  # 'Error', 'Warning', 'Info'
        self.message = message
        self.file = file
        self.line = line
        self.column = column
        self.length = length

    def __repr__(self):
        icon = "❌" if self.severity == 'Error' else ("⚠️" if self.severity == 'Warning' else "ℹ️")
        return f"{icon} [{self.severity}] {self.message} at {self.file}:{self.line}:{self.column} (len:{self.length})"

class Symbol:
    def __init__(self, name: str, kind: str, type_spec: str, line: int, column: int, signature=None, scope=None):
        self.name = name
        self.kind = kind          # 'variable', 'function', 'parameter'
        self.type_spec = type_spec
        self.scope = scope
        self.line = line
        self.column = column
        self.definition_loc = {"file": "source.c", "line": line, "column": column}
        self.references = []      # لیست نقاط استفاده: [{"file":..., "line":..., "col":...}]
        self.signature = signature # برای توابع
        self.is_initialized = False
        self.is_used = False

class SymbolTable:
    def __init__(self, parent=None, scope_name="Global", line_range=(1, 9999)):
        self.symbols = {}
        self.parent = parent
        self.scope_name = scope_name
        self.line_range = line_range
        self.children = []
        if parent:
            parent.children.append(self)

    def define(self, symbol: Symbol) -> bool:
        if symbol.name in self.symbols:
            return False
        symbol.scope = self
        self.symbols[symbol.name] = symbol
        return True

    def lookup(self, name: str):
        if name in self.symbols:
            return self.symbols[name], self
        if self.parent:
            return self.parent.lookup(name)
        return None, None

    def get_scope_at(self, line: int):
        for child in self.children:
            if child.line_range[0] <= line <= child.line_range[1]:
                return child.get_scope_at(line)
        return self

class SemanticAnalyzer:
    def __init__(self, file_name="source.c"):
        self.file_name = file_name
        self.global_scope = SymbolTable(scope_name="Global")
        self.current_scope = self.global_scope
        self.diagnostics = []
        self.current_function_return_type = None

    def analyze(self, ast: ProgramNode):
        # Pass 1: ثبت همه توابع در Global Scope (پشتیبانی از Forward Reference)
        for decl in ast.declarations:
            if isinstance(decl, FunctionDeclNode):
                sym = Symbol(decl.name, 'function', decl.return_type, decl.line, decl.column, signature=[p[0] for p in decl.params])
                if not self.global_scope.define(sym):
                    self.diagnostics.append(Diagnostic('Error', f"Duplicate function declaration '{decl.name}'", self.file_name, decl.line, decl.column, len(decl.name)))

        # Pass 2: بررسی عمیق Scopeها، Typeها و Diagnostics
        self._visit(ast)
        self._check_unused_symbols(self.global_scope)
        return self.diagnostics

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
        self.current_function_return_type = node.return_type
        
        end_line = node.body.line + 20
        func_scope = SymbolTable(parent=self.current_scope, scope_name=f"Function_{node.name}", line_range=(node.line, end_line))
        self.current_scope = func_scope

        for p_type, p_name in node.params:
            p_sym = Symbol(p_name, 'parameter', p_type, node.line, node.column)
            p_sym.is_initialized = True
            p_sym.is_used = True
            if not self.current_scope.define(p_sym):
                self.diagnostics.append(Diagnostic('Error', f"Duplicate parameter '{p_name}'", self.file_name, node.line, node.column, len(p_name)))

        self._visit(node.body)
        self._check_unused_symbols(self.current_scope)
        self.current_scope = self.current_scope.parent
        self.current_function_return_type = None

    def _visit_VarDeclNode(self, node: VarDeclNode):
        init_type = None
        if node.init_expr:
            init_type = self._visit(node.init_expr)

        # بررسی Shadowing
        existing_sym, existing_scope = self.current_scope.lookup(node.name)
        if existing_sym and existing_scope != self.current_scope:
            self.diagnostics.append(Diagnostic('Warning', f"Variable '{node.name}' shadows outer declaration", self.file_name, node.line, node.column, len(node.name)))

        sym = Symbol(node.name, 'variable', node.type_spec, node.line, node.column)
        if node.init_expr:
            sym.is_initialized = True
            if init_type and init_type != node.type_spec and init_type != 'unknown':
                self.diagnostics.append(Diagnostic('Error', f"Type mismatch in assignment to '{node.name}'. Expected {node.type_spec}, got {init_type}", self.file_name, node.line, node.column, len(node.name)))

        if not self.current_scope.define(sym):
            self.diagnostics.append(Diagnostic('Error', f"Duplicate variable declaration '{node.name}'", self.file_name, node.line, node.column, len(node.name)))

        node.inferred_type = node.type_spec

    def _visit_BlockNode(self, node: BlockNode):
        block_scope = SymbolTable(parent=self.current_scope, scope_name="Block", line_range=(node.line, node.line + 10))
        self.current_scope = block_scope
        for stmt in node.statements:
            self._visit(stmt)
        self._check_unused_symbols(self.current_scope)
        self.current_scope = self.current_scope.parent

    def _visit_ReturnStmtNode(self, node: ReturnStmtNode):
        ret_type = self._visit(node.expr) if node.expr else 'void'
        if self.current_function_return_type and ret_type != self.current_function_return_type and ret_type != 'unknown':
            self.diagnostics.append(Diagnostic('Error', f"Return type mismatch. Function expects {self.current_function_return_type}, got {ret_type}", self.file_name, node.line, node.column, 6))

    def _visit_AssignmentNode(self, node: AssignmentNode):
        expr_type = self._visit(node.expr)
        sym, _ = self.current_scope.lookup(node.name)
        if not sym:
            self.diagnostics.append(Diagnostic('Error', f"Undefined variable '{node.name}'", self.file_name, node.line, node.column, len(node.name)))
            return 'unknown'

        sym.is_used = True
        sym.is_initialized = True
        sym.references.append({"file": self.file_name, "line": node.line, "col": node.column})

        if expr_type and expr_type != sym.type_spec and expr_type != 'unknown':
            self.diagnostics.append(Diagnostic('Error', f"Type mismatch in assignment to '{node.name}'. Expected {sym.type_spec}, got {expr_type}", self.file_name, node.line, node.column, len(node.name)))
        return sym.type_spec

    def _visit_BinaryExprNode(self, node: BinaryExprNode):
        left_t = self._visit(node.left)
        right_t = self._visit(node.right)
        if left_t != right_t and 'unknown' not in (left_t, right_t):
            self.diagnostics.append(Diagnostic('Error', f"Type mismatch in binary operation '{node.op}' between {left_t} and {right_t}", self.file_name, node.line, node.column, len(node.op)))
        node.inferred_type = left_t if left_t != 'unknown' else right_t
        return node.inferred_type

    def _visit_CallExprNode(self, node: CallExprNode):
        sym, _ = self.current_scope.lookup(node.callee)
        if not sym or sym.kind != 'function':
            self.diagnostics.append(Diagnostic('Error', f"Undefined function '{node.callee}'", self.file_name, node.line, node.column, len(node.callee)))
            return 'unknown'

        sym.is_used = True
        sym.references.append({"file": self.file_name, "line": node.line, "col": node.column})

        if len(node.args) != len(sym.signature):
            self.diagnostics.append(Diagnostic('Error', f"Function '{node.callee}' expects {len(sym.signature)} arguments, got {len(node.args)}", self.file_name, node.line, node.column, len(node.callee)))

        for arg, expected_type in zip(node.args, sym.signature):
            arg_t = self._visit(arg)
            if arg_t != expected_type and arg_t != 'unknown':
                self.diagnostics.append(Diagnostic('Error', f"Argument type mismatch in call to '{node.callee}'. Expected {expected_type}, got {arg_t}", self.file_name, node.line, node.column, 5))

        node.inferred_type = sym.type_spec
        return sym.type_spec

    def _visit_IdentifierNode(self, node: IdentifierNode):
        sym, _ = self.current_scope.lookup(node.name)
        if not sym:
            self.diagnostics.append(Diagnostic('Error', f"Undefined identifier '{node.name}'", self.file_name, node.line, node.column, len(node.name)))
            return 'unknown'
        
        if not sym.is_initialized and sym.kind == 'variable':
            self.diagnostics.append(Diagnostic('Warning', f"Variable '{node.name}' used before initialization", self.file_name, node.line, node.column, len(node.name)))

        sym.is_used = True
        sym.references.append({"file": self.file_name, "line": node.line, "col": node.column})
        node.inferred_type = sym.type_spec
        return sym.type_spec

    def _visit_LiteralNode(self, node: LiteralNode):
        node.inferred_type = node.literal_type
        return node.literal_type

    def _check_unused_symbols(self, scope: SymbolTable):
        for name, sym in scope.symbols.items():
            if not sym.is_used and sym.kind == 'variable':
                self.diagnostics.append(Diagnostic('Info', f"Unused variable '{name}'", self.file_name, sym.line, sym.column, len(name)))