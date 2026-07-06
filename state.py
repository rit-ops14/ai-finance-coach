# state.py

# TypedDict lets us define what fields our shared dictionary will have
# It's like designing a form before filling it in
from typing import TypedDict, Optional


class FinanceState(TypedDict, total=False):
    # total=False means all fields are optional
    # (not every field needs to be filled at the start)

    # ── SECTION 1: User Inputs ──
    # These get filled when the user submits the form
    name: str                    # "Rahul Sharma"
    age: int                     # 25
    monthly_income: float        # 50000.0
    monthly_expenses: dict       # {"rent": 12000, "food": 7000, ...}
    total_expenses: float        # 34000.0 (calculated by Node 1)
    savings_goal: str            # "Save for Europe trip"
    goal_amount: float           # 150000.0
    goal_timeline_months: int    # 12
    risk_appetite: str           # "medium"
    existing_savings: float      # 20000.0

    # ── SECTION 2: Node Outputs ──
    # These get filled ONE BY ONE as each node runs
    # Node 1 fills profile_analysis
    # Node 2 fills budget_plan
    # Node 3 fills savings_plan
    # Node 4 fills final_report
    profile_analysis: str
    budget_plan: str
    savings_plan: str
    final_report: str

    # ── SECTION 3: Error Handling ──
    error: Optional[str]         # None if everything works, error message if not