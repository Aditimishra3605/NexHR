
import plotly.express as px
import pandas as pd

from services import salary_service
from assets.theme import rose_palette, style_fig, MAIN_TEXT


def department_cost_bar_chart():
    df = salary_service.get_department_cost_summary()
    if df.empty:
        return None
    df = df.sort_values("Total Cost", ascending=False)
    fig = px.bar(df, x="Department", y="Total Cost", color="Department",
                 title="Total Salary Cost by Department", text_auto=".2s",
                 color_discrete_sequence=rose_palette(len(df)))
    fig.update_traces(textfont_color=MAIN_TEXT, textposition="outside", marker_line_width=0)
    fig.update_layout(showlegend=False, yaxis_title="₹ per month", xaxis_title=None)
    return style_fig(fig)


def perk_breakdown_pie_chart():
    data = salary_service.calculate_perk_cost()
    breakdown = data["breakdown"]
    if not breakdown:
        return None
    df = pd.DataFrame({"Category": list(breakdown.keys()), "Cost": list(breakdown.values())})
    df = df.sort_values("Cost", ascending=False)
    fig = px.pie(df, names="Category", values="Cost", title="Monthly Perks Cost Breakdown", hole=0.55,
                 color_discrete_sequence=rose_palette(len(df)))
    fig.update_traces(textfont_color="white", marker_line=dict(color="white", width=2))
    return style_fig(fig, show_legend=True)


def salary_status_summary() -> dict:
    df = salary_service.get_salary_table()
    if df.empty:
        return {"paid": 0, "due": 0}
    counts = df["Salary Status"].value_counts().to_dict()
    return {"paid": counts.get("Paid", 0), "due": counts.get("Due", 0)}


def emp_type_distribution_pie():
    df = salary_service.get_salary_table()
    if df.empty:
        return None
    counts = df["Type"].value_counts().reset_index()
    counts.columns = ["Type", "Count"]
    counts = counts.sort_values("Count", ascending=False)
    fig = px.pie(counts, names="Type", values="Count",
                 title="Employee Type Distribution", hole=0.55,
                 color_discrete_sequence=rose_palette(len(counts)))
    fig.update_traces(textfont_color="white", marker_line=dict(color="white", width=2))
    return style_fig(fig, show_legend=True)
