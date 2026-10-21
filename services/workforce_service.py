"""
NexHR - Workforce Planning Service
Business logic for Tab 06 (Hire & Fire / Workforce Planning):
rule-based hiring recommendations (skill gap + estimated CTC) and a
workforce risk / retention analysis. All outputs are analytical
indicators for HR review -- final hire/fire decisions stay with
authorized human decision-makers (never automated here).
"""
from datetime import date, datetime
import pandas as pd

from database.connection import session_scope
from database import queries as q
from database.models import FiringLog, Rating

LOW_PERFORMANCE_THRESHOLD = 55.0     # performance % below this flags a review
LONG_TENURE_STAGNANT_YEARS = 3       # tenure beyond this with no rating improvement -> flag
MIN_COMPLAINTS_FOR_FLAG = 2


def get_hiring_requirements_table() -> pd.DataFrame:
    with session_scope() as db:
        reqs = q.get_hiring_requirements(db)
        rows = [{
            "Req ID": r.id,
            "Department": r.department.name if r.department else "-",
            "Role": r.role,
            "Required Skills": r.required_skills,
            "Experience Required (yrs)": r.experience_required,
            "Budget (per role, monthly)": r.budget,
            "Number Required": r.number_required,
            "Status": r.status.value,
        } for r in reqs]
        return pd.DataFrame(rows)


def generate_hiring_recommendation(department_name: str, role: str, required_skills: list[str],
                                    experience_required: float, number_required: int) -> dict:
    """
    Rule-based recommendation box: current team size, skill gap per required
    skill (naive count of employees NOT already tagged with that role/skill
    within the department), and estimated CTC (avg salary for that
    role+department, or department average as fallback).
    """
    with session_scope() as db:
        dept = q.get_department_by_name(db, department_name)
        if not dept:
            return {"error": f"Department '{department_name}' not found."}

        dept_employees = [e for e in q.get_all_employees(db) if e.department_id == dept.id]
        current_team_size = len(dept_employees)

        same_role_employees = [e for e in dept_employees if e.role.lower() == role.lower()]
        skill_gap = {skill: max(number_required - len(same_role_employees), 0) for skill in required_skills}

        if same_role_employees:
            salaries = [e.salary_record.effective_salary for e in same_role_employees if e.salary_record]
        else:
            salaries = [e.salary_record.effective_salary for e in dept_employees if e.salary_record]

        estimated_ctc_monthly = round(sum(salaries) / len(salaries), 2) if salaries else 0.0
        # Nudge estimate upward slightly for required experience above department average
        avg_exp = (sum(e.experience_years for e in dept_employees) / len(dept_employees)) if dept_employees else 0
        if experience_required > avg_exp:
            estimated_ctc_monthly = round(estimated_ctc_monthly * (1 + 0.05 * (experience_required - avg_exp)), 2)

        total_hiring_cost_monthly = round(estimated_ctc_monthly * number_required, 2)

        return {
            "department": department_name,
            "role": role,
            "current_team_size": current_team_size,
            "skill_gap": skill_gap,
            "estimated_ctc_monthly_per_hire": estimated_ctc_monthly,
            "estimated_ctc_annual_per_hire": round(estimated_ctc_monthly * 12, 2),
            "number_required": number_required,
            "total_additional_monthly_cost": total_hiring_cost_monthly,
            "total_additional_annual_cost": round(total_hiring_cost_monthly * 12, 2),
        }


def workforce_risk_analysis() -> pd.DataFrame:
    """
    Flags employees for HR review based on: performance score, project
    allocation, tenure & skill relevance signal, repeated performance
    issues, and complaint count. Output is advisory only.
    """
    with session_scope() as db:
        employees = q.get_all_employees(db, active_only=True)
        rows = []
        for e in employees:
            history = q.get_performance_history(db, e.id)
            latest = history[-1] if history else None
            complaints = q.get_complaints_count(db, e.id)

            reasons = []
            if latest and latest.performance_score < LOW_PERFORMANCE_THRESHOLD:
                reasons.append("Low performance score")
            if not e.current_project:
                reasons.append("No project allocation")
            if len(history) >= 2 and all(h.performance_score < LOW_PERFORMANCE_THRESHOLD for h in history[-2:]):
                reasons.append("Repeated performance issues")
            if complaints >= MIN_COMPLAINTS_FOR_FLAG:
                reasons.append(f"{complaints} complaints on record")
            if e.tenure_days / 365 >= LONG_TENURE_STAGNANT_YEARS and latest and latest.rating in (Rating.AVERAGE, Rating.BAD):
                reasons.append("Long tenure without growth")

            if reasons:
                rows.append({
                    "Emp ID": e.emp_code,
                    "Name": e.name,
                    "Department": e.department.name if e.department else "-",
                    "Performance Score": latest.performance_score if latest else None,
                    "Tenure": e.tenure_display,
                    "Complaints": complaints,
                    "Flags": ", ".join(reasons),
                })
        return pd.DataFrame(rows)


def log_hire_fire_action(action_type: str, employee_id: int = None, role: str = None, reason: str = None):
    """Audit log entry. Does not itself hire or fire -- purely a record for HR."""
    with session_scope() as db:
        entry = FiringLog(action_type=action_type, employee_id=employee_id, role=role,
                           reason=reason, action_date=datetime.utcnow())
        db.add(entry)
