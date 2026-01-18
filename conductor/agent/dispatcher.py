"""
Task Dispatcher Module
Dispatches tasks to AI agents (Jules, Claude, Gemini, Antigravity)
"""

import subprocess
import json
import os
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import uuid


class TaskDispatcher:
    """Dispatch tasks to various AI agents and track their status."""
    
    REPO_NAME = "samtheloanman/unified-cmtg"
    
    def __init__(self):
        # State directory for tracking dispatched tasks
        self.state_dir = Path("/home/samalabam/code/unified-cmtg/.conductor-state")
        self.state_dir.mkdir(exist_ok=True)
        
        self.tasks_file = self.state_dir / "dispatched_tasks.json"
        self.heartbeats_file = self.state_dir / "agent_heartbeats.json"
        
        # Initialize files if they don't exist
        if not self.tasks_file.exists():
            self._save_tasks({"tasks": [], "last_updated": None})
        if not self.heartbeats_file.exists():
            self._save_heartbeats({})
    
    def _load_tasks(self) -> Dict:
        """Load dispatched tasks from JSON file."""
        try:
            return json.loads(self.tasks_file.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return {"tasks": [], "last_updated": None}
    
    def _save_tasks(self, data: Dict):
        """Save dispatched tasks to JSON file."""
        data["last_updated"] = datetime.now().isoformat()
        self.tasks_file.write_text(json.dumps(data, indent=2))
    
    def _load_heartbeats(self) -> Dict:
        """Load agent heartbeats."""
        try:
            return json.loads(self.heartbeats_file.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_heartbeats(self, data: Dict):
        """Save agent heartbeats."""
        self.heartbeats_file.write_text(json.dumps(data, indent=2))
    
    def _update_heartbeat(self, agent: str, status: str):
        """Update the heartbeat for an agent."""
        heartbeats = self._load_heartbeats()
        heartbeats[agent] = {
            "status": status,
            "last_seen": datetime.now().isoformat()
        }
        self._save_heartbeats(heartbeats)
    
    def _add_task_record(self, task_id: str, agent: str, task_description: str, 
                         status: str, result: Optional[str] = None):
        """Add a task record to the tracking file."""
        data = self._load_tasks()
        data["tasks"].append({
            "id": task_id,
            "agent": agent,
            "task": task_description,
            "status": status,
            "result": result,
            "dispatched_at": datetime.now().isoformat(),
            "completed_at": None
        })
        self._save_tasks(data)
    
    def dispatch_to_jules(self, task_description: str, branch: str = "main") -> Dict:
        """
        Dispatch a task to Jules via the Jules REST API.
        
        The API creates a new session with the task as a prompt.
        See: https://jules.googleapis.com/v1alpha/sessions
        
        Args:
            task_description: The task to send to Jules
            branch: Git branch to work on (default: main)
            
        Returns:
            Dict with status, task_id, session_id, and any output/error
        """
        task_id = str(uuid.uuid4())[:8]
        
        # Get Jules API key from environment
        jules_api_key = os.environ.get("JULES_API_KEY")
        
        if not jules_api_key:
            # Check if key exists in .env file
            env_file = Path("/home/samalabam/code/unified-cmtg/.env")
            if env_file.exists():
                for line in env_file.read_text().splitlines():
                    if line.startswith("JULES_API_KEY="):
                        jules_api_key = line.split("=", 1)[1].strip().strip("'\"")
                        break
        
        if not jules_api_key:
            # Fall back to queuing for manual execution
            return self._queue_jules_task(task_id, task_description)
        
        try:
            self._update_heartbeat("Jules", "dispatching")
            
            # First, get the source ID for our repository
            sources_response = requests.get(
                "https://jules.googleapis.com/v1alpha/sources",
                headers={
                    "X-Goog-Api-Key": jules_api_key,
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if sources_response.status_code != 200:
                return self._queue_jules_task(task_id, task_description, 
                    f"Failed to list sources: {sources_response.status_code}")
            
            sources = sources_response.json().get("sources", [])
            
            # Find our repository - check 'id', 'name', and repo info
            source_name = None
            for source in sources:
                source_id = source.get("id", "")
                source_nm = source.get("name", "")
                repo_info = source.get("githubRepo", {})
                repo_name = repo_info.get("repo", "")
                
                # Match by id (e.g., "github/samtheloanman/unified-cmtg")
                if self.REPO_NAME.lower() in source_id.lower():
                    source_name = source_nm  # Use the full "name" for API calls
                    break
                # Match by repo name
                if repo_name.lower() == self.REPO_NAME.split("/")[-1].lower():
                    source_name = source_nm
                    break
            
            if not source_name:
                return self._queue_jules_task(task_id, task_description,
                    f"Repository {self.REPO_NAME} not found in Jules sources. Install Jules GitHub app first.")

            
            # Create a new session
            # The API auto-detects the repo from the prompt content
            # Include repo name in prompt for clarity
            full_prompt = f"[Repository: {self.REPO_NAME}]\n\n{task_description}"
            
            session_response = requests.post(
                "https://jules.googleapis.com/v1alpha/sessions",
                headers={
                    "X-Goog-Api-Key": jules_api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": full_prompt
                },
                timeout=60
            )


            
            if session_response.status_code in [200, 201]:
                session_data = session_response.json()
                session_id = session_data.get("name", "").split("/")[-1]
                
                self._add_task_record(task_id, "Jules", task_description, "dispatched", 
                    f"Session: {session_id}")
                self._update_heartbeat("Jules", "active")
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "session_id": session_id,
                    "message": f"✅ Task dispatched to Jules! Session: {session_id}",
                    "session_url": f"https://jules.google.com/session/{session_id}"
                }
            else:
                error_msg = session_response.text[:200]
                return self._queue_jules_task(task_id, task_description, 
                    f"API error {session_response.status_code}: {error_msg}")
                
        except requests.Timeout:
            return self._queue_jules_task(task_id, task_description, "Request timed out")
        except requests.RequestException as e:
            return self._queue_jules_task(task_id, task_description, str(e))
        except Exception as e:
            return {
                "success": False,
                "task_id": task_id,
                "message": f"Error dispatching to Jules: {str(e)}"
            }
    
    def _queue_jules_task(self, task_id: str, task_description: str, reason: str = None) -> Dict:
        """Queue a Jules task for manual execution when API is unavailable."""
        self._add_task_record(task_id, "Jules", task_description, "queued")
        self._update_heartbeat("Jules", "has_pending")
        
        # Write to Jules queue file
        queue_file = self.state_dir / "jules_queue.json"
        try:
            queue = json.loads(queue_file.read_text()) if queue_file.exists() else {"tasks": []}
        except:
            queue = {"tasks": []}
        
        queue["tasks"].append({
            "id": task_id,
            "task": task_description,
            "repo": self.REPO_NAME,
            "status": "pending",
            "reason": reason,
            "created_at": datetime.now().isoformat()
        })
        queue_file.write_text(json.dumps(queue, indent=2))
        
        msg = "Task queued for Jules"
        if reason:
            msg += f" ({reason})"
        msg += ". Set JULES_API_KEY to enable automatic dispatch."
        
        return {
            "success": False,
            "task_id": task_id,
            "message": msg,
            "queued": True
        }
    
    def dispatch_to_claude(self, task_description: str, workspace: str = None) -> Dict:
        """
        Dispatch a task to Claude via the Anthropic Messages API.
        
        Creates a conversation that is logged to a file for monitoring.
        Uses streaming to capture real-time output.
        
        Args:
            task_description: The task to send to Claude
            workspace: Optional workspace path (for context in prompt)
            
        Returns:
            Dict with status, session_id, and output log path
        """
        task_id = str(uuid.uuid4())[:8]
        workspace = workspace or "/home/samalabam/code/unified-cmtg"
        
        # Get Claude API key
        claude_api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if not claude_api_key:
            # Check MCP secrets file
            secrets_file = Path("/home/samalabam/code/custom-cmre-mcp/config/secrets.json")
            if secrets_file.exists():
                try:
                    secrets = json.loads(secrets_file.read_text())
                    claude_api_key = secrets.get("global", {}).get("ANTHROPIC_API_KEY")
                except:
                    pass
        
        if not claude_api_key:
            # Fall back to CLI
            return self._dispatch_claude_cli(task_id, task_description, workspace)
        
        try:
            self._update_heartbeat("Claude", "dispatching")
            
            # Create context-aware system prompt
            system_prompt = f"""You are Claude, an AI assistant helping with coding tasks.
            
Workspace: {workspace}
Repository: {self.REPO_NAME}

You have access to the codebase and should provide actionable coding assistance.
When given a task, analyze it carefully and provide implementation details."""

            # Make API request
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": claude_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 4096,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": task_description}
                    ]
                },
                timeout=180
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", [])
                output_text = ""
                for block in content:
                    if block.get("type") == "text":
                        output_text += block.get("text", "")
                
                # Save conversation to log file
                log_file = self.state_dir / f"claude_session_{task_id}.md"
                log_content = f"""# Claude Session {task_id}
**Created**: {datetime.now().isoformat()}
**Workspace**: {workspace}

## Task
{task_description}

## Response
{output_text}
"""
                log_file.write_text(log_content)
                
                self._add_task_record(task_id, "Claude", task_description, "completed", 
                    f"Session logged to: {log_file}")
                self._update_heartbeat("Claude", "active")
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "message": f"✅ Claude responded! View session: claude_session_{task_id}.md",
                    "output": output_text[:500] + "..." if len(output_text) > 500 else output_text,
                    "log_file": str(log_file),
                    "model": result.get("model"),
                    "usage": result.get("usage")
                }
            else:
                error_msg = response.text[:200]
                self._add_task_record(task_id, "Claude", task_description, "failed", error_msg)
                return {
                    "success": False,
                    "task_id": task_id,
                    "message": f"Claude API error {response.status_code}: {error_msg}"
                }
                
        except requests.Timeout:
            return {
                "success": False,
                "task_id": task_id,
                "message": "Claude API request timed out after 180 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "task_id": task_id,
                "message": f"Error dispatching to Claude: {str(e)}"
            }
    
    def _dispatch_claude_cli(self, task_id: str, task_description: str, workspace: str) -> Dict:
        """Fallback to Claude CLI when API key is not available."""
        try:
            cmd = ["claude", "-p", task_description]
            
            self._update_heartbeat("Claude", "dispatching")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=workspace
            )
            
            if result.returncode == 0:
                self._add_task_record(task_id, "Claude", task_description, "dispatched", result.stdout)
                self._update_heartbeat("Claude", "active")
                return {
                    "success": True,
                    "task_id": task_id,
                    "message": "Task dispatched to Claude Code CLI",
                    "output": result.stdout
                }
            else:
                self._add_task_record(task_id, "Claude", task_description, "failed", result.stderr)
                return {
                    "success": False,
                    "task_id": task_id,
                    "message": "Claude CLI dispatch failed",
                    "error": result.stderr
                }
                
        except FileNotFoundError:
            return {
                "success": False,
                "task_id": task_id,
                "message": "Claude CLI not found and API key not set. Set ANTHROPIC_API_KEY."
            }
        except Exception as e:
            return {
                "success": False,
                "task_id": task_id,
                "message": f"Error dispatching to Claude: {str(e)}"
            }

    
    def dispatch_to_gemini(self, task_description: str, workspace: str = None) -> Dict:
        """
        Dispatch a task to Gemini CLI.
        
        Args:
            task_description: The task to send to Gemini
            workspace: Optional workspace path
            
        Returns:
            Dict with status and any output/error
        """
        task_id = str(uuid.uuid4())[:8]
        workspace = workspace or "/home/samalabam/code/unified-cmtg"
        
        try:
            # Gemini CLI command
            cmd = ["gemini", "-p", task_description]
            
            self._update_heartbeat("Gemini", "dispatching")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=workspace
            )
            
            if result.returncode == 0:
                self._add_task_record(task_id, "Gemini", task_description, "dispatched", result.stdout)
                self._update_heartbeat("Gemini", "active")
                return {
                    "success": True,
                    "task_id": task_id,
                    "message": "Task dispatched to Gemini CLI",
                    "output": result.stdout
                }
            else:
                self._add_task_record(task_id, "Gemini", task_description, "failed", result.stderr)
                return {
                    "success": False,
                    "task_id": task_id,
                    "message": "Gemini dispatch failed",
                    "error": result.stderr
                }
                
        except FileNotFoundError:
            return {
                "success": False,
                "task_id": task_id,
                "message": "Gemini CLI not found. Please install gemini CLI."
            }
        except Exception as e:
            return {
                "success": False,
                "task_id": task_id,
                "message": f"Error dispatching to Gemini: {str(e)}"
            }
    
    def queue_for_antigravity(self, task_description: str) -> Dict:
        """
        Queue a task for Antigravity (adds to companion inbox for approval).
        
        Args:
            task_description: The task to queue
            
        Returns:
            Dict with status
        """
        task_id = str(uuid.uuid4())[:8]
        
        # Write to companion inbox file
        inbox_file = Path("/home/samalabam/code/unified-cmtg/.conductor-state/antigravity_inbox.json")
        
        try:
            inbox = json.loads(inbox_file.read_text()) if inbox_file.exists() else {"items": []}
        except:
            inbox = {"items": []}
        
        inbox["items"].append({
            "id": task_id,
            "task": task_description,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        })
        
        inbox_file.write_text(json.dumps(inbox, indent=2))
        self._add_task_record(task_id, "Antigravity", task_description, "queued")
        self._update_heartbeat("Antigravity", "has_pending")
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "Task queued for Antigravity. Check companion inbox for approval."
        }
    
    def get_dispatched_tasks(self, agent: str = None, limit: int = 10) -> List[Dict]:
        """Get recent dispatched tasks, optionally filtered by agent."""
        data = self._load_tasks()
        tasks = data.get("tasks", [])
        
        if agent:
            tasks = [t for t in tasks if t.get("agent") == agent]
        
        # Return most recent first
        return sorted(tasks, key=lambda x: x.get("dispatched_at", ""), reverse=True)[:limit]
    
    def get_agent_status(self, agent: str) -> Dict:
        """Get the current status of an agent."""
        heartbeats = self._load_heartbeats()
        return heartbeats.get(agent, {"status": "unknown", "last_seen": None})
    
    def get_all_agent_statuses(self) -> Dict:
        """Get status of all agents."""
        return self._load_heartbeats()


# Convenience functions
def dispatch_task(agent: str, task: str, **kwargs) -> Dict:
    """Dispatch a task to the specified agent."""
    dispatcher = TaskDispatcher()
    
    if agent.lower() == "jules":
        return dispatcher.dispatch_to_jules(task)
    elif agent.lower() == "claude":
        return dispatcher.dispatch_to_claude(task, kwargs.get("workspace"))
    elif agent.lower() == "gemini":
        return dispatcher.dispatch_to_gemini(task, kwargs.get("workspace"))
    elif agent.lower() == "antigravity":
        return dispatcher.queue_for_antigravity(task)
    else:
        return {"success": False, "message": f"Unknown agent: {agent}"}


if __name__ == "__main__":
    # Test the dispatcher
    dispatcher = TaskDispatcher()
    print("Agent statuses:", dispatcher.get_all_agent_statuses())
    print("Recent tasks:", dispatcher.get_dispatched_tasks(limit=5))
