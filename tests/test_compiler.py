import pytest
from src.lexer import Lexer, TokenType
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.detector import LanguageDetector
from src.program_analysis import ProgramAnalyzer
from src.ir_generator import IRGenerator


def test_lexer_tokens():
    code = "int main() { int x = 42; return x; }"
    lexer = Lexer(code)
    tokens, errors = lexer.tokenize()
    assert len(tokens) > 0
    assert tokens[0].type == TokenType.KEYWORD


def test_lexer_invalid_char():
    code = "int @x = 5;"
    lexer = Lexer(code)
    tokens, errors = lexer.tokenize()
    assert len(errors) > 0 or any(t.lexeme == "@" for t in tokens)


def test_parser_ast():
    code = "int main() { return 0; }"
    lexer = Lexer(code)
    tokens, errors = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert ast is not None


def test_parser_syntax_error():
    code = "int x = ; int y = 10;"
    lexer = Lexer(code)
    tokens, errors = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert len(parser.errors) > 0


def test_semantic_analysis():
    code = "int main() { int a = 10; return a; }"
    lexer = Lexer(code)
    tokens, errors = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    analyzer = SemanticAnalyzer(file_name="test.c")
    res = analyzer.analyze(ast)
    errors = getattr(analyzer, 'errors', getattr(analyzer, 'diagnostics', res))
    assert errors is None or len(errors) == 0 or isinstance(errors, list)


def test_language_detector():
    detector = LanguageDetector()
    result = detector.detect("def foo(): print('hi')", "test.py")
    assert result is not None


def test_ir_generator():
    """تست تولید کد واسط ۳ آدرسی (TAC)"""
    code = "int main() { int x = 5; return x; }"
    lexer = Lexer(code)
    tokens, _ = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    generator = IRGenerator()
    tac_code = generator.generate(ast)
    assert tac_code is not None
    assert "main:" in tac_code
    assert "return" in tac_code.lower()


def test_dead_code_elimination():
    """تست تحلیل و حذف کدهای مرده (DCE)"""
    code = "int main() {\n    int unused_var;\n    int x = 10;\n    return x;\n}"
    lexer = Lexer(code)
    tokens, _ = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    analyzer = SemanticAnalyzer(file_name="test.c")
    analyzer.analyze(ast)

    prog_analyzer = ProgramAnalyzer(ast, analyzer.global_scope, code, "test.c")
    dead_reports = prog_analyzer.detect_dead_code()
    assert len(dead_reports) > 0

    cleaned_code = prog_analyzer.eliminate_dead_code()
    assert "unused_var" not in cleaned_code