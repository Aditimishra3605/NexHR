"""
NexHR - An Integrated Employee Management, Performance & Payroll Analytics Platform
Main entry point. Run with: streamlit run app.py
"""
import streamlit as st
from streamlit_option_menu import option_menu

from database.connection import init_db
from assets.theme import apply_theme, render_sidebar_brand, PRIMARY, PRIMARY_DARK, LIGHT_ACCENT, SECONDARY_TEXT, MAIN_TEXT

st.set_page_config(
    page_title="NexHR | Workforce Intelligence Platform",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ensure DB tables exist even on a fresh clone (does not overwrite existing data).
init_db()

apply_theme()

# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    render_sidebar_brand()
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Employee Details", "Salary & Perks", "Performance & Rewards",
                 "Projects", "Workforce Planning", "AI Assistant"],
        icons=["grid-1x2", "people", "cash-coin", "trophy",
               "kanban", "person-gear", "cpu"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": SECONDARY_TEXT, "font-size": "15px"},
            "nav-link": {
                "font-size": "13.5px",
                "text-align": "left",
                "margin": "2px 0",
                "border-radius": "8px",
                "padding": "9px 12px",
                "color": MAIN_TEXT,
                "--hover-color": LIGHT_ACCENT,
            },
            "nav-link-selected": {
                "background-color": LIGHT_ACCENT,
                "color": PRIMARY_DARK,
                "font-weight": "600",
                "icon-color": PRIMARY_DARK,
            },
        },
    )
    st.markdown("---")
    st.caption("Major Project · B.Tech CSE (DSDA) · 7th Semester")

# ---------------------------------------------------------------------------
# Route to page module
# ---------------------------------------------------------------------------
if selected == "Dashboard":
    from pages import dashboard
    dashboard.render()
elif selected == "Employee Details":
    from pages import employees
    employees.render()
elif selected == "Salary & Perks":
    from pages import workforce_cost
    workforce_cost.render()
elif selected == "Performance & Rewards":
    from pages import performance
    performance.render()
elif selected == "Projects":
    from pages import projects
    projects.render()
elif selected == "Workforce Planning":
    from pages import workforce_planning
    workforce_planning.render()
elif selected == "AI Assistant":
    from pages import ai_assistant
    ai_assistant.render()



from data.seed_data import (
    seed,
)
try:
  seed()  # Yeh function aapke database tables mein sample data insert kar dega
except Exception as e:
  print("Database already seeded or error:", e)