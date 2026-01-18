import os
import sys
import subprocess
import re
from typing import List, Dict, Optional
from pathlib import Path
from github import Github, Auth
from github.GithubException import GithubException

# Constants
REPO_NAME = "samtheloanman/unified-cmtg"
CONDUCTOR_DIR = Path(__file__).resolve().parent.parent

class ConductorAgent:
    def __init__(self):
        self.github_token = self._get_github_token()
        self.g = Github(auth=Auth.Token(self.github_token))
        self.repo = self.g.get_repo(REPO_NAME)
        self.tracks_file = CONDUCTOR_DIR / "tracks.md"
        self.tasks_file = CONDUCTOR_DIR / "tasks.md"

    def _get_github_token(self) -> str:
        """Get GitHub token from gh CLI."""
        try:
            result = subprocess.run(
                ["gh", "auth", "token"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            print("Error: Could not get GitHub token. Please run 'gh auth login'.")
            sys.exit(1)

    def get_active_track(self) -> Dict[str, str]:
        """Parse tracks.md to find the active track."""
        if not self.tracks_file.exists():
            return {"name": "Unknown", "status": "Unknown"}
        
        content = self.tracks_file.read_text()
        match = re.search(r"\*\*Active Track\*\*: (.*)", content)
        track_name = match.group(1).strip() if match else "None"
        
        match_status = re.search(r"\*\*Status\*\*: (.*)", content)
        status = match_status.group(1).strip() if match_status else "Unknown"

        return {"name": track_name, "status": status}

    def get_tasks(self) -> List[Dict[str, str]]:
        """Parse tasks.md for uncompleted tasks."""
        if not self.tasks_file.exists():
            return []

        tasks = []
        content = self.tasks_file.read_text()
        lines = content.splitlines()
        
        current_phase = "Unknown"
        
        for line in lines:
            if line.startswith("## Phase"):
                current_phase = line.strip("# ").strip()
            
            match = re.search(r"^\s*-\s*\[([ /])\]\s*(.*)", line)
            if match:
                state_char = match.group(1)
                text = match.group(2).strip()
                
                status = "In Progress" if state_char == "/" else "Pending"
                
                issue_match = re.search(r"#(\d+)", text)
                issue_num = issue_match.group(1) if issue_match else None
                
                tasks.append({
                    "phase": current_phase,
                    "status": status,
                    "task": text,
                    "issue_num": issue_num
                })
        
        return tasks

    def get_github_items(self) -> Dict[str, List]:
        """Fetch open issues and PRs."""
        issues = []
        prs = []
        
        try:
            for issue in self.repo.get_issues(state='open'):
                item = {
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.html_url,
                    "created_at": issue.created_at,
                    "labels": [l.name for l in issue.labels]
                }
                
                if issue.pull_request:
                    prs.append(item)
                else:
                    issues.append(item)
                    
        except GithubException as e:
            print(f"GitHub API Error: {e}")
            
        return {"issues": issues, "prs": prs}

if __name__ == "__main__":
    agent = ConductorAgent()
    print("Active Track:", agent.get_active_track())
    print(f"Found {len(agent.get_tasks())} tasks.")
    gh_items = agent.get_github_items()
    print(f"Found {len(gh_items['issues'])} issues and {len(gh_items['prs'])} PRs.")
