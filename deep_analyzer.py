"""
Deep Code Analyzer
Provides deeper understanding of code functionality beyond just detecting technologies.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class FunctionInfo:
    """Information about a function/method."""
    name: str
    file: str
    docstring: str = ""
    parameters: List[str] = field(default_factory=list)
    is_public: bool = True
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    file: str
    docstring: str = ""
    methods: List[str] = field(default_factory=list)
    parent_classes: List[str] = field(default_factory=list)


@dataclass
class CodeInsights:
    """Deep insights about the codebase."""
    main_entry_points: List[str] = field(default_factory=list)
    public_functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: Dict[str, List[str]] = field(default_factory=dict)  # file -> imports
    routes: List[Dict] = field(default_factory=list)  # API routes
    database_models: List[str] = field(default_factory=list)
    config_patterns: List[str] = field(default_factory=list)
    error_handling: List[str] = field(default_factory=list)
    external_calls: List[str] = field(default_factory=list)  # HTTP calls, etc.
    cli_commands: List[str] = field(default_factory=list)
    scheduled_tasks: List[str] = field(default_factory=list)
    event_handlers: List[str] = field(default_factory=list)


class DeepCodeAnalyzer:
    """Analyzes code to understand actual functionality."""
    
    def __init__(self, repo_dir: str = "cloned_repo"):
        self.repo_dir = Path(repo_dir)
        self.insights = CodeInsights()
        self.file_contents: Dict[str, str] = {}
        
    def analyze(self) -> CodeInsights:
        """Perform deep analysis of the codebase."""
        self._load_source_files()
        self._find_entry_points()
        self._extract_functions_and_classes()
        self._find_routes()
        self._find_database_models()
        self._find_external_calls()
        self._find_cli_commands()
        return self.insights
    
    def _load_source_files(self):
        """Load all relevant source files."""
        source_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.php', '.rb'}
        ignore_dirs = {'node_modules', '.git', '__pycache__', 'venv', 'env', 'dist', 'build', '.venv'}
        
        for file_path in self.repo_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix in source_extensions:
                # Skip ignored directories
                if any(ignored in file_path.parts for ignored in ignore_dirs):
                    continue
                
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    if len(content) < 50000:  # Skip very large files
                        rel_path = str(file_path.relative_to(self.repo_dir))
                        self.file_contents[rel_path] = content
                except:
                    continue
    
    def _find_entry_points(self):
        """Find main entry points of the application."""
        entry_patterns = [
            # Python
            (r'if\s+__name__\s*==\s*["\']__main__["\']', 'Python main block'),
            (r'@click\.command|@app\.cli\.command', 'CLI command'),
            (r'def\s+main\s*\(', 'main() function'),
            
            # JavaScript/Node
            (r'app\.listen\s*\(', 'Express server'),
            (r'createServer\s*\(', 'HTTP server'),
            (r'export\s+default\s+function\s+App', 'React App component'),
            
            # General
            (r'if\s*\(\s*require\.main\s*===\s*module\s*\)', 'Node.js entry'),
        ]
        
        for file_path, content in self.file_contents.items():
            for pattern, description in entry_patterns:
                if re.search(pattern, content):
                    self.insights.main_entry_points.append(f"{file_path}: {description}")
    
    def _extract_functions_and_classes(self):
        """Extract function and class definitions."""
        for file_path, content in self.file_contents.items():
            if file_path.endswith('.py'):
                self._extract_python_definitions(file_path, content)
            elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                self._extract_js_definitions(file_path, content)
    
    def _extract_python_definitions(self, file_path: str, content: str):
        """Extract Python functions and classes."""
        # Find classes
        class_pattern = r'class\s+(\w+)\s*(?:\((.*?)\))?\s*:'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            parents = match.group(2).split(',') if match.group(2) else []
            parents = [p.strip() for p in parents if p.strip()]
            
            # Get docstring
            docstring = self._get_python_docstring(content, match.end())
            
            self.insights.classes.append(ClassInfo(
                name=class_name,
                file=file_path,
                docstring=docstring[:200] if docstring else "",
                parent_classes=parents
            ))
        
        # Find functions
        func_pattern = r'(?:^|\n)((?:@\w+.*?\n)*)\s*def\s+(\w+)\s*\((.*?)\)'
        for match in re.finditer(func_pattern, content, re.DOTALL):
            decorators_str = match.group(1)
            func_name = match.group(2)
            params_str = match.group(3)
            
            # Skip private functions for summary
            is_public = not func_name.startswith('_')
            
            decorators = re.findall(r'@(\w+)', decorators_str)
            params = [p.strip().split(':')[0].split('=')[0].strip() 
                     for p in params_str.split(',') if p.strip()]
            
            docstring = self._get_python_docstring(content, match.end())
            
            if is_public or decorators:  # Include decorated private functions
                self.insights.public_functions.append(FunctionInfo(
                    name=func_name,
                    file=file_path,
                    docstring=docstring[:150] if docstring else "",
                    parameters=params[:5],  # Limit params
                    is_public=is_public,
                    decorators=decorators
                ))
    
    def _get_python_docstring(self, content: str, start_pos: int) -> str:
        """Extract Python docstring after a definition."""
        # Look for docstring after the colon
        remaining = content[start_pos:start_pos + 500]
        docstring_match = re.search(r':\s*\n\s*["\'][\"\'][\"\'](.+?)["\'][\"\'][\"\']', remaining, re.DOTALL)
        if docstring_match:
            return docstring_match.group(1).strip()
        
        # Single line docstring
        docstring_match = re.search(r':\s*\n\s*["\'](.+?)["\']', remaining)
        if docstring_match:
            return docstring_match.group(1).strip()
        
        return ""
    
    def _extract_js_definitions(self, file_path: str, content: str):
        """Extract JavaScript/TypeScript functions and classes."""
        # Find exported functions
        patterns = [
            r'export\s+(?:async\s+)?function\s+(\w+)',
            r'export\s+const\s+(\w+)\s*=\s*(?:async\s*)?\(',
            r'module\.exports\s*=\s*{\s*(\w+)',
            r'class\s+(\w+)\s+extends',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                name = match.group(1)
                self.insights.public_functions.append(FunctionInfo(
                    name=name,
                    file=file_path,
                    is_public=True
                ))
    
    def _find_routes(self):
        """Find API routes/endpoints."""
        route_patterns = [
            # Flask
            (r'@app\.route\(["\'](.+?)["\'].*?\)\s*\ndef\s+(\w+)', 'Flask'),
            (r'@bp\.route\(["\'](.+?)["\'].*?\)', 'Flask Blueprint'),
            
            # FastAPI
            (r'@(?:app|router)\.(get|post|put|delete|patch)\(["\'](.+?)["\']', 'FastAPI'),
            
            # Express.js
            (r'(?:app|router)\.(get|post|put|delete|patch)\(["\'](.+?)["\']', 'Express'),
            
            # Django
            (r'path\(["\'](.+?)["\']', 'Django'),
            
            # Spring Boot
            (r'@(Get|Post|Put|Delete)Mapping\(["\'](.+?)["\']', 'Spring'),
        ]
        
        for file_path, content in self.file_contents.items():
            for pattern, framework in route_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    groups = match.groups()
                    route = groups[-1] if len(groups) > 1 else groups[0]
                    method = groups[0].upper() if len(groups) > 1 and groups[0] in ['get', 'post', 'put', 'delete', 'patch'] else 'GET'
                    
                    self.insights.routes.append({
                        'path': route,
                        'method': method,
                        'file': file_path,
                        'framework': framework
                    })
    
    def _find_database_models(self):
        """Find database model definitions."""
        model_patterns = [
            # SQLAlchemy
            r'class\s+(\w+)\s*\(.*?(?:db\.Model|Base|DeclarativeBase)',
            # Django
            r'class\s+(\w+)\s*\(.*?models\.Model',
            # Mongoose
            r'(?:const|let|var)\s+(\w+)Schema\s*=\s*new\s+(?:mongoose\.)?Schema',
            # TypeORM
            r'@Entity\(\).*?class\s+(\w+)',
            # Prisma (from schema)
            r'model\s+(\w+)\s*{',
        ]
        
        for file_path, content in self.file_contents.items():
            for pattern in model_patterns:
                for match in re.finditer(pattern, content, re.DOTALL):
                    model_name = match.group(1)
                    self.insights.database_models.append(f"{model_name} ({file_path})")
    
    def _find_external_calls(self):
        """Find external API calls and integrations."""
        external_patterns = [
            # HTTP clients
            (r'requests\.(get|post|put|delete)\(["\'](.+?)["\']', 'requests'),
            (r'axios\.(get|post|put|delete)\(["\'](.+?)["\']', 'axios'),
            (r'fetch\(["\'](.+?)["\']', 'fetch'),
            (r'http\.request\(', 'http'),
            
            # Cloud services
            (r'boto3\.client\(["\'](\w+)["\']', 'AWS'),
            (r'storage\.bucket\(', 'GCS'),
            (r'BlobServiceClient', 'Azure Blob'),
            
            # Messaging
            (r'pika\.BlockingConnection', 'RabbitMQ'),
            (r'KafkaProducer|KafkaConsumer', 'Kafka'),
            (r'redis\.Redis|Redis\(', 'Redis'),
        ]
        
        for file_path, content in self.file_contents.items():
            for pattern, service in external_patterns:
                if re.search(pattern, content):
                    self.insights.external_calls.append(f"{service} ({file_path})")
    
    def _find_cli_commands(self):
        """Find CLI command definitions."""
        cli_patterns = [
            # Click
            r'@click\.command\(\).*?def\s+(\w+)',
            # argparse
            r'parser\.add_argument\(["\']--?(\w+)["\']',
            # Typer
            r'@app\.command\(\).*?def\s+(\w+)',
            # Commander.js
            r'\.command\(["\'](\w+)["\']',
        ]
        
        for file_path, content in self.file_contents.items():
            for pattern in cli_patterns:
                for match in re.finditer(pattern, content, re.DOTALL):
                    cmd = match.group(1)
                    self.insights.cli_commands.append(f"{cmd} ({file_path})")
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the code insights."""
        summary_parts = []
        
        if self.insights.main_entry_points:
            summary_parts.append("Entry Points:")
            for ep in self.insights.main_entry_points[:5]:
                summary_parts.append(f"  • {ep}")
        
        if self.insights.routes:
            summary_parts.append(f"\nAPI Routes ({len(self.insights.routes)} total):")
            for route in self.insights.routes[:10]:
                summary_parts.append(f"  • {route['method']} {route['path']}")
        
        if self.insights.database_models:
            summary_parts.append(f"\nDatabase Models:")
            for model in self.insights.database_models[:8]:
                summary_parts.append(f"  • {model}")
        
        if self.insights.classes:
            summary_parts.append(f"\nMain Classes ({len(self.insights.classes)} total):")
            for cls in self.insights.classes[:8]:
                doc = f" - {cls.docstring[:50]}..." if cls.docstring else ""
                summary_parts.append(f"  • {cls.name}{doc}")
        
        if self.insights.external_calls:
            summary_parts.append(f"\nExternal Integrations:")
            for call in list(set(self.insights.external_calls))[:8]:
                summary_parts.append(f"  • {call}")
        
        if self.insights.cli_commands:
            summary_parts.append(f"\nCLI Commands:")
            for cmd in self.insights.cli_commands[:5]:
                summary_parts.append(f"  • {cmd}")
        
        return "\n".join(summary_parts)
