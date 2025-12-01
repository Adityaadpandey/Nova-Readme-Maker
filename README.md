# 📝 README Generator v2.0

An intelligent, interactive README generator that deeply understands your codebase and creates comprehensive documentation through conversation.

## ✨ What's New in v2.0

- **Multi-Provider Support**: Use Ollama (local), OpenAI, or Claude
- **Interactive Q&A**: The AI asks smart questions about your project before generating
- **Deep Code Understanding**: Analyzes actual code logic, not just config files
- **Multi-Pass Generation**: Analyze → Ask → Understand → Generate → Refine
- **Template System**: Choose from minimal, standard, detailed, or comprehensive styles
- **Iterative Refinement**: Review drafts and request specific changes
- **Missing Info Detection**: Identifies gaps and asks you to fill them

## 🚀 Quick Start

```bash
# Clone this repo
git clone https://github.com/Adityaadpandey/ReadmeMaker.git
cd ReadmeMaker

# Install dependencies
pip install -e .

# Run with Ollama (default)
python run.py https://github.com/user/project

# Run with OpenAI
export OPENAI_API_KEY=sk-...
python run.py https://github.com/user/project --model gpt-4o

# Run with Claude
export ANTHROPIC_API_KEY=sk-ant-...
python run.py https://github.com/user/project --model claude-3-5-sonnet-20241022
```

## 📋 Requirements

- Python 3.12+
- One of the following LLM providers:

| Provider | Setup | Models |
|----------|-------|--------|
| **Ollama** (local, free) | [Install Ollama](https://ollama.ai/), run `ollama pull llama3.2:latest` | llama3.2, mistral, codellama, etc. |
| **OpenAI** | Set `OPENAI_API_KEY` env var | gpt-4o, gpt-4o-mini, o1-preview |
| **Claude** | Set `ANTHROPIC_API_KEY` env var | claude-3-5-sonnet, claude-3-opus |

For cloud providers:
```bash
pip install openai      # For OpenAI
pip install anthropic   # For Claude
```

## 🎯 Usage

### Basic Usage

```bash
# Interactive mode with Ollama (default)
python run.py https://github.com/user/project

# Simple mode (no questions)
python run.py https://github.com/user/project --simple
```

### Using Different Models

```bash
# Ollama models
python run.py https://github.com/user/project --model llama3.2:3b
python run.py https://github.com/user/project --model mistral
python run.py https://github.com/user/project --model codellama

# OpenAI models (auto-detected from name)
python run.py https://github.com/user/project --model gpt-4o
python run.py https://github.com/user/project --model gpt-4o-mini
python run.py https://github.com/user/project --model o1-preview

# Claude models (auto-detected from name)
python run.py https://github.com/user/project --model claude-3-5-sonnet-20241022
python run.py https://github.com/user/project --model claude-3-opus-20240229

# Explicit provider prefix
python run.py https://github.com/user/project --model openai:gpt-4o
python run.py https://github.com/user/project --model claude:claude-3-haiku-20240307
```

### API Key Options

```bash
# Via environment variable (recommended)
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

# Via command line
python run.py https://github.com/user/project --model gpt-4o --api-key sk-...
```

## 📊 README Styles

| Style | Description | Best For |
|-------|-------------|----------|
| **Minimal** | Quick start only, ~50 lines | Simple scripts, utilities |
| **Standard** | Balanced coverage, ~150 lines | Most projects |
| **Detailed** | Comprehensive with examples, ~300 lines | Complex projects |
| **Comprehensive** | Everything included, 400+ lines | Enterprise projects |
| **API** | Focused on API documentation | Backend/API projects |
| **CLI** | Focused on commands and options | CLI tools |
| **Library** | Focused on API reference | npm/pip packages |
| **Data Science** | Includes model/dataset info | ML projects |

## 🔄 Generation Flow

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: Clone & Analyze                                   │
│  - Clone repository                                         │
│  - Detect languages, frameworks, technologies               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: Deep Code Analysis                                │
│  - Find entry points, classes, functions                    │
│  - Identify routes, models, integrations                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: Present Findings                                  │
│  - Show detected technologies                               │
│  - Allow corrections                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4: Interactive Q&A                                   │
│  - Ask about project purpose, audience, features            │
│  - Context-specific questions                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 5: AI Code Understanding                             │
│  - LLM analyzes source code                                 │
│  - User can correct understanding                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 6: Choose Style                                      │
│  - Suggest best template                                    │
│  - User selects preferred style                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 7: Generate README                                   │
│  - Create with all gathered context                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 8: Review & Refine                                   │
│  - Accept, refine, or regenerate                            │
│  - Check for missing info                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 9: Save & Cleanup                                    │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
readme-generator/
├── run.py                  # Quick launcher
├── readme_generator_v2.py  # Main interactive generator
├── model_provider.py       # Multi-provider LLM support (Ollama/OpenAI/Claude)
├── analyzer.py             # Project analysis (technologies, frameworks)
├── deep_analyzer.py        # Deep code analysis (functions, classes, routes)
├── question_engine.py      # Smart question generation
├── readme_templates.py     # README style templates
├── prompt.py               # Prompt creation utilities
├── docker.py               # Repository cloning
├── main.py                 # Original simple generator
└── pyproject.toml          # Project configuration
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source. Feel free to use and modify.

## 💡 Tips

- **Better results**: Answer the questions thoroughly - the more context you provide, the better the README
- **Model choice**: GPT-4o and Claude-3.5-Sonnet give excellent results; Ollama is free but may be slower
- **Refinement**: Don't hesitate to use the refine option multiple times
- **Debug mode**: Use `--debug` to keep the cloned repo and see what was analyzed
