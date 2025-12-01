"""
README Templates
Different templates for various README styles and project types.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ReadmeTemplate:
    """A README template configuration."""
    name: str
    description: str
    sections: List[str]
    style_guide: str


class TemplateManager:
    """Manages README templates for different styles and project types."""
    
    TEMPLATES = {
        'minimal': ReadmeTemplate(
            name="Minimal",
            description="Quick start only, bare essentials",
            sections=[
                "title",
                "description_short",
                "quick_start",
                "license"
            ],
            style_guide="""
- Keep it under 50 lines
- One-liner description
- Just the essential commands
- No fluff, no badges
- Perfect for simple scripts or utilities"""
        ),
        
        'standard': ReadmeTemplate(
            name="Standard",
            description="Balanced coverage of main topics",
            sections=[
                "title",
                "description",
                "features",
                "installation",
                "usage",
                "configuration",
                "contributing",
                "license"
            ],
            style_guide="""
- 100-200 lines
- Clear, concise descriptions
- Basic code examples
- Standard sections only
- Good for most projects"""
        ),
        
        'detailed': ReadmeTemplate(
            name="Detailed",
            description="Comprehensive with examples",
            sections=[
                "title_with_badges",
                "description",
                "table_of_contents",
                "features",
                "tech_stack",
                "prerequisites",
                "installation",
                "configuration",
                "usage_examples",
                "api_docs",
                "docker",
                "project_structure",
                "development",
                "testing",
                "contributing",
                "license",
                "support"
            ],
            style_guide="""
- 200-400 lines
- Detailed explanations
- Multiple code examples
- Screenshots/diagrams placeholders
- Troubleshooting tips
- Good for complex projects"""
        ),
        
        'comprehensive': ReadmeTemplate(
            name="Comprehensive",
            description="Everything including kitchen sink",
            sections=[
                "title_with_badges",
                "hero_description",
                "table_of_contents",
                "demo_section",
                "features_detailed",
                "tech_stack_detailed",
                "architecture",
                "prerequisites_detailed",
                "installation_multiple_methods",
                "configuration_detailed",
                "usage_comprehensive",
                "api_documentation",
                "docker_deployment",
                "kubernetes",
                "project_structure_detailed",
                "development_guide",
                "testing_guide",
                "troubleshooting",
                "faq",
                "roadmap",
                "contributing_detailed",
                "code_of_conduct",
                "security",
                "changelog",
                "license",
                "acknowledgments",
                "support_contact"
            ],
            style_guide="""
- 400+ lines
- Exhaustive documentation
- Multiple installation methods
- Full API reference
- Architecture diagrams
- FAQ section
- Roadmap
- For enterprise/complex projects"""
        ),
        
        # Project-type specific templates
        'api': ReadmeTemplate(
            name="API Project",
            description="Optimized for API/backend projects",
            sections=[
                "title_with_badges",
                "description",
                "features",
                "tech_stack",
                "prerequisites",
                "installation",
                "configuration",
                "api_endpoints",
                "authentication",
                "request_examples",
                "response_formats",
                "error_handling",
                "rate_limiting",
                "docker",
                "testing",
                "contributing",
                "license"
            ],
            style_guide="""
- Focus on API documentation
- Include request/response examples
- Document all endpoints
- Authentication details
- Error codes and handling"""
        ),
        
        'cli': ReadmeTemplate(
            name="CLI Tool",
            description="Optimized for command-line tools",
            sections=[
                "title",
                "description",
                "installation",
                "commands",
                "options",
                "examples",
                "configuration",
                "contributing",
                "license"
            ],
            style_guide="""
- Focus on commands and options
- Many usage examples
- Clear option descriptions
- Installation via package managers"""
        ),
        
        'library': ReadmeTemplate(
            name="Library/Package",
            description="Optimized for reusable libraries",
            sections=[
                "title_with_badges",
                "description",
                "installation",
                "quick_start",
                "api_reference",
                "examples",
                "configuration",
                "typescript_support",
                "browser_support",
                "contributing",
                "license"
            ],
            style_guide="""
- Focus on API reference
- Import/require examples
- TypeScript types if applicable
- Browser/Node compatibility
- Version compatibility"""
        ),
        
        'data_science': ReadmeTemplate(
            name="Data Science",
            description="Optimized for ML/data projects",
            sections=[
                "title",
                "description",
                "results",
                "dataset",
                "model_architecture",
                "requirements",
                "installation",
                "usage",
                "training",
                "evaluation",
                "notebooks",
                "citation",
                "license"
            ],
            style_guide="""
- Include results/metrics
- Dataset description
- Model architecture
- Training instructions
- Jupyter notebook links
- Citation format"""
        )
    }
    
    @classmethod
    def get_template(cls, style: str) -> ReadmeTemplate:
        """Get a template by style name."""
        return cls.TEMPLATES.get(style, cls.TEMPLATES['detailed'])
    
    @classmethod
    def list_templates(cls) -> List[Dict[str, str]]:
        """List all available templates."""
        return [
            {"name": name, "description": template.description}
            for name, template in cls.TEMPLATES.items()
        ]
    
    @classmethod
    def suggest_template(cls, context: Dict[str, Any]) -> str:
        """Suggest the best template based on project context."""
        # Check for API project
        if context.get('api_endpoints') and len(context.get('api_endpoints', [])) > 5:
            return 'api'
        
        # Check for CLI tool
        deps_str = str(context.get('dependencies', [])).lower()
        if context.get('cli_commands') or 'argparse' in deps_str or 'click' in deps_str:
            return 'cli'
        
        # Check for library/package
        if context.get('is_library') or 'setup.py' in str(context.get('files', [])):
            return 'library'
        
        # Check for data science
        ml_indicators = ['tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'jupyter']
        if any(ind in str(context.get('dependencies', [])).lower() for ind in ml_indicators):
            return 'data_science'
        
        # Based on complexity
        complexity = context.get('complexity_score', 0)
        if complexity < 10:
            return 'minimal'
        elif complexity < 25:
            return 'standard'
        elif complexity < 50:
            return 'detailed'
        else:
            return 'comprehensive'
    
    @classmethod
    def get_section_prompt(cls, section: str, context: Dict[str, Any]) -> str:
        """Get the prompt for generating a specific section."""
        section_prompts = {
            'title': f"# {context.get('project_name', 'Project')}",
            
            'title_with_badges': f"""# {context.get('project_name', 'Project')}

![License](https://img.shields.io/badge/license-{context.get('license', 'MIT')}-blue.svg)
![Version](https://img.shields.io/badge/version-{context.get('version', '1.0.0')}-green.svg)
""",
            
            'description_short': "Write a one-line description of what this project does.",
            
            'description': """Write a compelling 2-3 paragraph description that covers:
- What the project does
- Why it exists (problem it solves)
- Key benefits""",
            
            'hero_description': """Write an engaging hero section with:
- Catchy tagline
- 2-3 key benefits as bullet points
- What makes it special""",
            
            'features': "List 5-8 key features as bullet points with brief descriptions.",
            
            'features_detailed': """List all features organized by category:
- Core Features
- Advanced Features
- Integrations
Each with detailed descriptions.""",
            
            'tech_stack': "List the main technologies used in a clean format.",
            
            'tech_stack_detailed': """Create a detailed tech stack section with:
- Languages and versions
- Frameworks
- Databases
- DevOps tools
- Testing frameworks""",
            
            'prerequisites': "List what users need before installation.",
            
            'installation': """Provide step-by-step installation:
1. Clone
2. Install dependencies
3. Configure
4. Run""",
            
            'installation_multiple_methods': """Provide multiple installation methods:
- From source
- Via package manager (npm/pip/etc)
- Via Docker
- Via binary release""",
            
            'usage': "Show basic usage with code examples.",
            
            'usage_examples': """Provide multiple usage examples:
- Basic usage
- Common use cases
- Advanced usage""",
            
            'usage_comprehensive': """Comprehensive usage guide with:
- Quick start
- Basic examples
- Advanced examples
- Real-world scenarios
- Best practices""",
            
            'api_docs': "Document the main API endpoints or functions.",
            
            'api_documentation': """Full API documentation with:
- All endpoints
- Request/response formats
- Authentication
- Error codes
- Rate limits""",
            
            'docker': "Docker setup and usage instructions.",
            
            'docker_deployment': """Complete Docker guide:
- Development setup
- Production deployment
- Docker Compose
- Environment variables""",
            
            'project_structure': "Show the main project structure with brief descriptions.",
            
            'testing': "How to run tests.",
            
            'contributing': """Standard contributing section:
1. Fork
2. Branch
3. Commit
4. Push
5. PR""",
            
            'license': f"This project is licensed under the {context.get('license', 'MIT')} License.",
            
            'support': "How to get help or report issues."
        }
        
        return section_prompts.get(section, f"Write the {section} section.")


def get_style_instructions(style: str, context: Dict[str, Any]) -> str:
    """Get detailed instructions for generating a README in a specific style."""
    template = TemplateManager.get_template(style)
    
    instructions = f"""
README STYLE: {template.name}
{template.description}

SECTIONS TO INCLUDE:
{chr(10).join(f'- {section}' for section in template.sections)}

STYLE GUIDELINES:
{template.style_guide}

IMPORTANT:
- Follow the style guidelines strictly
- Only include sections that are relevant to this project
- Maintain consistent formatting throughout
- Use appropriate emoji for visual appeal (but don't overdo it)
"""
    
    return instructions
