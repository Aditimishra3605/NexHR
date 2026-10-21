"""
NexHR - Query Layer
Low-level, reusable SQLAlchemy queries. Services build business logic on
top of these; UI pages never touch the ORM directly.
"""
from datetime import date
from sqlalchemy import or_, func
from sqlalchemy.orm import Session, joinedload

from database.models import (
    Employee, Department, Salary, Performance, Project, Perk,
    HiringRequirement, WorkHistory, EmployeeTimeline, Complaint,
    EmployeeStatus,
)


def get_all_employees(db: Session, active_only: bool = False):
    q = db.query(Employee).options(
        joinedload(Employee.department),
        joinedload(Employee.salary_record),
        joinedload(Employee.current_project),
    )
    if active_only:
        q = q.filter(Employee.status == EmployeeStatus.ACTIVE)
    return q.order_by(Employee.id).all()


def get_employee_by_id(db: Session, emp_id: int):
    return db.query(Employee).filter(Employee.id == emp_id).first()


def get_employee_by_code(db: Session, emp_code: str):
    return db.query(Employee).filter(Employee.emp_code.ilike(emp_code.strip())).first()


def search_employees(db: Session, query: str):
    """Search by partial name match OR exact/partial employee code match."""
    query = query.strip()
    if not query:
        return get_all_employees(db)
    pattern = f"%{query}%"
    return (
        db.query(Employee)
        .filter(or_(Employee.name.ilike(pattern), Employee.emp_code.ilike(pattern)))
        .all()
    )


def get_departments(db: Session):
    return db.query(Department).order_by(Department.name).all()


def get_department_by_name(db: Session, name: str):
    return db.query(Department).filter(Department.name == name).first()


def get_all_projects(db: Session):
    return db.query(Project).options(joinedload(Project.manager)).order_by(Project.id).all()


def get_project_team(db: Session, project_id: int):
    return db.query(Employee).filter(Employee.project_id == project_id).all()


def get_latest_performance(db: Session, emp_id: int):
    return (
        db.query(Performance)
        .filter(Performance.employee_id == emp_id)
        .order_by(Performance.review_date.desc())
        .first()
    )


def get_performance_history(db: Session, emp_id: int):
    return (
        db.query(Performance)
        .filter(Performance.employee_id == emp_id)
        .order_by(Performance.review_date)
        .all()
    )


def get_perks_for_employee(db: Session, emp_id: int):
    return db.query(Perk).filter(Perk.employee_id == emp_id).all()


def get_all_perks(db: Session):
    return db.query(Perk).options(joinedload(Perk.employee)).all()


def get_work_history(db: Session, emp_id: int):
    return (
        db.query(WorkHistory)
        .filter(WorkHistory.employee_id == emp_id)
        .order_by(WorkHistory.year)
        .all()
    )


def get_timeline(db: Session, emp_id: int):
    return (
        db.query(EmployeeTimeline)
        .filter(EmployeeTimeline.employee_id == emp_id)
        .order_by(EmployeeTimeline.event_date)
        .all()
    )


def get_complaints_count(db: Session, emp_id: int) -> int:
    return db.query(func.count(Complaint.id)).filter(Complaint.employee_id == emp_id).scalar() or 0


def get_hiring_requirements(db: Session):
    return db.query(HiringRequirement).options(joinedload(HiringRequirement.department)).all()


def get_reportees(db: Session, manager_id: int):
    return db.query(Employee).filter(Employee.reporting_manager_id == manager_id).all()
