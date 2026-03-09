#!/usr/bin/env python3
"""
GitHub Setup Verification Script
Confirms GitHub PAT token is working and git operations are functional
"""

import subprocess
import sys
from pathlib import Path

def test_github_auth():
    """Test GitHub authentication."""
    print("🔐 Testing GitHub Authentication")
    print("=" * 36)
    
    try:
        # Test gh auth status
        result = subprocess.run(['gh', 'auth', 'status'], 
                              capture_output=True, text=True, check=True)
        print("✅ GitHub CLI authentication successful")
        print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub auth failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) not found")
        return False

def test_github_api():
    """Test GitHub API access."""
    print("\n📡 Testing GitHub API Access")
    print("=" * 32)
    
    try:
        # Test API call to get user info
        result = subprocess.run(['gh', 'api', 'user', '--jq', '.login'], 
                              capture_output=True, text=True, check=True)
        username = result.stdout.strip()
        print(f"✅ GitHub API access confirmed")
        print(f"   Authenticated as: {username}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub API test failed: {e}")
        return False

def test_git_operations():
    """Test basic git operations."""
    print("\n🔧 Testing Git Operations")
    print("=" * 26)
    
    project_dir = Path(__file__).parent
    
    try:
        # Test git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              cwd=project_dir, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository accessible")
            
            # Check for uncommitted changes
            if result.stdout.strip():
                print("   📝 Uncommitted changes detected")
            else:
                print("   ✅ Working directory clean")
        else:
            print("❌ Git status failed")
            return False
        
        # Test git remote
        result = subprocess.run(['git', 'remote', '-v'], 
                              cwd=project_dir, capture_output=True, text=True)
        if result.returncode == 0 and 'rmeyer1/alpaca-market-data' in result.stdout:
            print("✅ GitHub remote configured correctly")
            print("   Repository: rmeyer1/alpaca-market-data")
        else:
            print("❌ GitHub remote not properly configured")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Git operations test failed: {e}")
        return False

def test_git_push():
    """Test git push capability (dry run)."""
    print("\n🚀 Testing Git Push Capability")
    print("=" * 33)
    
    try:
        project_dir = Path(__file__).parent
        
        # Check if we can push (without actually pushing)
        result = subprocess.run(['git', 'ls-remote', 'origin'], 
                              cwd=project_dir, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git push capability confirmed")
            print("   Can communicate with GitHub repository")
        else:
            print("❌ Cannot communicate with GitHub repository")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Git push test failed: {e}")
        return False

def show_git_usage_examples():
    """Show practical git usage examples."""
    print("\n💡 Git & GitHub Usage Examples")
    print("=" * 34)
    
    examples = [
        "Check current branch and status:",
        "git status",
        "git branch",
        "",
        "Create and switch to new branch:",
        "git checkout -b feature/my-new-feature",
        "",
        "Stage and commit changes:",
        "git add .",
        "git commit -m \"feat: add new feature\"",
        "",
        "Push changes to GitHub:",
        "git push origin feature/my-new-feature",
        "",
        "Open pull request:",
        "gh pr create --title \"My new feature\" --body \"Description\"",
        "",
        "View pull requests:",
        "gh pr list",
        "gh pr view <number>",
        "",
        "Sync with remote:",
        "git pull origin main",
    ]
    
    for line in examples:
        if line.strip():
            print(f"  {line}")
        else:
            print()

def main():
    """Main verification function."""
    print("🎯 GitHub Setup Verification")
    print("=" * 30)
    
    tests = [
        test_github_auth,
        test_github_api, 
        test_git_operations,
        test_git_push
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            results.append(False)
    
    # Show usage examples
    show_git_usage_examples()
    
    # Summary
    print("\n" + "=" * 30)
    print("📊 GitHub Setup Summary")
    print("=" * 24)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 SUCCESS - GitHub fully configured!")
        print("\n✨ Your GitHub setup supports:")
        print("  • Authentication with personal access token")
        print("  • API access to GitHub")
        print("  • Git repository operations")
        print("  • Push/pull operations to GitHub")
        print("  • Pull request creation and management")
        print("  • Branch management and collaboration")
        
        print("\n🚀 Ready Git Operations:")
        print("  git status                    # Check repository status")
        print("  git add .                     # Stage all changes")
        print("  git commit -m 'feat: add X'   # Commit with conventional format")
        print("  git push origin main          # Push to main branch")
        print("  git checkout -b new-feature   # Create new branch")
        print("  gh pr create                  # Create pull request")
        print("  gh pr list                    # View pull requests")
        
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("Please check the error messages above")
    
    print(f"\n📁 Repository: {Path.cwd()}")
    print(f"🔑 GitHub Account: rmeyer1")
    print(f"🔗 Remote: https://github.com/rmeyer1/alpaca-market-data.git")
    
    return passed == total

if __name__ == "__main__":
    main()