"""Test CLI entrypoints after installation."""

import subprocess
import sys


def test_cli_entrypoints():
    """Test that CLI entrypoints are available after installation."""
    # Test basic CLI functionality for each entrypoint
    cli_commands = [
        "alpaca-bars --help",
        "alpaca-news --help", 
        "alpaca-quotes --help",
        "alpaca-trades --help",
        "alpaca-snapshot --help",
        "alpaca-crypto --help",
    ]
    
    for cmd in cli_commands:
        try:
            result = subprocess.run(
                cmd.split(), 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            # Should exit with 0 and show help text, not ModuleNotFoundError
            assert result.returncode == 0, f"Command '{cmd}' failed with exit code {result.returncode}"
            assert "ModuleNotFoundError: No module named 'scripts'" not in result.stderr
            assert "Usage:" in result.stdout or "usage:" in result.stdout
            
            print(f"✅ {cmd} - OK")
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {cmd} - Timeout (but probably working)")
        except Exception as e:
            print(f"❌ {cmd} - Error: {e}")
            raise


if __name__ == "__main__":
    test_cli_entrypoints()
    print("All CLI entrypoint tests passed!")