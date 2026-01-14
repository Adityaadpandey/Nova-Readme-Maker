"""
Expert README Prompt Generator
Creates prompts that produce human-expert quality README documentation.
"""

from typing import List, Tuple

from analyzer import EnhancedProjectAnalyzer


def create_comprehensive_prompt(analyzer: EnhancedProjectAnalyzer, key_files: List[Tuple[str, str]], repo_url: str) -> str:
    """Create an expert-level prompt for README generation that produces human-quality output."""

    project_name = analyzer.project_data.get('name') or repo_url.split('/')[-1].replace('.git', '')
    pd = analyzer.project_data

    # Build organized file content section
    file_contents = _organize_files(key_files)

    # Build comprehensive context
    tech_stack = _build_tech_stack(pd)
    docker_section = _build_docker_info(pd)
    features_section = _build_features(pd)
    api_section = _build_api_info(pd)
    env_section = _build_env_info(pd)
    commands_section = _build_commands(pd)

    # Determine project type and customize prompt accordingly
    project_type = _detect_project_type(pd)
    style_guide = _get_style_guide(project_type, pd)

    prompt = f"""You are a senior developer and technical writer with 15+ years of experience creating world-class documentation. You've written READMEs for projects used by millions of developers. Your documentation is known for being:
- Crystal clear and immediately actionable
- Comprehensive yet not overwhelming
- Professional with a human touch
- Technically accurate down to every command

Your task: Create the PERFECT README.md for this project. It should feel like it was written by someone who deeply understands both the code AND the needs of developers who will use it.

═══════════════════════════════════════════════════════════════════════════════
PROJECT IDENTITY
═══════════════════════════════════════════════════════════════════════════════
Name: {project_name}
Repository: {repo_url}
Type: {project_type}
Description: {pd.get('description', 'Analyze the code to determine')}
Version: {pd.get('version', 'Not specified')}
Author: {pd.get('author', 'Not specified')}
License: {pd.get('license', 'MIT')}

═══════════════════════════════════════════════════════════════════════════════
TECHNOLOGY ANALYSIS
═══════════════════════════════════════════════════════════════════════════════
{tech_stack}

═══════════════════════════════════════════════════════════════════════════════
DETECTED CAPABILITIES
═══════════════════════════════════════════════════════════════════════════════
{features_section}

{docker_section}

{api_section}

{env_section}

═══════════════════════════════════════════════════════════════════════════════
COMMANDS (Extracted from project files)
═══════════════════════════════════════════════════════════════════════════════
{commands_section}

═══════════════════════════════════════════════════════════════════════════════
PROJECT FILES (Analyze these carefully)
═══════════════════════════════════════════════════════════════════════════════
{file_contents}

═══════════════════════════════════════════════════════════════════════════════
README REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════
{style_guide}

═══════════════════════════════════════════════════════════════════════════════
EXPERT WRITING GUIDELINES
═══════════════════════════════════════════════════════════════════════════════

VOICE & TONE:
- Write like a friendly senior developer explaining to a colleague
- Be confident but not arrogant
- Use "you" and "your" to speak directly to the reader
- Avoid corporate jargon and buzzwords
- Be specific, not vague ("handles 10,000 requests/sec" not "high performance")

STRUCTURE:
- Start with a hook that immediately shows what the project does
- Lead with benefits, not features
- Put the most important information first
- Use progressive disclosure - simple overview, then details
- Every section should answer "why should I care?"

CODE EXAMPLES:
- Every code block must be copy-pasteable WITHOUT modification
- Show realistic examples, not toy demos
- Include expected output when helpful
- Use comments to explain non-obvious parts
- Test every command mentally before including it

FORMATTING:
- Use headers strategically to create scannable structure
- Bullet points for lists of 3+ items
- Tables for comparisons or structured data
- Code blocks with proper language hints (```bash, ```python, etc.)
- Emojis sparingly for visual hierarchy (📦 🚀 ⚙️ 📝 🔧 ✨)
- Horizontal rules to separate major sections

WHAT TO AVOID:
- ❌ NO placeholder text like [TODO], [Add here], [Your X here]
- ❌ NO vague descriptions ("a powerful tool for...")
- ❌ NO assumptions not backed by the code
- ❌ NO outdated patterns or deprecated commands
- ❌ NO walls of text without structure
- ❌ NO unnecessary sections that add no value
- ❌ NO generic content that could apply to any project

WHAT TO INCLUDE:
- ✅ Specific, verifiable claims backed by the code
- ✅ Real working commands from the project
- ✅ Clear prerequisites with version numbers
- ✅ Troubleshooting tips for common issues
- ✅ Links to relevant resources
- ✅ Badges that add value (build status, license, etc.)

═══════════════════════════════════════════════════════════════════════════════
REQUIRED SECTIONS (in this order)
═══════════════════════════════════════════════════════════════════════════════

1. **TITLE & BADGES**
   - Project name with optional tagline
   - 2-4 meaningful badges (license, version, build status)
   - One-liner description that captures the essence

2. **HERO SECTION** (What & Why)
   - 2-3 sentence compelling description
   - Key benefits as bullet points
   - Screenshot/demo link placeholder if applicable

3. **TABLE OF CONTENTS** (for READMEs > 100 lines)
   - Linked sections for easy navigation

4. **FEATURES** (if applicable)
   - Specific, verifiable features from the code
   - Grouped by category if many

5. **QUICK START** (Most Important!)
   - Fastest path to "it works!" moment
   - 3-5 commands maximum
   - Show expected output

6. **INSTALLATION** (Detailed)
   - Prerequisites with versions
   - Step-by-step installation
   - Verification that it worked

7. **CONFIGURATION** (if needed)
   - Environment variables explained
   - Configuration file format
   - Example configurations

8. **USAGE** (with examples)
   - Basic usage patterns
   - Common use cases
   - Advanced usage if applicable

9. **API DOCUMENTATION** (if API project)
   - Endpoint list with methods
   - Request/response examples
   - Authentication details

10. **DOCKER** (if applicable)
    - Quick start with Docker
    - Docker Compose setup
    - Production deployment notes

11. **DEVELOPMENT**
    - Setting up dev environment
    - Running tests
    - Contributing guidelines

12. **PROJECT STRUCTURE** (for complex projects)
    - Key directories explained
    - Where to find what

13. **TROUBLESHOOTING** (if complex)
    - Common issues and solutions
    - Debug tips

14. **LICENSE & CREDITS**
    - License type
    - Acknowledgments if any

═══════════════════════════════════════════════════════════════════════════════
GENERATE THE README NOW
═══════════════════════════════════════════════════════════════════════════════

Create a complete, polished README.md that a senior developer would be proud to have on their project. Make it feel like it was written by a human expert, not generated by AI. Every sentence should add value.

Start with the markdown content directly (no preamble). Begin with: # {project_name}
"""

    return prompt


def _organize_files(key_files: List[Tuple[str, str]]) -> str:
    """Organize files by type for better context."""
    config_files = []
    source_files = []
    doc_files = []

    config_exts = {'.json', '.toml', '.yml', '.yaml', '.ini', '.cfg', '.env'}
    doc_exts = {'.md', '.rst', '.txt'}

    for filename, content in key_files:
        lower_name = filename.lower()

        if any(lower_name.endswith(ext) for ext in config_exts) or 'dockerfile' in lower_name:
            config_files.append((filename, content[:2500]))
        elif any(lower_name.endswith(ext) for ext in doc_exts):
            doc_files.append((filename, content[:1500]))
        else:
            source_files.append((filename, content[:2000]))

    result = ""

    if config_files:
        result += "\n[CONFIGURATION FILES]\n"
        for filename, content in config_files[:6]:
            result += f"\n--- {filename} ---\n{content}\n"

    if source_files:
        result += "\n[SOURCE CODE]\n"
        for filename, content in source_files[:5]:
            result += f"\n--- {filename} ---\n{content}\n"

    if doc_files:
        result += "\n[DOCUMENTATION]\n"
        for filename, content in doc_files[:2]:
            result += f"\n--- {filename} ---\n{content}\n"

    return result


def _build_tech_stack(pd: dict) -> str:
    """Build technology stack description."""
    lines = []

    if pd.get('main_language'):
        lines.append(f"Primary Language: {pd['main_language']}")

    if pd.get('languages'):
        langs = ', '.join([f"{k} ({v} files)" for k, v in list(pd['languages'].items())[:5]])
        lines.append(f"All Languages: {langs}")

    if pd.get('frameworks'):
        lines.append(f"Frameworks: {', '.join(pd['frameworks'][:8])}")

    if pd.get('technologies'):
        lines.append(f"Technologies: {', '.join(pd['technologies'][:12])}")

    if pd.get('databases'):
        lines.append(f"Databases: {', '.join(pd['databases'])}")

    if pd.get('architecture_type'):
        lines.append(f"Architecture: {pd['architecture_type']}")

    complexity = pd.get('complexity_score', 0)
    difficulty = pd.get('setup_difficulty', 'Unknown')
    lines.append(f"Complexity: {difficulty} (Score: {complexity})")

    return '\n'.join(lines)


def _build_docker_info(pd: dict) -> str:
    """Build Docker information section."""
    if not pd.get('has_docker'):
        return ""

    lines = ["DOCKER CONFIGURATION:"]

    if pd.get('docker_services'):
        lines.append(f"  Services: {', '.join(pd['docker_services'])}")

    if pd.get('ports'):
        lines.append(f"  Exposed Ports: {', '.join(pd['ports'])}")

    if pd.get('databases'):
        lines.append(f"  Database Containers: {', '.join(pd['databases'])}")

    return '\n'.join(lines)


def _build_features(pd: dict) -> str:
    """Build features section."""
    if not pd.get('features'):
        return "Features: To be determined from code analysis"

    return f"Detected Features:\n  • " + '\n  • '.join(pd['features'][:15])


def _build_api_info(pd: dict) -> str:
    """Build API information section."""
    if not pd.get('api_endpoints'):
        return ""

    endpoints = pd['api_endpoints'][:15]
    lines = [f"API ENDPOINTS ({len(pd['api_endpoints'])} total):"]
    for endpoint in endpoints:
        lines.append(f"  • {endpoint}")

    return '\n'.join(lines)


def _build_env_info(pd: dict) -> str:
    """Build environment variables section."""
    if not pd.get('env_example_vars'):
        return ""

    vars_list = pd['env_example_vars'][:12]
    lines = ["ENVIRONMENT VARIABLES:"]
    for var in vars_list:
        lines.append(f"  • {var}")

    return '\n'.join(lines)


def _build_commands(pd: dict) -> str:
    """Build commands section."""
    lines = []

    if pd.get('install_cmd'):
        lines.append(f"Install: {pd['install_cmd']}")
    else:
        lines.append("Install: [Determine from package manager files]")

    if pd.get('run_cmd'):
        lines.append(f"Run: {pd['run_cmd']}")
    else:
        lines.append("Run: [Determine from scripts or entry points]")

    if pd.get('dev_cmd'):
        lines.append(f"Development: {pd['dev_cmd']}")

    if pd.get('test_cmd'):
        lines.append(f"Test: {pd['test_cmd']}")

    if pd.get('build_cmd'):
        lines.append(f"Build: {pd['build_cmd']}")

    return '\n'.join(lines)


def _detect_project_type(pd: dict) -> str:
    """Detect the type of project for customized prompt."""
    frameworks = [f.lower() for f in pd.get('frameworks', [])]
    features = [f.lower() for f in pd.get('features', [])]
    languages = list(pd.get('languages', {}).keys())

    # API/Backend
    if any(f in frameworks for f in ['fastapi', 'flask', 'express.js', 'django', 'nestjs', 'spring boot']):
        if pd.get('api_endpoints'):
            return "API/Backend Service"
        return "Web Application"

    # CLI Tool
    if 'cli' in features or any(t in str(pd.get('technologies', [])).lower() for t in ['argparse', 'click', 'typer', 'commander']):
        return "CLI Tool"

    # Library/Package
    if pd.get('architecture_type') == 'library' or 'setup.py' in str(pd.get('key_files', [])):
        return "Library/Package"

    # Data Science
    if any(t.lower() in ['tensorflow', 'pytorch', 'pandas', 'numpy', 'jupyter', 'scikit-learn'] for t in pd.get('technologies', [])):
        return "Data Science/ML Project"

    # Frontend
    if any(f in frameworks for f in ['react', 'vue.js', 'angular', 'next.js', 'svelte']):
        return "Frontend Application"

    # Full Stack
    if len(frameworks) > 2:
        return "Full-Stack Application"

    # Default
    if 'Python' in languages:
        return "Python Application"
    elif 'JavaScript' in languages or 'TypeScript' in languages:
        return "JavaScript/Node.js Application"

    return "Software Project"


def _get_style_guide(project_type: str, pd: dict) -> str:
    """Get project-type specific style guide."""
    complexity = pd.get('complexity_score', 0)

    base_guide = f"""
Project Type: {project_type}
Complexity: {pd.get('setup_difficulty', 'Medium')} ({complexity} points)
"""

    if project_type == "API/Backend Service":
        return base_guide + """
FOCUS AREAS for API projects:
- API endpoint documentation with request/response examples
- Authentication and authorization details
- Rate limiting and error handling
- Docker/deployment instructions
- Environment variables for secrets
- Database setup and migrations
"""

    elif project_type == "CLI Tool":
        return base_guide + """
FOCUS AREAS for CLI tools:
- Command reference with all options
- Multiple usage examples
- Installation via package managers
- Shell completion setup if available
- Configuration file format
"""

    elif project_type == "Library/Package":
        return base_guide + """
FOCUS AREAS for libraries:
- Installation via package managers (pip, npm, etc.)
- Quick import and basic usage
- API reference for main functions
- Compatibility information (Python versions, Node versions, etc.)
- TypeScript types if applicable
"""

    elif project_type == "Data Science/ML Project":
        return base_guide + """
FOCUS AREAS for data science projects:
- Data requirements and format
- Model architecture overview
- Training instructions
- Inference/prediction examples
- Results and benchmarks if available
- Jupyter notebook links
"""

    elif "Frontend" in project_type:
        return base_guide + """
FOCUS AREAS for frontend projects:
- Live demo link if available
- Screenshots or GIFs
- Build and deploy instructions
- Browser compatibility
- Component architecture overview
"""

    else:
        if complexity > 40:
            return base_guide + """
FOCUS AREAS for complex projects:
- Comprehensive prerequisites
- Detailed architecture overview
- Step-by-step setup with verification
- Troubleshooting section
- Development workflow
"""
        else:
            return base_guide + """
FOCUS AREAS for standard projects:
- Quick start (3-5 commands)
- Clear installation steps
- Basic usage examples
- Configuration options
"""
