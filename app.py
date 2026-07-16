import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="AI Supply Chain Demand & Risk Predictor",
    page_icon="📦",
    layout="wide"
)

# Load Data
sales = pd.read_csv("sales_history.csv")
suppliers = pd.read_csv("supplier_data.csv")
inventory = pd.read_csv("inventory.csv")

# Risk Calculation
suppliers["risk_score"] = (
    (100 - suppliers["on_time_delivery"]) * 0.4
    + (100 - suppliers["quality_score"]) * 0.3
    + (100 - suppliers["financial_score"]) * 0.3
).round(1)


def risk_level(score):
    if score <= 20:
        return "Low"
    elif score <= 40:
        return "Medium"
    else:
        return "High"


suppliers["risk_level"] = suppliers["risk_score"].apply(risk_level)

# Sidebar Filters
st.sidebar.header("Filters")

selected_warehouse = st.sidebar.selectbox(
    "Warehouse",
    ["All"] + inventory["warehouse"].unique().tolist()
)

selected_product = st.sidebar.selectbox(
    "Product",
    ["All"] + inventory["product"].unique().tolist()
)

selected_supplier = st.sidebar.selectbox(
    "Supplier",
    ["All"] + suppliers["supplier"].unique().tolist()
)

# Apply Filters
filtered_inventory = inventory.copy()
filtered_suppliers = suppliers.copy()
filtered_sales = sales.copy()

if selected_warehouse != "All":
    filtered_inventory = filtered_inventory[
        filtered_inventory["warehouse"] == selected_warehouse
    ]

if selected_product != "All":
    filtered_inventory = filtered_inventory[
        filtered_inventory["product"] == selected_product
    ]

    filtered_sales = filtered_sales[
        filtered_sales["product"] == selected_product
    ]

if selected_supplier != "All":
    filtered_suppliers = filtered_suppliers[
        filtered_suppliers["supplier"] == selected_supplier
    ]

# KPI Calculations
inventory_total = filtered_inventory["current_stock"].sum()

if len(filtered_sales) > 0:
    forecast = int(filtered_sales["sales"].tail(3).mean() * 1.15)
else:
    forecast = 0

if inventory_total > 0:
    stockout_risk = min(
        round((forecast / inventory_total) * 100, 1),
        100
    )
else:
    stockout_risk = 0

high_risk_count = len(
    filtered_suppliers[
        filtered_suppliers["risk_level"] == "High"
    ]
)

# Title
st.title("📦 AI Powered Supply Chain Demand & Risk Predictor")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Executive Dashboard",
        "Demand Forecast",
        "Supplier Risks",
        "AI Copilot"
    ]
)

# ---------------------------------------------------
# EXECUTIVE DASHBOARD
# ---------------------------------------------------
with tab1:

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Forecast Demand",
        forecast
    )

    c2.metric(
        "Inventory Units",
        inventory_total
    )

    c3.metric(
        "High Risk Suppliers",
        high_risk_count
    )

    c4.metric(
        "Stockout Risk %",
        stockout_risk
    )

    st.subheader("Filtered Inventory Overview")

    st.dataframe(
        filtered_inventory,
        use_container_width=True
    )

# ---------------------------------------------------
# DEMAND FORECAST
# ---------------------------------------------------
with tab2:

    st.subheader("Demand Forecast Trend")

    if len(filtered_sales) > 0:

        fig = px.line(
            filtered_sales,
            x="month",
            y="sales",
            color="product",
            markers=True,
            title="Historical Demand Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.success(
            f"Predicted Next Month Demand: {forecast} Units"
        )

    else:
        st.warning("No sales data available for selected filters.")

# ---------------------------------------------------
# SUPPLIER RISKS
# ---------------------------------------------------
with tab3:

    st.subheader("Supplier Risk Assessment")

    color_map = {
        "Low": "green",
        "Medium": "orange",
        "High": "red"
    }

    if len(filtered_suppliers) > 0:

        fig2 = px.bar(
            filtered_suppliers,
            x="supplier",
            y="risk_score",
            color="risk_level",
            color_discrete_map=color_map,
            title="Supplier Risk Ranking"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.dataframe(
            filtered_suppliers,
            use_container_width=True
        )

    else:
        st.warning("No supplier data available.")

# ---------------------------------------------------
# AI COPILOT
# ---------------------------------------------------
with tab4:

    st.subheader("🤖 Supply Chain AI Copilot")

    question = st.text_input(
        "Ask a question",
        "Why is inventory at risk?"
    )

    if st.button("Analyze"):

        risk_status = (
            "High" if stockout_risk > 70
            else "Medium" if stockout_risk > 40
            else "Low"
        )

        recommendation = f"""
### AI Analysis

**Question:** {question}

### Current Situation

- Forecasted Demand: **{forecast} Units**
- Current Inventory: **{inventory_total} Units**
- Stockout Risk: **{stockout_risk}%**
- Supplier Risk Level: **{risk_status}**

### Recommendations

✅ Increase procurement by 20%

✅ Maintain safety stock for at least 15 days

✅ Prioritize suppliers with Low Risk rating

✅ Review warehouse inventory every week

✅ Monitor demand spikes proactively

### Business Impact

Reducing stockout risk can improve order fulfillment rates and reduce revenue loss caused by inventory shortages.
"""

        st.markdown(recommendation)

# Footer
st.markdown("---")
st.caption("AI Powered Supply Chain Demand & Risk Predictor | Prototype Version")
