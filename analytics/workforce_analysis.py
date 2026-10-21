
import plotly.express as px
import pandas as pd
from database.connection import session_scope
from database import queries as q
from assets.theme import rose_palette, style_fig, PRIMARY_DARK, PRIMARY, SECONDARY, ACCENT

_PROJECT_STATUS_COLOR_MAP = {
    "Completed": "#1E8E5A",
    "Ongoing": PRIMARY,
    "Review": "#B7791F",
    "Not Started": ACCENT,
}


def department_headcount_chart():
    with session_scope() as db:
        employees = q.get_all_employees(db, active_only=True)
        agg = {}
        for e in employees:
            if e.department:
                agg[e.department.name] = agg.get(e.department.name, 0) + 1
        if not agg:
            return None
        df = pd.DataFrame({"Department": list(agg.keys()), "Headcount": list(agg.values())})
        df = df.sort_values("Headcount", ascending=False)
        fig = px.bar(df, x="Department", y="Headcount", color="Department", text_auto=True,
                     title="Department-wise Employee Count",
                     color_discrete_sequence=rose_palette(len(df)))
        fig.update_traces(textfont_color="white", marker_line_width=0, textposition="inside")
        fig.update_layout(showlegend=False, xaxis_title=None)
        return style_fig(fig)


def project_completion_chart():
    from services import project_service
    df = project_service.get_project_status()
    if df.empty:
        return None
    fig = px.bar(df, x="Project", y="Completion %", color="Status", text_auto=True,
                 title="Project Completion Overview", range_y=[0, 100],
                 color_discrete_map=_PROJECT_STATUS_COLOR_MAP)
    fig.update_traces(textfont_color="white", marker_line_width=0)
    fig.update_layout(xaxis_title=None)
    return style_fig(fig, show_legend=True)
