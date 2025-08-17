"""
Script to help set up remote Git repository for Bank Statement Analyzer.
Provides instructions for different Git hosting services.
"""

import subprocess
import sys

def run_git_command(command):
    """Run a git command and return the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_git_status():
    """Check current Git repository status."""
    print("🔍 Checking Git Repository Status")
    print("=" * 40)
    
    # Check if we're in a git repo
    success, stdout, stderr = run_git_command("git status --porcelain")
    if not success:
        print("❌ Not in a Git repository")
        return False
    
    # Check for uncommitted changes
    if stdout.strip():
        print("⚠️  You have uncommitted changes:")
        print(stdout)
        print("Please commit your changes before pushing to remote.")
        return False
    
    # Show current branch and commits
    success, branch, _ = run_git_command("git branch --show-current")
    success2, commits, _ = run_git_command("git log --oneline")
    
    print(f"✅ Current branch: {branch}")
    print(f"✅ Repository is clean (no uncommitted changes)")
    print(f"✅ Commit history:")
    for line in commits.split('\n')[:3]:  # Show last 3 commits
        print(f"   {line}")
    
    return True

def show_github_instructions():
    """Show GitHub setup instructions."""
    print("\n🐙 GitHub Setup Instructions")
    print("=" * 40)
    print("1. Go to https://github.com")
    print("2. Click 'New Repository' (+ icon)")
    print("3. Repository name: 'bank-statement-analyzer'")
    print("4. Description: 'Web-based bank statement analyzer with monthly Excel reports'")
    print("5. Set to Public or Private (your choice)")
    print("6. DON'T initialize with README (we already have one)")
    print("7. Click 'Create Repository'")
    print("\n📋 After creating, GitHub will show you the repository URL like:")
    print("   https://github.com/yourusername/bank-statement-analyzer.git")
    print("\n🚀 Then run these commands:")
    print("   git remote add origin https://github.com/yourusername/bank-statement-analyzer.git")
    print("   git branch -M main")
    print("   git push -u origin main")

def show_gitlab_instructions():
    """Show GitLab setup instructions."""
    print("\n🦊 GitLab Setup Instructions")
    print("=" * 40)
    print("1. Go to https://gitlab.com")
    print("2. Click 'New Project' > 'Create blank project'")
    print("3. Project name: 'bank-statement-analyzer'")
    print("4. Project description: 'Web-based bank statement analyzer'")
    print("5. Set visibility level (Public/Internal/Private)")
    print("6. Uncheck 'Initialize repository with a README'")
    print("7. Click 'Create Project'")
    print("\n🚀 Then run these commands:")
    print("   git remote add origin https://gitlab.com/yourusername/bank-statement-analyzer.git")
    print("   git branch -M main")
    print("   git push -u origin main")

def show_quick_setup():
    """Show quick setup for common scenarios."""
    print("\n⚡ Quick Setup (Choose Your Platform)")
    print("=" * 50)
    print("🐙 GitHub: Most popular, great for open source")
    print("🦊 GitLab: Great CI/CD, unlimited private repos")
    print("🪣 Bitbucket: Good for teams, integrates with Atlassian")
    print("☁️  Azure DevOps: Enterprise-focused, Microsoft ecosystem")
    
    print(f"\n📊 Your Repository Stats:")
    success, file_count, _ = run_git_command("git ls-files | wc -l")
    if success:
        print(f"   📁 Files: {file_count.strip()} tracked files")
    
    success, commit_count, _ = run_git_command("git rev-list --count HEAD")
    if success:
        print(f"   📝 Commits: {commit_count.strip()} commits")
    
    success, size_info, _ = run_git_command("git count-objects -vH")
    if success:
        for line in size_info.split('\n'):
            if 'size-pack' in line:
                print(f"   💾 Size: {line.split(':')[1].strip()}")
                break

def setup_remote_interactive():
    """Interactive remote setup."""
    print("🌐 Remote Repository Setup")
    print("=" * 30)
    
    print("\nWhere would you like to host your repository?")
    print("1. GitHub (github.com)")
    print("2. GitLab (gitlab.com)")  
    print("3. Other (manual setup)")
    print("4. Show me all instructions")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            show_github_instructions()
        elif choice == "2":
            show_gitlab_instructions()
        elif choice == "3":
            print("\n🔧 Manual Setup:")
            print("1. Create a repository on your chosen platform")
            print("2. Copy the repository URL")
            print("3. Run: git remote add origin <repository-url>")
            print("4. Run: git push -u origin master")
        elif choice == "4":
            show_github_instructions()
            show_gitlab_instructions()
        else:
            print("Invalid choice. Please run the script again.")
            
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")

def main():
    """Main function."""
    print("🏦 Bank Statement Analyzer - Remote Repository Setup")
    print("=" * 60)
    
    # Check Git status first
    if not check_git_status():
        return
    
    show_quick_setup()
    
    print(f"\n" + "="*60)
    setup_remote_interactive()
    
    print(f"\n💡 Pro Tips:")
    print("• Use a descriptive repository name like 'bank-statement-analyzer'")
    print("• Add a good description: 'Web-based PDF bank statement analyzer'")
    print("• Consider making it private if it will contain sensitive data")
    print("• The .gitignore already protects your PDFs and credentials")
    
    print(f"\n🎯 After pushing, you'll have:")
    print("• ✅ Cloud backup of your code")
    print("• ✅ Version history preserved")
    print("• ✅ Ability to collaborate with others")
    print("• ✅ Easy deployment from Git repository")

if __name__ == "__main__":
    main()
