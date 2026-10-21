"""
NexHR - AI Assistant Service (Groq)

STRICT SCOPE: this assistant may ONLY analyze and answer questions using
data already inside NexHR's database (employees, salary, performance,
projects, perks, hiring). It is explicitly restricted from:
  - modifying any data
  - hiring / firing anyone
  - uploading / sending any message or file
  - accessing external systems
  - executing arbitrary code
  - answering anything outside the dataset

Architecture (per blueprint):
  User Question -> AI Assistant -> Question Classification ->
  Allowed Analytics Only (strictly) -> Query Data -> Calculate Result ->
  AI Explains Result

We enforce this with a tool/function-calling pattern: Groq can only ever
invoke a small, fixed set of *read-only* analytics functions defined
below. It never receives raw DB/tool access and cannot generate or run
its own code.
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv

from services import salary_service, performance_service, project_service, employee_service

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """You are the NexHR Data Analysis Assistant, embedded in a company's internal
Employee Management System. You may ONLY use the provided tools to answer questions about
this company's employee, salary, performance, project, perks and hiring data.

Strict rules you must always follow:
1. Only answer questions about the HR/company data available through your tools.
2. If a question is outside this scope (general knowledge, unrelated advice, coding help,
   anything not answerable from the tools), politely refuse and say you are limited to
   analyzing this company's HR data.
3. You cannot modify data, hire or fire anyone, send messages/files, access external
   systems, or execute arbitrary code. You are read-only and advisory only.
4. Always call a tool to get real numbers before answering questions that require data.
   Never guess or fabricate figures.
5. Be concise, use rupee (₹) formatting for money, and explain the result in plain language
   after computing it.
"""

# ---------------------------------------------------------------------------
# Fixed, read-only tool definitions exposed to the model.
# The model can ONLY call these -- nothing else is reachable.
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_total_payroll",
            "description": "Get total monthly payroll cost across all active employees.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_daily_workforce_cost",
            "description": "Get the live daily running cost of the company's workforce (salary only).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_perk_cost_breakdown",
            "description": "Get the monthly perks/benefits cost broken down by category (canteen, coffee, transport, insurance, business trips, other), including whether the canteen minimum budget floor was applied.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_performers",
            "description": "Get the top N performing employees by performance score.",
            "parameters": {
                "type": "object",
                "properties": {"n": {"type": "integer", "description": "Number of top performers to return"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_status_summary",
            "description": "Get a count of projects by status (ongoing, completed, review, not started).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_department_cost_summary",
            "description": "Get total and average salary cost per department, plus headcount.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_employee",
            "description": "Search for an employee's details by name or employee ID.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Employee name or ID"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_bonus_pool_summary",
            "description": "Get total bonus payout currently allocated and count of bonus-eligible employees.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def _get_total_payroll(**_):
    return {"total_monthly_payroll": salary_service.calculate_total_payroll()}


def _get_daily_workforce_cost(**_):
    return salary_service.calculate_daily_salary()


def _get_perk_cost_breakdown(**_):
    return salary_service.calculate_perk_cost()


def _get_top_performers(n: int = 5, **_):
    df = performance_service.get_top_performers(n)
    return df.drop(columns=["_id"], errors="ignore").to_dict(orient="records")


def _get_project_status_summary(**_):
    return project_service.get_project_status_counts()


def _get_department_cost_summary(**_):
    df = salary_service.get_department_cost_summary()
    return df.to_dict(orient="records")


def _search_employee(query: str, **_):
    df = employee_service.search_employee(query)
    if df.empty:
        return {"found": False}
    return df.drop(columns=["_id"], errors="ignore").to_dict(orient="records")


def _get_bonus_pool_summary(**_):
    return performance_service.calculate_bonus_pool()


FUNCTION_MAP = {
    "get_total_payroll": _get_total_payroll,
    "get_daily_workforce_cost": _get_daily_workforce_cost,
    "get_perk_cost_breakdown": _get_perk_cost_breakdown,
    "get_top_performers": _get_top_performers,
    "get_project_status_summary": _get_project_status_summary,
    "get_department_cost_summary": _get_department_cost_summary,
    "search_employee": _search_employee,
    "get_bonus_pool_summary": _get_bonus_pool_summary,
}


def is_configured() -> bool:
    return bool(GROQ_API_KEY)


def ask_assistant(user_question: str, chat_history: list[dict] | None = None) -> str:
    """
    Send the question to Groq with the fixed tool set. The model can only
    ever call the read-only functions above; we execute those locally and
    feed results back for a final natural-language explanation.
    """
    if not is_configured():
        return ("⚠️ GROQ_API_KEY is not set. Add it to your `.env` file to enable the "
                "AI assistant. Get a free key at https://console.groq.com/keys")

    client = Groq(api_key=GROQ_API_KEY)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if chat_history:
        messages.extend(chat_history)
    messages.append({"role": "user", "content": user_question})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.2,
            max_tokens=800,
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for call in msg.tool_calls:
                fn_name = call.function.name
                try:
                    args = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}

                if fn_name not in FUNCTION_MAP:
                    result = {"error": "Function not permitted."}
                else:
                    result = FUNCTION_MAP[fn_name](**args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": fn_name,
                    "content": json.dumps(result, default=str),
                })

            follow_up = client.chat.completions.create(
                model=MODEL_NAME, messages=messages, temperature=0.2, max_tokens=800,
            )
            return follow_up.choices[0].message.content

        return msg.content

    except Exception as exc:  # noqa: BLE001
        return f"⚠️ AI assistant error: {exc}"
