#!/usr/bin/env python3
"""
Quick launcher for README Generator v2.0

Supports multiple LLM providers:
- Ollama (local, default)
- OpenAI (gpt-4o, gpt-4o-mini, etc.)
- Claude (claude-3-5-sonnet, etc.)

Usage:
    python run.py <github_repo_url>
    python run.py <github_repo_url> --model gpt-4o
    python run.py <github_repo_url> --model claude-3-5-sonnet-20241022
"""

import sys
import os


def print_help():
    print("""
📝 README Generator v2.0 - Interactive & Multi-Provider

USAGE:
    python run.py <github_repo_url> [options]

OPTIONS:
    --model <name>     Model to use (auto-detects provider)
    --api-key <key>    API key for OpenAI/Claude
    --simple           Simple mode (no interactive questions)
    --debug            Keep debug files and cloned repo

MODELS:
    Ollama (local, default):
        llama3.2:latest, llama3.2:3b, mistral, codellama, etc.
    
    OpenAI (requires OPENAI_API_KEY or --api-key):
        gpt-4o, gpt-4o-mini, gpt-4-turbo, o1-preview, o1-mini
    
    Claude (requires ANTHROPIC_API_KEY or --api-key):
        claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-haiku-20240307

EXAMPLES:
    # Using Ollama (default)
    python run.py https://github.com/user/project
    python run.py https://github.com/user/project --model llama3.2:3b
    
    # Using OpenAI
    export OPENAI_API_KEY=sk-...
    python run.py https://github.com/user/project --model gpt-4o
    
    # Using Claude
    export ANTHROPIC_API_KEY=sk-ant-...
    python run.py https://github.com/user/project --model claude-3-5-sonnet-20241022
    
    # With explicit API key
    python run.py https://github.com/user/project --model gpt-4o --api-key sk-...
    
    # Simple mode (no questions)
    python run.py https://github.com/user/project --simple
""")


def main():
    # Handle help flag
    if '--help' in sys.argv or '-h' in sys.argv or len(sys.argv) < 2:
        print_help()
        return 1
    
    repo_url = sys.argv[1]
    
    # Check for flags
    simple_mode = '--simple' in sys.argv
    debug_mode = '--debug' in sys.argv
    
    # Get model from args
    model = 'llama3.2:latest'
    for i, arg in enumerate(sys.argv):
        if arg == '--model' and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]
    
    # Get API key from args
    api_key = None
    for i, arg in enumerate(sys.argv):
        if arg == '--api-key' and i + 1 < len(sys.argv):
            api_key = sys.argv[i + 1]
    
    if simple_mode:
        # Use the original simple generator
        print("🚀 Running in SIMPLE mode (no interactive questions)")
        from main import main as simple_main
        sys.argv = ['main.py', '--repo', repo_url, '--model', model]
        if debug_mode:
            sys.argv.append('--debug')
        return simple_main()
    
    else:
        # Use v2 interactive generator with provider support
        print("🚀 Running INTERACTIVE mode")
        try:
            from readme_generator_v2 import ReadmeGeneratorV2
            generator = ReadmeGeneratorV2(model=model, debug=debug_mode, api_key=api_key)
            success = generator.run(repo_url)
            return 0 if success else 1
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            print("\n💡 Tip: Set API key via environment variable or --api-key flag")
            return 1


if __name__ == "__main__":
    sys.exit(main())
