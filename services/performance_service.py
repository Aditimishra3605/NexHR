"""
NexHR - Performance Service
Business logic for Dashboard top-performers and Tab 04
(Performance & Rewards): ratings, bonus eligibility, reporting hierarchy.
"""
import pandas as pd
from database.connection import session_scope
from database import queries as q
from database.models import Rating

BONUS_ELIGIBLE_RATINGS = {Rating.EXCELLENT, Rating.VERY_GOOD}


def get_top_performers(n: int = 5) -> pd.DataFrame:
    with session_scope() as db:
        employees = q.get_all_employees(db, active_only=True)
        rows = []
        for e in employees:
            latest = q.get_latest_performance(db, e.id)
            if latest:
                rows.append({
                    "Emp ID": e.emp_code, "Name": e.name,
                    "Department": e.department.name if e.department else "-",
                    "Performance Score": latest.performance_score,
                    "Rating": latest.rating.value,
                    "_id": e.id,
                })
        df = pd.DataFrame(rows)
        if df.empty:
            return df
        return df.sort_values("Performance Score", ascending=False).head(n).reset_index(drop=True)


def get_performance_bonus_table() -> pd.DataFrame:
    """Tab 04 main table: emp id, name, dept, project status, performance %, rating, bonus eligibility."""
    with session_scope() as db:
        employees = q.get_all_employees(db)
        rows = []
        for e in employees:
            latest = q.get_latest_performance(db, e.id)
            rows.append({
                "Emp ID": e.emp_code,
                "Name": e.name,
                "Department": e.department.name if e.department else "-",
                "Project Status": e.current_project.status.value if e.current_project else "No Project Assigned",
                "Performance (%)": latest.performance_score if latest else None,
                "Rating": latest.rating.value if latest else "Not Reviewed",
                "Bonus Eligible": "Yes" if (latest and latest.bonus_eligible) else "No",
                "_id": e.id,
            })
        return pd.DataFrame(rows)


def get_avg_performance_by_department() -> pd.DataFrame:
    with session_scope() as db:
        employees = q.get_all_employees(db)
        agg = {}
        for e in employees:
            latest = q.get_latest_performance(db, e.id)
            if latest and e.department:
                agg.setdefault(e.department.name, []).append(latest.performance_score)
        rows = [{"Department": d, "Avg Performance": round(sum(v) / len(v), 1)} for d, v in agg.items()]
        return pd.DataFrame(rows)


def get_reporting_hierarchy(manager_id: int) -> list[dict]:
    """Direct reportees of a manager -- feeds the hierarchy view."""
    with session_scope() as db:
        reportees = q.get_reportees(db, manager_id)
        result = []
        for r in reportees:
            latest = q.get_latest_performance(db, r.id)
            result.append({
                "id": r.id, "name": r.name, "role": r.role,
                "rating": latest.rating.value if latest else "Not Reviewed",
            })
        return result


def calculate_bonus_pool() -> dict:
    """Total bonus payout currently allocated across bonus-eligible employees."""
    with session_scope() as db:
        employees = q.get_all_employees(db, active_only=True)
        total_bonus = sum(e.salary_record.bonus_amount for e in employees if e.salary_record)
        eligible_count = 0
        for e in employees:
            latest = q.get_latest_performance(db, e.id)
            if latest and latest.bonus_eligible:
                eligible_count += 1
        return {"total_bonus_payout": round(total_bonus, 2), "eligible_employees": eligible_count}
