#!/usr/bin/env python3
"""
Interactive README Generator
A multi-pass, conversational approach to generating comprehensive README files.
"""

import argparse
import os
import shutil
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field

from analyzer import EnhancedProjectAnalyzer


@dataclass
class ProjectContext:
    """Stores all gathered information about the project."""
    # Auto-detected
    repo_url: str = ""
    project_name: str = ""
    detected_languages: Dict[str, int] = field(default_factory=dict)
    detected_frameworks: List[str] = field(default_factory=list)
    detected_technologies: List[str] = field(default_factory=list)
    detected_databases: List[str] = field(default_factory=list)
    detected_features: List[str] = field(default_factory=list)
    has_docker: bool = False
    docker_services: List[str] = field(default_factory=list)
    api_endpoints: List[str] = field(default_factory=list)
    env_vars: List[str] = field(default_factory=list)
    complexity_score: int = 0
    
    # User-provided
    project_purpose: str = ""
    target_audience: str = ""
    key_features: List[str] = field(default_factory=list)
    deployment_info: str = ""
    special_requirements: str = ""
    additional_context: str = ""
    readme_style: str = "detailed"  # minimal, standard, detailed, comprehensive
    
    # Corrections from user
    confirmed_technologies: List[str] = field(default_factory=list)
    removed_technologies: List[str] = field(default_factory=list)
    added_technologies: List[str] = field(default_factory=list)
    
    # Code understanding
    code_summary: str = ""
    main_functionality: List[str] = field(default_factory=list)
    
    # Review feedback
    draft_feedback: str = ""
    revision_requests: List[str] = field(default_factory=list)


class InteractiveReadmeGenerator:
    """Multi-pass interactive README generator."""
    
    def __init__(self, model: str = "llama3.2:latest", debug: bool = False):
        self.model = model
        self.debug = debug
        self.analyzer: Optional[EnhancedProjectAnalyzer] = None
        self.context = ProjectContext()
        self.key_files: List[tuple] = []
        
    def run(self, repo_url: str) -> bool:
        """Main entry point - runs the full interactive generation process."""
        self.context.repo_url = repo_url
        self.context.project_name = repo_url.split('/')[-1].replace('.git', '')
        
        print("\n" + "=" * 70)
        print("🚀 INTERACTIVE README GENERATOR")
        print("=" * 70)
        print(f"\n📂 Repository: {repo_url}")
        print(f"🧠 Model: {self.model}")
        print("\nThis tool will guide you through creating a perfect README.")
        print("It will analyze your project, ask questions, and refine the output.\n")
        
        # Phase 1: Clone and Analyze
        if not self._phase_clone_and_analyze():
            return False
        
        # Phase 2: Present Findings & Confirm
        self._phase_present_findings()
        
        # Phase 3: Ask Clarifying Questions
        self._phase_ask_questions()
        
        # Phase 4: Deep Code Understanding
        self._phase_understand_code()
        
        # Phase 5: Choose README Style
        self._phase_choose_style()
        
        # Phase 6: Generate Draft
        draft = self._phase_generate_draft()
        if not draft:
            return False
        
        # Phase 7: Review and Refine Loop
        final_readme = self._phase_review_and_refine(draft)
        
        # Phase 8: Save and Cleanup
        self._phase_save_and_cleanup(final_readme)
        
        return True
    
    def _phase_clone_and_analyze(self) -> bool:
        """Phase 1: Clone repository and perform initial analysis."""
        print("\n" + "-" * 50)
        print("📥 PHASE 1: Cloning & Analyzing Repository")
        print("-" * 50)
        
        # Clone
        from docker import clone_repo
        if not clone_repo(self.context.repo_url):
            return False
        
        # Analyze
        print("\n🔍 Performing deep project analysis...")
        self.analyzer = EnhancedProjectAnalyzer()
        self.analyzer.perform_full_analysis()
        
        # Store detected info in context
        self.context.detected_languages = self.analyzer.project_data.get('languages', {})
        self.context.detected_frameworks = self.analyzer.project_data.get('frameworks', [])
        self.context.detected_technologies = self.analyzer.project_data.get('technologies', [])
        self.context.detected_databases = self.analyzer.project_data.get('databases', [])
        self.context.detected_features = self.analyzer.project_data.get('features', [])
        self.context.has_docker = self.analyzer.project_data.get('has_docker', False)
        self.context.docker_services = self.analyzer.project_data.get('docker_services', [])
        self.context.api_endpoints = self.analyzer.project_data.get('api_endpoints', [])
        self.context.env_vars = self.analyzer.project_data.get('env_example_vars', [])
        self.context.complexity_score = self.analyzer.project_data.get('complexity_score', 0)
        
        # Get key files
        self.key_files = self.analyzer.get_key_files()
        
        print("✅ Analysis complete!")
        return True
    
    def _phase_present_findings(self):
        """Phase 2: Present what was detected and ask for confirmation."""
        print("\n" + "-" * 50)
        print("📊 PHASE 2: Analysis Results")
        print("-" * 50)
        
        print(f"\n🏷️  Project Name: {self.context.project_name}")
        print(f"📈 Complexity Score: {self.context.complexity_score} ({self.analyzer.project_data.get('setup_difficulty', 'Unknown')})")
        
        # Languages
        if self.context.detected_languages:
            print(f"\n💻 Languages Detected:")
            for lang, count in list(self.context.detected_languages.items())[:5]:
                print(f"   • {lang}: {count} files")
        
        # Frameworks
        if self.context.detected_frameworks:
            print(f"\n🛠️  Frameworks Detected:")
            for fw in self.context.detected_frameworks[:8]:
                print(f"   • {fw}")
        
        # Technologies
        if self.context.detected_technologies:
            print(f"\n🔧 Technologies Detected:")
            for tech in self.context.detected_technologies[:10]:
                print(f"   • {tech}")
        
        # Docker
        if self.context.has_docker:
            print(f"\n🐳 Docker Configuration:")
            print(f"   Services: {', '.join(self.context.docker_services) if self.context.docker_services else 'Standard container'}")
            if self.context.detected_databases:
                print(f"   Databases: {', '.join(self.context.detected_databases)}")
        
        # API Endpoints
        if self.context.api_endpoints:
            print(f"\n🌐 API Endpoints Detected: {len(self.context.api_endpoints)}")
            for endpoint in self.context.api_endpoints[:5]:
                print(f"   • {endpoint}")
            if len(self.context.api_endpoints) > 5:
                print(f"   ... and {len(self.context.api_endpoints) - 5} more")
        
        # Features
        if self.context.detected_features:
            print(f"\n✨ Features Detected:")
            for feature in self.context.detected_features[:8]:
                print(f"   • {feature}")
        
        # Confirm technologies
        print("\n" + "-" * 30)
        self._confirm_technologies()
    
    def _confirm_technologies(self):
        """Ask user to confirm/correct detected technologies."""
        print("\n🔍 Please review the detected technologies:")
        
        all_tech = list(set(
            self.context.detected_frameworks + 
            self.context.detected_technologies
        ))
        
        if all_tech:
            print(f"\nDetected: {', '.join(all_tech[:15])}")
            
            response = input("\n❓ Is this correct? (yes/no/edit): ").strip().lower()
            
            if response in ['no', 'n', 'edit', 'e']:
                print("\nEnter technologies to REMOVE (comma-separated, or press Enter to skip):")
                remove = input("Remove: ").strip()
                if remove:
                    self.context.removed_technologies = [t.strip() for t in remove.split(',')]
                
                print("\nEnter technologies to ADD (comma-separated, or press Enter to skip):")
                add = input("Add: ").strip()
                if add:
                    self.context.added_technologies = [t.strip() for t in add.split(',')]
                
                # Update the lists
                for tech in self.context.removed_technologies:
                    if tech in self.context.detected_frameworks:
                        self.context.detected_frameworks.remove(tech)
                    if tech in self.context.detected_technologies:
                        self.context.detected_technologies.remove(tech)
                
                self.context.detected_technologies.extend(self.context.added_technologies)
                print("✅ Technologies updated!")
        
        self.context.confirmed_technologies = list(set(
            self.context.detected_frameworks + 
            self.context.detected_technologies
        ))


    def _phase_ask_questions(self):
        """Phase 3: Ask clarifying questions about the project."""
        print("\n" + "-" * 50)
        print("❓ PHASE 3: Tell Me About Your Project")
        print("-" * 50)
        print("\nI'll ask a few questions to create a better README.\n")
        
        # Question 1: Project Purpose
        print("1️⃣  What is the main PURPOSE of this project?")
        print("   (What problem does it solve? What does it do?)")
        self.context.project_purpose = input("\n   Your answer: ").strip()
        
        # Question 2: Target Audience
        print("\n2️⃣  Who is the TARGET AUDIENCE?")
        print("   Options: developers, end-users, both, data-scientists, devops, etc.")
        self.context.target_audience = input("\n   Your answer: ").strip()
        
        # Question 3: Key Features
        print("\n3️⃣  What are the KEY FEATURES you want to highlight?")
        print("   (Comma-separated list, or press Enter to use auto-detected)")
        features_input = input("\n   Your answer: ").strip()
        if features_input:
            self.context.key_features = [f.strip() for f in features_input.split(',')]
        else:
            self.context.key_features = self.context.detected_features
        
        # Question 4: Deployment
        print("\n4️⃣  How is this project typically DEPLOYED?")
        print("   (e.g., Docker, cloud service, local, npm package, pip install, etc.)")
        self.context.deployment_info = input("\n   Your answer: ").strip()
        
        # Question 5: Special Requirements
        print("\n5️⃣  Any SPECIAL REQUIREMENTS or prerequisites?")
        print("   (API keys, external services, specific OS, etc.)")
        self.context.special_requirements = input("\n   Your answer: ").strip()
        
        # Question 6: Additional Context
        print("\n6️⃣  Anything else I should know about the project?")
        print("   (Unique selling points, important notes, etc.)")
        self.context.additional_context = input("\n   Your answer: ").strip()
        
        print("\n✅ Thank you! I have a much better understanding now.")
    
    def _phase_understand_code(self):
        """Phase 4: Use the model to deeply understand the code."""
        print("\n" + "-" * 50)
        print("🧠 PHASE 4: Deep Code Understanding")
        print("-" * 50)
        print("\nAnalyzing source code to understand functionality...")
        
        # Prepare code samples for analysis
        code_samples = self._get_code_samples()
        
        if not code_samples:
            print("⚠️  No significant source code found to analyze.")
            return
        
        # Create a prompt for code understanding
        understanding_prompt = self._create_understanding_prompt(code_samples)
        
        # Get model's understanding
        print("🤖 Asking the model to analyze the code...")
        response = self._call_model(understanding_prompt, timeout=300)
        
        if response:
            self.context.code_summary = response
            print("✅ Code analysis complete!")
            
            # Show summary and ask for corrections
            print("\n📝 Here's what I understand about the code:\n")
            print("-" * 40)
            # Show first 500 chars of summary
            preview = response[:800] + "..." if len(response) > 800 else response
            print(preview)
            print("-" * 40)
            
            correct = input("\n❓ Is this understanding correct? (yes/no): ").strip().lower()
            if correct in ['no', 'n']:
                print("\nPlease provide corrections or clarifications:")
                correction = input("Your input: ").strip()
                if correction:
                    self.context.code_summary += f"\n\nUser Correction: {correction}"
        else:
            print("⚠️  Could not analyze code. Continuing with detected information.")
    
    def _get_code_samples(self) -> str:
        """Get representative code samples for analysis."""
        samples = []
        source_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.php', '.rb']
        
        # Get entry point files first
        entry_points = ['main.py', 'app.py', 'index.js', 'server.js', 'main.go', 'main.rs']
        
        for entry in entry_points:
            for filename, content in self.key_files:
                if filename.endswith(entry):
                    samples.append(f"=== {filename} ===\n{content[:2000]}")
                    break
        
        # Add other source files
        for filename, content in self.key_files:
            if any(filename.endswith(ext) for ext in source_extensions):
                if not any(filename in s for s in samples):
                    samples.append(f"=== {filename} ===\n{content[:1500]}")
                    if len(samples) >= 6:  # Limit to 6 files
                        break
        
        return "\n\n".join(samples)
    
    def _create_understanding_prompt(self, code_samples: str) -> str:
        """Create prompt for code understanding."""
        return f"""Analyze this codebase and provide a clear, concise summary of:

1. MAIN FUNCTIONALITY: What does this code actually do? (be specific)
2. KEY COMPONENTS: What are the main modules/classes/functions?
3. DATA FLOW: How does data flow through the application?
4. EXTERNAL INTEGRATIONS: What external services/APIs does it use?
5. UNIQUE ASPECTS: What makes this implementation interesting or unique?

Project Context:
- Name: {self.context.project_name}
- Languages: {', '.join(self.context.detected_languages.keys())}
- Frameworks: {', '.join(self.context.detected_frameworks)}
- User says it's for: {self.context.project_purpose or 'Not specified'}

CODE TO ANALYZE:
{code_samples}

Provide a clear, technical summary that would help write accurate documentation.
Focus on WHAT the code does, not just what technologies it uses.
Be specific about functionality, not generic."""
    
    def _phase_choose_style(self):
        """Phase 5: Let user choose README style."""
        print("\n" + "-" * 50)
        print("🎨 PHASE 5: Choose README Style")
        print("-" * 50)
        
        print("\nWhat style of README would you like?\n")
        print("1️⃣  MINIMAL    - Quick start only, bare essentials")
        print("2️⃣  STANDARD   - Balanced, covers main topics")
        print("3️⃣  DETAILED   - Comprehensive with examples (recommended)")
        print("4️⃣  COMPREHENSIVE - Everything including API docs, architecture, etc.")
        
        choice = input("\nYour choice (1-4, or press Enter for detailed): ").strip()
        
        style_map = {
            '1': 'minimal',
            '2': 'standard',
            '3': 'detailed',
            '4': 'comprehensive'
        }
        
        self.context.readme_style = style_map.get(choice, 'detailed')
        print(f"\n✅ Selected style: {self.context.readme_style.upper()}")
    
    def _phase_generate_draft(self) -> Optional[str]:
        """Phase 6: Generate the README draft."""
        print("\n" + "-" * 50)
        print("📝 PHASE 6: Generating README Draft")
        print("-" * 50)
        print("\n🤖 Creating your README based on all gathered information...")
        print("   This may take a minute or two...\n")
        
        # Create the comprehensive prompt
        prompt = self._create_generation_prompt()
        
        # Generate with longer timeout for complex projects
        timeout = 600 if self.context.complexity_score > 50 else 400
        
        draft = self._call_model(prompt, timeout=timeout)
        
        if draft:
            # Clean up the output
            draft = self._clean_readme_output(draft)
            print("✅ Draft generated!")
            return draft
        else:
            print("❌ Failed to generate draft.")
            return None


    def _create_generation_prompt(self) -> str:
        """Create the comprehensive generation prompt with all context."""
        
        # Build file contents section
        file_contents = ""
        config_files = []
        source_files = []
        
        for filename, content in self.key_files:
            if any(filename.endswith(ext) for ext in ['.json', '.txt', '.toml', '.yml', '.yaml', 'Dockerfile', '.md']):
                config_files.append((filename, content[:2000]))
            else:
                source_files.append((filename, content[:1500]))
        
        if config_files:
            file_contents += "\n=== CONFIGURATION FILES ===\n"
            for filename, content in config_files[:5]:
                file_contents += f"\n--- {filename} ---\n{content}\n"
        
        if source_files:
            file_contents += "\n=== SOURCE FILES ===\n"
            for filename, content in source_files[:4]:
                file_contents += f"\n--- {filename} ---\n{content}\n"
        
        # Style-specific instructions
        style_instructions = {
            'minimal': """
Create a MINIMAL README with only:
- Project title and one-line description
- Quick install command
- Basic usage example
- License
Keep it under 100 lines.""",
            
            'standard': """
Create a STANDARD README with:
- Project title and description
- Features list (bullet points)
- Installation steps
- Basic usage
- Configuration (if needed)
- Contributing section
- License""",
            
            'detailed': """
Create a DETAILED README with:
- Compelling project description
- Table of contents
- Comprehensive features list
- Tech stack section
- Prerequisites
- Step-by-step installation
- Configuration guide
- Usage examples with code
- API documentation (if applicable)
- Docker instructions (if applicable)
- Project structure
- Development guide
- Testing instructions
- Contributing guidelines
- License and support""",
            
            'comprehensive': """
Create a COMPREHENSIVE README with EVERYTHING:
- Eye-catching header with badges
- Detailed project description
- Table of contents
- Screenshots/demo section placeholder
- Complete features list with descriptions
- Full tech stack breakdown
- System requirements
- Detailed prerequisites
- Multiple installation methods
- Complete configuration guide
- Extensive usage examples
- Full API documentation
- Docker/deployment guide
- Architecture overview
- Project structure with descriptions
- Development setup
- Testing guide
- Troubleshooting section
- FAQ section
- Roadmap placeholder
- Contributing guidelines
- Code of conduct reference
- License
- Acknowledgments
- Support/contact info"""
        }
        
        prompt = f"""You are creating a README.md file for a software project. You have been given comprehensive information about the project from both automated analysis AND direct user input.

=== PROJECT INFORMATION ===
Name: {self.context.project_name}
Repository: {self.context.repo_url}

=== USER-PROVIDED CONTEXT (IMPORTANT - USE THIS!) ===
Project Purpose: {self.context.project_purpose or 'Not specified - infer from code'}
Target Audience: {self.context.target_audience or 'Developers'}
Key Features to Highlight: {', '.join(self.context.key_features) if self.context.key_features else 'Use detected features'}
Deployment Method: {self.context.deployment_info or 'Infer from project structure'}
Special Requirements: {self.context.special_requirements or 'None specified'}
Additional Context: {self.context.additional_context or 'None'}

=== DETECTED INFORMATION ===
Main Language: {list(self.context.detected_languages.keys())[0] if self.context.detected_languages else 'Unknown'}
All Languages: {', '.join(self.context.detected_languages.keys()) if self.context.detected_languages else 'Unknown'}
Frameworks: {', '.join(self.context.detected_frameworks) if self.context.detected_frameworks else 'None detected'}
Technologies: {', '.join(self.context.confirmed_technologies[:15]) if self.context.confirmed_technologies else 'None detected'}
Databases: {', '.join(self.context.detected_databases) if self.context.detected_databases else 'None'}
Has Docker: {'Yes' if self.context.has_docker else 'No'}
Docker Services: {', '.join(self.context.docker_services) if self.context.docker_services else 'N/A'}
API Endpoints: {len(self.context.api_endpoints)} detected
Environment Variables: {', '.join(self.context.env_vars[:10]) if self.context.env_vars else 'None detected'}
Complexity: {self.context.complexity_score} points ({self.analyzer.project_data.get('setup_difficulty', 'Unknown')})

=== CODE UNDERSTANDING ===
{self.context.code_summary if self.context.code_summary else 'No deep code analysis available'}

=== COMMANDS DETECTED ===
Install: {self.analyzer.project_data.get('install_cmd', 'Not detected')}
Run: {self.analyzer.project_data.get('run_cmd', 'Not detected')}
Dev: {self.analyzer.project_data.get('dev_cmd', 'Not detected')}
Test: {self.analyzer.project_data.get('test_cmd', 'Not detected')}
Build: {self.analyzer.project_data.get('build_cmd', 'Not detected')}

=== PROJECT FILES ===
{file_contents}

=== README STYLE REQUESTED ===
{style_instructions.get(self.context.readme_style, style_instructions['detailed'])}

=== CRITICAL INSTRUCTIONS ===
1. USE THE USER-PROVIDED CONTEXT - they know their project best
2. Be ACCURATE - only include information you can verify or that the user provided
3. Make all commands COPY-PASTEABLE and correct
4. Write a compelling description based on the project purpose provided
5. Highlight the features the user mentioned
6. Include the deployment method they specified
7. Mention special requirements they noted
8. DO NOT include placeholder text like [Add description here]
9. DO NOT make up features or functionality not evident in the code
10. If something is unclear, be honest about it rather than guessing
11. Use proper markdown formatting
12. Make it professional and well-organized

Generate the README now:"""
        
        return prompt
    
    def _phase_review_and_refine(self, draft: str) -> str:
        """Phase 7: Show draft and allow refinement."""
        print("\n" + "-" * 50)
        print("🔍 PHASE 7: Review & Refine")
        print("-" * 50)
        
        current_draft = draft
        iteration = 0
        max_iterations = 5
        
        while iteration < max_iterations:
            iteration += 1
            
            # Show the draft
            print(f"\n📄 Current README Draft (Revision {iteration}):\n")
            print("=" * 60)
            print(current_draft[:3000])
            if len(current_draft) > 3000:
                print(f"\n... [{len(current_draft) - 3000} more characters] ...")
            print("=" * 60)
            
            print(f"\n📊 Draft Statistics:")
            print(f"   • Length: {len(current_draft):,} characters")
            print(f"   • Lines: {current_draft.count(chr(10)):,}")
            
            # Ask for feedback
            print("\n❓ What would you like to do?\n")
            print("1️⃣  ACCEPT  - Save this README as-is")
            print("2️⃣  REFINE  - Request specific changes")
            print("3️⃣  REGENERATE - Start fresh with different approach")
            print("4️⃣  VIEW FULL - See the complete README")
            
            choice = input("\nYour choice (1-4): ").strip()
            
            if choice == '1':
                print("\n✅ README accepted!")
                return current_draft
            
            elif choice == '2':
                print("\n📝 What changes would you like?")
                print("   (Be specific: 'make description shorter', 'add more examples', etc.)")
                feedback = input("\nYour feedback: ").strip()
                
                if feedback:
                    self.context.revision_requests.append(feedback)
                    print("\n🔄 Refining README based on your feedback...")
                    
                    refined = self._refine_readme(current_draft, feedback)
                    if refined:
                        current_draft = refined
                        print("✅ Refinement complete!")
                    else:
                        print("⚠️  Refinement failed, keeping current version.")
            
            elif choice == '3':
                print("\n🔄 Regenerating README with fresh approach...")
                new_draft = self._call_model(self._create_generation_prompt(), timeout=400)
                if new_draft:
                    current_draft = self._clean_readme_output(new_draft)
                    print("✅ New draft generated!")
                else:
                    print("⚠️  Regeneration failed, keeping current version.")
            
            elif choice == '4':
                print("\n" + "=" * 60)
                print("FULL README:")
                print("=" * 60)
                print(current_draft)
                print("=" * 60)
                input("\nPress Enter to continue...")
            
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
        
        print(f"\n⚠️  Maximum iterations ({max_iterations}) reached. Saving current version.")
        return current_draft
    
    def _refine_readme(self, current_draft: str, feedback: str) -> Optional[str]:
        """Refine the README based on user feedback."""
        prompt = f"""You are refining a README.md based on user feedback.

CURRENT README:
{current_draft}

USER FEEDBACK:
{feedback}

INSTRUCTIONS:
1. Apply the user's requested changes
2. Keep everything else the same
3. Maintain proper markdown formatting
4. Return the COMPLETE updated README

Generate the refined README now:"""
        
        return self._call_model(prompt, timeout=300)
    
    def _phase_save_and_cleanup(self, readme_content: str):
        """Phase 8: Save the README and cleanup."""
        print("\n" + "-" * 50)
        print("💾 PHASE 8: Saving & Cleanup")
        print("-" * 50)
        
        # Save README
        output_path = "README.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"\n✅ README saved to: {output_path}")
        print(f"   Size: {len(readme_content):,} characters")
        print(f"   Lines: {readme_content.count(chr(10)):,}")
        
        # Save context for debugging
        if self.debug:
            context_path = "readme_context.json"
            with open(context_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'project_name': self.context.project_name,
                    'repo_url': self.context.repo_url,
                    'detected_languages': self.context.detected_languages,
                    'detected_frameworks': self.context.detected_frameworks,
                    'detected_technologies': self.context.detected_technologies,
                    'user_purpose': self.context.project_purpose,
                    'target_audience': self.context.target_audience,
                    'key_features': self.context.key_features,
                    'readme_style': self.context.readme_style,
                    'revision_requests': self.context.revision_requests,
                    'complexity_score': self.context.complexity_score
                }, f, indent=2)
            print(f"   Debug context saved to: {context_path}")
        
        # Cleanup
        if not self.debug:
            try:
                shutil.rmtree("cloned_repo")
                print("\n🧹 Cleaned up temporary files.")
            except:
                pass
        else:
            print("\n🐛 Debug mode: Repository preserved in 'cloned_repo/'")
        
        print("\n" + "=" * 50)
        print("🎉 README GENERATION COMPLETE!")
        print("=" * 50)


    def _call_model(self, prompt: str, timeout: int = 300) -> Optional[str]:
        """Call the Ollama model with the given prompt."""
        try:
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt.encode('utf-8'),
                capture_output=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                error = result.stderr.decode() if result.stderr else "Unknown error"
                print(f"⚠️  Model error: {error[:200]}")
                return None
            
            output = result.stdout.decode('utf-8').strip()
            return output
            
        except subprocess.TimeoutExpired:
            print(f"⚠️  Model timed out after {timeout}s")
            return None
        except FileNotFoundError:
            print("❌ Ollama not found. Please install Ollama and ensure it's running.")
            return None
        except Exception as e:
            print(f"⚠️  Error calling model: {e}")
            return None
    
    def _clean_readme_output(self, output: str) -> str:
        """Clean up the model output to get clean README content."""
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
        
        # Find where the actual README starts (first # heading)
        lines = output.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#') and not stripped.startswith('##'):
                start_idx = i
                break
        
        if start_idx > 0:
            output = '\n'.join(lines[start_idx:])
        
        # Remove common artifacts
        output = re.sub(r'^\s*Here\'s.*?:\s*\n', '', output, flags=re.IGNORECASE)
        output = re.sub(r'^\s*I\'ve created.*?:\s*\n', '', output, flags=re.IGNORECASE)
        
        return output.strip()


def main():
    """Main entry point for the interactive README generator."""
    parser = argparse.ArgumentParser(
        description="Interactive README Generator - Creates perfect READMEs through conversation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python interactive_readme.py --repo https://github.com/user/project
    python interactive_readme.py --repo https://github.com/user/project --model llama3.2:3b
    python interactive_readme.py --repo https://github.com/user/project --debug
        """
    )
    
    parser.add_argument('--repo', required=True, help='Git repository URL to analyze')
    parser.add_argument('--model', default='llama3.2:latest', 
                       help='Ollama model to use (default: llama3.2:latest)')
    parser.add_argument('--debug', action='store_true',
                       help='Keep debug files and enable verbose output')
    
    args = parser.parse_args()
    
    generator = InteractiveReadmeGenerator(model=args.model, debug=args.debug)
    success = generator.run(args.repo)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
