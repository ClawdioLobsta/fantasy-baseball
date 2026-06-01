#!/usr/bin/env python3

"""
Fantasy baseball automatic refresh script.
Fetches latest stats and commits changes to repository.
"""

import time
import subprocess
from datetime import datetime
import sys
from pathlib import Path

def run_command(cmd: list[str], cwd: str | Path = None) -> bool:
    """Run command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def refresh_data():
    """Refresh baseball data and commit changes."""
    repo_path = Path(__file__).resolve().parent.parent
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting data refresh...")
    
    # Activate virtual environment and run scripts
    venv_python = repo_path / ".venv" / "bin" / "python"
    if not venv_python.exists():
        print("ERROR: Virtual environment not found!")
        return False
    
    # Fetch new stats
    success, output = run_command([str(venv_python), "src/fetch_stats.py"], repo_path)
    if not success:
        print(f"ERROR fetching stats: {output}")
        return False
    
    # Fetch prospects
    success, output = run_command([str(venv_python), "src/fetch_prospects.py"], repo_path)
    if not success:
        print(f"ERROR fetching prospects: {output}")
        return False
    
    # Calculate projections
    success, output = run_command([str(venv_python), "src/projections.py"], repo_path)
    if not success:
        print(f"ERROR calculating projections: {output}")
        return False
    
    # Git commit
    success, output = run_command(["git", "add", "."], repo_path)
    if not success:
        print(f"ERROR adding files: {output}")
        return False
    
    success, output = run_command([
        "git", "commit", 
        "-m", f"Auto-update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    ], repo_path)
    if "nothing to commit" in output:
        print("No changes to commit")
    elif not success:
        print(f"ERROR committing: {output}")
        return False
    
    # Push to GitHub
    success, output = run_command(["git", "push"], repo_path)
    if not success:
        print(f"ERROR pushing: {output}")
        return False
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Refresh completed successfully!")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode - don't commit
        print("TEST MODE: Running without commits")
    else:
        refresh_data()