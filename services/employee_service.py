"""
NexHR - Employee Service
Business logic for Tab 02 (Employee Details): search, profile assembly,
resume links, work history and timeline.
"""
from datetime import date
import pandas as pd

from database.connection import session_scope
from database import queries as q


def search_employee(query: str) -> pd.DataFrame:
    """
    Search employees by partial name OR emp_code (case-insensitive).
    Returns a flat DataFrame ready for st.dataframe display.
    Empty query returns the full employee list.
    """
    with session_scope() as db:
        results = q.search_employees(db, query) if query else q.get_all_employees(db)
        rows = []
        for e in results:
            rows.append({
                "Emp ID": e.emp_code,
                "Name": e.name,
                "Department": e.department.name if e.department else "-",
                "Role": e.role,
                "Type": e.emp_type.value,
                "Experience (yrs)": e.experience_years,
                "Current Project": e.current_project.name if e.current_project else "Unassigned",
                "Status": e.status.value,
                "_id": e.id,
            })
        return pd.DataFrame(rows)


def get_all_employees_df() -> pd.DataFrame:
    return search_employee("")


def get_employee_details(emp_id: int) -> dict:
    """
    Full profile payload for the Employee Profile card:
    basic info, salary, performance, project, tenure, resume link,
    work history and timeline -- exactly as sketched in the blueprint.
    """
    with session_scope() as db:
        e = q.get_employee_by_id(db, emp_id)
        if not e:
            return {}

        latest_perf = q.get_latest_performance(db, emp_id)
        work_hist = q.get_work_history(db, emp_id)
        timeline = q.get_timeline(db, emp_id)

        return {
            "id": e.id,
            "emp_code": e.emp_code,
            "name": e.name,
            "email": e.email,
            "role": e.role,
            "department": e.department.name if e.department else "-",
            "emp_type": e.emp_type.value,
            "joining_date": e.joining_date,
            "experience_years": e.experience_years,
            "tenure_display": e.tenure_display,
            "current_project": e.current_project.name if e.current_project else "Unassigned",
            "base_salary": e.salary_record.base_salary if e.salary_record else 0,
            "effective_salary": e.salary_record.effective_salary if e.salary_record else 0,
            "salary_status": e.salary_record.salary_status.value if e.salary_record else "-",
            "performance_score": latest_perf.performance_score if latest_perf else None,
            "rating": latest_perf.rating.value if latest_perf else "Not Reviewed",
            "status": e.status.value,
            "resume_link": e.resume_link,
            "manager": e.manager.name if e.manager else "-",
            "work_history": [
                {"company": w.company_name, "role": w.role, "duration_years": w.duration_years, "year": w.year}
                for w in work_hist
            ],
            "timeline": [
                {"date": t.event_date, "event": t.event_type.value, "description": t.description}
                for t in timeline
            ],
        }


def get_employee_by_code_or_id(identifier: str) -> dict:
    """Convenience lookup supporting both emp_code (e.g. 'NEX-1004') and raw id."""
    with session_scope() as db:
        emp = q.get_employee_by_code(db, identifier)
        if not emp and identifier.isdigit():
            emp = q.get_employee_by_id(db, int(identifier))
        return get_employee_details(emp.id) if emp else {}
