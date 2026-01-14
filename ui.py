"""
CLI UI Module
Beautiful terminal interface using Rich library.
"""

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from rich.live import Live
from rich.layout import Layout
from rich.style import Style
from rich.box import ROUNDED, HEAVY, DOUBLE
from rich.syntax import Syntax
from rich import print as rprint
from typing import List, Dict, Optional, Any, Callable
import questionary
from questionary import Style as QStyle

console = Console()

# Custom questionary style for consistent look
QUESTIONARY_STYLE = QStyle([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#2196f3 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#2196f3'),
    ('separator', 'fg:#cc5454'),
    ('instruction', 'fg:#808080'),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])


class CLITheme:
    """Color theme for CLI."""
    PRIMARY = "#673ab7"
    SECONDARY = "#2196f3"
    SUCCESS = "#4caf50"
    WARNING = "#ff9800"
    ERROR = "#f44336"
    INFO = "#03a9f4"
    MUTED = "#9e9e9e"

    # Styled components
    HEADER_STYLE = Style(color="white", bgcolor="#673ab7", bold=True)
    PHASE_STYLE = Style(color="#673ab7", bold=True)
    SUCCESS_STYLE = Style(color="#4caf50", bold=True)
    WARNING_STYLE = Style(color="#ff9800")
    ERROR_STYLE = Style(color="#f44336", bold=True)
    INFO_STYLE = Style(color="#03a9f4")


def print_banner():
    """Print a beautiful ASCII banner."""
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
        subtitle="[dim]AI-Powered README Generator[/dim]",
        border_style="magenta",
        box=DOUBLE,
        padding=(0, 2)
    ))


def print_header(title: str, subtitle: str = ""):
    """Print a styled header."""
    header_text = Text(title, style="bold white")
    if subtitle:
        header_text.append(f"\n{subtitle}", style="dim white")

    console.print(Panel(
        header_text,
        border_style="magenta",
        box=ROUNDED,
        padding=(1, 2)
    ))


def print_phase(number: int, title: str, description: str = ""):
    """Print a phase header."""
    phase_text = Text()
    phase_text.append(f"PHASE {number}", style="bold magenta")
    phase_text.append(f"  {title}", style="bold white")

    if description:
        phase_text.append(f"\n{description}", style="dim")

    console.print()
    console.print(Panel(
        phase_text,
        border_style="magenta",
        box=ROUNDED,
        padding=(0, 2)
    ))


def print_success(message: str):
    """Print a success message."""
    console.print(f"[bold green]✓[/] {message}")


def print_error(message: str):
    """Print an error message."""
    console.print(f"[bold red]✗[/] {message}")


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"[bold yellow]![/] {message}")


def print_info(message: str):
    """Print an info message."""
    console.print(f"[bold blue]ℹ[/] {message}")


def print_step(message: str, icon: str = "→"):
    """Print a step indicator."""
    console.print(f"[magenta]{icon}[/] {message}")


def create_spinner(message: str) -> Progress:
    """Create a spinner for long operations."""
    return Progress(
        SpinnerColumn(style="magenta"),
        TextColumn("[bold]{task.description}"),
        console=console,
        transient=True
    )


def spinner_task(message: str):
    """Context manager for spinner tasks."""
    return create_spinner(message)


def print_analysis_table(data: Dict[str, Any]):
    """Print analysis results as a beautiful table."""
    table = Table(
        title="[bold magenta]Project Analysis[/]",
        box=ROUNDED,
        border_style="magenta",
        show_header=True,
        header_style="bold white"
    )

    table.add_column("Category", style="cyan", width=20)
    table.add_column("Details", style="white")

    if data.get('project_name'):
        table.add_row("Project", f"[bold]{data['project_name']}[/]")

    if data.get('languages'):
        langs = ", ".join([f"{k} ({v})" for k, v in list(data['languages'].items())[:5]])
        table.add_row("Languages", langs)

    if data.get('frameworks'):
        table.add_row("Frameworks", ", ".join(data['frameworks'][:6]))

    if data.get('technologies'):
        table.add_row("Technologies", ", ".join(data['technologies'][:8]))

    if data.get('has_docker'):
        docker_info = "Yes"
        if data.get('docker_services'):
            docker_info += f" - {', '.join(data['docker_services'][:4])}"
        table.add_row("Docker", docker_info)

    if data.get('databases'):
        table.add_row("Databases", ", ".join(data['databases']))

    if data.get('api_endpoints'):
        table.add_row("API Endpoints", f"{len(data['api_endpoints'])} detected")

    if data.get('complexity_score'):
        score = data['complexity_score']
        difficulty = data.get('setup_difficulty', 'Unknown')
        color = "green" if score < 20 else "yellow" if score < 40 else "red"
        table.add_row("Complexity", f"[{color}]{score} points ({difficulty})[/]")

    if data.get('features'):
        table.add_row("Features", ", ".join(data['features'][:5]))

    console.print()
    console.print(table)


def print_code_insights(insights: Dict[str, Any]):
    """Print code insights in a formatted way."""
    if not any(insights.values()):
        return

    table = Table(
        title="[bold magenta]Code Insights[/]",
        box=ROUNDED,
        border_style="blue",
        show_header=False
    )

    table.add_column("Type", style="cyan", width=20)
    table.add_column("Details", style="white")

    if insights.get('entry_points'):
        table.add_row("Entry Points", ", ".join(insights['entry_points'][:5]))

    if insights.get('main_classes'):
        table.add_row("Main Classes", ", ".join(insights['main_classes'][:5]))

    if insights.get('routes'):
        routes = [f"{r.get('method', 'GET')} {r.get('path', '/')}" for r in insights['routes'][:5]]
        table.add_row("Routes", ", ".join(routes))

    if insights.get('db_models'):
        table.add_row("DB Models", ", ".join(insights['db_models'][:5]))

    if insights.get('external_integrations'):
        table.add_row("Integrations", ", ".join(insights['external_integrations'][:5]))

    if insights.get('cli_commands'):
        table.add_row("CLI Commands", ", ".join(insights['cli_commands'][:5]))

    console.print()
    console.print(table)


def ask_select(question: str, choices: List[str], default: str = None) -> str:
    """Ask a select question with beautiful styling."""
    return questionary.select(
        question,
        choices=choices,
        default=default,
        style=QUESTIONARY_STYLE
    ).ask()


def ask_text(question: str, default: str = "", required: bool = False) -> str:
    """Ask a text input question."""
    while True:
        answer = questionary.text(
            question,
            default=default,
            style=QUESTIONARY_STYLE
        ).ask()

        if answer or not required:
            return answer or ""

        print_warning("This question is required. Please provide an answer.")


def ask_confirm(question: str, default: bool = True) -> bool:
    """Ask a confirmation question."""
    return questionary.confirm(
        question,
        default=default,
        style=QUESTIONARY_STYLE
    ).ask()


def ask_checkbox(question: str, choices: List[str]) -> List[str]:
    """Ask a checkbox question."""
    return questionary.checkbox(
        question,
        choices=choices,
        style=QUESTIONARY_STYLE
    ).ask() or []


def print_readme_preview(content: str, max_lines: int = 40):
    """Print a README preview with syntax highlighting."""
    lines = content.split('\n')
    preview = '\n'.join(lines[:max_lines])

    if len(lines) > max_lines:
        preview += f"\n\n... [{len(lines) - max_lines} more lines] ..."

    console.print()
    console.print(Panel(
        Markdown(preview),
        title="[bold]README Preview[/]",
        border_style="green",
        box=ROUNDED,
        padding=(1, 2)
    ))

    # Stats
    console.print()
    console.print(f"[dim]📊 {len(content):,} characters • {len(lines):,} lines[/]")


def print_review_menu() -> str:
    """Print the review menu and get selection."""
    choices = [
        {"name": "✓ Accept - Save this README", "value": "accept"},
        {"name": "✎ Refine - Request specific changes", "value": "refine"},
        {"name": "↻ Regenerate - Generate fresh draft", "value": "regenerate"},
        {"name": "👁 View Full - See complete README", "value": "view"},
        {"name": "🔍 Check Missing - Find missing info", "value": "check"},
    ]

    console.print()
    result = questionary.select(
        "What would you like to do?",
        choices=[c["name"] for c in choices],
        style=QUESTIONARY_STYLE
    ).ask()

    for c in choices:
        if c["name"] == result:
            return c["value"]
    return "accept"


def print_style_menu(styles: List[Dict], suggested: str) -> str:
    """Print the style selection menu."""
    choices = []
    for style in styles:
        name = style["name"]
        desc = style["description"]
        marker = " ⭐ SUGGESTED" if name.lower() == suggested.lower() else ""
        choices.append(f"{name.upper():15} - {desc}{marker}")

    console.print()
    console.print(Panel(
        "[bold]Choose your README style[/]\n\n"
        "[dim]Different styles for different projects. "
        "The suggested style is based on your project's complexity and type.[/]",
        border_style="magenta",
        box=ROUNDED
    ))

    result = questionary.select(
        "Select a style:",
        choices=choices,
        style=QUESTIONARY_STYLE
    ).ask()

    if result:
        return result.split()[0].lower()
    return suggested


def print_question(question: Any, show_options: bool = True) -> str:
    """Print a question and get the answer."""
    importance_colors = {
        "critical": "red",
        "important": "yellow",
        "optional": "dim"
    }

    color = importance_colors.get(question.importance, "white")
    marker = "●" if question.importance == "critical" else "○" if question.importance == "important" else "·"

    console.print()
    console.print(f"[{color}]{marker}[/] [bold]{question.text}[/]")

    if question.options and show_options:
        return ask_select("", question.options, question.default or question.options[0])
    else:
        required = question.importance == "critical"
        return ask_text("", question.default, required=required)


def print_questionnaire_header(category: str):
    """Print a questionnaire category header."""
    console.print()
    console.print(f"[bold magenta]━━━ {category} ━━━[/]")


def print_completion_banner(output_path: str, stats: Dict[str, Any]):
    """Print the completion banner."""
    completion_text = Text()
    completion_text.append("README GENERATED SUCCESSFULLY!\n\n", style="bold green")
    completion_text.append(f"📄 Saved to: ", style="white")
    completion_text.append(f"{output_path}\n", style="bold cyan")
    completion_text.append(f"📊 Size: {stats.get('chars', 0):,} characters\n", style="dim")
    completion_text.append(f"📝 Lines: {stats.get('lines', 0):,}", style="dim")

    console.print()
    console.print(Panel(
        completion_text,
        title="[bold white]🎉 Complete![/]",
        border_style="green",
        box=DOUBLE,
        padding=(1, 3)
    ))


def print_model_info(provider_name: str, model: str):
    """Print model information."""
    console.print(f"[dim]🤖 Model: {provider_name} ({model})[/]")


def print_repo_info(repo_url: str):
    """Print repository information."""
    console.print(f"[dim]📦 Repository: {repo_url}[/]")


def run_with_spinner(message: str, func: Callable, *args, **kwargs) -> Any:
    """Run a function with a spinner."""
    with create_spinner(message) as progress:
        task = progress.add_task(message, total=None)
        result = func(*args, **kwargs)
        progress.update(task, completed=True)
    return result


def print_understanding_preview(understanding: str, max_chars: int = 600):
    """Print AI understanding preview."""
    preview = understanding[:max_chars]
    if len(understanding) > max_chars:
        preview += "..."

    console.print()
    console.print(Panel(
        preview,
        title="[bold]AI Understanding[/]",
        border_style="blue",
        box=ROUNDED,
        padding=(1, 2)
    ))


def print_missing_info(items: List[str]):
    """Print missing info items."""
    if not items:
        print_success("No obvious missing information detected!")
        return

    console.print()
    console.print("[bold yellow]⚠ Potentially missing:[/]")
    for item in items:
        console.print(f"  [yellow]•[/] {item}")


def clear_screen():
    """Clear the console screen."""
    console.clear()


def print_divider():
    """Print a divider line."""
    console.print("[dim]" + "─" * 60 + "[/]")
