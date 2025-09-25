#!/usr/bin/env python3
"""
Demo runner script for OpenHands Agent SDK experiments.
This script helps run demos from any location by setting up the proper environment.
"""

import os
import sys
import subprocess
from pathlib import Path

def find_agent_sdk_path():
    """Find the agent-sdk directory."""
    current_dir = Path.cwd()
    
    # Check common locations
    possible_paths = [
        current_dir / "agent-sdk",
        current_dir.parent / "agent-sdk", 
        Path.home() / "agent-sdk",
        Path("/workspace/project/agent-sdk"),
    ]
    
    for path in possible_paths:
        if path.exists() and (path / "openhands").exists():
            return path
    
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_demo.py <demo_file.py>")
        print("\nAvailable demos:")
        demo_dir = Path(__file__).parent
        for demo_file in demo_dir.glob("*.py"):
            if demo_file.name != "run_demo.py":
                print(f"  - {demo_file.name}")
        sys.exit(1)
    
    demo_file = sys.argv[1]
    demo_path = Path(__file__).parent / demo_file
    
    if not demo_path.exists():
        print(f"Error: Demo file '{demo_file}' not found.")
        sys.exit(1)
    
    # Find agent-sdk directory
    agent_sdk_path = find_agent_sdk_path()
    if not agent_sdk_path:
        print("Error: Could not find agent-sdk directory.")
        print("Please ensure the agent-sdk repository is cloned and built.")
        print("\nTo set up:")
        print("  git clone https://github.com/All-Hands-AI/agent-sdk/")
        print("  cd agent-sdk")
        print("  make build")
        sys.exit(1)
    
    print(f"Found agent-sdk at: {agent_sdk_path}")
    
    # Check if ANTHROPIC_API_KEY is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please set it before running demos:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Change to agent-sdk directory and run the demo
    print(f"Running demo: {demo_file}")
    print("=" * 50)
    
    try:
        os.chdir(agent_sdk_path)
        
        # Set up environment to include the agent-sdk in Python path
        env = os.environ.copy()
        current_pythonpath = env.get("PYTHONPATH", "")
        if current_pythonpath:
            env["PYTHONPATH"] = f"{agent_sdk_path}:{current_pythonpath}"
        else:
            env["PYTHONPATH"] = str(agent_sdk_path)
        
        result = subprocess.run([
            "uv", "run", "python", str(demo_path)
        ], env=env, check=True)
        print("=" * 50)
        print("Demo completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error running demo: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
        sys.exit(1)

if __name__ == "__main__":
    main()