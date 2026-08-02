import pytest
from src.incremental_parser import IncrementalParser

def test_incremental_parse_full_initialization():
    parser = IncrementalParser()
    code = "int x = 10;\nint y = 20;\nint z = x + y;"
    
    result = parser.parse_full(code)
    assert result["mode"] == "Full Parse"
    assert result["total_lines_parsed"] == 3
    assert result["ast_cache_size"] == 3

def test_incremental_parse_partial_update():
    parser = IncrementalParser()
    old_code = "int x = 10;\nint y = 20;\nint z = x + y;"
    parser.parse_full(old_code)
    
    new_code = "int x = 10;\nint y = 99;\nint z = x + y;"
    result = parser.parse_incremental(old_code, new_code)
    
    assert result["mode"] == "Incremental Re-Parse"
    assert result["modified_regions"] == 1
    assert 2 in result["reparsed_lines"]