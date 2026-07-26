from src.ast_nodes import FunctionDeclNode, CallExprNode, IdentifierNode, VarDeclNode, ReturnStmtNode, IfStmtNode

class BasicBlock:
    def __init__(self, block_id: int, label=""):
        self.block_id = block_id
        self.label = label
        self.statements = []
        self.successors = []

    def __repr__(self):
        stmts_str = ", ".join([s.__class__.__name__ for s in self.statements])
        return f"Block_{self.block_id} [{self.label}] -> ({stmts_str})"

class CFGBuilder:
    def __init__(self):
        self.block_counter = 0

    def build_cfg(self, func_node: FunctionDeclNode):
        self.block_counter = 0
        entry_block = BasicBlock(self._next_id(), "ENTRY")
        exit_block = BasicBlock(self._next_id(), "EXIT")
        
        current_block = BasicBlock(self._next_id(), "B1")
        entry_block.successors.append(current_block)

        self._process_statements(func_node.body.statements, current_block, exit_block)
        return entry_block

    def _next_id(self):
        self.block_counter += 1
        return self.block_counter

    def _process_statements(self, statements, current_block, exit_block):
        curr = current_block
        for stmt in statements:
            if isinstance(stmt, IfStmtNode):
                cond_block = curr
                cond_block.statements.append(stmt.condition)

                then_block = BasicBlock(self._next_id(), "THEN")
                cond_block.successors.append(then_block)
                then_stmts = stmt.then_branch.statements if hasattr(stmt.then_branch, 'statements') else [stmt.then_branch]
                self._process_statements(then_stmts, then_block, exit_block)

                if stmt.else_branch:
                    else_block = BasicBlock(self._next_id(), "ELSE")
                    cond_block.successors.append(else_block)
                    else_stmts = stmt.else_branch.statements if hasattr(stmt.else_branch, 'statements') else [stmt.else_branch]
                    self._process_statements(else_stmts, else_block, exit_block)
                else:
                    cond_block.successors.append(exit_block)

            elif isinstance(stmt, ReturnStmtNode):
                curr.statements.append(stmt)
                curr.successors.append(exit_block)
            else:
                curr.statements.append(stmt)


class CallGraphBuilder:
    @classmethod
    def build_call_graph(cls, ast):
        call_graph = {}
        for decl in ast.declarations:
            if isinstance(decl, FunctionDeclNode):
                func_name = decl.name
                call_graph[func_name] = set()
                cls._extract_calls(decl.body, call_graph[func_name])
        return call_graph

    @classmethod
    def _extract_calls(cls, node, calls_set):
        if not node:
            return
        if isinstance(node, CallExprNode):
            calls_set.add(node.callee)
        
        for attr in dir(node):
            if not attr.startswith('_'):
                val = getattr(node, attr)
                if isinstance(val, list):
                    for item in val:
                        if hasattr(item, 'line'):
                            cls._extract_calls(item, calls_set)
                elif hasattr(val, 'line'):
                    cls._extract_calls(val, calls_set)


class RefactoringEngine:
    def __init__(self, ast, code: str):
        self.ast = ast
        self.code_lines = code.split('\n')

    def goto_definition(self, symbol_name: str):
        for decl in self.ast.declarations:
            if isinstance(decl, FunctionDeclNode) and decl.name == symbol_name:
                return {"file": "semantic_test.c", "line": decl.line, "col": decl.column, "type": "function"}
            if isinstance(decl, VarDeclNode) and decl.name == symbol_name:
                return {"file": "semantic_test.c", "line": decl.line, "col": decl.column, "type": "variable"}
            
            if isinstance(decl, FunctionDeclNode):
                for stmt in decl.body.statements:
                    if isinstance(stmt, VarDeclNode) and stmt.name == symbol_name:
                        return {"file": "semantic_test.c", "line": stmt.line, "col": stmt.column, "type": "variable"}
        return None

    def find_all_references(self, symbol_name: str):
        refs = []
        self._find_refs_in_node(self.ast, symbol_name, refs)
        return refs

    def _find_refs_in_node(self, node, symbol_name, refs):
        if not node:
            return
        if isinstance(node, IdentifierNode) and node.name == symbol_name:
            refs.append({"line": node.line, "col": node.column})
        if isinstance(node, CallExprNode) and node.callee == symbol_name:
            refs.append({"line": node.line, "col": node.column})
        if isinstance(node, (VarDeclNode, FunctionDeclNode)) and node.name == symbol_name:
            refs.append({"line": node.line, "col": node.column})

        for attr in dir(node):
            if not attr.startswith('_'):
                val = getattr(node, attr)
                if isinstance(val, list):
                    for item in val:
                        if hasattr(item, 'line'):
                            self._find_refs_in_node(item, symbol_name, refs)
                elif hasattr(val, 'line'):
                    self._find_refs_in_node(val, symbol_name, refs)

    def safe_rename(self, old_name: str, new_name: str):
        refs = self.find_all_references(old_name)
        if not refs:
            return False, "Symbol not found"

        new_lines = list(self.code_lines)
        for ref in refs:
            line_idx = ref['line'] - 1
            line_content = new_lines[line_idx]
            new_lines[line_idx] = line_content.replace(old_name, new_name)

        return True, "\n".join(new_lines)