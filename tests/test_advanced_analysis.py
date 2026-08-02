import pytest
from src.dominator_tree import DominatorTreeBuilder
from src.ssa_transformer import SSATransformer

def test_dominator_tree_structure():
    code_mock = "int main() { int x = 0; if(x) { x=1; } else { x=2; } return x; }"
    builder = DominatorTreeBuilder()
    result = builder.analyze(code_mock)
    
    dominators = result["dominators"]
    idom = result["idom"]
    
    assert "ENTRY" in dominators["ENTRY"]
    assert "ENTRY" in dominators["B1 (evaluate condition)"]
    assert idom["B2 (true branch)"] == "B1 (evaluate condition)"

def test_ssa_phi_function_insertion():
    code_mock = "int x = 10; if(cond) x = 20; else x = 30; return x;"
    transformer = SSATransformer()
    result = transformer.transform(code_mock)
    
    phi_nodes = result["phi_nodes"]
    assert len(phi_nodes) > 0
    
    # بررسی وجود قالب (x_2, x_3) در توابع تولید شده
    has_phi_merge = any("(x_2, x_3)" in phi for phi in phi_nodes)
    assert has_phi_merge is True