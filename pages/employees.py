"""
NexHR - Tab 02: Employee Details
Layout order (per corporate UX spec): View Employee Profile first, then
Search Employee, then the Employee Table. Search (by name OR emp ID,
partial matching) and the profile click-through are both fully intact --
only their position and visual styling changed.
"""
import os
import streamlit as st

from services import employee_service
from assets.theme import (
    page_header, section_title, card_start, card_end, field, status_pill,
)

RESUME_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)))

_STATUS_KIND = {"Active": "green", "Inactive": "red", "On Leave": "amber"}
_SALARY_KIND = {"Paid": "green", "Due": "amber"}


def _render_profile(emp_id: int):
    d = employee_service.get_employee_details(emp_id)
    if not d:
        st.error("Employee not found.")
        return

    top = st.columns([2.2, 1, 1, 1])
    with top[0]:
        st.markdown(f"### {d['name']}")
        st.caption(f"{d['emp_code']}  ·  {d['role']}  ·  {d['department']}")
    top[1].metric("Salary", f"₹{d['effective_salary']:,.0f}")
    top[2].metric("Performance", f"{d['performance_score']}%" if d['performance_score'] else "N/A")
    top[3].metric("Tenure", d["tenure_display"])

    # Row 1: Employment Information (Left) | Employee Timeline (Right)
    row1_col1, row1_col2 = st.columns([1.3, 1])

    with row1_col1:
        card_start("Employment Information")
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            field("Joining Date", str(d['joining_date']))
            field("Employee Type", d['emp_type'])
            field("Department", d['department'])
        with r1c2:
            field("Experience", f"{d['experience_years']} years")
            field("Tenure", d['tenure_display'])
            field("Current Project", d['current_project'])
        field("Reporting Manager", d['manager'])
        card_end()

    with row1_col2:
        card_start("Employee Timeline")
        if not d["timeline"]:
            st.caption("No timeline events recorded.")
        for t in d["timeline"]:
            st.markdown(f"**{t['date']}** — {t['event']}")
            if t["description"]:
                st.caption(t["description"])
        card_end()

    # Row 2: Compensation (Left) | Performance (Right)
    row2_col1, row2_col2 = st.columns([1.3, 1])

    with row2_col1:
        card_start("Compensation")
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            field("Current Salary", f"₹{d['effective_salary']:,.0f}")
        with r2c2:
            st.markdown('<div class="nexhr-field-label">Salary Status</div>', unsafe_allow_html=True)
            st.markdown(status_pill(d['salary_status'], _SALARY_KIND.get(d['salary_status'], 'rose')),
                        unsafe_allow_html=True)
        card_end()

    with row2_col2:
        card_start("Performance")
        r3c1, r3c2 = st.columns(2)
        with r3c1:
            field("Performance Score", f"{d['performance_score']}%" if d['performance_score'] else "Not Reviewed")
        with r3c2:
            field("Rating", d['rating'])
        st.markdown('<div class="nexhr-field-label">Current Status</div>', unsafe_allow_html=True)
        st.markdown(status_pill(d['status'], _STATUS_KIND.get(d['status'], 'rose')), unsafe_allow_html=True)
        card_end()

    # Row 3: Work History (Left) | Resume (Right)
    row3_col1, row3_col2 = st.columns([1.3, 1])

    with row3_col1:
        if d["work_history"]:
            card_start("Work History")
            for w in d["work_history"]:
                st.write(f"**{w['company']}** — {w['role']} ({w['duration_years']} yrs, {w['year']})")
            card_end()

    with row3_col2:
        card_start("Resume")
        resume_path = os.path.join(RESUME_ROOT, d["resume_link"]) if d["resume_link"] else None
        if resume_path and os.path.exists(resume_path):
            with open(resume_path, "rb") as f:
                st.download_button("Download Resume (PDF)", data=f.read(),
                                    file_name=f"{d['emp_code']}_resume.pdf", mime="application/pdf")
        else:
            st.caption("No resume on file.")
        card_end()

def render():
    page_header("Employee Details", "Manage and explore employee workforce information")

    # ------------------------------------------------------------------
    # 1. VIEW EMPLOYEE PROFILE (uses the full roster, independent of search)
    # ------------------------------------------------------------------
    section_title("View Employee Profile", "user")
    full_df = employee_service.get_all_employees_df()
    profile_options = ["Select an employee..."] + [
        f"{row['Name']} ({row['Emp ID']})" for _, row in full_df.iterrows()
    ]
    profile_choice = st.selectbox("Select an employee...", profile_options, label_visibility="collapsed",
                                   key="profile_select")
    if profile_choice != "Select an employee...":
        idx = profile_options.index(profile_choice) - 1
        emp_internal_id = int(full_df.iloc[idx]["_id"])
        _render_profile(emp_internal_id)

    st.markdown("---")

    # ------------------------------------------------------------------
    # 2. SEARCH EMPLOYEE
    # ------------------------------------------------------------------
    section_title("Search Employee", "search")
    
    # State reset karne ke liye ek chota callback function banayein
    def clear_search():
        st.session_state["emp_search_query"] = ""

    search_col, clear_col = st.columns([4, 1])
    query = search_col.text_input("Search by name or Employee ID (e.g. 'Priya' or 'NEX-1004')",
                                   key="emp_search_query", label_visibility="collapsed",
                                   placeholder="Search by name or Employee ID (e.g. 'Priya' or 'NEX-1004')")
    
    # if condition aur st.rerun() hata kar yahan on_click callback lagayein
    clear_col.button("Clear", width='stretch', on_click=clear_search)

    df = employee_service.search_employee(query)
    if df.empty:
        st.warning("No matching employees found. Showing full employee list instead.")
        df = employee_service.get_all_employees_df()
    else:
        st.caption(f"{len(df)} employee(s) found.")
    # ------------------------------------------------------------------
    # 3. EMPLOYEE TABLE
    # ------------------------------------------------------------------
    section_title("Employee Table", "briefcase")
    display_df = df.drop(columns=["_id"])
    st.dataframe(display_df, width='stretch', hide_index=True, height=380)
