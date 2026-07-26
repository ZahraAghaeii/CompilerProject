from src.lexer import TokenType, Token
from src.ast_nodes import *

class Parser:
    def __init__(self, tokens: list):
        self.tokens = [t for t in tokens if t.type != TokenType.COMMENT and t.type != TokenType.PREPROCESSOR]
        self.pos = 0
        self.errors = []

    def _peek(self, offset=0) -> Token:
        target = self.pos + offset
        if target < len(self.tokens):
            return self.tokens[target]
        return self.tokens[-1]

    def _match(self, *expected_values) -> bool:
        current = self._peek()
        if current.value in expected_values or current.type in expected_values:
            self.pos += 1
            return True
        return False

    def _consume(self, expected_value, error_message: str) -> Token:
        current = self._peek()
        if current.value == expected_value or current.type == expected_value:
            self.pos += 1
            return current
        self.errors.append(f"Parser Error at {current.line}:{current.column}: {error_message} (Got '{current.value}')")
        return None

    def _synchronize(self):
        """Panic-mode recovery"""
        self.pos += 1
        while self.pos < len(self.tokens):
            if self._peek(-1).value in (';', '}'):
                return
            if self._peek().value in ('if', 'while', 'for', 'return', 'int', 'float', 'char', 'void'):
                return
            self.pos += 1

    def parse(self) -> ProgramNode:
        declarations = []
        start_token = self._peek()
        while self._peek().type != TokenType.EOF:
            try:
                decl = self._parse_declaration()
                if decl:
                    declarations.append(decl)
            except Exception as e:
                self._synchronize()
        return ProgramNode(declarations, start_token.line, start_token.column)

    def _parse_declaration(self):
        type_token = self._peek()
        if type_token.value in ('int', 'float', 'char', 'void', 'double'):
            self.pos += 1
            name_token = self._consume(TokenType.IDENTIFIER, "Expected function or variable name")
            if not name_token:
                self._synchronize()
                return None

            if self._peek().value == '(':
                # Function declaration
                self.pos += 1
                params = self._parse_param_list()
                self._consume(')', "Expected ')' after parameters")
                body = self._parse_block()
                return FunctionDeclNode(type_token.value, name_token.value, params, body, type_token.line, type_token.column)
            else:
                # Variable declaration
                init_expr = None
                if self._match('='):
                    init_expr = self._parse_expression()
                self._consume(';', "Expected ';' after variable declaration")
                return VarDeclNode(type_token.value, name_token.value, init_expr, type_token.line, type_token.column)

        self.errors.append(f"Parser Error at {type_token.line}:{type_token.column}: Unexpected token '{type_token.value}'")
        self._synchronize()
        return None

    def _parse_param_list(self) -> list:
        params = []
        if self._peek().value != ')':
            while True:
                p_type = self._peek().value
                if p_type in ('int', 'float', 'char', 'void', 'double'):
                    self.pos += 1
                    p_name = self._consume(TokenType.IDENTIFIER, "Expected parameter name")
                    if p_name:
                        params.append((p_type, p_name.value))
                if not self._match(','):
                    break
        return params

    def _parse_block(self) -> BlockNode:
        token = self._consume('{', "Expected '{' to start block")
        line, col = (token.line, token.column) if token else (1, 1)
        statements = []
        while self._peek().value != '}' and self._peek().type != TokenType.EOF:
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        self._consume('}', "Expected '}' after block")
        return BlockNode(statements, line, col)

    def _parse_statement(self):
        curr = self._peek()
        if curr.value in ('int', 'float', 'char', 'void', 'double'):
            return self._parse_declaration()
        elif curr.value == 'if':
            self.pos += 1
            self._consume('(', "Expected '(' after 'if'")
            cond = self._parse_expression()
            self._consume(')', "Expected ')' after if condition")
            then_b = self._parse_statement()
            else_b = None
            if self._match('else'):
                else_b = self._parse_statement()
            return IfStmtNode(cond, then_b, else_b, curr.line, curr.column)
        elif curr.value == 'while':
            self.pos += 1
            self._consume('(', "Expected '(' after 'while'")
            cond = self._parse_expression()
            self._consume(')', "Expected ')' after condition")
            body = self._parse_statement()
            return WhileStmtNode(cond, body, curr.line, curr.column)
        elif curr.value == 'return':
            self.pos += 1
            expr = None
            if self._peek().value != ';':
                expr = self._parse_expression()
            self._consume(';', "Expected ';' after return")
            return ReturnStmtNode(expr, curr.line, curr.column)
        elif curr.value == '{':
            return self._parse_block()
        else:
            expr = self._parse_expression()
            self._consume(';', "Expected ';' after expression")
            return expr

    def _parse_expression(self):
        return self._parse_assignment()

    def _parse_assignment(self):
        if self._peek().type == TokenType.IDENTIFIER and self._peek(1).value in ('=', '+=', '-=', '*=', '/='):
            name_tok = self.pos
            name = self.tokens[name_tok].value
            op = self.tokens[name_tok + 1].value
            self.pos += 2
            expr = self._parse_assignment()
            return AssignmentNode(name, op, expr, self.tokens[name_tok].line, self.tokens[name_tok].column)
        return self._parse_relational()

    def _parse_relational(self):
        left = self._parse_additive()
        while self._peek().value in ('<', '>', '<=', '>=', '==', '!='):
            op_tok = self._peek()
            self.pos += 1
            right = self._parse_additive()
            left = BinaryExprNode(left, op_tok.value, right, op_tok.line, op_tok.column)
        return left

    def _parse_additive(self):
        left = self._parse_multiplicative()
        while self._peek().value in ('+', '-'):
            op_tok = self._peek()
            self.pos += 1
            right = self._parse_multiplicative()
            left = BinaryExprNode(left, op_tok.value, right, op_tok.line, op_tok.column)
        return left

    def _parse_multiplicative(self):
        left = self._parse_primary()
        while self._peek().value in ('*', '/', '%'):
            op_tok = self._peek()
            self.pos += 1
            right = self._parse_primary()
            left = BinaryExprNode(left, op_tok.value, right, op_tok.line, op_tok.column)
        return left

    def _parse_primary(self):
        curr = self._peek()
        if curr.type == TokenType.INT_LITERAL:
            self.pos += 1
            return LiteralNode(int(curr.value), 'int', curr.line, curr.column)
        elif curr.type == TokenType.FLOAT_LITERAL:
            self.pos += 1
            return LiteralNode(float(curr.value), 'float', curr.line, curr.column)
        elif curr.type == TokenType.STRING_LITERAL:
            self.pos += 1
            return LiteralNode(curr.value, 'string', curr.line, curr.column)
        elif curr.type == TokenType.IDENTIFIER:
            self.pos += 1
            if self._match('('):
                args = []
                if self._peek().value != ')':
                    while True:
                        args.append(self._parse_expression())
                        if not self._match(','):
                            break
                self._consume(')', "Expected ')' after function arguments")
                return CallExprNode(curr.value, args, curr.line, curr.column)
            return IdentifierNode(curr.value, curr.line, curr.column)
        elif self._match('('):
            expr = self._parse_expression()
            self._consume(')', "Expected ')'")
            return expr
        
        self.errors.append(f"Parser Error at {curr.line}:{curr.column}: Unexpected expression token '{curr.value}'")
        self.pos += 1
        return None