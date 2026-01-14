"""
Nova Deep Scanner
Comprehensive code analysis that extracts every important detail from a codebase.
"""

import os
import re
import json
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class FunctionInfo:
    """Detailed function information."""
    name: str
    file_path: str
    line_number: int
    docstring: str = ""
    parameters: List[str] = field(default_factory=list)
    return_type: str = ""
    decorators: List[str] = field(default_factory=list)
    is_async: bool = False
    is_public: bool = True
    calls: List[str] = field(default_factory=list)
    complexity: int = 0
    code_snippet: str = ""


@dataclass
class ClassInfo:
    """Detailed class information."""
    name: str
    file_path: str
    line_number: int
    docstring: str = ""
    base_classes: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    is_dataclass: bool = False
    is_model: bool = False
    code_snippet: str = ""


@dataclass
class RouteInfo:
    """API route information."""
    method: str
    path: str
    handler: str
    file_path: str
    line_number: int
    docstring: str = ""
    parameters: List[Dict] = field(default_factory=list)
    request_body: str = ""
    response_type: str = ""
    auth_required: bool = False
    code_snippet: str = ""


@dataclass
class ConfigInfo:
    """Configuration information."""
    file_path: str
    file_type: str
    content: str
    parsed: Dict = field(default_factory=dict)
    env_vars: List[str] = field(default_factory=list)
    secrets: List[str] = field(default_factory=list)
    ports: List[str] = field(default_factory=list)


@dataclass
class DependencyInfo:
    """Dependency information."""
    name: str
    version: str = ""
    is_dev: bool = False
    purpose: str = ""
    category: str = ""


@dataclass
class TestInfo:
    """Test information."""
    name: str
    file_path: str
    test_type: str  # unit, integration, e2e
    covers: List[str] = field(default_factory=list)


@dataclass
class ProjectContext:
    """Complete project context for README generation."""
    # Basic info
    name: str = ""
    description: str = ""
    version: str = ""
    author: str = ""
    license: str = ""
    repo_url: str = ""

    # Languages and frameworks
    primary_language: str = ""
    languages: Dict[str, int] = field(default_factory=dict)
    frameworks: List[str] = field(default_factory=list)

    # Architecture
    architecture_type: str = ""  # monolith, microservice, library, cli, etc.
    entry_points: List[str] = field(default_factory=list)
    main_modules: List[str] = field(default_factory=list)

    # Code structure
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    routes: List[RouteInfo] = field(default_factory=list)

    # Configuration
    configs: List[ConfigInfo] = field(default_factory=list)
    env_vars: List[Dict] = field(default_factory=list)  # {name, required, default, description}

    # Dependencies
    dependencies: List[DependencyInfo] = field(default_factory=list)
    dev_dependencies: List[DependencyInfo] = field(default_factory=list)

    # Commands
    install_commands: List[str] = field(default_factory=list)
    run_commands: List[str] = field(default_factory=list)
    dev_commands: List[str] = field(default_factory=list)
    test_commands: List[str] = field(default_factory=list)
    build_commands: List[str] = field(default_factory=list)

    # Testing
    tests: List[TestInfo] = field(default_factory=list)
    test_framework: str = ""

    # Docker
    has_docker: bool = False
    docker_services: List[Dict] = field(default_factory=list)
    docker_commands: List[str] = field(default_factory=list)

    # Database
    databases: List[str] = field(default_factory=list)
    db_models: List[Dict] = field(default_factory=list)

    # Features
    features: List[str] = field(default_factory=list)
    integrations: List[str] = field(default_factory=list)

    # Documentation
    existing_docs: Dict[str, str] = field(default_factory=dict)
    code_examples: List[Dict] = field(default_factory=list)

    # Project structure
    directory_structure: Dict = field(default_factory=dict)
    key_files: List[Tuple[str, str]] = field(default_factory=list)

    # Complexity
    complexity_score: int = 0
    setup_difficulty: str = "Medium"
    estimated_setup_time: str = "10-15 minutes"


class DeepScanner:
    """
    Deep code scanner that extracts comprehensive information from a codebase.
    """

    def __init__(self, repo_path: str = "cloned_repo"):
        self.repo_path = Path(repo_path)
        self.context = ProjectContext()

        # File patterns
        self.source_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.rb', '.php'}
        self.config_files = {
            'package.json', 'pyproject.toml', 'setup.py', 'setup.cfg',
            'requirements.txt', 'Pipfile', 'Cargo.toml', 'go.mod',
            'composer.json', 'Gemfile', 'pom.xml', 'build.gradle'
        }
        self.docker_files = {'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml'}

        # Framework patterns
        self.framework_patterns = {
            # Python
            'fastapi': [r'from\s+fastapi', r'FastAPI\(\)'],
            'flask': [r'from\s+flask', r'Flask\(__name__\)'],
            'django': [r'from\s+django', r'INSTALLED_APPS'],
            'tornado': [r'from\s+tornado', r'tornado\.web'],
            'pyramid': [r'from\s+pyramid'],

            # JavaScript/TypeScript
            'react': [r'from\s+[\'"]react[\'"]', r'import\s+React'],
            'vue': [r'from\s+[\'"]vue[\'"]', r'createApp'],
            'angular': [r'@angular/core', r'@Component'],
            'express': [r'from\s+[\'"]express[\'"]', r'require\([\'"]express[\'"]\)'],
            'nestjs': [r'@nestjs/core', r'@Module'],
            'nextjs': [r'from\s+[\'"]next', r'next/'],

            # Others
            'spring': [r'@SpringBootApplication', r'org\.springframework'],
            'rails': [r'Rails\.application', r'ActionController'],
            'laravel': [r'Illuminate\\', r'artisan'],
            'gin': [r'github\.com/gin-gonic/gin'],
            'actix': [r'actix_web', r'actix-web'],
        }

        # Database patterns
        self.db_patterns = {
            'postgresql': [r'postgres', r'psycopg2', r'pg_', r'5432'],
            'mysql': [r'mysql', r'pymysql', r'3306'],
            'mongodb': [r'mongodb', r'pymongo', r'mongoose', r'27017'],
            'redis': [r'redis', r'6379'],
            'sqlite': [r'sqlite', r'\.db'],
            'elasticsearch': [r'elasticsearch', r'9200'],
        }

    def scan(self) -> ProjectContext:
        """Perform comprehensive scan of the codebase."""
        print("🔍 Starting deep scan...")

        # Phase 1: Basic structure
        self._scan_directory_structure()
        self._detect_languages()

        # Phase 2: Configuration files
        self._scan_config_files()
        self._extract_dependencies()
        self._extract_commands()

        # Phase 3: Source code analysis
        self._scan_source_files()
        self._detect_frameworks()
        self._extract_routes()
        self._extract_models()

        # Phase 4: Docker analysis
        self._scan_docker()

        # Phase 5: Test analysis
        self._scan_tests()

        # Phase 6: Documentation
        self._scan_existing_docs()
        self._extract_code_examples()

        # Phase 7: Feature detection
        self._detect_features()
        self._detect_integrations()

        # Phase 8: Calculate complexity
        self._calculate_complexity()

        # Phase 9: Collect key files
        self._collect_key_files()

        print(f"✅ Deep scan complete: {len(self.context.functions)} functions, "
              f"{len(self.context.classes)} classes, {len(self.context.routes)} routes")

        return self.context

    def _scan_directory_structure(self):
        """Scan and understand directory structure."""
        structure = {}

        important_dirs = {
            'src': 'Source code',
            'lib': 'Library code',
            'app': 'Application code',
            'api': 'API endpoints',
            'routes': 'Route handlers',
            'controllers': 'Controllers',
            'models': 'Data models',
            'views': 'View templates',
            'templates': 'Templates',
            'static': 'Static files',
            'public': 'Public assets',
            'tests': 'Test files',
            'test': 'Test files',
            'spec': 'Test specifications',
            'docs': 'Documentation',
            'config': 'Configuration',
            'scripts': 'Scripts',
            'bin': 'Executables',
            'utils': 'Utilities',
            'helpers': 'Helper functions',
            'middleware': 'Middleware',
            'services': 'Services',
            'components': 'UI Components',
            'hooks': 'React hooks',
            'store': 'State management',
            'migrations': 'Database migrations',
        }

        for item in self.repo_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                dir_name = item.name.lower()
                file_count = len(list(item.rglob('*')))

                structure[item.name] = {
                    'type': 'directory',
                    'description': important_dirs.get(dir_name, 'Project directory'),
                    'file_count': file_count
                }
            elif item.is_file():
                structure[item.name] = {
                    'type': 'file',
                    'description': self._get_file_description(item.name)
                }

        self.context.directory_structure = structure

    def _get_file_description(self, filename: str) -> str:
        """Get description for a file."""
        descriptions = {
            'README.md': 'Project documentation',
            'LICENSE': 'License file',
            'package.json': 'Node.js package configuration',
            'pyproject.toml': 'Python project configuration',
            'requirements.txt': 'Python dependencies',
            'Dockerfile': 'Docker container definition',
            'docker-compose.yml': 'Docker Compose configuration',
            '.env.example': 'Environment variables template',
            'Makefile': 'Build automation',
            '.gitignore': 'Git ignore rules',
            'tsconfig.json': 'TypeScript configuration',
            'webpack.config.js': 'Webpack configuration',
            'vite.config.js': 'Vite configuration',
            '.eslintrc': 'ESLint configuration',
            'pytest.ini': 'Pytest configuration',
            'jest.config.js': 'Jest configuration',
        }
        return descriptions.get(filename, 'Project file')

    def _detect_languages(self):
        """Detect programming languages used."""
        extension_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript (React)',
            '.tsx': 'TypeScript (React)',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.cs': 'C#',
            '.cpp': 'C++',
            '.c': 'C',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.sql': 'SQL',
            '.sh': 'Shell',
        }

        lang_counts = defaultdict(int)

        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in extension_map:
                    lang_counts[extension_map[ext]] += 1

        self.context.languages = dict(sorted(lang_counts.items(), key=lambda x: -x[1]))

        if self.context.languages:
            self.context.primary_language = list(self.context.languages.keys())[0]

    def _scan_config_files(self):
        """Scan all configuration files."""
        for config_file in self.config_files:
            for file_path in self.repo_path.rglob(config_file):
                if file_path.is_file():
                    try:
                        content = file_path.read_text(errors='ignore')
                        config = ConfigInfo(
                            file_path=str(file_path.relative_to(self.repo_path)),
                            file_type=file_path.suffix or file_path.name,
                            content=content[:5000]
                        )

                        # Parse the config
                        config.parsed = self._parse_config(file_path, content)
                        config.env_vars = self._extract_env_vars_from_content(content)
                        config.ports = self._extract_ports(content)

                        self.context.configs.append(config)

                        # Extract project info
                        self._extract_project_info(config)

                    except Exception:
                        continue

        # Also scan .env.example
        for env_file in self.repo_path.glob('.env*'):
            if env_file.is_file() and 'example' in env_file.name.lower():
                try:
                    content = env_file.read_text(errors='ignore')
                    self._parse_env_file(content)
                except Exception:
                    continue

    def _parse_config(self, file_path: Path, content: str) -> Dict:
        """Parse configuration file content."""
        try:
            if file_path.suffix == '.json' or file_path.name == 'package.json':
                return json.loads(content)
            elif file_path.suffix == '.toml':
                import tomli
                return tomli.loads(content)
            elif file_path.suffix in {'.yml', '.yaml'}:
                import yaml
                return yaml.safe_load(content) or {}
        except Exception:
            pass
        return {}

    def _extract_env_vars_from_content(self, content: str) -> List[str]:
        """Extract environment variable references."""
        patterns = [
            r'process\.env\.(\w+)',
            r'os\.environ(?:\.get)?\([\'"](\w+)',
            r'\$\{(\w+)\}',
            r'getenv\([\'"](\w+)',
        ]

        env_vars = set()
        for pattern in patterns:
            env_vars.update(re.findall(pattern, content))

        return list(env_vars)

    def _extract_ports(self, content: str) -> List[str]:
        """Extract port numbers from content."""
        # Look for common port patterns
        patterns = [
            r'(?:port|PORT)[\'"\s:=]+(\d{4,5})',
            r'localhost:(\d{4,5})',
            r':(\d{4,5})(?:/|"|\s|$)',
        ]

        ports = set()
        for pattern in patterns:
            for match in re.findall(pattern, content):
                port = int(match)
                if 1024 <= port <= 65535:  # Valid port range
                    ports.add(str(port))

        return list(ports)

    def _parse_env_file(self, content: str):
        """Parse .env.example file."""
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip().strip('"\'')

                # Determine if it's a secret
                is_secret = any(s in key.upper() for s in ['SECRET', 'KEY', 'PASSWORD', 'TOKEN', 'API'])

                # Determine if it's required (no default value)
                is_required = value == '' or value.startswith('your_') or value.startswith('<')

                self.context.env_vars.append({
                    'name': key,
                    'default': value if not is_required else None,
                    'required': is_required,
                    'is_secret': is_secret,
                    'description': self._guess_env_description(key)
                })

    def _guess_env_description(self, key: str) -> str:
        """Guess the description of an environment variable."""
        key_lower = key.lower()

        if 'database' in key_lower or 'db_' in key_lower:
            return 'Database configuration'
        elif 'redis' in key_lower:
            return 'Redis connection'
        elif 'api_key' in key_lower:
            return 'API key for external service'
        elif 'secret' in key_lower:
            return 'Secret key for security'
        elif 'host' in key_lower:
            return 'Hostname configuration'
        elif 'port' in key_lower:
            return 'Port number'
        elif 'url' in key_lower:
            return 'URL endpoint'
        elif 'debug' in key_lower:
            return 'Debug mode flag'
        elif 'log' in key_lower:
            return 'Logging configuration'
        elif 'mail' in key_lower or 'smtp' in key_lower:
            return 'Email/SMTP configuration'
        elif 'aws' in key_lower:
            return 'AWS configuration'
        elif 'jwt' in key_lower:
            return 'JWT authentication'
        else:
            return 'Configuration variable'

    def _extract_project_info(self, config: ConfigInfo):
        """Extract project info from config."""
        parsed = config.parsed

        if not parsed:
            return

        # package.json
        if 'name' in parsed:
            self.context.name = self.context.name or parsed.get('name', '')
            self.context.description = self.context.description or parsed.get('description', '')
            self.context.version = self.context.version or parsed.get('version', '')
            self.context.author = self.context.author or str(parsed.get('author', ''))
            self.context.license = self.context.license or parsed.get('license', '')

        # pyproject.toml
        if 'project' in parsed:
            proj = parsed['project']
            self.context.name = self.context.name or proj.get('name', '')
            self.context.description = self.context.description or proj.get('description', '')
            self.context.version = self.context.version or proj.get('version', '')

    def _extract_dependencies(self):
        """Extract all dependencies."""
        for config in self.context.configs:
            parsed = config.parsed

            # package.json
            if 'dependencies' in parsed:
                for name, version in parsed['dependencies'].items():
                    self.context.dependencies.append(DependencyInfo(
                        name=name,
                        version=version,
                        is_dev=False,
                        category=self._categorize_dependency(name)
                    ))

            if 'devDependencies' in parsed:
                for name, version in parsed['devDependencies'].items():
                    self.context.dev_dependencies.append(DependencyInfo(
                        name=name,
                        version=version,
                        is_dev=True,
                        category=self._categorize_dependency(name)
                    ))

            # pyproject.toml
            if 'project' in parsed and 'dependencies' in parsed['project']:
                for dep in parsed['project']['dependencies']:
                    name = re.split(r'[<>=!]', dep)[0].strip()
                    self.context.dependencies.append(DependencyInfo(
                        name=name,
                        is_dev=False,
                        category=self._categorize_dependency(name)
                    ))

            # requirements.txt
            if config.file_type == '.txt' and 'requirements' in config.file_path.lower():
                for line in config.content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        name = re.split(r'[<>=!]', line)[0].strip()
                        if name:
                            self.context.dependencies.append(DependencyInfo(
                                name=name,
                                is_dev='dev' in config.file_path.lower(),
                                category=self._categorize_dependency(name)
                            ))

    def _categorize_dependency(self, name: str) -> str:
        """Categorize a dependency."""
        name_lower = name.lower()

        categories = {
            'web framework': ['express', 'fastapi', 'flask', 'django', 'koa', 'hapi', 'nestjs'],
            'database': ['mongoose', 'sequelize', 'typeorm', 'prisma', 'sqlalchemy', 'psycopg2', 'pymongo'],
            'testing': ['jest', 'mocha', 'pytest', 'unittest', 'vitest', 'cypress'],
            'ui framework': ['react', 'vue', 'angular', 'svelte'],
            'state management': ['redux', 'mobx', 'vuex', 'pinia', 'zustand'],
            'authentication': ['passport', 'jwt', 'oauth', 'auth0'],
            'validation': ['joi', 'yup', 'zod', 'pydantic'],
            'http client': ['axios', 'requests', 'httpx', 'node-fetch'],
            'utility': ['lodash', 'underscore', 'ramda'],
            'cli': ['commander', 'yargs', 'click', 'typer', 'argparse'],
            'logging': ['winston', 'pino', 'bunyan', 'loguru'],
            'formatting': ['prettier', 'eslint', 'black', 'isort'],
        }

        for category, packages in categories.items():
            if any(pkg in name_lower for pkg in packages):
                return category

        return 'other'

    def _extract_commands(self):
        """Extract available commands."""
        for config in self.context.configs:
            parsed = config.parsed

            # package.json scripts
            if 'scripts' in parsed:
                scripts = parsed['scripts']

                for key in ['install', 'postinstall']:
                    if key in scripts:
                        self.context.install_commands.append(f"npm run {key}")

                for key in ['start', 'serve']:
                    if key in scripts:
                        self.context.run_commands.append(f"npm run {key}")

                for key in ['dev', 'develop', 'watch']:
                    if key in scripts:
                        self.context.dev_commands.append(f"npm run {key}")

                for key in ['test', 'test:unit', 'test:e2e']:
                    if key in scripts:
                        self.context.test_commands.append(f"npm run {key}")

                for key in ['build', 'compile']:
                    if key in scripts:
                        self.context.build_commands.append(f"npm run {key}")

            # pyproject.toml scripts
            if 'project' in parsed and 'scripts' in parsed['project']:
                for name, path in parsed['project']['scripts'].items():
                    self.context.run_commands.append(name)

        # Detect from primary language
        if self.context.primary_language == 'Python':
            if not self.context.install_commands:
                self.context.install_commands = ['pip install -r requirements.txt']

            # Look for main.py, app.py, etc.
            for entry in ['main.py', 'app.py', 'run.py', 'server.py']:
                if (self.repo_path / entry).exists():
                    self.context.run_commands.append(f'python {entry}')
                    break

            # Check for pytest
            if any('pytest' in d.name.lower() for d in self.context.dependencies):
                self.context.test_commands.append('pytest')

        elif self.context.primary_language in ['JavaScript', 'TypeScript']:
            if not self.context.install_commands:
                self.context.install_commands = ['npm install']

    def _scan_source_files(self):
        """Scan all source files for functions and classes."""
        for ext in self.source_extensions:
            for file_path in self.repo_path.rglob(f'*{ext}'):
                if self._should_skip_file(file_path):
                    continue

                try:
                    content = file_path.read_text(errors='ignore')
                    rel_path = str(file_path.relative_to(self.repo_path))

                    if ext == '.py':
                        self._analyze_python_file(rel_path, content)
                    elif ext in {'.js', '.ts', '.jsx', '.tsx'}:
                        self._analyze_js_file(rel_path, content)

                except Exception:
                    continue

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_dirs = {'node_modules', 'venv', '.venv', '__pycache__', 'dist', 'build', '.git'}
        return any(skip in file_path.parts for skip in skip_dirs)

    def _analyze_python_file(self, file_path: str, content: str):
        """Analyze a Python file."""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return

        lines = content.split('\n')

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Get code snippet
                start = node.lineno - 1
                end = min(start + 15, len(lines))
                snippet = '\n'.join(lines[start:end])

                func_info = FunctionInfo(
                    name=node.name,
                    file_path=file_path,
                    line_number=node.lineno,
                    docstring=ast.get_docstring(node) or '',
                    parameters=[arg.arg for arg in node.args.args],
                    decorators=[self._get_decorator_name(d) for d in node.decorator_list],
                    is_async=isinstance(node, ast.AsyncFunctionDef),
                    is_public=not node.name.startswith('_'),
                    code_snippet=snippet
                )

                # Get return type annotation
                if node.returns:
                    func_info.return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else ''

                self.context.functions.append(func_info)

            elif isinstance(node, ast.ClassDef):
                # Get code snippet
                start = node.lineno - 1
                end = min(start + 30, len(lines))
                snippet = '\n'.join(lines[start:end])

                class_info = ClassInfo(
                    name=node.name,
                    file_path=file_path,
                    line_number=node.lineno,
                    docstring=ast.get_docstring(node) or '',
                    base_classes=[self._get_base_name(b) for b in node.bases],
                    decorators=[self._get_decorator_name(d) for d in node.decorator_list],
                    methods=[n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))],
                    is_dataclass='dataclass' in [self._get_decorator_name(d) for d in node.decorator_list],
                    code_snippet=snippet
                )

                # Check if it's a model
                class_info.is_model = any(base in ['Model', 'Base', 'BaseModel', 'Document']
                                         for base in class_info.base_classes)

                self.context.classes.append(class_info)

    def _get_decorator_name(self, node) -> str:
        """Get decorator name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return ''

    def _get_base_name(self, node) -> str:
        """Get base class name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return ''

    def _analyze_js_file(self, file_path: str, content: str):
        """Analyze JavaScript/TypeScript file."""
        lines = content.split('\n')

        # Function patterns
        func_patterns = [
            r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)',
            r'(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>',
            r'(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?function',
        ]

        for pattern in func_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                start = line_num - 1
                end = min(start + 15, len(lines))
                snippet = '\n'.join(lines[start:end])

                self.context.functions.append(FunctionInfo(
                    name=match.group(1),
                    file_path=file_path,
                    line_number=line_num,
                    is_async='async' in match.group(0),
                    is_public=not match.group(1).startswith('_'),
                    code_snippet=snippet
                ))

        # Class patterns
        class_pattern = r'(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?'
        for match in re.finditer(class_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            start = line_num - 1
            end = min(start + 30, len(lines))
            snippet = '\n'.join(lines[start:end])

            self.context.classes.append(ClassInfo(
                name=match.group(1),
                file_path=file_path,
                line_number=line_num,
                base_classes=[match.group(2)] if match.group(2) else [],
                code_snippet=snippet
            ))

    def _detect_frameworks(self):
        """Detect frameworks used."""
        all_content = ""

        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in self.source_extensions:
                if not self._should_skip_file(file_path):
                    try:
                        all_content += file_path.read_text(errors='ignore') + "\n"
                    except:
                        continue

        for framework, patterns in self.framework_patterns.items():
            for pattern in patterns:
                if re.search(pattern, all_content, re.IGNORECASE):
                    self.context.frameworks.append(framework)
                    break

    def _extract_routes(self):
        """Extract API routes."""
        route_patterns = {
            # FastAPI
            r'@(?:app|router)\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]',
            # Flask
            r'@(?:app|bp|blueprint)\.(route)\([\'"]([^\'"]+)[\'"]',
            # Express
            r'(?:app|router)\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]',
            # Django
            r'path\([\'"]([^\'"]+)[\'"]',
        }

        for file_path in self.repo_path.rglob('*'):
            if file_path.suffix in {'.py', '.js', '.ts'}:
                if self._should_skip_file(file_path):
                    continue

                try:
                    content = file_path.read_text(errors='ignore')
                    rel_path = str(file_path.relative_to(self.repo_path))
                    lines = content.split('\n')

                    for pattern in route_patterns:
                        for match in re.finditer(pattern, content, re.IGNORECASE):
                            line_num = content[:match.start()].count('\n') + 1
                            start = max(0, line_num - 2)
                            end = min(line_num + 20, len(lines))
                            snippet = '\n'.join(lines[start:end])

                            method = match.group(1).upper() if len(match.groups()) > 1 else 'GET'
                            path = match.group(2) if len(match.groups()) > 1 else match.group(1)

                            # Extract docstring or comments
                            docstring = ""
                            for i in range(line_num, min(line_num + 5, len(lines))):
                                if '"""' in lines[i] or "'''" in lines[i]:
                                    docstring = lines[i].strip().strip('"""').strip("'''")
                                    break

                            self.context.routes.append(RouteInfo(
                                method=method,
                                path=path,
                                handler=f"handler_at_line_{line_num}",
                                file_path=rel_path,
                                line_number=line_num,
                                docstring=docstring,
                                code_snippet=snippet
                            ))

                except Exception:
                    continue

    def _extract_models(self):
        """Extract database models."""
        for cls in self.context.classes:
            if cls.is_model:
                self.context.db_models.append({
                    'name': cls.name,
                    'file': cls.file_path,
                    'docstring': cls.docstring,
                    'attributes': cls.attributes,
                    'snippet': cls.code_snippet
                })

    def _scan_docker(self):
        """Scan Docker configuration."""
        for docker_file in self.docker_files:
            file_path = self.repo_path / docker_file
            if file_path.exists():
                self.context.has_docker = True

                try:
                    content = file_path.read_text(errors='ignore')

                    if 'compose' in docker_file:
                        # Parse docker-compose
                        self._parse_docker_compose(content)
                    else:
                        # Parse Dockerfile
                        self._parse_dockerfile(content)

                except Exception:
                    continue

        if self.context.has_docker:
            self.context.docker_commands = [
                'docker-compose up -d',
                'docker-compose down',
                'docker-compose logs -f'
            ]

    def _parse_docker_compose(self, content: str):
        """Parse docker-compose file."""
        try:
            import yaml
            config = yaml.safe_load(content)

            if 'services' in config:
                for name, service in config['services'].items():
                    service_info = {
                        'name': name,
                        'image': service.get('image', ''),
                        'build': service.get('build', ''),
                        'ports': service.get('ports', []),
                        'environment': service.get('environment', []),
                        'depends_on': service.get('depends_on', [])
                    }
                    self.context.docker_services.append(service_info)

                    # Detect databases
                    image = str(service.get('image', '')).lower()
                    for db in ['postgres', 'mysql', 'mongo', 'redis', 'elasticsearch']:
                        if db in image or db in name.lower():
                            if db not in self.context.databases:
                                self.context.databases.append(db)

        except Exception:
            pass

    def _parse_dockerfile(self, content: str):
        """Parse Dockerfile."""
        # Extract base image
        base_match = re.search(r'FROM\s+(\S+)', content)
        if base_match:
            self.context.docker_services.append({
                'name': 'app',
                'image': base_match.group(1),
                'type': 'dockerfile'
            })

        # Extract exposed ports
        for match in re.findall(r'EXPOSE\s+(\d+)', content):
            if match not in [s.get('ports', []) for s in self.context.docker_services]:
                pass  # Could add to ports

    def _scan_tests(self):
        """Scan test files."""
        test_dirs = ['tests', 'test', 'spec', '__tests__']

        for test_dir in test_dirs:
            test_path = self.repo_path / test_dir
            if test_path.exists():
                for file_path in test_path.rglob('*'):
                    if file_path.is_file() and file_path.suffix in {'.py', '.js', '.ts'}:
                        try:
                            content = file_path.read_text(errors='ignore')
                            rel_path = str(file_path.relative_to(self.repo_path))

                            # Count test functions
                            test_funcs = re.findall(r'(?:def\s+test_|it\([\'"]|test\([\'"])(\w+)', content)

                            for test_name in test_funcs:
                                self.context.tests.append(TestInfo(
                                    name=test_name,
                                    file_path=rel_path,
                                    test_type=self._detect_test_type(rel_path, content)
                                ))

                        except Exception:
                            continue

        # Detect test framework
        if any('pytest' in d.name.lower() for d in self.context.dependencies):
            self.context.test_framework = 'pytest'
        elif any('jest' in d.name.lower() for d in self.context.dependencies):
            self.context.test_framework = 'jest'
        elif any('mocha' in d.name.lower() for d in self.context.dependencies):
            self.context.test_framework = 'mocha'

    def _detect_test_type(self, path: str, content: str) -> str:
        """Detect type of test."""
        path_lower = path.lower()
        content_lower = content.lower()

        if 'e2e' in path_lower or 'end-to-end' in path_lower:
            return 'e2e'
        elif 'integration' in path_lower or 'int_' in path_lower:
            return 'integration'
        elif 'fixture' in content_lower or 'mock' in content_lower:
            return 'unit'

        return 'unit'

    def _scan_existing_docs(self):
        """Scan existing documentation."""
        doc_files = ['README.md', 'CONTRIBUTING.md', 'CHANGELOG.md', 'API.md', 'ARCHITECTURE.md']

        for doc_file in doc_files:
            file_path = self.repo_path / doc_file
            if file_path.exists():
                try:
                    content = file_path.read_text(errors='ignore')
                    self.context.existing_docs[doc_file] = content[:3000]
                except Exception:
                    continue

        # Check docs directory
        docs_path = self.repo_path / 'docs'
        if docs_path.exists():
            for file_path in docs_path.rglob('*.md'):
                try:
                    content = file_path.read_text(errors='ignore')
                    rel_path = str(file_path.relative_to(self.repo_path))
                    self.context.existing_docs[rel_path] = content[:2000]
                except Exception:
                    continue

    def _extract_code_examples(self):
        """Extract code examples from docs and comments."""
        # From existing docs
        for doc_name, content in self.context.existing_docs.items():
            # Find code blocks
            code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
            for lang, code in code_blocks:
                if len(code.strip()) > 20:
                    self.context.code_examples.append({
                        'source': doc_name,
                        'language': lang or 'text',
                        'code': code.strip()[:500]
                    })

        # From docstrings
        for func in self.context.functions[:50]:  # Limit
            if func.docstring and '>>>' in func.docstring:
                # Python doctest style
                self.context.code_examples.append({
                    'source': f"{func.file_path}:{func.name}",
                    'language': 'python',
                    'code': func.docstring
                })

    def _detect_features(self):
        """Detect project features."""
        all_content = ""

        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in self.source_extensions:
                if not self._should_skip_file(file_path):
                    try:
                        all_content += file_path.read_text(errors='ignore')[:5000] + "\n"
                    except:
                        continue

        feature_patterns = {
            'Authentication': [r'auth', r'login', r'jwt', r'oauth', r'session'],
            'API': [r'@app\.(get|post)', r'router\.', r'endpoint'],
            'Database': [r'database', r'model', r'schema', r'migration'],
            'Caching': [r'cache', r'redis', r'memcached'],
            'Queue': [r'celery', r'rabbitmq', r'kafka', r'queue'],
            'WebSocket': [r'websocket', r'socket\.io', r'ws://'],
            'File Upload': [r'upload', r'multipart', r'file.*form'],
            'Email': [r'smtp', r'sendmail', r'email'],
            'Logging': [r'logger', r'logging', r'winston'],
            'Validation': [r'validate', r'schema', r'pydantic'],
            'Testing': [r'test_', r'describe\(', r'it\('],
            'Documentation': [r'swagger', r'openapi', r'apidoc'],
            'Rate Limiting': [r'rate.?limit', r'throttle'],
            'CORS': [r'cors', r'cross.?origin'],
            'Compression': [r'gzip', r'compress'],
            'Security': [r'helmet', r'csrf', r'xss', r'sanitize'],
        }

        for feature, patterns in feature_patterns.items():
            for pattern in patterns:
                if re.search(pattern, all_content, re.IGNORECASE):
                    if feature not in self.context.features:
                        self.context.features.append(feature)
                    break

    def _detect_integrations(self):
        """Detect external integrations."""
        integration_patterns = {
            'AWS': [r'boto3', r'aws-sdk', r's3', r'lambda', r'dynamodb'],
            'GCP': [r'google-cloud', r'gcp', r'firestore'],
            'Azure': [r'azure', r'@azure/'],
            'Stripe': [r'stripe'],
            'Twilio': [r'twilio'],
            'SendGrid': [r'sendgrid'],
            'Slack': [r'slack'],
            'GitHub': [r'github', r'octokit'],
            'OpenAI': [r'openai', r'gpt'],
            'Sentry': [r'sentry'],
            'DataDog': [r'datadog'],
            'Cloudinary': [r'cloudinary'],
        }

        all_deps = [d.name.lower() for d in self.context.dependencies]

        for integration, patterns in integration_patterns.items():
            for pattern in patterns:
                if any(re.search(pattern, dep, re.IGNORECASE) for dep in all_deps):
                    if integration not in self.context.integrations:
                        self.context.integrations.append(integration)
                    break

    def _calculate_complexity(self):
        """Calculate project complexity."""
        score = 0

        # Language complexity
        score += len(self.context.languages) * 5

        # Framework complexity
        score += len(self.context.frameworks) * 8

        # Docker complexity
        if self.context.has_docker:
            score += 10
            score += len(self.context.docker_services) * 5

        # Database complexity
        score += len(self.context.databases) * 10

        # Dependencies
        score += min(len(self.context.dependencies) // 5, 20)

        # Routes (API complexity)
        score += min(len(self.context.routes) // 5, 15)

        # Environment variables
        score += min(len(self.context.env_vars), 10)

        # Features
        score += len(self.context.features) * 2

        self.context.complexity_score = score

        # Determine difficulty
        if score < 20:
            self.context.setup_difficulty = "Easy"
            self.context.estimated_setup_time = "5 minutes"
        elif score < 40:
            self.context.setup_difficulty = "Medium"
            self.context.estimated_setup_time = "10-15 minutes"
        elif score < 70:
            self.context.setup_difficulty = "Hard"
            self.context.estimated_setup_time = "30-45 minutes"
        else:
            self.context.setup_difficulty = "Complex"
            self.context.estimated_setup_time = "1+ hours"

    def _collect_key_files(self):
        """Collect key files for context."""
        priority_files = [
            'package.json', 'pyproject.toml', 'requirements.txt',
            'Dockerfile', 'docker-compose.yml', '.env.example',
            'main.py', 'app.py', 'index.js', 'index.ts',
            'server.py', 'server.js', 'api.py', 'routes.py'
        ]

        collected = []

        # First, get priority files
        for priority in priority_files:
            for file_path in self.repo_path.rglob(priority):
                if not self._should_skip_file(file_path):
                    try:
                        content = file_path.read_text(errors='ignore')
                        rel_path = str(file_path.relative_to(self.repo_path))
                        collected.append((rel_path, content[:4000]))
                    except:
                        continue

        # Then add important source files
        for file_path in self.repo_path.rglob('*'):
            if len(collected) >= 15:
                break

            if file_path.is_file() and file_path.suffix in self.source_extensions:
                if not self._should_skip_file(file_path):
                    rel_path = str(file_path.relative_to(self.repo_path))
                    if rel_path not in [c[0] for c in collected]:
                        try:
                            content = file_path.read_text(errors='ignore')
                            collected.append((rel_path, content[:3000]))
                        except:
                            continue

        self.context.key_files = collected
