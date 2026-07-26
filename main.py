from src.lexer import Lexer

def main():
    with open("tests/test_code.c", "r", encoding="utf-8") as f:
        code = f.read()

    print("=== STEP 1: LEXICAL ANALYSIS ===")
    lexer = Lexer(code)
    tokens, errors = lexer.tokenize()

    for token in tokens:
        print(token)

    if errors:
        print("\n=== LEXER ERRORS ===")
        for err in errors:
            print(err)

if __name__ == "__main__":
    main()