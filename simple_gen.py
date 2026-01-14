import subprocess
import os
import json
import re
from typing import List, Tuple

from analyzer import EnhancedProjectAnalyzer
from prompts import create_comprehensive_prompt




def generate_comprehensive_readme(analyzer: EnhancedProjectAnalyzer, key_files: List[Tuple[str, str]],
                                repo_url: str, model: str = "llama3.2:latest") -> bool:
    """Generate comprehensive README with enhanced prompting."""
    print("🤖 Generating comprehensive README...")
    print(f"📊 Project complexity: {analyzer.project_data['setup_difficulty']} ({analyzer.project_data['complexity_score']} points)")

    prompt = create_comprehensive_prompt(analyzer, key_files, repo_url)

    try:
        # Use longer timeout for complex projects
        timeout = 1600 if analyzer.project_data['complexity_score'] > 50 else 800

        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode('utf-8'),
            capture_output=True,
            timeout=timeout
        )

        if result.returncode != 0:
            print(f"❌ Ollama error: {result.stderr.decode()}")
            return False

        output = result.stdout.decode('utf-8').strip()

        # Enhanced output cleaning
        # Remove code block markers
        if output.startswith('```markdown'):
            output = output[11:]
        elif output.startswith('```'):
            output = output[3:]
        if output.endswith('```'):
            output = output[:-3]

        # Remove any meta-commentary at the beginning
        lines = output.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#') and not stripped.startswith('##') and len(stripped) > 1:
                start_idx = i
                break

        if start_idx > 0:
            output = '\n'.join(lines[start_idx:])

        # Clean up any remaining artifacts
        output = re.sub(r'\[.*?\]', '', output, flags=re.MULTILINE)
        output = re.sub(r'^\s*Note:.*', '', output, flags=re.MULTILINE | re.IGNORECASE)  # Remove notes

        # Save README
        with open("README.md", "w", encoding='utf-8') as f:
            f.write(output.strip())

        # Save analysis data for debugging
        if os.getenv('DEBUG'):
            with open("project_analysis.json", "w", encoding='utf-8') as f:
                json.dump(analyzer.project_data, f, indent=2, default=str)

        print("✅ Comprehensive README.md generated!")
        print(f"📄 Size: {len(output):,} characters")
        print(f"🎯 Features detected: {len(analyzer.project_data['features'])}")
        print(f"🛠 Technologies identified: {len(analyzer.project_data['technologies'])}")
        return True

    except subprocess.TimeoutExpired:
        print("❌ Generation timed out (project might be very complex)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
