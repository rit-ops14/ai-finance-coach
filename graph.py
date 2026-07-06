# graph.py

# StateGraph is the main LangGraph class for building pipelines
# START and END are special markers — like the green and red circles
# in a flowchart
from langgraph.graph import StateGraph, START, END

# Import our FinanceState (the shared memory blueprint)
from state import FinanceState

# Import all 4 node functions
from nodes import (
    analyze_profile,
    budget_breakdown,
    savings_strategy,
    generate_report
)


def build_graph():
    """
    Constructs the LangGraph pipeline.
    
    Visual representation of what we're building:
    
    START
      ↓
    [analyze_profile]   ← Node 1
      ↓
    [budget_breakdown]  ← Node 2
      ↓
    [savings_strategy]  ← Node 3
      ↓
    [generate_report]   ← Node 4
      ↓
    END
    """
    
    # Create a StateGraph that uses FinanceState as its shared memory
    # Every node will receive this state and can read/write to it
    builder = StateGraph(FinanceState)
    
    # ── ADD NODES ──
    # add_node(name, function)
    # name   = what we call this step (any string we choose)
    # function = the Python function that runs when this node is reached
    builder.add_node("analyze_profile",  analyze_profile)
    builder.add_node("budget_breakdown", budget_breakdown)
    builder.add_node("savings_strategy", savings_strategy)
    builder.add_node("generate_report",  generate_report)
    
    # ── ADD EDGES ──
    # add_edge(from, to)
    # This draws an arrow FROM one node TO the next
    # This determines the ORDER of execution
    builder.add_edge(START,                "analyze_profile")
    # START → analyze_profile (first node to run)
    
    builder.add_edge("analyze_profile",    "budget_breakdown")
    # After analyze_profile finishes → run budget_breakdown
    
    builder.add_edge("budget_breakdown",   "savings_strategy")
    # After budget_breakdown finishes → run savings_strategy
    
    builder.add_edge("savings_strategy",   "generate_report")
    # After savings_strategy finishes → run generate_report
    
    builder.add_edge("generate_report",    END)
    # After generate_report finishes → pipeline is done
    
    # compile() validates the graph structure and makes it executable
    # After this, the graph is "locked" and ready to run
    graph = builder.compile()
    
    return graph


def run_finance_coach(user_data: dict) -> dict:
    """
    The main function called by app.py (the UI).
    
    Takes:  user_data dict (from the web form)
    Returns: complete state dict (with all 4 node outputs)
    
    graph.invoke() runs the ENTIRE pipeline from START to END
    and returns the final state after all nodes have completed.
    """
    
    graph = build_graph()
    
    # graph.invoke() is like pressing "Run" on the entire pipeline
    # It takes the initial state (user's data) and passes it through
    # all 4 nodes, collecting outputs along the way
    final_state = graph.invoke(user_data)
    
    return final_state


# ── TEST WITHOUT THE UI ──
# When you run "python graph.py", this block executes
# It lets you test the full pipeline in the terminal
if __name__ == "__main__":
    
    # This is sample test data simulating what the UI form sends
    test_data = {
        "name":                 "Priya Sharma",
        "age":                  26,
        "monthly_income":       55000,
        "monthly_expenses": {
            "rent":             15000,
            "food":             8000,
            "transport":        3000,
            "utilities":        2000,
            "entertainment":    4000,
            "shopping":         5000,
            "subscriptions":    1500,
            "other":            2000
        },
        "savings_goal":         "Emergency fund + Europe trip",
        "goal_amount":          150000,
        "goal_timeline_months": 12,
        "risk_appetite":        "medium",
        "existing_savings":     20000
    }
    
    print("🚀 Starting LangGraph Finance Coach Pipeline...\n")
    result = run_finance_coach(test_data)
    
    # Print each node's output to verify they all ran
    print("\n" + "="*60)
    print("✅ NODE 1 OUTPUT (Profile Analysis):")
    print(result.get("profile_analysis", "Missing"))
    
    print("\n" + "="*60)
    print("✅ NODE 2 OUTPUT (Budget Plan):")
    print(result.get("budget_plan", "Missing"))
    
    print("\n" + "="*60)
    print("✅ NODE 3 OUTPUT (Savings Strategy):")
    print(result.get("savings_plan", "Missing"))
    
    print("\n" + "="*60)
    print("✅ NODE 4 OUTPUT (Final Report):")
    print(result.get("final_report", "Missing"))