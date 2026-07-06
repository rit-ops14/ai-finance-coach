# nodes.py

import os
from groq import Groq
from dotenv import load_dotenv

# load_dotenv() reads your .env file and loads GROQ_API_KEY
# into the environment so os.getenv() can find it
load_dotenv()


def get_client():
    """
    Creates and returns a Groq client.
    Think of this like picking up a phone before making a call.
    The client is the "phone" — we use it to talk to Groq's AI.
    """
    api_key = os.getenv("GROQ_API_KEY")
    # os.getenv reads the key from .env file
    
    if not api_key:
        raise ValueError("GROQ_API_KEY not found! Check your .env file")
    
    return Groq(api_key=api_key)


def call_llm(prompt: str, max_tokens: int = 800) -> str:
    """
    This is the actual call to the AI.
    
    prompt     = the instruction/question we send to the AI
    max_tokens = maximum length of the AI's response
                 (tokens are pieces of words — roughly 1 token = 0.75 words)
    
    This is a helper function — instead of repeating the API call 
    code in all 4 nodes, we write it once here and call it from each node.
    """
    client = get_client()
    
    # client.chat.completions.create sends our prompt to Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        # This is the specific AI model we're using
        # llama-3.3-70b = Meta's LLaMA model with 70 billion parameters
        # "versatile" = good at both analysis and creative writing
        
        messages=[{
            "role": "user",       # "user" means this message is from us
            "content": prompt     # our actual instruction to the AI
        }],
        
        max_tokens=max_tokens,    # cap the response length
        temperature=0.4           # balanced — not too rigid, not too creative
    )
    
    # response.choices[0].message.content extracts just the text
    # response is an object → choices is a list → [0] is first choice
    # → message is the AI's reply → content is the actual text
    return response.choices[0].message.content


# ════════════════════════════════════════
# NODE 1 — Analyze Financial Profile
# ════════════════════════════════════════
def analyze_profile(state: dict) -> dict:
    """
    First node in the pipeline.
    
    What it does:
    - Reads income, expenses, goals from state
    - Calculates key financial metrics (surplus, savings rate)
    - Asks AI to assess the person's financial health
    - Returns the analysis to be stored in state
    
    Input:  state dict with user's raw numbers
    Output: {"profile_analysis": "...", "total_expenses": 34000}
    """
    
    print("🔍 Node 1 running: Analyzing financial profile...")
    
    # Calculate derived values from raw inputs
    # sum() adds up all the values in the expenses dictionary
    total_expenses   = sum(state["monthly_expenses"].values())
    
    # Surplus = money left after all expenses
    monthly_surplus  = state["monthly_income"] - total_expenses
    
    # Savings rate = what percentage of income is left for saving
    # Good benchmark: anything above 20% is healthy
    savings_rate     = (monthly_surplus / state["monthly_income"]) * 100

    # Format the expense dictionary into readable text for the prompt
    # This turns {"rent": 12000, "food": 7000} into:
    # "  - Rent: ₹12,000"
    # "  - Food: ₹7,000"
    expense_breakdown = "\n".join([
        f"  - {category.title()}: ₹{amount:,.0f}"
        # .title() capitalizes first letter: "rent" → "Rent"
        # :,.0f formats number with commas: 12000 → "12,000"
        for category, amount in state["monthly_expenses"].items()
    ])

    # Build the prompt — this is Prompt Engineering
    # We give the AI:
    # 1. A ROLE: "You are an expert finance coach"
    # 2. ALL THE DATA: actual numbers from state
    # 3. EXACT FORMAT: what sections to write
    # This structure ensures consistent, useful output
    prompt = f"""
    You are an expert personal finance coach. 
    Analyze this person's financial profile honestly and helpfully.
    
    PERSON DETAILS:
    Name: {state['name']}, Age: {state['age']}
    Monthly Income: ₹{state['monthly_income']:,.0f}
    
    EXPENSE BREAKDOWN:
    {expense_breakdown}
    Total Expenses: ₹{total_expenses:,.0f}
    
    KEY METRICS:
    Monthly Surplus: ₹{monthly_surplus:,.0f}
    Savings Rate: {savings_rate:.1f}%
    Existing Savings: ₹{state['existing_savings']:,.0f}
    
    GOAL: {state['savings_goal']}
    Target: ₹{state['goal_amount']:,.0f} in {state['goal_timeline_months']} months
    Risk Appetite: {state['risk_appetite']}
    
    Write your analysis with these exact sections:
    
    ## 💰 Financial Health Score
    Score this person out of 10 based on their savings rate, 
    surplus, and spending patterns. Explain the score briefly.
    
    ## 📊 Current Situation Summary
    In 3-4 sentences, describe what their numbers tell you.
    Use the actual rupee figures.
    
    ## 🚨 Areas of Concern
    What needs immediate attention? Be specific.
    If nothing major, say "No critical red flags identified."
    
    ## 🌟 What They Are Doing Well
    Acknowledge any positive financial habits shown in the data.
    
    Keep each section to 3-4 sentences maximum.
    Be encouraging but honest. Use simple language.
    """
    
    analysis = call_llm(prompt, max_tokens=700)
    
    # Return a dictionary — LangGraph automatically merges this
    # into the shared state before passing to the next node
    return {
        "profile_analysis": analysis,
        "total_expenses": total_expenses
        # We also save total_expenses so Node 2 and 3 can use it
        # without recalculating
    }


# ════════════════════════════════════════
# NODE 2 — Create Budget Plan
# ════════════════════════════════════════
def budget_breakdown(state: dict) -> dict:
    """
    Second node. Runs AFTER analyze_profile.
    
    What it does:
    - Reads the profile analysis from Node 1
    - Creates a realistic, personalized budget
    - Uses the 50/30/20 rule as a framework
    - Returns budget recommendations
    
    The 50/30/20 rule:
    - 50% of income → Needs (rent, food, bills)
    - 30% of income → Wants (entertainment, shopping)
    - 20% of income → Savings
    """
    
    print("📊 Node 2 running: Creating budget plan...")
    
    income    = state["monthly_income"]
    expenses  = state["monthly_expenses"]
    total_exp = state["total_expenses"]
    # Note: total_expenses was calculated and saved by Node 1
    # This is the power of shared state — we don't recalculate
    
    surplus = income - total_exp
    
    # Calculate ideal 50/30/20 amounts for this person's income
    needs_target   = income * 0.50   # 50% of income
    wants_target   = income * 0.30   # 30% of income
    savings_target = income * 0.20   # 20% of income
    
    # Format expenses with percentage of income for context
    expense_breakdown = "\n".join([
        f"  - {cat.title()}: ₹{amt:,.0f} "
        f"({(amt/income*100):.1f}% of income)"
        for cat, amt in expenses.items()
    ])
    
    prompt = f"""
    You are a personal finance coach creating a detailed budget plan.
    
    FINANCIAL SNAPSHOT:
    Monthly Income: ₹{income:,.0f}
    Total Current Spending: ₹{total_exp:,.0f} ({(total_exp/income*100):.1f}% of income)
    Monthly Surplus: ₹{surplus:,.0f}
    
    CURRENT SPENDING BREAKDOWN:
    {expense_breakdown}
    
    50/30/20 RULE TARGETS FOR THIS INCOME:
    Needs (50%): ₹{needs_target:,.0f}
    Wants (30%): ₹{wants_target:,.0f}
    Savings (20%): ₹{savings_target:,.0f}
    
    THEIR GOAL: {state['savings_goal']}
    They need ₹{state['goal_amount']:,.0f} in {state['goal_timeline_months']} months
    
    Create a practical budget plan:
    
    ## 📋 Your Optimized Budget
    For each expense category, show:
    Current amount → Recommended amount
    Explain any reduction suggestions kindly.
    
    ## ✂️ Smart Cost Reductions
    Suggest 3 specific, realistic ways to reduce spending.
    Give exact rupee amounts. Be practical, not extreme.
    
    ## 📐 50/30/20 Analysis
    How does their spending compare to the 50/30/20 rule?
    Which category is over/under the ideal?
    
    ## ⚡ 3 Actions For This Month
    Three specific things they can do immediately to improve 
    their budget. Include rupee amounts and exact steps.
    
    Be specific, use actual numbers, and be realistic for 
    someone living in India.
    """
    
    budget_plan = call_llm(prompt, max_tokens=900)
    
    return {"budget_plan": budget_plan}


# ════════════════════════════════════════
# NODE 3 — Savings & Investment Strategy
# ════════════════════════════════════════
def savings_strategy(state: dict) -> dict:
    """
    Third node. Runs AFTER budget_breakdown.
    
    What it does:
    - Calculates if the goal is financially achievable
    - Recommends how to split the monthly surplus
    - Suggests specific Indian investment products
    - Creates a 3-month action plan
    
    Key calculation:
    Amount still needed = Goal amount - Existing savings
    Monthly saving required = Amount still needed / Months remaining
    If monthly surplus >= monthly saving required → goal is achievable
    """
    
    print("💰 Node 3 running: Building savings strategy...")
    
    income        = state["monthly_income"]
    total_exp     = state["total_expenses"]
    surplus       = income - total_exp
    goal_amount   = state["goal_amount"]
    goal_months   = state["goal_timeline_months"]
    existing      = state["existing_savings"]
    
    # Core calculation — is this goal actually achievable?
    still_needed           = max(0, goal_amount - existing)
    # max(0, ...) prevents negative values if they already have enough
    
    monthly_saving_needed  = still_needed / goal_months if goal_months > 0 else 0
    goal_is_achievable     = surplus >= monthly_saving_needed
    
    # Emergency fund rule: you should have 3-6 months of expenses saved
    # as a safety net before investing
    emergency_fund_target  = total_exp * 6   # 6 months of expenses
    emergency_fund_gap     = max(0, emergency_fund_target - existing)
    
    prompt = f"""
    You are a SEBI-registered financial advisor creating a savings 
    and investment strategy. Use Indian financial context throughout.
    
    PERSON: {state['name']}, Age {state['age']}
    Monthly Surplus Available: ₹{surplus:,.0f}
    Existing Savings: ₹{existing:,.0f}
    Risk Appetite: {state['risk_appetite'].upper()}
    
    GOAL MATH:
    Goal: {state['savings_goal']}
    Total Target: ₹{goal_amount:,.0f}
    Already Saved: ₹{existing:,.0f}
    Still Need: ₹{still_needed:,.0f}
    Months Left: {goal_months}
    Required Monthly Saving: ₹{monthly_saving_needed:,.0f}
    Current Monthly Surplus: ₹{surplus:,.0f}
    Is Goal Achievable? {'YES ✅' if goal_is_achievable else 'NEEDS ADJUSTMENT ⚠️'}
    
    EMERGENCY FUND STATUS:
    Recommended (6 months expenses): ₹{emergency_fund_target:,.0f}
    Current Savings: ₹{existing:,.0f}
    Gap: ₹{emergency_fund_gap:,.0f}
    
    Create a complete strategy:
    
    ## 🎯 Goal Reality Check
    Is this goal achievable with current numbers? Show the math clearly.
    If not, what would need to change?
    
    ## 🛡️ Emergency Fund Plan
    Should they build emergency fund first or work toward goal simultaneously?
    Give a specific monthly amount and timeline.
    
    ## 📅 Monthly Surplus Allocation
    Split ₹{surplus:,.0f} across:
    - Emergency fund top-up
    - Goal savings  
    - Investment/wealth building
    Show exact rupee splits with percentages.
    
    ## 📈 Investment Options (India-specific)
    Based on {state['risk_appetite']} risk appetite, recommend from:
    FD, PPF, Mutual Fund SIP, ELSS, NPS, Digital Gold, Index Funds
    For each recommended option:
    - What it is (one sentence)
    - Expected annual returns
    - Minimum investment amount
    - Why it suits this person
    
    ## 🗓️ 90-Day Quick Start Plan
    Specific weekly actions for the first 3 months.
    Each action must have a rupee amount and a deadline.
    
    Be practical for Indian context. Use ₹ symbol throughout.
    """
    
    savings_plan = call_llm(prompt, max_tokens=1000)
    
    return {"savings_plan": savings_plan}


# ════════════════════════════════════════
# NODE 4 — Generate Final Report
# ════════════════════════════════════════
def generate_report(state: dict) -> dict:
    """
    Final node. Runs AFTER savings_strategy.
    
    What it does:
    - Reads ALL previous node outputs from state
    - Synthesizes everything into one cohesive report
    - Creates a 90-day action plan
    - Adds motivational closing message
    
    This is the "synthesis" step — taking 3 separate analyses
    and combining them into one unified, readable coaching report.
    
    This node has access to ALL previous outputs because they're 
    all in the shared state — that's the power of LangGraph's state.
    """
    
    print("📝 Node 4 running: Generating final coaching report...")
    
    income    = state["monthly_income"]
    total_exp = state["total_expenses"]
    surplus   = income - total_exp
    rate      = (surplus / income * 100) if income > 0 else 0
    
    prompt = f"""
    You are a senior personal finance coach writing a final 
    comprehensive report. You have completed 3 separate analyses.
    Now synthesize them into one clear, motivating, actionable report.
    
    PERSON: {state['name']}, Age {state['age']}
    Monthly Income: ₹{income:,.0f}
    Monthly Surplus: ₹{surplus:,.0f}
    Savings Rate: {rate:.1f}%
    Goal: {state['savings_goal']} — ₹{state['goal_amount']:,.0f} 
    in {state['goal_timeline_months']} months
    Risk Profile: {state['risk_appetite']}
    
    ANALYSES DONE (use these as context, don't repeat verbatim):
    Profile Analysis: {state['profile_analysis'][:400]}
    Budget Plan: {state['budget_plan'][:400]}  
    Savings Strategy: {state['savings_plan'][:400]}
    
    Write the final coaching report:
    
    ## 🌟 Executive Summary
    4-5 sentences covering: current situation, main challenge, 
    biggest opportunity, and overall path forward.
    Reference {state['name']} by name. Use actual numbers.
    
    ## 🗺️ Your 90-Day Action Plan
    TOP 10 most important actions for the next 90 days.
    Format each as:
    "📅 [Week/Month]: [Specific action] — Target: ₹[amount]"
    Be very specific. Each action must be completable.
    
    ## 📊 Financial Scorecard
    Create this scorecard table:
    
    | Metric | Current | Target | Status |
    |--------|---------|--------|--------|
    | Savings Rate | {rate:.1f}% | 20%+ | [emoji] |
    | Monthly Savings | ₹{surplus:,.0f} | ₹[target] | [emoji] |
    | Emergency Fund | [status] | ₹[target] | [emoji] |
    | Goal Progress | [%] | 100% | [emoji] |
    
    Use ✅ for on track, ⚠️ for needs work, ❌ for critical
    
    ## 💪 Coach's Final Message
    3 sentences directly to {state['name']}.
    Reference their specific goal ({state['savings_goal']}).
    Be genuinely encouraging. Make it personal, not generic.
    
    ## ⚠️ Important Disclaimer
    This report is AI-generated for educational and informational 
    purposes only. It does not constitute financial advice. 
    Please consult a SEBI-registered financial advisor before 
    making investment decisions.
    """
    
    final_report = call_llm(prompt, max_tokens=1200)
    
    return {"final_report": final_report}