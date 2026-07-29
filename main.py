import json
from src.lexer import Lexer
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.program_analysis import ProgramAnalyzer


def run_test_pipeline(test_name, code, action="general", rename_args=None):
    print(f"\n{'=' * 60}")
    print(f"🚀 RUNNING TEST: {test_name}")
    print(f"{'=' * 60}")

    try:
        lexer = Lexer(code)
        tokens, _ = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        analyzer = SemanticAnalyzer(file_name="test_case.c")
        analyzer.analyze(ast)

        prog_analyzer = ProgramAnalyzer(ast, analyzer.global_scope, code, "test_case.c")

        if action == "data-flow":
            reports = prog_analyzer.analyze_definite_assignment()
            for r in reports: print(r)

        elif action == "dead-code":
            reports = prog_analyzer.detect_dead_code()
            for r in reports: print(r)

        elif action == "rename" and rename_args:
            print(f"Target: Rename '{rename_args['old']}' to '{rename_args['new']}' at line {rename_args['line']}")
            ok, new_code, diff = prog_analyzer.safe_rename(
                rename_args['old'], rename_args['new'], rename_args['line']
            )
            if ok:
                print("=== UNIFIED DIFF ===")
                print(diff)
            else:
                print(f"Error: {new_code}")

        elif action == "general":
            print("--- Call Graph & Recursion ---")
            print("Call Graph:", prog_analyzer.build_call_graph())
            print("Recursive Functions:", prog_analyzer.detect_recursive_functions())

            print("\n--- Dead Code Detection ---")
            for r in prog_analyzer.detect_dead_code(): print(r)

            print("\n--- Data-Flow Analysis ---")
            for r in prog_analyzer.analyze_definite_assignment(): print(r)

    except Exception as e:
        print(f"❌ Test Crashed: {e}")


TEST_1_DATA_FLOW = """int test_data_flow(int flag) {
    int a;
    int b = 10;
    if (flag > 0) {
        a = 100;
    } else {
        b = 200;
    }
    int c = a + b; 
    return c;
}"""

TEST_2_UNREACHABLE = """int test_unreachable() {
    int x = 0;
    while (x < 10) {
        if (x == 5) {
            break;
            x = 100;
        }
        x = x + 1;
        continue;
        x = 200;
    }
    return x;
    int y = 50;
}"""

TEST_3_SHADOWING = """int val = 100;

int test_shadowing(int val) {
    int x = val;
    {
        int val = 20;
        x = val;
    }
    return val;
}"""

TEST_4_DEAD_ISOLATED = """int dead_recursive(int n) {
    if (n <= 0) return 0;
    return dead_recursive(n - 1);
}

int unused_helper() {
    int temp = 10;
    return temp;
}

int main() {
    int active = 1;
    return active;
}"""


def main():
    print("🌟 === ADVANCED COMPILER PIPELINE & PROGRAM ANALYSIS === 🌟")

    try:
        with open("tests/semantic_test.c", "r", encoding="utf-8") as f:
            general_code = f.read()
        run_test_pipeline("0. General Pipeline (semantic_test.c)", general_code, "general")
    except FileNotFoundError:
        print("\n⚠️ General test file 'tests/semantic_test.c' not found, skipping...")

    run_test_pipeline("1. Data-Flow (Uninitialized Variables)", TEST_1_DATA_FLOW, "data-flow")
    run_test_pipeline("2. Unreachable Code (Post-Jump)", TEST_2_UNREACHABLE, "dead-code")
    run_test_pipeline("3. Safe Rename (Scope Shadowing)", TEST_3_SHADOWING, "rename",
                      {"old": "val", "new": "inner_val", "line": 6})
    run_test_pipeline("4. Dead Code (Isolated Functions & Vars)", TEST_4_DEAD_ISOLATED, "dead-code")
    try:
        from src.highlighter import SyntaxHighlighter

        html_test_file = "tests/test_code.c"
        with open(html_test_file, "r", encoding="utf-8") as hf:
            html_code = hf.read()

        lexer_h = Lexer(html_code)
        tokens_h, _ = lexer_h.tokenize()
        parser_h = Parser(tokens_h)
        ast_h = parser_h.parse()

        html_output = SyntaxHighlighter.highlight_html(html_code, tokens_h, ast_h)
        with open("output.html", "w", encoding="utf-8") as f:
            f.write(html_output)

        print("\n--- 7. Syntax Highlighter ---")
        print("Successfully updated 'output.html' from 'tests/test_code.c'!")
    except Exception as e:
        print(f"\nCould not generate HTML output: {e}")

if __name__ == "__main__":
    main()