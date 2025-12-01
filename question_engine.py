"""
Question Engine
Uses the LLM to generate intelligent, context-aware questions about the project.
"""

from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass


@dataclass
class Question:
    """A question to ask the user."""
    id: str
    text: str
    category: str
    importance: str  # critical, important, optional
    default: str = ""
    options: List[str] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = []


class QuestionEngine:
    """Generates and manages questions for the user."""
    
    def __init__(self, provider: Any):
        """
        Initialize with a model provider.
        
        Args:
            provider: A ModelProvider instance (from model_provider.py)
        """
        self.provider = provider
        self.answers: Dict[str, str] = {}
    
    def generate_smart_questions(self, project_context: Dict[str, Any]) -> List[Question]:
        """Generate context-aware questions based on project analysis."""
        questions = []
        
        # Always ask these core questions
        questions.extend(self._get_core_questions())
        
        # Add context-specific questions
        questions.extend(self._get_context_questions(project_context))
        
        # Use LLM to generate additional smart questions
        llm_questions = self._generate_llm_questions(project_context)
        if llm_questions:
            questions.extend(llm_questions)
        
        return questions
    
    def _get_core_questions(self) -> List[Question]:
        """Get the core questions that are always asked."""
        return [
            Question(
                id="purpose",
                text="What is the main PURPOSE of this project? What problem does it solve?",
                category="Overview",
                importance="critical"
            ),
            Question(
                id="audience",
                text="Who is the TARGET AUDIENCE for this project?",
                category="Overview",
                importance="critical",
                options=["developers", "end-users", "both", "data-scientists", "devops", "researchers", "other"]
            ),
            Question(
                id="key_features",
                text="What are the TOP 3-5 FEATURES you want to highlight?",
                category="Features",
                importance="critical"
            ),
            Question(
                id="unique_value",
                text="What makes this project UNIQUE or better than alternatives?",
                category="Overview",
                importance="important"
            ),
        ]
    
    def _get_context_questions(self, context: Dict[str, Any]) -> List[Question]:
        """Generate questions based on detected project characteristics."""
        questions = []
        
        # Docker-specific questions
        if context.get('has_docker'):
            questions.append(Question(
                id="docker_purpose",
                text="Is Docker the PRIMARY way to run this project, or just an option?",
                category="Deployment",
                importance="important",
                options=["primary", "optional", "development-only", "production-only"]
            ))
            
            if context.get('docker_services'):
                questions.append(Question(
                    id="services_explanation",
                    text=f"Can you briefly explain what each Docker service does? ({', '.join(context['docker_services'][:5])})",
                    category="Deployment",
                    importance="important"
                ))
        
        # API-specific questions
        if context.get('api_endpoints'):
            questions.append(Question(
                id="api_auth",
                text="Does the API require authentication? If so, what type?",
                category="API",
                importance="important",
                options=["none", "api-key", "jwt", "oauth", "basic-auth", "other"]
            ))
            questions.append(Question(
                id="api_docs",
                text="Is there existing API documentation (Swagger, OpenAPI, etc.)?",
                category="API",
                importance="optional"
            ))
        
        # Database questions
        if context.get('databases'):
            questions.append(Question(
                id="db_setup",
                text=f"Are there any special database setup steps? (Detected: {', '.join(context['databases'])})",
                category="Setup",
                importance="important"
            ))
            questions.append(Question(
                id="db_migrations",
                text="How should users handle database migrations?",
                category="Setup",
                importance="optional"
            ))
        
        # Environment variables
        if context.get('env_vars'):
            questions.append(Question(
                id="env_required",
                text="Which environment variables are REQUIRED vs optional?",
                category="Configuration",
                importance="important"
            ))
            questions.append(Question(
                id="env_secrets",
                text="Are there any API keys or secrets users need to obtain? From where?",
                category="Configuration",
                importance="important"
            ))
        
        # Framework-specific questions
        frameworks = context.get('frameworks', [])
        
        if any(fw in frameworks for fw in ['React', 'Vue.js', 'Angular', 'Next.js']):
            questions.append(Question(
                id="frontend_build",
                text="What's the recommended way to build for production?",
                category="Build",
                importance="optional"
            ))
        
        if any(fw in frameworks for fw in ['Django', 'Flask', 'FastAPI', 'Express.js']):
            questions.append(Question(
                id="backend_deploy",
                text="What's the recommended production deployment setup?",
                category="Deployment",
                importance="optional"
            ))
        
        # Complexity-based questions
        complexity = context.get('complexity_score', 0)
        if complexity > 30:
            questions.append(Question(
                id="prerequisites",
                text="Are there any non-obvious prerequisites or system requirements?",
                category="Setup",
                importance="important"
            ))
            questions.append(Question(
                id="common_issues",
                text="What are the most common setup issues users encounter?",
                category="Troubleshooting",
                importance="optional"
            ))
        
        # Testing questions
        if context.get('test_cmd'):
            questions.append(Question(
                id="test_coverage",
                text="What's the current test coverage? Any specific testing instructions?",
                category="Development",
                importance="optional"
            ))
        
        return questions
    
    def _generate_llm_questions(self, context: Dict[str, Any]) -> List[Question]:
        """Use LLM to generate additional smart questions."""
        prompt = f"""Based on this project analysis, suggest 2-3 SPECIFIC questions that would help create a better README.

Project Info:
- Name: {context.get('project_name', 'Unknown')}
- Languages: {', '.join(context.get('languages', {}).keys())}
- Frameworks: {', '.join(context.get('frameworks', []))}
- Has Docker: {context.get('has_docker', False)}
- Complexity: {context.get('complexity_score', 0)}
- Features detected: {', '.join(context.get('features', [])[:5])}

Generate questions that:
1. Would reveal important information NOT obvious from the code
2. Help understand the project's real-world usage
3. Clarify any ambiguous aspects

Format each question on a new line, starting with "Q: "
Only output the questions, nothing else."""

        try:
            output = self.provider.generate(prompt, timeout=60)
            
            if output:
                questions = []
                
                for line in output.split('\n'):
                    line = line.strip()
                    if line.startswith('Q:'):
                        q_text = line[2:].strip()
                        if q_text and len(q_text) > 10:
                            questions.append(Question(
                                id=f"llm_{len(questions)}",
                                text=q_text,
                                category="Additional",
                                importance="optional"
                            ))
                
                return questions[:3]  # Limit to 3 LLM questions
                
        except Exception as e:
            print(f"⚠️  Could not generate smart questions: {e}")
        
        return []
    
    def ask_questions_interactive(self, questions: List[Question]) -> Dict[str, str]:
        """Interactively ask questions and collect answers."""
        print("\n" + "=" * 50)
        print("📋 PROJECT QUESTIONNAIRE")
        print("=" * 50)
        print("\nPlease answer these questions to help create a better README.")
        print("Press Enter to skip optional questions.\n")
        
        # Group by category
        categories = {}
        for q in questions:
            if q.category not in categories:
                categories[q.category] = []
            categories[q.category].append(q)
        
        for category, cat_questions in categories.items():
            print(f"\n--- {category} ---\n")
            
            for q in cat_questions:
                importance_marker = "🔴" if q.importance == "critical" else "🟡" if q.importance == "important" else "⚪"
                
                print(f"{importance_marker} {q.text}")
                
                if q.options:
                    print(f"   Options: {', '.join(q.options)}")
                
                if q.default:
                    print(f"   Default: {q.default}")
                
                answer = input("   Your answer: ").strip()
                
                if answer or q.importance == "critical":
                    if not answer and q.importance == "critical":
                        # Re-ask critical questions
                        while not answer:
                            print("   ⚠️  This question is required.")
                            answer = input("   Your answer: ").strip()
                    
                    self.answers[q.id] = answer
                elif q.default:
                    self.answers[q.id] = q.default
        
        return self.answers
    
    def get_missing_info_questions(self, readme_draft: str, context: Dict[str, Any]) -> List[Question]:
        """Analyze a README draft and identify missing information."""
        prompt = f"""Analyze this README draft and identify what important information is MISSING or UNCLEAR.

README DRAFT:
{readme_draft[:3000]}

PROJECT CONTEXT:
- Has Docker: {context.get('has_docker', False)}
- Has API: {len(context.get('api_endpoints', [])) > 0}
- Databases: {', '.join(context.get('databases', []))}
- Complexity: {context.get('complexity_score', 0)}

List 2-3 specific pieces of MISSING information that would improve this README.
Format: "MISSING: [description of what's missing]"
Only output the missing items, nothing else."""

        try:
            output = self.provider.generate(prompt, timeout=60)
            
            if output:
                questions = []
                
                for line in output.split('\n'):
                    line = line.strip()
                    if line.startswith('MISSING:'):
                        missing = line[8:].strip()
                        if missing:
                            questions.append(Question(
                                id=f"missing_{len(questions)}",
                                text=f"Can you provide: {missing}",
                                category="Missing Info",
                                importance="important"
                            ))
                
                return questions[:3]
                
        except Exception as e:
            print(f"⚠️  Could not analyze missing info: {e}")
        
        return []
