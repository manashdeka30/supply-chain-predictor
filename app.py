import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="AI Supply Chain Demand & Risk Predictor",
    page_icon="📦",
    layout="wide"
)

sales = pd.read_csv("sales_history.csv")
suppliers = pd.read_csv("supplier_data.csv")
inventory = pd.read_csv("inventory.csv")

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
    return "High"

suppliers["risk_level"] = suppliers["risk_score"].apply(risk_level)

forecast = int(sales["sales"].tail(3).mean() * 1.15)
inventory_total = inventory["current_stock"].sum()

stockout_risk = min(
    round((forecast / max(inventory_total, 1)) * 100, 1),
    100
)

st.title("📦 AI Powered Supply Chain Demand & Risk Predictor")

with st.sidebar:
    st.header("Filters")

    selected_warehouse = st.selectbox(
        "Warehouse",
        ["All"] + inventory["warehouse"].unique().tolist()
    )

    selected_supplier = st.selectbox(
        "Supplier",
        ["All"] + suppliers["supplier"].tolist()
    )

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Executive Dashboard",
        "Demand Forecast",
        "Supplier Risks",
        "AI Copilot"
    ]
)

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
        len(
            suppliers[
                suppliers["risk_level"] == "High"
            ]
        )
    )

    c4.metric(
        "Stockout Risk %",
        stockout_risk
    )

    st.subheader("Inventory Overview")
    st.dataframe(inventory)

with tab2:

    st.subheader("Historical Demand")

    fig = px.line(
        sales,
        x="month",
        y="sales",
        color="product",
        markers=True,
        title="Demand Trend"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.success(
        f"Predicted Next Month Demand: {forecast} Units"
    )

with tab3:

    st.subheader("Supplier Risk Assessment")

    color_map = {
        "Low": "green",
        "Medium": "orange",
        "High": "red"
    }

    fig2 = px.bar(
        suppliers,
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

    st.dataframe(suppliers)

with tab4:

    st.subheader("Supply Chain AI Copilot")

    question = st.text_input(
        "Ask a question",
        "Why is inventory at risk?"
    )

    if st.button("Analyze"):

        recommendation = f"""
### AI Analysis

Forecasted Demand: {forecast}

Current Inventory: {inventory_total}

Stockout Risk: {stockout_risk}%

### Recommendations

✅ Increase procurement by 20%

✅ Maintain safety stock for 15 days

✅ Prioritize low-risk suppliers

✅ Monitor warehouse inventory weekly

✅ Prepare alternate sourcing strategy
"""

        st.markdown(recommendation)
