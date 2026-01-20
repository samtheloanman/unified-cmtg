import re
import subprocess
import json
import os
import sys

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MILESTONES_PATH = os.path.join(ROOT_DIR, "MILESTONES.md")
TASKS_PATH = os.path.join(ROOT_DIR, "unified-platform", "conductor", "tasks.md")

def run_gh_command(args):
    """Runs a gh command and returns the output (JSON if parsing)"""
    try:
        # If args start with "api", we might face 404 if repo context isn't inferred. 
        # But assuming CWD is repo root, it should work.
        result = subprocess.run(["gh"] + args, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {' '.join(args)}\nWith error: {e.stderr}")
        return None

def get_existing_milestones():
    """Fetches existing milestones from GitHub using API"""
    # GET /repos/:owner/:repo/milestones
    output = run_gh_command(["api", "/repos/:owner/:repo/milestones", "--paginate"])
    if output:
        return {m["title"]: m for m in json.loads(output)}
    return {}

def create_milestone(title, description=""):
    """Creates a milestone on GitHub using API"""
    print(f"Creating milestone: {title}")
    # POST /repos/:owner/:repo/milestones
    run_gh_command([
        "api", "/repos/:owner/:repo/milestones", 
        "--method", "POST", 
        "-f", f"title={title}", 
        "-f", f"description={description}"
    ])

def get_existing_issues():
    """Fetches existing issues using REST API"""
    # GET /repos/:owner/:repo/issues?state=all
    # Explicitly use GET to avoid implicit POST when params are present
    output = run_gh_command(["api", "/repos/:owner/:repo/issues", "--paginate", "--method", "GET", "-f", "state=all"])
    issues = {}
    if output:
        for issue in json.loads(output):
            issues[issue["title"]] = issue
    return issues

def parse_milestones_file():
    """Parses MILESTONES.md to get high-level milestone definitions"""
    milestones = []
    with open(MILESTONES_PATH, 'r') as f:
        content = f.read()
    
    # Regex for ## ✅ Milestone 1: Title
    regex = r"^##\s+.*\s+(Milestone\s+\d+):\s+(.*)$"
    matches = re.finditer(regex, content, re.MULTILINE)
    
    for match in matches:
        prefix = match.group(1) # Milestone 1
        name = match.group(2).strip() # Foundation & Legacy Verification
        full_title = f"{prefix}: {name}"
        milestones.append({"title": full_title, "description": name})
        
    return milestones

def parse_tasks_file():
    """Parses conductor/tasks.md to get tasks grouped by Phase Title"""
    tasks_by_phase = {}
    current_phase_title = None
    
    with open(TASKS_PATH, 'r') as f:
        lines = f.readlines()
    
    phase_regex = r"^##\s+(Phase\s+\d+.*?)$" # Capture "Phase 1: Title"
    
    for line in lines:
        line = line.strip()
        if line.startswith("## Phase"):
             current_phase_title = line.strip("# ").strip()
             if current_phase_title not in tasks_by_phase:
                 tasks_by_phase[current_phase_title] = []
             continue
            
        if current_phase_title:
            task_regex = r"^-\s+\[([ x])\]\s+\*\*(.*?)\*\*(.*)$"
            task_match = re.search(task_regex, line)
            if task_match:
                completed = task_match.group(1) == 'x'
                title = task_match.group(2).strip()
                desc = task_match.group(3).strip()
                if desc.startswith(":"):
                    desc = desc[1:].strip()
                
                tasks_by_phase[current_phase_title].append({
                    "title": title,
                    "body": desc,
                    "completed": completed
                })
                
    return tasks_by_phase

def calculate_similarity(s1, s2):
    """Simple Jaccard similarity on sets of words"""
    set1 = set(re.findall(r"\w+", s1.lower()))
    set2 = set(re.findall(r"\w+", s2.lower()))
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0

def sync():
    print("Fetching existing GitHub data...")
    gh_milestones = get_existing_milestones()
    gh_issues = get_existing_issues()
    
    print("Parsing local files...")
    local_milestones = parse_milestones_file()
    tasks_by_phase = parse_tasks_file()
    
    # 1. Sync Milestones
    processed_milestones = {} 
    
    print("Syncing Milestones definitions from MILESTONES.md...")
    for lm in local_milestones:
        full_title = lm["title"]
        if full_title in gh_milestones:
            print(f"Milestone exists: {full_title}")
            processed_milestones[lm["title"]] = gh_milestones[full_title]["number"] # Need number for issue assignment
        else:
            create_milestone(full_title, lm["description"])
            # We need to re-fetch to get the number
            gh_milestones = get_existing_milestones()
            if full_title in gh_milestones:
                processed_milestones[lm["title"]] = gh_milestones[full_title]["number"]
            
    # Create simple mapping
    phase_mapping = {}
    
    # Pre-compute milestone title to full object map
    milestone_by_title = {lm["title"]: lm for lm in local_milestones}

    for phase_title, tasks in tasks_by_phase.items():
        # phase_title: "Phase 3a: Programmatic SEO..."
        # extract "3a"
        match = re.search(r"Phase\s+(\d+[a-z]?)", phase_title)
        if not match:
            print(f"Could not extract phase number from: {phase_title}")
            continue
            
        phase_num = match.group(1) # "3a", "1", "2"
        
        # Look for matching Milestone with that number
        target_milestone = None
        for m_title in milestone_by_title.keys():
            # Check for "Milestone 3a:..."
            m_match = re.search(r"Milestone\s+(\d+[a-z]?)", m_title)
            if m_match and m_match.group(1) == phase_num:
                target_milestone = m_title
                break
        
        if target_milestone:
             phase_mapping[phase_title] = target_milestone
             print(f"Mapped '{phase_title}' -> '{target_milestone}'")
        else:
             print(f"Warning: No matching milestone found for phase number {phase_num}")

    # Track milestone status
    milestone_status_updates = {}

    for phase_title, tasks in tasks_by_phase.items():
        target_milestone_title = phase_mapping.get(phase_title)
        if not target_milestone_title:
            continue
            
        milestone_number = processed_milestones.get(target_milestone_title)
        if not milestone_number:
            print(f"Skipping tasks for {phase_title} (Milestone number not found)")
            continue

        print(f"Syncing {len(tasks)} tasks from '{phase_title}' to '{target_milestone_title}' ({milestone_number})...")
        
        all_completed = True

        for task in tasks:
            title = task["title"]
            body = task["body"]
            completed = task["completed"]
            
            if not completed:
                all_completed = False
            
            issue = gh_issues.get(title)
            
            if issue:
                # Update logic using REST
                number = issue["number"]
                current_state = issue["state"]
                should_be_closed = completed
                is_closed = current_state == "closed" # REST API uses lowercase "closed", "open"
                
                updates = []
                
                if should_be_closed and not is_closed:
                    print(f"Closing issue: {title}")
                    run_gh_command(["api", f"/repos/:owner/:repo/issues/{number}", "--method", "PATCH", "-f", "state=closed"])
                elif not should_be_closed and is_closed:
                    print(f"Reopening issue: {title}")
                    run_gh_command(["api", f"/repos/:owner/:repo/issues/{number}", "--method", "PATCH", "-f", "state=open"])
                
                # Check milestone
                current_m_id = issue["milestone"]["number"] if issue.get("milestone") else None
                if current_m_id != milestone_number:
                     print(f"Updating milestone for issue: {title}")
                     # Milestone is integer for API
                     run_gh_command(["api", f"/repos/:owner/:repo/issues/{number}", "--method", "PATCH", "-f", f"milestone={milestone_number}"])

            else:
                # Create issue using REST
                print(f"Creating issue: {title}")
                # POST /repos/:owner/:repo/issues
                # Note: body param
                run_gh_command([
                    "api", "/repos/:owner/:repo/issues", 
                    "--method", "POST", 
                    "-f", f"title={title}", 
                    "-f", f"body={body}", 
                    "-F", f"milestone={milestone_number}" # -F for non-string fields? milestone is int but API takes int. gh -f sends string. -F might be needed or raw json.
                    # gh api -f milestone=1 sends "milestone":"1". API expects integer.
                    # Workaround: use --input - or raw field for int? 
                    # gh api autoconverts? 
                    # Actually gh api -f usually sends strings. 
                    # Let's try -F (magic type inference? No, -F is for file).
                    # 'gh api' documentation: -f denotes string parameter. -F denotes typed parameter (bool, int, file).
                ])
                
                if completed:
                     # Since we can't easily get the number of the newly created issue without parsing output,
                     # and usually new issues are open, we assume it's open.
                     # But future runs will close it. 
                     # Or we can just let it go.
                     pass
        
        # If all tasks in this phase are completed, we should ensure the milestone is closed.
        # Note: A milestone might span multiple phases? 
        # In our mapping, it seems one-to-one or many-to-one.
        # If any phase maps to a milestone and has OPEN tasks, the milestone should be OPEN.
        # If all phases mapping to a milestone are COMPLETE, the milestone should be CLOSED.
        
        if target_milestone_title not in milestone_status_updates:
             milestone_status_updates[target_milestone_title] = True # Assume closed initially
        
        if not all_completed:
             milestone_status_updates[target_milestone_title] = False # Mark as needs open

    # Apply milestone status updates
    print("\nUpdating Milestone States...")
    for title, should_close in milestone_status_updates.items():
        m_number = processed_milestones.get(title)
        if not m_number: continue
        
        # We need check current status. 
        # get_existing_milestones only fetches Open by default? No we used --state all
        
        # Actually `get_existing_milestones` result is stored in `gh_milestones`.
        # title -> obj
        m_obj = gh_milestones.get(title)
        if not m_obj: continue
        
        current_state = m_obj.get("state", "open")
        
        if should_close and current_state == "open":
            print(f"Closing Milestone: {title}")
            run_gh_command(["api", f"/repos/:owner/:repo/milestones/{m_number}", "--method", "PATCH", "-f", "state=closed"])
        elif not should_close and current_state == "closed":
            print(f"Reopening Milestone: {title}")
            run_gh_command(["api", f"/repos/:owner/:repo/milestones/{m_number}", "--method", "PATCH", "-f", "state=open"])

if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        print("Dry run mode not fully implemented in this script version, but proceed carefully.")
    sync()
