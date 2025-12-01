#!/usr/bin/env python3
"""
Quick launcher for README Generator v2.0

Usage:
    python run.py <github_repo_url>
    python run.py https://github.com/user/project
    python run.py https://github.com/user/project --simple  # Use old simple mode
"""

import sys
import os


def main():
    # Handle help flag
    if '--help' in sys.argv or '-h' in sys.argv or len(sys.argv) < 2:
        print("📝 README Generator v2.0")
        print("\nUsage:")
        print("  python run.py <github_repo_url>")
        print("  python run.py <github_repo_url> --simple    # Simple mode (no questions)")
        print("  python run.py <github_repo_url> --debug     # Keep debug files")
        print("\nExamples:")
        print("  python run.py https://github.com/user/project")
        print("  python run.py https://github.com/user/project --simple")
        return 1
    
    repo_url = sys.argv[1]
    
    # Check for flags
    simple_mode = '--simple' in sys.argv
    debug_mode = '--debug' in sys.argv
    
    # Get model from args if specified
    model = 'llama3.2:latest'
    for i, arg in enumerate(sys.argv):
        if arg == '--model' and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]
    
    if simple_mode:
        # Use the original simple generator
        print("🚀 Running in SIMPLE mode (no interactive questions)")
        from main import main as simple_main
        sys.argv = ['main.py', '--repo', repo_url, '--model', model]
        if debug_mode:
            sys.argv.append('--debug')
        return simple_main()
    else:
        # Use the new interactive generator
        print("🚀 Running in INTERACTIVE mode")
        from readme_generator_v2 import ReadmeGeneratorV2
        generator = ReadmeGeneratorV2(model=model, debug=debug_mode)
        success = generator.run(repo_url)
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
