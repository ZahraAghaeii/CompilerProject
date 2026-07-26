from src.lexer import Lexer
from src.parser import Parser
from src.highlighter import SyntaxHighlighter
from src.semantic import SemanticAnalyzer
from src.completion import IntellisenseEngine

def print_ast(node, indent=""):
    if not node:
        return
    print(f"{indent}{node.__class__.__name__} [Line:{node.line}, Col:{node.column}]", end="")
    if hasattr(node, 'name'):
        print(f" -> {node.name}", end="")
    if hasattr(node, 'value'):
        print(f" -> {node.value}", end="")
    if hasattr(node, 'inferred_type') and node.inferred_type:
        print(f" <Type: {node.inferred_type}>", end="")
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
    test_file = "tests/semantic_test.c"
    with open(test_file, "r", encoding="utf-8") as f:
        code = f.read()

    print("=== 1. LEXICAL ANALYSIS ===")
    lexer = Lexer(code)
    tokens, lex_errors = lexer.tokenize()
    print(f"Total Tokens: {len(tokens)}")

    print("\n=== 2. PARSING & AST CONSTRUCTION ===")
    parser = Parser(tokens)
    ast = parser.parse()

    print("\n=== 3. SEMANTIC ANALYSIS & TYPE CHECKING ===")
    analyzer = SemanticAnalyzer()
    errors, warnings = analyzer.analyze(ast)

    if errors:
        print("\n--- SEMANTIC ERRORS ---")
        for err in errors:
            print(f"❌ {err}")

    if warnings:
        print("\n--- SEMANTIC WARNINGS & INFO ---")
        for warn in warnings:
            print(f"⚠️ {warn}")

    if not errors and not parser.errors and not lex_errors:
        print("\n✅ Semantic Analysis passed successfully!")
        print("\nAnnotated AST:")
        print_ast(ast)

    print("\n=== 4. INTELLISENSE / AUTO-COMPLETION DEMO ===")
    engine = IntellisenseEngine(analyzer.global_scope)
    completions = engine.get_completions(analyzer.global_scope, prefix="f")
    print("Suggestions for prefix 'f':")
    for item in completions:
        print(f" 💡 {item['label']} [{item['kind']}] -> {item['detail']}")

    print("\n=== 5. SYNTAX HIGHLIGHTING ===")
    html_output = SyntaxHighlighter.highlight_html(code, tokens, ast)
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html_output)
    print("HTML output updated in 'output.html'!")

if __name__ == "__main__":
    main()