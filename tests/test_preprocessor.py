import pytest
from src.preprocessor import Preprocessor

def test_macro_expansion_simple():
    code = "#define PI 3.14\nfloat radius = 10.0;\nfloat area = PI * radius * radius;"
    preprocessor = Preprocessor()
    result = preprocessor.process(code)
    
    assert "PI" in result["macros_found"]
    assert result["macros_found"]["PI"] == "3.14"
    assert "float area = 3.14 * radius * radius;" in result["expanded_code"]

def test_macro_expansion_no_collision():
    code = "#define MAX 100\nint MAX_VALUE = MAX;"
    preprocessor = Preprocessor()
    result = preprocessor.process(code)
    
    assert "int MAX_VALUE = 100;" in result["expanded_code"]
    assert "int 100_VALUE" not in result["expanded_code"]