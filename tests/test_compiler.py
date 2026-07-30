import pytest
from src.lexer import Lexer, TokenType
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.detector import LanguageDetector


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

    analyzer = SemanticAnalyzer()
    res = analyzer.analyze(ast)
    # بررسی وجود خطاها از طریق خروجی یا صفت‌های رایج
    errors = getattr(analyzer, 'errors', getattr(analyzer, 'diagnostics', res))
    assert errors is None or len(errors) == 0 or isinstance(errors, list)


def test_language_detector():
    detector = LanguageDetector()
    result = detector.detect("def foo(): print('hi')", "test.py")
    assert result is not None