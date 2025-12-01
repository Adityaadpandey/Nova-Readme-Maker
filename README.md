# 📖  Nova README Generator

**An advanced command‑line tool that clones a Git repository, performs deep project analysis, and uses an AI model to generate a comprehensive README.**

---

## ✨ Overview

- **Deep analysis** of the target repository (language, complexity, project structure).
- **AI‑powered README generation** via Ollama – the output is tailored to the project’s real architecture.
- **Shallow analysis mode** for quick runs on large repos.
- **Debug mode** keeps intermediate files for troubleshooting.
- Works with **Python ≥ 3.12** and only relies on open‑source libraries.

---

## 🚀 Installation

```bash
git clone https://github.com/Adityaadpandey/Nova-Readme-Maker
cd Nova-Readme-Maker
pip install .
```

---

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--repo` *required* | — | Git repository URL to analyze. |
| `--model` | `llama3.2:latest` | Ollama model name (e.g., `llama3.2:3b`, `gpt4o-mini`). |
| `--debug` | `False` | Keeps all debug files (cloned repo, analysis logs). |
| `--shallow` | `False` | Performs a fast shallow analysis (shallow clone + limited checks). |
| `--simple` | `False` | (Available via `python run.py `) Skips all prompts, uses defaults. |

---

## 💡 Quick Start

```bash
# Basic run (deep analysis, default model)
python run.py  --repo https://github.com/user/project

# Use a specific Ollama model
python run.py  --repo https://github.com/user/project --model llama3.2:3b

# Enable debug mode
python run.py  --repo https://github.com/user/project --debug

# Shallow analysis (faster but less thorough)
python run.py  --repo https://github.com/user/project --shallow
```

---

## 🔧 Configuration

All configuration is handled via command‑line flags. No external config files are required.
If you wish to **reuse a model** across multiple runs, simply add the `--model` flag with your preferred model name.

---

## 🧰 How It Works

1. **Clones** the target repo into a temporary `cloned_repo/` directory (shallow clone by default).
2. **Analyzes** the repository structure, detecting language(s), file‑types, and an estimated `complexity_score`.
3. **Generates a prompt** for Ollama that reflects the real architecture of the repo.
4. **Runs** the selected Ollama model to produce a markdown README.
5. **Writes** the generated README to `README.md` in the repository’s root.

Debugging information (clone logs, analysis outputs) are stored in `cloned_repo/` if `--debug` is set.

---

## 🤝 Contributing

Pull requests are welcome!
If you discover bugs or want to add features, feel free to open an issue or submit a PR.
Please keep the code focused on **CLI usability** and **AI‑driven generation** – this repository is a minimal, self‑contained tool.

---

## 📄 License

Refer to the [LICENSE](LICENSE) file in this repository for licensing terms.
If no license file is present, the legal terms are defined by the repository’s contents.

---

## 👤 Author

Built for the open‑source community.
© 2024 – Adityaadpandey

---
