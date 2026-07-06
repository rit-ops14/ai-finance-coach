# app.py

import streamlit as st        # the web framework
import plotly.express as px   # for pie/bar charts
import plotly.graph_objects as go  # for line/gauge/radar charts
from graph import run_finance_coach  # our pipeline

# ── PAGE SETUP ──
st.set_page_config(
    page_title="AI Finance Coach",
    page_icon="💰",
    layout="wide"
)

# ── HEADER ──
st.markdown("""
# 💰 AI Personal Finance Coach
### *Powered by LangGraph + Groq LLaMA 3.3 70B*
Get your personalized financial plan in under 60 seconds.
""")

st.divider()

# ════════════════════════════════════════
# SIDEBAR — The Input Form
# ════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📝 Your Details")

    st.markdown("### 👤 Personal Info")
    name = st.text_input("Your Name", value="Rahul Sharma")
    age = st.slider("Your Age", min_value=18, max_value=65, value=25)

    st.divider()

    st.markdown("### 💵 Income")
    monthly_income = st.number_input(
        "Monthly Take-home Salary (₹)",
        min_value=10000, max_value=1000000, value=50000, step=1000
    )
    existing_savings = st.number_input(
        "Existing Savings (₹)",
        min_value=0, max_value=10000000, value=15000, step=1000
    )

    st.divider()

    st.markdown("### 🧾 Monthly Expenses")
    st.caption("Adjust each to match your actual spending:")

    rent          = st.number_input("🏠 Rent / EMI",        value=12000, step=500)
    food          = st.number_input("🍔 Food & Groceries",  value=7000,  step=500)
    transport     = st.number_input("🚗 Transport",          value=3000,  step=500)
    utilities     = st.number_input("💡 Utilities & Bills", value=2000,  step=500)
    entertainment = st.number_input("🎬 Entertainment",     value=3000,  step=500)
    shopping      = st.number_input("🛍️ Shopping",          value=4000,  step=500)
    subscriptions = st.number_input("📱 Subscriptions",     value=1000,  step=500)
    other         = st.number_input("📦 Other",             value=2000,  step=500)

    st.divider()

    st.markdown("### 🎯 Your Financial Goal")
    savings_goal = st.text_area(
        "What are you saving for?",
        value="Build emergency fund and save for a vacation",
        height=80
    )
    goal_amount = st.number_input(
        "Goal Amount (₹)",
        min_value=1000, max_value=10000000, value=100000, step=5000
    )
    goal_timeline = st.slider("Timeline (months)", min_value=1, max_value=60, value=12)
    risk_appetite = st.selectbox("Risk Appetite", options=["low", "medium", "high"], index=1)

    st.divider()

    analyze_btn = st.button(
        "🚀 Generate My Financial Plan",
        type="primary",
        use_container_width=True
    )

# ════════════════════════════════════════
# HELPER: Financial Health Score
# ════════════════════════════════════════
def compute_health_score(savings_rate_pct, needs_pct, wants_pct):
    """
    Blends three signals into a single 0-100 health score:
    - Savings rate (higher is better, capped at 30% = full marks)
    - Needs ratio (closer to ideal 50% is better)
    - Wants ratio (closer to ideal 30% is better)
    """
    savings_score = min(savings_rate_pct / 30 * 100, 100)
    needs_score = max(0, 100 - abs(needs_pct - 50) * 2)
    wants_score = max(0, 100 - abs(wants_pct - 30) * 2)
    return round((savings_score * 0.5) + (needs_score * 0.25) + (wants_score * 0.25))


def make_gauge(score):
    if score >= 75:
        bar_color = "#4CAF50"
    elif score >= 50:
        bar_color = "#FFC107"
    else:
        bar_color = "#F44336"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={'suffix': " / 100", 'font': {'size': 40}},
        title={'text': "Financial Health Score", 'font': {'size': 20}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': bar_color, 'thickness': 0.3},
            'steps': [
                {'range': [0, 50], 'color': '#FDE8E8'},
                {'range': [50, 75], 'color': '#FFF6DA'},
                {'range': [75, 100], 'color': '#E5F6E8'}
            ],
        }
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=10))
    return fig


# ════════════════════════════════════════
# MAIN AREA — Results
# ════════════════════════════════════════

if not analyze_btn:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.info("**🔍 Node 1**\nProfile Analysis & Health Score")
    with c2:
        st.info("**📊 Node 2**\nSmart Budget with 50/30/20")
    with c3:
        st.info("**💰 Node 3**\nSavings & Investment Plan")
    with c4:
        st.info("**📝 Node 4**\nFull Coaching Report")

    st.markdown("\n👈 Fill the form in the sidebar and click **Generate My Financial Plan**")

else:
    expenses = {
        "rent":          rent,
        "food":          food,
        "transport":     transport,
        "utilities":     utilities,
        "entertainment": entertainment,
        "shopping":      shopping,
        "subscriptions": subscriptions,
        "other":         other
    }

    total_expenses   = sum(expenses.values())
    monthly_surplus  = monthly_income - total_expenses
    savings_rate_pct = (monthly_surplus / monthly_income * 100) if monthly_income > 0 else 0

    # Classify into Needs / Wants for the 50/30/20 comparison
    needs_total  = rent + food + transport + utilities
    wants_total  = entertainment + shopping + subscriptions + other
    needs_pct    = (needs_total / monthly_income * 100) if monthly_income > 0 else 0
    wants_pct    = (wants_total / monthly_income * 100) if monthly_income > 0 else 0
    savings_pct  = max(savings_rate_pct, 0)

    health_score = compute_health_score(savings_rate_pct, needs_pct, wants_pct)

    # ── TOP ROW: GAUGE + METRICS ──
    st.markdown(f"## 📊 {name}'s Financial Snapshot")

    gauge_col, metrics_col = st.columns([1, 2])

    with gauge_col:
        st.plotly_chart(make_gauge(health_score), use_container_width=True)

    with metrics_col:
        m1, m2 = st.columns(2)
        m3, m4 = st.columns(2)
        m1.metric("💵 Income", f"₹{monthly_income:,.0f}")
        m2.metric("💸 Expenses", f"₹{total_expenses:,.0f}")
        m3.metric("💰 Surplus", f"₹{monthly_surplus:,.0f}",
                  delta="Surplus" if monthly_surplus > 0 else "⚠️ Deficit")
        m4.metric("📈 Savings Rate", f"{savings_rate_pct:.1f}%",
                  delta="✅ Healthy" if savings_rate_pct >= 20 else "⚠️ Below 20%")

    st.divider()

    # ── 50/30/20 COMPARISON CHART ──
    st.markdown("### ⚖️ Your Split vs the Ideal 50/30/20 Rule")

    fig_compare = go.Figure(data=[
        go.Bar(name='Your Budget', x=['Needs', 'Wants', 'Savings'],
               y=[needs_pct, wants_pct, savings_pct],
               marker_color='#4C72B0', text=[f"{v:.0f}%" for v in [needs_pct, wants_pct, savings_pct]],
               textposition='outside'),
        go.Bar(name='Ideal (50/30/20)', x=['Needs', 'Wants', 'Savings'],
               y=[50, 30, 20],
               marker_color='#DDDDDD', text=['50%', '30%', '20%'],
               textposition='outside')
    ])
    fig_compare.update_layout(barmode='group', height=350, yaxis_title="% of Income")
    st.plotly_chart(fig_compare, use_container_width=True)

    # ── EXPENSE PIE + RADAR SIDE BY SIDE ──
    pie_col, radar_col = st.columns(2)

    with pie_col:
        st.markdown("### 🥧 How Your Money is Spent")
        chart_expenses = {**expenses}
        if monthly_surplus > 0:
            chart_expenses["savings_available"] = monthly_surplus

        fig_pie = px.pie(
            values=list(chart_expenses.values()),
            names=[k.replace("_", " ").title() for k in chart_expenses.keys()],
            hole=0.35,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=380)
        st.plotly_chart(fig_pie, use_container_width=True)

    with radar_col:
        st.markdown("### 🕸️ Category Spend Intensity")
        categories = [k.title() for k in expenses.keys()]
        values = [(v / monthly_income * 100) if monthly_income > 0 else 0 for v in expenses.values()]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='% of Income',
            line_color='#4C72B0'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            showlegend=False,
            height=380
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ── GOAL PROGRESS ──
    st.markdown("### 🎯 Goal Progress")
    progress = min(existing_savings / goal_amount, 1.0) if goal_amount > 0 else 0
    st.progress(progress)
    st.caption(
        f"₹{existing_savings:,.0f} of ₹{goal_amount:,.0f} saved "
        f"({progress*100:.1f}% complete) — Goal: {savings_goal}"
    )

    st.divider()

    # ── RUN THE LANGGRAPH PIPELINE ──
    st.markdown("## 🤖 Running LangGraph Analysis Pipeline...")

    col_n1, col_n2, col_n3, col_n4 = st.columns(4)
    with col_n1:
        n1 = st.empty(); n1.warning("🔍 Node 1: Waiting...")
    with col_n2:
        n2 = st.empty(); n2.warning("📊 Node 2: Waiting...")
    with col_n3:
        n3 = st.empty(); n3.warning("💰 Node 3: Waiting...")
    with col_n4:
        n4 = st.empty(); n4.warning("📝 Node 4: Waiting...")

    user_data = {
        "name":                 name,
        "age":                  age,
        "monthly_income":       monthly_income,
        "monthly_expenses":     expenses,
        "total_expenses":       total_expenses,
        "savings_goal":         savings_goal,
        "goal_amount":          goal_amount,
        "goal_timeline_months": goal_timeline,
        "risk_appetite":        risk_appetite,
        "existing_savings":     existing_savings
    }

    with st.spinner("🧠 AI is analyzing your finances through 4 nodes..."):
        result = run_finance_coach(user_data)

    n1.success("✅ Node 1: Profile Done")
    n2.success("✅ Node 2: Budget Done")
    n3.success("✅ Node 3: Savings Done")
    n4.success("✅ Node 4: Report Done")

    st.success("🎉 Your personalized financial plan is ready!")
    st.divider()

    # ── RESULTS: KEY INSIGHTS FIRST, DETAIL ON DEMAND ──
    st.markdown("## 🌟 Your Coaching Summary")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Full Report",
        "🔍 Profile Analysis",
        "📊 Budget Plan",
        "💰 Savings Strategy"
    ])

    with tab1:
        with st.expander("📖 Read Full Report", expanded=True):
            st.markdown(result.get("final_report", "Report generation failed"))

        st.divider()

        download_text = f"""
PERSONAL FINANCE COACH — AI REPORT
Name: {name} | Age: {age}
Generated by: AI Personal Finance Coach (LangGraph + Groq)
{'='*50}

FINANCIAL SNAPSHOT:
Income:   ₹{monthly_income:,.0f}/month
Expenses: ₹{total_expenses:,.0f}/month
Surplus:  ₹{monthly_surplus:,.0f}/month
Health Score: {health_score}/100
Goal:     {savings_goal} — ₹{goal_amount:,.0f} in {goal_timeline} months

{'='*50}
PROFILE ANALYSIS:
{result.get('profile_analysis', '')}

{'='*50}
BUDGET PLAN:
{result.get('budget_plan', '')}

{'='*50}
SAVINGS STRATEGY:
{result.get('savings_plan', '')}

{'='*50}
FINAL COACHING REPORT:
{result.get('final_report', '')}

{'='*50}
DISCLAIMER: AI-generated for educational purposes only.
Not financial advice. Consult a SEBI-registered advisor.
        """

        st.download_button(
            label="⬇️ Download Full Report as .txt",
            data=download_text,
            file_name=f"{name.replace(' ','_')}_finance_report.txt",
            mime="text/plain",
            use_container_width=True
        )

    with tab2:
        st.caption("Generated by Node 1 of the LangGraph pipeline")
        with st.expander("🔍 Read Profile Analysis", expanded=True):
            st.markdown(result.get("profile_analysis", "Not available"))

    with tab3:
        st.caption("Generated by Node 2 of the LangGraph pipeline")

        st.markdown("### 📊 Expense Category Breakdown")
        fig_bar = px.bar(
            x=[k.title() for k in expenses.keys()],
            y=list(expenses.values()),
            labels={"x": "Category", "y": "Amount (₹)"},
            color=list(expenses.values()),
            color_continuous_scale="Blues"
        )
        fig_bar.update_layout(height=350)
        st.plotly_chart(fig_bar, use_container_width=True)

        with st.expander("📖 Read Full Budget Plan"):
            st.markdown(result.get("budget_plan", "Not available"))

    with tab4:
        st.caption("Generated by Node 3 of the LangGraph pipeline")

        st.markdown("### 📈 Savings Trajectory to Your Goal")
        still_needed   = max(0, goal_amount - existing_savings)
        monthly_needed = still_needed / goal_timeline if goal_timeline > 0 else 0

        months     = list(range(0, goal_timeline + 1))
        projected  = [
            min(existing_savings + (monthly_needed * m), goal_amount)
            for m in months
        ]

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=months, y=projected,
            mode='lines+markers',
            name='Projected Savings',
            line=dict(color='#4CAF50', width=3),
            fill='tozeroy',
            fillcolor='rgba(76,175,80,0.1)'
        ))
        fig_line.add_hline(
            y=goal_amount,
            line_dash="dash",
            line_color="red",
            annotation_text=f"🎯 Goal: ₹{goal_amount:,.0f}"
        )
        fig_line.update_layout(
            xaxis_title="Month Number",
            yaxis_title="Total Savings (₹)",
            height=400
        )
        st.plotly_chart(fig_line, use_container_width=True)

        with st.expander("📖 Read Full Savings Strategy"):
            st.markdown(result.get("savings_plan", "Not available"))

# ── FOOTER ──
st.divider()
st.caption("Built with LangGraph + Groq LLaMA 3.3 70B + Streamlit | Educational purposes only")