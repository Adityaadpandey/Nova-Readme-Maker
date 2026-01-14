"""
Nova Generator v3
The core engine that brings everything together for perfect README generation.
"""

import os
import shutil
import json
import signal
import sys
from pathlib import Path
from typing import Optional, Dict, List, Any

from scanner import DeepScanner, ProjectContext
from sections import SectionGenerator, create_full_readme_prompt
from repo import clone_repo
from providers import create_provider, detect_provider_from_model

# Try to import Rich UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.markdown import Markdown
    from rich.box import ROUNDED, DOUBLE
    console = Console()
    RICH_UI = True
except ImportError:
    RICH_UI = False
    console = None


# Signal handling for graceful exit
_interrupted = False


def _signal_handler(signum, frame):
    global _interrupted
    _interrupted = True
    print("\n\n⚠ Interrupted! Cleaning up...")
    try:
        if os.path.exists("cloned_repo"):
            shutil.rmtree("cloned_repo")
    except:
        pass
    print("✓ Cleanup complete. Goodbye!")
    sys.exit(0)


signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


class NovaGenerator:
    """
    Nova README Generator v3 - Deep scanning, intelligent context, perfect output.
    """

    def __init__(
        self,
        model: str = "llama3.2:latest",
        api_key: Optional[str] = None,
        debug: bool = False,
        quick_mode: bool = False
    ):
        self.model_string = model
        self.api_key = api_key
        self.debug = debug
        self.quick_mode = quick_mode

        # Setup model provider
        provider_type, model_name = detect_provider_from_model(model)
        self.provider = create_provider(provider_type, model_name, api_key)

        # Will be set during scan
        self.context: Optional[ProjectContext] = None
        self.scanner: Optional[DeepScanner] = None

    def generate(self, repo_url: str) -> bool:
        """Generate a README for the given repository."""

        self._print_banner()

        # Phase 1: Clone repository
        if not self._clone_repo(repo_url):
            return False

        # Phase 2: Deep scan
        self._deep_scan()

        # Phase 3: Show analysis
        self._show_analysis()

        # Phase 4: Ask clarifying questions (unless quick mode)
        if not self.quick_mode:
            self._ask_questions()

        # Phase 5: Generate README
        readme = self._generate_readme()
        if not readme:
            return False

        # Phase 6: Review and refine
        if not self.quick_mode:
            readme = self._review_and_refine(readme)

        # Phase 7: Save
        self._save(readme)

        return True

    def _print_banner(self):
        """Print Nova banner."""
        if RICH_UI:
            banner = """
███╗   ██╗ ██████╗ ██╗   ██╗ █████╗
████╗  ██║██╔═══██╗██║   ██║██╔══██╗
██╔██╗ ██║██║   ██║██║   ██║███████║
██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║
██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║
╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝
            """
            console.print(Panel(
                banner,
                title="[bold white]v3.0[/]",
                subtitle="[dim]Deep Scan • Perfect READMEs[/]",
                border_style="magenta",
                box=DOUBLE
            ))
            console.print(f"[dim]🤖 Model:[/] {self.provider.get_name()}")
            console.print(f"[dim]⚡ Mode:[/] {'Quick' if self.quick_mode else 'Interactive'}")
            console.print()
        else:
            print("\n" + "=" * 60)
            print("  🚀 NOVA v3.0 - Deep Scan README Generator")
            print("=" * 60)
            print(f"  Model: {self.provider.get_name()}")
            print(f"  Mode: {'Quick' if self.quick_mode else 'Interactive'}")
            print("=" * 60 + "\n")

    def _clone_repo(self, repo_url: str) -> bool:
        """Clone the repository."""
        if RICH_UI:
            console.print(Panel("[bold]Phase 1:[/] Cloning Repository", border_style="blue"))

            with Progress(
                SpinnerColumn(style="magenta"),
                TextColumn("[bold]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("Cloning...", total=None)
                success = clone_repo(repo_url)
                progress.update(task, completed=True)

            if success:
                console.print("[green]✓[/] Repository cloned")
            else:
                console.print("[red]✗[/] Failed to clone repository")
            return success
        else:
            print("📦 Cloning repository...")
            return clone_repo(repo_url)

    def _deep_scan(self):
        """Perform deep scan of the codebase."""
        if RICH_UI:
            console.print()
            console.print(Panel("[bold]Phase 2:[/] Deep Code Analysis", border_style="blue"))

            with Progress(
                SpinnerColumn(style="magenta"),
                TextColumn("[bold]{task.description}"),
                BarColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Scanning codebase...", total=100)

                self.scanner = DeepScanner()

                # Simulate progress through different phases
                progress.update(task, advance=20, description="Analyzing structure...")
                self.scanner._scan_directory_structure()
                self.scanner._detect_languages()

                progress.update(task, advance=20, description="Scanning configs...")
                self.scanner._scan_config_files()
                self.scanner._extract_dependencies()
                self.scanner._extract_commands()

                progress.update(task, advance=20, description="Analyzing code...")
                self.scanner._scan_source_files()
                self.scanner._detect_frameworks()
                self.scanner._extract_routes()
                self.scanner._extract_models()

                progress.update(task, advance=15, description="Scanning Docker...")
                self.scanner._scan_docker()

                progress.update(task, advance=10, description="Analyzing tests...")
                self.scanner._scan_tests()

                progress.update(task, advance=10, description="Collecting examples...")
                self.scanner._scan_existing_docs()
                self.scanner._extract_code_examples()

                progress.update(task, advance=5, description="Finalizing...")
                self.scanner._detect_features()
                self.scanner._detect_integrations()
                self.scanner._calculate_complexity()
                self.scanner._collect_key_files()

                self.context = self.scanner.context

            console.print("[green]✓[/] Deep scan complete")
        else:
            print("\n🔍 Performing deep scan...")
            self.scanner = DeepScanner()
            self.context = self.scanner.scan()

    def _show_analysis(self):
        """Show analysis results."""
        ctx = self.context

        if RICH_UI:
            console.print()
            console.print(Panel("[bold]Phase 3:[/] Analysis Results", border_style="blue"))

            # Main info table
            table = Table(title="Project Overview", box=ROUNDED, border_style="cyan")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Project", ctx.name or "Unknown")
            table.add_row("Primary Language", ctx.primary_language)
            table.add_row("Languages", f"{len(ctx.languages)} detected")
            table.add_row("Frameworks", ", ".join(ctx.frameworks[:5]) or "None")
            table.add_row("Dependencies", str(len(ctx.dependencies)))

            # Complexity with color
            color = "green" if ctx.complexity_score < 30 else "yellow" if ctx.complexity_score < 60 else "red"
            table.add_row("Complexity", f"[{color}]{ctx.setup_difficulty} ({ctx.complexity_score} pts)[/]")
            table.add_row("Setup Time", ctx.estimated_setup_time)

            console.print(table)

            # Code analysis table
            if ctx.functions or ctx.classes or ctx.routes:
                code_table = Table(title="Code Analysis", box=ROUNDED, border_style="green")
                code_table.add_column("Type", style="green")
                code_table.add_column("Count", style="white")

                code_table.add_row("Functions", str(len(ctx.functions)))
                code_table.add_row("Classes", str(len(ctx.classes)))
                code_table.add_row("API Routes", str(len(ctx.routes)))
                code_table.add_row("DB Models", str(len(ctx.db_models)))
                code_table.add_row("Tests", str(len(ctx.tests)))

                console.print(code_table)

            # Features
            if ctx.features:
                console.print(f"\n[bold]Features:[/] {', '.join(ctx.features[:10])}")

            # Docker
            if ctx.has_docker:
                services = [s.get('name', 'unknown') for s in ctx.docker_services]
                console.print(f"[bold]Docker:[/] {len(ctx.docker_services)} services ({', '.join(services[:5])})")

            # Databases
            if ctx.databases:
                console.print(f"[bold]Databases:[/] {', '.join(ctx.databases)}")

        else:
            print(f"\n📊 Analysis Results:")
            print(f"   Project: {ctx.name}")
            print(f"   Language: {ctx.primary_language}")
            print(f"   Frameworks: {', '.join(ctx.frameworks[:5])}")
            print(f"   Functions: {len(ctx.functions)}")
            print(f"   Classes: {len(ctx.classes)}")
            print(f"   Routes: {len(ctx.routes)}")
            print(f"   Complexity: {ctx.setup_difficulty}")

    def _ask_questions(self):
        """Ask clarifying questions."""
        if RICH_UI:
            console.print()
            console.print(Panel("[bold]Phase 4:[/] Quick Questions", border_style="blue"))

            # Only ask the most important questions
            questions = []

            if not self.context.description:
                questions.append({
                    'key': 'description',
                    'question': 'What does this project do? (1-2 sentences)',
                    'required': True
                })

            if not self.context.features:
                questions.append({
                    'key': 'features',
                    'question': 'What are the key features? (comma-separated)',
                    'required': False
                })

            if self.context.has_docker and not self.context.docker_services:
                questions.append({
                    'key': 'docker_purpose',
                    'question': 'What does the Docker setup do?',
                    'required': False
                })

            if questions:
                console.print("[dim]Answer a few questions to improve the README:[/]")

                for q in questions:
                    marker = "[red]*[/]" if q['required'] else "[dim](optional)[/]"
                    answer = console.input(f"\n{marker} {q['question']}\n> ")

                    if answer:
                        if q['key'] == 'description':
                            self.context.description = answer
                        elif q['key'] == 'features':
                            self.context.features.extend([f.strip() for f in answer.split(',')])
            else:
                console.print("[green]✓[/] Sufficient information detected, skipping questions")

        else:
            print("\n❓ Quick questions (press Enter to skip):")

            if not self.context.description:
                answer = input("   What does this project do? ").strip()
                if answer:
                    self.context.description = answer

    def _generate_readme(self) -> Optional[str]:
        """Generate the README."""
        if RICH_UI:
            console.print()
            console.print(Panel("[bold]Phase 5:[/] Generating README", border_style="blue"))

            # Create the prompt
            prompt = create_full_readme_prompt(self.context)

            # Show what we're generating
            generator = SectionGenerator(self.context)
            sections = generator.get_sections_to_generate()
            console.print(f"[dim]Generating {len(sections)} sections...[/]")

            with Progress(
                SpinnerColumn(style="magenta"),
                TextColumn("[bold]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("AI is writing your README...", total=None)

                # Determine timeout based on complexity
                timeout = 300 if self.context.complexity_score < 40 else 600

                readme = self.provider.generate(prompt, timeout=timeout)

                progress.update(task, completed=True)

            if readme:
                readme = self._clean_output(readme)
                readme = self._validate_quality(readme)
                console.print("[green]✓[/] README generated!")
                return readme
            else:
                console.print("[red]✗[/] Generation failed")
                return None

        else:
            print("\n🤖 Generating README...")
            prompt = create_full_readme_prompt(self.context)
            readme = self.provider.generate(prompt, timeout=300)

            if readme:
                return self._clean_output(readme)
            return None

    def _validate_quality(self, readme: str) -> str:
        """Validate and fix quality issues."""
        issues = []

        # Check for placeholders
        import re
        placeholders = re.findall(r'\[(?:TODO|Add|Insert|Your|PLACEHOLDER)[^\]]*\]', readme, re.IGNORECASE)
        if placeholders:
            issues.append(f"Found {len(placeholders)} placeholder(s)")

        # Check minimum length
        if len(readme) < 800:
            issues.append("README is too short")

        # Check for required sections
        required = ['#', 'install', 'usage']
        for req in required:
            if req.lower() not in readme.lower():
                issues.append(f"Missing {req} section")

        if issues:
            if RICH_UI:
                console.print(f"[yellow]⚠ Quality issues: {', '.join(issues)}[/]")
                console.print("[dim]Attempting to fix...[/]")

            fix_prompt = f"""Fix these issues in the README:
{', '.join(issues)}

Current README:
{readme}

Return the fixed README with:
1. All placeholders replaced with real content
2. All required sections present
3. Minimum 1000 characters

Return ONLY the fixed README, no explanations."""

            fixed = self.provider.generate(fix_prompt, timeout=180)
            if fixed:
                return self._clean_output(fixed)

        return readme

    def _clean_output(self, output: str) -> str:
        """Clean the generated output."""
        import re

        # Remove markdown code block wrappers
        if output.startswith('```markdown'):
            output = output[11:]
        elif output.startswith('```md'):
            output = output[5:]
        elif output.startswith('```'):
            output = output[3:]

        if output.endswith('```'):
            output = output[:-3]

        # Find the actual README start
        lines = output.split('\n')
        start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('#') and not line.strip().startswith('##'):
                start = i
                break

        if start > 0:
            output = '\n'.join(lines[start:])

        # Remove meta-commentary
        output = re.sub(r'^Here\'s.*?:\s*\n', '', output, flags=re.IGNORECASE)
        output = re.sub(r'^I\'ve created.*?:\s*\n', '', output, flags=re.IGNORECASE)

        return output.strip()

    def _review_and_refine(self, readme: str) -> str:
        """Review and refine the README."""
        if RICH_UI:
            console.print()
            console.print(Panel("[bold]Phase 6:[/] Review & Refine", border_style="blue"))

            # Show preview
            preview_lines = readme.split('\n')[:50]
            preview = '\n'.join(preview_lines)
            if len(readme.split('\n')) > 50:
                preview += f"\n\n... [{len(readme.split(chr(10))) - 50} more lines] ..."

            console.print(Panel(
                Markdown(preview),
                title="[bold]README Preview[/]",
                border_style="green"
            ))

            console.print(f"\n[dim]📊 {len(readme):,} characters • {readme.count(chr(10)):,} lines[/]")

            # Options
            console.print("\n[bold]Options:[/]")
            console.print("  1. [green]Accept[/] - Save this README")
            console.print("  2. [yellow]Refine[/] - Request changes")
            console.print("  3. [cyan]View Full[/] - See complete README")

            choice = console.input("\nChoice (1/2/3) [1]: ").strip() or "1"

            if choice == "1":
                console.print("[green]✓[/] README accepted!")
                return readme

            elif choice == "2":
                feedback = console.input("\nWhat changes would you like?\n> ").strip()
                if feedback:
                    with Progress(
                        SpinnerColumn(style="magenta"),
                        TextColumn("[bold]Refining...[/]"),
                        console=console,
                        transient=True
                    ) as progress:
                        task = progress.add_task("Refining...", total=None)

                        refine_prompt = f"""Refine this README based on the feedback.

CURRENT README:
{readme}

FEEDBACK:
{feedback}

Apply the changes and return the complete updated README."""

                        refined = self.provider.generate(refine_prompt, timeout=180)
                        progress.update(task, completed=True)

                    if refined:
                        return self._clean_output(refined)

                return readme

            elif choice == "3":
                console.print(Panel(readme, title="Full README", border_style="green"))
                console.input("\nPress Enter to continue...")
                return self._review_and_refine(readme)

        return readme

    def _save(self, readme: str):
        """Save the README and cleanup."""
        if RICH_UI:
            console.print()
            console.print(Panel("[bold]Phase 7:[/] Saving", border_style="blue"))

        # Save README
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(readme)

        # Save debug info
        if self.debug:
            debug_data = {
                'name': self.context.name,
                'languages': self.context.languages,
                'frameworks': self.context.frameworks,
                'features': self.context.features,
                'complexity_score': self.context.complexity_score,
                'routes_count': len(self.context.routes),
                'functions_count': len(self.context.functions),
                'classes_count': len(self.context.classes),
            }
            with open("nova_debug.json", "w") as f:
                json.dump(debug_data, f, indent=2)

        # Cleanup
        if not self.debug:
            try:
                shutil.rmtree("cloned_repo")
            except:
                pass

        if RICH_UI:
            console.print(Panel(
                f"[bold green]✓ README.md saved successfully![/]\n\n"
                f"[dim]📊 {len(readme):,} characters • {readme.count(chr(10)):,} lines[/]\n"
                f"[dim]⏱️  Estimated setup time: {self.context.estimated_setup_time}[/]",
                title="[bold]🎉 Complete![/]",
                border_style="green",
                box=DOUBLE
            ))
        else:
            print(f"\n✅ README.md saved!")
            print(f"   Size: {len(readme):,} characters")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Nova v3 - Deep Scan README Generator"
    )
    parser.add_argument('repo', nargs='?', help='GitHub repository URL')
    parser.add_argument('--model', default='llama3.2:latest', help='Model to use')
    parser.add_argument('--api-key', help='API key for OpenAI/Claude')
    parser.add_argument('--quick', action='store_true', help='Quick mode (no questions)')
    parser.add_argument('--debug', action='store_true', help='Keep debug files')

    args = parser.parse_args()

    if not args.repo:
        parser.print_help()
        return 1

    try:
        generator = NovaGenerator(
            model=args.model,
            api_key=args.api_key,
            quick_mode=args.quick,
            debug=args.debug
        )
        success = generator.generate(args.repo)
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
