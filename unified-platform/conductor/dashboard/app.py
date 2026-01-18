import streamlit as st
import sys
import os
import pandas as pd
from pathlib import Path

# Add parent directory to path to import agent
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from agent.sync import ConductorAgent

st.set_page_config(
    page_title="Conductor Dashboard",
    page_icon="🚄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Agent
@st.cache_resource
def get_agent():
    return ConductorAgent()

agent = get_agent()

# Sidebar
with st.sidebar:
    st.title("🚄 Conductor")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Quick Actions**")
    # Placeholder for future command runners
    st.button("🚀 Start Track (Coming Soon)", disabled=True)

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
    # Fetch GitHub items (cached manually via button for now to avoid API rate limits on every rerun)
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
    
    # Filter options
    phases = ["All"] + list(df['phase'].unique())
    selected_phase = st.selectbox("Filter by Phase", phases)
    
    if selected_phase != "All":
        df = df[df['phase'] == selected_phase]
    
    # Display as a clean table
    st.dataframe(
        df[['phase', 'status', 'task', 'issue_num']],
        column_config={
            "phase": "Phase",
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["Pending", "In Progress"],
                required=True,
            ),
            "task": "Task Description",
            "issue_num": st.column_config.LinkColumn(
                "GitHub Issue",
                display_text="Open Issue",
                help="Click to view on GitHub"
            )
        },
        use_container_width=True,
        hide_index=True,
    )
else:
    st.success("No pending tasks found! All caught up.")

# 3. GitHub Detailed View
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
