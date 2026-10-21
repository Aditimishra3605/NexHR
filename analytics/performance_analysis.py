
import plotly.express as px

from services import performance_service, employee_service
from assets.theme import rose_palette, style_fig, PRIMARY, PRIMARY_DARK, SECONDARY, ACCENT

_RATING_COLOR_MAP = {
    "Excellent": PRIMARY_DARK,
    "Very Good": PRIMARY,
    "Average": SECONDARY,
    "Bad": ACCENT,
}


def top_performers_bar_chart(n: int = 5):
    df = performance_service.get_top_performers(n)
    if df.empty:
        return None
    fig = px.bar(df, x="Name", y="Performance Score", color="Rating",
                 title=f"Top {n} Performing Employees", text_auto=True,
                 color_discrete_map=_RATING_COLOR_MAP)
    fig.update_traces(textfont_color="white", marker_line_width=0)
    fig.update_layout(yaxis_title="Performance Score (%)", xaxis_title=None)
    return style_fig(fig, show_legend=True)


def avg_performance_by_department_chart():
    df = performance_service.get_avg_performance_by_department()
    if df.empty:
        return None
    df = df.sort_values("Avg Performance", ascending=False)
    fig = px.bar(df, x="Department", y="Avg Performance", color="Department",
                 title="Average Performance Score by Department", text_auto=True,
                 color_discrete_sequence=rose_palette(len(df)))
    fig.update_traces(textfont_color="white", marker_line_width=0, textposition="inside")
    fig.update_layout(showlegend=False, yaxis_title="Avg Performance (%)", xaxis_title=None)
    return style_fig(fig)


def experience_distribution_chart():
    df = employee_service.get_all_employees_df()
    if df.empty:
        return None
    fig = px.histogram(df, x="Experience (yrs)", nbins=10,
                        title="Employees by Experience", color_discrete_sequence=[PRIMARY])
    fig.update_traces(marker_line_width=0)
    fig.update_layout(yaxis_title="Number of Employees", bargap=0.12)
    return style_fig(fig)


def role_distribution_chart():
    df = employee_service.get_all_employees_df()
    if df.empty:
        return None
    counts = df["Role"].value_counts().reset_index()
    counts.columns = ["Role", "Count"]
    counts = counts.sort_values("Count", ascending=False)
    fig = px.bar(counts, x="Role", y="Count", title="Employees by Role", text_auto=True,
                 color_discrete_sequence=[PRIMARY_DARK])
    fig.update_traces(textfont_color="white", marker_line_width=0, textposition="inside")
    fig.update_layout(xaxis_title=None, yaxis_title="Number of Employees")
    return style_fig(fig, height=380)
