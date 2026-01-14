"""
Nova Section Generator
Generates each README section with targeted context for maximum quality.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from scanner import ProjectContext, RouteInfo


@dataclass
class Section:
    """README section definition."""
    id: str
    title: str
    required: bool
    order: int
    condition: str = ""  # Condition for inclusion


class SectionGenerator:
    """
    Generates README sections one by one with targeted context.
    Each section gets only the relevant information for best quality.
    """

    # Section definitions
    SECTIONS = [
        Section("header", "Header & Badges", required=True, order=1),
        Section("description", "Description", required=True, order=2),
        Section("toc", "Table of Contents", required=False, order=3),
        Section("features", "Features", required=True, order=4),
        Section("quick_start", "Quick Start", required=True, order=5),
        Section("prerequisites", "Prerequisites", required=True, order=6),
        Section("installation", "Installation", required=True, order=7),
        Section("configuration", "Configuration", required=False, order=8, condition="has_env_vars"),
        Section("usage", "Usage", required=True, order=9),
        Section("api", "API Documentation", required=False, order=10, condition="has_routes"),
        Section("docker", "Docker", required=False, order=11, condition="has_docker"),
        Section("database", "Database", required=False, order=12, condition="has_database"),
        Section("testing", "Testing", required=False, order=13, condition="has_tests"),
        Section("project_structure", "Project Structure", required=False, order=14),
        Section("development", "Development", required=False, order=15),
        Section("troubleshooting", "Troubleshooting", required=False, order=16, condition="is_complex"),
        Section("contributing", "Contributing", required=True, order=17),
        Section("license", "License", required=True, order=18),
    ]

    def __init__(self, context: ProjectContext):
        self.context = context

    def get_sections_to_generate(self) -> List[Section]:
        """Get list of sections to generate based on project context."""
        sections = []

        for section in self.SECTIONS:
            if section.required:
                sections.append(section)
            elif self._check_condition(section.condition):
                sections.append(section)

        return sorted(sections, key=lambda s: s.order)

    def _check_condition(self, condition: str) -> bool:
        """Check if a condition is met."""
        if not condition:
            return True

        conditions = {
            "has_env_vars": len(self.context.env_vars) > 0,
            "has_routes": len(self.context.routes) > 0,
            "has_docker": self.context.has_docker,
            "has_database": len(self.context.databases) > 0,
            "has_tests": len(self.context.tests) > 0,
            "is_complex": self.context.complexity_score > 40,
        }

        return conditions.get(condition, False)

    def build_section_context(self, section_id: str) -> Dict[str, Any]:
        """Build targeted context for a specific section."""
        ctx = self.context

        # Common context
        base = {
            "project_name": ctx.name or ctx.repo_url.split('/')[-1],
            "repo_url": ctx.repo_url,
            "primary_language": ctx.primary_language,
            "frameworks": ctx.frameworks,
        }

        # Section-specific context
        if section_id == "header":
            return {
                **base,
                "version": ctx.version,
                "license": ctx.license,
                "description": ctx.description,
            }

        elif section_id == "description":
            return {
                **base,
                "description": ctx.description,
                "features": ctx.features[:10],
                "architecture_type": ctx.architecture_type,
                "main_purpose": self._infer_purpose(),
            }

        elif section_id == "features":
            return {
                **base,
                "features": ctx.features,
                "routes_count": len(ctx.routes),
                "integrations": ctx.integrations,
                "databases": ctx.databases,
                "has_docker": ctx.has_docker,
                "has_tests": len(ctx.tests) > 0,
            }

        elif section_id == "quick_start":
            return {
                **base,
                "install_commands": ctx.install_commands,
                "run_commands": ctx.run_commands,
                "has_docker": ctx.has_docker,
                "docker_commands": ctx.docker_commands,
                "ports": self._get_main_ports(),
            }

        elif section_id == "prerequisites":
            return {
                **base,
                "languages": ctx.languages,
                "dependencies_count": len(ctx.dependencies),
                "has_docker": ctx.has_docker,
                "databases": ctx.databases,
                "key_dependencies": self._get_key_dependencies(),
            }

        elif section_id == "installation":
            return {
                **base,
                "install_commands": ctx.install_commands,
                "has_env_vars": len(ctx.env_vars) > 0,
                "env_vars": ctx.env_vars[:10],
                "key_files": self._get_config_file_content(),
            }

        elif section_id == "configuration":
            return {
                **base,
                "env_vars": ctx.env_vars,
                "configs": self._get_config_info(),
                "has_docker": ctx.has_docker,
            }

        elif section_id == "usage":
            return {
                **base,
                "run_commands": ctx.run_commands,
                "dev_commands": ctx.dev_commands,
                "entry_points": ctx.entry_points,
                "main_functions": self._get_main_functions(),
                "code_examples": ctx.code_examples[:5],
                "ports": self._get_main_ports(),
            }

        elif section_id == "api":
            return {
                **base,
                "routes": self._format_routes(),
                "route_count": len(ctx.routes),
                "has_auth": any('auth' in f.lower() for f in ctx.features),
            }

        elif section_id == "docker":
            return {
                **base,
                "docker_services": ctx.docker_services,
                "docker_commands": ctx.docker_commands,
                "ports": self._get_main_ports(),
                "databases": ctx.databases,
            }

        elif section_id == "database":
            return {
                **base,
                "databases": ctx.databases,
                "db_models": ctx.db_models[:10],
                "has_migrations": any('migration' in f.lower() for f in ctx.features),
            }

        elif section_id == "testing":
            return {
                **base,
                "test_commands": ctx.test_commands,
                "test_framework": ctx.test_framework,
                "test_count": len(ctx.tests),
                "test_types": list(set(t.test_type for t in ctx.tests)),
            }

        elif section_id == "project_structure":
            return {
                **base,
                "directory_structure": ctx.directory_structure,
                "main_modules": ctx.main_modules,
                "entry_points": ctx.entry_points,
            }

        elif section_id == "development":
            return {
                **base,
                "dev_commands": ctx.dev_commands,
                "test_commands": ctx.test_commands,
                "build_commands": ctx.build_commands,
                "dev_dependencies": [d.name for d in ctx.dev_dependencies[:10]],
            }

        elif section_id == "troubleshooting":
            return {
                **base,
                "common_issues": self._get_common_issues(),
                "databases": ctx.databases,
                "has_docker": ctx.has_docker,
            }

        elif section_id == "contributing":
            return {
                **base,
                "test_commands": ctx.test_commands,
                "has_tests": len(ctx.tests) > 0,
            }

        elif section_id == "license":
            return {
                **base,
                "license": ctx.license or "MIT",
                "author": ctx.author,
            }

        return base

    def _infer_purpose(self) -> str:
        """Infer the main purpose of the project."""
        ctx = self.context

        if len(ctx.routes) > 10:
            return "API service"
        elif ctx.has_docker and len(ctx.docker_services) > 3:
            return "microservices application"
        elif any('cli' in f.lower() for f in ctx.features):
            return "command-line tool"
        elif 'react' in str(ctx.frameworks).lower():
            return "React application"
        elif 'fastapi' in str(ctx.frameworks).lower():
            return "FastAPI backend service"
        elif 'flask' in str(ctx.frameworks).lower():
            return "Flask web application"
        elif 'django' in str(ctx.frameworks).lower():
            return "Django web application"

        return "software application"

    def _get_key_dependencies(self) -> List[Dict]:
        """Get key dependencies with descriptions."""
        key_deps = []
        categories = ['web framework', 'database', 'authentication', 'testing']

        for dep in self.context.dependencies:
            if dep.category in categories:
                key_deps.append({
                    'name': dep.name,
                    'version': dep.version,
                    'category': dep.category
                })

        return key_deps[:15]

    def _get_config_file_content(self) -> str:
        """Get relevant config file content."""
        result = ""

        for config in self.context.configs[:3]:
            result += f"\n--- {config.file_path} ---\n"
            result += config.content[:2000]

        return result

    def _get_config_info(self) -> List[Dict]:
        """Get configuration information."""
        configs = []

        for config in self.context.configs:
            configs.append({
                'file': config.file_path,
                'type': config.file_type,
                'env_vars': config.env_vars[:10],
                'ports': config.ports,
            })

        return configs[:5]

    def _get_main_functions(self) -> List[Dict]:
        """Get main/important functions."""
        main_funcs = []

        for func in self.context.functions:
            if func.is_public and func.docstring:
                main_funcs.append({
                    'name': func.name,
                    'file': func.file_path,
                    'docstring': func.docstring[:200],
                    'parameters': func.parameters,
                    'snippet': func.code_snippet[:500] if func.code_snippet else ""
                })

        return main_funcs[:10]

    def _format_routes(self) -> List[Dict]:
        """Format routes for documentation."""
        formatted = []

        for route in self.context.routes:
            formatted.append({
                'method': route.method,
                'path': route.path,
                'docstring': route.docstring,
                'file': route.file_path,
                'snippet': route.code_snippet[:400] if route.code_snippet else ""
            })

        return formatted[:20]

    def _get_main_ports(self) -> List[str]:
        """Get main ports used."""
        ports = set()

        for config in self.context.configs:
            ports.update(config.ports)

        for service in self.context.docker_services:
            if 'ports' in service:
                for port in service['ports']:
                    if isinstance(port, str):
                        # Handle "3000:3000" format
                        ports.add(port.split(':')[0])

        return list(ports)[:5]

    def _get_common_issues(self) -> List[Dict]:
        """Get common issues based on project type."""
        issues = []

        if self.context.has_docker:
            issues.append({
                'problem': 'Docker containers not starting',
                'solution': 'Check if ports are available and Docker daemon is running'
            })

        if self.context.databases:
            issues.append({
                'problem': 'Database connection failed',
                'solution': 'Verify database credentials in .env and ensure database server is running'
            })

        if len(self.context.env_vars) > 0:
            issues.append({
                'problem': 'Missing environment variables',
                'solution': 'Copy .env.example to .env and fill in required values'
            })

        issues.append({
            'problem': 'Dependencies not installing',
            'solution': f'Make sure you have the correct version of {self.context.primary_language} installed'
        })

        return issues


def build_section_prompt(section_id: str, section_context: Dict[str, Any]) -> str:
    """Build a prompt for generating a specific section."""

    prompts = {
        "header": """Generate the README header section with:
- Project title: {project_name}
- 2-4 badges (license: {license}, version: {version} if available)
- One compelling tagline that captures what this project does

Format:
# Project Name

[![Badge](url)]...

> Compelling one-liner tagline

---

Context:
{section_context}
""",

        "description": """Generate the project description section.

Create 2-3 paragraphs that:
1. Explain WHAT this project does (be specific, not generic)
2. Explain WHO it's for and WHY they'd use it
3. Highlight key benefits (not just features)

Project info:
- Name: {project_name}
- Type: {main_purpose}
- Key features: {features}
- Frameworks: {frameworks}

Write like a human developer explaining to a colleague. Be specific and avoid buzzwords.
""",

        "features": """Generate the Features section.

Create a bullet list of features based on these detected capabilities:
{features}

Also include:
- {routes_count} API endpoints (if applicable)
- Integrations: {integrations}
- Database support: {databases}
- Docker support: {has_docker}

Format with emojis for visual appeal. Group related features together.
Be specific about what each feature actually does.
""",

        "quick_start": """Generate the Quick Start section.

This is the MOST IMPORTANT section - get users to "it works!" in 3-5 commands.

Available commands:
- Install: {install_commands}
- Run: {run_commands}
- Docker: {docker_commands}
- Ports: {ports}

Format:
## 🚀 Quick Start

```bash
# Clone and install
git clone {repo_url}
cd {project_name}
[install command]

# Run
[run command]
```

Then show expected output or URL to visit.
""",

        "prerequisites": """Generate the Prerequisites section.

Based on:
- Primary language: {primary_language}
- All languages: {languages}
- Key dependencies: {key_dependencies}
- Databases: {databases}
- Docker required: {has_docker}

List prerequisites with version numbers:
- Runtime requirements
- Package managers
- Database requirements
- Docker (if needed)

Be specific about versions when known.
""",

        "installation": """Generate the Installation section.

Create numbered step-by-step instructions:
1. Clone the repository
2. Install dependencies: {install_commands}
3. Set up environment variables (if {has_env_vars})

Include the actual config files content for reference:
{key_files}

Make every command copy-pasteable. Include verification steps.
""",

        "configuration": """Generate the Configuration section.

Environment variables to document:
{env_vars}

For each variable, explain:
- What it's for
- Whether it's required
- Default value (if any)
- Example value

Format as a table if there are many variables.
""",

        "usage": """Generate the Usage section.

Available commands:
- Run: {run_commands}
- Dev: {dev_commands}

Entry points: {entry_points}

Code examples from the project:
{code_examples}

Main functions/APIs:
{main_functions}

Show:
1. Basic usage
2. Common use cases with examples
3. Advanced usage (if applicable)

Include actual working code examples.
""",

        "api": """Generate the API Documentation section.

Total endpoints: {route_count}
Has authentication: {has_auth}

Routes to document:
{routes}

For each endpoint include:
- Method and path
- Description
- Request parameters/body (if known)
- Response format (if known)
- Example curl command

Format as a table or organized list.
""",

        "docker": """Generate the Docker section.

Services:
{docker_services}

Commands:
{docker_commands}

Ports: {ports}
Databases: {databases}

Include:
1. Quick start with Docker Compose
2. Individual Docker commands
3. Environment configuration
4. How to access the running services
""",

        "database": """Generate the Database section.

Databases used: {databases}
Has migrations: {has_migrations}

Models:
{db_models}

Include:
1. Database setup instructions
2. Migration commands (if applicable)
3. Schema overview
4. Connection configuration
""",

        "testing": """Generate the Testing section.

Test framework: {test_framework}
Test count: {test_count}
Test types: {test_types}
Commands: {test_commands}

Include:
1. How to run all tests
2. How to run specific test types
3. Coverage information (if available)
4. Writing new tests guidelines
""",

        "project_structure": """Generate the Project Structure section.

Directory structure:
{directory_structure}

Main modules: {main_modules}
Entry points: {entry_points}

Create an ASCII tree showing the important directories and files.
Explain what each major directory contains.
""",

        "development": """Generate the Development section.

Commands:
- Dev: {dev_commands}
- Test: {test_commands}
- Build: {build_commands}

Dev dependencies: {dev_dependencies}

Include:
1. Setting up development environment
2. Code style and linting
3. Making changes
4. Testing changes
""",

        "troubleshooting": """Generate the Troubleshooting section.

Common issues:
{common_issues}

Format as:
### Problem: [Description]
**Solution:** [Steps to fix]

Include issues related to:
- Docker: {has_docker}
- Databases: {databases}
""",

        "contributing": """Generate the Contributing section.

Has tests: {has_tests}
Test commands: {test_commands}

Standard format:
1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit PR

Keep it concise but welcoming.
""",

        "license": """Generate the License section.

License: {license}
Author: {author}

Simple format:
## 📄 License

This project is licensed under the {license} License - see the [LICENSE](LICENSE) file for details.
""",
    }

    template = prompts.get(section_id, "Generate the {section_id} section based on: {section_context}")

    # Format the template with context
    try:
        return template.format(
            section_context=str(section_context),
            **section_context
        )
    except KeyError:
        return template.format(
            section_context=str(section_context),
            section_id=section_id,
            **{k: section_context.get(k, 'N/A') for k in ['project_name', 'repo_url', 'primary_language', 'frameworks', 'features', 'license', 'version']}
        )


def create_full_readme_prompt(context: ProjectContext) -> str:
    """Create a comprehensive prompt for full README generation."""

    generator = SectionGenerator(context)
    sections = generator.get_sections_to_generate()

    # Build section contexts
    section_info = ""
    for section in sections:
        ctx = generator.build_section_context(section.id)
        section_info += f"\n### {section.title}\n"
        for key, value in ctx.items():
            if value:
                section_info += f"- {key}: {value}\n"

    # Get route information
    routes_info = ""
    if context.routes:
        routes_info = "\nAPI ENDPOINTS:\n"
        for route in context.routes[:15]:
            routes_info += f"  {route.method} {route.path}\n"
            if route.docstring:
                routes_info += f"      {route.docstring[:100]}\n"

    # Get class/function info
    code_info = ""
    if context.classes:
        code_info += "\nMAIN CLASSES:\n"
        for cls in context.classes[:10]:
            code_info += f"  {cls.name} ({cls.file_path})\n"
            if cls.docstring:
                code_info += f"      {cls.docstring[:100]}\n"

    if context.functions:
        code_info += "\nKEY FUNCTIONS:\n"
        for func in context.functions[:15]:
            if func.is_public and func.docstring:
                code_info += f"  {func.name}({', '.join(func.parameters[:3])})\n"
                code_info += f"      {func.docstring[:100]}\n"

    # Get file contents
    file_contents = ""
    for path, content in context.key_files[:10]:
        file_contents += f"\n--- {path} ---\n{content[:2500]}\n"

    prompt = f"""You are an expert technical writer creating the PERFECT README for this project.

═══════════════════════════════════════════════════════════════════════════════
PROJECT OVERVIEW
═══════════════════════════════════════════════════════════════════════════════
Name: {context.name}
Repository: {context.repo_url}
Description: {context.description}
Version: {context.version}
License: {context.license}

Primary Language: {context.primary_language}
All Languages: {', '.join(context.languages.keys())}
Frameworks: {', '.join(context.frameworks)}

Architecture: {context.architecture_type}
Complexity: {context.setup_difficulty} ({context.complexity_score} points)
Estimated Setup Time: {context.estimated_setup_time}

═══════════════════════════════════════════════════════════════════════════════
COMMANDS
═══════════════════════════════════════════════════════════════════════════════
Install: {', '.join(context.install_commands) or 'Not detected'}
Run: {', '.join(context.run_commands) or 'Not detected'}
Dev: {', '.join(context.dev_commands) or 'Not detected'}
Test: {', '.join(context.test_commands) or 'Not detected'}
Build: {', '.join(context.build_commands) or 'Not detected'}

═══════════════════════════════════════════════════════════════════════════════
FEATURES & CAPABILITIES
═══════════════════════════════════════════════════════════════════════════════
Features: {', '.join(context.features)}
Integrations: {', '.join(context.integrations)}
Databases: {', '.join(context.databases)}
Docker: {'Yes - ' + str(len(context.docker_services)) + ' services' if context.has_docker else 'No'}
Tests: {len(context.tests)} tests ({context.test_framework})
{routes_info}

═══════════════════════════════════════════════════════════════════════════════
ENVIRONMENT VARIABLES
═══════════════════════════════════════════════════════════════════════════════
{chr(10).join(f"- {v['name']}: {v['description']} {'(required)' if v.get('required') else '(optional)'}" for v in context.env_vars[:15])}

═══════════════════════════════════════════════════════════════════════════════
CODE STRUCTURE
═══════════════════════════════════════════════════════════════════════════════
{code_info}

═══════════════════════════════════════════════════════════════════════════════
PROJECT FILES
═══════════════════════════════════════════════════════════════════════════════
{file_contents}

═══════════════════════════════════════════════════════════════════════════════
SECTIONS TO INCLUDE
═══════════════════════════════════════════════════════════════════════════════
{', '.join(s.title for s in sections)}

═══════════════════════════════════════════════════════════════════════════════
QUALITY REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

1. ACCURACY: Every command and code example must work exactly as shown
2. COMPLETENESS: Cover all the sections listed above
3. SPECIFICITY: No vague descriptions - be precise about what things do
4. COPY-PASTE READY: All code blocks must work without modification
5. HUMAN VOICE: Write like a senior developer, not a marketing team
6. NO PLACEHOLDERS: Never use [TODO], [Add here], or similar
7. STRUCTURE: Use headers, bullets, tables, and code blocks effectively
8. PROGRESSIVE: Start simple, add complexity gradually

FORMAT REQUIREMENTS:
- Start with # {context.name} (project title)
- Use badges for: license, version (if known)
- Include Table of Contents for navigation
- Use emojis sparingly for visual hierarchy
- Code blocks must specify language (```bash, ```python, etc.)
- Tables for API endpoints and environment variables

Generate the complete, production-ready README now. Make it exceptional.
"""

    return prompt
