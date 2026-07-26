from src.lexer import Lexer
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.program_analysis import ProgramAnalyzer
import json

def main():
    test_file = "tests/semantic_test.c"
    with open(test_file, "r", encoding="utf-8") as f:
        code = f.read()

    print("=== FULL COMPILER PIPELINE & PROGRAM ANALYSIS ===")
    
    lexer = Lexer(code)
    tokens, _ = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer(file_name="semantic_test.c")
    analyzer.analyze(ast)

    prog_analyzer = ProgramAnalyzer(ast, analyzer.global_scope, code)

    print("\n--- 1. Call Graph & Recursion ---")
    print("Call Graph:", prog_analyzer.build_call_graph())
    print("Recursive Functions:", prog_analyzer.detect_recursive_functions())

    print("\n--- 2. Go-to-Definition (JSON Format - Section 6.3) ---")
    print(json.dumps(prog_analyzer.goto_definition_json("factorial"), indent=2))

    print("\n--- 3. Hover Information ---")
    print(prog_analyzer.hover_info("factorial"))

    print("\n--- 4. Safe Rename Refactoring (With Unified Diff - Section 6.4) ---")
    ok, new_code, diff = prog_analyzer.safe_rename("factorial", "calc_fact", target_line=1)
    if ok:
        print("Diff generated successfully:")
        print(diff)

    print("\n--- 5. Dead Code Detection (Section 6.5) ---")
    for report in prog_analyzer.detect_dead_code():
        print(report)

if __name__ == "__main__":
    main()