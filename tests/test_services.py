"""
NexHR - Basic Service Layer Tests
Run with: python -m pytest tests/ -v
(Run `python -m data.seed_data` first so there is data to test against.)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services import employee_service, salary_service, performance_service, project_service, workforce_service


def test_search_employee_by_id_returns_exact_match():
    df = employee_service.search_employee("NEX-1001")
    assert not df.empty
    assert df.iloc[0]["Emp ID"] == "NEX-1001"


def test_search_employee_by_partial_name():
    df = employee_service.search_employee("a")
    assert not df.empty  # at least one name should contain 'a'


def test_search_employee_no_match_returns_empty():
    df = employee_service.search_employee("zzzznomatchzzzz")
    assert df.empty


def test_get_employee_details_has_required_fields():
    details = employee_service.get_employee_details(1)
    required_keys = {"name", "emp_code", "department", "role", "effective_salary",
                      "current_project", "tenure_display", "resume_link", "work_history", "timeline"}
    assert required_keys.issubset(details.keys())


def test_daily_salary_cost_is_positive():
    result = salary_service.calculate_daily_salary()
    assert result["daily_cost"] > 0
    assert result["annual_payroll"] == result["monthly_payroll"] * 12


def test_canteen_budget_floor_enforced():
    result = salary_service.calculate_perk_cost()
    assert result["breakdown"]["Canteen"] >= salary_service.MINIMUM_MONTHLY_CANTEEN_BUDGET


def test_top_performers_sorted_descending():
    df = performance_service.get_top_performers(5)
    scores = df["Performance Score"].tolist()
    assert scores == sorted(scores, reverse=True)


def test_increment_cost_calculation():
    result = salary_service.calculate_increment_cost([1, 2], 10)
    assert result["new_total_monthly"] > result["current_total_monthly"]
    assert result["additional_annual_cost"] == round(result["additional_monthly_cost"] * 12, 2)


def test_project_status_counts_not_empty():
    counts = project_service.get_project_status_counts()
    assert sum(counts.values()) > 0


def test_hiring_recommendation_returns_estimate():
    rec = workforce_service.generate_hiring_recommendation(
        "Engineering", "Software Engineer", ["Python", "SQL"], 3, 2
    )
    assert rec["estimated_ctc_monthly_per_hire"] >= 0
    assert rec["number_required"] == 2


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
