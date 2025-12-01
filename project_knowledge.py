"""
Project Knowledge Base
Deep understanding of project structure, dependencies, and architecture.
Uses embeddings and vector store for intelligent context retrieval.
"""

import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import subprocess


@dataclass
class FileKnowledge:
    """Knowledge extracted from a single file."""
    path: str
    file_type: str  # config, source, docs, test, etc.
    language: str
    size: int
    content_hash: str
    
    # Extracted knowledge
    summary: str = ""
    purpose: str = ""
    key_elements: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    
    # For vector store
    embedding: List[float] = field(default_factory=list)
    chunks: List[str] = field(default_factory=list)


@dataclass
class DependencyInfo:
    """Detailed information about a dependency."""
    name: str
    version: str = ""
    purpose: str = ""  # What it's used for
    category: str = ""  # framework, utility, database, etc.
    is_dev: bool = False
    documentation_url: str = ""


@dataclass 
class ServiceInfo:
    """Information about a Docker service or microservice."""
    name: str
    image: str = ""
    purpose: str = ""
    ports: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    volumes: List[str] = field(default_factory=list)
    healthcheck: str = ""


@dataclass
class ProjectKnowledge:
    """Complete knowledge base for a project."""
    # Basic info
    name: str = ""
    description: str = ""
    version: str = ""
    
    # File knowledge
    files: Dict[str, FileKnowledge] = field(default_factory=dict)
    
    # Dependencies
    dependencies: List[DependencyInfo] = field(default_factory=list)
    dev_dependencies: List[DependencyInfo] = field(default_factory=list)
    
    # Architecture
    services: List[ServiceInfo] = field(default_factory=list)
    architecture_type: str = ""  # monolith, microservices, serverless, etc.
    
    # Technical details
    entry_points: List[str] = field(default_factory=list)
    api_routes: List[Dict] = field(default_factory=list)
    database_models: List[Dict] = field(default_factory=list)
    environment_vars: List[Dict] = field(default_factory=list)
    
    # Build & Deploy
    build_system: str = ""  # npm, pip, cargo, maven, etc.
    ci_cd: List[str] = field(default_factory=list)
    deployment_targets: List[str] = field(default_factory=list)
    
    # LLM-generated understanding
    project_summary: str = ""
    technical_overview: str = ""
    setup_guide: str = ""
    
    # Vector store chunks for RAG
    knowledge_chunks: List[Dict] = field(default_factory=list)


class SimpleVectorStore:
    """
    Simple vector store using cosine similarity.
    For production, you'd use something like ChromaDB, Pinecone, or FAISS.
    """
    
    def __init__(self):
        self.documents: List[Dict] = []
        self.embeddings: List[List[float]] = []
    
    def add(self, text: str, metadata: Dict = None):
        """Add a document to the store."""
        # Simple hash-based "embedding" for demo
        # In production, use actual embeddings from an embedding model
        embedding = self._simple_embedding(text)
        self.documents.append({
            'text': text,
            'metadata': metadata or {},
            'embedding': embedding
        })
        self.embeddings.append(embedding)
    
    def _simple_embedding(self, text: str) -> List[float]:
        """
        Create a simple embedding based on word frequencies.
        This is a placeholder - in production use real embeddings.
        """
        # Normalize and tokenize
        words = re.findall(r'\w+', text.lower())
        
        # Create a simple bag-of-words style embedding
        # Using hash to create consistent dimensions
        embedding = [0.0] * 256
        for word in words:
            idx = hash(word) % 256
            embedding[idx] += 1
        
        # Normalize
        magnitude = sum(x*x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(x * y for x, y in zip(a, b))
        return dot_product  # Already normalized
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for most relevant documents."""
        if not self.documents:
            return []
        
        query_embedding = self._simple_embedding(query)
        
        # Calculate similarities
        similarities = []
        for i, doc in enumerate(self.documents):
            sim = self._cosine_similarity(query_embedding, doc['embedding'])
            similarities.append((sim, i))
        
        # Sort by similarity
        similarities.sort(reverse=True)
        
        # Return top_k results
        results = []
        for sim, idx in similarities[:top_k]:
            results.append({
                'text': self.documents[idx]['text'],
                'metadata': self.documents[idx]['metadata'],
                'score': sim
            })
        
        return results
    
    def get_all(self) -> List[Dict]:
        """Get all documents."""
        return [{'text': d['text'], 'metadata': d['metadata']} for d in self.documents]
    
    def save(self, path: str):
        """Save the vector store to disk."""
        data = {
            'documents': [
                {'text': d['text'], 'metadata': d['metadata']}
                for d in self.documents
            ]
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, path: str):
        """Load the vector store from disk."""
        with open(path, 'r') as f:
            data = json.load(f)
        
        self.documents = []
        self.embeddings = []
        
        for doc in data['documents']:
            self.add(doc['text'], doc['metadata'])


class DeepProjectAnalyzer:
    """
    Performs deep analysis of a project to build comprehensive knowledge.
    """
    
    # Dependency purpose mappings
    DEPENDENCY_PURPOSES = {
        # Python
        'django': ('Web Framework', 'Full-stack web framework with ORM, admin, auth'),
        'flask': ('Web Framework', 'Lightweight web framework'),
        'fastapi': ('Web Framework', 'Modern async API framework with auto-docs'),
        'sqlalchemy': ('Database', 'SQL toolkit and ORM'),
        'celery': ('Task Queue', 'Distributed task queue'),
        'redis': ('Cache/Queue', 'In-memory data store client'),
        'requests': ('HTTP Client', 'HTTP library for API calls'),
        'pytest': ('Testing', 'Testing framework'),
        'pandas': ('Data Processing', 'Data manipulation and analysis'),
        'numpy': ('Scientific Computing', 'Numerical computing'),
        'tensorflow': ('Machine Learning', 'Deep learning framework'),
        'pytorch': ('Machine Learning', 'Deep learning framework'),
        'scikit-learn': ('Machine Learning', 'ML algorithms library'),
        'boto3': ('Cloud', 'AWS SDK'),
        'pydantic': ('Validation', 'Data validation using Python type hints'),
        'uvicorn': ('Server', 'ASGI server'),
        'gunicorn': ('Server', 'WSGI HTTP server'),
        'alembic': ('Database', 'Database migrations'),
        'jwt': ('Auth', 'JSON Web Token handling'),
        'passlib': ('Auth', 'Password hashing'),
        'httpx': ('HTTP Client', 'Async HTTP client'),
        'aiohttp': ('HTTP', 'Async HTTP client/server'),
        
        # JavaScript/Node
        'react': ('Frontend Framework', 'UI component library'),
        'vue': ('Frontend Framework', 'Progressive JavaScript framework'),
        'angular': ('Frontend Framework', 'Full-featured frontend framework'),
        'next': ('Framework', 'React framework with SSR'),
        'express': ('Web Framework', 'Minimal Node.js web framework'),
        'nestjs': ('Web Framework', 'Progressive Node.js framework'),
        'prisma': ('Database', 'Next-gen ORM'),
        'mongoose': ('Database', 'MongoDB ODM'),
        'sequelize': ('Database', 'SQL ORM'),
        'axios': ('HTTP Client', 'Promise-based HTTP client'),
        'jest': ('Testing', 'JavaScript testing framework'),
        'typescript': ('Language', 'Typed JavaScript'),
        'tailwindcss': ('Styling', 'Utility-first CSS framework'),
        'socket.io': ('Real-time', 'Real-time bidirectional communication'),
        'passport': ('Auth', 'Authentication middleware'),
        'jsonwebtoken': ('Auth', 'JWT implementation'),
        'bcrypt': ('Auth', 'Password hashing'),
        'webpack': ('Build', 'Module bundler'),
        'vite': ('Build', 'Next-gen frontend tooling'),
        'eslint': ('Linting', 'JavaScript linter'),
        'prettier': ('Formatting', 'Code formatter'),
    }
    
    def __init__(self, repo_dir: str = "cloned_repo", model: str = "llama3.2:latest"):
        self.repo_dir = Path(repo_dir)
        self.model = model
        self.knowledge = ProjectKnowledge()
        self.vector_store = SimpleVectorStore()
    
    def analyze(self) -> ProjectKnowledge:
        """Perform complete deep analysis."""
        print("🔬 Starting deep project analysis...")
        
        # Phase 1: Analyze configuration files first (most important)
        print("   📦 Analyzing package configurations...")
        self._analyze_package_configs()
        
        # Phase 2: Analyze Docker setup
        print("   🐳 Analyzing Docker configuration...")
        self._analyze_docker_deep()
        
        # Phase 3: Analyze environment configuration
        print("   🔐 Analyzing environment configuration...")
        self._analyze_environment()
        
        # Phase 4: Analyze source code structure
        print("   📂 Analyzing source code structure...")
        self._analyze_source_structure()
        
        # Phase 5: Analyze CI/CD
        print("   🔄 Analyzing CI/CD configuration...")
        self._analyze_cicd()
        
        # Phase 6: Build knowledge chunks for vector store
        print("   🧠 Building knowledge base...")
        self._build_knowledge_chunks()
        
        # Phase 7: Use LLM for deep understanding
        print("   🤖 Generating AI understanding...")
        self._generate_llm_understanding()
        
        print("✅ Deep analysis complete!")
        return self.knowledge
    
    def _analyze_package_configs(self):
        """Deeply analyze package configuration files."""
        # Python: pyproject.toml, requirements.txt, setup.py, Pipfile
        self._analyze_python_packages()
        
        # Node.js: package.json
        self._analyze_node_packages()
        
        # Other: Cargo.toml, go.mod, pom.xml, build.gradle, composer.json
        self._analyze_other_packages()
    
    def _analyze_python_packages(self):
        """Deep analysis of Python package files."""
        # Check pyproject.toml
        pyproject = self.repo_dir / 'pyproject.toml'
        if pyproject.exists():
            content = self._read_file(pyproject)
            self._add_to_vector_store(content, 'pyproject.toml', 'config')
            
            # Extract project info
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if name_match:
                self.knowledge.name = name_match.group(1)
            
            desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
            if desc_match:
                self.knowledge.description = desc_match.group(1)
            
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if version_match:
                self.knowledge.version = version_match.group(1)
            
            # Extract dependencies
            deps_section = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if deps_section:
                deps = re.findall(r'["\']([^"\'>=<\s]+)', deps_section.group(1))
                for dep in deps:
                    self._add_dependency(dep, is_dev=False)
            
            self.knowledge.build_system = 'pip/pyproject.toml'
        
        # Check requirements.txt
        requirements = self.repo_dir / 'requirements.txt'
        if requirements.exists():
            content = self._read_file(requirements)
            self._add_to_vector_store(content, 'requirements.txt', 'config')
            
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    dep_name = re.split(r'[>=<\[\s]', line)[0]
                    version = ''
                    version_match = re.search(r'[>=<]+(.+)', line)
                    if version_match:
                        version = version_match.group(1).strip()
                    self._add_dependency(dep_name, version=version, is_dev=False)
            
            if not self.knowledge.build_system:
                self.knowledge.build_system = 'pip'
        
        # Check requirements-dev.txt or dev-requirements.txt
        for dev_req in ['requirements-dev.txt', 'dev-requirements.txt', 'requirements_dev.txt']:
            dev_file = self.repo_dir / dev_req
            if dev_file.exists():
                content = self._read_file(dev_file)
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        dep_name = re.split(r'[>=<\[\s]', line)[0]
                        self._add_dependency(dep_name, is_dev=True)
    
    def _analyze_node_packages(self):
        """Deep analysis of Node.js package.json."""
        package_json = self.repo_dir / 'package.json'
        if not package_json.exists():
            return
        
        try:
            content = self._read_file(package_json)
            self._add_to_vector_store(content, 'package.json', 'config')
            
            data = json.loads(content)
            
            self.knowledge.name = data.get('name', '')
            self.knowledge.description = data.get('description', '')
            self.knowledge.version = data.get('version', '')
            self.knowledge.build_system = 'npm'
            
            # Analyze scripts
            scripts = data.get('scripts', {})
            scripts_info = []
            for name, cmd in scripts.items():
                scripts_info.append(f"npm run {name}: {cmd}")
            
            if scripts_info:
                self._add_to_vector_store(
                    "Available npm scripts:\n" + "\n".join(scripts_info),
                    'package.json',
                    'scripts'
                )
            
            # Analyze dependencies
            for dep, version in data.get('dependencies', {}).items():
                self._add_dependency(dep, version=version, is_dev=False)
            
            for dep, version in data.get('devDependencies', {}).items():
                self._add_dependency(dep, version=version, is_dev=True)
            
        except json.JSONDecodeError:
            pass
    
    def _analyze_other_packages(self):
        """Analyze other package managers."""
        # Cargo.toml (Rust)
        cargo = self.repo_dir / 'Cargo.toml'
        if cargo.exists():
            content = self._read_file(cargo)
            self._add_to_vector_store(content, 'Cargo.toml', 'config')
            self.knowledge.build_system = 'cargo'
        
        # go.mod (Go)
        gomod = self.repo_dir / 'go.mod'
        if gomod.exists():
            content = self._read_file(gomod)
            self._add_to_vector_store(content, 'go.mod', 'config')
            self.knowledge.build_system = 'go modules'
        
        # pom.xml (Java/Maven)
        pom = self.repo_dir / 'pom.xml'
        if pom.exists():
            content = self._read_file(pom)
            self._add_to_vector_store(content, 'pom.xml', 'config')
            self.knowledge.build_system = 'maven'
        
        # build.gradle (Java/Gradle)
        gradle = self.repo_dir / 'build.gradle'
        if gradle.exists():
            content = self._read_file(gradle)
            self._add_to_vector_store(content, 'build.gradle', 'config')
            self.knowledge.build_system = 'gradle'
    
    def _add_dependency(self, name: str, version: str = "", is_dev: bool = False):
        """Add a dependency with enriched information."""
        name_lower = name.lower()
        
        # Look up purpose
        category, purpose = self.DEPENDENCY_PURPOSES.get(
            name_lower, 
            ('Unknown', f'{name} library')
        )
        
        dep_info = DependencyInfo(
            name=name,
            version=version,
            purpose=purpose,
            category=category,
            is_dev=is_dev
        )
        
        if is_dev:
            self.knowledge.dev_dependencies.append(dep_info)
        else:
            self.knowledge.dependencies.append(dep_info)


    def _analyze_docker_deep(self):
        """Deep analysis of Docker configuration."""
        # Analyze Dockerfile
        dockerfile = self.repo_dir / 'Dockerfile'
        if dockerfile.exists():
            content = self._read_file(dockerfile)
            self._add_to_vector_store(content, 'Dockerfile', 'docker')
            self._parse_dockerfile(content)
        
        # Analyze docker-compose files
        compose_files = ['docker-compose.yml', 'docker-compose.yaml', 'compose.yml', 'compose.yaml']
        for compose_name in compose_files:
            compose_file = self.repo_dir / compose_name
            if compose_file.exists():
                content = self._read_file(compose_file)
                self._add_to_vector_store(content, compose_name, 'docker')
                self._parse_docker_compose(content)
                break
    
    def _parse_dockerfile(self, content: str):
        """Parse Dockerfile for detailed information."""
        dockerfile_info = {
            'base_image': '',
            'stages': [],
            'exposed_ports': [],
            'env_vars': [],
            'workdir': '',
            'entrypoint': '',
            'cmd': '',
            'copy_instructions': [],
            'run_instructions': []
        }
        
        # Extract base image
        from_matches = re.findall(r'^FROM\s+([^\s]+)(?:\s+AS\s+(\w+))?', content, re.MULTILINE | re.IGNORECASE)
        for match in from_matches:
            image, stage = match
            dockerfile_info['base_image'] = image
            if stage:
                dockerfile_info['stages'].append(stage)
        
        # Extract ports
        port_matches = re.findall(r'^EXPOSE\s+(.+)$', content, re.MULTILINE | re.IGNORECASE)
        for ports in port_matches:
            dockerfile_info['exposed_ports'].extend(ports.split())
        
        # Extract environment variables
        env_matches = re.findall(r'^ENV\s+(\w+)(?:=|\s+)(.*)$', content, re.MULTILINE | re.IGNORECASE)
        for name, value in env_matches:
            dockerfile_info['env_vars'].append({'name': name, 'value': value.strip()})
        
        # Extract workdir
        workdir_match = re.search(r'^WORKDIR\s+(.+)$', content, re.MULTILINE | re.IGNORECASE)
        if workdir_match:
            dockerfile_info['workdir'] = workdir_match.group(1).strip()
        
        # Extract entrypoint
        entrypoint_match = re.search(r'^ENTRYPOINT\s+(.+)$', content, re.MULTILINE | re.IGNORECASE)
        if entrypoint_match:
            dockerfile_info['entrypoint'] = entrypoint_match.group(1).strip()
        
        # Extract CMD
        cmd_match = re.search(r'^CMD\s+(.+)$', content, re.MULTILINE | re.IGNORECASE)
        if cmd_match:
            dockerfile_info['cmd'] = cmd_match.group(1).strip()
        
        # Extract RUN instructions (for understanding build process)
        run_matches = re.findall(r'^RUN\s+(.+)$', content, re.MULTILINE | re.IGNORECASE)
        dockerfile_info['run_instructions'] = run_matches[:10]  # Limit to 10
        
        # Create a summary for vector store
        summary = f"""Dockerfile Analysis:
- Base Image: {dockerfile_info['base_image']}
- Multi-stage: {'Yes' if dockerfile_info['stages'] else 'No'}
- Exposed Ports: {', '.join(dockerfile_info['exposed_ports']) or 'None'}
- Working Directory: {dockerfile_info['workdir'] or 'Not set'}
- Entry Point: {dockerfile_info['entrypoint'] or 'Not set'}
- CMD: {dockerfile_info['cmd'] or 'Not set'}
- Build Steps: {len(dockerfile_info['run_instructions'])} RUN instructions
"""
        self._add_to_vector_store(summary, 'Dockerfile', 'docker-analysis')
    
    def _parse_docker_compose(self, content: str):
        """Parse docker-compose.yml for detailed service information."""
        try:
            import yaml
            data = yaml.safe_load(content)
        except:
            # Fallback to regex parsing
            self._parse_docker_compose_regex(content)
            return
        
        services = data.get('services', {})
        
        for service_name, service_config in services.items():
            service_info = ServiceInfo(name=service_name)
            
            if isinstance(service_config, dict):
                service_info.image = service_config.get('image', '')
                service_info.ports = service_config.get('ports', [])
                service_info.depends_on = service_config.get('depends_on', [])
                service_info.volumes = service_config.get('volumes', [])
                
                # Parse environment
                env = service_config.get('environment', {})
                if isinstance(env, dict):
                    service_info.environment = env
                elif isinstance(env, list):
                    for item in env:
                        if '=' in str(item):
                            key, val = str(item).split('=', 1)
                            service_info.environment[key] = val
                
                # Determine purpose based on image
                service_info.purpose = self._determine_service_purpose(
                    service_name, 
                    service_info.image
                )
            
            self.knowledge.services.append(service_info)
        
        # Determine architecture type
        if len(self.knowledge.services) > 3:
            self.knowledge.architecture_type = 'microservices'
        elif len(self.knowledge.services) > 1:
            self.knowledge.architecture_type = 'multi-container'
        else:
            self.knowledge.architecture_type = 'containerized'
        
        # Create summary for vector store
        services_summary = "Docker Compose Services:\n"
        for svc in self.knowledge.services:
            services_summary += f"\n- {svc.name}:\n"
            services_summary += f"  Image: {svc.image}\n"
            services_summary += f"  Purpose: {svc.purpose}\n"
            services_summary += f"  Ports: {', '.join(str(p) for p in svc.ports) or 'None'}\n"
            if svc.depends_on:
                services_summary += f"  Depends on: {', '.join(svc.depends_on)}\n"
        
        self._add_to_vector_store(services_summary, 'docker-compose.yml', 'docker-services')
    
    def _parse_docker_compose_regex(self, content: str):
        """Fallback regex parsing for docker-compose."""
        # Find services
        services = re.findall(r'^\s{2}(\w+):\s*$', content, re.MULTILINE)
        services = [s for s in services if s not in ['version', 'services', 'volumes', 'networks']]
        
        for service_name in services:
            service_info = ServiceInfo(name=service_name)
            
            # Try to find image
            image_match = re.search(
                rf'{service_name}:.*?image:\s*([^\n]+)',
                content, re.DOTALL
            )
            if image_match:
                service_info.image = image_match.group(1).strip()
            
            service_info.purpose = self._determine_service_purpose(
                service_name, 
                service_info.image
            )
            
            self.knowledge.services.append(service_info)
    
    def _determine_service_purpose(self, name: str, image: str) -> str:
        """Determine the purpose of a Docker service."""
        name_lower = name.lower()
        image_lower = image.lower() if image else ''
        
        # Database services
        if any(db in name_lower or db in image_lower for db in ['postgres', 'postgresql']):
            return 'PostgreSQL database for persistent data storage'
        if any(db in name_lower or db in image_lower for db in ['mysql', 'mariadb']):
            return 'MySQL/MariaDB database for persistent data storage'
        if 'mongo' in name_lower or 'mongo' in image_lower:
            return 'MongoDB NoSQL database'
        if 'redis' in name_lower or 'redis' in image_lower:
            return 'Redis in-memory cache and message broker'
        if 'elastic' in name_lower or 'elastic' in image_lower:
            return 'Elasticsearch for search and analytics'
        
        # Message queues
        if 'rabbit' in name_lower or 'rabbit' in image_lower:
            return 'RabbitMQ message broker'
        if 'kafka' in name_lower or 'kafka' in image_lower:
            return 'Apache Kafka event streaming'
        
        # Web servers
        if 'nginx' in name_lower or 'nginx' in image_lower:
            return 'Nginx web server/reverse proxy'
        if 'traefik' in name_lower or 'traefik' in image_lower:
            return 'Traefik reverse proxy and load balancer'
        
        # Application services
        if any(app in name_lower for app in ['app', 'api', 'web', 'backend', 'server']):
            return 'Main application service'
        if 'frontend' in name_lower or 'client' in name_lower:
            return 'Frontend web application'
        if 'worker' in name_lower or 'celery' in name_lower:
            return 'Background task worker'
        
        return 'Application service'
    
    def _analyze_environment(self):
        """Analyze environment configuration files."""
        env_files = ['.env.example', '.env.template', '.env.sample', '.env.local.example']
        
        for env_file in env_files:
            env_path = self.repo_dir / env_file
            if env_path.exists():
                content = self._read_file(env_path)
                self._add_to_vector_store(content, env_file, 'environment')
                
                # Parse environment variables
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Determine purpose
                        purpose = self._determine_env_var_purpose(key)
                        
                        self.knowledge.environment_vars.append({
                            'name': key,
                            'example_value': value,
                            'purpose': purpose,
                            'required': not value  # Empty value likely means required
                        })
                
                break
    
    def _determine_env_var_purpose(self, var_name: str) -> str:
        """Determine the purpose of an environment variable."""
        name_upper = var_name.upper()
        
        # Database
        if any(db in name_upper for db in ['DATABASE', 'DB_', 'POSTGRES', 'MYSQL', 'MONGO', 'REDIS']):
            return 'Database configuration'
        
        # Authentication
        if any(auth in name_upper for auth in ['SECRET', 'KEY', 'TOKEN', 'JWT', 'AUTH', 'PASSWORD']):
            return 'Authentication/Security'
        
        # API
        if 'API' in name_upper:
            return 'API configuration'
        
        # URLs
        if any(url in name_upper for url in ['URL', 'HOST', 'PORT', 'ENDPOINT']):
            return 'Service URL/endpoint'
        
        # Cloud
        if any(cloud in name_upper for cloud in ['AWS', 'AZURE', 'GCP', 'S3', 'BUCKET']):
            return 'Cloud service configuration'
        
        # Email
        if any(email in name_upper for email in ['SMTP', 'MAIL', 'EMAIL']):
            return 'Email service configuration'
        
        # Environment
        if any(env in name_upper for env in ['ENV', 'NODE_ENV', 'DEBUG', 'LOG']):
            return 'Application environment'
        
        return 'Application configuration'
    
    def _analyze_source_structure(self):
        """Analyze source code structure."""
        # Find entry points
        entry_point_files = [
            'main.py', 'app.py', 'server.py', 'index.py', '__main__.py',
            'index.js', 'server.js', 'app.js', 'main.js',
            'main.go', 'main.rs', 'Main.java', 'Program.cs'
        ]
        
        for entry_file in entry_point_files:
            entry_path = self.repo_dir / entry_file
            if entry_path.exists():
                content = self._read_file(entry_path)
                self._add_to_vector_store(content, entry_file, 'entry-point')
                self.knowledge.entry_points.append(entry_file)
        
        # Analyze source directories
        src_dirs = ['src', 'app', 'lib', 'api', 'server', 'backend', 'frontend']
        for src_dir in src_dirs:
            src_path = self.repo_dir / src_dir
            if src_path.exists() and src_path.is_dir():
                self._analyze_directory(src_path, src_dir)
        
        # Analyze root level source files
        self._analyze_root_source_files()
    
    def _analyze_directory(self, dir_path: Path, dir_name: str):
        """Analyze a source directory."""
        source_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.php', '.rb'}
        
        files_analyzed = 0
        for file_path in dir_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in source_extensions:
                if files_analyzed >= 20:  # Limit per directory
                    break
                
                # Skip test files for main analysis
                if 'test' in file_path.name.lower() or 'spec' in file_path.name.lower():
                    continue
                
                content = self._read_file(file_path)
                if content and len(content) < 10000:
                    rel_path = str(file_path.relative_to(self.repo_dir))
                    self._add_to_vector_store(content[:3000], rel_path, 'source')
                    files_analyzed += 1
    
    def _analyze_root_source_files(self):
        """Analyze source files in root directory."""
        source_extensions = {'.py', '.js', '.ts'}
        
        for file_path in self.repo_dir.iterdir():
            if file_path.is_file() and file_path.suffix in source_extensions:
                content = self._read_file(file_path)
                if content and len(content) < 10000:
                    self._add_to_vector_store(content[:3000], file_path.name, 'source')
    
    def _analyze_cicd(self):
        """Analyze CI/CD configuration."""
        cicd_files = [
            ('.github/workflows', 'GitHub Actions'),
            ('.gitlab-ci.yml', 'GitLab CI'),
            ('Jenkinsfile', 'Jenkins'),
            ('.travis.yml', 'Travis CI'),
            ('.circleci/config.yml', 'CircleCI'),
            ('azure-pipelines.yml', 'Azure Pipelines'),
            ('bitbucket-pipelines.yml', 'Bitbucket Pipelines')
        ]
        
        for path, name in cicd_files:
            full_path = self.repo_dir / path
            if full_path.exists():
                self.knowledge.ci_cd.append(name)
                
                if full_path.is_dir():
                    # GitHub Actions - analyze workflow files
                    for workflow in full_path.glob('*.yml'):
                        content = self._read_file(workflow)
                        self._add_to_vector_store(content, str(workflow.relative_to(self.repo_dir)), 'cicd')
                else:
                    content = self._read_file(full_path)
                    self._add_to_vector_store(content, path, 'cicd')


    def _build_knowledge_chunks(self):
        """Build knowledge chunks for the vector store."""
        # Create summary chunks
        
        # Dependencies summary
        if self.knowledge.dependencies:
            deps_summary = "Project Dependencies:\n"
            for dep in self.knowledge.dependencies[:20]:
                deps_summary += f"- {dep.name} ({dep.category}): {dep.purpose}\n"
            self._add_to_vector_store(deps_summary, 'dependencies', 'summary')
        
        # Services summary
        if self.knowledge.services:
            services_summary = "Docker Services Architecture:\n"
            for svc in self.knowledge.services:
                services_summary += f"- {svc.name}: {svc.purpose}\n"
                if svc.ports:
                    services_summary += f"  Ports: {', '.join(str(p) for p in svc.ports)}\n"
            self._add_to_vector_store(services_summary, 'services', 'summary')
        
        # Environment variables summary
        if self.knowledge.environment_vars:
            env_summary = "Environment Variables:\n"
            for env in self.knowledge.environment_vars[:15]:
                required = "REQUIRED" if env['required'] else "optional"
                env_summary += f"- {env['name']} ({required}): {env['purpose']}\n"
            self._add_to_vector_store(env_summary, 'environment', 'summary')
        
        # Store all chunks in knowledge
        self.knowledge.knowledge_chunks = self.vector_store.get_all()
    
    def _generate_llm_understanding(self):
        """Use LLM to generate deep understanding of the project."""
        # Get relevant context from vector store
        context = self._get_relevant_context("project overview architecture purpose features")
        
        # Generate project summary
        summary_prompt = f"""Based on this project information, provide a comprehensive summary.

PROJECT: {self.knowledge.name or 'Unknown'}
DESCRIPTION: {self.knowledge.description or 'Not provided'}
BUILD SYSTEM: {self.knowledge.build_system or 'Unknown'}
ARCHITECTURE: {self.knowledge.architecture_type or 'Unknown'}

CONTEXT FROM PROJECT FILES:
{context}

DEPENDENCIES ({len(self.knowledge.dependencies)} total):
{self._format_dependencies()[:1500]}

DOCKER SERVICES:
{self._format_services()[:1000]}

Provide:
1. A clear, compelling project description (2-3 sentences)
2. What problem it solves
3. Key technical highlights
4. Target users

Be specific and accurate based on the actual code and configuration."""

        self.knowledge.project_summary = self._call_model(summary_prompt, timeout=120) or ""
        
        # Generate technical overview
        tech_prompt = f"""Based on this project, provide a technical overview.

PROJECT: {self.knowledge.name}
BUILD SYSTEM: {self.knowledge.build_system}
ARCHITECTURE: {self.knowledge.architecture_type}

DEPENDENCIES:
{self._format_dependencies()[:2000]}

SERVICES:
{self._format_services()[:1500]}

ENTRY POINTS: {', '.join(self.knowledge.entry_points)}

Provide:
1. Technology stack breakdown
2. Architecture explanation
3. How components interact
4. Key design decisions evident from the code

Be technical but clear."""

        self.knowledge.technical_overview = self._call_model(tech_prompt, timeout=120) or ""
        
        # Generate setup guide
        setup_prompt = f"""Based on this project configuration, provide setup instructions.

BUILD SYSTEM: {self.knowledge.build_system}
HAS DOCKER: {'Yes' if self.knowledge.services else 'No'}

ENVIRONMENT VARIABLES:
{self._format_env_vars()[:1500]}

SERVICES:
{self._format_services()[:1000]}

Provide step-by-step setup instructions including:
1. Prerequisites
2. Installation steps
3. Environment configuration
4. How to run the application
5. How to run with Docker (if applicable)

Be specific with actual commands."""

        self.knowledge.setup_guide = self._call_model(setup_prompt, timeout=120) or ""
    
    def _format_dependencies(self) -> str:
        """Format dependencies for prompt."""
        lines = []
        for dep in self.knowledge.dependencies[:25]:
            lines.append(f"- {dep.name}: {dep.purpose} ({dep.category})")
        return "\n".join(lines)
    
    def _format_services(self) -> str:
        """Format services for prompt."""
        if not self.knowledge.services:
            return "No Docker services"
        
        lines = []
        for svc in self.knowledge.services:
            lines.append(f"- {svc.name}: {svc.purpose}")
            if svc.image:
                lines.append(f"  Image: {svc.image}")
            if svc.ports:
                lines.append(f"  Ports: {', '.join(str(p) for p in svc.ports)}")
        return "\n".join(lines)
    
    def _format_env_vars(self) -> str:
        """Format environment variables for prompt."""
        if not self.knowledge.environment_vars:
            return "No environment variables documented"
        
        lines = []
        for env in self.knowledge.environment_vars[:20]:
            required = "REQUIRED" if env['required'] else "optional"
            lines.append(f"- {env['name']} ({required}): {env['purpose']}")
        return "\n".join(lines)
    
    def _get_relevant_context(self, query: str, top_k: int = 5) -> str:
        """Get relevant context from vector store."""
        results = self.vector_store.search(query, top_k=top_k)
        
        context_parts = []
        for result in results:
            source = result['metadata'].get('source', 'unknown')
            context_parts.append(f"[From {source}]:\n{result['text'][:1000]}")
        
        return "\n\n".join(context_parts)
    
    def _add_to_vector_store(self, content: str, source: str, category: str):
        """Add content to vector store with metadata."""
        if not content or len(content.strip()) < 50:
            return
        
        # Chunk large content
        max_chunk_size = 1500
        if len(content) > max_chunk_size:
            chunks = self._chunk_content(content, max_chunk_size)
            for i, chunk in enumerate(chunks):
                self.vector_store.add(chunk, {
                    'source': source,
                    'category': category,
                    'chunk': i
                })
        else:
            self.vector_store.add(content, {
                'source': source,
                'category': category
            })
    
    def _chunk_content(self, content: str, max_size: int) -> List[str]:
        """Split content into chunks."""
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line) + 1
            if current_size + line_size > max_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            current_chunk.append(line)
            current_size += line_size
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def _read_file(self, path: Path) -> str:
        """Read file with error handling."""
        try:
            return path.read_text(encoding='utf-8', errors='ignore')
        except:
            try:
                return path.read_text(encoding='latin-1')
            except:
                return ""
    
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
            
        except Exception as e:
            print(f"⚠️  Model call failed: {e}")
            return None
    
    def get_context_for_readme(self, section: str) -> str:
        """Get relevant context for a specific README section."""
        section_queries = {
            'description': 'project purpose overview what it does',
            'features': 'features capabilities functionality',
            'installation': 'install setup requirements dependencies',
            'usage': 'usage run start commands examples',
            'docker': 'docker compose services containers',
            'api': 'api endpoints routes http',
            'configuration': 'environment variables config settings',
            'architecture': 'architecture structure components services'
        }
        
        query = section_queries.get(section, section)
        return self._get_relevant_context(query, top_k=3)
    
    def save_knowledge(self, path: str = "project_knowledge.json"):
        """Save the knowledge base to disk."""
        data = {
            'name': self.knowledge.name,
            'description': self.knowledge.description,
            'version': self.knowledge.version,
            'build_system': self.knowledge.build_system,
            'architecture_type': self.knowledge.architecture_type,
            'entry_points': self.knowledge.entry_points,
            'dependencies': [
                {'name': d.name, 'version': d.version, 'purpose': d.purpose, 'category': d.category}
                for d in self.knowledge.dependencies
            ],
            'services': [
                {'name': s.name, 'image': s.image, 'purpose': s.purpose, 'ports': s.ports}
                for s in self.knowledge.services
            ],
            'environment_vars': self.knowledge.environment_vars,
            'ci_cd': self.knowledge.ci_cd,
            'project_summary': self.knowledge.project_summary,
            'technical_overview': self.knowledge.technical_overview,
            'setup_guide': self.knowledge.setup_guide
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Also save vector store
        self.vector_store.save(path.replace('.json', '_vectors.json'))
