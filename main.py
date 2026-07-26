from src.lexer import Lexer
from src.parser import Parser
from src.highlighter import SyntaxHighlighter

def print_ast(node, indent=""):
    if not node:
        return
    print(f"{indent}{node.__class__.__name__} [Line:{node.line}, Col:{node.column}]", end="")
    if hasattr(node, 'name'):
        print(f" -> {node.name}", end="")
    if hasattr(node, 'value'):
        print(f" -> {node.value}", end="")
    print()
    
    for attr in dir(node):
        if not attr.startswith('_') and attr not in ('line', 'column', 'inferred_type', 'name', 'value'):
            val = getattr(node, attr)
            if isinstance(val, list):
                for item in val:
                    if hasattr(item, 'line'):
                        print_ast(item, indent + "  ")
            elif hasattr(val, 'line'):
                print_ast(val, indent + "  ")

def main():
    with open("tests/test_code.c", "r", encoding="utf-8") as f:
        code = f.read()

    print("=== 1. LEXICAL ANALYSIS ===")
    lexer = Lexer(code)
    tokens, lex_errors = lexer.tokenize()
    print(f"Total Tokens: {len(tokens)}")

    print("\n=== 2. PARSING & AST CONSTRUCTION ===")
    parser = Parser(tokens)
    ast = parser.parse()
    
    if parser.errors or lex_errors:
        print("\n--- ERRORS DETECTED ---")
        for err in lex_errors + parser.errors:
            print(err)
    else:
        print("AST successfully generated:\n")
        print_ast(ast)

    print("\n=== 3. SYNTAX HIGHLIGHTING ===")
    print("--- ANSI Terminal Output ---")
    print(SyntaxHighlighter.highlight_ansi(code, tokens))

    html_output = SyntaxHighlighter.highlight_html(code, tokens)
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html_output)
    print("\nHTML output saved to 'output.html'!")

if __name__ == "__main__":
    main()