class ASTNode:
    def __init__(self, line: int, column: int):
        self.line = line
        self.column = column
        self.inferred_type = None  # برای استفاده در فاز ۲

class ProgramNode(ASTNode):
    def __init__(self, declarations, line=1, column=1):
        super().__init__(line, column)
        self.declarations = declarations

class VarDeclNode(ASTNode):
    def __init__(self, type_spec: str, name: str, init_expr, line: int, column: int):
        super().__init__(line, column)
        self.type_spec = type_spec
        self.name = name
        self.init_expr = init_expr

class FunctionDeclNode(ASTNode):
    def __init__(self, return_type: str, name: str, params: list, body, line: int, column: int):
        super().__init__(line, column)
        self.return_type = return_type
        self.name = name
        self.params = params  # لیست زوج (type, name)
        self.body = body

class BlockNode(ASTNode):
    def __init__(self, statements: list, line: int, column: int):
        super().__init__(line, column)
        self.statements = statements

class IfStmtNode(ASTNode):
    def __init__(self, condition, then_branch, else_branch, line: int, column: int):
        super().__init__(line, column)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class WhileStmtNode(ASTNode):
    def __init__(self, condition, body, line: int, column: int):
        super().__init__(line, column)
        self.condition = condition
        self.body = body

class ReturnStmtNode(ASTNode):
    def __init__(self, expr, line: int, column: int):
        super().__init__(line, column)
        self.expr = expr

class BinaryExprNode(ASTNode):
    def __init__(self, left, op: str, right, line: int, column: int):
        super().__init__(line, column)
        self.left = left
        self.op = op
        self.right = right

class AssignmentNode(ASTNode):
    def __init__(self, name: str, op: str, expr, line: int, column: int):
        super().__init__(line, column)
        self.name = name
        self.op = op
        self.expr = expr

class CallExprNode(ASTNode):
    def __init__(self, callee: str, args: list, line: int, column: int):
        super().__init__(line, column)
        self.callee = callee
        self.args = args

class IdentifierNode(ASTNode):
    def __init__(self, name: str, line: int, column: int):
        super().__init__(line, column)
        self.name = name

class LiteralNode(ASTNode):
    def __init__(self, value, literal_type: str, line: int, column: int):
        super().__init__(line, column)
        self.value = value
        self.literal_type = literal_type