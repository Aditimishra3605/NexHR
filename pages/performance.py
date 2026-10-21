"""
NexHR - Tab 04: Performance & Rewards
Hierarchy-based performance view, project status per employee, and an
increment calculator that shows total additional cost to the company.
"""
import streamlit as st

from services import performance_service, salary_service
from database.connection import session_scope
from database import queries as q
from assets.theme import page_header, section_title, card_start, card_end


def render():
    page_header("Performance & Rewards", "Employee performance and reward analytics")

    section_title("Performance & Bonus Overview", "award")
    df = performance_service.get_performance_bonus_table()
    if df.empty:
        st.info("No employees found.")
        return

    fcol1, fcol2 = st.columns(2)
    with session_scope() as db:
        depts = ["All"] + [d.name for d in q.get_departments(db)]
    dept_filter = fcol1.selectbox("Department", depts, key="perf_dept")
    rating_filter = fcol2.selectbox("Rating", ["All", "Excellent", "Very Good", "Average", "Bad", "Not Reviewed"], key="perf_rating")

    view_df = df.copy()
    if dept_filter != "All":
        view_df = view_df[view_df["Department"] == dept_filter]
    if rating_filter != "All":
        view_df = view_df[view_df["Rating"] == rating_filter]

    st.dataframe(view_df.drop(columns=["_id"]), width='stretch', hide_index=True, height=350)

    st.markdown("---")

    # --- Hierarchy view ---
    section_title("Reporting Hierarchy", "sitemap")
    st.caption("Based on department managers.")
    with session_scope() as db:
        managers = [
            {"id": e.id, "label": f"{e.name} ({e.emp_code})"}
            for e in q.get_all_employees(db, active_only=True)
            if q.get_reportees(db, e.id)
        ]
    if not managers:
        st.info("No manager/reportee relationships found.")
    else:
        manager_labels = [m["label"] for m in managers]
        chosen = st.selectbox("View team under manager:", manager_labels, key="hierarchy_manager")
        manager_id = managers[manager_labels.index(chosen)]["id"]
        reportees = performance_service.get_reporting_hierarchy(manager_id)
        cols = st.columns(min(len(reportees), 4) or 1)
        for i, r in enumerate(reportees):
            with cols[i % len(cols)]:
                # card_start() aur card_end() hata kar st.container use karein
                with st.container(border=True):
                    st.markdown(f"**{r['name']}**")
                    st.caption(f"{r['role']} · {r['rating']}")

    st.markdown("---")

    # --- Increment Calculator ---
    section_title("Increment Cost Calculator", "target")
    st.caption("Select employees and a % increment to preview the total additional cost to the company.")

    with session_scope() as db:
        all_emps = q.get_all_employees(db, active_only=True)
        emp_options = {f"{e.name} ({e.emp_code})": e.id for e in all_emps}

    selected_labels = st.multiselect("Select employees for increment", list(emp_options.keys()),
                                      key="increment_emp_select")
    increment_pct = st.slider("Increment %", min_value=0, max_value=50, value=10, step=1, key="increment_pct")

    if selected_labels:
        emp_ids = [emp_options[label] for label in selected_labels]
        result = salary_service.calculate_increment_cost(emp_ids, increment_pct)

        c1, c2, c3 = st.columns(3)
        c1.metric("Current Total (monthly)", f"₹{result['current_total_monthly']:,.0f}")
        c2.metric("New Total (monthly)", f"₹{result['new_total_monthly']:,.0f}")
        c3.metric("Additional Annual Cost to Company", f"₹{result['additional_annual_cost']:,.0f}",
                  delta=f"+₹{result['additional_monthly_cost']:,.0f}/month")

        st.dataframe(result["details"], width='stretch', hide_index=True)
    else:
        st.info("Select one or more employees above to calculate increment cost.")
