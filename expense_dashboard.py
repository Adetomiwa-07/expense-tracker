
import json
from pathlib import Path
from datetime import date
import streamlit as st

# =====================================
# 1. CONFIGURATION
# =====================================

st.set_page_config(
    page_title="My Expense Tracker",
    page_icon="💰",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
EXPENSES_FILE = BASE_DIR / "expenses.json"
BUDGET_FILE = BASE_DIR / "budget.json"


# =====================================
# 2. LOAD AND SAVE DATA
# =====================================

def load_expenses():
    try:
        with open(EXPENSES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        st.error("The expenses file contains invalid JSON.")
        return []


def save_expenses(expenses):
    with open(EXPENSES_FILE, "w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=4)


def load_budget():
    try:
        with open(BUDGET_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return max(0.0, float(data.get("budget", 20000)))

    except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError):
        return 20000.0


def save_budget(budget):
    with open(BUDGET_FILE, "w", encoding="utf-8") as file:
        json.dump({"budget": budget}, file, indent=4)


# =====================================
# 3. LOAD EXISTING DATA
# =====================================

expenses = load_expenses()
budget = load_budget()


# =====================================
# 4. DASHBOARD HEADER
# =====================================

st.title("💰 My Expense Tracker")
st.write("Track your spending and manage your budget.")
st.caption("Record expenses, monitor your budget, and review monthly spending.")

st.divider()


# =====================================
# 5. ADD NEW EXPENSE
# =====================================

st.header("Add a New Expense")

with st.form("expense_form", clear_on_submit=True):
    expense_name = st.text_input("Expense name")

    category = st.selectbox(
        "Category",
        [
            "Food",
            "Transport",
            "Housing",
            "Bills",
            "Health",
            "Education",
            "Entertainment",
            "Other"
        ]
    )

    amount = st.number_input(
        "Amount (₦)",
        min_value=0.0,
        value=0.0,
        step=100.0
    )

    expense_date = st.date_input(
        "Expense date",
        value=date.today()
    )

    submitted = st.form_submit_button("Add Expense")

    if submitted:
        if not expense_name.strip():
            st.error("Please enter an expense name.")

        elif amount <= 0:
            st.error("The amount must be greater than zero.")

        else:
            expenses.append({
                "name": expense_name.strip(),
                "category": category,
                "amount": amount,
                "date": expense_date.isoformat()
            })

            save_expenses(expenses)
            st.success("Expense saved successfully!")
            st.rerun()


st.divider()


# =====================================
# 6. BUDGET SETTINGS
# =====================================

st.header("Budget Settings")

with st.form("budget_form"):
    new_budget = st.number_input(
        "Monthly budget (₦)",
        min_value=0.0,
        value=float(budget),
        step=1000.0
    )

    budget_submitted = st.form_submit_button("Save Budget")

    if budget_submitted:
        save_budget(new_budget)
        st.success("Budget saved successfully!")
        st.rerun()


st.divider()


# =====================================
# 7. MONTHLY REPORT FILTER
# =====================================

st.header("Expense Reports")

today = date.today()

selected_month = st.date_input(
    "Choose a month to review",
    value=today.replace(day=1),
    help="Select any date within the month you want to review."
)

month_key = selected_month.strftime("%Y-%m")

month_expenses = [
    expense for expense in expenses
    if expense.get("date", "").startswith(month_key)
]


# =====================================
# 8. MONTHLY CALCULATIONS
# =====================================

total = sum(
    float(expense.get("amount", 0))
    for expense in month_expenses
)

remaining = budget - total

st.subheader(selected_month.strftime("%B %Y") + " Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Monthly Spending", f"₦{total:,.2f}")
col2.metric("Monthly Budget", f"₦{budget:,.2f}")
col3.metric("Budget Remaining", f"₦{remaining:,.2f}")

if budget > 0:
    progress = min(total / budget, 1.0)

    st.progress(
        progress,
        text=f"{progress:.0%} of budget used"
    )

if total > budget:
    st.warning("Your spending has exceeded the saved budget.")
elif budget > 0:
    st.success("Your spending is within the saved budget.")


# =====================================
# 9. MONTHLY EXPENSE TABLE
# =====================================

st.subheader("Expenses for Selected Month")

if month_expenses:
    st.dataframe(
        month_expenses,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Monthly Expenses",
        data=json.dumps(month_expenses, indent=4),
        file_name=f"expenses_{month_key}.json",
        mime="application/json"
    )

else:
    st.info("No expenses recorded for this month.")


# =====================================
# 10. CATEGORY CHART
# =====================================

st.subheader("Spending by Category")

if month_expenses:
    category_totals = {}

    for expense in month_expenses:
        category_name = expense.get("category", "Other")
        category_amount = float(expense.get("amount", 0))

        category_totals[category_name] = (
            category_totals.get(category_name, 0)
            + category_amount
        )

    st.bar_chart(category_totals, horizontal=True)

else:
    st.info("Add expenses for this month to see the chart.")


st.divider()


# =====================================
# 11. DELETE AN EXPENSE
# =====================================

st.header("Delete an Expense")

if expenses:
    expense_options = [
        (
            f"{i + 1}. {item.get('name', 'Unnamed')} | "
            f"{item.get('date', 'No date')} | "
            f"₦{float(item.get('amount', 0)):,.2f}"
        )
        for i, item in enumerate(expenses)
    ]

    selected_index = st.selectbox(
        "Choose an expense to delete",
        range(len(expenses)),
        format_func=lambda i: expense_options[i]
    )

    if st.button("Delete Selected Expense"):
        expenses.pop(selected_index)
        save_expenses(expenses)
        st.success("Expense deleted successfully.")
        st.rerun()

else:
    st.info("There are no expenses to delete.")


# =====================================
# 12. FOOTER
# =====================================

st.divider()
st.caption("My Expense Tracker | Built with Python and Streamlit")
