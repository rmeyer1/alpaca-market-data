#!/usr/bin/env python3
"""Add main() functions to CLI scripts that are missing them."""

import os
import glob

def add_main_function(script_path):
    """Add main function to a CLI script."""
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Check if main function already exists
    if 'def main():' in content:
        print(f"✅ {os.path.basename(script_path)} already has main() function")
        return
    
    # Check if it has the if __name__ == "__main__" pattern
    if 'if __name__ == "__main__":' in content:
        # Add main function after the if __name__ == "__main__" block
        # Find the line after if __name__ == "__main__": and indent the app() call
        
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            if line.strip() == 'if __name__ == "__main__":':
                # Add the main function first
                new_lines.extend([
                    'def main():',
                    '    """Main entry point for CLI commands."""',
                    '    app()',
                    '',
                    '',
                    line  # Keep the original if __name__ line
                ])
            else:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        
        with open(script_path, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Added main() function to {os.path.basename(script_path)}")
    else:
        print(f"⚠️  {os.path.basename(script_path)} doesn't have expected pattern, skipping")

def main():
    """Add main functions to all CLI scripts."""
    script_dir = "scripts"
    script_files = [
        "get_bars.py",
        "get_quotes.py", 
        "get_news.py",
        "get_snapshot.py",
        "get_trades.py",
        "get_option_quotes.py",
        "get_option_snapshot.py", 
        "get_option_trades.py",
        "crypto_cli.py"
    ]
    
    for script_file in script_files:
        script_path = os.path.join(script_dir, script_file)
        if os.path.exists(script_path):
            add_main_function(script_path)
        else:
            print(f"⚠️  Script {script_file} not found")

if __name__ == "__main__":
    main()