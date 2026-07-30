"""
Intermediate Code Generator (Three-Address Code - TAC)
Bonus Feature: Generates linear intermediate code representation from AST.
"""

class TACInstruction:
    def __init__(self, op, arg1, arg2, result):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    def __repr__(self):
        if self.op == '=':
            return f"{self.result} = {self.arg1}"
        elif self.op in ['+', '-', '*', '/', '%', '<', '>', '<=', '>=', '==', '!=']:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        elif self.op == 'LABEL':
            return f"{self.result}:"
        elif self.op == 'JUMP':
            return f"goto {self.result}"
        elif self.op == 'JUMP_IF_FALSE':
            return f"ifFalse {self.arg1} goto {self.result}"
        elif self.op == 'RETURN':
            return f"RETURN {self.arg1 if self.arg1 else ''}".strip()
        elif self.op == 'PARAM':
            return f"param {self.arg1}"
        elif self.op == 'CALL':
            return f"{self.result} = call {self.arg1}, {self.arg2}"
        return f"{self.op} {self.arg1} {self.arg2} {self.result}"


class IRGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0

    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def generate(self, node):
        if not node:
            return ""
        method_name = f"gen_{type(node).__name__}"
        generator = getattr(self, method_name, self.generic_gen)
        return generator(node)

    def generic_gen(self, node):
        if hasattr(node, 'statements') and isinstance(node.statements, list):
            for stmt in node.statements:
                self.generate(stmt)
        elif hasattr(node, 'body'):
            self.generate(node.body)
        return None

    def gen_ProgramNode(self, node):
        for decl in getattr(node, 'declarations', []):
            self.generate(decl)
        return self.get_code()

    def gen_FunctionDeclNode(self, node):
        func_label = getattr(node, 'name', 'func')
        self.instructions.append(TACInstruction('LABEL', None, None, func_label))
        if hasattr(node, 'body') and node.body:
            if hasattr(node.body, 'statements'):
                for stmt in node.body.statements:
                    self.generate(stmt)
            else:
                self.generate(node.body)

    def gen_VarDeclNode(self, node):
        init_expr = getattr(node, 'init_expr', getattr(node, 'initializer', None))
        if init_expr:
            val = self.generate(init_expr)
            self.instructions.append(TACInstruction('=', val, None, node.name))
        return node.name

    def gen_AssignmentNode(self, node):
        val = self.generate(node.expr)
        target = getattr(node, 'name', 'var')
        self.instructions.append(TACInstruction('=', val, None, target))
        return target

    def gen_BinaryOpNode(self, node):
        left = self.generate(node.left)
        right = self.generate(node.right)
        temp = self.new_temp()
        self.instructions.append(TACInstruction(node.op, left, right, temp))
        return temp

    def gen_BinaryExprNode(self, node):
        left = self.generate(node.left)
        right = self.generate(node.right)
        temp = self.new_temp()
        self.instructions.append(TACInstruction(node.op, left, right, temp))
        return temp

    def gen_LiteralNode(self, node):
        return str(node.value)

    def gen_IdentifierNode(self, node):
        return str(node.name)

    def gen_VariableNode(self, node):
        return str(node.name)

    def gen_ReturnNode(self, node):
        val = self.generate(node.expr) if hasattr(node, 'expr') and node.expr else ""
        self.instructions.append(TACInstruction('RETURN', val, None, None))

    def gen_ReturnStmtNode(self, node):
        val = self.generate(node.expr) if hasattr(node, 'expr') and node.expr else ""
        self.instructions.append(TACInstruction('RETURN', val, None, None))

    def get_code(self):
        return "\n".join(str(instr) for instr in self.instructions)