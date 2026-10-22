"""
NexHR - Tab 01: Dashboard
KPI cards, top performers, project overview, and supporting visualizations.
"""
import streamlit as st

from services import salary_service, performance_service, project_service, employee_service
from database.connection import session_scope
from database import queries as q
from database.models import EmployeeStatus
from analytics import salary_analysis, performance_analysis, workforce_analysis
from assets.theme import (
    page_header, section_title, status_pill, project_status_kind, card_start, card_end, field,
)


def render():
    page_header("Dashboard", "Workforce overview and organizational analytics")

    with session_scope() as db:
        all_emps = q.get_all_employees(db)
        active_emps = [e for e in all_emps if e.status == EmployeeStatus.ACTIVE]
        total_employees = len(all_emps)
        active_employees = len(active_emps)

    payroll_info = salary_service.calculate_daily_salary()
    perk_info = salary_service.calculate_perk_cost()

    with session_scope() as db:
        due_count = sum(1 for e in q.get_all_employees(db) if e.salary_record and e.salary_record.salary_status.value == "Due")
        due_amount = sum(e.salary_record.total_payout for e in q.get_all_employees(db)
                          if e.salary_record and e.salary_record.salary_status.value == "Due")

    # --- KPI Cards ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Employees", total_employees)
    c2.metric("Active Employees", active_employees)
    c3.metric("Monthly Payroll", f"₹{payroll_info['monthly_payroll']:,.0f}")

    st.write("") 
    
    c4, c5 = st.columns(2)
    c4.metric("Total Salary Due", f"₹{due_amount:,.0f}", delta=f"{due_count} employees", delta_color="inverse")
    c5.metric("Daily Workforce Cost", f"₹{payroll_info['daily_cost']:,.0f}")

    st.write("")
    c6, c7 = st.columns(2)
    c6.metric("Total Salary Paid (this cycle)",
              f"₹{payroll_info['monthly_payroll'] - due_amount:,.0f}")
    c7.metric("Total Monthly Perks Cost", f"₹{perk_info['total_monthly_perks']:,.0f}",
              help="Includes the enforced ₹2.5L minimum canteen budget.")

    st.markdown("---")

    # --- Top Performers + Project Overview ---
    left, right = st.columns([1.1, 1])

    with left:
        section_title("Top Performer Employees", "award")
        
        # Session state mein top_df store kar lete hain taaki select karne par data shuffle na ho
        if "cached_top_performers" not in st.session_state:
            st.session_state["cached_top_performers"] = performance_service.get_top_performers(5)
            
        top_df = st.session_state["cached_top_performers"]

        if top_df.empty:
            st.info("No performance data yet.")
        else:
            display_df = top_df.drop(columns=["_id"], errors="ignore")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            selected_name = st.selectbox(
                "View full details of:",
                options=top_df["Name"].tolist(),
                index=None,
                placeholder="Search an employee...",
                key="dash_top_performer_select_unique"
            )

    with right:
        section_title("Project Overview", "folder")
        proj_df = project_service.get_project_status()
        if proj_df.empty:
            st.info("No projects yet.")
        else:
            for i, (_, row) in enumerate(proj_df.iterrows()):
                pill = status_pill(row['Status'], project_status_kind(row['Status']))
                st.markdown(f"**{row['Project']}** &nbsp; {pill}", unsafe_allow_html=True)
                st.progress(min(int(row["Completion %"]), 100))
                st.caption(f"{row['Completion %']}% complete · Team of {row['Team Size']}")
                if i < len(proj_df) - 1:
                    st.markdown(
                        "<hr style='margin:8px 0;border-color:#E5E7EB;'>", unsafe_allow_html=True)

    # --- Employee Details Expander (Columns ke bahar render karein taaki poori width mile aur clash na ho) ---
    if st.session_state.get("dash_top_performer_select_unique"):
        selected_name = st.session_state["dash_top_performer_select_unique"]
        matched_row = top_df[top_df["Name"] == selected_name]
        if not matched_row.empty:
            emp_id_val = matched_row["_id"].iloc[0]
            # Handle both int or string ID safely
            try:
                emp_id = int(emp_id_val)
            except ValueError:
                emp_id = emp_id_val 

            details = employee_service.get_employee_details(emp_id)
            if details:
                with st.expander(f"📌 {details['name']} — {details['role']}", expanded=True):
                    dcol1, dcol2, dcol3 = st.columns(3)
                    with dcol1:
                        field("Department", details.get('department', 'N/A'))
                        field("Tenure", details.get('tenure_display', 'N/A'))
                    with dcol2:
                        field("Salary", f"₹{details.get('effective_salary', 0):,.0f}")
                        field("Current Project", details.get('current_project', 'N/A'))
                    with dcol3:
                        field("Rating", details.get('rating', 'N/A'))
                        field("Status", details.get('status', 'N/A'))

    st.markdown("---")

    # --- Charts Grid ---
    section_title("Workforce Analytics", "bar-chart")
    g1, g2 = st.columns(2)
    with g1:
        fig = workforce_analysis.department_headcount_chart()
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    with g2:
        fig = salary_analysis.emp_type_distribution_pie()
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    g3, g4 = st.columns(2)
    with g3:
        fig = performance_analysis.avg_performance_by_department_chart()
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    with g4:
        fig = performance_analysis.experience_distribution_chart()
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    g5, g6 = st.columns(2)
    with g5:
        fig = performance_analysis.role_distribution_chart()
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    with g6:
        fig = salary_analysis.department_cost_bar_chart()
        if fig:
            st.plotly_chart(fig, use_container_width=True)