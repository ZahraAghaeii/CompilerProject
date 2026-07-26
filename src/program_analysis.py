import difflib
from src.ast_nodes import FunctionDeclNode, CallExprNode, IdentifierNode, VarDeclNode, ReturnStmtNode, IfStmtNode, AssignmentNode

class BasicBlock:
    def __init__(self, block_id: int, label=""):
        self.block_id = block_id
        self.label = label
        self.statements = []
        self.successors = []
        self.predecessors = []

    def add_successor(self, succ):
        if succ not in self.successors:
            self.successors.append(succ)
            succ.predecessors.append(self)

    def __repr__(self):
        return f"Block_{self.block_id} [{self.label}]"


class CFGBuilder:
    def __init__(self):
        self.block_counter = 0

    def _next_id(self):
        self.block_counter += 1
        return self.block_counter

    def build_cfg(self, func_node: FunctionDeclNode):
        self.block_counter = 0
        entry_block = BasicBlock(self._next_id(), "ENTRY")
        exit_block = BasicBlock(self._next_id(), "EXIT")
        
        first_block = BasicBlock(self._next_id(), "B1")
        entry_block.add_successor(first_block)

        curr = self._process_statements(func_node.body.statements, first_block, exit_block)
        if curr and exit_block not in curr.successors:
            curr.add_successor(exit_block)

        return entry_block, exit_block

    def _process_statements(self, statements, current_block, exit_block):
        curr = current_block
        for stmt in statements:
            if isinstance(stmt, ReturnStmtNode):
                curr.statements.append(stmt)
                curr.add_successor(exit_block)
                return None

            elif isinstance(stmt, IfStmtNode):
                curr.statements.append(stmt.condition)
                
                then_block = BasicBlock(self._next_id(), "THEN")
                else_block = BasicBlock(self._next_id(), "ELSE")
                merge_block = BasicBlock(self._next_id(), "JOIN")

                curr.add_successor(then_block)
                curr.add_successor(else_block if stmt.else_branch else merge_block)

                then_stmts = stmt.then_branch.statements if hasattr(stmt.then_branch, 'statements') else [stmt.then_branch]
                then_end = self._process_statements(then_stmts, then_block, exit_block)
                if then_end:
                    then_end.add_successor(merge_block)

                if stmt.else_branch:
                    else_stmts = stmt.else_branch.statements if hasattr(stmt.else_branch, 'statements') else [stmt.else_branch]
                    else_end = self._process_statements(else_stmts, else_block, exit_block)
                    if else_end:
                        else_end.add_successor(merge_block)

                curr = merge_block
            else:
                curr.statements.append(stmt)
        return curr


class ProgramAnalyzer:
    def __init__(self, ast, symbol_table, code: str, file_name="semantic_test.c"):
        self.ast = ast
        self.global_scope = symbol_table
        self.code = code
        self.file_name = file_name
        self.code_lines = code.split('\n')

    def build_call_graph(self):
        graph = {}
        for decl in self.ast.declarations:
            if isinstance(decl, FunctionDeclNode):
                graph[decl.name] = set()
                self._extract_calls(decl.body, graph[decl.name])
        return graph

    def _extract_calls(self, node, calls_set):
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
                            self._extract_calls(item, calls_set)
                elif hasattr(val, 'line'):
                    self._extract_calls(val, calls_set)

    def detect_recursive_functions(self):
        cg = self.build_call_graph()
        return [func for func, callees in cg.items() if func in callees]

    def goto_definition_json(self, symbol_name: str):
        sym, scope = self.global_scope.lookup(symbol_name)
        if not sym:
            return {"error": f"Symbol '{symbol_name}' not found"}

        refs = []
        for r in sym.references:
            refs.append({"file": r["file"], "line": r["line"], "col": r["col"]})

        return {
            "symbol": sym.name,
            "kind": sym.kind,
            "type": sym.type_spec + (f"({', '.join(sym.signature)})" if sym.signature else ""),
            "defined_at": sym.definition_loc,
            "references": refs
        }

    def hover_info(self, symbol_name: str):
        sym, scope = self.global_scope.lookup(symbol_name)
        if not sym:
            return "Symbol not found"
        sig = f"({', '.join(sym.signature)}) -> {sym.type_spec}" if sym.signature else f": {sym.type_spec}"
        return f"[{sym.kind.upper()}] {sym.name}{sig}\nDefined at line {sym.line}, scope: {scope.scope_name}"

    def safe_rename(self, target_symbol: str, new_name: str, target_line: int):
        sym, scope = self.global_scope.lookup(target_symbol)
        if not sym:
            return False, "Symbol not found.", ""

        if new_name in scope.symbols:
            return False, f"Conflict error: Symbol '{new_name}' already exists in scope '{scope.scope_name}'.", ""

        affected_locations = [sym.definition_loc] + sym.references
        new_lines = list(self.code_lines)
        for loc in affected_locations:
            l_idx = loc['line'] - 1
            line_str = new_lines[l_idx]
            new_lines[l_idx] = line_str.replace(target_symbol, new_name)

        diff = list(difflib.unified_diff(
            self.code_lines, new_lines,
            fromfile=self.file_name, tofile=f"{self.file_name} (renamed)"
        ))
        return True, "\n".join(new_lines), "\n".join(diff)

    def detect_dead_code(self):
        reports = []
        cg = self.build_call_graph()
        
        all_funcs = set(cg.keys())
        reachable = {"main"}
        queue = ["main"]
        while queue:
            curr = queue.pop(0)
            for callee in cg.get(curr, []):
                if callee in all_funcs and callee not in reachable:
                    reachable.add(callee)
                    queue.append(callee)

        unreachable_funcs = all_funcs - reachable
        for uf in unreachable_funcs:
            reports.append(f"💀 DEAD FUNCTION: '{uf}' is never reachable from 'main'")

        self._check_dead_vars_in_scope(self.global_scope, reports)

        if not reports:
            reports.append("✅ No dead code detected!")

        return reports

    def _check_dead_vars_in_scope(self, scope, reports):
        for sym in scope.symbols.values():
            if sym.kind == 'variable' and not sym.is_used:
                reports.append(f"⚠️ UNUSED VARIABLE: '{sym.name}' declared at line {sym.line} is never read")