"""
NexHR - Salary Service
Business logic for Tab 03 (Salaries) and the Perks module:
daily/monthly payroll cost, perks with a canteen budget floor, increment
cost preview, and salary status tracking. Canteen workers are included as
regular employees (emp_type = Canteen Staff) so their pay flows through
the same payroll calculations.
"""
from datetime import date
import pandas as pd

from database.connection import session_scope
from database import queries as q
from database.models import SalaryStatus

MINIMUM_MONTHLY_CANTEEN_BUDGET = 250_000.0  # ₹2.5L floor, enforced regardless of actual spend


def get_salary_table(department: str = "All", role: str = "All", emp_type: str = "All",
                      status: str = "All") -> pd.DataFrame:
    """Tabular per-employee salary view with filters, used by the Salary tab."""
    with session_scope() as db:
        employees = q.get_all_employees(db)
        rows = []
        for e in employees:
            if department != "All" and (not e.department or e.department.name != department):
                continue
            if role != "All" and e.role != role:
                continue
            if emp_type != "All" and e.emp_type.value != emp_type:
                continue
            sal = e.salary_record
            if not sal:
                continue
            if status != "All" and sal.salary_status.value != status:
                continue
            rows.append({
                "Emp ID": e.emp_code,
                "Name": e.name,
                "Department": e.department.name if e.department else "-",
                "Role": e.role,
                "Type": e.emp_type.value,
                "Base Salary": sal.base_salary,
                "Increment %": sal.increment_percent,
                "Bonus": sal.bonus_amount,
                "Total Payout": sal.total_payout,
                "Salary Status": sal.salary_status.value,
                "Last Paid": sal.last_paid_date,
            })
        return pd.DataFrame(rows)


def calculate_total_payroll() -> float:
    """Sum of total monthly payout across all active employees."""
    with session_scope() as db:
        employees = q.get_all_employees(db, active_only=True)
        return round(sum(e.salary_record.total_payout for e in employees if e.salary_record), 2)


def calculate_daily_salary() -> dict:
    """
    Live daily workforce cost. Annual salary = monthly payout * 12;
    daily cost = annual / 365. This always reflects the current DB state
    (i.e. it's re-run on every Streamlit refresh -- there is no cached/stale copy).
    """
    monthly = calculate_total_payroll()
    annual = monthly * 12
    daily = annual / 365
    return {"monthly_payroll": round(monthly, 2), "annual_payroll": round(annual, 2),
            "daily_cost": round(daily, 2)}


def calculate_perk_cost() -> dict:
    """
    Total perks cost breakdown by category. The canteen category is floored
    at MINIMUM_MONTHLY_CANTEEN_BUDGET even if actual logged spend is lower,
    because "khana zaruri hota hai".
    """
    with session_scope() as db:
        perks = q.get_all_perks(db)
        breakdown = {}
        for p in perks:
            breakdown[p.perk_type.value] = breakdown.get(p.perk_type.value, 0) + p.monthly_cost

        canteen_actual = breakdown.get("Canteen", 0.0)
        canteen_final = max(canteen_actual, MINIMUM_MONTHLY_CANTEEN_BUDGET)
        breakdown["Canteen"] = round(canteen_final, 2)

        total = round(sum(breakdown.values()), 2)
        return {
            "breakdown": breakdown,
            "canteen_actual_spend": round(canteen_actual, 2),
            "canteen_floor_applied": canteen_actual < MINIMUM_MONTHLY_CANTEEN_BUDGET,
            "total_monthly_perks": total,
        }


def calculate_increment_cost(emp_ids: list[int], increment_percent: float) -> dict:
    """
    Preview the total additional cost to the company if the given employees
    receive `increment_percent` on top of their current effective salary.
    Used by the Performance & Rewards tab's increment calculator.
    """
    with session_scope() as db:
        current_total = 0.0
        new_total = 0.0
        details = []
        for emp_id in emp_ids:
            e = q.get_employee_by_id(db, emp_id)
            if not e or not e.salary_record:
                continue
            current = e.salary_record.effective_salary
            new = round(current * (1 + increment_percent / 100), 2)
            current_total += current
            new_total += new
            details.append({"Name": e.name, "Emp ID": e.emp_code,
                             "Current Salary": current, "New Salary": new,
                             "Increase": round(new - current, 2)})
        return {
            "current_total_monthly": round(current_total, 2),
            "new_total_monthly": round(new_total, 2),
            "additional_monthly_cost": round(new_total - current_total, 2),
            "additional_annual_cost": round((new_total - current_total) * 12, 2),
            "details": details,
        }


def mark_salary_paid(emp_id: int):
    with session_scope() as db:
        e = q.get_employee_by_id(db, emp_id)
        if e and e.salary_record:
            e.salary_record.salary_status = SalaryStatus.PAID
            e.salary_record.last_paid_date = date.today()


def get_department_cost_summary() -> pd.DataFrame:
    """Total & average salary cost grouped by department -- feeds dashboard charts."""
    with session_scope() as db:
        employees = q.get_all_employees(db)
        agg = {}
        for e in employees:
            if not e.department or not e.salary_record:
                continue
            dept = e.department.name
            agg.setdefault(dept, []).append(e.salary_record.total_payout)
        rows = [{"Department": d, "Total Cost": round(sum(v), 2),
                  "Avg Cost": round(sum(v) / len(v), 2), "Headcount": len(v)}
                for d, v in agg.items()]
        return pd.DataFrame(rows)
