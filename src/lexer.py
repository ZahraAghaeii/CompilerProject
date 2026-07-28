from enum import Enum, auto


class TokenType(Enum):
    # Keywords
    KEYWORD = auto()

    # Literals
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()
    CHAR_LITERAL = auto()
    BOOL_LITERAL = auto()

    # Identifiers
    IDENTIFIER = auto()

    # Operators & Delimiters
    OPERATOR = auto()
    DELIMITER = auto()

    # Preprocessor
    PREPROCESSOR = auto()

    # Special / Error
    COMMENT = auto()
    INVALID = auto()
    EOF = auto()


class Token:
    def __init__(self, type_: TokenType, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', Line:{self.line}, Col:{self.column})"


class Lexer:
    KEYWORDS = {
        'if', 'else', 'while', 'for', 'return', 'int', 'float',
        'double', 'char', 'void', 'struct', 'break', 'continue', 'bool'
    }

    OPERATORS = [
        '==', '!=', '<=', '>=', '&&', '||', '->', '++', '--',
        '+=', '-=', '*=', '/=', '+', '-', '*', '/', '%', '=', '<', '>', '!'
    ]

    DELIMITERS = ['{', '}', '(', ')', '[', ']', ';', ',', '.']

    def __init__(self, source_code: str):
        self.code = source_code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.length = len(source_code)
        self.tokens = []
        self.errors = []

    def _peek(self, offset=0):
        target = self.pos + offset
        return self.code[target] if target < self.length else ''

    def _advance(self):
        ch = self._peek()
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def tokenize(self):
        while self.pos < self.length:
            start_line = self.line
            start_col = self.column
            ch = self._peek()

            # Whitespaces
            if ch.isspace():
                self._advance()
                continue

            # Preprocessor directives (#include, #define)
            if ch == '#':
                val = ""
                while self._peek() and self._peek() != '\n':
                    val += self._advance()
                self.tokens.append(Token(TokenType.PREPROCESSOR, val, start_line, start_col))
                continue

            # Comments
            if ch == '/' and self._peek(1) == '/':
                val = ""
                while self._peek() and self._peek() != '\n':
                    val += self._advance()
                self.tokens.append(Token(TokenType.COMMENT, val, start_line, start_col))
                continue

            if ch == '/' and self._peek(1) == '*':
                val = self._advance() + self._advance()
                terminated = False
                while self.pos < self.length:
                    if self._peek() == '*' and self._peek(1) == '/':
                        val += self._advance() + self._advance()
                        terminated = True
                        break
                    val += self._advance()
                if not terminated:
                    self.errors.append(f"Lexer Error at {start_line}:{start_col}: Unterminated block comment")
                    self.tokens.append(Token(TokenType.INVALID, val, start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.COMMENT, val, start_line, start_col))
                continue

            # Strings
            if ch == '"':
                val = self._advance()
                terminated = False
                while self.pos < self.length:
                    c = self._advance()
                    val += c
                    if c == '"' and val[-2] != '\\':
                        terminated = True
                        break
                    if c == '\n':
                        break
                if not terminated:
                    self.errors.append(f"Lexer Error at {start_line}:{start_col}: Unterminated string literal")
                    self.tokens.append(Token(TokenType.INVALID, val, start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.STRING_LITERAL, val, start_line, start_col))
                continue

            # Character Literals
            if ch == "'":
                val = self._advance()
                terminated = False

                if self._peek() == '\\':
                    val += self._advance()
                    if self._peek():
                        val += self._advance()
                else:
                    if self._peek() and self._peek() not in ("'", '\n'):
                        val += self._advance()

                if self._peek() == "'":
                    val += self._advance()
                    terminated = True

                if not terminated:
                    self.errors.append(
                        f"Lexer Error at {start_line}:{start_col}: Unterminated or invalid character literal")
                    self.tokens.append(Token(TokenType.INVALID, val, start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.CHAR_LITERAL, val, start_line, start_col))
                continue

            # Numbers
            if ch.isdigit():
                val = ""
                is_float = False
                while self._peek().isdigit() or (self._peek() == '.' and not is_float):
                    if self._peek() == '.':
                        is_float = True
                    val += self._advance()
                t_type = TokenType.FLOAT_LITERAL if is_float else TokenType.INT_LITERAL
                self.tokens.append(Token(t_type, val, start_line, start_col))
                continue

            # Identifiers and Keywords
            if ch.isalpha() or ch == '_':
                val = ""
                while self._peek().isalnum() or self._peek() == '_':
                    val += self._advance()

                if val in ('true', 'false'):
                    t_type = TokenType.BOOL_LITERAL
                elif val in self.KEYWORDS:
                    t_type = TokenType.KEYWORD
                else:
                    t_type = TokenType.IDENTIFIER

                self.tokens.append(Token(t_type, val, start_line, start_col))
                continue

            # Operators (Maximal Munch)
            matched_op = None
            for op in self.OPERATORS:
                if self.code.startswith(op, self.pos):
                    matched_op = op
                    break
            if matched_op:
                for _ in range(len(matched_op)):
                    self._advance()
                self.tokens.append(Token(TokenType.OPERATOR, matched_op, start_line, start_col))
                continue

            # Delimiters
            if ch in self.DELIMITERS:
                val = self._advance()
                self.tokens.append(Token(TokenType.DELIMITER, val, start_line, start_col))
                continue

            # Invalid Character
            val = self._advance()
            self.errors.append(f"Lexer Error at {start_line}:{start_col}: Unrecognized character '{val}'")
            self.tokens.append(Token(TokenType.INVALID, val, start_line, start_col))

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens, self.errors