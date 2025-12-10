# 🚀 Nova-Readme-Maker

> An intelligent README generator that analyzes GitHub repositories and creates professional documentation through AI-powered code understanding and interactive refinement.

## 📋 Description

Nova-Readme-Maker is a sophisticated command-line tool that automates the creation of comprehensive README files for software projects. It combines deep repository analysis with interactive LLM-guided workflows to generate context-aware documentation tailored to your project's complexity and target audience.

The tool clones your GitHub repository, performs multi-layer code analysis, engages you with clarifying questions, and produces a polished README.md file without requiring manual content creation.

## 🎯 Key Features

- **🔍 Deep Repository Analysis** - Automatically detects languages, frameworks, dependencies, commands, databases, and project architecture
- **🧠 AI-Powered Generation** - Uses LLM models (Ollama, OpenAI, Anthropic) to create context-aware documentation
- **💬 Interactive Refinement** - Multi-phase workflow with user confirmation, clarifying questions, and iterative improvement
- **⚡ Multi-Version Support** - Three generator versions (V2, V3, Interactive) with progressive capabilities
- **🎨 Flexible Templates** - Four README styles (minimal, standard, detailed, comprehensive) to match your needs
- **🔗 Vector-Aware Context** - Optional semantic search using embeddings for intelligent content retrieval
- **🛠️ Multi-Language Support** - Analyzes Python, JavaScript, TypeScript, Java, Go, Rust, PHP, and more

## 📦 Installation

### Requirements
- Python 3.12+
- Git (for repository cloning)

### Install from Source

```bash
git clone https://github.com/Adityaadpandey/Nova-Readme-Maker.git
cd Nova-Readme-Maker
pip install -e .
```

### Using pip

```bash
pip install readme-generator
```

## 🚀 Commands

### Basic Usage

Run with default Ollama model:
```bash
python main.py
```

### Interactive Mode (Recommended)

```bash
python interactive_readme.py --repo <GitHub-URL> --model <model-name>
```

### Advanced Generation (V3)

```bash
python readme_generator_v3.py --repo <GitHub-URL> --model <model-name> --debug
```

### Command-Line Tools

```bash
# Using installed package
readme-gen --repo https://github.com/user/project --model llama3.2:latest
readme-gen-simple
```

## 🎛️ Options

### Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `--repo` | GitHub repository URL (required) | — |
| `--model` | LLM model to use | `llama3.2:latest` |
| `--api-key` | API key for cloud models (OpenAI/Anthropic) | — |
| `--debug` | Enable detailed logging | `false` |
| `--embeddings` | Enable vector store for semantic search | `true` |
| `--embedding-provider` | Embedding provider: `local`, `openai`, `ollama` | `local` |

### Supported Models

**Local (Ollama):**
```bash
python main.py --model llama3.2:latest
python main.py --model llama2
python main.py --model mistral
```

**Cloud-Based:**
```bash
python main.py --model gpt-4 --api-key sk-...
python main.py --model claude-3-sonnet --api-key sk-ant-...
```

## 📖 Examples

### Generate README for a Python Project

```bash
python interactive_readme.py --repo https://github.com/pallets/flask --model llama3.2:latest
```

The tool will:
1. Clone the repository
2. Analyze project structure, dependencies, and code architecture
3. Present findings for your confirmation
4. Ask clarifying questions about purpose and audience
5. Let you select a README style
6. Generate a professional README.md
7. Offer iterative refinement options

### Generate with Debug Information

```bash
python readme_generator_v3.py --repo https://github.com/torvalds/linux --model gpt-4 --api-key YOUR_API_KEY --debug
```

### Use Vector Store for Enhanced Context

```bash
python main.py --repo https://github.com/owner/project --embeddings true --embedding-provider local
```

## ⚙️ Configuration

### Environment Variables

```bash
export OLLAMA_BASE_URL=http://localhost:11434
export OPENAI_API_KEY=sk-your-api-key
export ANTHROPIC_API_KEY=sk-ant-your-api-key
```

### Using Configuration File

Create a `.readme-config.yaml`:

```yaml
model: llama3.2:latest
debug: false
use_embeddings: true
embedding_provider: local
api_key: null
```

Then run:
```bash
python main.py --config .readme-config.yaml
```

## 🏗️ Architecture Overview

### Core Components

| Component | Purpose |
|-----------|---------|
| **EnhancedProjectAnalyzer** | Scans repository structure, detects tech stack, dependencies, commands |
| **DeepCodeAnalyzer** | Parses source code across languages to extract functions, classes, routes, models |
| **QuestionEngine** | Generates targeted clarifying questions based on project analysis |
| **TemplateManager** | Provides four configurable README style templates |
| **VectorStore** | Stores and retrieves project context via semantic embeddings |

### Data Flow

```
GitHub URL
    ↓
[Clone Repository]
    ↓
[Analyze Project Structure]
[Analyze Source Code]
    ↓
[Present Auto-Detected Findings]
    ↓
[Ask Clarifying Questions]
    ↓
[Merge Auto-Detected + User Input]
    ↓
[Select README Style]
    ↓
[Generate README with LLM]
    ↓
[User Review & Refinement]
    ↓
[Output README.md]
```

## 🔧 Development

### Project Structure

```
Nova-Readme-Maker/
├── main.py                      # Simple entry point
├── interactive_readme.py         # Interactive multi-phase generator
├── readme_generator_v2.py       # Enhanced generator with embeddings
├── readme_generator_v3.py       # Advanced generator with vector store
├── deep_analyzer.py             # Code parsing and analysis
├── analyzer.py                  # Project structure analysis
├── question_engine.py           # LLM-based question generation
├── template_manager.py          # README style templates
├── vector_store.py              # Vector database for context
├── providers.py                 # LLM provider abstraction
└── pyproject.toml              # Project configuration
```

### Dependencies

```
gitpython>=3.1.44      # Repository cloning
ollama>=0.5.1          # Local LLM support
pyyaml>=6.0            # Configuration parsing
sentence-transformers  # Embeddings (optional)
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ by [Aditya Pandey](https://github.com/Adityaadpandey)**

Have questions? Open an issue on [GitHub](https://github.com/Adityaadpandey/Nova-Readme-Maker/issues)