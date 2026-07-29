import difflib
import re

from src.ast_nodes import (
    FunctionDeclNode, CallExprNode, ReturnStmtNode, IfStmtNode, WhileStmtNode, ForStmtNode, BreakStmtNode,
    ContinueStmtNode
)


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

    def _process_statements(self, statements, current_block, exit_block, loop_start=None, loop_end=None):
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

                then_stmts = stmt.then_branch.statements if hasattr(stmt.then_branch, 'statements') else [
                    stmt.then_branch]
                then_end = self._process_statements(then_stmts, then_block, exit_block, loop_start, loop_end)
                if then_end:
                    then_end.add_successor(merge_block)

                if stmt.else_branch:
                    else_stmts = stmt.else_branch.statements if hasattr(stmt.else_branch, 'statements') else [
                        stmt.else_branch]
                    else_end = self._process_statements(else_stmts, else_block, exit_block, loop_start, loop_end)
                    if else_end:
                        else_end.add_successor(merge_block)

                curr = merge_block

            elif isinstance(stmt, WhileStmtNode):
                cond_block = BasicBlock(self._next_id(), "WHILE_COND")
                body_block = BasicBlock(self._next_id(), "WHILE_BODY")
                end_block = BasicBlock(self._next_id(), "WHILE_END")

                curr.add_successor(cond_block)
                cond_block.statements.append(stmt.condition)

                cond_block.add_successor(body_block)
                cond_block.add_successor(end_block)

                body_stmts = stmt.body.statements if hasattr(stmt.body, 'statements') else [stmt.body]
                body_end = self._process_statements(body_stmts, body_block, exit_block, loop_start=cond_block,
                                                    loop_end=end_block)

                if body_end:
                    body_end.add_successor(cond_block)

                curr = end_block

            elif isinstance(stmt, ForStmtNode):
                if stmt.init:
                    curr.statements.append(stmt.init)

                cond_block = BasicBlock(self._next_id(), "FOR_COND")
                body_block = BasicBlock(self._next_id(), "FOR_BODY")
                step_block = BasicBlock(self._next_id(), "FOR_STEP")
                end_block = BasicBlock(self._next_id(), "FOR_END")

                curr.add_successor(cond_block)
                if stmt.condition:
                    cond_block.statements.append(stmt.condition)

                cond_block.add_successor(body_block)
                cond_block.add_successor(end_block)

                if stmt.step:
                    step_block.statements.append(stmt.step)
                step_block.add_successor(cond_block)

                body_stmts = stmt.body.statements if hasattr(stmt.body, 'statements') else [stmt.body]
                body_end = self._process_statements(body_stmts, body_block, exit_block, loop_start=step_block,
                                                    loop_end=end_block)

                if body_end:
                    body_end.add_successor(step_block)

                curr = end_block

            elif isinstance(stmt, BreakStmtNode):
                curr.statements.append(stmt)
                if loop_end:
                    curr.add_successor(loop_end)
                return None

            elif isinstance(stmt, ContinueStmtNode):
                curr.statements.append(stmt)
                if loop_start:
                    curr.add_successor(loop_start)
                return None

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

    def goto_definition_json(self, symbol_name: str, target_line: int):
        sym, scope = self._find_symbol_by_line(self.global_scope, symbol_name, target_line)

        if not sym:
            return {"error": f"Symbol '{symbol_name}' not found at line {target_line}"}

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

    def hover_info(self, symbol_name: str, target_line: int):
        sym, scope = self._find_symbol_by_line(self.global_scope, symbol_name, target_line)

        if not sym:
            return "Symbol not found"
        sig = f"({', '.join(sym.signature)}) -> {sym.type_spec}" if sym.signature else f": {sym.type_spec}"
        return f"[{sym.kind.upper()}] {sym.name}{sig}\nDefined at line {sym.line}, scope: {scope.scope_name}"

    def safe_rename(self, target_symbol: str, new_name: str, target_line: int):
        sym, scope = self._find_symbol_by_line(self.global_scope, target_symbol, target_line)

        if not sym:
            return False, f"Symbol '{target_symbol}' not found at line {target_line}.", ""

        if new_name in scope.symbols and scope.symbols[new_name] != sym:
            return False, f"Conflict error: Symbol '{new_name}' already exists in scope '{scope.scope_name}'.", ""

        affected_locations = [sym.definition_loc] + sym.references
        new_lines = list(self.code_lines)
        for loc in affected_locations:
            l_idx = loc['line'] - 1
            line_str = new_lines[l_idx]
            new_lines[l_idx] = re.sub(rf'\b{target_symbol}\b', new_name, line_str)

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
            reports.append(f"  DEAD FUNCTION: '{uf}' is never reachable from 'main'")

        self._check_dead_vars_in_scope(self.global_scope, reports)

        from src.ast_nodes import BlockNode, ReturnStmtNode, BreakStmtNode, ContinueStmtNode

        def check_unreachable_stmts(node):
            if not node:
                return
            if isinstance(node, BlockNode):
                found_jump = False
                for stmt in node.statements:
                    if found_jump:
                        reports.append(
                            f"  UNREACHABLE CODE: Statement at line {stmt.line} is dead code (after return/break/continue)")
                    if isinstance(stmt, (ReturnStmtNode, BreakStmtNode, ContinueStmtNode)):
                        found_jump = True
                    else:
                        check_unreachable_stmts(stmt)
            else:
                for attr in dir(node):
                    if not attr.startswith('_'):
                        val = getattr(node, attr)
                        if isinstance(val, list):
                            for item in val:
                                if hasattr(item, 'line'):
                                    check_unreachable_stmts(item)
                        elif hasattr(val, 'line'):
                            check_unreachable_stmts(val)

        check_unreachable_stmts(self.ast)

        if not reports:
            reports.append("  No dead code detected!")

        return reports

    def _check_dead_vars_in_scope(self, scope, reports):
        if not scope:
            return

        for sym in scope.symbols.values():
            if sym.kind == 'variable' and not sym.is_used:
                reports.append(f"  UNUSED VARIABLE: '{sym.name}' declared at line {sym.line} is never read")

        if hasattr(scope, 'children'):
            for child in scope.children:
                self._check_dead_vars_in_scope(child, reports)

    def analyze_definite_assignment(self):
        reports = []
        from src.ast_nodes import FunctionDeclNode, AssignmentNode, IdentifierNode, VarDeclNode

        cfg_builder = CFGBuilder()

        for decl in self.ast.declarations:
            if not isinstance(decl, FunctionDeclNode) or not decl.body:
                continue

            entry_block, exit_block = cfg_builder.build_cfg(decl)

            blocks = []
            queue = [entry_block]
            visited = {entry_block.block_id}
            while queue:
                curr = queue.pop(0)
                blocks.append(curr)
                for succ in curr.successors:
                    if succ.block_id not in visited:
                        visited.add(succ.block_id)
                        queue.append(succ)

            assigned_initially = set()
            for p in getattr(decl, 'params', []):
                p_name = p[1] if isinstance(p, tuple) else getattr(p, 'name', '')
                if p_name: assigned_initially.add(p_name)

            all_vars = set()
            for b in blocks:
                for stmt in b.statements:
                    if isinstance(stmt, VarDeclNode): all_vars.add(stmt.name)

            in_sets = {b.block_id: set(all_vars) for b in blocks}
            in_sets[entry_block.block_id] = set(assigned_initially)
            out_sets = {b.block_id: set(all_vars) for b in blocks}
            out_sets[entry_block.block_id] = set(assigned_initially)

            def get_def_use(stmt):
                defs, uses = set(), set()
                if isinstance(stmt, VarDeclNode) and stmt.init_expr:
                    defs.add(stmt.name)
                elif isinstance(stmt, AssignmentNode):
                    defs.add(stmt.name)

                def extract_uses(node):
                    if not node: return
                    if isinstance(node, IdentifierNode): uses.add(node.name)
                    for attr in dir(node):
                        if not attr.startswith('_') and attr != 'name':
                            val = getattr(node, attr)
                            if isinstance(val, list):
                                for item in val:
                                    if hasattr(item, 'line'): extract_uses(item)
                            elif hasattr(val, 'line'):
                                extract_uses(val)

                if isinstance(stmt, AssignmentNode):
                    extract_uses(stmt.expr)
                elif isinstance(stmt, VarDeclNode):
                    extract_uses(stmt.init_expr)
                else:
                    extract_uses(stmt)

                return defs, uses

            changed = True
            while changed:
                changed = False
                for b in blocks:
                    if b == entry_block: continue

                    if b.predecessors:
                        new_in = set.intersection(*(out_sets[p.block_id] for p in b.predecessors))
                    else:
                        new_in = set()

                    in_sets[b.block_id] = new_in

                    current_out = set(new_in)
                    for stmt in b.statements:
                        defs, _ = get_def_use(stmt)
                        current_out.update(defs)

                    if current_out != out_sets[b.block_id]:
                        out_sets[b.block_id] = current_out
                        changed = True

            for b in blocks:
                current_assigned = set(in_sets[b.block_id])
                for stmt in b.statements:
                    defs, uses = get_def_use(stmt)
                    for u in uses:
                        if u in all_vars and u not in current_assigned:
                            line = getattr(stmt, 'line', 'unknown')
                            reports.append(
                                f"  DATA-FLOW WARNING: Variable '{u}' may be used uninitialized on some paths at line {line} in function '{decl.name}'")
                    current_assigned.update(defs)

        if not reports:
            reports.append("  No Data-Flow warnings detected. All variables are safely assigned.")

        return reports

    def _find_symbol_by_line(self, scope, name, line):
        if name in scope.symbols:
            sym = scope.symbols[name]
            if sym.line == line or any(r['line'] == line for r in sym.references):
                return sym, scope

        for child in getattr(scope, 'children', []):
            res, child_scope = self._find_symbol_by_line(child, name, line)
            if res:
                return res, child_scope

        return None, None