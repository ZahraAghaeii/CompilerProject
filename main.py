from src.lexer import Lexer
from src.parser import Parser
from src.highlighter import SyntaxHighlighter
from src.semantic import SemanticAnalyzer
from src.completion import IntellisenseEngine

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

    print("\n=== 3. SEMANTIC ANALYSIS & DIAGNOSTICS (SECTION 5.5) ===")
    analyzer = SemanticAnalyzer(file_name="semantic_test.c")
    diagnostics = analyzer.analyze(ast)

    for diag in diagnostics:
        print(diag)

    print("\n=== 4. INTELLISENSE AUTO-COMPLETION AT CURSOR (SECTION 5.4) ===")
    engine = IntellisenseEngine(analyzer.global_scope)
    # دریافت پیشنهادات برای مکان‌نما در خط ۱۲ و ستون ۵ با پیشوند 'f'
    completions = engine.get_completions_at(line=12, column=5, prefix="f")
    print("Suggestions at Cursor (Line 12, Col 5):")
    for item in completions:
        print(f" 💡 {item['label']} [{item['kind']}] -> {item['detail']} (SortScore: {item['sortOrder']})")

    print("\n=== 5. SYNTAX HIGHLIGHTING ===")
    html_output = SyntaxHighlighter.highlight_html(code, tokens, ast)
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html_output)
    print("HTML output saved to 'output.html'!")

if __name__ == "__main__":
    main()