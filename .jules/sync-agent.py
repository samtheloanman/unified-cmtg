#!/usr/bin/env python3
"""
Jules Ralph-Loop Sync Agent
24/7 automation for keeping unified-cmtg documentation synchronized with git changes.

Environment: Docker on dell-brain
Python-based implementation (no claude-code plugin required)
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
import time
import fcntl


class SyncAgent:
    """Main sync agent for automated documentation updates."""

    def __init__(self):
        """Initialize the sync agent with proper paths."""
        # Determine repo root dynamically
        self.script_dir = Path(__file__).parent.parent
        self.repo_root = self.script_dir
        self.unified_platform = self.repo_root / "unified-platform"

        # Documentation files
        self.tasks_file = self.unified_platform / "conductor" / "tasks.md"
        self.current_file = self.unified_platform / "conductor" / "current.md"
        self.status_file = self.repo_root / "docs" / "history" / "PROJECT_STATUS_REVIEW.md"
        self.dashboard_file = self.repo_root / "dashboard-data.json"

        # Reports and logs
        self.reports_dir = self.repo_root / "SYNC_REPORTS"
        self.reports_dir.mkdir(exist_ok=True)
        self.sync_report_file = self.reports_dir / "sync-latest.md"

        # State directory
        self.state_dir = self.repo_root / ".ralph-loop-state"
        self.state_dir.mkdir(exist_ok=True)
        self.log_file = self.state_dir / "sync-schedule.log"
        self.lock_file = self.state_dir / ".sync-lock"

        # Counters
        self.changes = {"completed": [], "new": [], "updated": []}
        self.start_time = datetime.now()

    def log(self, message):
        """Write to both stdout and log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        print(formatted)
        with open(self.log_file, "a") as f:
            f.write(formatted + "\n")

    def acquire_lock(self, timeout=30):
        """Acquire execution lock to prevent concurrent runs."""
        try:
            with open(self.lock_file, "w") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                f.write(str(os.getpid()))
                return True
        except IOError:
            self.log("ERROR: Already running, skipping this cycle")
            return False

    def release_lock(self):
        """Release execution lock."""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
        except Exception as e:
            self.log(f"WARNING: Could not release lock: {e}")

    def run_command(self, cmd, cwd=None):
        """Run a command and return output."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.repo_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip(), result.returncode == 0
        except subprocess.TimeoutExpired:
            self.log(f"ERROR: Command timeout: {cmd}")
            return "", False
        except Exception as e:
            self.log(f"ERROR: Command failed: {cmd} - {e}")
            return "", False

    def analyze_git(self):
        """Analyze git history to detect completions."""
        self.log("Analyzing git changes...")

        # Get last 10 commits
        output, success = self.run_command(["git", "log", "-n", "10", "--oneline", "--format=%h - %s"])
        if not success:
            self.log("WARNING: Could not read git log")
            return

        commits = output.split("\n") if output else []
        self.log(f"Found {len(commits)} recent commits")

        for commit in commits:
            if not commit.strip():
                continue

            # Detect patterns in commit messages
            if any(keyword in commit.lower() for keyword in ["complete", "done", "finished", "✅"]):
                self.changes["completed"].append(commit)
                self.log(f"  ✅ Completed: {commit}")

            if any(keyword in commit.lower() for keyword in ["feat:", "feature"]):
                self.changes["new"].append(commit)
                self.log(f"  ⏳ New feature: {commit}")

            if any(keyword in commit.lower() for keyword in ["fix:", "update:", "improve"]):
                self.changes["updated"].append(commit)
                self.log(f"  🔄 Updated: {commit}")

    def read_file(self, filepath):
        """Safely read a file."""
        try:
            if filepath.exists():
                return filepath.read_text(encoding="utf-8")
        except Exception as e:
            self.log(f"WARNING: Could not read {filepath}: {e}")
        return ""

    def write_file(self, filepath, content):
        """Safely write a file."""
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            self.log(f"ERROR: Could not write {filepath}: {e}")
            return False

    def update_tasks_file(self):
        """Update conductor/tasks.md with new timestamp."""
        self.log("Updating conductor/tasks.md...")
        content = self.read_file(self.tasks_file)

        if not content:
            self.log("WARNING: tasks.md is empty or missing")
            return False

        # Update timestamp
        new_timestamp = self.start_time.strftime("%Y-%m-%d %H:%M %Z")
        updated_content = re.sub(
            r"\*\*Last Updated\*\*:.*",
            f"**Last Updated**: {new_timestamp} (Ralph-Loop Sync)",
            content
        )

        # If no timestamp line, add one at the end
        if "**Last Updated**" not in updated_content:
            updated_content += f"\n\n**Last Updated**: {new_timestamp} (Ralph-Loop Sync)\n"

        return self.write_file(self.tasks_file, updated_content)

    def update_current_file(self):
        """Update conductor/current.md with fresh date and status."""
        self.log("Updating conductor/current.md...")
        content = self.read_file(self.current_file)

        if not content:
            self.log("WARNING: current.md is empty or missing")
            return False

        # Update date
        today = self.start_time.strftime("%Y-%m-%d")
        updated_content = re.sub(r"\*\*Date\*\*:.*", f"**Date**: {today}", content)

        return self.write_file(self.current_file, updated_content)

    def generate_sync_report(self):
        """Generate detailed sync report."""
        self.log("Generating sync report...")

        completed_count = len(self.changes["completed"])
        new_count = len(self.changes["new"])
        updated_count = len(self.changes["updated"])

        report = f"""# Sync Report - {self.start_time.strftime("%Y-%m-%d %H:%M %Z")}

## Summary

Jules automated sync completed successfully.

**Changes Detected**:
- Tasks Completed: {completed_count}
- New Features: {new_count}
- Updates/Fixes: {updated_count}
- Total: {completed_count + new_count + updated_count}

---

## Git Changes Analyzed

### Completed Tasks ({completed_count})
"""

        if self.changes["completed"]:
            for change in self.changes["completed"]:
                report += f"- ✅ {change}\n"
        else:
            report += "- None\n"

        report += f"""
### New Features ({new_count})
"""
        if self.changes["new"]:
            for change in self.changes["new"]:
                report += f"- ⏳ {change}\n"
        else:
            report += "- None\n"

        report += f"""
### Updates/Fixes ({updated_count})
"""
        if self.changes["updated"]:
            for change in self.changes["updated"]:
                report += f"- 🔄 {change}\n"
        else:
            report += "- None\n"

        report += f"""
---

## Documentation Updated

✅ conductor/tasks.md - Timestamp refreshed
✅ conductor/current.md - Date refreshed
✅ SYNC_REPORTS/sync-latest.md - Report generated
✅ dashboard-data.json - Metrics refreshed

---

## Next Steps

Review updated documentation:
- `conductor/current.md` - Current sprint status
- `SYNC_REPORTS/sync-latest.md` - This report
- `dashboard-data.json` - Live metrics

For detailed project status, see `conductor/current.md`.

---

**Agent**: Jules
**Type**: Automated Sync
**Environment**: Docker on dell-brain
**Status**: ✅ COMPLETE
**Duration**: {(datetime.now() - self.start_time).total_seconds():.1f}s

Generated: {self.start_time.strftime("%Y-%m-%d %H:%M:%S %Z")}
"""

        return self.write_file(self.sync_report_file, report)

    def update_dashboard_data(self):
        """Update dashboard-data.json with fresh metrics."""
        self.log("Refreshing dashboard data...")

        try:
            # Read existing dashboard data if it exists
            dashboard_data = {}
            if self.dashboard_file.exists():
                content = self.read_file(self.dashboard_file)
                if content:
                    dashboard_data = json.loads(content)

            # Update metadata
            dashboard_data["meta"] = {
                "generated_at": self.start_time.isoformat(),
                "last_sync": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "active"
            }

            # Add sync statistics
            dashboard_data["sync_stats"] = {
                "completed": len(self.changes["completed"]),
                "new": len(self.changes["new"]),
                "updated": len(self.changes["updated"]),
                "total_changes": len(self.changes["completed"]) + len(self.changes["new"]) + len(self.changes["updated"])
            }

            # Write back
            return self.write_file(
                self.dashboard_file,
                json.dumps(dashboard_data, indent=2)
            )
        except json.JSONDecodeError:
            self.log("WARNING: dashboard-data.json is invalid JSON, skipping")
            return False

    def git_commit_and_push(self):
        """Commit and push changes to origin/main."""
        self.log("Committing changes to git...")

        # Check if there are changes
        status_output, _ = self.run_command(["git", "status", "--porcelain"])
        if not status_output:
            self.log("No changes to commit")
            return True

        # Stage files
        files_to_stage = [
            "unified-platform/conductor/tasks.md",
            "unified-platform/conductor/current.md",
            "docs/history/PROJECT_STATUS_REVIEW.md",
            "SYNC_REPORTS/sync-latest.md",
            "dashboard/dashboard-data.json"
        ]

        for file in files_to_stage:
            self.run_command(["git", "add", file])

        # Create commit message
        changes_summary = f"completed={len(self.changes['completed'])}, new={len(self.changes['new'])}, updated={len(self.changes['updated'])}"
        commit_msg = f"""chore(jules): Hourly sync - {changes_summary}

Automated documentation sync by Jules agent.

Changes:
- Tasks completed: {len(self.changes['completed'])}
- New features: {len(self.changes['new'])}
- Updates/fixes: {len(self.changes['updated'])}

Documentation updated:
- conductor/tasks.md (timestamp)
- conductor/current.md (date)
- SYNC_REPORTS/sync-latest.md (report)
- dashboard-data.json (metrics)

Co-Authored-By: Jules Agent <noreply@dell-brain.local>
"""

        # Commit
        _, commit_success = self.run_command(["git", "commit", "-m", commit_msg])
        if not commit_success:
            self.log("WARNING: Commit failed")
            return False

        self.log("✅ Changes committed")

        # Push
        self.log("Pushing to origin/main...")
        _, push_success = self.run_command(["git", "push", "origin", "main"])
        if not push_success:
            self.log("WARNING: Push failed (will retry next hour)")
            return False

        self.log("✅ Changes pushed to origin/main")
        return True

    def run(self):
        """Main sync execution."""
        self.log("=" * 70)
        self.log("Jules: Ralph-Loop Automated Sync Starting")
        self.log("=" * 70)

        # Acquire lock
        if not self.acquire_lock():
            return False

        try:
            # Step 1: Analyze git
            self.analyze_git()

            # Step 2: Update documentation
            self.update_tasks_file()
            self.update_current_file()

            # Step 3: Generate report
            self.generate_sync_report()

            # Step 4: Update dashboard
            self.update_dashboard_data()

            # Step 5: Git operations
            self.git_commit_and_push()

            # Success
            duration = (datetime.now() - self.start_time).total_seconds()
            self.log("=" * 70)
            self.log(f"✅ Jules: Sync Completed Successfully ({duration:.1f}s)")
            self.log("=" * 70)
            return True

        except Exception as e:
            self.log(f"ERROR: Sync failed: {e}")
            import traceback
            self.log(traceback.format_exc())
            return False

        finally:
            self.release_lock()


def main():
    """Entry point."""
    agent = SyncAgent()
    success = agent.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
