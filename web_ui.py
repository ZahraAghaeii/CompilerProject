from flask import Flask, request, jsonify, render_template_string
import json
from src.lexer import Lexer
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.program_analysis import ProgramAnalyzer
from src.detector import LanguageDetector
from src.ir_generator import IRGenerator
from src.preprocessor import Preprocessor
from src.python_plugin import PythonPlugin
from src.dominator_tree import DominatorTreeBuilder
from src.reaching_definitions import ReachingDefinitionsAnalyzer
from src.ssa_transformer import SSATransformer
from src.incremental_parser import IncrementalParser

app = Flask(__name__)

# Single global instance to maintain AST caching state across keystrokes/requests
incremental_parser_instance = IncrementalParser()
previous_code_cache = ""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Compiler IDE - Ultimate Edition</title>
    <!-- Mermaid.js for visual rendering of AST and Call Graph -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({ startOnLoad: false, theme: 'dark' });</script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #d4d4d4; padding: 20px; margin: 0; }
        h2 { color: #569cd6; border-bottom: 1px solid #333; padding-bottom: 10px; }
        .container { display: flex; gap: 20px; }
        .editor-section, .output-section { flex: 1; display: flex; flex-direction: column; gap: 15px; }
        textarea { width: 100%; height: 350px; background-color: #2d2d2d; color: #dcdcaa; font-family: 'Consolas', monospace; font-size: 14px; padding: 15px; border: 1px solid #444; border-radius: 5px; box-sizing: border-box; resize: vertical; }
        .panel { background-color: #252526; padding: 15px; border: 1px solid #333; border-radius: 5px; }
        button { background-color: #0e639c; color: white; border: none; padding: 8px 12px; cursor: pointer; margin-right: 5px; margin-bottom: 5px; border-radius: 4px; font-weight: bold; transition: 0.2s; }
        button:hover { background-color: #1177bb; }
        input { padding: 8px; background-color: #3c3c3c; color: white; border: 1px solid #555; margin-right: 5px; border-radius: 4px; }
        pre { white-space: pre-wrap; word-wrap: break-word; color: #9cdcfe; font-family: 'Consolas', monospace; margin: 0; }
        .controls-grid { display: grid; grid-template-columns: auto 1fr; gap: 10px; align-items: center; }
        #visual-canvas { background-color: #1e1e1e; padding: 10px; border-radius: 5px; overflow: auto; max-height: 400px; display: none; }
    </style>
</head>
<body>
    <h2>🚀 Compiler Advanced IDE (Ultimate Bonus Package)</h2>

    <div class="container">
        <!-- Source Code Editor Section -->
        <div class="editor-section">
            <div class="panel">
                <h3 style="margin-top: 0; color: #ce9178;">Source Code</h3>
                <textarea id="code">int main() {
    int x = 10;
    if (x > 5) {
        x = 20;
    } else {
        x = 30;
    }
    return x;
}</textarea>
            </div>

            <div class="panel">
                <h3 style="margin-top: 0; color: #4ec9b0;">Program Analysis & Optimization (Bonus Features)</h3>
                <button onclick="runPreprocess()" style="background-color: #b5ce28; color: #1e1e1e;">⚙️ Expand Macros</button>
                <button onclick="runPythonPlugin()" style="background-color: #3572A5;">🐍 Parse Python (Plugin)</button>
                <button onclick="runDominatorTree()" style="background-color: #8A2BE2;">🌳 Dominator Tree</button>
                <button onclick="runReachingDefinitions()" style="background-color: #008080;">📍 Reaching Definitions</button>
                <button onclick="runSSAForm()" style="background-color: #D35400;">🔄 SSA Form (ϕ)</button>
                <button onclick="runIncrementalParse()" style="background-color: #F39C12; color: #1e1e1e;">⚡ Incremental Parse</button>
                <button onclick="runAnalysis('dead-code')">💀 Detect Dead Code</button>
                <button onclick="runAnalysis('eliminate-dead-code')" style="background-color: #d16969;">✂️ Eliminate Dead Code (DCE)</button>
                <button onclick="runAnalysis('generate-ir')" style="background-color: #ce9178;">⚡ Generate TAC (IR Code)</button>
                <button onclick="runAnalysis('data-flow')">🌊 Data Flow</button>
                <button onclick="runAnalysis('callgraph')">📞 Call Graph (JSON)</button>
                <button onclick="runVisualCallGraph()">📊 Visual Call Graph</button>
                <button onclick="runVisualAST()" style="background-color: #6a9955;">🌳 Visual AST Diagram</button>
                <button onclick="runDetectLanguage()">🔍 Detect Language</button>
            </div>
        </div>

        <!-- Navigation and Output Section -->
        <div class="output-section">
            <div class="panel controls-grid">
                <label>Symbol:</label> <input type="text" id="sym" placeholder="e.g. x">
                <label>Line:</label> <input type="number" id="line" value="2">
                <label>New Name:</label> <input type="text" id="newName" placeholder="New name">

                <div style="grid-column: 1 / -1; margin-top: 10px;">
                    <button onclick="runAction('hover')" style="background-color: #569cd6;">ℹ️ Hover Info</button>
                    <button onclick="runAction('goto')" style="background-color: #dcdcaa; color: #1e1e1e;">📍 Go to Definition</button>
                    <button onclick="runAction('rename')" style="background-color: #c586c0;">✏️ Rename Refactor</button>
                </div>
            </div>

            <div class="panel" style="flex: 1;">
                <h3 style="margin-top: 0; color: #d4d4d4;">Output Console & Visualizations</h3>
                <hr style="border-color: #444; margin-bottom: 15px;">
                <div id="visual-canvas"></div>
                <pre id="output">Results will appear here...</pre>
            </div>
        </div>
    </div>

    <script>
        async function postData(url, data) {
            const response = await fetch(url, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            return response.json();
        }

        function getCode() { return document.getElementById('code').value; }

        function showConsole() {
            document.getElementById('output').style.display = 'block';
            document.getElementById('visual-canvas').style.display = 'none';
        }

        function showVisual() {
            document.getElementById('output').style.display = 'none';
            document.getElementById('visual-canvas').style.display = 'block';
        }

        async function runPreprocess() {
            showConsole();
            document.getElementById('output').innerText = "Expanding macros & preprocessing... ⏳";
            const res = await postData('/preprocess', { code: getCode() });
            document.getElementById('output').innerText = res.output;
        }

        async function runPythonPlugin() {
            showConsole();
            document.getElementById('output').innerText = "Parsing Python code via plugin... ⏳";
            const res = await postData('/parse-python', { code: getCode() });
            document.getElementById('output').innerText = res.output;
        }

        async function runDominatorTree() {
            showConsole();
            document.getElementById('output').innerText = "Calculating Dominator Tree... ⏳";
            const res = await postData('/dominator-tree', { code: getCode() });
            document.getElementById('output').innerText = res.output;
        }

        async function runReachingDefinitions() {
            showConsole();
            document.getElementById('output').innerText = "Analyzing Reaching Definitions... ⏳";
            const res = await postData('/reaching-definitions', { code: getCode() });
            document.getElementById('output').innerText = res.output;
        }

        async function runSSAForm() {
            showConsole();
            document.getElementById('output').innerText = "Transforming to SSA Form (ϕ)... ⏳";
            const res = await postData('/ssa-form', { code: getCode() });
            document.getElementById('output').innerText = res.output;
        }

        async function runIncrementalParse() {
            showConsole();
            document.getElementById('output').innerText = "Performing Tree-sitter style Incremental Re-Parse... ⏳";
            const res = await postData('/incremental-parse', { code: getCode() });
            document.getElementById('output').innerText = res.output;
        }

        async function runAnalysis(endpoint) {
            showConsole();
            document.getElementById('output').innerText = "Analyzing code... ⏳";
            const res = await postData('/' + endpoint, { code: getCode() });
            document.getElementById('output').innerText = res.output;
        }

        async function runAction(endpoint) {
            showConsole();
            document.getElementById('output').innerText = "Processing request... ⏳";
            const data = {
                code: getCode(),
                symbol: document.getElementById('sym').value,
                line: parseInt(document.getElementById('line').value),
                new_name: document.getElementById('newName').value
            };
            const res = await postData('/' + endpoint, data);
            document.getElementById('output').innerText = res.output;
        }

        async function runDetectLanguage() {
            showConsole();
            document.getElementById('output').innerText = "Detecting programming language... ⏳";
            const res = await postData('/detect-language', { code: getCode() });

            if (res.language === "Unknown") {
                document.getElementById('output').innerText = "Could not confidently detect the language.";
                return;
            }

            let outputText = `🔎 Detected Language: ${res.language}\n`;
            outputText += `🎯 Confidence: ${res.confidence}%\n\n`;
            outputText += `📊 Scores Breakdown:\n`;
            for (const [lang, score] of Object.entries(res.scores)) {
                outputText += `  - ${lang}: ${score}%\n`;
            }

            document.getElementById('output').innerText = outputText;
        }

        async function runVisualAST() {
            showVisual();
            const visualCanvas = document.getElementById('visual-canvas');
            visualCanvas.innerHTML = "<p style='color:#9cdcfe;'>Generating Graphical AST Tree... ⏳</p>";

            const res = await postData('/ast-visual', { code: getCode() });
            if (res.error) {
                showConsole();
                document.getElementById('output').innerText = "AST Visualizer Error: " + res.error;
                return;
            }

            visualCanvas.innerHTML = `<div class="mermaid">${res.mermaid_graph}</div>`;
            mermaid.run({ nodes: visualCanvas.querySelectorAll('.mermaid') });
        }

        async function runVisualCallGraph() {
            showVisual();
            const visualCanvas = document.getElementById('visual-canvas');
            visualCanvas.innerHTML = "<p style='color:#9cdcfe;'>Generating Visual Call Graph... ⏳</p>";

            const res = await postData('/callgraph-visual', { code: getCode() });
            if (res.error) {
                showConsole();
                document.getElementById('output').innerText = "Call Graph Error: " + res.error;
                return;
            }

            visualCanvas.innerHTML = `<div class="mermaid">${res.mermaid_graph}</div>`;
            mermaid.run({ nodes: visualCanvas.querySelectorAll('.mermaid') });
        }
    </script>
</body>
</html>
"""


def analyze_code_from_web(code_text):
    lexer = Lexer(code_text)
    tokens, _ = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer(file_name="web_editor.c")
    analyzer.analyze(ast)
    return ast, ProgramAnalyzer(ast, analyzer.global_scope, code_text, "web_editor.c")


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/preprocess', methods=['POST'])
def preprocess():
    preprocessor = Preprocessor()
    result = preprocessor.process(request.json['code'])

    output_text = "=== MACRO EXPANSION & PREPROCESSING ===\n\n"
    if result["macros_found"]:
        output_text += "📌 Defined Macros:\n"
        for k, v in result["macros_found"].items():
            output_text += f"  • {k} ➔ {v}\n"
        output_text += "\n📌 Expansions Applied:\n"
        for note in result["expansion_notes"]:
            output_text += f"  • {note}\n"
        output_text += "\n=== PREPROCESSED SOURCE CODE ===\n\n"
        output_text += result["expanded_code"]
    else:
        output_text += "No #define directives found in the source code."

    return jsonify({"output": output_text})


@app.route('/parse-python', methods=['POST'])
def parse_python():
    plugin = PythonPlugin()
    result = plugin.parse(request.json['code'])

    output_text = "=== MULTI-LANGUAGE PLUGIN: PYTHON PARSER ===\n\n"
    output_text += f"📌 Language: {result['language']}\n"
    output_text += f"📌 Total Lines: {result['total_lines']}\n\n"
    output_text += "🔍 Extracted Functions:\n"
    for fn in result['functions']:
        output_text += f"  • {fn}()\n"
    if not result['functions']:
        output_text += "  (None)\n"

    output_text += "\n🔍 Extracted Variables:\n"
    for var in result['variables']:
        output_text += f"  • {var}\n"
    if not result['variables']:
        output_text += "  (None)\n"

    return jsonify({"output": output_text})


@app.route('/dominator-tree', methods=['POST'])
def dominator_tree():
    builder = DominatorTreeBuilder()
    result = builder.analyze(request.json['code'])

    output_text = "=== CONTROL FLOW GRAPH: DOMINATOR TREE ANALYSIS ===\n\n"
    output_text += "📌 Dominator Sets (Dom(n)):\n"
    for block, doms in result["dominators"].items():
        output_text += f"  • Dom({block}) = {{ {', '.join(doms)} }}\n"

    output_text += "\n📌 Immediate Dominators (IDom(n)):\n"
    for block, idom in result["idom"].items():
        output_text += f"  • IDom({block}) ➔ {idom}\n"

    return jsonify({"output": output_text})


@app.route('/reaching-definitions', methods=['POST'])
def reaching_definitions():
    analyzer = ReachingDefinitionsAnalyzer()
    result = analyzer.analyze(request.json['code'])

    output_text = "=== DATA-FLOW ANALYSIS: REACHING DEFINITIONS ===\n\n"
    output_text += "📌 Defined Assignments (Definitions):\n"
    for d in result["definitions"]:
        output_text += f"  • {d}\n"

    output_text += "\n📌 GEN and KILL Sets per Basic Block:\n"
    for block, gk in result["gen_kill"].items():
        output_text += f"  • {block}:\n"
        output_text += f"      GEN  = {{ {', '.join(gk['GEN'])} }}\n"
        output_text += f"      KILL = {{ {', '.join(gk['KILL'])} }}\n"

    output_text += "\n📌 IN and OUT Sets per Basic Block:\n"
    for block, in_out in result["reaching"].items():
        output_text += f"  • {block}:\n"
        output_text += f"      IN  = {{ {', '.join(in_out['IN'])} }}\n"
        output_text += f"      OUT = {{ {', '.join(in_out['OUT'])} }}\n"

    return jsonify({"output": output_text})


@app.route('/ssa-form', methods=['POST'])
def ssa_form():
    transformer = SSATransformer()
    result = transformer.transform(request.json['code'])

    output_text = "=== STATIC SINGLE ASSIGNMENT (SSA) FORM TRANSFORMATION ===\n\n"
    output_text += "📌 Inserted Phi-Functions (ϕ):\n"
    for phi in result["phi_nodes"]:
        output_text += f"  • {phi}\n"

    output_text += "\n=== TRANSFORMED SSA CODE ===\n\n"
    output_text += "\n".join(result["ssa"])

    return jsonify({"output": output_text})


@app.route('/incremental-parse', methods=['POST'])
def incremental_parse():
    global previous_code_cache
    new_code = request.json['code']

    if not previous_code_cache:
        result = incremental_parser_instance.parse_full(new_code)
        previous_code_cache = new_code
        output_text = "=== INCREMENTAL PARSER: INITIAL FULL PARSE ===\n\n"
        output_text += f"📌 Mode: {result['mode']}\n"
        output_text += f"📌 Total Lines Parsed: {result['total_lines_parsed']}\n"
        output_text += f"📌 AST Cache Initialized with {result['ast_cache_size']} nodes.\n"
    else:
        result = incremental_parser_instance.parse_incremental(previous_code_cache, new_code)
        previous_code_cache = new_code
        output_text = "=== INCREMENTAL PARSER: PARTIAL TREE RE-PARSE ===\n\n"
        output_text += f"📌 Mode: {result['mode']} (Tree-sitter strategy)\n"
        output_text += f"📌 Modified Line Regions Detected: {result['modified_regions']}\n"
        output_text += f"📌 Reparsed Lines: {result['reparsed_lines']}\n"
        output_text += f"📌 Status: {result['status']}\n"

    return jsonify({"output": output_text})


@app.route('/dead-code', methods=['POST'])
def dead_code():
    _, analyzer = analyze_code_from_web(request.json['code'])
    reports = analyzer.detect_dead_code()
    return jsonify({"output": "\n".join(reports)})


@app.route('/eliminate-dead-code', methods=['POST'])
def eliminate_dead_code():
    _, analyzer = analyze_code_from_web(request.json['code'])
    optimized_code = analyzer.eliminate_dead_code()
    return jsonify({"output": optimized_code})


@app.route('/generate-ir', methods=['POST'])
def generate_ir():
    ast, _ = analyze_code_from_web(request.json['code'])
    generator = IRGenerator()
    tac_code = generator.generate(ast)
    return jsonify({"output": tac_code if tac_code else "No TAC generated."})


@app.route('/data-flow', methods=['POST'])
def data_flow():
    _, analyzer = analyze_code_from_web(request.json['code'])
    reports = analyzer.analyze_definite_assignment()
    return jsonify({"output": "\n".join(reports)})


@app.route('/callgraph', methods=['POST'])
def callgraph():
    _, analyzer = analyze_code_from_web(request.json['code'])
    cg = {k: list(v) for k, v in analyzer.build_call_graph().items()}
    return jsonify({"output": json.dumps(cg, indent=2)})


@app.route('/callgraph-visual', methods=['POST'])
def callgraph_visual():
    try:
        _, analyzer = analyze_code_from_web(request.json['code'])
        cg = analyzer.build_call_graph()

        mermaid_lines = ["graph TD"]
        for caller, callees in cg.items():
            for callee in callees:
                mermaid_lines.append(f"    {caller} --> {callee}")

        if len(mermaid_lines) == 1:
            mermaid_lines.append("    NoCallsFound[No Function Calls Detected]")

        return jsonify({"mermaid_graph": "\n".join(mermaid_lines)})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/ast-visual', methods=['POST'])
def ast_visual():
    try:
        ast, _ = analyze_code_from_web(request.json['code'])
        node_counter = 0
        mermaid_lines = ["graph TD"]

        def walk_ast(node, parent_id=None):
            nonlocal node_counter
            node_counter += 1
            current_id = f"node_{node_counter}"

            node_label = type(node).__name__
            if hasattr(node, 'name') and node.name:
                node_label += f"({node.name})"
            elif hasattr(node, 'value') and node.value:
                node_label += f"({node.value})"

            mermaid_lines.append(f'    {current_id}["{node_label}"]')

            if parent_id:
                mermaid_lines.append(f"    {parent_id} --> {current_id}")

            for attr in dir(node):
                if not attr.startswith('_'):
                    val = getattr(node, attr)
                    if isinstance(val, list):
                        for item in val:
                            if hasattr(item, '__class__') and hasattr(item, '__dict__'):
                                walk_ast(item, current_id)
                    elif hasattr(val, '__class__') and hasattr(val, '__dict__'):
                        walk_ast(val, current_id)

        walk_ast(ast)
        return jsonify({"mermaid_graph": "\n".join(mermaid_lines)})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/hover', methods=['POST'])
def hover():
    req = request.json
    if not req.get('symbol'): return jsonify({"output": "Error: Please enter a symbol name."})
    _, analyzer = analyze_code_from_web(req['code'])
    res = analyzer.hover_info(req['symbol'], req['line'])
    return jsonify({"output": res})


@app.route('/goto', methods=['POST'])
def goto():
    req = request.json
    if not req.get('symbol'): return jsonify({"output": "Error: Please enter a symbol name."})
    _, analyzer = analyze_code_from_web(req['code'])
    res = analyzer.goto_definition_json(req['symbol'], req['line'])
    return jsonify({"output": json.dumps(res, indent=2)})


@app.route('/rename', methods=['POST'])
def rename():
    req = request.json
    if not req.get('symbol') or not req.get('new_name'):
        return jsonify({"output": "Error: Please enter both Symbol and New Name."})
    _, analyzer = analyze_code_from_web(req['code'])
    ok, new_code, diff = analyzer.safe_rename(req['symbol'], req['new_name'], req['line'])
    return jsonify({"output": diff if ok else f"Error: {new_code}"})


@app.route('/detect-language', methods=['POST'])
def detect_language():
    data = request.json
    code = data.get('code', '')
    filename = data.get('filename', '')

    detector = LanguageDetector()
    result = detector.detect(code, filename)
    return jsonify(result)


if __name__ == '__main__':
    print("🌟 Visual Compiler Web UI is starting! Open your browser: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)