#!/usr/bin/env python3
"""
Nova v2.5 - Quick Launcher

AI-powered README generator that creates human-expert quality documentation.

Supports multiple LLM providers:
- Ollama (local, default)
- OpenAI (gpt-4o, gpt-4o-mini, etc.)
- Claude (claude-3-5-sonnet, etc.)
"""

import sys
import os

# Check if rich is installed, if not show simple fallback
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.box import DOUBLE, ROUNDED
    import questionary
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False


def print_help_rich():
    """Print help with Rich styling."""
    help_text = """
[bold magenta]USAGE[/]
    python run.py <github_repo_url> [options]

[bold magenta]OPTIONS[/]
    [cyan]--model <name>[/]           Model to use (auto-detects provider)
    [cyan]--api-key <key>[/]          API key for OpenAI/Claude
    [cyan]--simple[/]                 Simple mode (no interactive questions)
    [cyan]--quick[/]                  Quick mode (minimal questions, smart defaults)
    [cyan]--debug[/]                  Keep debug files and cloned repo
    [cyan]--no-embeddings[/]          Disable vector store (faster)
    [cyan]--embedding-provider X[/]   Embedding provider: local, openai, ollama

[bold magenta]MODELS[/]
    [yellow]Ollama[/] (local, default):
        llama3.2:latest, llama3.2:3b, mistral, codellama

    [yellow]OpenAI[/] (requires OPENAI_API_KEY):
        gpt-4o, gpt-4o-mini, gpt-4-turbo, o1-preview

    [yellow]Claude[/] (requires ANTHROPIC_API_KEY):
        claude-3-5-sonnet-20241022, claude-3-opus-20240229

[bold magenta]EXAMPLES[/]
    [dim]# Basic usage with Ollama[/]
    python run.py https://github.com/user/project

    [dim]# Using OpenAI GPT-4[/]
    python run.py https://github.com/user/project --model gpt-4o

    [dim]# Quick mode with Claude[/]
    python run.py https://github.com/user/project --model claude-3-5-sonnet-20241022 --quick

    [dim]# Simple mode (no questions)[/]
    python run.py https://github.com/user/project --simple
"""

    banner = """
███╗   ██╗ ██████╗ ██╗   ██╗ █████╗
████╗  ██║██╔═══██╗██║   ██║██╔══██╗
██╔██╗ ██║██║   ██║██║   ██║███████║
██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║
██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║
╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝
    """

    console.print(Panel(
        Text(banner, style="bold magenta", justify="center"),
        title="[bold white]v2.5[/]",
        subtitle="[dim]AI-Powered README Generator[/]",
        border_style="magenta",
        box=DOUBLE,
        padding=(0, 2)
    ))

    console.print(help_text)


def print_help_simple():
    """Print help without Rich (fallback)."""
    print("""
🚀 Nova v2.5 - AI-Powered README Generator

USAGE:
    python run.py <github_repo_url> [options]

OPTIONS:
    --model <name>           Model to use (auto-detects provider)
    --api-key <key>          API key for OpenAI/Claude
    --simple                 Simple mode (no interactive questions)
    --quick                  Quick mode (minimal questions, smart defaults)
    --debug                  Keep debug files and cloned repo
    --no-embeddings          Disable vector store (faster but less accurate)
    --embedding-provider X   Embedding provider: local, openai, ollama (default: local)

MODELS:
    Ollama (local, default):
        llama3.2:latest, llama3.2:3b, mistral, codellama, etc.

    OpenAI (requires OPENAI_API_KEY or --api-key):
        gpt-4o, gpt-4o-mini, gpt-4-turbo, o1-preview, o1-mini

    Claude (requires ANTHROPIC_API_KEY or --api-key):
        claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-haiku-20240307

EXAMPLES:
    # Basic usage with Ollama
    python run.py https://github.com/user/project

    # Using OpenAI with embeddings
    export OPENAI_API_KEY=sk-...
    python run.py https://github.com/user/project --model gpt-4o

    # Using Claude
    export ANTHROPIC_API_KEY=sk-ant-...
    python run.py https://github.com/user/project --model claude-3-5-sonnet-20241022

    # Quick mode (less questions)
    python run.py https://github.com/user/project --quick

    # Simple mode (no questions)
    python run.py https://github.com/user/project --simple
""")


def print_help():
    """Print help based on Rich availability."""
    if RICH_AVAILABLE:
        print_help_rich()
    else:
        print_help_simple()


def interactive_setup():
    """Interactive setup when no arguments provided."""
    if not RICH_AVAILABLE:
        return None

    from cli_ui import print_banner, ask_text, ask_select, ask_confirm, print_info

    print_banner()
    console.print()
    console.print("[bold]Welcome to Nova![/] Let's generate a README for your project.\n")

    # Get repository URL
    repo_url = ask_text(
        "Enter the GitHub repository URL:",
        required=True
    )

    if not repo_url:
        return None

    # Select mode
    mode = ask_select(
        "Select generation mode:",
        [
            "Interactive (recommended) - Guided questions for best results",
            "Quick - Fewer questions, smart defaults",
            "Simple - No questions, auto-generate"
        ]
    )

    # Select model provider
    provider = ask_select(
        "Select AI provider:",
        [
            "Ollama (local, free) - Requires Ollama installed",
            "OpenAI - Requires API key",
            "Claude - Requires API key"
        ]
    )

    # Get model based on provider
    if "Ollama" in provider:
        model = ask_select(
            "Select Ollama model:",
            ["llama3.2:latest", "llama3.2:3b", "mistral", "codellama", "Other"]
        )
        if model == "Other":
            model = ask_text("Enter model name:", "llama3.2:latest")
        api_key = None
    elif "OpenAI" in provider:
        model = ask_select(
            "Select OpenAI model:",
            ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1-preview"]
        )
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            api_key = ask_text("Enter OpenAI API key (or set OPENAI_API_KEY):", required=True)
    else:
        model = ask_select(
            "Select Claude model:",
            ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
        )
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            api_key = ask_text("Enter Anthropic API key (or set ANTHROPIC_API_KEY):", required=True)

    # Determine mode flags
    simple_mode = "Simple" in mode
    quick_mode = "Quick" in mode

    # Use embeddings?
    use_embeddings = True
    if not simple_mode:
        use_embeddings = ask_confirm("Enable semantic code search? (better results, slower)", default=True)

    return {
        'repo_url': repo_url,
        'model': model,
        'api_key': api_key,
        'simple_mode': simple_mode,
        'quick_mode': quick_mode,
        'use_embeddings': use_embeddings
    }


def main():
    # Handle help flag or no arguments with interactive mode
    if '--help' in sys.argv or '-h' in sys.argv:
        print_help()
        return 0

    # If no arguments, try interactive setup
    if len(sys.argv) < 2:
        if RICH_AVAILABLE:
            config = interactive_setup()
            if not config:
                print_help()
                return 1
        else:
            print_help()
            return 1
    else:
        # Parse command line arguments
        repo_url = sys.argv[1]

        # Check for flags
        simple_mode = '--simple' in sys.argv
        quick_mode = '--quick' in sys.argv
        debug_mode = '--debug' in sys.argv
        no_embeddings = '--no-embeddings' in sys.argv

        # Get model from args
        model = 'llama3.2:latest'
        for i, arg in enumerate(sys.argv):
            if arg == '--model' and i + 1 < len(sys.argv):
                model = sys.argv[i + 1]

        # Get API key from args
        api_key = None
        for i, arg in enumerate(sys.argv):
            if arg == '--api-key' and i + 1 < len(sys.argv):
                api_key = sys.argv[i + 1]

        # Get embedding provider
        embedding_provider = 'local'
        for i, arg in enumerate(sys.argv):
            if arg == '--embedding-provider' and i + 1 < len(sys.argv):
                embedding_provider = sys.argv[i + 1]

        config = {
            'repo_url': repo_url,
            'model': model,
            'api_key': api_key,
            'simple_mode': simple_mode,
            'quick_mode': quick_mode,
            'debug_mode': debug_mode,
            'use_embeddings': not no_embeddings,
            'embedding_provider': embedding_provider
        }

    # Run the generator
    if config.get('simple_mode'):
        # Use the original simple generator
        if RICH_AVAILABLE:
            console.print("[magenta]🚀 Nova running in SIMPLE mode[/] (no interactive questions)")
        else:
            print("🚀 Nova running in SIMPLE mode (no interactive questions)")

        from main import main as simple_main
        sys.argv = ['main.py', '--repo', config['repo_url'], '--model', config['model']]
        if config.get('debug_mode'):
            sys.argv.append('--debug')
        return simple_main()

    else:
        # Use v2 interactive generator with provider support
        if RICH_AVAILABLE:
            console.print("[magenta]🚀 Nova running in INTERACTIVE mode[/]")
        else:
            print("🚀 Nova running in INTERACTIVE mode")

        try:
            from readme_generator_v2 import ReadmeGeneratorV2
            generator = ReadmeGeneratorV2(
                model=config['model'],
                debug=config.get('debug_mode', False),
                api_key=config.get('api_key'),
                use_embeddings=config.get('use_embeddings', True),
                embedding_provider=config.get('embedding_provider', 'local'),
                quick_mode=config.get('quick_mode', False)
            )
            success = generator.run(config['repo_url'])
            return 0 if success else 1
        except ValueError as e:
            if RICH_AVAILABLE:
                console.print(f"[red]✗ Configuration error:[/] {e}")
                console.print("\n[yellow]💡 Tip:[/] Set API key via environment variable or --api-key flag")
            else:
                print(f"❌ Configuration error: {e}")
                print("\n💡 Tip: Set API key via environment variable or --api-key flag")
            return 1


if __name__ == "__main__":
    sys.exit(main())
