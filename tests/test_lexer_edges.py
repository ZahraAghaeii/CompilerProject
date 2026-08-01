import pytest
from src.lexer import Lexer, TokenType

def test_lexer_unterminated_string():
    code = 'char* str = "hello world;'
    lexer = Lexer(code)
    tokens, errors = lexer.tokenize()
    
    assert len(errors) > 0
    assert any("Unterminated string literal" in err for err in errors)
    assert any(t.type == TokenType.INVALID for t in tokens)

def test_lexer_unterminated_block_comment():
    code = 'int a = 5; /* This comment never ends ... \n int b = 10;'
    lexer = Lexer(code)
    tokens, errors = lexer.tokenize()
    
    assert len(errors) > 0
    assert any("Unterminated block comment" in err for err in errors)

def test_lexer_invalid_character_recovery():
    code = 'int x = 10 $ 5;'
    lexer = Lexer(code)
    tokens, errors = lexer.tokenize()
    
    assert len(errors) > 0
    assert any("Unrecognized character '$'" in err for err in errors)
    assert tokens[-2].value == ';'