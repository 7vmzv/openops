#!/usr/bin/env python3
"""
OpenOps CLI Demo - Showcase the capabilities
"""

import time
import subprocess
import sys

def run_command(cmd):
    """Run CLI command and show output"""
    print(f"$ python openops.py {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            [sys.executable, "openops.py"] + cmd.split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out")
    except Exception as e:
        print(f"ERROR: Error running command: {e}")
    
    print("\n" + "=" * 60 + "\n")
    time.sleep(2)

def main():
    """Run CLI demo"""
    print("OpenOps CLI Demo")
    print("=" * 60)
    print("This demo showcases the OpenOps CLI capabilities.")
    print("Make sure the API Gateway is running at http://localhost:8000")
    print("=" * 60)
    
    input("Press Enter to start the demo...")
    print()
    
    # Demo commands
    commands = [
        "health",
        "services", 
        'query "What database errors are happening?"',
        'query "Show me authentication failures" --level ERROR --limit 3',
        'search "timeout" --limit 5',
        'search "payment" --service payment-service'
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"Demo {i}/{len(commands)}: {cmd}")
        run_command(cmd)
        
        if i < len(commands):
            input("Press Enter for next demo...")
            print()
    
    print("Demo completed!")
    print("\nTry the interactive mode:")
    print("  python chat.py")

if __name__ == "__main__":
    main()