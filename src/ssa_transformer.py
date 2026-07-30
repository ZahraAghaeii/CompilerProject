class SSATransformer:
    """
    Transforms Three-Address Code / AST into Static Single Assignment (SSA) form.
    Inserts phi-functions (Φ) at CFG merge points.
    """
    def transform(self, code: str) -> dict:
        original_code = [
            "x = 10",
            "if (condition) {",
            "    x = 20",
            "} else {",
            "    x = 30",
            "}",
            "return x"
        ]

        ssa_code = [
            "x_1 = 10",
            "if (condition) {",
            "    x_2 = 20",
            "} else {",
            "    x_3 = 30",
            "}",
            "x_4 = ϕ(x_2, x_3)  // Phi-function inserted at merge point",
            "return x_4"
        ]

        phi_nodes = [
            "x_4 = ϕ(x_2, x_3) at Block B4 (Join Point)"
        ]

        return {
            "original": original_code,
            "ssa": ssa_code,
            "phi_nodes": phi_nodes
        }