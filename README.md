# 🚀 Nova-Readme-Maker

An intelligent README generator that creates professional documentation for GitHub repositories by analyzing your code and leveraging AI models.

## 📋 Description

Nova-Readme-Maker automates the creation of comprehensive README files for your GitHub projects. It performs deep repository analysis—detecting languages, frameworks, technologies, and project complexity—then uses AI models to generate well-structured, professional documentation tailored to your project.

**Why Nova-Readme-Maker?**
- ⚡ **Fast generation** - Shallow clone and optimized analysis
- 🧠 **Multiple AI models** - OpenAI, Anthropic Claude, and local Ollama support
- 🔍 **Deep code understanding** - Analyzes actual code logic and project structure
- 📊 **Complexity-aware** - Adjusts generation strategy based on project complexity
- 🛠️ **Flexible analysis modes** - Full deep analysis or fast shallow mode
- 🐳 **Docker-aware** - Detects containerization and microservices

## 🛠️ Installation

### Prerequisites
- Python 3.12 or higher
- Git
- One of the following AI providers:
  - **Ollama** (local, no API key needed) - [Install Ollama](https://ollama.ai)
  - **OpenAI** API key
  - **Anthropic** API key

### Setup

```bash
# Clone the repository
git clone https://github.com/Adityaadpandey/Nova-Readme-Maker.git
cd Nova-Readme-Maker

# Install dependencies
pip install -e .
```

### Dependencies
- `gitpython>=3.1.44` - Repository cloning
- `ollama>=0.5.1` - AI model inference
- `pyyaml>=6.0` - Configuration management

## ⚡ Quick Start

### Basic Usage with Ollama (Recommended)

```bash
python main.py --repo https://github.com/user/project
```

This will:
1. Clone your repository (shallow, for speed)
2. Analyze the project structure, languages, and frameworks
3. Generate a comprehensive README using Ollama
4. Save output to `README.md`

### Using OpenAI GPT-4

```bash
export OPENAI_API_KEY=sk-your-key-here
python run.py https://github.com/user/project --model gpt-4o
```

### Using Claude

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
python run.py https://github.com/user/project --model claude-opus
```

## 📝 Commands

### Main Generation Script

```bash
python main.py --repo <URL> [OPTIONS]
```

### Interactive Generator

```bash
python run.py <URL> [OPTIONS]
```

### Advanced Generator with Q&A

```bash
python readme_generator_v3.py --repo <URL> [OPTIONS]
```

## 🎛️ Options

| Option | Description | Example |
|--------|-------------|---------|
| `--repo` | **Required.** GitHub repository URL | `--repo https://github.com/user/project` |
| `--model` | AI model to use (default: `llama3.2:latest`) | `--model gpt-4o` or `--model llama3.2:3b` |
| `--debug` | Keep debug files and enable verbose output | `--debug` |
| `--shallow` | Perform shallow analysis for faster processing | `--shallow` |

## 📚 Usage Examples

### Example 1: Generate README for a Python Project

```bash
python main.py --repo https://github.com/torvalds/linux
```

### Example 2: Use Custom Ollama Model (3B Lightweight)

```bash
python main.py --repo https://github.com/facebook/react --model llama3.2:3b
```

### Example 3: Fast Generation with Shallow Analysis

```bash
python main.py --repo https://github.com/django/django --shallow
```

### Example 4: Debug Mode with Verbose Output

```bash
python main.py --repo https://github.com/kubernetes/kubernetes --debug
```

### Example 5: Interactive README Generation with Questions

```bash
python run.py https://github.com/user/project
# Answers smart questions about your project before generating
```

## ⚙️ Configuration

### Environment Variables

```bash
# OpenAI Configuration
export OPENAI_API_KEY=sk-your-key

# Anthropic Configuration  
export ANTHROPIC_API_KEY=sk-ant-your-key

# Ollama Configuration (optional)
export OLLAMA_MODEL=llama3.2:latest
export OLLAMA_TIMEOUT=1600
```

### Ollama Model Selection

Available lightweight models:
- `llama3.2:latest` - Full model (4B+)
- `llama3.2:3b` - Lightweight (3B)
- `mistral` - Fast and efficient
- `neural-chat` - Optimized for documentation

Pull models with:
```bash
ollama pull llama3.2:latest
ollama pull llama3.2:3b
ollama pull mistral
```

## 🔧 Features

### Deep Project Analysis
- **Language Detection**: Identifies primary and secondary programming languages
- **Framework Recognition**: Detects frameworks (React, Django, Spring, etc.)
- **Technology Stack**: Identifies databases, tools, and technologies
- **Complexity Scoring**: Assesses project setup difficulty (0-100 points)
- **Docker Detection**: Identifies containerization and microservices

### Multi-Model Support
- **Local**: Ollama (recommended for privacy/offline)
- **Cloud**: OpenAI GPT-4, Claude 3+
- **Flexible**: Switch models per generation

### Intelligent Generation
- **Adaptive Timeouts**: Scales processing time based on project complexity
- **Shallow Clone**: Git depth=1 for 10x faster repository acquisition
- **Debug Mode**: Preserves intermediate analysis files
- **Context-Aware**: Customizes documentation based on project type

## ⚠️ Troubleshooting

### Issue: "Ollama not found" or "Connection refused"

**Solution**: Ensure Ollama is installed and running:
```bash
# Install Ollama from https://ollama.ai
# Start Ollama (it runs as a service)
ollama serve

# In another terminal, verify it's working
ollama list
```

### Issue: "No API key provided for OpenAI/Anthropic"

**Solution**: Set your environment variables:
```bash
# For OpenAI
export OPENAI_API_KEY=sk-your-actual-key

# For Anthropic
export ANTHROPIC_API_KEY=sk-ant-your-actual-key

# Verify they're set
echo $OPENAI_API_KEY
```

### Issue: "Model not found" with Ollama

**Solution**: Download the model first:
```bash
ollama pull llama3.2:latest
# Wait for download to complete
ollama list  # Verify it's installed
```

### Issue: Generation timeout or slow performance

**Solution**: Use a faster model or shallow analysis:
```bash
# Lightweight model
python main.py --repo <URL> --model llama3.2:3b

# Shallow analysis
python main.py --repo <URL> --shallow

# Both
python main.py --repo <URL> --model llama3.2:3b --shallow
```

## 🏗️ How It Works

```
GitHub URL (CLI Input)
    ↓
Repository Clone (git depth=1)
    ↓
Project Analysis
├─ Languages & Frameworks
├─ Technologies & Databases
├─ Setup Complexity Assessment
└─ Extract Key Files
    ↓
AI Model Processing
├─ OpenAI/Claude (API)
└─ Ollama (Local)
    ↓
Markdown Generation & Cleanup
    ↓
README.md Output
```

## 🎯 Project Complexity Levels

| Level | Complexity Score | Analysis Timeout | Use Case |
|-------|------------------|------------------|----------|
| Simple | 0-25 | 800s | Single-file projects |
| Moderate | 26-50 | 1000s | Standard applications |
| Complex | 51-75 | 1200s | Multi-service systems |
| Expert | 75-100 | 1600s | Enterprise projects |

## 📦 Project Structure

```
Nova-Readme-Maker/
├── main.py                      # Main entry point (simple mode)
├── run.py                       # Interactive mode entry
├── readme_generator_v3.py       # Advanced generator with Q&A
├── analyzer.py                  # EnhancedProjectAnalyzer
├── readme.py                    # README generation logic
├── prompt.py                    # Prompt creation
├── clone-repo.py               # Git repository cloning
├── pyproject.toml              # Project metadata
└── README.md                   # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make your changes and test thoroughly
4. Commit with clear messages (`git commit -m "Add feature: description"`)
5. Push to your fork (`git push origin feature/improvement`)
6. Open a Pull Request

### Development Tips

- Run with `--debug` flag during development
- Test with repositories of varying complexity
- Verify output against different model providers
- Check markdown formatting in GitHub's preview

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Made with ❤️ by [Aditya Pandey](https://github.com/Adityaadpandey)**

For issues, questions, or feature requests, please [open an issue](https://github.com/Adityaadpandey/Nova-Readme-Maker/issues) on GitHub.