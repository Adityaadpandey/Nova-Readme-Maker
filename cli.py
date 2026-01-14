#!/usr/bin/env python3
"""
Nova v3.0 - Quick Launcher

AI-powered README generator with deep code scanning.

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
    [cyan]--quick[/]                  Quick mode (minimal questions)
    [cyan]--debug[/]                  Keep debug files and cloned repo
    [cyan]--v2[/]                     Use v2 generator (legacy)

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
        title="[bold white]v3.0[/]",
        subtitle="[dim]Deep Scan • Perfect READMEs[/]",
        border_style="magenta",
        box=DOUBLE,
        padding=(0, 2)
    ))

    console.print(help_text)


def print_help_simple():
    """Print help without Rich (fallback)."""
    print("""
🚀 Nova v3.0 - Deep Scan README Generator

USAGE:
    python run.py <github_repo_url> [options]

OPTIONS:
    --model <name>           Model to use (auto-detects provider)
    --api-key <key>          API key for OpenAI/Claude
    --quick                  Quick mode (minimal questions)
    --debug                  Keep debug files and cloned repo
    --v2                     Use v2 generator (legacy)

MODELS:
    Ollama (local, default):
        llama3.2:latest, llama3.2:3b, mistral, codellama

    OpenAI (requires OPENAI_API_KEY):
        gpt-4o, gpt-4o-mini, gpt-4-turbo, o1-preview

    Claude (requires ANTHROPIC_API_KEY):
        claude-3-5-sonnet-20241022, claude-3-opus-20240229

EXAMPLES:
    # Basic usage with Ollama
    python run.py https://github.com/user/project

    # Using OpenAI
    python run.py https://github.com/user/project --model gpt-4o

    # Quick mode
    python run.py https://github.com/user/project --quick
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

    from questionary import Style as QStyle

    QUESTIONARY_STYLE = QStyle([
        ('qmark', 'fg:#673ab7 bold'),
        ('question', 'bold'),
        ('answer', 'fg:#2196f3 bold'),
        ('pointer', 'fg:#673ab7 bold'),
        ('highlighted', 'fg:#673ab7 bold'),
        ('selected', 'fg:#2196f3'),
    ])

    # Print banner
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
        title="[bold white]v3.0[/]",
        subtitle="[dim]Deep Scan • Perfect READMEs[/]",
        border_style="magenta",
        box=DOUBLE
    ))

    console.print()
    console.print("[bold]Welcome to Nova![/] Let's create a perfect README.\n")

    # Get repository URL
    repo_url = questionary.text(
        "Enter the GitHub repository URL:",
        style=QUESTIONARY_STYLE
    ).ask()

    if not repo_url:
        return None

    # Select mode
    mode = questionary.select(
        "Select generation mode:",
        choices=[
            "Interactive (recommended) - Deep scan with guided questions",
            "Quick - Deep scan, minimal questions",
        ],
        style=QUESTIONARY_STYLE
    ).ask()

    # Select model provider
    provider = questionary.select(
        "Select AI provider:",
        choices=[
            "Ollama (local, free) - Requires Ollama installed",
            "OpenAI - Requires API key",
            "Claude - Requires API key"
        ],
        style=QUESTIONARY_STYLE
    ).ask()

    # Get model based on provider
    if "Ollama" in provider:
        model = questionary.select(
            "Select Ollama model:",
            choices=["llama3.2:latest", "llama3.2:3b", "mistral", "codellama", "Other"],
            style=QUESTIONARY_STYLE
        ).ask()
        if model == "Other":
            model = questionary.text("Enter model name:", default="llama3.2:latest", style=QUESTIONARY_STYLE).ask()
        api_key = None
    elif "OpenAI" in provider:
        model = questionary.select(
            "Select OpenAI model:",
            choices=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1-preview"],
            style=QUESTIONARY_STYLE
        ).ask()
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            api_key = questionary.text("Enter OpenAI API key:", style=QUESTIONARY_STYLE).ask()
    else:
        model = questionary.select(
            "Select Claude model:",
            choices=["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
            style=QUESTIONARY_STYLE
        ).ask()
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            api_key = questionary.text("Enter Anthropic API key:", style=QUESTIONARY_STYLE).ask()

    quick_mode = "Quick" in mode

    return {
        'repo_url': repo_url,
        'model': model,
        'api_key': api_key,
        'quick_mode': quick_mode,
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
        quick_mode = '--quick' in sys.argv
        debug_mode = '--debug' in sys.argv
        use_v2 = '--v2' in sys.argv

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

        config = {
            'repo_url': repo_url,
            'model': model,
            'api_key': api_key,
            'quick_mode': quick_mode,
            'debug_mode': debug_mode,
            'use_v2': use_v2,
        }

    # Run the generator
    if config.get('use_v2'):
        # Use legacy v2 generator
        if RICH_AVAILABLE:
            console.print("[magenta]🚀 Running Nova v2 (legacy)[/]")
        else:
            print("🚀 Running Nova v2 (legacy)")

        try:
            from generator_v2 import ReadmeGeneratorV2
            generator = ReadmeGeneratorV2(
                model=config['model'],
                debug=config.get('debug_mode', False),
                api_key=config.get('api_key'),
                quick_mode=config.get('quick_mode', False)
            )
            success = generator.run(config['repo_url'])
            return 0 if success else 1
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    else:
        # Use new v3 generator with deep scanning
        if RICH_AVAILABLE:
            console.print("[magenta]🚀 Running Nova v3 (Deep Scan)[/]")
        else:
            print("🚀 Running Nova v3 (Deep Scan)")

        try:
            from generator import NovaGenerator
            generator = NovaGenerator(
                model=config['model'],
                api_key=config.get('api_key'),
                debug=config.get('debug_mode', False),
                quick_mode=config.get('quick_mode', False)
            )
            success = generator.generate(config['repo_url'])
            return 0 if success else 1
        except ValueError as e:
            if RICH_AVAILABLE:
                console.print(f"[red]✗ Configuration error:[/] {e}")
                console.print("\n[yellow]💡 Tip:[/] Set API key via environment variable or --api-key flag")
            else:
                print(f"❌ Configuration error: {e}")
                print("\n💡 Tip: Set API key via environment variable or --api-key flag")
            return 1
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"[red]✗ Error:[/] {e}")
            else:
                print(f"❌ Error: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
