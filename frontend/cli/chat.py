#!/usr/bin/env python3
"""
Interactive OpenOps CLI - Chat-like interface
"""

from openops import OpenOpsCLI
import sys

def interactive_mode():
    """Run CLI in interactive chat mode"""
    cli = OpenOpsCLI()
    
    print("=" * 60)
    print("OpenOps Interactive Mode")
    print("=" * 60)
    print("Type your questions naturally, or use commands:")
    print("  • 'health' - Check system health")
    print("  • 'services' - List available services")
    print("  • 'help' - Show this help")
    print("  • 'quit' or 'exit' - Exit")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\nOpenOps> ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            elif user_input.lower() == 'help':
                print("""Available commands:
  • health - Check system health
  • services - List available services
  • search <query> - Search logs
  
Or ask natural language questions like:
  • "What database errors happened?"
  • "Show me payment service issues"
  • "Any authentication failures?"
                """)
                continue
            
            elif user_input.lower() == 'health':
                cli.health()
                continue
            
            elif user_input.lower() == 'services':
                cli.services()
                continue
            
            elif user_input.lower().startswith('search '):
                query = user_input[7:].strip()
                if query:
                    cli.search(query, limit=5)
                else:
                    print("ERROR: Please provide a search query")
                continue
            
            # Default: treat as natural language query
            cli.query(user_input, limit=3)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    interactive_mode()