#!/usr/bin/env python3
"""
README Generator v3.0
Deep understanding with vector store for intelligent context retrieval.

Features:
- Deep project analysis with knowledge base
- Vector store for intelligent context retrieval
- Multi-pass LLM understanding
- Section-by-section generation with relevant context
- Interactive refinement
"""

import argparse
import os
import shutil
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field

from docker import clone_repo
from project_knowledge import DeepProjectAnalyzer, ProjectKnowledge, SimpleVectorStore
from question_engine import QuestionEngine
from readme_templates import TemplateManager, get_style_instructions


@dataclass
class GenerationState:
    """Tracks the state of README generation."""
    repo_url: str = ""
    project_name: str = ""
    readme_style: str = "detailed"
    user_answers: Dict[str, str] = field(default_factory=dict)
    generated_sections: Dict[str, str] = field(default_factory=dict)
    revision_count: int = 0


class ReadmeGeneratorV3:
    """
    Advanced README generator with deep project understanding.
    Uses vector store for intelligent context retrieval.
    """
    
    def __init__(self, model: str = "llama3.2:latest", debug: bool = False):
        self.model = model
        self.debug = debug
        self.state = GenerationState()
        self.knowledge: Optional[ProjectKnowledge] = None
        self.analyzer: Optional[DeepProjectAnalyzer] = None
        self.question_engine = QuestionEngine(model)
    
    def run(self, repo_url: str) -> bool:
        """Run the complete generation pipeline."""
        self.state.repo_url = repo_url
        self.state.project_name = repo_url.split('/')[-1].replace('.git', '')
        
        self._print_header()
        
        # Phase 1: Clone Repository
        if not self._phase_clone():
            return False
        
        # Phase 2: Deep Analysis with Knowledge Base
        if not self._phase_deep_analysis():
            return False
        
        # Phase 3: Present Understanding
        self._phase_present_understanding()
        
        # Phase 4: Interactive Q&A
        self._phase_questions()
        
        # Phase 5: Choose Style
        self._phase_choose_style()
        
        # Phase 6: Generate README with Context
        draft = self._phase_generate_with_context()
        if not draft:
            return False
        
        # Phase 7: Review and Refine
        final = self._phase_review_refine(draft)
        
        # Phase 8: Save
        self._phase_save(final)
        
        return True
    
    def _print_header(self):
        """Print welcome header."""
        print("\n" + "═" * 70)
        print("  📝 README GENERATOR v3.0 - Deep Understanding Edition")
        print("═" * 70)
        print(f"\n  Repository: {self.state.repo_url}")
        print(f"  Model: {self.model}")
        print("\n  Features:")
        print("  • Deep project analysis with knowledge base")
        print("  • Vector store for intelligent context retrieval")
        print("  • Section-by-section generation with relevant context")
        print("  • Interactive refinement")
        print("═" * 70)
    
    def _phase_clone(self) -> bool:
        """Phase 1: Clone the repository."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│  PHASE 1: Cloning Repository                                     │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        return clone_repo(self.state.repo_url)
    
    def _phase_deep_analysis(self) -> bool:
        """Phase 2: Perform deep analysis and build knowledge base."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│  PHASE 2: Deep Project Analysis                                  │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        try:
            self.analyzer = DeepProjectAnalyzer(model=self.model)
            self.knowledge = self.analyzer.analyze()
            
            # Save knowledge for debugging
            if self.debug:
                self.analyzer.save_knowledge("debug_knowledge.json")
            
            return True
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return False
    
    def _phase_present_understanding(self):
        """Phase 3: Present what we understood about the project."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│  PHASE 3: Project Understanding                                  │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        k = self.knowledge
        
        print(f"\n🏷️  Project: {k.name or self.state.project_name}")
        if k.description:
            print(f"📝 Description: {k.description}")
        print(f"🔧 Build System: {k.build_system or 'Unknown'}")
        print(f"🏗️  Architecture: {k.architecture_type or 'Unknown'}")
        
        # Dependencies
        if k.dependencies:
            print(f"\n📦 Dependencies ({len(k.dependencies)} total):")
            # Group by category
            by_category = {}
            for dep in k.dependencies:
                cat = dep.category or 'Other'
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(dep)
            
            for category, deps in list(by_category.items())[:6]:
                dep_names = [d.name for d in deps[:4]]
                more = f" +{len(deps)-4} more" if len(deps) > 4 else ""
                print(f"   {category}: {', '.join(dep_names)}{more}")
        
        # Docker Services
        if k.services:
            print(f"\n🐳 Docker Services ({len(k.services)}):")
            for svc in k.services[:5]:
                print(f"   • {svc.name}: {svc.purpose}")
        
        # Environment Variables
        if k.environment_vars:
            required = [e for e in k.environment_vars if e.get('required')]
            optional = [e for e in k.environment_vars if not e.get('required')]
            print(f"\n🔐 Environment Variables:")
            print(f"   Required: {len(required)}, Optional: {len(optional)}")
            if required:
                print(f"   Required vars: {', '.join(e['name'] for e in required[:5])}")
        
        # CI/CD
        if k.ci_cd:
            print(f"\n🔄 CI/CD: {', '.join(k.ci_cd)}")
        
        # Entry Points
        if k.entry_points:
            print(f"\n🚀 Entry Points: {', '.join(k.entry_points)}")
        
        # AI Understanding
        if k.project_summary:
            print(f"\n🤖 AI Understanding:")
            print("-" * 50)
            # Show first 400 chars
            summary = k.project_summary[:400]
            if len(k.project_summary) > 400:
                summary += "..."
            print(summary)
            print("-" * 50)
        
        # Ask for confirmation
        print("\n❓ Is this understanding correct?")
        response = input("   (yes/no/details): ").strip().lower()
        
        if response == 'details':
            self._show_full_understanding()
        elif response in ['no', 'n']:
            self._correct_understanding()
    
    def _show_full_understanding(self):
        """Show full AI understanding."""
        k = self.knowledge
        
        print("\n" + "=" * 60)
        print("FULL PROJECT UNDERSTANDING")
        print("=" * 60)
        
        if k.project_summary:
            print("\n📝 PROJECT SUMMARY:")
            print(k.project_summary)
        
        if k.technical_overview:
            print("\n🔧 TECHNICAL OVERVIEW:")
            print(k.technical_overview)
        
        if k.setup_guide:
            print("\n📋 SETUP GUIDE:")
            print(k.setup_guide)
        
        print("=" * 60)
        input("\nPress Enter to continue...")
    
    def _correct_understanding(self):
        """Allow user to correct the understanding."""
        print("\n📝 Please provide corrections:")
        
        print("\nWhat is the main purpose of this project?")
        purpose = input("   Purpose: ").strip()
        if purpose:
            self.state.user_answers['purpose_correction'] = purpose
        
        print("\nAny technologies incorrectly detected or missing?")
        tech_correction = input("   Corrections: ").strip()
        if tech_correction:
            self.state.user_answers['tech_correction'] = tech_correction
        
        print("\nAnything else important to know?")
        other = input("   Other: ").strip()
        if other:
            self.state.user_answers['other_correction'] = other
        
        print("\n✅ Corrections noted!")
    
    def _phase_questions(self):
        """Phase 4: Ask intelligent questions."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│  PHASE 4: Project Questions                                      │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        # Prepare context for question generation
        q_context = {
            'project_name': self.state.project_name,
            'languages': {self.knowledge.build_system: 1} if self.knowledge.build_system else {},
            'frameworks': [d.name for d in self.knowledge.dependencies if d.category == 'Web Framework'],
            'has_docker': bool(self.knowledge.services),
            'docker_services': [s.name for s in self.knowledge.services],
            'api_endpoints': [],
            'databases': [s.name for s in self.knowledge.services if 'database' in s.purpose.lower()],
            'env_vars': [e['name'] for e in self.knowledge.environment_vars],
            'complexity_score': len(self.knowledge.dependencies) + len(self.knowledge.services) * 5,
            'features': [],
            'cli_commands': [],
            'test_cmd': ''
        }
        
        # Generate and ask questions
        questions = self.question_engine.generate_smart_questions(q_context)
        self.state.user_answers.update(
            self.question_engine.ask_questions_interactive(questions)
        )
        
        print("\n✅ Thank you for the information!")
    
    def _phase_choose_style(self):
        """Phase 5: Choose README style."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│  PHASE 5: Choose README Style                                    │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        # Suggest based on project
        complexity = len(self.knowledge.dependencies) + len(self.knowledge.services) * 5
        
        if complexity < 10:
            suggested = 'standard'
        elif complexity < 30:
            suggested = 'detailed'
        else:
            suggested = 'comprehensive'
        
        print("\n📋 Available styles:\n")
        styles = ['minimal', 'standard', 'detailed', 'comprehensive']
        
        for i, style in enumerate(styles, 1):
            template = TemplateManager.get_template(style)
            marker = " ⭐ (suggested)" if style == suggested else ""
            print(f"  {i}. {style.upper():<15} - {template.description}{marker}")
        
        choice = input(f"\nChoice (1-4, Enter for {suggested}): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 4:
            self.state.readme_style = styles[int(choice) - 1]
        else:
            self.state.readme_style = suggested
        
        print(f"\n✅ Selected: {self.state.readme_style.upper()}")


    def _phase_generate_with_context(self) -> Optional[str]:
        """Phase 6: Generate README using vector store for context."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│  PHASE 6: Generating README with Deep Context                    │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        print("\n🤖 Generating README section by section...")
        print("   Using knowledge base for relevant context...\n")
        
        # Generate section by section for better quality
        sections = self._get_sections_for_style()
        
        generated_parts = []
        
        for i, section in enumerate(sections, 1):
            print(f"   [{i}/{len(sections)}] Generating {section}...")
            
            # Get relevant context from vector store
            context = self.analyzer.get_context_for_readme(section)
            
            # Generate section
            section_content = self._generate_section(section, context)
            
            if section_content:
                generated_parts.append(section_content)
                self.state.generated_sections[section] = section_content
        
        if not generated_parts:
            print("❌ Failed to generate README")
            return None
        
        # Combine all sections
        full_readme = "\n\n".join(generated_parts)
        
        # Final polish pass
        print("\n   🔄 Final polish pass...")
        polished = self._polish_readme(full_readme)
        
        print("✅ README generated!")
        return polished or full_readme
    
    def _get_sections_for_style(self) -> List[str]:
        """Get sections to generate based on style."""
        style_sections = {
            'minimal': ['header', 'quick_start'],
            'standard': ['header', 'features', 'installation', 'usage', 'contributing'],
            'detailed': [
                'header', 'features', 'tech_stack', 'prerequisites',
                'installation', 'configuration', 'usage', 'docker',
                'project_structure', 'contributing', 'license'
            ],
            'comprehensive': [
                'header', 'features', 'tech_stack', 'architecture',
                'prerequisites', 'installation', 'configuration',
                'usage', 'api', 'docker', 'project_structure',
                'development', 'testing', 'troubleshooting',
                'contributing', 'license', 'support'
            ]
        }
        
        sections = style_sections.get(self.state.readme_style, style_sections['detailed'])
        
        # Filter based on project
        if not self.knowledge.services:
            sections = [s for s in sections if s != 'docker']
        
        return sections
    
    def _generate_section(self, section: str, context: str) -> Optional[str]:
        """Generate a specific README section with relevant context."""
        k = self.knowledge
        
        # Section-specific prompts
        section_prompts = {
            'header': self._create_header_prompt(context),
            'features': self._create_features_prompt(context),
            'tech_stack': self._create_tech_stack_prompt(context),
            'architecture': self._create_architecture_prompt(context),
            'prerequisites': self._create_prerequisites_prompt(context),
            'installation': self._create_installation_prompt(context),
            'configuration': self._create_configuration_prompt(context),
            'usage': self._create_usage_prompt(context),
            'api': self._create_api_prompt(context),
            'docker': self._create_docker_prompt(context),
            'project_structure': self._create_structure_prompt(context),
            'development': self._create_development_prompt(context),
            'testing': self._create_testing_prompt(context),
            'troubleshooting': self._create_troubleshooting_prompt(context),
            'contributing': self._create_contributing_prompt(),
            'license': self._create_license_prompt(),
            'support': self._create_support_prompt(),
            'quick_start': self._create_quick_start_prompt(context)
        }
        
        prompt = section_prompts.get(section)
        if not prompt:
            return None
        
        result = self._call_model(prompt, timeout=90)
        return self._clean_section(result) if result else None
    
    def _create_header_prompt(self, context: str) -> str:
        """Create prompt for header section."""
        k = self.knowledge
        user_purpose = self.state.user_answers.get('purpose', '')
        
        return f"""Generate the header section for a README.md file.

PROJECT: {k.name or self.state.project_name}
USER SAYS PURPOSE: {user_purpose or 'Not specified'}
AI UNDERSTANDING: {k.project_summary[:500] if k.project_summary else 'Not available'}

RELEVANT CONTEXT:
{context[:1000]}

Generate:
1. Project title with emoji
2. Short tagline (one line)
3. 2-3 paragraph description explaining:
   - What the project does
   - Why it exists / what problem it solves
   - Key benefits

Format as markdown. Start with # {k.name or self.state.project_name}
Be compelling but accurate. No placeholder text."""
    
    def _create_features_prompt(self, context: str) -> str:
        """Create prompt for features section."""
        k = self.knowledge
        user_features = self.state.user_answers.get('key_features', '')
        
        deps_by_category = {}
        for dep in k.dependencies:
            cat = dep.category
            if cat not in deps_by_category:
                deps_by_category[cat] = []
            deps_by_category[cat].append(dep.name)
        
        return f"""Generate the Features section for a README.

USER HIGHLIGHTED FEATURES: {user_features or 'Not specified'}

DETECTED CAPABILITIES:
{json.dumps(deps_by_category, indent=2)[:1000]}

SERVICES: {[s.purpose for s in k.services][:5]}

CONTEXT:
{context[:800]}

Generate a "## ✨ Features" section with:
- 6-10 key features as bullet points
- Each feature should have a brief description
- Use emojis for visual appeal
- Be specific based on actual capabilities

Format as markdown."""
    
    def _create_tech_stack_prompt(self, context: str) -> str:
        """Create prompt for tech stack section."""
        k = self.knowledge
        
        deps_info = []
        for dep in k.dependencies[:20]:
            deps_info.append(f"- {dep.name}: {dep.purpose} ({dep.category})")
        
        return f"""Generate the Tech Stack section for a README.

BUILD SYSTEM: {k.build_system}
ARCHITECTURE: {k.architecture_type}

DEPENDENCIES:
{chr(10).join(deps_info)}

SERVICES:
{[f"{s.name}: {s.purpose}" for s in k.services]}

Generate a "## 🛠️ Tech Stack" section with:
- Organized by category (Languages, Frameworks, Databases, etc.)
- Brief explanation of why each technology is used
- Use a clean table or list format

Format as markdown."""
    
    def _create_architecture_prompt(self, context: str) -> str:
        """Create prompt for architecture section."""
        k = self.knowledge
        
        return f"""Generate the Architecture section for a README.

ARCHITECTURE TYPE: {k.architecture_type}
SERVICES: {[(s.name, s.purpose) for s in k.services]}
ENTRY POINTS: {k.entry_points}

TECHNICAL OVERVIEW:
{k.technical_overview[:1000] if k.technical_overview else 'Not available'}

CONTEXT:
{context[:800]}

Generate a "## 🏗️ Architecture" section with:
- High-level architecture description
- How components interact
- Data flow explanation
- ASCII diagram if helpful

Format as markdown."""
    
    def _create_prerequisites_prompt(self, context: str) -> str:
        """Create prompt for prerequisites section."""
        k = self.knowledge
        
        return f"""Generate the Prerequisites section for a README.

BUILD SYSTEM: {k.build_system}
HAS DOCKER: {'Yes' if k.services else 'No'}
REQUIRED ENV VARS: {[e['name'] for e in k.environment_vars if e.get('required')][:10]}

USER MENTIONED REQUIREMENTS: {self.state.user_answers.get('special_requirements', 'None')}

Generate a "## 📋 Prerequisites" section with:
- Required software and versions
- System requirements
- External services needed (if any)
- Use a checklist format

Format as markdown. Be specific about versions."""
    
    def _create_installation_prompt(self, context: str) -> str:
        """Create prompt for installation section."""
        k = self.knowledge
        
        return f"""Generate the Installation section for a README.

PROJECT: {k.name or self.state.project_name}
BUILD SYSTEM: {k.build_system}
HAS DOCKER: {'Yes' if k.services else 'No'}

SETUP GUIDE FROM ANALYSIS:
{k.setup_guide[:1000] if k.setup_guide else 'Not available'}

CONTEXT:
{context[:800]}

Generate a "## 🚀 Installation" section with:
1. Clone command
2. Install dependencies command
3. Any additional setup steps
4. Docker alternative (if applicable)

Use numbered steps. All commands must be copy-pasteable.
Format as markdown with code blocks."""
    
    def _create_configuration_prompt(self, context: str) -> str:
        """Create prompt for configuration section."""
        k = self.knowledge
        
        env_info = []
        for env in k.environment_vars[:15]:
            required = "REQUIRED" if env.get('required') else "optional"
            env_info.append(f"- {env['name']} ({required}): {env['purpose']}")
        
        return f"""Generate the Configuration section for a README.

ENVIRONMENT VARIABLES:
{chr(10).join(env_info) if env_info else 'None documented'}

USER INFO: {self.state.user_answers.get('env_secrets', 'None provided')}

Generate a "## ⚙️ Configuration" section with:
1. How to set up environment variables
2. Table of all variables with descriptions
3. Example .env file content
4. Where to get API keys (if mentioned)

Format as markdown with code blocks for examples."""
    
    def _create_usage_prompt(self, context: str) -> str:
        """Create prompt for usage section."""
        k = self.knowledge
        
        return f"""Generate the Usage section for a README.

BUILD SYSTEM: {k.build_system}
ENTRY POINTS: {k.entry_points}
HAS DOCKER: {'Yes' if k.services else 'No'}

SETUP GUIDE:
{k.setup_guide[:800] if k.setup_guide else 'Not available'}

CONTEXT:
{context[:600]}

Generate a "## 🎯 Usage" section with:
1. How to start the application
2. Development mode command
3. Production mode command
4. Common use cases with examples

All commands must be copy-pasteable.
Format as markdown with code blocks."""
    
    def _create_api_prompt(self, context: str) -> str:
        """Create prompt for API section."""
        return f"""Generate the API Documentation section for a README.

CONTEXT:
{context[:1500]}

Generate a "## 📚 API Documentation" section with:
- Overview of API structure
- Authentication method (if any)
- Key endpoints with examples
- Request/response format

Format as markdown with code blocks for examples."""
    
    def _create_docker_prompt(self, context: str) -> str:
        """Create prompt for Docker section."""
        k = self.knowledge
        
        services_info = []
        for svc in k.services:
            services_info.append(f"- {svc.name}: {svc.purpose}")
            if svc.ports:
                services_info.append(f"  Ports: {', '.join(str(p) for p in svc.ports)}")
        
        return f"""Generate the Docker section for a README.

SERVICES:
{chr(10).join(services_info)}

ARCHITECTURE: {k.architecture_type}

USER DOCKER INFO: {self.state.user_answers.get('docker_purpose', 'Not specified')}

Generate a "## 🐳 Docker" section with:
1. Quick start with docker-compose
2. Explanation of each service
3. How to access the application
4. Useful docker commands
5. How to view logs

Format as markdown with code blocks."""
    
    def _create_structure_prompt(self, context: str) -> str:
        """Create prompt for project structure section."""
        k = self.knowledge
        
        return f"""Generate the Project Structure section for a README.

ENTRY POINTS: {k.entry_points}
BUILD SYSTEM: {k.build_system}

CONTEXT:
{context[:1000]}

Generate a "## 📁 Project Structure" section with:
- ASCII tree of main directories
- Brief description of each directory's purpose
- Key files explained

Format as markdown with code block for tree."""
    
    def _create_development_prompt(self, context: str) -> str:
        """Create prompt for development section."""
        k = self.knowledge
        
        dev_deps = [d.name for d in k.dev_dependencies[:10]]
        
        return f"""Generate the Development section for a README.

BUILD SYSTEM: {k.build_system}
DEV DEPENDENCIES: {dev_deps}
CI/CD: {k.ci_cd}

Generate a "## 👨‍💻 Development" section with:
- How to set up development environment
- Code style guidelines
- How to run in development mode
- Useful development commands

Format as markdown."""
    
    def _create_testing_prompt(self, context: str) -> str:
        """Create prompt for testing section."""
        k = self.knowledge
        
        test_deps = [d.name for d in k.dependencies + k.dev_dependencies 
                     if d.category == 'Testing']
        
        return f"""Generate the Testing section for a README.

TESTING TOOLS: {test_deps or ['Not detected']}
BUILD SYSTEM: {k.build_system}

Generate a "## 🧪 Testing" section with:
- How to run tests
- Test coverage information
- Types of tests included

Format as markdown with code blocks."""
    
    def _create_troubleshooting_prompt(self, context: str) -> str:
        """Create prompt for troubleshooting section."""
        k = self.knowledge
        
        common_issues = self.state.user_answers.get('common_issues', '')
        
        return f"""Generate the Troubleshooting section for a README.

BUILD SYSTEM: {k.build_system}
HAS DOCKER: {'Yes' if k.services else 'No'}
USER MENTIONED ISSUES: {common_issues or 'None'}

Generate a "## 🔧 Troubleshooting" section with:
- Common issues and solutions
- How to check logs
- Where to get help

Format as markdown."""
    
    def _create_contributing_prompt(self) -> str:
        """Create prompt for contributing section."""
        return """Generate a standard Contributing section for a README.

Generate a "## 🤝 Contributing" section with:
1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit PR

Keep it concise. Format as markdown."""
    
    def _create_license_prompt(self) -> str:
        """Create prompt for license section."""
        return """Generate a brief License section.

Generate a "## 📄 License" section.
Just mention MIT License or that the license is in the LICENSE file.
Keep it to 1-2 lines."""
    
    def _create_support_prompt(self) -> str:
        """Create prompt for support section."""
        return """Generate a Support section for a README.

Generate a "## 💬 Support" section with:
- How to report issues
- Where to ask questions
- How to contribute

Keep it brief. Format as markdown."""
    
    def _create_quick_start_prompt(self, context: str) -> str:
        """Create prompt for quick start (minimal style)."""
        k = self.knowledge
        
        return f"""Generate a minimal Quick Start README.

PROJECT: {k.name or self.state.project_name}
BUILD SYSTEM: {k.build_system}
HAS DOCKER: {'Yes' if k.services else 'No'}

SETUP GUIDE:
{k.setup_guide[:1000] if k.setup_guide else 'Not available'}

Generate a minimal README with:
1. Title
2. One-line description
3. Quick start commands (clone, install, run)
4. That's it!

Keep it under 30 lines. Format as markdown."""
    
    def _polish_readme(self, readme: str) -> Optional[str]:
        """Final polish pass on the README."""
        prompt = f"""Polish this README for consistency and quality.

README:
{readme[:8000]}

Tasks:
1. Ensure consistent formatting
2. Fix any markdown issues
3. Remove any placeholder text
4. Ensure all code blocks are properly formatted
5. Add table of contents if missing and README is long

Return the polished README. Keep all content, just improve formatting."""
        
        return self._call_model(prompt, timeout=120)


    def _phase_review_refine(self, draft: str) -> str:
        """Phase 7: Review and refine the README."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│  PHASE 7: Review & Refine                                        │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        current = draft
        
        while self.state.revision_count < 5:
            self.state.revision_count += 1
            
            # Show preview
            print(f"\n📄 README Preview (v{self.state.revision_count}):\n")
            print("─" * 60)
            lines = current.split('\n')[:40]
            print('\n'.join(lines))
            if len(current.split('\n')) > 40:
                print(f"\n... [{len(current.split(chr(10))) - 40} more lines]")
            print("─" * 60)
            
            print(f"\n📊 Stats: {len(current):,} chars, {current.count(chr(10)):,} lines")
            
            # Options
            print("\n❓ Options:\n")
            print("  1. ✅ ACCEPT - Save this README")
            print("  2. ✏️  REFINE - Request changes")
            print("  3. 🔄 REGENERATE - Generate fresh")
            print("  4. 👁️  VIEW FULL - See complete README")
            print("  5. 📝 EDIT SECTION - Regenerate specific section")
            
            choice = input("\nChoice (1-5): ").strip()
            
            if choice == '1':
                print("\n✅ README accepted!")
                return current
            
            elif choice == '2':
                feedback = input("\nWhat changes? ").strip()
                if feedback:
                    print("\n🔄 Refining...")
                    refined = self._refine_with_context(current, feedback)
                    if refined:
                        current = refined
                        print("✅ Refined!")
            
            elif choice == '3':
                print("\n🔄 Regenerating...")
                new_draft = self._phase_generate_with_context()
                if new_draft:
                    current = new_draft
            
            elif choice == '4':
                print("\n" + "=" * 60)
                print(current)
                print("=" * 60)
                input("\nPress Enter...")
            
            elif choice == '5':
                self._edit_section(current)
                # Rebuild from sections
                if self.state.generated_sections:
                    current = "\n\n".join(self.state.generated_sections.values())
        
        return current
    
    def _refine_with_context(self, readme: str, feedback: str) -> Optional[str]:
        """Refine README using vector store context."""
        # Get relevant context based on feedback
        context = self.analyzer.get_context_for_readme(feedback)
        
        prompt = f"""Refine this README based on user feedback.

CURRENT README:
{readme[:6000]}

USER FEEDBACK: {feedback}

RELEVANT PROJECT CONTEXT:
{context[:1500]}

Apply the changes while keeping everything else intact.
Return the complete updated README."""
        
        return self._call_model(prompt, timeout=180)
    
    def _edit_section(self, current: str):
        """Allow editing a specific section."""
        sections = list(self.state.generated_sections.keys())
        
        print("\n📝 Available sections:")
        for i, section in enumerate(sections, 1):
            print(f"  {i}. {section}")
        
        choice = input("\nWhich section to regenerate? ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(sections):
            section = sections[int(choice) - 1]
            print(f"\n🔄 Regenerating {section}...")
            
            context = self.analyzer.get_context_for_readme(section)
            new_content = self._generate_section(section, context)
            
            if new_content:
                self.state.generated_sections[section] = new_content
                print("✅ Section regenerated!")
    
    def _phase_save(self, readme: str):
        """Phase 8: Save the README."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│  PHASE 8: Saving                                                 │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        # Clean the output
        readme = self._clean_output(readme)
        
        # Save
        with open("README.md", 'w', encoding='utf-8') as f:
            f.write(readme)
        
        print(f"\n✅ Saved: README.md")
        print(f"   Size: {len(readme):,} characters")
        print(f"   Lines: {readme.count(chr(10)):,}")
        
        # Save debug info
        if self.debug:
            self.analyzer.save_knowledge("debug_knowledge.json")
            
            with open("debug_state.json", 'w') as f:
                json.dump({
                    'user_answers': self.state.user_answers,
                    'readme_style': self.state.readme_style,
                    'sections': list(self.state.generated_sections.keys())
                }, f, indent=2)
            
            print("   Debug files saved")
        
        # Cleanup
        if not self.debug:
            try:
                shutil.rmtree("cloned_repo")
                print("\n🧹 Cleaned up")
            except:
                pass
        
        print("\n" + "═" * 70)
        print("  🎉 README GENERATION COMPLETE!")
        print("═" * 70)
    
    def _call_model(self, prompt: str, timeout: int = 120) -> Optional[str]:
        """Call the LLM model."""
        try:
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt.encode('utf-8'),
                capture_output=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return result.stdout.decode('utf-8').strip()
            return None
            
        except subprocess.TimeoutExpired:
            return None
        except Exception as e:
            print(f"⚠️  Model error: {e}")
            return None
    
    def _clean_section(self, content: str) -> str:
        """Clean a generated section."""
        if not content:
            return ""
        
        # Remove code block wrappers
        if content.startswith('```markdown'):
            content = content[11:]
        elif content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        
        return content.strip()
    
    def _clean_output(self, output: str) -> str:
        """Clean the final output."""
        import re
        
        # Remove code block wrappers
        if output.startswith('```markdown'):
            output = output[11:]
        elif output.startswith('```'):
            output = output[3:]
        if output.endswith('```'):
            output = output[:-3]
        
        # Remove meta commentary
        output = re.sub(r'^Here\'s.*?:\s*\n', '', output, flags=re.IGNORECASE)
        output = re.sub(r'^I\'ve.*?:\s*\n', '', output, flags=re.IGNORECASE)
        
        return output.strip()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="README Generator v3.0 - Deep Understanding Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python readme_generator_v3.py --repo https://github.com/user/project
    python readme_generator_v3.py --repo https://github.com/user/project --model llama3.2:3b
    python readme_generator_v3.py --repo https://github.com/user/project --debug
        """
    )
    
    parser.add_argument('--repo', required=True, help='Git repository URL')
    parser.add_argument('--model', default='llama3.2:latest', help='Ollama model')
    parser.add_argument('--debug', action='store_true', help='Keep debug files')
    
    args = parser.parse_args()
    
    generator = ReadmeGeneratorV3(model=args.model, debug=args.debug)
    success = generator.run(args.repo)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
