# 💰 AI Personal Finance Coach

An AI-powered personal finance coach that turns your income, expenses, and
savings goals into a complete, personalized financial plan in under 60
seconds — built with **LangGraph**, **Groq's LLaMA 3.3 70B**, and **Streamlit**.

You fill in a simple form (income, expenses, goals), and a 4-step AI
pipeline analyzes your financial health, builds a budget using the
50/30/20 rule, designs a savings/investment strategy for the Indian
context, and synthesizes it all into one final coaching report — complete
with interactive charts and a downloadable summary.

---

## ✨ Features

- **Financial Health Score (0–100)** — a single gauge score blending your savings rate, needs ratio, and wants ratio
- **50/30/20 budget comparison** — see your actual spending split vs the ideal Needs/Wants/Savings ratio
- **Interactive visualizations** — expense pie chart, category radar chart, savings-goal projection line chart, all built with Plotly
- **Goal tracking** — progress bar showing how close you are to your savings goal, with a month-by-month projection
- **4-stage AI reasoning pipeline** (see Architecture below), each stage visible as its own tab so you can see exactly how the AI reasoned
- **Downloadable report** — full plan exportable as a `.txt` file

---

## 🧠 Architecture

The core of this project is a **LangGraph pipeline**: instead of one big
prompt trying to do everything, the analysis is split into 4 sequential
nodes, each focused on one job and building on the previous node's output
via shared state.

```
START
  │
  ▼
┌─────────────────────┐
│ 1. analyze_profile   │  Calculates surplus & savings rate,
│                      │  asks the LLM for a health score +
│                      │  honest situation summary
└──────────┬───────────┘
           ▼
┌─────────────────────┐
│ 2. budget_breakdown  │  Compares spending to the 50/30/20 rule,
│                      │  asks the LLM for specific cost-cutting
│                      │  suggestions
└──────────┬───────────┘
           ▼
┌─────────────────────┐
│ 3. savings_strategy  │  Checks if the goal is mathematically
│                      │  achievable, recommends India-specific
│                      │  investment options (FD, PPF, SIP, etc.)
└──────────┬───────────┘
           ▼
┌─────────────────────┐
│ 4. generate_report   │  Synthesizes all 3 previous outputs into
│                      │  one final report with a 90-day action
│                      │  plan and scorecard
└──────────┬───────────┘
           ▼
          END
```

Every node reads from and writes to one shared `FinanceState` dictionary
(defined in `state.py`), so node 4 can reference the outputs of nodes 1–3
without recalculating anything — that's the core benefit of LangGraph's
state-passing design.

### File-by-file breakdown

| File | Role |
|---|---|
| `app.py` | Streamlit UI — the input form, all charts/gauges, and result tabs |
| `graph.py` | Builds the LangGraph `StateGraph`: defines the 4 nodes and the order they run in |
| `nodes.py` | The actual logic + LLM prompts for each of the 4 pipeline steps |
| `state.py` | `FinanceState` — the shared "memory" schema that flows through the graph |

---

## 🛠️ Tech Stack

- **LLM**: Groq API, running `llama-3.3-70b-versatile`
- **Agent framework**: LangGraph (`StateGraph`, sequential nodes)
- **Frontend**: Streamlit
- **Visualizations**: Plotly (gauge, pie, radar, grouped bar, line charts)

---

## 🚀 Setup

```bash
git clone https://github.com/rit-ops14/ai-finance-coach.git
cd ai-finance-coach

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install streamlit plotly langgraph groq python-dotenv

# Add your API key
cp .env.example .env
# then edit .env and add: GROQ_API_KEY=your_key_here
# get a free key at https://console.groq.com/keys

streamlit run app.py
```

Open the local URL Streamlit prints (usually `http://localhost:8501`),
fill in the sidebar form with your income, expenses, and goals, then click
**"🚀 Generate My Financial Plan"**.

---

## 📸 Example usage

1. Enter monthly income (e.g. ₹50,000) and expenses across 8 categories
2. Set a savings goal (e.g. "Build emergency fund", ₹100,000 in 12 months)
3. Click generate — watch all 4 pipeline nodes complete live
4. Explore the tabs: Full Report, Profile Analysis, Budget Plan, Savings Strategy
5. Download the complete plan as a `.txt` file

---

## ⚠️ Disclaimer

This tool is built for educational purposes as part of a college project.
All financial guidance is AI-generated and does **not** constitute
professional financial advice. Please consult a SEBI-registered financial
advisor before making real investment decisions.

---

## 🔭 Future improvements

- Persist user data across sessions (currently single-session only)
- Add expense tracking over time instead of a one-time snapshot
- Support multiple currencies / non-Indian financial contexts
- Add authentication so multiple users can save separate plans