import argparse
import subprocess
import git
import os
import shutil
from pathlib import Path
import json
import re
from typing import List, Tuple

# Simplified patterns for better accuracy
IGNORE_PATTERNS = {
    'directories': {'.git', '__pycache__', 'node_modules', '.vscode', '.idea', 'dist', 'build', 'venv', 'env'},
    'files': {'.gitignore', '.env', '.DS_Store', 'Thumbs.db', '*.log', '*.lock'},
    'extensions': {'.pyc', '.pyo', '.so', '.dll', '.exe', '.class', '.jar'}
}

class SimpleProjectAnalyzer:
    def __init__(self, repo_dir: str = "cloned_repo"):
        self.repo_dir = Path(repo_dir)
        self.project_data = {
            'name': '',
            'description': '',
            'main_language': '',
            'frameworks': [],
            'has_docker': False,
            'docker_services': [],
            'entry_point': '',
            'install_cmd': '',
            'run_cmd': '',
            'test_cmd': '',
            'dependencies': [],
            'ports': [],
            'env_vars': []
        }

    def should_ignore(self, file_path: Path) -> bool:
        """Simple file filtering."""
        for part in file_path.parts:
            if part in IGNORE_PATTERNS['directories']:
                return True
        if file_path.suffix in IGNORE_PATTERNS['extensions']:
            return True
        return False

    def analyze_package_json(self):
        """Extract real info from package.json."""
        pkg_file = self.repo_dir / 'package.json'
        if not pkg_file.exists():
            return

        try:
            with open(pkg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.project_data.update({
                'name': data.get('name', ''),
                'description': data.get('description', ''),
                'main_language': 'JavaScript',
                'entry_point': data.get('main', 'index.js')
            })

            # Get actual scripts
            scripts = data.get('scripts', {})
            if 'start' in scripts:
                self.project_data['run_cmd'] = 'npm start'
            elif 'dev' in scripts:
                self.project_data['run_cmd'] = 'npm run dev'

            if 'test' in scripts:
                self.project_data['test_cmd'] = 'npm test'

            self.project_data['install_cmd'] = 'npm install'

            # Detect frameworks from dependencies
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            if 'react' in deps:
                self.project_data['frameworks'].append('React')
            if 'vue' in deps:
                self.project_data['frameworks'].append('Vue.js')
            if 'express' in deps:
                self.project_data['frameworks'].append('Express.js')
            if 'next' in deps:
                self.project_data['frameworks'].append('Next.js')

        except Exception as e:
            print(f"Warning: Could not parse package.json: {e}")

    def analyze_python_files(self):
        """Extract info from Python project files."""
        # Check requirements.txt
        req_file = self.repo_dir / 'requirements.txt'
        if req_file.exists():
            self.project_data['main_language'] = 'Python'
            self.project_data['install_cmd'] = 'pip install -r requirements.txt'

            try:
                with open(req_file, 'r') as f:
                    deps = [line.strip().split('==')[0].split('>=')[0]
                           for line in f if line.strip() and not line.startswith('#')]

                if any('django' in dep.lower() for dep in deps):
                    self.project_data['frameworks'].append('Django')
                    self.project_data['run_cmd'] = 'python manage.py runserver'
                elif any('flask' in dep.lower() for dep in deps):
                    self.project_data['frameworks'].append('Flask')
                    self.project_data['run_cmd'] = 'python app.py'
                elif any('fastapi' in dep.lower() for dep in deps):
                    self.project_data['frameworks'].append('FastAPI')
                    self.project_data['run_cmd'] = 'uvicorn main:app --reload'

            except Exception as e:
                print(f"Warning: Could not parse requirements.txt: {e}")

        # Find main Python file
        python_files = ['main.py', 'app.py', 'run.py', 'server.py', 'manage.py']
        for py_file in python_files:
            if (self.repo_dir / py_file).exists():
                self.project_data['entry_point'] = py_file
                if not self.project_data['run_cmd']:
                    self.project_data['run_cmd'] = f'python {py_file}'
                break

    def analyze_docker(self):
        """Analyze Docker files for accurate setup info."""
        dockerfile = self.repo_dir / 'Dockerfile'
        compose_file = None

        # Find docker-compose file
        for compose_name in ['docker-compose.yml', 'docker-compose.yaml', 'compose.yml']:
            if (self.repo_dir / compose_name).exists():
                compose_file = self.repo_dir / compose_name
                break

        if dockerfile.exists():
            self.project_data['has_docker'] = True
            try:
                with open(dockerfile, 'r') as f:
                    content = f.read()

                # Extract exposed ports
                port_matches = re.findall(r'EXPOSE\s+(\d+)', content)
                self.project_data['ports'].extend(port_matches)

                # Extract environment variables
                env_matches = re.findall(r'ENV\s+(\w+)', content)
                self.project_data['env_vars'].extend(env_matches)

            except Exception as e:
                print(f"Warning: Could not parse Dockerfile: {e}")

        if compose_file:
            try:
                with open(compose_file, 'r') as f:
                    content = f.read()

                # Extract services (simple regex approach)
                services = re.findall(r'^\s*(\w+):\s*$', content, re.MULTILINE)
                # Filter out common YAML keys
                services = [s for s in services if s not in ['version', 'services', 'volumes', 'networks']]
                self.project_data['docker_services'] = services[:5]  # Limit to 5 services

                # Extract ports from compose
                port_matches = re.findall(r'"(\d+):\d+"', content)
                self.project_data['ports'].extend(port_matches)

            except Exception as e:
                print(f"Warning: Could not parse docker-compose file: {e}")

    def get_key_files(self) -> List[Tuple[str, str]]:
        """Get content from only the most important files."""
        important_files = []

        # Priority files to analyze
        priority_files = [
            'package.json', 'requirements.txt', 'Dockerfile', 'docker-compose.yml',
            'docker-compose.yaml', 'README.md', 'main.py', 'app.py', 'index.js',
            'server.js', 'manage.py'
        ]

        for filename in priority_files:
            file_path = self.repo_dir / filename
            if file_path.exists() and not self.should_ignore(file_path):
                content = self._read_file(file_path)
                if content and len(content) < 5000:  # Skip very large files
                    important_files.append((filename, content))

        return important_files

    def _read_file(self, file_path: Path) -> str:
        """Read file with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Truncate if too long
                if len(content) > 3000:
                    content = content[:2000] + "\n\n... [TRUNCATED] ..."
                return content
        except:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()[:2000]
            except:
                return ""

def clone_repo(repo_url: str, dest_dir: str = "cloned_repo") -> bool:
    """Clone repository."""
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    print(f"🔄 Cloning {repo_url}...")
    try:
        git.Repo.clone_from(repo_url, dest_dir)
        print("✅ Repository cloned!")
        return True
    except Exception as e:
        print(f"❌ Error cloning: {e}")
        return False

def create_simple_prompt(analyzer: SimpleProjectAnalyzer, key_files: List[Tuple[str, str]], repo_url: str) -> str:
    """Create a focused, accurate prompt."""

    project_name = analyzer.project_data.get('name') or repo_url.split('/')[-1].replace('.git', '')

    # Build file content section
    file_contents = ""
    for filename, content in key_files:
        file_contents += f"\n=== {filename} ===\n{content}\n"

    docker_info = ""
    if analyzer.project_data['has_docker']:
        docker_info = f"""
DOCKER SETUP DETECTED:
- Services: {', '.join(analyzer.project_data['docker_services']) if analyzer.project_data['docker_services'] else 'Standard container'}
- Ports: {', '.join(analyzer.project_data['ports']) if analyzer.project_data['ports'] else 'Not specified'}
"""

    prompt = f"""Create a simple, accurate README.md for this project. Use ONLY information you can verify from the files below.

PROJECT: {project_name}
REPO: {repo_url}
LANGUAGE: {analyzer.project_data['main_language']}
FRAMEWORKS: {', '.join(analyzer.project_data['frameworks']) if analyzer.project_data['frameworks'] else 'None detected'}
{docker_info}

KEY FILES CONTENT:
{file_contents}

Create a README with these sections ONLY if you can verify the information:

# {project_name}

{analyzer.project_data['description'] if analyzer.project_data['description'] else '[Write a brief description based on the code/files above]'}

## 🚀 Quick Start

### Prerequisites
[List only what you can see is actually required]

### Installation
```bash
git clone {repo_url}
cd {project_name}
{analyzer.project_data['install_cmd'] if analyzer.project_data['install_cmd'] else '[Add install command based on files above]'}
```

### Running the Application
```bash
{analyzer.project_data['run_cmd'] if analyzer.project_data['run_cmd'] else '[Add run command based on files above]'}
```

{f'''### Using Docker
```bash
docker-compose up
```
Access at: http://localhost:{analyzer.project_data["ports"][0] if analyzer.project_data["ports"] else "3000"}
''' if analyzer.project_data['has_docker'] else ''}

{f'''### Testing
```bash
{analyzer.project_data['test_cmd']}
```
''' if analyzer.project_data['test_cmd'] else ''}

## 📁 Project Structure
[Describe the main directories/files you can see, keep it simple]

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

RULES:
- Be accurate - only include what you can verify from the files
- Keep it simple and practical
- Don't add placeholder text in brackets
- Don't mention files that aren't in the project
- Focus on how to actually use the project
- If Docker is present, include Docker instructions
- Make all commands copy-pasteable
"""

    return prompt

def generate_readme(analyzer: SimpleProjectAnalyzer, key_files: List[Tuple[str, str]],
                   repo_url: str, model: str = "llama3.2:latest") -> bool:
    """Generate README with better prompting."""
    print("🤖 Generating README...")

    prompt = create_simple_prompt(analyzer, key_files, repo_url)

    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode('utf-8'),
            capture_output=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            print(f"❌ Ollama error: {result.stderr.decode()}")
            return False

        output = result.stdout.decode('utf-8').strip()

        # Clean output
        if output.startswith('```markdown'):
            output = output[11:]
        if output.startswith('```'):
            output = output[3:]
        if output.endswith('```'):
            output = output[:-3]

        # Remove any explanatory text before the actual README
        lines = output.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('#') and not line.strip().startswith('##'):
                start_idx = i
                break

        if start_idx > 0:
            output = '\n'.join(lines[start_idx:])

        # Save README
        with open("README.md", "w", encoding='utf-8') as f:
            f.write(output.strip())

        print("✅ README.md generated!")
        print(f"📄 Size: {len(output):,} characters")
        return True

    except subprocess.TimeoutExpired:
        print("❌ Generation timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Simple, accurate README generator")
    parser.add_argument('--repo', required=True, help='Git repository URL')
    parser.add_argument('--model', default='llama3.2:latest', help='Ollama model')
    parser.add_argument('--debug', action='store_true', help='Keep debug files')

    args = parser.parse_args()

    print("🚀 Simple README Generator")
    print(f"📂 Repository: {args.repo}")

    # Clone repo
    if not clone_repo(args.repo):
        return 1

    # Analyze project
    print("🔍 Analyzing project...")
    analyzer = SimpleProjectAnalyzer()
    analyzer.analyze_package_json()
    analyzer.analyze_python_files()
    analyzer.analyze_docker()

    print(f"📊 Found: {analyzer.project_data['main_language']} project")
    if analyzer.project_data['frameworks']:
        print(f"   Frameworks: {', '.join(analyzer.project_data['frameworks'])}")
    if analyzer.project_data['has_docker']:
        print(f"   Docker: Yes ({len(analyzer.project_data['docker_services'])} services)")

    # Get key files
    key_files = analyzer.get_key_files()
    print(f"📋 Analyzing {len(key_files)} key files")

    # Generate README
    success = generate_readme(analyzer, key_files, args.repo, args.model)

    if success:
        print("\n🎉 Done! Check README.md")
    else:
        print("\n❌ Failed to generate README")
        print("💡 Tips:")
        print("• Make sure Ollama is running: ollama serve")
        print(f"• Pull model: ollama pull {args.model}")
        print("• Try smaller model: --model llama3.2:1b")
        return 1

    # Cleanup
    if not args.debug:
        try:
            shutil.rmtree("cloned_repo")
        except:
            pass

    return 0

if __name__ == "__main__":
    exit(main())
