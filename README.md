# NOVA

[![Version](https://img.shields.io/badge/version-3.0.0-blue)](#)
[![Python](https://img.shields.io/badge/python-%3E%3D3.12-3776AB?logo=python&logoColor=white)](#)
[![License](https://img.shields.io/badge/license-Not%20specified-lightgrey)](#)

Nova is an AI-powered README generator that performs deep code scanning and (optionally) semantic retrieval over your codebase to produce high-quality, accurate documentation. It analyzes project structure, detects languages/frameworks, extracts key entities (functions/classes/routes/config), and can use embeddings to ground README generation in the actual code.

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [CLI commands](#cli-commands)
  - [Choosing a model/provider](#choosing-a-modelprovider)
- [Project Structure](#project-structure)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Deep project scanning**
  - Extracts detailed metadata for **functions**, **classes**, **routes**, and **config**.
  - Detects languages and common frameworks/technologies (e.g., FastAPI, Flask, Django, Vue, Angular, Next.js, etc.).
- **Semantic code search (embeddings)**
  - Chunking + vector search for retrieving relevant code context during generation.
  - Supports multiple embedding backends:
    - **Local** (`sentence-transformers`) – free, offline
    - **OpenAI** – hosted embeddings
    - **Ollama** – local embeddings/models
- **Interactive CLI UX**
  - Rich terminal UI (panels, progress, styled prompts).
  - Smart, context-aware questions to fill in missing project intent/details.
- **Multiple generator entrypoints**
  - `nova` (main CLI)
  - `nova-v2` (v2 generator)
  - `nova-simple` (simplified flow)

Integrations:

- **OpenAI** (and code references indicate support for local and Ollama-based workflows)

---

## Quick Start

```bash
pip install -r requirements.txt
```

Then run Nova in your repository:

```bash
nova
```

Nova will analyze the current directory, ask a few questions (if needed), and generate/update `README.md`.

---

## Prerequisites

- **Python >= 3.12** (per `pyproject.toml`)
- If using **local embeddings**:
  - `sentence-transformers` (installed separately if not included in your environment)
- If using **Ollama-based generation/embeddings**:
  - Ollama installed and available on your `PATH` (`ollama` command works)

---

## Installation

### Option A: Install dependencies (repo-style)

```bash
pip install -r requirements.txt
```

### Option B: Install as a package (if you build/publish it)

This repository defines a Python package named `nova` with console scripts in `pyproject.toml`. If you install it as a package (editable or standard), you should get:

- `nova`
- `nova-v2`
- `nova-simple`

Example (editable install):

```bash
pip install -e .
```

---

## Usage

### CLI commands

Run one of the available entrypoints:

```bash
nova
```

```bash
nova-v2
```

```bash
nova-simple
```

What they do (high-level):

- **`nova`**: primary CLI experience (interactive, Rich UI, project scanning + generation).
- **`nova-v2`**: alternate generator flow (useful if you prefer the v2 pipeline).
- **`nova-simple`**: streamlined generation path.

### Choosing a model/provider

Nova supports multiple “provider” concepts across generation and embeddings:

- **Embeddings** (see `vectors.py`):
  - `LocalEmbeddingProvider` (sentence-transformers)
  - `OpenAIEmbeddingProvider`
  - `OllamaEmbeddingProvider`
- **Generation** (example: `simple_gen.py` uses Ollama via `subprocess.run(["ollama", "run", model], ...)`)

If you use the “simple” generator path with Ollama, you’ll typically specify or rely on a default model like:

- `llama3.2:latest` (default shown in `simple_gen.py`)

Example (conceptual):

```bash
# run nova-simple and select an Ollama model when prompted (if supported by the CLI)
nova-simple
```

---

## Project Structure

Key modules (based on the codebase overview):

- `analyzer.py`
  - Enhanced repository analysis (language/framework detection, ignore patterns, dependency heuristics).
- `scanner.py`
  - Deep AST/static scanning for:
    - `FunctionInfo`, `ClassInfo`, `RouteInfo`, `ConfigInfo`, etc.
  - Produces a `ProjectContext` used to drive README generation.
- `vectors.py`
  - Semantic search layer:
    - `CodeChunk` and `CodeChunker` for chunking code into meaningful segments
    - `VectorStore` for in-memory similarity search (cosine similarity)
    - Embedding providers (local/OpenAI/Ollama)
    - `create_embedding_provider(...)` factory
- `questions.py`
  - Smart question engine to collect missing information from the user.
- `prompts.py`
  - Prompt builder that composes “expert-level” README prompts from analysis + key files.
- `sections.py`
  - Section-by-section README generation strategy (conditional inclusion like env vars/routes/tests).
- `templates.py`
  - Template manager for different README styles (minimal/standard/detailed/comprehensive).
- `ui.py`
  - Rich-based CLI UI: banners, panels, progress, styled question prompts.
- `simple_gen.py`
  - Ollama-driven README generation with output cleaning and optional debug export.

---

## Development

This repository does not advertise a dedicated dev/test/build command set, but typical workflows:

### Run locally

```bash
nova
```

### Debug analysis output

Some flows write `project_analysis.json` when `DEBUG` is set:

```bash
DEBUG=1 nova-simple
```

### Code style & checks

No formatter/linter configuration is shown in the provided snapshot. If you add them, common choices for Python 3.12 projects:

- `ruff` (lint + format)
- `black` (format)
- `mypy` (types)

---

## Troubleshooting

### `sentence-transformers not installed`

If you select local embeddings and see an ImportError, install:

```bash
pip install sentence-transformers
```

### Ollama command not found / model fails to run

- Ensure Ollama is installed and `ollama` is on your PATH.
- Verify the model exists locally:

```bash
ollama list
```

- Try running the model directly:

```bash
ollama run llama3.2:latest
```

### Generation times out on large/complex repos

The “simple” generator increases timeout for complex projects, but very large repos may still take time. Consider:

- Running on a smaller subset
- Using a faster model
- Ensuring your machine has enough RAM/CPU if using local models/embeddings

---

## Contributing

Contributions are welcome—especially improvements to:

- framework/route detection in `scanner.py`
- better chunking and retrieval quality in `vectors.py`
- additional templates and section logic in `templates.py` / `sections.py`
- CLI ergonomics and UX in `ui.py`

Suggested process:

1. Fork the repo
2. Create a feature branch
3. Make changes with clear commit messages
4. Open a PR describing:
   - what changed
   - why it changed
   - how to test it manually (since automated tests are not currently detected)

---

## License

No license value was provided in the project metadata.
If you intend this project to be open source, add a `LICENSE` file and update `pyproject.toml` with the correct license identifier (e.g., MIT, Apache-2.0, GPL-3.0).
