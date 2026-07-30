# 🚀 Compiler & Advanced IDE Infrastructure

[![CI/CD Pipeline](https://github.com/ZahraAghaeii/CompilerProject/actions/workflows/ci.yml/badge.svg)](https://github.com/ZahraAghaeii/CompilerProject/actions)

An end-to-end **Compiler Front-End** and **Advanced Web-Based IDE Analysis Engine** built in Python.

This project covers the complete compilation pipeline, from **lexical analysis** to **abstract syntax tree generation**, **semantic analysis**, and advanced IDE features including **Data-Flow Analysis**, **Call Graph Generation**, **Automatic Language Detection**, and **Safe Refactoring**.

---

# 📌 Features & Architecture

## 🔍 1. Compiler Front-End Pipeline

- **Lexer (`src/lexer.py`)**
  - Tokenizes source code according to the EBNF grammar specification.

- **Parser (`src/parser.py`)**
  - Builds the Abstract Syntax Tree (AST) using modular AST node definitions.

- **Semantic Analyzer (`src/semantic.py`)**
  - Performs type checking, symbol table construction, and scope validation.

- **Syntax Highlighter (`src/highlighter.py`)**
  - Produces syntax-highlighted HTML output for source code visualization.

---

## ⚡ 2. Advanced Program Analysis & IDE Engine

- **Dead Code Detection**
  - Detects unreachable statements and unused code blocks.

- **Data-Flow Analysis (`src/program_analysis.py`)**
  - Tracks variable definitions, uses, and liveness across control-flow paths.

- **Call Graph Generation**
  - Builds function call graphs for inter-procedural analysis.

- **Safe Rename Refactoring**
  - Renames identifiers safely while preserving scope correctness.

- **Auto-Completion (`src/completion.py`)**
  - Provides intelligent code completion suggestions based on scope analysis.

---

## 🌟 3. Bonus Features

- **Automatic Language Detection (`src/detector.py`)**
  - Predicts the programming language of an input code snippet (Python, C/C++, Java, JavaScript, Bash) using:
    - Shebang detection
    - Keyword frequency analysis
    - Delimiter patterns
    - Indentation style
    - File extension

- **CI/CD Automation**
  - GitHub Actions automatically runs tests, generates HTML outputs, and deploys reports to GitHub Pages.

---

# 🛠️ Project Structure

```text
CompilerProject/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── advanced-ci.yml
│
├── grammar/
│   └── grammar.ebnf
│
├── src/
│   ├── ast_nodes.py
│   ├── completion.py
│   ├── detector.py
│   ├── highlighter.py
│   ├── lexer.py
│   ├── parser.py
│   ├── program_analysis.py
│   ├── repl.py
│   └── semantic.py
│
├── tests
│   ├── semantic_test.c
│   ├── test_code.c
│   ├── test_semantic_errors.c
│   ├── test_semantic_scopes.c
│   └── test_semantic_types.c
│
├── web_ui.py
├── main.py
└── README.md
```

---

# 💻 Installation

## Prerequisites

- Python 3.10+
- Flask

Install the required package:

```bash
pip install flask
```

---

# ▶️ Usage

## Run the Compiler via CLI

```bash
python main.py tests/test_code.c
```

---

## Launch the Web IDE

```bash
python web_ui.py
```

Then open:

```
http://127.0.0.1:5000
```

---

<!-- # 🧪 Running Tests

Execute all unit tests:

```bash
python -m unittest discover -s tests
``` -->

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