#!/usr/bin/env python3
"""
Nova v2.5
AI-powered README generator with deep code understanding.

Features:
- Multi-pass analysis (analyze → ask → understand → generate → refine)
- Interactive question-answer flow with beautiful CLI
- Deep code understanding with vector store
- Template-based generation
- Iterative refinement
- Missing info detection
- Multiple LLM providers (Ollama, OpenAI, Claude)
- Semantic code search via embeddings
- Quality validation for perfect READMEs
"""

import argparse
import os
import shutil
import json
import signal
import sys
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict

# Global flag for graceful shutdown
_interrupted = False


def _signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    global _interrupted
    _interrupted = True

    print("\n\n⚠ Interrupted! Cleaning up...")

    # Cleanup
    try:
        if os.path.exists("cloned_repo"):
            shutil.rmtree("cloned_repo")
    except:
        pass

    print("✓ Cleanup complete. Goodbye!")
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

# Local imports
from analyzer import EnhancedProjectAnalyzer
from analyzer_v2 import DeepCodeAnalyzer
from questions import QuestionEngine, Question
from templates import TemplateManager, get_style_instructions
from repo import clone_repo
from providers import ModelProvider, create_provider, detect_provider_from_model
from vectors import VectorStore, CodeChunker, create_embedding_provider

# Try to import Rich UI, fallback to simple mode
try:
    from ui import (
        console, print_banner, print_phase, print_success, print_error,
        print_warning, print_info, print_step, print_analysis_table,
        print_code_insights, print_style_menu, print_readme_preview,
        print_review_menu, print_completion_banner, print_model_info,
        print_repo_info, print_understanding_preview, print_missing_info,
        ask_text, ask_confirm, ask_select, print_questionnaire_header,
        print_question, print_divider, create_spinner
    )
    RICH_UI = True
except ImportError:
    RICH_UI = False


@dataclass
class GenerationContext:
    """Complete context for README generation."""
    # Repository info
    repo_url: str = ""
    project_name: str = ""

    # Auto-detected (from EnhancedProjectAnalyzer)
    languages: Dict[str, int] = field(default_factory=dict)
    frameworks: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    has_docker: bool = False
    docker_services: List[str] = field(default_factory=list)
    api_endpoints: List[str] = field(default_factory=list)
    env_vars: List[str] = field(default_factory=list)
    complexity_score: int = 0
    setup_difficulty: str = "Unknown"

    # Commands
    install_cmd: str = ""
    run_cmd: str = ""
    dev_cmd: str = ""
    test_cmd: str = ""
    build_cmd: str = ""

    # Deep analysis (from DeepCodeAnalyzer)
    entry_points: List[str] = field(default_factory=list)
    main_classes: List[str] = field(default_factory=list)
    routes: List[Dict] = field(default_factory=list)
    db_models: List[str] = field(default_factory=list)
    external_integrations: List[str] = field(default_factory=list)
    cli_commands: List[str] = field(default_factory=list)

    # User-provided answers
    user_answers: Dict[str, str] = field(default_factory=dict)

    # LLM understanding
    code_understanding: str = ""

    # Generation settings
    readme_style: str = "detailed"

    # File contents
    key_files: List[tuple] = field(default_factory=list)


class ReadmeGeneratorV2:
    """Enhanced README generator with full interactive flow."""

    def __init__(self, model: str = "llama3.2:latest", debug: bool = False,
                 api_key: Optional[str] = None, use_embeddings: bool = True,
                 embedding_provider: str = "local", quick_mode: bool = False):
        self.model_string = model
        self.debug = debug
        self.api_key = api_key
        self.context = GenerationContext()
        self.analyzer: Optional[EnhancedProjectAnalyzer] = None
        self.deep_analyzer: Optional[DeepCodeAnalyzer] = None
        self.vector_store: Optional[VectorStore] = None
        self.use_embeddings = use_embeddings
        self.embedding_provider_type = embedding_provider
        self.quick_mode = quick_mode

        # Setup model provider (auto-detect from model string)
        provider_type, model_name = detect_provider_from_model(model)
        self.provider = create_provider(provider_type, model_name, api_key)

        # Question engine uses the same provider
        self.question_engine = QuestionEngine(self.provider)

    def run(self, repo_url: str) -> bool:
        """Run the complete generation pipeline."""
        self.context.repo_url = repo_url
        self.context.project_name = repo_url.split('/')[-1].replace('.git', '')

        self._print_header()

        # Phase 1: Clone & Initial Analysis
        if not self._phase1_clone_and_analyze():
            return False

        # Phase 2: Deep Code Understanding
        self._phase2_deep_analysis()

        # Phase 3: Present Findings
        self._phase3_present_findings()

        # Phase 4: Interactive Q&A (skip in quick mode for non-critical questions)
        self._phase4_ask_questions()

        # Phase 5: LLM Code Understanding
        self._phase5_llm_understanding()

        # Phase 6: Choose Style
        self._phase6_choose_style()

        # Phase 7: Generate Draft
        draft = self._phase7_generate()
        if not draft:
            return False

        # Phase 8: Review & Refine
        final = self._phase8_review_refine(draft)

        # Phase 9: Save & Cleanup
        self._phase9_save(final)

        return True

    def _print_header(self):
        """Print the welcome header."""
        if RICH_UI:
            print_banner()
            console.print()
            print_repo_info(self.context.repo_url)
            print_model_info(self.provider.get_name(), self.model_string)
            console.print()
            if self.quick_mode:
                print_info("Quick mode enabled - using smart defaults")
        else:
            print("\n" + "═" * 70)
            print("  🚀 NOVA v2.5 - AI-Powered README Generator")
            print("═" * 70)
            print(f"\n  Repository: {self.context.repo_url}")
            print(f"  Model: {self.provider.get_name()}")
            print("\n  Nova will guide you through creating the perfect README.")
            print("═" * 70)

    def _phase1_clone_and_analyze(self) -> bool:
        """Phase 1: Clone repository and perform initial analysis."""
        if RICH_UI:
            print_phase(1, "Repository Analysis", "Cloning and analyzing project structure")
        else:
            print("\n┌─────────────────────────────────────────────────────────────────┐")
            print("│  PHASE 1: Cloning & Analyzing Repository                        │")
            print("└─────────────────────────────────────────────────────────────────┘")

        # Clone
        if RICH_UI:
            with create_spinner("Cloning repository...") as progress:
                task = progress.add_task("Cloning repository...", total=None)
                success = clone_repo(self.context.repo_url)
                progress.update(task, completed=True)
            if not success:
                print_error("Failed to clone repository")
                return False
        else:
            if not clone_repo(self.context.repo_url):
                return False

        # Analyze with EnhancedProjectAnalyzer
        if RICH_UI:
            with create_spinner("Analyzing project structure...") as progress:
                task = progress.add_task("Analyzing project structure...", total=None)
                self.analyzer = EnhancedProjectAnalyzer()
                self.analyzer.perform_full_analysis()
                progress.update(task, completed=True)
        else:
            print("\n🔍 Running comprehensive project analysis...")
            self.analyzer = EnhancedProjectAnalyzer()
            self.analyzer.perform_full_analysis()

        # Transfer data to context
        pd = self.analyzer.project_data
        self.context.languages = pd.get('languages', {})
        self.context.frameworks = pd.get('frameworks', [])
        self.context.technologies = pd.get('technologies', [])
        self.context.databases = pd.get('databases', [])
        self.context.features = pd.get('features', [])
        self.context.has_docker = pd.get('has_docker', False)
        self.context.docker_services = pd.get('docker_services', [])
        self.context.api_endpoints = pd.get('api_endpoints', [])
        self.context.env_vars = pd.get('env_example_vars', [])
        self.context.complexity_score = pd.get('complexity_score', 0)
        self.context.setup_difficulty = pd.get('setup_difficulty', 'Unknown')
        self.context.install_cmd = pd.get('install_cmd', '')
        self.context.run_cmd = pd.get('run_cmd', '')
        self.context.dev_cmd = pd.get('dev_cmd', '')
        self.context.test_cmd = pd.get('test_cmd', '')
        self.context.build_cmd = pd.get('build_cmd', '')
        self.context.key_files = self.analyzer.get_key_files()

        if RICH_UI:
            print_success("Initial analysis complete!")
        else:
            print("✅ Initial analysis complete!")
        return True

    def _phase2_deep_analysis(self):
        """Phase 2: Deep code analysis."""
        if RICH_UI:
            print_phase(2, "Deep Code Analysis", "Examining code patterns and structure")
        else:
            print("\n┌─────────────────────────────────────────────────────────────────┐")
            print("│  PHASE 2: Deep Code Analysis                                     │")
            print("└─────────────────────────────────────────────────────────────────┘")

        if RICH_UI:
            with create_spinner("Analyzing code structure...") as progress:
                task = progress.add_task("Analyzing code structure...", total=None)
                self.deep_analyzer = DeepCodeAnalyzer()
                insights = self.deep_analyzer.analyze()
                progress.update(task, completed=True)
        else:
            print("\n🔬 Analyzing code structure and patterns...")
            self.deep_analyzer = DeepCodeAnalyzer()
            insights = self.deep_analyzer.analyze()

        # Transfer insights to context
        self.context.entry_points = insights.main_entry_points
        self.context.main_classes = [f"{c.name}: {c.docstring[:50]}" for c in insights.classes[:10]]
        self.context.routes = insights.routes
        self.context.db_models = insights.database_models
        self.context.external_integrations = list(set(insights.external_calls))
        self.context.cli_commands = insights.cli_commands

        if RICH_UI:
            print_success("Deep analysis complete!")
        else:
            print("✅ Deep analysis complete!")

        # Build vector store for semantic search
        if self.use_embeddings:
            self._build_vector_store()

        # Show code insights
        if RICH_UI:
            print_code_insights({
                'entry_points': self.context.entry_points,
                'main_classes': self.context.main_classes,
                'routes': self.context.routes,
                'db_models': self.context.db_models,
                'external_integrations': self.context.external_integrations,
                'cli_commands': self.context.cli_commands
            })
        else:
            summary = self.deep_analyzer.get_summary()
            if summary:
                print("\n📊 Code Insights:")
                for line in summary.split('\n')[:15]:
                    print(f"   {line}")

    def _build_vector_store(self):
        """Build vector store for semantic code search."""
        if RICH_UI:
            with create_spinner("Building semantic search index...") as progress:
                task = progress.add_task("Building semantic search index...", total=None)
                self._do_build_vector_store()
                progress.update(task, completed=True)
        else:
            print("\n🔢 Building vector store for semantic search...")
            self._do_build_vector_store()

    def _do_build_vector_store(self):
        """Actually build the vector store."""
        try:
            # Create embedding provider
            if self.embedding_provider_type == "openai" and self.api_key:
                embedding_provider = create_embedding_provider("openai", api_key=self.api_key)
            elif self.embedding_provider_type == "ollama":
                embedding_provider = create_embedding_provider("ollama")
            else:
                embedding_provider = create_embedding_provider("local")

            # Chunk the codebase
            chunker = CodeChunker()
            chunks = chunker.chunk_repository()

            # Build vector store
            self.vector_store = VectorStore(embedding_provider)
            self.vector_store.add_chunks(chunks)
            self.vector_store.build_embeddings()

            if RICH_UI:
                print_success(f"Vector store ready ({len(chunks)} code chunks)")
            else:
                print(f"✅ Vector store ready! ({len(chunks)} chunks)")

        except ImportError as e:
            if RICH_UI:
                print_warning(f"Could not build vector store: {e}")
            else:
                print(f"⚠️  Could not build vector store: {e}")
            self.vector_store = None
        except Exception as e:
            if RICH_UI:
                print_warning(f"Vector store error: {e}")
            else:
                print(f"⚠️  Vector store error: {e}")
            self.vector_store = None

    def _phase3_present_findings(self):
        """Phase 3: Present analysis findings to user."""
        if RICH_UI:
            print_phase(3, "Analysis Results", "Review detected project information")
            print_analysis_table({
                'project_name': self.context.project_name,
                'languages': self.context.languages,
                'frameworks': self.context.frameworks,
                'technologies': self.context.technologies,
                'has_docker': self.context.has_docker,
                'docker_services': self.context.docker_services,
                'databases': self.context.databases,
                'api_endpoints': self.context.api_endpoints,
                'complexity_score': self.context.complexity_score,
                'setup_difficulty': self.context.setup_difficulty,
                'features': self.context.features
            })
        else:
            print("\n┌─────────────────────────────────────────────────────────────────┐")
            print("│  PHASE 3: Analysis Results                                       │")
            print("└─────────────────────────────────────────────────────────────────┘")

            print(f"\n🏷️  Project: {self.context.project_name}")
            print(f"📈 Complexity: {self.context.complexity_score} points ({self.context.setup_difficulty})")

            if self.context.languages:
                print(f"\n💻 Languages:")
                for lang, count in list(self.context.languages.items())[:5]:
                    print(f"   • {lang}: {count} files")

            if self.context.frameworks:
                print(f"\n🛠️  Frameworks: {', '.join(self.context.frameworks[:8])}")

        # Ask for confirmation/corrections (skip in quick mode)
        if self.quick_mode:
            if RICH_UI:
                print_info("Quick mode: Using detected analysis")
            return

        if RICH_UI:
            print_divider()
            correct = ask_confirm("Is this analysis correct?", default=True)
            if not correct:
                self._correct_analysis()
        else:
            print("\n" + "-" * 50)
            print("❓ Is this analysis correct?")
            response = input("   (yes/no/edit): ").strip().lower()

            if response in ['no', 'n', 'edit', 'e']:
                self._correct_analysis()

    def _correct_analysis(self):
        """Allow user to correct the analysis."""
        if RICH_UI:
            console.print("\n[bold]Let's correct the analysis:[/]")

            # Correct technologies
            console.print(f"\n[dim]Current technologies: {', '.join(self.context.technologies[:15])}[/]")
            remove = ask_text("Technologies to REMOVE (comma-separated, or Enter to skip):")
            if remove:
                to_remove = [t.strip().lower() for t in remove.split(',')]
                self.context.technologies = [t for t in self.context.technologies
                                             if t.lower() not in to_remove]

            add = ask_text("Technologies to ADD (comma-separated, or Enter to skip):")
            if add:
                self.context.technologies.extend([t.strip() for t in add.split(',')])

            # Correct frameworks
            console.print(f"\n[dim]Current frameworks: {', '.join(self.context.frameworks)}[/]")
            remove = ask_text("Frameworks to REMOVE (comma-separated, or Enter to skip):")
            if remove:
                to_remove = [f.strip().lower() for f in remove.split(',')]
                self.context.frameworks = [f for f in self.context.frameworks
                                           if f.lower() not in to_remove]

            add = ask_text("Frameworks to ADD (comma-separated, or Enter to skip):")
            if add:
                self.context.frameworks.extend([f.strip() for f in add.split(',')])

            print_success("Analysis updated!")
        else:
            print("\n📝 Let's correct the analysis:")
            # ... (fallback code same as original)

    def _phase4_ask_questions(self):
        """Phase 4: Ask intelligent questions."""
        if RICH_UI:
            print_phase(4, "Project Information", "Tell us about your project")
        else:
            print("\n┌─────────────────────────────────────────────────────────────────┐")
            print("│  PHASE 4: Tell Me About Your Project                            │")
            print("└─────────────────────────────────────────────────────────────────┘")

        # Prepare context for question generation
        q_context = {
            'project_name': self.context.project_name,
            'languages': self.context.languages,
            'frameworks': self.context.frameworks,
            'has_docker': self.context.has_docker,
            'docker_services': self.context.docker_services,
            'api_endpoints': self.context.api_endpoints,
            'databases': self.context.databases,
            'env_vars': self.context.env_vars,
            'complexity_score': self.context.complexity_score,
            'features': self.context.features,
            'cli_commands': self.context.cli_commands,
            'test_cmd': self.context.test_cmd
        }

        # Generate smart questions
        questions = self.question_engine.generate_smart_questions(q_context)

        # In quick mode, only ask critical questions
        if self.quick_mode:
            questions = [q for q in questions if q.importance == "critical"]
            if RICH_UI:
                print_info(f"Quick mode: Asking {len(questions)} essential questions")

        # Ask questions interactively
        if RICH_UI:
            self.context.user_answers = self._ask_questions_rich(questions)
        else:
            self.context.user_answers = self.question_engine.ask_questions_interactive(questions)

        if RICH_UI:
            print_success("Thank you! I have a much better understanding now.")
        else:
            print("\n✅ Thank you! I have a much better understanding now.")

    def _ask_questions_rich(self, questions: List[Question]) -> Dict[str, str]:
        """Ask questions with Rich UI."""
        answers = {}

        console.print()
        console.print("[dim]Answer these questions to help create a better README.[/]")
        console.print("[dim]Press Enter to skip optional questions.[/]")

        # Group by category
        categories = {}
        for q in questions:
            if q.category not in categories:
                categories[q.category] = []
            categories[q.category].append(q)

        for category, cat_questions in categories.items():
            print_questionnaire_header(category)

            for q in cat_questions:
                answer = print_question(q)

                if answer or q.importance == "critical":
                    if not answer and q.importance == "critical":
                        # Re-ask critical questions
                        while not answer:
                            print_warning("This question is required.")
                            answer = print_question(q)
                    answers[q.id] = answer
                elif q.default:
                    answers[q.id] = q.default

        return answers

    def _phase5_llm_understanding(self):
        """Phase 5: Use LLM to understand the code deeply."""
        if RICH_UI:
            print_phase(5, "AI Code Understanding", "Deep analysis of your codebase")
        else:
            print("\n┌─────────────────────────────────────────────────────────────────┐")
            print("│  PHASE 5: AI Code Understanding                                  │")
            print("└─────────────────────────────────────────────────────────────────┘")

        # Prepare code samples
        code_samples = self._prepare_code_samples()

        if not code_samples:
            if RICH_UI:
                print_warning("No significant source code found.")
            else:
                print("⚠️  No significant source code found.")
            return

        # Create understanding prompt
        prompt = self._create_understanding_prompt(code_samples)

        # Get understanding
        if RICH_UI:
            with create_spinner("AI is analyzing your codebase...") as progress:
                task = progress.add_task("AI is analyzing your codebase...", total=None)
                understanding = self._call_model(prompt, timeout=180)
                progress.update(task, completed=True)
        else:
            print("\n🤖 Asking AI to analyze and understand the codebase...")
            understanding = self._call_model(prompt, timeout=180)

        if understanding:
            self.context.code_understanding = understanding
            if RICH_UI:
                print_success("Code understanding complete!")
                print_understanding_preview(understanding)
            else:
                print("✅ Code understanding complete!")
                print("\n📝 AI's Understanding:\n" + "-" * 40)
                preview = understanding[:600] + "..." if len(understanding) > 600 else understanding
                print(preview)
                print("-" * 40)

            # Ask for corrections (skip in quick mode)
            if not self.quick_mode:
                if RICH_UI:
                    correct = ask_confirm("Is this understanding accurate?", default=True)
                    if not correct:
                        correction = ask_text("Please provide corrections:")
                        if correction:
                            self.context.code_understanding += f"\n\n[User Correction]: {correction}"
                else:
                    correct = input("\n❓ Is this understanding accurate? (yes/no): ").strip().lower()
                    if correct in ['no', 'n']:
                        correction = input("Please provide corrections: ").strip()
                        if correction:
                            self.context.code_understanding += f"\n\n[User Correction]: {correction}"
        else:
            if RICH_UI:
                print_warning("Could not get AI understanding. Continuing with detected info.")
            else:
                print("⚠️  Could not get AI understanding. Continuing with detected info.")

    def _prepare_code_samples(self) -> str:
        """Prepare code samples for LLM analysis using vector store if available."""
        # If we have a vector store, use semantic search to find relevant code
        if self.vector_store and self.vector_store.chunks:
            semantic_samples = self._get_semantic_code_samples()
            if semantic_samples:
                return semantic_samples

        # Fallback to traditional file-based sampling
        samples = []
        source_ext = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs'}
        priority_names = ['main', 'app', 'index', 'server', 'api', 'routes', 'models']

        for filename, content in self.context.key_files:
            if any(filename.endswith(ext) for ext in source_ext):
                is_priority = any(p in filename.lower() for p in priority_names)
                max_len = 2500 if is_priority else 1500

                samples.append(f"=== {filename} ===\n{content[:max_len]}")

                if len(samples) >= 8:
                    break

        return "\n\n".join(samples)

    def _get_semantic_code_samples(self) -> str:
        """Get code samples using semantic search."""
        samples = []
        queries = [
            "main entry point application startup initialization",
            "API routes endpoints handlers controllers",
            "database models schema data structures",
            "core business logic main functionality",
            "configuration settings environment setup",
            "authentication authorization security"
        ]

        seen_chunks = set()

        for query in queries:
            try:
                results = self.vector_store.search(query, top_k=3)

                for chunk, score in results:
                    if chunk.id not in seen_chunks and score > 0.1:
                        seen_chunks.add(chunk.id)
                        samples.append(f"=== {chunk.file_path} ({chunk.chunk_type}) ===\n{chunk.content[:1500]}")

                        if len(samples) >= 12:
                            break

                if len(samples) >= 12:
                    break
            except Exception:
                continue

        # If semantic search didn't find much, add some chunks directly
        if len(samples) < 3 and self.vector_store.chunks:
            for chunk in self.vector_store.chunks[:5]:
                if chunk.id not in seen_chunks:
                    samples.append(f"=== {chunk.file_path} ({chunk.chunk_type}) ===\n{chunk.content[:1500]}")
                    if len(samples) >= 8:
                        break

        return "\n\n".join(samples)

    def _get_relevant_code_for_readme(self) -> str:
        """Get relevant code snippets for README generation using vector store."""
        sections = []

        # Get configuration files
        config_results = self.vector_store.search("configuration setup package dependencies", top_k=3, chunk_types=['config'])
        for chunk, _ in config_results:
            sections.append(f"--- {chunk.file_path} ---\n{chunk.content[:2000]}")

        # Get main application code
        app_results = self.vector_store.search("main application entry point server", top_k=2, chunk_types=['function', 'class', 'module'])
        for chunk, _ in app_results:
            sections.append(f"--- {chunk.file_path} ({chunk.chunk_type}) ---\n{chunk.content[:1500]}")

        # Get API/routes if present
        if self.context.api_endpoints:
            api_results = self.vector_store.search("API routes endpoints handlers", top_k=2)
            for chunk, _ in api_results:
                sections.append(f"--- {chunk.file_path} ---\n{chunk.content[:1200]}")

        # Get documentation
        doc_results = self.vector_store.search("readme documentation usage examples", top_k=1, chunk_types=['doc'])
        for chunk, _ in doc_results:
            sections.append(f"--- {chunk.file_path} ---\n{chunk.content[:1500]}")

        return "\n".join(sections)

    def _create_understanding_prompt(self, code_samples: str) -> str:
        """Create prompt for code understanding."""
        user_purpose = self.context.user_answers.get('purpose', 'Not specified')

        return f"""Analyze this codebase and provide a clear, accurate summary.

PROJECT: {self.context.project_name}
USER SAYS IT'S FOR: {user_purpose}
LANGUAGES: {', '.join(self.context.languages.keys())}
FRAMEWORKS: {', '.join(self.context.frameworks)}

CODE TO ANALYZE:
{code_samples}

Provide a technical summary covering:
1. WHAT IT DOES: Main functionality (be specific, not generic)
2. HOW IT WORKS: Key components and their roles
3. DATA FLOW: How data moves through the system
4. KEY FEATURES: What capabilities does it provide
5. INTEGRATIONS: External services/APIs used

Be accurate and specific. Don't make assumptions not supported by the code.
Focus on actual functionality, not just listing technologies."""

    def _phase6_choose_style(self):
        """Phase 6: Let user choose README style."""
        if RICH_UI:
            print_phase(6, "README Style", "Choose the documentation style")
        else:
            print("\n┌─────────────────────────────────────────────────────────────────┐")
            print("│  PHASE 6: Choose README Style                                    │")
            print("└─────────────────────────────────────────────────────────────────┘")

        # Get suggested template
        suggest_context = {
            'api_endpoints': self.context.api_endpoints,
            'cli_commands': self.context.cli_commands,
            'dependencies': self.context.technologies,
            'complexity_score': self.context.complexity_score,
            'files': [f[0] for f in self.context.key_files]
        }
        suggested = TemplateManager.suggest_template(suggest_context)

        if self.quick_mode:
            self.context.readme_style = suggested
            if RICH_UI:
                print_info(f"Quick mode: Using suggested style '{suggested}'")
            else:
                print(f"📋 Quick mode: Using suggested style '{suggested}'")
            return

        templates = TemplateManager.list_templates()

        if RICH_UI:
            style_options = ['minimal', 'standard', 'detailed', 'comprehensive', 'api', 'cli', 'library', 'data_science']
            styles = [{"name": s, "description": TemplateManager.get_template(s).description} for s in style_options]
            self.context.readme_style = print_style_menu(styles, suggested)
            print_success(f"Selected style: {self.context.readme_style.upper()}")
        else:
            print("\n📋 Available README styles:\n")
            style_options = ['minimal', 'standard', 'detailed', 'comprehensive', 'api', 'cli', 'library', 'data_science']

            for i, style in enumerate(style_options, 1):
                template = TemplateManager.get_template(style)
                marker = " ⭐ (suggested)" if style == suggested else ""
                print(f"  {i}. {template.name.upper():<15} - {template.description}{marker}")

            print(f"\n💡 Based on your project, I suggest: {suggested.upper()}")

            choice = input(f"\nYour choice (1-{len(style_options)}, or press Enter for suggested): ").strip()

            if choice.isdigit() and 1 <= int(choice) <= len(style_options):
                self.context.readme_style = style_options[int(choice) - 1]
            else:
                self.context.readme_style = suggested

            print(f"\n✅ Selected style: {self.context.readme_style.upper()}")

    def _phase7_generate(self) -> Optional[str]:
        """Phase 7: Generate the README draft."""
        if RICH_UI:
            print_phase(7, "Generating README", "Creating your documentation")
        else:
            print("\n┌─────────────────────────────────────────────────────────────────┐")
            print("│  PHASE 7: Generating README                                      │")
            print("└─────────────────────────────────────────────────────────────────┘")

        # Create comprehensive prompt
        prompt = self._create_generation_prompt()

        # Generate with appropriate timeout
        timeout = 600 if self.context.complexity_score > 50 else 400

        if RICH_UI:
            with create_spinner("Generating your README...") as progress:
                task = progress.add_task("Generating your README...", total=None)
                draft = self._call_model(prompt, timeout=timeout)
                progress.update(task, completed=True)
        else:
            print("\n🤖 Creating your README with all gathered information...")
            print("   This may take 1-2 minutes for complex projects...\n")
            draft = self._call_model(prompt, timeout=timeout)

        if draft:
            draft = self._clean_output(draft)

            # Validate quality
            draft = self._validate_and_improve(draft)

            if RICH_UI:
                print_success("Draft generated!")
            else:
                print("✅ Draft generated!")
            return draft
        else:
            if RICH_UI:
                print_error("Failed to generate README.")
            else:
                print("❌ Failed to generate README.")
            return None

    def _create_generation_prompt(self) -> str:
        """Create the comprehensive generation prompt."""
        # Get style instructions
        style_instructions = get_style_instructions(self.context.readme_style, {
            'license': self.context.user_answers.get('license', 'MIT'),
            'version': '1.0.0'
        })

        # Build file contents - use vector store for smarter selection if available
        file_contents = ""
        if self.vector_store:
            file_contents = self._get_relevant_code_for_readme()
        else:
            for filename, content in self.context.key_files[:8]:
                max_len = 2000 if any(filename.endswith(ext) for ext in ['.json', '.toml', '.yml', '.yaml']) else 1200
                file_contents += f"\n--- {filename} ---\n{content[:max_len]}\n"

        # Build user answers section
        user_info = "\n".join([f"- {k}: {v}" for k, v in self.context.user_answers.items() if v])

        # Enhanced prompt for perfect README generation
        prompt = f"""You are an expert technical writer creating a world-class README.md file.
Your goal is to create a README that is:
- Professional and polished
- Clear and easy to follow
- Complete but not overwhelming
- Immediately useful to developers

══════════════════════════════════════════════════════════════════════
PROJECT INFORMATION
══════════════════════════════════════════════════════════════════════
Name: {self.context.project_name}
Repository: {self.context.repo_url}

══════════════════════════════════════════════════════════════════════
USER-PROVIDED INFORMATION (THIS IS THE MOST IMPORTANT!)
══════════════════════════════════════════════════════════════════════
{user_info if user_info else "No additional user input provided."}

══════════════════════════════════════════════════════════════════════
DETECTED TECHNICAL DETAILS
══════════════════════════════════════════════════════════════════════
Main Language: {list(self.context.languages.keys())[0] if self.context.languages else 'Unknown'}
All Languages: {', '.join(self.context.languages.keys()) if self.context.languages else 'Unknown'}
Frameworks: {', '.join(self.context.frameworks) if self.context.frameworks else 'None'}
Technologies: {', '.join(self.context.technologies[:12]) if self.context.technologies else 'None'}
Databases: {', '.join(self.context.databases) if self.context.databases else 'None'}
Docker: {'Yes - Services: ' + ', '.join(self.context.docker_services) if self.context.has_docker else 'No'}
API Endpoints: {len(self.context.api_endpoints)} detected
Environment Variables: {', '.join(self.context.env_vars[:8]) if self.context.env_vars else 'None'}
Complexity: {self.context.setup_difficulty} ({self.context.complexity_score} points)

══════════════════════════════════════════════════════════════════════
COMMANDS (VERIFIED FROM CODE)
══════════════════════════════════════════════════════════════════════
Install: {self.context.install_cmd or 'Not detected - infer from project type'}
Run: {self.context.run_cmd or 'Not detected - infer from project type'}
Dev: {self.context.dev_cmd or 'Not detected'}
Test: {self.context.test_cmd or 'Not detected'}
Build: {self.context.build_cmd or 'Not detected'}

══════════════════════════════════════════════════════════════════════
AI CODE UNDERSTANDING
══════════════════════════════════════════════════════════════════════
{self.context.code_understanding if self.context.code_understanding else 'No deep analysis available.'}

══════════════════════════════════════════════════════════════════════
DEEP CODE INSIGHTS
══════════════════════════════════════════════════════════════════════
Entry Points: {', '.join(self.context.entry_points[:5]) if self.context.entry_points else 'Not detected'}
Main Classes: {', '.join(self.context.main_classes[:5]) if self.context.main_classes else 'Not detected'}
Database Models: {', '.join(self.context.db_models[:5]) if self.context.db_models else 'None'}
External Integrations: {', '.join(self.context.external_integrations[:5]) if self.context.external_integrations else 'None'}
CLI Commands: {', '.join(self.context.cli_commands[:5]) if self.context.cli_commands else 'None'}

══════════════════════════════════════════════════════════════════════
PROJECT FILES
══════════════════════════════════════════════════════════════════════
{file_contents}

══════════════════════════════════════════════════════════════════════
STYLE REQUIREMENTS
══════════════════════════════════════════════════════════════════════
{style_instructions}

══════════════════════════════════════════════════════════════════════
QUALITY STANDARDS (MUST FOLLOW)
══════════════════════════════════════════════════════════════════════
1. START with a compelling project title and one-liner description
2. Use badges where appropriate (build status, license, version)
3. Every code example must be COPY-PASTEABLE and TESTED
4. NO placeholder text like [Add here], [TODO], [Your X here]
5. NO made-up features - only include what's verified from the code
6. Include a clear Table of Contents for longer READMEs
7. Installation steps must be numbered and complete
8. Configuration section must explain EVERY environment variable
9. Use appropriate emojis sparingly for visual appeal (📦 🚀 ⚙️ 📝 etc.)
10. End with clear contributing guidelines and license info
11. If you're unsure about something, be honest rather than inventing
12. Make the README scannable - use headers, bullets, and code blocks

FORMATTING RULES:
- Use proper Markdown syntax
- Code blocks must specify the language (```bash, ```python, etc.)
- Tables for comparing options or listing endpoints
- Collapsible sections for lengthy content (<details> tags)

Generate the complete, polished README now. Make it perfect."""

        return prompt

    def _validate_and_improve(self, readme: str) -> str:
        """Validate and improve the generated README."""
        issues = []

        # Check for common issues
        if '[' in readme and ']' in readme:
            # Check for placeholder patterns
            import re
            placeholders = re.findall(r'\[(?:TODO|Add|Insert|Your|PLACEHOLDER)[^\]]*\]', readme, re.IGNORECASE)
            if placeholders:
                issues.append(f"Found {len(placeholders)} placeholder(s)")

        if len(readme) < 500:
            issues.append("README is too short")

        if '# ' not in readme:
            issues.append("Missing headers")

        if '```' not in readme:
            issues.append("No code blocks")

        # If issues found, try to fix
        if issues:
            if RICH_UI:
                print_warning(f"Quality check found issues: {', '.join(issues)}")
                print_step("Attempting to fix...")
            else:
                print(f"⚠️  Quality check found issues: {', '.join(issues)}")

            fix_prompt = f"""The following README has some issues that need fixing:
{', '.join(issues)}

README:
{readme}

Please fix these issues and return the complete improved README.
Remove any placeholder text and ensure all sections are complete.
Return ONLY the fixed README, no explanations."""

            fixed = self._call_model(fix_prompt, timeout=180)
            if fixed:
                return self._clean_output(fixed)

        return readme

    def _phase8_review_refine(self, draft: str) -> str:
        """Phase 8: Review and refine the README."""
        if RICH_UI:
            print_phase(8, "Review & Refine", "Polish your README")
        else:
            print("\n┌─────────────────────────────────────────────────────────────────┐")
            print("│  PHASE 8: Review & Refine                                        │")
            print("└─────────────────────────────────────────────────────────────────┘")

        current = draft
        iteration = 0
        max_iterations = 5

        while iteration < max_iterations:
            iteration += 1

            # Show draft preview
            if RICH_UI:
                print_readme_preview(current, max_lines=40)
            else:
                print(f"\n📄 README Draft (v{iteration}):\n")
                print("─" * 60)
                preview_lines = current.split('\n')[:50]
                print('\n'.join(preview_lines))
                if len(current.split('\n')) > 50:
                    print(f"\n... [{len(current.split(chr(10))) - 50} more lines] ...")
                print("─" * 60)
                print(f"\n📊 Stats: {len(current):,} chars, {current.count(chr(10)):,} lines")

            # In quick mode, auto-accept first draft
            if self.quick_mode and iteration == 1:
                if RICH_UI:
                    print_success("Quick mode: Auto-accepting README")
                else:
                    print("✅ Quick mode: Auto-accepting README")
                return current

            # Options
            if RICH_UI:
                choice = print_review_menu()
            else:
                print("\n❓ What would you like to do?\n")
                print("  1. ✅ ACCEPT - Save this README")
                print("  2. ✏️  REFINE - Request specific changes")
                print("  3. 🔄 REGENERATE - Generate fresh draft")
                print("  4. 👁️  VIEW FULL - See complete README")
                print("  5. 🔍 CHECK MISSING - Find missing information")
                choice = input("\nChoice (1-5): ").strip()
                choice_map = {'1': 'accept', '2': 'refine', '3': 'regenerate', '4': 'view', '5': 'check'}
                choice = choice_map.get(choice, 'accept')

            if choice == 'accept':
                if RICH_UI:
                    print_success("README accepted!")
                else:
                    print("\n✅ README accepted!")
                return current

            elif choice == 'refine':
                if RICH_UI:
                    console.print("\n[bold]What changes would you like?[/]")
                    console.print("[dim]Examples: 'shorter description', 'more examples', 'add badges'[/]")
                    feedback = ask_text("Your feedback:")
                else:
                    print("\n📝 What changes would you like?")
                    print("   Examples: 'shorter description', 'more examples', 'add badges'")
                    feedback = input("\nYour feedback: ").strip()

                if feedback:
                    if RICH_UI:
                        with create_spinner("Refining README...") as progress:
                            task = progress.add_task("Refining README...", total=None)
                            refined = self._refine_readme(current, feedback)
                            progress.update(task, completed=True)
                    else:
                        print("\n🔄 Refining...")
                        refined = self._refine_readme(current, feedback)

                    if refined:
                        current = self._clean_output(refined)
                        if RICH_UI:
                            print_success("Refined!")
                        else:
                            print("✅ Refined!")
                    else:
                        if RICH_UI:
                            print_warning("Refinement failed, keeping current.")
                        else:
                            print("⚠️  Refinement failed, keeping current.")

            elif choice == 'regenerate':
                if RICH_UI:
                    with create_spinner("Regenerating README...") as progress:
                        task = progress.add_task("Regenerating README...", total=None)
                        new_draft = self._call_model(self._create_generation_prompt(), timeout=400)
                        progress.update(task, completed=True)
                else:
                    print("\n🔄 Regenerating...")
                    new_draft = self._call_model(self._create_generation_prompt(), timeout=400)

                if new_draft:
                    current = self._clean_output(new_draft)
                    if RICH_UI:
                        print_success("New draft generated!")
                    else:
                        print("✅ New draft generated!")
                else:
                    if RICH_UI:
                        print_warning("Regeneration failed.")
                    else:
                        print("⚠️  Regeneration failed.")

            elif choice == 'view':
                if RICH_UI:
                    console.print(Panel(current, title="[bold]Full README[/]", border_style="green"))
                    ask_text("Press Enter to continue...")
                else:
                    print("\n" + "═" * 60)
                    print("FULL README:")
                    print("═" * 60)
                    print(current)
                    print("═" * 60)
                    input("\nPress Enter to continue...")

            elif choice == 'check':
                if RICH_UI:
                    with create_spinner("Checking for missing information...") as progress:
                        task = progress.add_task("Checking...", total=None)
                        missing = self._check_missing_info(current)
                        progress.update(task, completed=True)
                else:
                    print("\n🔍 Checking for missing information...")
                    missing = self._check_missing_info(current)

                if RICH_UI:
                    print_missing_info(missing)
                else:
                    if missing:
                        print("\n⚠️  Potentially missing:")
                        for item in missing:
                            print(f"   • {item}")
                    else:
                        print("✅ No obvious missing information detected!")

                if missing:
                    if RICH_UI:
                        fill = ask_confirm("Would you like to provide this info?", default=True)
                    else:
                        fill = input("\nWould you like to provide this info? (yes/no): ").strip().lower()
                        fill = fill in ['yes', 'y']

                    if fill:
                        for item in missing:
                            if RICH_UI:
                                answer = ask_text(f"{item}:")
                            else:
                                answer = input(f"   {item}: ").strip()
                            if answer:
                                self.context.user_answers[f"missing_{len(self.context.user_answers)}"] = f"{item}: {answer}"

                        # Regenerate with new info
                        if RICH_UI:
                            with create_spinner("Regenerating with new information...") as progress:
                                task = progress.add_task("Regenerating...", total=None)
                                new_draft = self._call_model(self._create_generation_prompt(), timeout=400)
                                progress.update(task, completed=True)
                        else:
                            print("\n🔄 Regenerating with new information...")
                            new_draft = self._call_model(self._create_generation_prompt(), timeout=400)

                        if new_draft:
                            current = self._clean_output(new_draft)

        if RICH_UI:
            print_warning("Max iterations reached. Saving current version.")
        else:
            print(f"\n⚠️  Max iterations reached. Saving current version.")
        return current

    def _refine_readme(self, current: str, feedback: str) -> Optional[str]:
        """Refine README based on feedback."""
        prompt = f"""Refine this README based on user feedback.

CURRENT README:
{current}

USER FEEDBACK:
{feedback}

Apply the requested changes while keeping everything else intact.
Maintain the same quality and formatting standards.
Return the COMPLETE updated README."""

        return self._call_model(prompt, timeout=300)

    def _check_missing_info(self, readme: str) -> List[str]:
        """Check for missing information in the README."""
        missing = []
        readme_lower = readme.lower()

        checks = [
            (self.context.has_docker and 'docker' not in readme_lower, "Docker setup instructions"),
            (self.context.api_endpoints and 'api' not in readme_lower, "API documentation"),
            (self.context.env_vars and 'environment' not in readme_lower and 'env' not in readme_lower, "Environment variables"),
            (self.context.test_cmd and 'test' not in readme_lower, "Testing instructions"),
            ('license' not in readme_lower, "License information"),
            ('install' not in readme_lower, "Installation instructions"),
            (self.context.databases and not any(db.lower() in readme_lower for db in self.context.databases), "Database setup"),
        ]

        for condition, message in checks:
            if condition:
                missing.append(message)

        return missing[:5]

    def _phase9_save(self, readme: str):
        """Phase 9: Save README and cleanup."""
        if RICH_UI:
            print_phase(9, "Saving", "Finalizing your README")
        else:
            print("\n┌─────────────────────────────────────────────────────────────────┐")
            print("│  PHASE 9: Saving & Cleanup                                       │")
            print("└─────────────────────────────────────────────────────────────────┘")

        # Save README
        with open("README.md", 'w', encoding='utf-8') as f:
            f.write(readme)

        stats = {
            'chars': len(readme),
            'lines': readme.count('\n')
        }

        if RICH_UI:
            print_completion_banner("README.md", stats)
        else:
            print(f"\n✅ README saved to: README.md")
            print(f"   Size: {len(readme):,} characters")
            print(f"   Lines: {readme.count(chr(10)):,}")

        # Save debug info
        if self.debug:
            debug_data = {
                'project_name': self.context.project_name,
                'repo_url': self.context.repo_url,
                'languages': self.context.languages,
                'frameworks': self.context.frameworks,
                'technologies': self.context.technologies,
                'user_answers': self.context.user_answers,
                'readme_style': self.context.readme_style,
                'complexity_score': self.context.complexity_score
            }
            with open("generation_context.json", 'w') as f:
                json.dump(debug_data, f, indent=2)
            if RICH_UI:
                print_info("Debug info saved to: generation_context.json")
            else:
                print(f"   Debug info saved to: generation_context.json")

        # Cleanup
        if not self.debug:
            try:
                shutil.rmtree("cloned_repo")
                if RICH_UI:
                    print_info("Cleaned up temporary files.")
                else:
                    print("\n🧹 Cleaned up temporary files.")
            except:
                pass
        else:
            if RICH_UI:
                print_info("Debug mode: Repository preserved in 'cloned_repo/'")
            else:
                print("\n🐛 Debug mode: Repository preserved in 'cloned_repo/'")

    def _call_model(self, prompt: str, timeout: int = 300) -> Optional[str]:
        """Call the model using the configured provider."""
        return self.provider.generate(prompt, timeout=timeout)

    def _clean_output(self, output: str) -> str:
        """Clean model output."""
        import re

        # Remove code block wrappers
        if output.startswith('```markdown'):
            output = output[11:]
        elif output.startswith('```md'):
            output = output[5:]
        elif output.startswith('```'):
            output = output[3:]

        if output.endswith('```'):
            output = output[:-3]

        # Find actual README start
        lines = output.split('\n')
        start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('#') and not line.strip().startswith('##'):
                start = i
                break

        if start > 0:
            output = '\n'.join(lines[start:])

        # Remove meta commentary
        output = re.sub(r'^Here\'s.*?:\s*\n', '', output, flags=re.IGNORECASE)
        output = re.sub(r'^I\'ve created.*?:\s*\n', '', output, flags=re.IGNORECASE)

        return output.strip()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Nova v2.5 - AI-Powered README Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Using Ollama (default)
    python readme_generator_v2.py --repo https://github.com/user/project
    python readme_generator_v2.py --repo https://github.com/user/project --model llama3.2:3b

    # Using OpenAI
    python readme_generator_v2.py --repo https://github.com/user/project --model gpt-5.2-2025-12-11
    python readme_generator_v2.py --repo https://github.com/user/project --model gpt-5-mini-2025-08-07 --api-key sk-...

    # Using Claude
    python readme_generator_v2.py --repo https://github.com/user/project --model claude-sonnet-4-5-20250929

    # Quick mode (fewer questions)
    python readme_generator_v2.py --repo https://github.com/user/project --quick

Model auto-detection:
    - Models starting with 'gpt-' or 'o1' -> OpenAI
    - Models starting with 'claude' -> Anthropic Claude
    - Everything else -> Ollama (local)
    - Or use prefix: 'openai:model', 'claude:model', 'ollama:model'

Environment variables for API keys:
    - OPENAI_API_KEY for OpenAI models
    - ANTHROPIC_API_KEY for Claude models
        """
    )

    parser.add_argument('--repo', required=True, help='Git repository URL')
    parser.add_argument('--model', default='llama3.2:latest',
                       help='Model to use. Auto-detects provider from name')
    parser.add_argument('--api-key', dest='api_key', help='API key for OpenAI/Claude')
    parser.add_argument('--debug', action='store_true', help='Keep debug files')
    parser.add_argument('--quick', action='store_true', help='Quick mode with fewer questions')
    parser.add_argument('--no-embeddings', dest='no_embeddings', action='store_true',
                       help='Disable vector store embeddings')
    parser.add_argument('--embedding-provider', dest='embedding_provider', default='local',
                       choices=['local', 'openai', 'ollama'],
                       help='Embedding provider for vector store (default: local)')

    args = parser.parse_args()

    try:
        generator = ReadmeGeneratorV2(
            model=args.model,
            debug=args.debug,
            api_key=args.api_key,
            use_embeddings=not args.no_embeddings,
            embedding_provider=args.embedding_provider,
            quick_mode=args.quick
        )
        success = generator.run(args.repo)
        return 0 if success else 1
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
