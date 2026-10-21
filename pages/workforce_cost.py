"""
NexHR - Tab 03: Salary & Perks
Live, auto-refreshing salary dashboard: per-day running cost, per-employee
salary table (sortable, filterable, searchable), tick/cross salary status,
and the Perks module including canteen workers and the enforced ₹2.5L
minimum canteen budget.
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from services import salary_service
from analytics import salary_analysis
from database.connection import session_scope
from database import queries as q
from assets.theme import page_header, section_title


def render():
    page_header("Salary & Perks", "Compensation and employee benefit insights")

    top = st.columns([3, 1])
    with top[1]:
        auto_refresh = st.toggle("Live auto-refresh", value=False,
                                  help="Re-queries the database on an interval so this tab always shows current, not stale, data.")
    if auto_refresh:
        st_autorefresh(interval=10_000, key="salary_autorefresh")  # every 10s
        st.caption("Auto-refreshing every 10 seconds from the database.")
    else:
        st.caption("Data is re-queried from the database on every page interaction (no cached/stale copy).")

    cost_info = salary_service.calculate_daily_salary()
    k1, k2, k3 = st.columns(3)
    k1.metric("Daily Salary Cost", f"₹{cost_info['daily_cost']:,.0f}")
    k2.metric("Monthly Payroll", f"₹{cost_info['monthly_payroll']:,.0f}")
    k3.metric("Annualized Payroll", f"₹{cost_info['annual_payroll']:,.0f}")

    st.write("")
    tab1, tab2, tab3 = st.tabs(["Per-Employee Salary", "Perks & Benefits", "Daily Cost Breakdown"])

    # ------------------------------------------------------------------
    with tab1:
        with session_scope() as db:
            depts = ["All"] + [d.name for d in q.get_departments(db)]
            roles = ["All"] + sorted({e.role for e in q.get_all_employees(db)})

        fcol1, fcol2, fcol3, fcol4, fcol5 = st.columns(5)
        dept_filter = fcol1.selectbox("Department", depts, key="sal_dept")
        role_filter = fcol2.selectbox("Role", roles, key="sal_role")
        type_filter = fcol3.selectbox("Type", ["All", "Full-Time", "Part-Time", "Contract", "Intern", "Canteen Staff"], key="sal_type")
        status_filter = fcol4.selectbox("Salary Status", ["All", "Paid", "Due"], key="sal_status")
        search_query = fcol5.text_input("Search name/ID", key="sal_search")

        df = salary_service.get_salary_table(dept_filter, role_filter, type_filter, status_filter)
        if search_query and not df.empty:
            df = df[df["Name"].str.contains(search_query, case=False) |
                     df["Emp ID"].str.contains(search_query, case=False)]

        if df.empty:
            st.info("No employees match the selected filters.")
        else:
            sort_col1, sort_col2 = st.columns(2)
            sort_by = sort_col1.selectbox("Sort by", ["Department", "Total Payout", "Increment %", "Name"], key="sal_sort")
            ascending = sort_col2.radio("Order", ["Ascending", "Descending"], horizontal=True, key="sal_order") == "Ascending"
            df = df.sort_values(sort_by, ascending=ascending)

            display_df = df.copy()
            display_df["Paid?"] = display_df["Salary Status"].apply(lambda s: "✓ Paid" if s == "Paid" else "✕ Due")
            display_df = display_df.drop(columns=["Salary Status"])
            st.dataframe(display_df, width='stretch', hide_index=True, height=420)
            st.caption(f"Showing {len(display_df)} employee(s). Total payout for this view: "
                       f"₹{display_df['Total Payout'].sum():,.0f}")

    # ------------------------------------------------------------------
    with tab2:
        perk_info = salary_service.calculate_perk_cost()
        p1, p2 = st.columns(2)
        p1.metric("Total Monthly Perks Cost", f"₹{perk_info['total_monthly_perks']:,.0f}")
        floor_note = " (minimum ₹2.5L floor applied)" if perk_info["canteen_floor_applied"] else ""
        p2.metric("Canteen Budget", f"₹{perk_info['breakdown']['Canteen']:,.0f}{floor_note}")

        if perk_info["canteen_floor_applied"]:
            st.info(f"Actual logged canteen spend was ₹{perk_info['canteen_actual_spend']:,.0f}, "
                    "which is below the company's enforced minimum canteen budget of ₹2,50,000 "
                    "(khana zaruri hota hai) — so the minimum has been applied instead.")

        pie = salary_analysis.perk_breakdown_pie_chart()
        if pie:
            st.plotly_chart(pie, width='stretch')

        section_title("Canteen & Support Staff", "users")
        st.caption("Canteen workers are company employees too — their salaries are included in the "
                   "regular payroll above (Employee Type = 'Canteen Staff'), not treated separately.")
        canteen_df = salary_service.get_salary_table(emp_type="Canteen Staff")
        if canteen_df.empty:
            st.info("No canteen staff records found.")
        else:
            st.dataframe(canteen_df.drop(columns=["Salary Status", "Last Paid"], errors="ignore"),
                         width='stretch', hide_index=True)

    # ------------------------------------------------------------------
    with tab3:
        section_title("Daily Workforce Cost Breakdown", "bar-chart")
        fcol1, fcol2, fcol3 = st.columns(3)
        with session_scope() as db:
            depts = ["All"] + [d.name for d in q.get_departments(db)]
            roles = ["All"] + sorted({e.role for e in q.get_all_employees(db)})
        d_dept = fcol1.selectbox("Department", depts, key="daily_dept")
        d_role = fcol2.selectbox("Role", roles, key="daily_role")
        d_type = fcol3.selectbox("Type", ["All", "Full-Time", "Part-Time", "Contract", "Intern", "Canteen Staff"], key="daily_type")

        filtered = salary_service.get_salary_table(d_dept, d_role, d_type)
        if filtered.empty:
            st.info("No employees match the selected filters.")
        else:
            monthly = filtered["Total Payout"].sum()
            annual = monthly * 12
            daily = annual / 365
            c1, c2, c3 = st.columns(3)
            c1.metric("Annual Salary (filtered)", f"₹{annual:,.0f}")
            c2.metric("Monthly (filtered)", f"₹{monthly:,.0f}")
            c3.metric("Daily Cost (filtered)", f"₹{daily:,.0f}")
