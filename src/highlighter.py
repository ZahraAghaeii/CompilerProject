from src.lexer import TokenType, Token

class SyntaxHighlighter:
    ANSI_COLORS = {
        TokenType.KEYWORD: "\033[1;34m",       # Bold Blue
        TokenType.IDENTIFIER: "\033[0;37m",    # White
        TokenType.INT_LITERAL: "\033[0;33m",   # Orange/Yellow
        TokenType.FLOAT_LITERAL: "\033[0;33m", # Orange/Yellow
        TokenType.STRING_LITERAL: "\033[0;32m",# Warm Green
        TokenType.OPERATOR: "\033[0;37m",      # Light Gray
        TokenType.DELIMITER: "\033[0;37m",     # Light Gray
        TokenType.COMMENT: "\033[3;90m",       # Italic Gray
        TokenType.PREPROCESSOR: "\033[0;35m",  # Magenta
        TokenType.INVALID: "\033[4;31m"        # Red Underline
    }
    RESET = "\033[0m"

    CSS_STYLES = """
    <style>
        body { background-color: #1e1e1e; color: #d4d4d4; font-family: 'Consolas', monospace; padding: 20px; }
        .keyword { color: #569cd6; font-weight: bold; }
        .identifier { color: #9cdcfe; }
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
    def highlight_ansi(cls, code: str, tokens: list) -> str:
        output = ""
        last_pos = 0
        for token in tokens:
            if token.type == TokenType.EOF:
                break
            # اضافه کردن فاصله‌ها و اینترهای بین توکن‌ها
            pos_in_code = code.find(token.value, last_pos)
            if pos_in_code != -1:
                output += code[last_pos:pos_in_code]
                last_pos = pos_in_code + len(token.value)
            
            color = cls.ANSI_COLORS.get(token.type, "")
            output += f"{color}{token.value}{cls.RESET}"
        
        output += code[last_pos:]
        return output

    @classmethod
    def highlight_html(cls, code: str, tokens: list) -> str:
        html_code = f"<html><head>{cls.CSS_STYLES}</head><body><pre>"
        last_pos = 0
        
        class_map = {
            TokenType.KEYWORD: "keyword",
            TokenType.IDENTIFIER: "identifier",
            TokenType.INT_LITERAL: "number",
            TokenType.FLOAT_LITERAL: "number",
            TokenType.STRING_LITERAL: "string",
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
            val_escaped = token.value.replace("<", "&lt;").replace(">", "&gt;")
            html_code += f'<span class="{css_class}">{val_escaped}</span>'
            
        html_code += code[last_pos:].replace("<", "&lt;").replace(">", "&gt;")
        html_code += "</pre></body></html>"
        return html_code