from src.lexer import Lexer
from src.parser import Parser
from src.highlighter import SyntaxHighlighter
from src.semantic import SemanticAnalyzer
from src.completion import IntellisenseEngine
from src.program_analysis import CFGBuilder, CallGraphBuilder, RefactoringEngine

def print_cfg(block, visited=None):
    if visited is None:
        visited = set()
    if block.block_id in visited:
        return
    visited.add(block.block_id)
    
    succs = ", ".join([f"Block_{b.block_id}" for b in block.successors])
    print(f"  [Block_{block.block_id} - {block.label}] -> Successors: [{succs}]")
    for succ in block.successors:
        print_cfg(succ, visited)

def main():
    test_file = "tests/semantic_test.c"
    with open(test_file, "r", encoding="utf-8") as f:
        code = f.read()

    print("==========================================")
    print("      COMPILER FRONT-END & IDE ENGINE     ")
    print("==========================================")

    # Phase 1 & 2 Execution
    lexer = Lexer(code)
    tokens, _ = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer(file_name="semantic_test.c")
    analyzer.analyze(ast)

    # Phase 3 Execution
    print("\n=== PHASE 3: PROGRAM ANALYSIS & IDE FEATURES ===")
    
    # 1. Call Graph
    call_graph = CallGraphBuilder.build_call_graph(ast)
    print("\n📊 1. Call Graph:")
    for caller, callees in call_graph.items():
        print(f"  Function '{caller}' calls -> {list(callees) if callees else 'None'}")

    # 2. Control Flow Graph (CFG)
    cfg_builder = CFGBuilder()
    print("\n🔀 2. Control Flow Graph (CFG) for 'factorial':")
    for decl in ast.declarations:
        if hasattr(decl, 'name') and decl.name == 'factorial':
            entry_block = cfg_builder.build_cfg(decl)
            print_cfg(entry_block)

    # 3. Refactoring & Navigation
    ref_engine = RefactoringEngine(ast, code)
    print("\n📍 3. Go-to-Definition ('factorial'):")
    def_info = ref_engine.goto_definition("factorial")
    print(f"  Defined at: {def_info}")

    print("\n🔍 4. Find All References ('n'):")
    refs = ref_engine.find_all_references("n")
    for r in refs:
        print(f"  Ref at Line:{r['line']}, Col:{r['col']}")

    print("\n✏️ 5. Safe Rename Demo (Renaming 'factorial' to 'calc_fact'):")
    success, renamed_code = ref_engine.safe_rename("factorial", "calc_fact")
    if success:
        print("  --- Code After Rename ---")
        print(renamed_code)

    # Save Final HTML
    html_output = SyntaxHighlighter.highlight_html(code, tokens, ast)
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html_output)

if __name__ == "__main__":
    main()