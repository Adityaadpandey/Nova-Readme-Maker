#!/usr/bin/env python3
"""
Nova v2.5 - Simple Mode
Fast README generation without interactive questions.
"""

import argparse
import os
import shutil
import signal
import sys

from analyzer import EnhancedProjectAnalyzer
from docker import clone_repo
from readme import generate_comprehensive_readme

# Try to import Rich for better UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    console = None


# Global flag for graceful shutdown
_interrupted = False


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    global _interrupted
    _interrupted = True

    if RICH_AVAILABLE:
        console.print("\n[yellow]⚠ Interrupted! Cleaning up...[/]")
    else:
        print("\n⚠ Interrupted! Cleaning up...")

    # Cleanup
    try:
        if os.path.exists("cloned_repo"):
            shutil.rmtree("cloned_repo")
    except:
        pass

    if RICH_AVAILABLE:
        console.print("[green]✓ Cleanup complete. Goodbye![/]")
    else:
        print("✓ Cleanup complete. Goodbye!")

    sys.exit(0)


def print_header(repo_url: str, model: str, shallow: bool):
    """Print the header with project info."""
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel.fit(
            "[bold magenta]Nova v2.5[/] - Simple Mode\n"
            "[dim]Fast README generation without questions[/]",
            border_style="magenta"
        ))
        console.print(f"[dim]📦 Repository:[/] {repo_url}")
        console.print(f"[dim]🤖 Model:[/] {model}")
        console.print(f"[dim]🔍 Analysis:[/] {'Shallow' if shallow else 'Deep'}")
        console.print()
        console.print("[dim]Press Ctrl+C at any time to exit gracefully[/]")
        console.print()
    else:
        print("\n🚀 Nova v2.5 - Simple Mode")
        print("=" * 60)
        print(f"📂 Repository: {repo_url}")
        print(f"🧠 Model: {model}")
        print(f"🔍 Analysis: {'Shallow' if shallow else 'Deep'}")
        print("=" * 60)
        print("\nPress Ctrl+C at any time to exit gracefully\n")


def print_analysis_results(analyzer):
    """Print analysis results."""
    pd = analyzer.project_data

    if RICH_AVAILABLE:
        from rich.table import Table

        table = Table(title="[bold]Analysis Results[/]", show_header=False, border_style="blue")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Main Language", pd.get('main_language', 'Unknown'))
        table.add_row("Languages", f"{len(pd.get('languages', {}))} detected")
        table.add_row("Frameworks", ', '.join(pd.get('frameworks', [])[:5]) or 'None')
        table.add_row("Technologies", f"{len(pd.get('technologies', []))} detected")
        table.add_row("Features", f"{len(pd.get('features', []))} detected")
        table.add_row("Docker", 'Yes' if pd.get('has_docker') else 'No')

        complexity = pd.get('complexity_score', 0)
        difficulty = pd.get('setup_difficulty', 'Unknown')
        color = "green" if complexity < 20 else "yellow" if complexity < 40 else "red"
        table.add_row("Complexity", f"[{color}]{difficulty} ({complexity} points)[/]")

        if pd.get('has_docker'):
            table.add_row("Services", f"{len(pd.get('docker_services', []))}")
            table.add_row("Databases", ', '.join(pd.get('databases', [])) or 'None')

        console.print()
        console.print(table)
        console.print()
    else:
        print(f"\n📊 Analysis Results:")
        print(f"   Main Language: {pd.get('main_language', 'Unknown')}")
        print(f"   Languages: {len(pd.get('languages', {}))} detected")
        print(f"   Frameworks: {len(pd.get('frameworks', []))} detected")
        print(f"   Technologies: {len(pd.get('technologies', []))} detected")
        print(f"   Features: {len(pd.get('features', []))} detected")
        print(f"   Docker: {'Yes' if pd.get('has_docker') else 'No'}")
        print(f"   Complexity: {pd.get('setup_difficulty', 'Unknown')} ({pd.get('complexity_score', 0)} points)")

        if pd.get('has_docker'):
            print(f"   Services: {len(pd.get('docker_services', []))}")
            print(f"   Databases: {len(pd.get('databases', []))}")


def print_success(analyzer):
    """Print success message."""
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(
            "[bold green]✓ README.md generated successfully![/]\n\n"
            "[dim]The README includes:[/]\n"
            "  • Comprehensive project overview\n"
            "  • Technology stack analysis\n"
            "  • Step-by-step setup instructions\n"
            "  • Usage examples and commands\n"
            + ("  • Docker deployment guide\n" if analyzer.project_data.get('has_docker') else "")
            + ("  • API documentation\n" if analyzer.project_data.get('api_endpoints') else "")
            + "  • Project structure overview\n"
            "  • Development guidelines\n"
            "  • Contributing instructions",
            title="[bold white]🎉 Complete![/]",
            border_style="green"
        ))
    else:
        print("\n🎉 Success! Generated comprehensive README.md")
        print("\n💡 README includes:")
        print("   ✅ Comprehensive project overview")
        print("   ✅ Technology stack analysis")
        print("   ✅ Step-by-step setup instructions")
        print("   ✅ Usage examples and commands")
        if analyzer.project_data.get('has_docker'):
            print("   ✅ Docker deployment guide")
        if analyzer.project_data.get('api_endpoints'):
            print("   ✅ API documentation")
        print("   ✅ Project structure overview")
        print("   ✅ Development guidelines")
        print("   ✅ Contributing instructions")


def print_error(model: str):
    """Print error message with troubleshooting tips."""
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(
            "[bold red]✗ Failed to generate README[/]\n\n"
            "[dim]Troubleshooting tips:[/]\n"
            f"  • Ensure Ollama is running: [cyan]ollama serve[/]\n"
            f"  • Pull the model: [cyan]ollama pull {model}[/]\n"
            "  • Try a smaller model: [cyan]--model llama3.2:1b[/]\n"
            "  • Use shallow analysis: [cyan]--shallow[/]\n"
            "  • Check if repository is accessible",
            title="[bold white]Error[/]",
            border_style="red"
        ))
    else:
        print("\n❌ Failed to generate README")
        print("\n💡 Troubleshooting tips:")
        print("• Ensure Ollama is running: ollama serve")
        print(f"• Pull the model: ollama pull {model}")
        print("• Try a smaller model: --model llama3.2:1b")
        print("• Use shallow analysis: --shallow")
        print("• Check if repository is accessible")


def main():
    # Register signal handlers for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(
        description="Nova v2.5 - Simple Mode (Fast README generation, no questions)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py --repo https://github.com/user/project
    python main.py --repo https://github.com/user/project --model llama3.2:3b
    python main.py --repo https://github.com/user/project --debug --shallow

Press Ctrl+C at any time to exit gracefully.
        """
    )
    parser.add_argument('--repo', required=True, help='Git repository URL')
    parser.add_argument('--model', default='llama3.2:latest',
                       help='Ollama model to use (default: llama3.2:latest)')
    parser.add_argument('--debug', action='store_true',
                       help='Keep debug files and enable verbose output')
    parser.add_argument('--shallow', action='store_true',
                       help='Perform shallow analysis for faster processing')

    args = parser.parse_args()

    print_header(args.repo, args.model, args.shallow)

    # Clone repository
    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(style="magenta"),
            TextColumn("[bold]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Cloning repository...", total=None)
            success = clone_repo(args.repo)
            progress.update(task, completed=True)

        if not success:
            console.print("[red]✗ Failed to clone repository[/]")
            return 1
        console.print("[green]✓[/] Repository cloned")
    else:
        if not clone_repo(args.repo):
            return 1

    # Check for interrupt
    if _interrupted:
        return 0

    # Initialize enhanced analyzer
    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(style="magenta"),
            TextColumn("[bold]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Analyzing project...", total=None)
            analyzer = EnhancedProjectAnalyzer()
            if not args.shallow:
                analyzer.perform_full_analysis()
            else:
                analyzer.analyze_package_json()
                analyzer.analyze_python_files()
                analyzer.analyze_docker()
            progress.update(task, completed=True)
        console.print("[green]✓[/] Analysis complete")
    else:
        print("\n🔍 Analyzing project...")
        analyzer = EnhancedProjectAnalyzer()
        if not args.shallow:
            analyzer.perform_full_analysis()
        else:
            analyzer.analyze_package_json()
            analyzer.analyze_python_files()
            analyzer.analyze_docker()

    # Check for interrupt
    if _interrupted:
        return 0

    # Print analysis summary
    print_analysis_results(analyzer)

    # Get key files
    key_files = analyzer.get_key_files()

    if RICH_AVAILABLE:
        console.print(f"[dim]📋 Analyzing {len(key_files)} key files[/]")
    else:
        print(f"\n📋 Analyzing {len(key_files)} key files")

    # Check for interrupt
    if _interrupted:
        return 0

    # Generate README
    if RICH_AVAILABLE:
        console.print()
        with Progress(
            SpinnerColumn(style="magenta"),
            TextColumn("[bold]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Generating README (this may take a minute)...", total=None)
            success = generate_comprehensive_readme(analyzer, key_files, args.repo, args.model)
            progress.update(task, completed=True)
    else:
        success = generate_comprehensive_readme(analyzer, key_files, args.repo, args.model)

    if success:
        print_success(analyzer)
    else:
        print_error(args.model)
        return 1

    # Cleanup
    if not args.debug:
        try:
            shutil.rmtree("cloned_repo")
            if RICH_AVAILABLE:
                console.print("[dim]🧹 Cleaned up temporary files[/]")
            else:
                print("🧹 Cleaned up temporary files")
        except:
            pass
    else:
        if RICH_AVAILABLE:
            console.print(f"[dim]🐛 Debug mode: Files preserved in 'cloned_repo' directory[/]")
        else:
            print(f"🐛 Debug mode: Files preserved in 'cloned_repo' directory")
        if os.path.exists("project_analysis.json"):
            if RICH_AVAILABLE:
                console.print(f"[dim]🐛 Project analysis saved to 'project_analysis.json'[/]")
            else:
                print(f"🐛 Project analysis saved to 'project_analysis.json'")

    return 0


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        # Fallback handler
        print("\n\n⚠ Interrupted! Goodbye!")
        try:
            if os.path.exists("cloned_repo"):
                shutil.rmtree("cloned_repo")
        except:
            pass
        exit(0)
