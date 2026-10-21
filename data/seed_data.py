"""
NexHR - Demo Data Seeder
Populates the database with realistic fake data using Faker, so the app
is fully explorable out-of-the-box. Run: python -m data.seed_data
Safe to re-run -- it wipes and recreates all tables first.
"""
import os
import random
from datetime import date, timedelta

from faker import Faker
from fpdf import FPDF

from database.connection import engine, session_scope, init_db
from database.models import (
    Base, Department, Employee, Salary, Performance, Project, Perk,
    HiringRequirement, WorkHistory, EmployeeTimeline, Complaint,
    EmployeeType, EmployeeStatus, SalaryStatus, ProjectStatus, Rating,
    PerkType, HiringStatus, EventType,
)

fake = Faker()
Faker.seed(42)
random.seed(42)

RESUME_DIR = os.path.join(os.path.dirname(__file__), "..", "resumes")

DEPARTMENTS = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Support", "Facilities"]

ROLES_BY_DEPT = {
    "Engineering": ["Software Engineer", "Senior Engineer", "DevOps Engineer", "QA Engineer", "Engineering Manager"],
    "Sales": ["Sales Executive", "Account Manager", "Sales Lead"],
    "Marketing": ["Marketing Executive", "Content Strategist", "SEO Specialist"],
    "HR": ["HR Executive", "Talent Acquisition Specialist", "HR Manager"],
    "Finance": ["Financial Analyst", "Accountant", "Finance Manager"],
    "Operations": ["Operations Executive", "Operations Manager"],
    "Support": ["Support Executive", "Support Lead"],
    "Facilities": ["Canteen Staff", "Housekeeping", "Security"],
}

SKILLS_BY_DEPT = {
    "Engineering": ["Python", "SQL", "AWS", "React", "Docker", "Java"],
    "Sales": ["B2B Sales", "CRM", "Negotiation", "Communication"],
    "Marketing": ["SEO", "Content Strategy", "Analytics", "Social Media"],
    "HR": ["Recruitment", "Employee Relations", "Payroll", "Onboarding"],
    "Finance": ["Accounting", "Financial Analysis", "Excel", "Taxation"],
    "Operations": ["Supply Chain", "Logistics", "Process Optimization"],
    "Support": ["Customer Service", "Troubleshooting", "Zendesk"],
    "Facilities": ["Maintenance", "Safety Protocols", "Cleaning", "Time Management"]
}

RATING_BY_SCORE = lambda s: (
    Rating.EXCELLENT if s >= 85 else
    Rating.VERY_GOOD if s >= 70 else
    Rating.AVERAGE if s >= 55 else
    Rating.BAD
)


def generate_resume_pdf(emp_code: str, name: str, role: str, experience: float) -> str:
    """Creates a tiny placeholder resume PDF for the demo and returns its relative path."""
    os.makedirs(RESUME_DIR, exist_ok=True)
    filename = f"{emp_code}.pdf"
    filepath = os.path.join(RESUME_DIR, filename)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, name, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 8, f"Role: {role}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Experience: {experience} years", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Employee ID: {emp_code}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.multi_cell(0, 7, fake.paragraph(nb_sentences=6))
    pdf.output(filepath)
    return os.path.join("resumes", filename)


def seed():
    print("Dropping & recreating all tables...")
    Base.metadata.drop_all(bind=engine)
    init_db()

    with session_scope() as db:
        # --- Departments ---
        dept_objs = {}
        for name in DEPARTMENTS:
            d = Department(name=name)
            db.add(d)
            dept_objs[name] = d
        db.flush()

        # --- Projects ---
        project_names = ["Client Portal Revamp", "Internal CRM", "Mobile App Launch",
                          "Payroll Automation", "Cloud Migration", "Marketing Campaign Q3",
                          "Customer Support Bot", "Warehouse Management System"]
        projects = []
        for pname in project_names:
            status = random.choice(list(ProjectStatus))
            completion = 100.0 if status == ProjectStatus.COMPLETED else round(random.uniform(10, 95), 1)
            start = fake.date_between(start_date="-2y", end_date="-30d")
            proj = Project(
                name=pname, status=status, completion_percentage=completion,
                start_date=start, due_date=start + timedelta(days=random.randint(60, 400)),
            )
            db.add(proj)
            projects.append(proj)
        db.flush()

        # --- Employees ---
        employees = []
        num_employees = 65
        for i in range(num_employees):
            dept_name = random.choice(DEPARTMENTS)
            dept = dept_objs[dept_name]
            role = random.choice(ROLES_BY_DEPT[dept_name])
            emp_type = (EmployeeType.CANTEEN_STAFF if role in ("Canteen Staff", "Housekeeping", "Security")
                        else random.choices(
                            [EmployeeType.FULL_TIME, EmployeeType.PART_TIME, EmployeeType.CONTRACT, EmployeeType.INTERN],
                            weights=[70, 10, 12, 8])[0])
            experience = round(random.uniform(0.5, 15), 1)
            joining_date = fake.date_between(start_date="-6y", end_date="-15d")
            name = fake.name()
            emp_code = f"NEX-{1001 + i}"

            if emp_type == EmployeeType.CANTEEN_STAFF:
                base_salary = round(random.uniform(15000, 28000), -2)
            elif role in ("Engineering Manager", "HR Manager", "Finance Manager", "Operations Manager"):
                base_salary = round(random.uniform(120000, 220000), -2)
            elif emp_type == EmployeeType.INTERN:
                base_salary = round(random.uniform(15000, 30000), -2)
            else:
                base_salary = round(random.uniform(35000, 110000), -2)

            status = random.choices([EmployeeStatus.ACTIVE, EmployeeStatus.INACTIVE, EmployeeStatus.ON_LEAVE],
                                     weights=[88, 5, 7])[0]
            assigned_project = random.choice(projects) if random.random() > 0.15 else None

            resume_link = generate_resume_pdf(emp_code, name, role, experience)

            emp = Employee(
                emp_code=emp_code, name=name, email=fake.unique.email(),
                department_id=dept.id, role=role, emp_type=emp_type,
                experience_years=experience, joining_date=joining_date,
                base_salary=base_salary, project_id=assigned_project.id if assigned_project else None,
                resume_link=resume_link, status=status,
            )
            db.add(emp)
            employees.append(emp)
        db.flush()

        # assign a manager per department (first employee in that dept)
        for dept_name, dept in dept_objs.items():
            dept_emps = [e for e in employees if e.department_id == dept.id]
            if dept_emps:
                manager = dept_emps[0]
                dept.manager_id = manager.id
                for e in dept_emps[1:]:
                    e.reporting_manager_id = manager.id
        db.flush()

        # assign project managers
        for proj in projects:
            candidates = [e for e in employees if e.project_id == proj.id]
            if candidates:
                proj.manager_id = random.choice(candidates).id
        db.flush()

        # --- Salaries ---
        for e in employees:
            increment = round(random.choice([0, 0, 5, 8, 10, 12, 15]), 1)
            bonus = round(random.choice([0, 0, 2000, 5000, 10000, 15000]), 2)
            salary_status = random.choices([SalaryStatus.PAID, SalaryStatus.DUE], weights=[80, 20])[0]
            sal = Salary(
                employee_id=e.id, base_salary=e.base_salary, increment_percent=increment,
                bonus_amount=bonus, salary_status=salary_status,
                last_paid_date=fake.date_between(start_date="-30d", end_date="today") if salary_status == SalaryStatus.PAID else None,
            )
            db.add(sal)

        # --- Perks (a few categories per employee, canteen staff excluded from getting canteen perk themselves) ---
        for e in employees:
            n_perks = random.randint(1, 3)
            chosen = random.sample(list(PerkType), n_perks)
            for pt in chosen:
                if pt == PerkType.CANTEEN:
                    cost = round(random.uniform(1500, 3500), 2)
                elif pt == PerkType.COFFEE_BEVERAGES:
                    cost = round(random.uniform(300, 900), 2)
                elif pt == PerkType.TRANSPORT:
                    cost = round(random.uniform(2000, 6000), 2)
                elif pt == PerkType.INSURANCE:
                    cost = round(random.uniform(1000, 4000), 2)
                elif pt == PerkType.BUSINESS_TRIP:
                    cost = round(random.uniform(0, 8000), 2)
                else:
                    cost = round(random.uniform(200, 1500), 2)
                db.add(Perk(employee_id=e.id, perk_type=pt, monthly_cost=cost))

        # --- Performance reviews (1-3 historical reviews per employee) ---
        for e in employees:
            n_reviews = random.randint(1, 3)
            review_date = e.joining_date + timedelta(days=90)
            for _ in range(n_reviews):
                score = round(random.uniform(35, 98), 1)
                rating = RATING_BY_SCORE(score)
                bonus_eligible = rating in (Rating.EXCELLENT, Rating.VERY_GOOD)
                db.add(Performance(
                    employee_id=e.id, review_date=min(review_date, date.today()),
                    performance_score=score, rating=rating, bonus_eligible=bonus_eligible,
                ))
                review_date += timedelta(days=180)

        # --- Work history (prior companies, ~60% of employees) ---
        for e in employees:
            if random.random() < 0.6:
                for _ in range(random.randint(1, 2)):
                    db.add(WorkHistory(
                        employee_id=e.id, company_name=fake.company(),
                        role=random.choice(["Associate", "Analyst", "Executive", "Engineer", "Consultant"]),
                        duration_years=round(random.uniform(0.5, 4), 1),
                        year=random.randint(2015, e.joining_date.year - 1) if e.joining_date.year > 2016 else 2016,
                    ))

        # --- Employee timeline ---
        for e in employees:
            db.add(EmployeeTimeline(employee_id=e.id, event_date=e.joining_date, event_type=EventType.JOINED,
                                     description=f"Joined as {e.role}"))
            if e.project_id:
                db.add(EmployeeTimeline(
                    employee_id=e.id, event_date=e.joining_date + timedelta(days=30),
                    event_type=EventType.PROJECT_ASSIGNED, description="Assigned to a project"))
            db.add(EmployeeTimeline(
                employee_id=e.id, event_date=e.joining_date + timedelta(days=90),
                event_type=EventType.PERFORMANCE_REVIEW, description="First performance review"))
            if random.random() < 0.4:
                db.add(EmployeeTimeline(
                    employee_id=e.id, event_date=e.joining_date + timedelta(days=365),
                    event_type=EventType.SALARY_INCREMENT, description="Annual increment"))
            if random.random() < 0.15:
                db.add(EmployeeTimeline(
                    employee_id=e.id, event_date=e.joining_date + timedelta(days=500),
                    event_type=EventType.PROMOTED, description="Promoted to a senior role"))

        # --- Complaints (sparse, for workforce risk analysis) ---
        for e in employees:
            if random.random() < 0.12:
                for _ in range(random.randint(1, 3)):
                    db.add(Complaint(
                        employee_id=e.id,
                        complaint_date=fake.date_between(start_date="-1y", end_date="today"),
                        description=random.choice([
                            "Missed project deadline", "Attendance concern",
                            "Client feedback issue", "Behavioral concern raised by peer",
                        ]),
                    ))

        # --- Hiring requirements ---
        for _ in range(6):
            dept_name = random.choice(DEPARTMENTS)
            dept = dept_objs[dept_name]
            role = random.choice(ROLES_BY_DEPT[dept_name])
            
            # Department ke hisaab se skills pick karega
            available_skills = SKILLS_BY_DEPT.get(dept_name, ["Communication", "Teamwork"])
            num_skills = min(random.randint(2, 3), len(available_skills))
            selected_skills = ", ".join(random.sample(available_skills, k=num_skills))

            db.add(HiringRequirement(
                department_id=dept.id, role=role,
                required_skills=selected_skills,
                experience_required=round(random.uniform(1, 6), 1),
                budget=round(random.uniform(40000, 120000), -2),
                number_required=random.randint(1, 4),
                status=random.choice(list(HiringStatus)),
            ))

    print(f"Seed complete: {num_employees} employees across {len(DEPARTMENTS)} departments, "
          f"{len(project_names)} projects.")


if __name__ == "__main__":
    seed()
