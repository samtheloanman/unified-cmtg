import os
import sys
import subprocess
import re
from typing import List, Dict, Optional
from pathlib import Path
from github import Github
from github.GithubException import GithubException

# Constants
REPO_NAME = "samtheloanman/unified-cmtg"
# Try to find the data in the root or in unified-platform
ROOT_CONDUCTOR = Path(__file__).resolve().parent.parent
PLATFORM_CONDUCTOR = ROOT_CONDUCTOR.parent / "unified-platform" / "conductor"

class ConductorAgent:
    def __init__(self):
        self.github_token = self._get_github_token()
        if self.github_token:
            print(f"DEBUG: Token loaded. Length: {len(self.github_token)}")
            print(f"DEBUG: Token start: {self.github_token[:4]}... end: ...{self.github_token[-4:]}")
            try:
                self.g = Github(self.github_token)
                self.repo = self.g.get_repo(REPO_NAME)
            except Exception as e:
                print(f"Warning: Could not connect to GitHub: {e}")
                self.g = None
                self.repo = None
        else:
            self.g = None
            self.repo = None
        
        # Priority to the platform conductor data which is more complete
        if (PLATFORM_CONDUCTOR / "tracks.md").exists():
            self.conductor_dir = PLATFORM_CONDUCTOR
        else:
            self.conductor_dir = ROOT_CONDUCTOR
            
        self.tracks_file = self.conductor_dir / "tracks.md"
        
        # Determine Active Track and Checklist File
        self.active_track_id = self._get_active_track_id()
        if self.active_track_id:
            self.checklist_file = self.conductor_dir / "tracks" / self.active_track_id / "checklist.md"
            # Fallback if specific checklist doesn't exist
            if not self.checklist_file.exists():
                print(f"Warning: Checklist not found at {self.checklist_file}, falling back to tasks.md")
                self.checklist_file = self.conductor_dir / "tasks.md"
        else:
            self.checklist_file = self.conductor_dir / "tasks.md"
            
        self.assignments_file = self.conductor_dir / "agent_assignments.md"
        self.current_file = self.conductor_dir / "current.md"
        
        # Jules Automation logs and reports
        self.repo_root = self.conductor_dir.parent.parent if self.conductor_dir.name == "conductor" else self.conductor_dir.parent
        self.sync_report_file = self.repo_root / "SYNC_REPORTS" / "sync-latest.md"
        self.sync_log_file = self.repo_root / ".ralph-loop-state" / "sync-schedule.log"

    def _get_active_track_id(self) -> Optional[str]:
        """Parse tracks.md to find the active track ID."""
        if not self.tracks_file.exists():
            return None
        
        content = self.tracks_file.read_text()
        match = re.search(r"\*\*Track ID\*\*: `(.*?)`", content)
        if match:
            return match.group(1).strip()
        return None

    def _get_github_token(self) -> Optional[str]:
        """Get GitHub token from env or gh CLI."""
        # 1. Try environment variable
        env_token = os.getenv("GITHUB_TOKEN")
        if env_token:
            return env_token

        # 2. Try gh CLI
        try:
            result = subprocess.run(
                ["gh", "auth", "token"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            print("Warning: Could not get GitHub token via CLI.")
            return None

    def get_active_track(self) -> Dict[str, str]:
        """Parse tracks.md to find the active track."""
        if not self.tracks_file.exists():
            return {"name": "Unknown", "status": "Unknown"}
        
        content = self.tracks_file.read_text()
        match = re.search(r"\*\*Active Track\*\*: (.*)", content)
        track_name = match.group(1).strip() if match else "None"
        
        match_status = re.search(r"\*\*Status\*\*: (.*)", content)
        status = match_status.group(1).strip() if match_status else "Unknown"

        # Check for Next Task (often mentions agent)
        match_next = re.search(r"\*\*Next Task\*\*: (.*)", content)
        next_task = match_next.group(1).strip() if match_next else None

        return {"name": track_name, "status": status, "next_task": next_task}

    def get_tasks(self) -> List[Dict[str, str]]:
        """Parse checklist.md (or tasks.md) for tasks."""
        if not self.checklist_file.exists():
            return []

        tasks = []
        content = self.checklist_file.read_text()
        lines = content.splitlines()
        
        current_phase = "Unknown"
        current_header_agent = None
        
        for line_num, line in enumerate(lines):
            if line.startswith("## Phase"):
                current_phase = line.strip("# ").strip()
                # Check if phase header mentions an agent
                agent_match = re.search(r"\((.*?)\s*-", current_phase)
                current_header_agent = agent_match.group(1) if agent_match else None

            if line.startswith("###"):
                # Subheaders like "### ⏳ F.5A: Core Infrastructure (Jules - Current)"
                agent_match = re.search(r"\((.*?)\s*-", line)
                current_header_agent = agent_match.group(1) if agent_match else current_header_agent
            
            # Match uncompleted tasks: - [ ] or - [/] or - [x] or - [-]
            # Capture the task text
            match = re.search(r"^\s*-\s*\[([ /x-])\]\s*(.*)", line)
            if match:
                state_char = match.group(1)
                text = match.group(2).strip()
                
                if state_char == "x":
                    status = "Done"
                elif state_char == "/":
                    status = "In Progress"
                elif state_char == "-":
                    status = "Paused"
                else:
                    status = "Pending"
                
                # Check for GitHub issue reference
                issue_match = re.search(r"#(\d+)", text)
                issue_num = issue_match.group(1) if issue_match else None
                
                # Determine assignment
                assigned_to = current_header_agent
                inline_agent = re.search(r"\((.*?)\s*-", text)
                if inline_agent:
                    assigned_to = inline_agent.group(1)
                
                tasks.append({
                    "phase": current_phase,
                    "status": status,
                    "task": text,
                    "issue_num": issue_num,
                    "assigned_to": assigned_to,
                    "line_num": line_num  # Track line number for updates
                })
        
        return tasks

    def update_task_status(self, task_text: str, new_status: str) -> bool:
        """Update the status of a specific task in checklist.md."""
        if not self.checklist_file.exists():
            return False
            
        content = self.checklist_file.read_text()
        lines = content.splitlines()
        
        status_char = " "
        if new_status == "In Progress":
            status_char = "/"
        elif new_status == "Done" or new_status == "Complete":
            status_char = "x"
        elif new_status == "Paused":
            status_char = "-"
        
        for i, line in enumerate(lines):
            # Match strict task text to avoid partial matches
            if task_text in line and re.match(r"^\s*-\s*\[[ /x-]\]", line):
                # Replace the status char
                updated_line = re.sub(r"^(\s*-\s*\[)[ /x-](\])", f"\\1{status_char}\\2", line)
                lines[i] = updated_line
                self.checklist_file.write_text("\n".join(lines))
                return True
        return False

    def update_task_assignment(self, task_text: str, new_agent: str) -> bool:
        """Update the assignment for a specific task in checklist.md."""
        if not self.checklist_file.exists():
            return False
        
        content = self.checklist_file.read_text()
        lines = content.splitlines()
        
        # Find the task line and add/update inline assignment
        for i, line in enumerate(lines):
            # Match the task by its text content
            if task_text in line and re.match(r"^\s*-\s*\[[ /x-]\]", line):
                # Remove existing inline assignment if present
                updated_line = re.sub(r"\s*\([^)]*-[^)]*\)\s*$", "", line)
                # Add new assignment
                if new_agent and new_agent.strip():
                    updated_line = f"{updated_line} ({new_agent} - Assigned)"
                lines[i] = updated_line
                
                # Write back
                self.checklist_file.write_text("\n".join(lines))
                return True
        
        return False

    def bulk_update_assignments(self, updates: List[Dict]) -> int:
        """Update multiple task assignments and statuses at once.
        
        Args:
            updates: List of dicts with 'task', 'assigned_to', and optionally 'status'
        
        Returns:
            Number of successfully updated tasks
        """
        count = 0
        for update in updates:
            success = False
            task = update.get('task', '')
            
            # Update assignment if provided
            if 'assigned_to' in update:
                if self.update_task_assignment(task, update.get('assigned_to', '')):
                    success = True
            
            # Update status if provided
            if 'status' in update:
                if self.update_task_status(task, update.get('status')):
                    success = True
            
            if success:
                count += 1
        return count

    def get_agent_assignments(self, agent_name: str) -> List[Dict[str, str]]:
        """Extract tasks from agent_assignments.md for a specific agent."""
        if not self.assignments_file.exists():
            return []
            
        content = self.assignments_file.read_text()
        
        # Look for the agent's section specifically
        # Case insensitive search for the agent name in a header
        agent_marker = f"## .*?{agent_name}"
        match = re.search(rf"{agent_marker}.*?\n(.*?)(?=\n##|$)", content, re.DOTALL | re.IGNORECASE)
        
        if not match:
            return []
            
        section_content = match.group(1)
        tasks = []
        
        # Find "### Task X: Name" patterns
        task_matches = re.finditer(r"### Task \d+: (.*?)\n(.*?)(?=\n###|$)", section_content, re.DOTALL)
        for tm in task_matches:
            title = tm.group(1).strip()
            details = tm.group(2).strip()
            
            # Try to find file path if available
            file_match = re.search(r"\*\*File\*\*: `(.*?)`", details)
            file_path = file_match.group(1) if file_match else ""
            
            tasks.append({
                "title": title,
                "file": file_path,
                "details": details
            })
            
        return tasks

    def get_jules_activity(self, limit: int = 10) -> List[str]:
        """Read the latest activity from Jules' sync log."""
        if not self.sync_log_file.exists():
            return ["No activity log found."]
        
        try:
            lines = self.sync_log_file.read_text().splitlines()
            return lines[-limit:]
        except Exception as e:
            return [f"Error reading activity log: {e}"]

    def get_latest_sync_report(self) -> Dict[str, str]:
        """Read the latest sync report summary."""
        if not self.sync_report_file.exists():
            return {"status": "No report found", "date": "N/A", "summary": ""}
        
        try:
            content = self.sync_report_file.read_text()
            # Extract basic info
            match_date = re.search(r"# Sync Report - (.*)", content)
            date = match_date.group(1).strip() if match_date else "Unknown"
            
            # Extract summary section
            match_summary = re.search(r"## Summary\n\n(.*?)\n\n", content, re.DOTALL)
            summary = match_summary.group(1).strip() if match_summary else ""

            # Check for overall status
            status = "✅ Success" if "completed successfully" in content.lower() else "⚠️ Warning/Error"

            return {
                "status": status,
                "date": date,
                "summary": summary,
                "full_report": content
            }
        except Exception as e:
            return {"status": "Error", "date": "N/A", "summary": str(e)}

    def get_github_items(self) -> Dict[str, List]:
        """Fetch open issues and PRs."""
        issues = []
        prs = []
        
        try:
            if not self.repo:
                return {"issues": [], "prs": []}
                
            print(f"Fetching GitHub items for {self.repo.full_name}...")
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

    def execute_command(self, command: str) -> str:
        """Execute a command and return the result."""
        command_lower = command.lower().strip()
        
        if "sync" in command_lower and "github" in command_lower:
            gh_items = self.get_github_items()
            return f"✅ Synced with GitHub:\n- {len(gh_items['issues'])} open issues\n- {len(gh_items['prs'])} open PRs"
        
        # Jules Activity
        elif "jules" in command_lower or "activity" in command_lower:
            report = self.get_latest_sync_report()
            logs = self.get_jules_activity(5)
            log_text = "\n".join([f"• {l}" for l in logs])
            return f"""🤖 **Jules Activity Status**
**Latest Sync:** {report['date']}
**Status:** {report['status']}
**Summary:** {report['summary']}

**Recent Logs:**
{log_text}"""
        
        elif "list" in command_lower and "task" in command_lower:
            tasks = self.get_tasks()
            in_progress = [t for t in tasks if t['status'] == 'In Progress']
            pending = [t for t in tasks if t['status'] == 'Pending']
            return f"📋 Task Summary:\n- {len(in_progress)} in progress\n- {len(pending)} pending\n- {len(tasks)} total"
        
        elif "track" in command_lower or "status" in command_lower:
            track = self.get_active_track()
            return f"🎯 Active Track: {track['name']}\nStatus: {track['status']}"
        
        elif "help" in command_lower:
            return """Available Commands:
• **sync github** - Refresh GitHub issues and PRs
• **list tasks** - Show task summary
• **jules activity** - Show latest Jules automation status
• **track status** - Show active track
• **help** - Show this help message"""
        
        else:
            return f"⚠️ Command not recognized: '{command}'\nType 'help' for available commands."

if __name__ == "__main__":
    agent = ConductorAgent()
    print(f"Using data from: {agent.conductor_dir}")
    print("Active Track:", agent.get_active_track())
    print(f"Found {len(agent.get_tasks())} tasks.")
    print("Jules Tasks:", [t['task'] for t in agent.get_tasks() if t.get('assigned_to') == 'Jules'])
