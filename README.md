# 🚀 Compiler & Advanced IDE Infrastructure

[![CI/CD Pipeline](https://github.com/ZahraAghaeii/CompilerProject/actions/workflows/ci.yml/badge.svg)](https://github.com/ZahraAghaeii/CompilerProject/actions)

An end-to-end **Compiler Front-End** and **Advanced Web-Based IDE Analysis Engine** built in Python and Flask.

This project covers the complete compilation pipeline, from **lexical analysis** to **abstract syntax tree generation**, **semantic analysis**, **intermediate code generation (TAC)**, and advanced IDE features including **Data-Flow Analysis**, **Dead Code Elimination (DCE)**, **Visual Call Graph Generation**, **Interactive AST Diagrams**, **Automatic Language Detection**, and **Safe Refactoring**.

---

# 📌 Features & Architecture

## 🔍 1. Compiler Front-End Pipeline

- **Lexer (`src/lexer.py`)**
  - Tokenizes source code according to the EBNF grammar specification with line and column tracking.

- **Parser (`src/parser.py`)**
  - Builds the Abstract Syntax Tree (AST) using modular AST node definitions.

- **Semantic Analyzer (`src/semantic.py`)**
  - Performs type checking, symbol table construction, identifier validation, and scope verification.

- **Syntax Highlighter (`src/highlighter.py`)**
  - Produces syntax-highlighted HTML output for source code visualization.

- **Auto-Completion (`src/completion.py`)**
  - Provides intelligent code completion suggestions based on scope analysis.

---

## ⚡ 2. Advanced Program Analysis & IDE Engine

- **Dead Code Detection & Elimination (DCE) (`src/program_analysis.py`)**
  - Detects unreachable statements, unused variable declarations, and automatically removes dead code paths.

- **Intermediate Code Generation (TAC / IR Generation) (`src/ir_generator.py`)**
  - Transforms the AST into linear Three-Address Code (TAC) for intermediate representation and optimization analysis.

- **Data-Flow Analysis (`src/program_analysis.py`)**
  - Tracks variable definitions, uses, liveness, and definite assignment across control-flow paths.

- **Call Graph Generation & Visualization (`web_ui.py`)**
  - Builds inter-procedural function call graphs with both JSON output and interactive visual diagrams using Mermaid.js.

- **Safe Rename Refactoring**
  - Renames identifiers safely across the code while preserving scope correctness and displaying a unified diff.

---

## 🌟 3. Bonus Features & Advanced Compiler Analyses (100% Coverage)

- **⚙️ Preprocessor / Macro Expansion (`src/preprocessor.py`)**
  - Detects and resolves `#define` directives and expands macro substitutions prior to lexical evaluation.

- **🐍 Multi-Language Support via Plugin Architecture (`src/python_plugin.py`)**
  - Modular plugin allowing Python code parsing and analysis alongside C/C++ without modifying core stages.

- **🌳 Dominator Tree Analysis (`src/dominator_tree.py`)**
  - Computes Dominator Sets ($\text{Dom}(n)$) and Immediate Dominators ($\text{IDom}(n)$) over Control Flow Graphs (CFG).

- **📍 Reaching Definitions Analysis (`src/reaching_definitions.py`)**
  - Implements data-flow algorithms calculating $\text{GEN}$, $\text{KILL}$, $\text{IN}$, and $\text{OUT}$ sets per basic block.

- **🔄 Static Single Assignment (SSA) Transformation (`src/ssa_transformer.py`)**
  - Transforms code to SSA form with unique variable versions and $\phi$-function insertions at merge points.

- **⚡ Incremental Re-Parsing (`src/incremental_parser.py`)**
  - Uses AST caching (Tree-sitter strategy) to re-parse only modified line regions for real-time responsiveness.

- **🔍 Automatic Language Detection (`src/detector.py`)**
  - Predicts the programming language of an input code snippet (Python, C/C++, Java, JavaScript, Bash) using:
    - Shebang detection
    - Keyword frequency analysis
    - Delimiter patterns
    - Indentation style
    - File extension analysis

- **🌳 Interactive AST Visualizer (`web_ui.py`)**
  - Renders interactive, graphical AST diagrams in real-time using Mermaid.js.

- **📊 Visual Call Graph Rendering (`web_ui.py`)**
  - Graphical representation of function dependencies directly within the Web IDE console.

- **⚡ Three-Address Code (TAC) Generator (`src/ir_generator.py`)**
  - Renders low-level intermediate code instructions (`t1 = 5 + 3`, `x = t1`) from source code.

- **✂️ Automatic Dead Code Elimination (DCE)**
  - Cleans up AST/source code by stripping unreferenced variables and unused code constructs.

- **🐳 Docker Containerization**
  - Full Docker support (`Dockerfile`) for environment isolation, containerized testing, and seamless deployment.

- **🧪 Automated Unit Testing & Coverage**
  - Full `pytest` integration covering Lexer, Parser, Semantic Analyzer, IR Generator, Preprocessor, SSA, and Language Detector components with coverage report generation.

- **📊 CI/CD Automation**
  - GitHub Actions automatically runs tests, generates HTML outputs, and deploys reports to GitHub Pages.

---

# 🛠️ Project Structure

```text
CompilerProject/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── advanced-ci.yml
├── grammar/
│   └── grammar.ebnf
├── src/
│   ├── ast_nodes.py
│   ├── completion.py
│   ├── detector.py
│   ├── dominator_tree.py
│   ├── highlighter.py
│   ├── incremental_parser.py
│   ├── ir_generator.py
│   ├── lexer.py
│   ├── parser.py
│   ├── preprocessor.py
│   ├── program_analysis.py
│   ├── python_plugin.py
│   ├── reaching_definitions.py
│   ├── repl.py
│   ├── semantic.py
│   └── ssa_transformer.py
├── tests/
│   ├── __pycache__/
│   ├── semantic_test.c
│   ├── test_advanced_analysis.py
│   ├── test_code.c
│   ├── test_compiler.py
│   ├── test_incremental_parser.py
│   ├── test_lexer_edges.py
│   ├── test_preprocessor.py
│   ├── test_semantic_errors.c
│   ├── test_semantic_scopes.c
│   └── test_semantic_types.c
├── Dockerfile
├── main.py
├── README.md
├── requirements.txt
└── web_ui.py
```

---

# 💻 Installation & Usage

## Prerequisites

- Python 3.10+
- Dependencies: Install via `requirements.txt`

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

### Run the Compiler via CLI

```bash
python main.py tests/test_code.c
```

### Launch the Web IDE (with AST & Visual Features)

```bash
python web_ui.py
```

Then open your browser at:

```text
[http://127.0.0.1:5000](http://127.0.0.1:5000)
```

---

# 🐳 Docker Deployment

To build and run the compiler project using Docker:

```bash
# Build the Docker image
docker build -t compiler-project .

# Run the container
docker run -p 5000:5000 compiler-project
```

---

# 🧪 Automated Testing & Coverage

This project uses `pytest` and `pytest-cov` for automated testing and code coverage analysis.

### Run Unit Tests
```bash
python -m pytest tests/
```

### Run Tests with Coverage Report
```bash
python -m pytest --cov=src tests/
```

### 1. Preprocessor Tests (`tests/test_preprocessor.py`)
Verifies Macro Expansions (`#define`) and ensures no name collision occurs during replacement.

**Run this test:**
```bash
python -m pytest tests/test_preprocessor.py
```

### 2. Advanced Analysis Tests (`tests/test_advanced_analysis.py`)
Verifies the CFG Dominator Tree logic and the proper insertion of $\phi$-functions for Static Single Assignment (SSA) form.

**Run this test:**
```bash
python -m pytest tests/test_advanced_analysis.py
```
### 3. Incremental Parser Tests (`tests/test_incremental_parser.py`)
Validates the AST caching mechanism to ensure only modified lines are re-parsed for better IDE performance.

**Run this test:**
```bash
python -m pytest tests/test_incremental_parser.py
```
### 4. Lexer Edge Cases Tests (`tests/test_lexer_edges.py`)
Tests error recovery mechanisms for specific syntax mistakes like unclosed block comments, unterminated strings, and invalid characters.

**Run this test:**
```bash
python -m pytest tests/test_lexer_edges.py
```
---

# 📊 CI/CD Workflow

GitHub Actions automatically performs the following tasks:

- ✅ Runs the complete unit test suite on every **push** and **pull request**
- ✅ Generates syntax-highlighted HTML outputs
- ✅ Builds project artifacts
- ✅ Publishes reports through GitHub Pages
- ✅ Displays workflow status using the GitHub Actions badge

---

# 📄 License

This project was developed for educational purposes as part of a Compiler Design course.

---

## 👩‍💻 Authors

- **Zahra Aghaeii**
- **mobinFallahiEshratabadi**
- **AriaTn84**
- **koamz**