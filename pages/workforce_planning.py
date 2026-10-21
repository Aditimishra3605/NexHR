"""
NexHR - Tab 06: Hire & Fire / Workforce Planning
Rule-based hiring recommendations (skill gap + estimated CTC) shown as a
box visual after the user enters requirements, plus a workforce risk /
retention analysis. Final hire/fire decisions remain with authorized
human decision-makers -- this tab only surfaces analytical indicators.
"""
import streamlit as st

from services import workforce_service
from database.connection import session_scope
from database import queries as q
from assets.theme import page_header, section_title, card_start, card_end


def render():
    page_header("Workforce Planning", "Workforce requirements, skill gaps and staffing insights")

    section_title("Hiring Recommendation", "target")

    with session_scope() as db:
        depts = [d.name for d in q.get_departments(db)]

    with st.form("hiring_form"):
        c1, c2 = st.columns(2)
        department = c1.selectbox("Department", depts)
        role = c2.text_input("Role", placeholder="e.g. Software Engineer")

        c3, c4 = st.columns(2)
        skills_raw = c3.text_input("Required Skills (comma separated)", placeholder="Python, SQL, AWS")
        experience = c4.number_input("Experience Needed (years)", min_value=0.0, max_value=25.0, value=2.0, step=0.5)

        c5, c6 = st.columns(2)
        budget = c5.number_input("Budget (monthly, per role) — optional cap", min_value=0, value=0, step=5000)
        num_required = c6.number_input("Number of Employees Required", min_value=1, max_value=50, value=1)

        submitted = st.form_submit_button("Generate Recommendation", width='stretch', type="primary")

    if submitted:
        skills = [s.strip() for s in skills_raw.split(",") if s.strip()] or ["General"]
        rec = workforce_service.generate_hiring_recommendation(department, role or "Unspecified Role",
                                                                 skills, experience, int(num_required))
        if "error" in rec:
            st.error(rec["error"])
        else:
            card_start(f"Recommendation — {rec['role']} · {rec['department']}")
            st.markdown(f"**Current {rec['department']} team:** {rec['current_team_size']} employees")
            st.markdown("**Skill Gap:**")
            for skill, gap in rec['skill_gap'].items():
                st.markdown(f"&nbsp;&nbsp;• {skill} — {gap} employee(s) needed", unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            m1.metric("Estimated CTC per hire (monthly)", f"₹{rec['estimated_ctc_monthly_per_hire']:,.0f}")
            m2.metric(f"Total additional cost ({rec['number_required']} hire(s), monthly)",
                      f"₹{rec['total_additional_monthly_cost']:,.0f}")
            st.caption(f"Annualized: ₹{rec['estimated_ctc_annual_per_hire']:,.0f} per hire · "
                       f"₹{rec['total_additional_annual_cost']:,.0f} total")
            card_end()

            if budget and rec["estimated_ctc_monthly_per_hire"] > budget:
                st.warning(f"Estimated CTC (₹{rec['estimated_ctc_monthly_per_hire']:,.0f}) exceeds "
                           f"your stated budget cap of ₹{budget:,.0f} per role.")

            if st.button("Log this as a hiring requirement"):
                workforce_service.log_hire_fire_action("hire", role=role, reason=f"{num_required} needed in {department}")
                st.success("Logged. Final hiring decisions remain with HR/authorized decision-makers.")

    st.markdown("---")

    # --- Existing hiring requirements ---
    section_title("Open Hiring Requirements", "sliders")
    req_df = workforce_service.get_hiring_requirements_table()
    if req_df.empty:
        st.info("No hiring requirements logged yet.")
    else:
        st.dataframe(req_df, width='stretch', hide_index=True)

    st.markdown("---")

    # --- Workforce Risk / Retention Analysis ---
    section_title("Workforce Risk / Retention Analysis", "alert-triangle")
    st.caption("Employees flagged for HR review based on performance score, project allocation, "
               "tenure, repeated performance issues, and complaint history. These are analytical "
               "indicators only — final decisions rest with HR.")

    risk_df = workforce_service.workforce_risk_analysis()
    if risk_df.empty:
        st.success("No employees currently flagged for review.")
    else:
        st.dataframe(risk_df, width='stretch', hide_index=True)
        st.caption(f"{len(risk_df)} employee(s) flagged out of the active workforce.")

        with st.expander("Log a fire/exit review action"):
            emp_choice = st.selectbox("Employee", risk_df["Name"].tolist())
            reason = st.text_input("Reason for review", placeholder="e.g. Performance below threshold for 2 cycles")
            if st.button("Log Review Action"):
                emp_code = risk_df[risk_df["Name"] == emp_choice]["Emp ID"].iloc[0]
                with session_scope() as db:
                    emp = q.get_employee_by_code(db, emp_code)
                    emp_id = emp.id if emp else None
                workforce_service.log_hire_fire_action("fire", employee_id=emp_id, reason=reason)
                st.success(f"Review action logged for {emp_choice}. This is a record for HR — "
                           "no automatic termination occurs.")
