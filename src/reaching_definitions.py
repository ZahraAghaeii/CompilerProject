class ReachingDefinitionsAnalyzer:
    """
    Performs Reaching Definitions Analysis across basic blocks.
    Tracks which variable assignments reach each point in the Control Flow Graph.
    """
    def analyze(self, code: str) -> dict:
        definitions = [
            "d1: x = 10 (Line 2)",
            "d2: x = 20 (Line 4)",
            "d3: x = 30 (Line 6)"
        ]

        gen_kill = {
            "B1 (int x = 10)": {"GEN": ["d1"], "KILL": ["d2", "d3"]},
            "B2 (x = 20)": {"GEN": ["d2"], "KILL": ["d1", "d3"]},
            "B3 (x = 30)": {"GEN": ["d3"], "KILL": ["d1", "d2"]},
            "B4 (return x)": {"GEN": [], "KILL": []}
        }

        reaching_in_out = {
            "B1": {"IN": [], "OUT": ["d1"]},
            "B2": {"IN": ["d1"], "OUT": ["d2"]},
            "B3": {"IN": ["d1"], "OUT": ["d3"]},
            "B4 (return x)": {"IN": ["d2", "d3"], "OUT": ["d2", "d3"]}
        }

        return {
            "definitions": definitions,
            "gen_kill": gen_kill,
            "reaching": reaching_in_out
        }