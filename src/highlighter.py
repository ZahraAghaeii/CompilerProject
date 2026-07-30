from src.lexer import TokenType, Token
from src.ast_nodes import FunctionDeclNode, CallExprNode


class SyntaxHighlighter:
    TYPE_NAMES = {'int', 'float', 'double', 'char', 'void', 'struct', 'bool'}

    ANSI_COLORS = {
        TokenType.KEYWORD: "\033[1;34m",  # Bold Blue (Keywords)
        'TYPE_NAME': "\033[0;36m",  # Teal/Cyan (Data types)
        TokenType.IDENTIFIER: "\033[0;37m",  # White (Variables)
        'FUNCTION_NAME': "\033[1;33m",  # Yellow/Gold (Functions)
        TokenType.INT_LITERAL: "\033[0;33m",  # Orange (Integers)
        TokenType.FLOAT_LITERAL: "\033[0;33m",  # Orange (Floats)
        TokenType.BOOL_LITERAL: "\033[0;33m",  # Orange (Booleans)
        TokenType.STRING_LITERAL: "\033[0;32m",  # Warm Green (Strings)
        TokenType.CHAR_LITERAL: "\033[0;32m",  # Warm Green (Characters)
        TokenType.OPERATOR: "\033[0;37m",  # Light Gray (Operators)
        TokenType.DELIMITER: "\033[0;37m",  # Light Gray (Delimiters)
        TokenType.COMMENT: "\033[3;90m",  # Italic Gray (Comments)
        TokenType.PREPROCESSOR: "\033[0;35m",  # Magenta (Preprocessors)
        TokenType.INVALID: "\033[4;31m"  # Red Underline (Errors)
    }
    RESET = "\033[0m"

    CSS_STYLES = """
    <style>
        body { background-color: #1e1e1e; color: #d4d4d4; font-family: 'Consolas', monospace; padding: 20px; }
        .keyword { color: #569cd6; font-weight: bold; }
        .type-name { color: #4ec9b0; } /* Teal/Cyan */
        .identifier { color: #9cdcfe; }
        .func-name { color: #dcdcaa; font-weight: bold; }
        .number { color: #b5cea8; }
        .string { color: #ce9178; }
        .comment { color: #6a9955; font-style: italic; }
        .preprocessor { color: #c586c0; }
        .operator { color: #d4d4d4; }
        .delimiter { color: #ffd700; }
        .invalid { color: #f44747; text-decoration: underline; }
    </style>
    """

    @classmethod
    def _extract_func_positions(cls, ast_node):
        func_positions = set()
        if not ast_node:
            return func_positions

        if isinstance(ast_node, (FunctionDeclNode, CallExprNode)):
            name = getattr(ast_node, 'name', None) or getattr(ast_node, 'callee', None)
            if name:
                func_positions.add((ast_node.line, name))

        for attr in dir(ast_node):
            if not attr.startswith('_'):
                val = getattr(ast_node, attr)
                if isinstance(val, list):
                    for item in val:
                        if hasattr(item, 'line'):
                            func_positions.update(cls._extract_func_positions(item))
                elif hasattr(val, 'line'):
                    func_positions.update(cls._extract_func_positions(val))
        return func_positions

    @classmethod
    def highlight_ansi(cls, code: str, tokens: list, ast=None) -> str:
        func_pos = cls._extract_func_positions(ast) if ast else set()
        output = ""
        last_pos = 0

        for token in tokens:
            if token.type == TokenType.EOF:
                break
            pos_in_code = code.find(token.value, last_pos)
            if pos_in_code != -1:
                output += code[last_pos:pos_in_code]
                last_pos = pos_in_code + len(token.value)

            color_key = token.type

            if token.type == TokenType.KEYWORD and token.value in cls.TYPE_NAMES:
                color_key = 'TYPE_NAME'
            elif token.type == TokenType.IDENTIFIER and (token.line, token.value) in func_pos:
                color_key = 'FUNCTION_NAME'

            color = cls.ANSI_COLORS.get(color_key, "")
            output += f"{color}{token.value}{cls.RESET}"

        output += code[last_pos:]
        return output

    @classmethod
    def highlight_html(cls, code: str, tokens: list, ast=None) -> str:
        func_pos = cls._extract_func_positions(ast) if ast else set()
        html_code = f"<html><head>{cls.CSS_STYLES}</head><body><pre>"
        last_pos = 0

        class_map = {
            TokenType.KEYWORD: "keyword",
            TokenType.IDENTIFIER: "identifier",
            TokenType.INT_LITERAL: "number",
            TokenType.FLOAT_LITERAL: "number",
            TokenType.BOOL_LITERAL: "number",
            TokenType.STRING_LITERAL: "string",
            TokenType.CHAR_LITERAL: "string",
            TokenType.COMMENT: "comment",
            TokenType.PREPROCESSOR: "preprocessor",
            TokenType.OPERATOR: "operator",
            TokenType.DELIMITER: "delimiter",
            TokenType.INVALID: "invalid"
        }

        for token in tokens:
            if token.type == TokenType.EOF:
                break
            pos_in_code = code.find(token.value, last_pos)
            if pos_in_code != -1:
                html_code += code[last_pos:pos_in_code].replace("<", "&lt;").replace(">", "&gt;")
                last_pos = pos_in_code + len(token.value)

            css_class = class_map.get(token.type, "")

            # CSS
            if token.type == TokenType.KEYWORD and token.value in cls.TYPE_NAMES:
                css_class = "type-name"
            elif token.type == TokenType.IDENTIFIER and (token.line, token.value) in func_pos:
                css_class = "func-name"

            val_escaped = token.value.replace("<", "&lt;").replace(">", "&gt;")
            html_code += f'<span class="{css_class}">{val_escaped}</span>'

        html_code += code[last_pos:].replace("<", "&lt;").replace(">", "&gt;")
        html_code += "</pre></body></html>"
        return html_code