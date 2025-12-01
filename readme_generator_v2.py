#!/usr/bin/env python3
"""
README Generator v2.0
A fully interactive, multi-pass README generator with deep code understanding.

Features:
- Multi-pass analysis (analyze → ask → understand → generate → refine)
- Interactive question-answer flow
- Deep code understanding
- Template-based generation
- Iterative refinement
- Missing info detection
"""

import argparse
import os
import shutil
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict

# Local imports
from analyzer import EnhancedProjectAnalyzer
from deep_analyzer import DeepCodeAnalyzer
from question_engine import QuestionEngine, Question
from readme_templates import TemplateManager, get_style_instructions
from docker import clone_repo


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
    
    def __init__(self, model: str = "llama3.2:latest", debug: bool = False):
        self.model = model
        self.debug = debug
        self.context = GenerationContext()
        self.analyzer: Optional[EnhancedProjectAnalyzer] = None
        self.deep_analyzer: Optional[DeepCodeAnalyzer] = None
        self.question_engine = QuestionEngine(model)
        
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
        
        # Phase 4: Interactive Q&A
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
        print("\n" + "═" * 70)
        print("  📝 README GENERATOR v2.0 - Interactive & Intelligent")
        print("═" * 70)
        print(f"\n  Repository: {self.context.repo_url}")
        print(f"  Model: {self.model}")
        print("\n  This tool will guide you through creating the perfect README.")
        print("  It analyzes your code, asks smart questions, and refines the output.")
        print("═" * 70)
    
    def _phase1_clone_and_analyze(self) -> bool:
        """Phase 1: Clone repository and perform initial analysis."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│  PHASE 1: Cloning & Analyzing Repository                        │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        # Clone
        if not clone_repo(self.context.repo_url):
            return False
        
        # Analyze with EnhancedProjectAnalyzer
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
        
        print("✅ Initial analysis complete!")
        return True
    
    def _phase2_deep_analysis(self):
        """Phase 2: Deep code analysis."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│  PHASE 2: Deep Code Analysis                                     │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
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
        
        print("✅ Deep analysis complete!")
        
        # Show summary
        summary = self.deep_analyzer.get_summary()
        if summary:
            print("\n📊 Code Insights:")
            for line in summary.split('\n')[:15]:
                print(f"   {line}")


    def _phase3_present_findings(self):
        """Phase 3: Present analysis findings to user."""
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
        
        if self.context.technologies:
            print(f"\n🔧 Technologies: {', '.join(self.context.technologies[:10])}")
        
        if self.context.has_docker:
            print(f"\n🐳 Docker: Yes")
            if self.context.docker_services:
                print(f"   Services: {', '.join(self.context.docker_services)}")
            if self.context.databases:
                print(f"   Databases: {', '.join(self.context.databases)}")
        
        if self.context.api_endpoints:
            print(f"\n🌐 API Endpoints: {len(self.context.api_endpoints)} detected")
        
        if self.context.features:
            print(f"\n✨ Features: {', '.join(self.context.features[:6])}")
        
        # Ask for confirmation/corrections
        print("\n" + "-" * 50)
        print("❓ Is this analysis correct?")
        response = input("   (yes/no/edit): ").strip().lower()
        
        if response in ['no', 'n', 'edit', 'e']:
            self._correct_analysis()
    
    def _correct_analysis(self):
        """Allow user to correct the analysis."""
        print("\n📝 Let's correct the analysis:")
        
        # Correct technologies
        print(f"\nCurrent technologies: {', '.join(self.context.technologies[:15])}")
        remove = input("Technologies to REMOVE (comma-separated, or Enter to skip): ").strip()
        if remove:
            to_remove = [t.strip().lower() for t in remove.split(',')]
            self.context.technologies = [t for t in self.context.technologies 
                                         if t.lower() not in to_remove]
        
        add = input("Technologies to ADD (comma-separated, or Enter to skip): ").strip()
        if add:
            self.context.technologies.extend([t.strip() for t in add.split(',')])
        
        # Correct frameworks
        print(f"\nCurrent frameworks: {', '.join(self.context.frameworks)}")
        remove = input("Frameworks to REMOVE (comma-separated, or Enter to skip): ").strip()
        if remove:
            to_remove = [f.strip().lower() for f in remove.split(',')]
            self.context.frameworks = [f for f in self.context.frameworks 
                                       if f.lower() not in to_remove]
        
        add = input("Frameworks to ADD (comma-separated, or Enter to skip): ").strip()
        if add:
            self.context.frameworks.extend([f.strip() for f in add.split(',')])
        
        print("\n✅ Analysis updated!")
    
    def _phase4_ask_questions(self):
        """Phase 4: Ask intelligent questions."""
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
        
        # Ask questions interactively
        self.context.user_answers = self.question_engine.ask_questions_interactive(questions)
        
        print("\n✅ Thank you! I have a much better understanding now.")
    
    def _phase5_llm_understanding(self):
        """Phase 5: Use LLM to understand the code deeply."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│  PHASE 5: AI Code Understanding                                  │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        print("\n🤖 Asking AI to analyze and understand the codebase...")
        
        # Prepare code samples
        code_samples = self._prepare_code_samples()
        
        if not code_samples:
            print("⚠️  No significant source code found.")
            return
        
        # Create understanding prompt
        prompt = self._create_understanding_prompt(code_samples)
        
        # Get understanding
        understanding = self._call_model(prompt, timeout=180)
        
        if understanding:
            self.context.code_understanding = understanding
            print("✅ Code understanding complete!")
            
            # Show preview
            print("\n📝 AI's Understanding:\n" + "-" * 40)
            preview = understanding[:600] + "..." if len(understanding) > 600 else understanding
            print(preview)
            print("-" * 40)
            
            # Ask for corrections
            correct = input("\n❓ Is this understanding accurate? (yes/no): ").strip().lower()
            if correct in ['no', 'n']:
                correction = input("Please provide corrections: ").strip()
                if correction:
                    self.context.code_understanding += f"\n\n[User Correction]: {correction}"
        else:
            print("⚠️  Could not get AI understanding. Continuing with detected info.")
    
    def _prepare_code_samples(self) -> str:
        """Prepare code samples for LLM analysis."""
        samples = []
        source_ext = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs'}
        
        # Prioritize entry points and main files
        priority_names = ['main', 'app', 'index', 'server', 'api', 'routes', 'models']
        
        for filename, content in self.context.key_files:
            # Check if it's a source file
            if any(filename.endswith(ext) for ext in source_ext):
                # Prioritize important files
                is_priority = any(p in filename.lower() for p in priority_names)
                max_len = 2500 if is_priority else 1500
                
                samples.append(f"=== {filename} ===\n{content[:max_len]}")
                
                if len(samples) >= 8:
                    break
        
        return "\n\n".join(samples)
    
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
        
        print("\n📋 Available README styles:\n")
        templates = TemplateManager.list_templates()
        
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
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│  PHASE 7: Generating README                                      │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        print("\n🤖 Creating your README with all gathered information...")
        print("   This may take 1-2 minutes for complex projects...\n")
        
        # Create comprehensive prompt
        prompt = self._create_generation_prompt()
        
        # Generate with appropriate timeout
        timeout = 600 if self.context.complexity_score > 50 else 400
        
        draft = self._call_model(prompt, timeout=timeout)
        
        if draft:
            draft = self._clean_output(draft)
            print("✅ Draft generated!")
            return draft
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
        
        # Build file contents
        file_contents = ""
        for filename, content in self.context.key_files[:8]:
            max_len = 2000 if any(filename.endswith(ext) for ext in ['.json', '.toml', '.yml', '.yaml']) else 1200
            file_contents += f"\n--- {filename} ---\n{content[:max_len]}\n"
        
        # Build user answers section
        user_info = "\n".join([f"- {k}: {v}" for k, v in self.context.user_answers.items() if v])
        
        prompt = f"""Generate a professional README.md for this project.

══════════════════════════════════════════════════════════════════════
PROJECT INFORMATION
══════════════════════════════════════════════════════════════════════
Name: {self.context.project_name}
Repository: {self.context.repo_url}

══════════════════════════════════════════════════════════════════════
USER-PROVIDED INFORMATION (PRIORITIZE THIS!)
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
COMMANDS
══════════════════════════════════════════════════════════════════════
Install: {self.context.install_cmd or 'Not detected'}
Run: {self.context.run_cmd or 'Not detected'}
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
CRITICAL INSTRUCTIONS
══════════════════════════════════════════════════════════════════════
1. USE USER-PROVIDED INFO FIRST - they know their project best
2. Be ACCURATE - only include verifiable information
3. Make commands COPY-PASTEABLE
4. NO placeholder text like [Add here] or [TODO]
5. NO made-up features or functionality
6. Use proper markdown formatting
7. Be professional and well-organized
8. Include relevant emojis for visual appeal (don't overdo it)
9. If unsure about something, be honest rather than guessing

Generate the complete README now:"""
        
        return prompt
    
    def _phase8_review_refine(self, draft: str) -> str:
        """Phase 8: Review and refine the README."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│  PHASE 8: Review & Refine                                        │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        current = draft
        iteration = 0
        max_iterations = 5
        
        while iteration < max_iterations:
            iteration += 1
            
            # Show draft preview
            print(f"\n📄 README Draft (v{iteration}):\n")
            print("─" * 60)
            preview_lines = current.split('\n')[:50]
            print('\n'.join(preview_lines))
            if len(current.split('\n')) > 50:
                print(f"\n... [{len(current.split(chr(10))) - 50} more lines] ...")
            print("─" * 60)
            
            print(f"\n📊 Stats: {len(current):,} chars, {current.count(chr(10)):,} lines")
            
            # Options
            print("\n❓ What would you like to do?\n")
            print("  1. ✅ ACCEPT - Save this README")
            print("  2. ✏️  REFINE - Request specific changes")
            print("  3. 🔄 REGENERATE - Generate fresh draft")
            print("  4. 👁️  VIEW FULL - See complete README")
            print("  5. 🔍 CHECK MISSING - Find missing information")
            
            choice = input("\nChoice (1-5): ").strip()
            
            if choice == '1':
                print("\n✅ README accepted!")
                return current
            
            elif choice == '2':
                print("\n📝 What changes would you like?")
                print("   Examples: 'shorter description', 'more examples', 'add badges'")
                feedback = input("\nYour feedback: ").strip()
                
                if feedback:
                    print("\n🔄 Refining...")
                    refined = self._refine_readme(current, feedback)
                    if refined:
                        current = self._clean_output(refined)
                        print("✅ Refined!")
                    else:
                        print("⚠️  Refinement failed, keeping current.")
            
            elif choice == '3':
                print("\n🔄 Regenerating...")
                new_draft = self._call_model(self._create_generation_prompt(), timeout=400)
                if new_draft:
                    current = self._clean_output(new_draft)
                    print("✅ New draft generated!")
                else:
                    print("⚠️  Regeneration failed.")
            
            elif choice == '4':
                print("\n" + "═" * 60)
                print("FULL README:")
                print("═" * 60)
                print(current)
                print("═" * 60)
                input("\nPress Enter to continue...")
            
            elif choice == '5':
                print("\n🔍 Checking for missing information...")
                missing = self._check_missing_info(current)
                if missing:
                    print("\n⚠️  Potentially missing:")
                    for item in missing:
                        print(f"   • {item}")
                    
                    fill = input("\nWould you like to provide this info? (yes/no): ").strip().lower()
                    if fill in ['yes', 'y']:
                        for item in missing:
                            answer = input(f"   {item}: ").strip()
                            if answer:
                                self.context.user_answers[f"missing_{len(self.context.user_answers)}"] = f"{item}: {answer}"
                        
                        # Regenerate with new info
                        print("\n🔄 Regenerating with new information...")
                        new_draft = self._call_model(self._create_generation_prompt(), timeout=400)
                        if new_draft:
                            current = self._clean_output(new_draft)
                else:
                    print("✅ No obvious missing information detected!")
            
            else:
                print("Invalid choice.")
        
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
Return the COMPLETE updated README."""
        
        return self._call_model(prompt, timeout=300)
    
    def _check_missing_info(self, readme: str) -> List[str]:
        """Check for missing information in the README."""
        missing = []
        readme_lower = readme.lower()
        
        # Check for common missing elements
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
        
        return missing[:5]  # Limit to 5 items
    
    def _phase9_save(self, readme: str):
        """Phase 9: Save README and cleanup."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│  PHASE 9: Saving & Cleanup                                       │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        # Save README
        with open("README.md", 'w', encoding='utf-8') as f:
            f.write(readme)
        
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
            print(f"   Debug info saved to: generation_context.json")
        
        # Cleanup
        if not self.debug:
            try:
                shutil.rmtree("cloned_repo")
                print("\n🧹 Cleaned up temporary files.")
            except:
                pass
        else:
            print("\n🐛 Debug mode: Repository preserved in 'cloned_repo/'")
        
        print("\n" + "═" * 70)
        print("  🎉 README GENERATION COMPLETE!")
        print("═" * 70)
    
    def _call_model(self, prompt: str, timeout: int = 300) -> Optional[str]:
        """Call the Ollama model."""
        try:
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt.encode('utf-8'),
                capture_output=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                error = result.stderr.decode()[:200] if result.stderr else "Unknown error"
                print(f"⚠️  Model error: {error}")
                return None
            
            return result.stdout.decode('utf-8').strip()
            
        except subprocess.TimeoutExpired:
            print(f"⚠️  Timeout after {timeout}s")
            return None
        except FileNotFoundError:
            print("❌ Ollama not found. Install it and run 'ollama serve'")
            return None
        except Exception as e:
            print(f"⚠️  Error: {e}")
            return None
    
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
        description="README Generator v2.0 - Interactive & Intelligent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python readme_generator_v2.py --repo https://github.com/user/project
    python readme_generator_v2.py --repo https://github.com/user/project --model llama3.2:3b
    python readme_generator_v2.py --repo https://github.com/user/project --debug
        """
    )
    
    parser.add_argument('--repo', required=True, help='Git repository URL')
    parser.add_argument('--model', default='llama3.2:latest', help='Ollama model (default: llama3.2:latest)')
    parser.add_argument('--debug', action='store_true', help='Keep debug files')
    
    args = parser.parse_args()
    
    generator = ReadmeGeneratorV2(model=args.model, debug=args.debug)
    success = generator.run(args.repo)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
