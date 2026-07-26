import json
from src.lexer import Lexer
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.program_analysis import CFGBuilder, ProgramAnalyzer

def start_repl(file_path="tests/semantic_test.c"):
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    lexer = Lexer(code)
    tokens, _ = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer(file_name=file_path)
    analyzer.analyze(ast)

    prog_analyzer = ProgramAnalyzer(ast, analyzer.global_scope, code, file_path)

    print("\n========================================================")
    print(" 🚀 COMPILER INTERACTIVE REPL CLI (PHASE 3) ")
    print(" Commands: goto-def <sym> | find-refs <sym> | hover <sym>")
    print("           rename <old> <new> <line> | callgraph | dead-code | exit")
    print("========================================================\n")

    while True:
        try:
            cmd = input("ide-cli> ").strip().split()
            if not cmd:
                continue
            action = cmd[0].lower()

            if action == "exit":
                break
            elif action == "goto-def" and len(cmd) >= 2:
                res = prog_analyzer.goto_definition_json(cmd[1])
                print(json.dumps(res, indent=2))
            elif action == "hover" and len(cmd) >= 2:
                print(prog_analyzer.hover_info(cmd[1]))
            elif action == "find-refs" and len(cmd) >= 2:
                res = prog_analyzer.goto_definition_json(cmd[1])
                print(json.dumps(res.get("references", []), indent=2))
            elif action == "callgraph":
                print(json.dumps({k: list(v) for k, v in prog_analyzer.build_call_graph().items()}, indent=2))
            elif action == "dead-code":
                reports = prog_analyzer.detect_dead_code()
                for r in reports:
                    print(r)
            elif action == "rename" and len(cmd) >= 4:
                old, new, line = cmd[1], cmd[2], int(cmd[3])
                ok, new_code, diff = prog_analyzer.safe_rename(old, new, line)
                if ok:
                    print("=== UNIFIED DIFF ===")
                    print(diff)
                else:
                    print(f"❌ Error: {new_code}")
            else:
                print("Unknown or incomplete command.")
        except Exception as e:
            print(f"Error executing command: {e}")

if __name__ == "__main__":
    start_repl()