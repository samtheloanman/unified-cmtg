import streamlit as st
import sys
import pandas as pd
from pathlib import Path

# Add parent directory to path to import agent
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from agent.sync import ConductorAgent
from agent.dispatcher import TaskDispatcher

st.set_page_config(
    page_title="Conductor Dashboard",
    page_icon="🚄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Agent and Dispatcher
@st.cache_resource
def get_agent():
    return ConductorAgent()

@st.cache_resource
def get_dispatcher():
    return TaskDispatcher()

agent = get_agent()
dispatcher = get_dispatcher()

# Sidebar
with st.sidebar:
    st.title("🚄 Conductor")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("**🤖 Agent Status**")
    
    # Get agent statuses
    statuses = dispatcher.get_all_agent_statuses()
    
    for agent_name in ["Jules", "Claude", "Gemini", "Antigravity"]:
        status_info = statuses.get(agent_name, {})
        status = status_info.get("status", "idle")
        
        if status == "active":
            st.success(f"🟢 {agent_name}: Active")
        elif status == "dispatching":
            st.warning(f"🟡 {agent_name}: Working...")
        elif status == "has_pending":
            st.info(f"📥 {agent_name}: Has pending tasks")
        elif status == "error":
            st.error(f"🔴 {agent_name}: Error")
        else:
            st.caption(f"⚪ {agent_name}: Idle")
    
    st.markdown("---")
    st.markdown("**Quick Actions**")
    st.button("🚀 Start Track (Coming Soon)", disabled=True)
    
    st.markdown("---")
    st.markdown("---")
    st.caption(f"Data source: `{agent.checklist_file}`")

# Main Content
st.title("Mission Control Center")

# 1. Active Track Section
track_info = agent.get_active_track()
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🎯 Active Focus")
    st.info(f"**Track:** {track_info['name']}")
    st.caption(f"Status: {track_info['status']}")

with col2:
    st.header("GitHub Status")
    if 'gh_data' not in st.session_state:
        with st.spinner("Fetching GitHub data..."):
            st.session_state.gh_data = agent.get_github_items()
    
    gh_data = st.session_state.gh_data
    
    m1, m2 = st.columns(2)
    m1.metric("Open Issues", len(gh_data['issues']))
    m2.metric("Open PRs", len(gh_data['prs']))

# 2. Upcoming Tasks
st.markdown("---")
st.header("📋 Upcoming Tasks")

tasks = agent.get_tasks()
if tasks:
    df = pd.DataFrame(tasks)
    
    # Ensure assigned_to column exists
    if 'assigned_to' not in df.columns:
        df['assigned_to'] = None
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        phases = ["All"] + sorted(list(df['phase'].unique()))
        selected_phase = st.selectbox("Filter by Phase", phases)
    
    with col_f2:
        agent_options = ["All Agents"] + sorted([str(a) for a in df['assigned_to'].unique() if a])
        selected_agent = st.selectbox("Filter by Agent", agent_options)
    
    filtered_df = df.copy()
    if selected_phase != "All":
        filtered_df = filtered_df[filtered_df['phase'] == selected_phase]
    
    if selected_agent != "All Agents":
        filtered_df = filtered_df[filtered_df['assigned_to'] == selected_agent]
    
    # Map Status to Action for UI
    def map_status_to_action(status):
        if status == "In Progress": return "Start"
        if status == "Pending": return "Stop"
        if status == "Paused": return "Pause"
        if status == "Done": return "Finish"
        return "Stop" # Default

    filtered_df['action'] = filtered_df['status'].apply(map_status_to_action)
    
    # Editable table
    st.caption("💡 **Tip**: To assign tasks to an agent, edit the phase header in `tasks.md` with `(AgentName - Status)`")
    
    edited_df = st.data_editor(
        filtered_df[['phase', 'assigned_to', 'action', 'task']],
        column_config={
            "phase": st.column_config.TextColumn("Phase", disabled=True),
            "assigned_to": st.column_config.SelectboxColumn(
                "Assigned To",
                options=["Jules", "Antigravity", "Claude", "Gemini", None],
                help="Select agent to assign this task"
            ),
            "action": st.column_config.SelectboxColumn(
                "Action",
                options=["Start", "Stop", "Pause", "Finish"],
                required=True,
                help="Start, Stop, Pause (Rate Limit), or Finish task"
            ),
            "task": st.column_config.TextColumn("Task Description", disabled=True),
        },
        hide_index=True,
        key="task_editor"
    )
    
    # Save button
    col_save, col_info = st.columns([1, 3])
    with col_save:
        if st.button("💾 Save Assignments", type="primary"):
            # Find changes by comparing edited_df with filtered_df
            updates = []
            for idx, row in edited_df.iterrows():
                orig_assignment = filtered_df.loc[idx, 'assigned_to'] if idx in filtered_df.index else None
                new_assignment = row['assigned_to']
                
                orig_action = filtered_df.loc[idx, 'action'] if idx in filtered_df.index else None
                new_action = row['action']
                
                update = {'task': row['task']}
                has_change = False
                
                if orig_assignment != new_assignment:
                    update['assigned_to'] = new_assignment
                    has_change = True
                    
                if orig_action != new_action:
                    # Map Action back to Status
                    new_status = "Pending"
                    if new_action == "Start": new_status = "In Progress"
                    elif new_action == "Pause": new_status = "Paused"
                    elif new_action == "Finish": new_status = "Done"
                    
                    update['status'] = new_status
                    has_change = True
                
                if has_change:
                    updates.append(update)
            
            if updates:
                count = agent.bulk_update_assignments(updates)
                st.success(f"✅ Updated {count} task(s)! Click Refresh Data to see changes.")
                st.cache_data.clear()
            else:
                st.info("No changes to save.")
    
    with col_info:
        st.caption("Changes are saved directly to `checklist.md`")
else:
    st.success("No pending tasks found! All caught up.")

# 3. Jules Robot Room
st.markdown("---")
st.header("🤖 Robot Room (Jules)")

report = agent.get_latest_sync_report()
logs = agent.get_jules_activity(10)

c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("Automation Status")
    st.info(f"**Last Sync:** {report['date']}")
    if "Success" in report['status']:
        st.success(report['status'])
    else:
        st.warning(report['status'])
    st.write(report['summary'])

with c2:
    st.subheader("Recent Activity Logs")
    log_content = "\n".join(logs)
    st.code(log_content, language="text")

# 4. GitHub Detailed View
st.markdown("---")
st.header("Octocat's Corner 🐙")

tab1, tab2 = st.tabs(["Issues", "Pull Requests"])

with tab1:
    for issue in gh_data['issues']:
        with st.expander(f"#{issue['number']} {issue['title']}"):
            st.markdown(f"**Created:** {issue['created_at']}")
            st.markdown(f"**Labels:** {', '.join(issue['labels'])}")
            st.markdown(f"[View on GitHub]({issue['url']})")

with tab2:
    for pr in gh_data['prs']:
        st.markdown(f"- [#{pr['number']}]({pr['url']}) {pr['title']}")

# 5. Agent Dispatch Center
st.markdown("---")
st.header("🚀 Agent Dispatch Center")

dispatch_col1, dispatch_col2 = st.columns([2, 1])

with dispatch_col1:
    st.subheader("Dispatch New Task")
    
    selected_dispatch_agent = st.selectbox(
        "Select Agent",
        ["Jules", "Claude", "Gemini", "Antigravity"],
        key="dispatch_agent"
    )
    
    task_input = st.text_area(
        "Task Description",
        placeholder="Describe the task to dispatch to the agent...",
        key="dispatch_task"
    )
    
    if st.button("🚀 Dispatch Task", type="primary"):
        if task_input.strip():
            if selected_dispatch_agent == "Jules":
                result = dispatcher.dispatch_to_jules(task_input)
            elif selected_dispatch_agent == "Claude":
                result = dispatcher.dispatch_to_claude(task_input)
            elif selected_dispatch_agent == "Gemini":
                result = dispatcher.dispatch_to_gemini(task_input)
            else:
                result = dispatcher.queue_for_antigravity(task_input)
            
            if result.get("success"):
                st.success(f"✅ {result.get('message')} (ID: {result.get('task_id')})")
            else:
                st.error(f"❌ {result.get('message')}")
                if result.get("error"):
                    st.code(result.get("error"))
        else:
            st.warning("Please enter a task description.")

with dispatch_col2:
    st.subheader("Recent Dispatches")
    
    recent_tasks = dispatcher.get_dispatched_tasks(limit=5)
    
    if recent_tasks:
        for task in recent_tasks:
            status_icon = "✅" if task.get("status") == "dispatched" else "⏳" if task.get("status") == "queued" else "❌"
            st.markdown(f"**{status_icon} {task.get('agent')}** - {task.get('task')[:40]}...")
            st.caption(f"ID: {task.get('id')} | {task.get('dispatched_at', '')[:16]}")
    else:
        st.caption("No tasks dispatched yet.")

# 6. Chat Interface
st.markdown("---")
st.header("💬 Command Agent")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Send a command to the Conductor Agent..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # Check for dispatch commands
    if prompt.lower().startswith("@"):
        parts = prompt.split(" ", 1)
        agent_tag = parts[0][1:].lower()  # Remove @ and lowercase
        task_text = parts[1] if len(parts) > 1 else ""
        
        if agent_tag in ["jules", "claude", "gemini", "antigravity"] and task_text:
            from agent.dispatcher import dispatch_task
            result = dispatch_task(agent_tag, task_text)
            response = f"🚀 **Dispatched to {agent_tag.title()}**\n\n{result.get('message')}"
        else:
            response = "Usage: `@jules <task>`, `@claude <task>`, `@gemini <task>`, or `@antigravity <task>`"
    else:
        response = agent.execute_command(prompt)
    
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()
