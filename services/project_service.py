"""
NexHR - Project Service
Feeds the Dashboard "Project Overview" widget and the standalone Projects tab.
"""
import pandas as pd
from database.connection import session_scope
from database import queries as q


def get_project_status() -> pd.DataFrame:
    with session_scope() as db:
        projects = q.get_all_projects(db)
        rows = []
        for p in projects:
            team = q.get_project_team(db, p.id)
            rows.append({
                "Project": p.name,
                "Manager": p.manager.name if p.manager else "-",
                "Status": p.status.value,
                "Completion %": p.completion_percentage,
                "Team Size": len(team),
                "Start Date": p.start_date,
                "Due Date": p.due_date,
                "_id": p.id,
            })
        return pd.DataFrame(rows)


def get_project_status_counts() -> dict:
    df = get_project_status()
    if df.empty:
        return {}
    return df["Status"].value_counts().to_dict()


def get_project_team_details(project_id: int) -> pd.DataFrame:
    with session_scope() as db:
        team = q.get_project_team(db, project_id)
        rows = [{"Emp ID": e.emp_code, "Name": e.name, "Role": e.role,
                 "Department": e.department.name if e.department else "-"} for e in team]
        return pd.DataFrame(rows)
