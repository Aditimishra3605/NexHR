"""
NexHR - SQLAlchemy ORM Models
Covers: Employees, Departments, Salaries, Perks, Performance, Projects,
Hiring Requirements, Work History, Employee Timeline, Complaints.
"""
from datetime import date, datetime
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Text, Enum
)
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class EmployeeType(str, enum.Enum):
    FULL_TIME = "Full-Time"
    PART_TIME = "Part-Time"
    CONTRACT = "Contract"
    INTERN = "Intern"
    CANTEEN_STAFF = "Canteen Staff"


class EmployeeStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ON_LEAVE = "On Leave"


class SalaryStatus(str, enum.Enum):
    PAID = "Paid"
    DUE = "Due"


class ProjectStatus(str, enum.Enum):
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    REVIEW = "Review"
    NOT_STARTED = "Not Started"


class Rating(str, enum.Enum):
    EXCELLENT = "Excellent"
    VERY_GOOD = "Very Good"
    AVERAGE = "Average"
    BAD = "Bad"


class PerkType(str, enum.Enum):
    CANTEEN = "Canteen"
    COFFEE_BEVERAGES = "Coffee & Beverages"
    TRANSPORT = "Transport"
    INSURANCE = "Insurance"
    BUSINESS_TRIP = "Business Trip"
    OTHER = "Other"


class HiringStatus(str, enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    CLOSED = "Closed"


class EventType(str, enum.Enum):
    JOINED = "Joined Company"
    PROJECT_ASSIGNED = "Project Assigned"
    PERFORMANCE_REVIEW = "Performance Review"
    SALARY_INCREMENT = "Salary Increment"
    PROMOTED = "Promoted"
    BONUS_AWARDED = "Bonus Awarded"
    EXIT = "Exit"


# ---------------------------------------------------------------------------
# Core Tables
# ---------------------------------------------------------------------------
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

    manager = relationship("Employee", foreign_keys=[manager_id], post_update=True)
    employees = relationship(
        "Employee", back_populates="department", foreign_keys="Employee.department_id"
    )


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    emp_code = Column(String(20), unique=True, nullable=False)  # e.g. NEX-1001
    name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", use_alter=True, name="fk_emp_dept"))
    role = Column(String(100), nullable=False)
    emp_type = Column(Enum(EmployeeType), nullable=False, default=EmployeeType.FULL_TIME)
    experience_years = Column(Float, default=0.0)
    joining_date = Column(Date, nullable=False)
    base_salary = Column(Float, nullable=False, default=0.0)
    project_id = Column(Integer, ForeignKey("projects.id", use_alter=True, name="fk_emp_project"), nullable=True)
    reporting_manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    resume_link = Column(String(255), nullable=True)
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.ACTIVE)

    department = relationship(
        "Department", back_populates="employees", foreign_keys=[department_id]
    )
    current_project = relationship("Project", foreign_keys=[project_id])
    manager = relationship("Employee", remote_side=[id], foreign_keys=[reporting_manager_id])

    salary_record = relationship(
        "Salary", back_populates="employee", uselist=False, cascade="all, delete-orphan"
    )
    performance_reviews = relationship(
        "Performance", back_populates="employee", cascade="all, delete-orphan"
    )
    perks = relationship("Perk", back_populates="employee", cascade="all, delete-orphan")
    work_history = relationship(
        "WorkHistory", back_populates="employee", cascade="all, delete-orphan"
    )
    timeline_events = relationship(
        "EmployeeTimeline",
        back_populates="employee",
        cascade="all, delete-orphan",
        order_by="EmployeeTimeline.event_date",
    )
    complaints = relationship("Complaint", back_populates="employee", cascade="all, delete-orphan")

    @property
    def tenure_days(self) -> int:
        return (date.today() - self.joining_date).days

    @property
    def tenure_display(self) -> str:
        days = self.tenure_days
        years, rem_days = divmod(days, 365)
        months = rem_days // 30
        parts = []
        if years:
            parts.append(f"{years}y")
        if months:
            parts.append(f"{months}m")
        if not parts:
            parts.append(f"{days}d")
        return " ".join(parts)


class Salary(Base):
    __tablename__ = "salaries"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), unique=True, nullable=False)
    base_salary = Column(Float, nullable=False, default=0.0)
    increment_percent = Column(Float, default=0.0)  # cumulative increment %
    bonus_amount = Column(Float, default=0.0)  # current cycle bonus
    salary_status = Column(Enum(SalaryStatus), default=SalaryStatus.DUE)
    last_paid_date = Column(Date, nullable=True)

    employee = relationship("Employee", back_populates="salary_record")

    @property
    def effective_salary(self) -> float:
        return round(self.base_salary * (1 + self.increment_percent / 100), 2)

    @property
    def total_payout(self) -> float:
        return round(self.effective_salary + self.bonus_amount, 2)


class Performance(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    review_date = Column(Date, nullable=False, default=date.today)
    performance_score = Column(Float, nullable=False)  # 0-100 %
    rating = Column(Enum(Rating), nullable=False)
    bonus_eligible = Column(Boolean, default=False)

    employee = relationship("Employee", back_populates="performance_reviews")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ONGOING)
    start_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    completion_percentage = Column(Float, default=0.0)

    manager = relationship("Employee", foreign_keys=[manager_id])


class Perk(Base):
    __tablename__ = "perks"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    perk_type = Column(Enum(PerkType), nullable=False)
    monthly_cost = Column(Float, nullable=False, default=0.0)

    employee = relationship("Employee", back_populates="perks")


class HiringRequirement(Base):
    __tablename__ = "hiring_requirements"

    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    role = Column(String(100), nullable=False)
    required_skills = Column(String(255), nullable=False)  # comma separated
    experience_required = Column(Float, default=0.0)
    budget = Column(Float, nullable=False)
    number_required = Column(Integer, nullable=False, default=1)
    status = Column(Enum(HiringStatus), default=HiringStatus.OPEN)
    created_date = Column(Date, default=date.today)

    department = relationship("Department")


class WorkHistory(Base):
    """Prior work experience shown in an employee's profile."""
    __tablename__ = "work_history"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    company_name = Column(String(150), nullable=False)
    role = Column(String(100), nullable=False)
    duration_years = Column(Float, nullable=False)
    year = Column(Integer, nullable=False)

    employee = relationship("Employee", back_populates="work_history")


class EmployeeTimeline(Base):
    """Timeline events shown on an employee's profile (joined, promoted, etc.)."""
    __tablename__ = "employee_timeline"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    event_date = Column(Date, nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    description = Column(String(255), nullable=True)

    employee = relationship("Employee", back_populates="timeline_events")


class Complaint(Base):
    """Used by workforce risk / retention analysis."""
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    complaint_date = Column(Date, nullable=False, default=date.today)
    description = Column(Text, nullable=True)

    employee = relationship("Employee", back_populates="complaints")


class FiringLog(Base):
    """Audit log for hire/fire decisions taken through the Workforce Planning tab."""
    __tablename__ = "hiring_firing_log"

    id = Column(Integer, primary_key=True)
    action_type = Column(String(10), nullable=False)  # 'hire' or 'fire'
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    role = Column(String(100), nullable=True)
    reason = Column(String(255), nullable=True)
    action_date = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee")
