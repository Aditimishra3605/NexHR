"""
NexHR - Projects Tab
Standalone project status board (completed / ongoing / review / not
started) with a drill-down into each project's team. Complements the
compact Project Overview widget shown on the Dashboard.
"""
import streamlit as st

from services import project_service
from analytics import workforce_analysis
from assets.theme import page_header, section_title


def render():
    page_header("Projects", "Project status, completion tracking and team allocation")

    counts = project_service.get_project_status_counts()
    if counts:
        cols = st.columns(len(counts))
        for col, (status, count) in zip(cols, counts.items()):
            col.metric(status, count)

    st.markdown("---")

    fig = workforce_analysis.project_completion_chart()
    if fig:
        st.plotly_chart(fig, width='stretch')

    df = project_service.get_project_status()
    if df.empty:
        st.info("No projects found.")
        return

    section_title("Project Status Board", "folder")
    status_filter = st.selectbox("Filter by status", ["All"] + sorted(df["Status"].unique().tolist()))
    view_df = df if status_filter == "All" else df[df["Status"] == status_filter]
    st.dataframe(view_df.drop(columns=["_id"]), width='stretch', hide_index=True)

    section_title("View Project Team", "users")
    options = ["Select a project..."] + view_df["Project"].tolist()
    choice = st.selectbox("Project", options, label_visibility="collapsed")
    if choice != "Select a project...":
        project_id = int(view_df[view_df["Project"] == choice]["_id"].iloc[0])
        team_df = project_service.get_project_team_details(project_id)
        if team_df.empty:
            st.info("No team members currently assigned to this project.")
        else:
            st.dataframe(team_df, width='stretch', hide_index=True)
