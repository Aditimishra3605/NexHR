<<<<<<< HEAD
# NexHR — An Integrated Employee Management, Performance & Payroll Analytics Platform

A B.Tech CSE (DSDA) 7th-semester major project. NexHR is a Streamlit-based
platform for managing employee data, tracking payroll/perks in real time,
evaluating performance, planning workforce hiring/firing, and querying
company data through a strictly scoped AI assistant.

## Problem Statement

Organizations often manage employee information, salary records,
performance matrix, project assignments and workforce planning through
disconnected spreadsheets and systems. This makes it difficult to obtain
a unified view of workforce performance, employee costs, project status
and staffing requirements. NexHR addresses this by providing an
integrated, data-driven platform for employee management, workforce
analytics, compensation monitoring, performance evaluation and staffing
decision support.

## Features

| Tab | What it does |
|---|---|
| **Dashboard** | KPI cards (headcount, payroll, salary due, daily cost), top performers, project overview, department/role/experience charts |
| **Employee Details** | Excel-style table with a valid search (by name OR employee ID, partial matching), click-through profile with salary, project, tenure, downloadable resume, work history and a visual timeline |
| **Salary & Perks** | Live/auto-refreshing payroll data (always queries the DB fresh — no stale cache), per-day workforce cost, sortable/filterable per-employee salary table with paid/due status, Perks module with an enforced ₹2.5 lakh minimum canteen budget, canteen staff included as regular employees |
| **Performance & Rewards** | Hierarchy-based team view, project status per employee, and an increment calculator that previews total additional cost to the company before you commit to a raise |
| **Projects** | Full project status board (ongoing/completed/review/not started) with team drill-down |
| **Workforce Planning** | Rule-based hiring recommendation engine (skill gap + estimated CTC based on department/role averages) and a workforce risk/retention analysis flagging employees for HR review — all decisions remain with human HR staff |
| **AI Assistant** | Groq-powered chat, strictly limited via function-calling to read-only analytics over this dataset. Cannot modify data, hire/fire, send messages, or access anything outside the app |

## Tech Stack

- **Frontend:** Streamlit + streamlit-option-menu (custom dark theme)
- **Backend:** Python, SQLAlchemy ORM
- **Database:** SQLite by default (zero setup) — swap to PostgreSQL by changing one line in `.env`
- **Visualization:** Plotly
- **AI:** Groq API (free tier) with strict function-calling scope
- **Demo data:** Faker + fpdf2 (auto-generates realistic employees and placeholder resume PDFs)

## Project Structure

```
NexHR/
├── app.py                     # Main entry point — run this with `streamlit run app.py`
├── pages/
│   ├── dashboard.py
│   ├── employees.py
│   ├── workforce_cost.py      # Salary & Perks tab
│   ├── performance.py
│   ├── projects.py
│   ├── workforce_planning.py  # Hire & Fire tab
│   └── ai_assistant.py
├── database/
│   ├── connection.py
│   ├── models.py
│   └── queries.py
├── services/
│   ├── employee_service.py
│   ├── salary_service.py
│   ├── performance_service.py
│   ├── project_service.py
│   ├── workforce_service.py
│   └── ai_service.py
├── analytics/
│   ├── salary_analysis.py
│   ├── performance_analysis.py
│   └── workforce_analysis.py
├── data/
│   └── seed_data.py           # Generates realistic demo data
├── resumes/                   # Auto-generated placeholder resume PDFs
├── assets/
├── tests/
│   └── test_services.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup & Running

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
```
Open `.env` and:
- Leave `DATABASE_URL` as-is to use SQLite (recommended for your viva/demo), or point it at a PostgreSQL instance.
- Add your free Groq API key (get one at https://console.groq.com/keys) to enable the AI Assistant tab.

### 3. Seed demo data
```bash
python -m data.seed_data
```
This creates `nexhr.db` with 65 realistic employees across 8 departments,
8 projects, salaries, perks, performance history, work history, timeline
events, and placeholder resume PDFs in `/resumes`.

### 4. Run the app
```bash
streamlit run app.py
```

### 5. (Optional) Run tests
```bash
python -m pytest tests/ -v
```

## Deploying to Streamlit Community Cloud

1. Push this repo to GitHub (make sure `.env` is **not** committed — only `.env.example`).
2. On [share.streamlit.io](https://share.streamlit.io), create a new app pointing to `app.py`.
3. In the app's "Secrets" settings, add:
   ```toml
   GROQ_API_KEY = "your_key_here"
   ```
4. Since Streamlit Cloud's filesystem is ephemeral, either:
   - Run `python -m data.seed_data` once via a one-off script/button on first load, or
   - Switch `DATABASE_URL` to a hosted PostgreSQL instance (e.g. Supabase, Neon, Railway) so data persists across restarts.

## Design Notes / Betterment Ideas

A few deliberate decisions worth mentioning in your project report / viva:

- **"Live" refresh in Streamlit**: Streamlit isn't a persistent always-on server in the traditional sense — each interaction reruns the script. NexHR's "live" salary data comes from **always querying the database fresh** on every rerun (no cached DataFrame), plus an optional auto-refresh toggle (`streamlit-autorefresh`) that reruns the script every 10 seconds — so if the DB is updated externally, the dashboard reflects it automatically.
- **Canteen budget floor**: `calculate_perk_cost()` enforces the ₹2.5L minimum regardless of actual logged spend, exactly as specified — with a visible note in the UI explaining why.
- **AI Assistant scope enforcement**: rather than trusting the model's own restraint, the assistant can *only* call a fixed set of 8 read-only Python functions (defined in `ai_service.py`). It has no raw database access, cannot execute code, and any question outside HR data scope gets a polite refusal per the system prompt.
- **Hire/Fire decisions stay human**: the Workforce Planning tab produces analytical indicators (skill gap, estimated CTC, risk flags) but any hire/fire action is only *logged* for HR review — nothing is automated.
- **Role-based login** (Admin/HR/Manager views), **audit logging**, and **PDF/Excel export of reports** are natural next additions if you want to extend this further before submission — see the chat for suggested code hooks.

---
Built as a major project for B.Tech CSE (DSDA), 7th Semester.
=======
# NexHR
Workforce Intelligence Platform
>>>>>>> 088a908030d000cd5db8fa12280b00faea6486c8
