import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI Supply Chain Predictor", layout="wide")

sales=pd.read_csv('sales_history.csv')
sup=pd.read_csv('supplier_data.csv')
inv=pd.read_csv('inventory.csv')

st.title('AI Powered Supply Chain Demand and Risk Predictor')

avg_sales=sales['sales'].tail(3).mean()
forecast=int(avg_sales*1.15)
stock=inv['current_stock'].sum()
stockout=max(0,min(100,int((forecast/max(stock,1))*100)))

sup['risk_score']=((100-sup['on_time_delivery'])*0.4 + (100-sup['quality_score'])*0.3 + (100-sup['financial_score'])*0.3).round(1)

c1,c2,c3,c4=st.columns(4)
c1.metric('Forecast Demand', forecast)
c2.metric('Inventory Units', int(stock))
c3.metric('High Risk Suppliers', int((sup['risk_score']>25).sum()))
c4.metric('Stockout Risk %', stockout)

st.subheader('Demand Trend')
fig=px.line(sales,x='month',y='sales',color='product',markers=True)
st.plotly_chart(fig,use_container_width=True)

st.subheader('Supplier Risk Scores')
st.dataframe(sup)

st.subheader('Inventory')
st.dataframe(inv)

st.subheader('AI Recommendation')
if stock < forecast:
    st.warning(f'Demand is forecast at {forecast} units. Current inventory may be insufficient. Increase procurement and prioritize low-risk suppliers.')
else:
    st.success('Inventory appears sufficient for projected demand.')
