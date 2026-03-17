import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Stock Trend AI Dashboard", layout="wide", page_icon="📈")

# ---------------- CUSTOM STYLE ----------------
st.markdown("""
<style>
body {
    background-color:#0a142f;
    color:white;
    font-family: Arial, sans-serif;
}
.main-title{
    text-align:center;
    background: linear-gradient(90deg,#1e3d59,#1e5799);
    padding:25px;
    border-radius:10px;
    color:white;
}
.feature-card{
    background: linear-gradient(135deg,#1e3d59,#1e5799);
    padding:20px;
    border-radius:12px;
    text-align:center;
    font-weight:bold;
    transition: transform 0.2s, box-shadow 0.2s;
}
.feature-card:hover{
    transform: translateY(-5px);
    box-shadow:0 8px 15px rgba(255,255,255,0.2);
}
.stat-card{
    background:#1e3d59;
    padding:15px;
    border-radius:10px;
    text-align:center;
}
.footer{
    text-align:center;
    padding:10px;
    color:gray;
}
.table-container{
    overflow-x:auto;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="main-title">
<h1>📈 Stock Trend AI Dashboard</h1>
<p>Professional Stock & Crypto Analysis</p>
<p style="color:#ffd700;">Milestone - 3</p>
</div>
""", unsafe_allow_html=True)

# ---------------- KEY FEATURES ----------------
st.markdown("## 🚀 Key Features")
cols = st.columns(6)
features = ["📂 CSV Upload", "📊 Dataset Preview", "📉 Data Distribution", 
            "🧹 Outlier Detection", "🤖 AI Prediction", "📈 Market Insights"]
for col, feat in zip(cols, features):
    col.markdown(f'<div class="feature-card">{feat}</div>', unsafe_allow_html=True)

# ---------------- CSV UPLOAD ----------------
st.markdown("## 📂 Upload Dataset")
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
df = None
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("Dataset Loaded Successfully!")

# ---------------- DATA PREVIEW ----------------
if df is not None:
    st.markdown("## 📊 Dataset Preview")
    st.dataframe(df.head(10))

# ---------------- STOCK CHART ----------------
if df is not None:
    st.markdown("## 📈 Stock Price Chart")
    numeric_df = df.select_dtypes(include=np.number)
    if not numeric_df.empty:
        st.line_chart(numeric_df)

# ---------------- DATA DISTRIBUTION ----------------
if df is not None:
    st.markdown("## 📉 Data Distribution")
    closes = df.iloc[:,4].astype(float) if df.shape[1] > 4 else df.iloc[:,0].astype(float)
    q1 = closes.quantile(0.25)
    q3 = closes.quantile(0.75)
    iqr = q3 - q1
    filtered = closes[(closes >= q1 - 1.5*iqr) & (closes <= q3 + 1.5*iqr)]
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Before Outliers")
        st.bar_chart(closes)
    with col2:
        st.subheader("After Outliers Removed")
        st.bar_chart(filtered)

# ---------------- STATISTICS PANEL ----------------
if df is not None:
    st.markdown("## 📊 Stock Performance Metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Mean Price", round(closes.mean(),2))
    col2.metric("Std Deviation", round(closes.std(),2))
    col3.metric("Max Price", round(closes.max(),2))
    col4.metric("Min Price", round(closes.min(),2))
    col5.metric("Last Close", round(closes.iloc[-1],2))
    col6.metric("Total Records", len(df))

# ---------------- AI PREDICTION ----------------
st.markdown("## 🔮 AI Prediction")
p1, p2, p3 = st.columns([2,2,1])
symbol = p1.text_input("Stock Symbol", "TSLA").upper()
days_option = p2.selectbox("Prediction Duration", ["Next Day", "7 Days", "20 Days", "30 Days"])
refresh_btn = p3.button("Predict / Refresh")

predicted = None
last_close = closes.iloc[-1] if df is not None else None
days = 1

if refresh_btn and df is not None:
    # Map selection to days
    days_map = {"Next Day": 1, "7 Days": 7, "20 Days": 20, "30 Days": 30}
    days = days_map[days_option]

    # Simulate prediction with trend + random noise
    trend = np.linspace(0, 0.05, days)
    noise = np.random.normal(0, 0.01, days)
    predicted = last_close * (1 + trend + noise)

    # Determine trend for coloring
    direction = "Up 📈" if predicted[-1] > last_close else "Down 📉"
    color = "#00FF00" if direction.startswith("Up") else "#FF4136"

    # Animated Prediction Chart (glowing hover effect)
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=list(range(1, days + 1)),
        y=predicted,
        mode='lines+markers',
        line=dict(color=color, width=4),
        marker=dict(size=10, color=color, line=dict(width=2, color='white')),
        hovertemplate='Day %{x}: $%{y:.2f}<extra></extra>'
    ))
    fig_line.update_layout(
        title=f"{symbol} Predicted Price ({days_option}) {direction}",
        xaxis_title="Day",
        yaxis_title="Price",
        template="plotly_dark",
        paper_bgcolor="#0a142f",
        plot_bgcolor="#0d1b2a",
        hovermode="x unified"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Pie chart for prediction breakdown
    fig_pie = go.Figure(data=[go.Pie(
        labels=[f'Day {i+1}' for i in range(days)],
        values=predicted,
        hole=0.4,
        marker=dict(colors=[color]*days)
    )])
    fig_pie.update_layout(title=f"{symbol} Prediction Breakdown", template="plotly_dark", paper_bgcolor="#0a142f")
    st.plotly_chart(fig_pie, use_container_width=True)

# ---------------- OVERALL STOCK TABLE ----------------
if df is not None and predicted is not None:
    st.markdown("## 📋 Overall Stock Performance")
    performance_data = {
        "Metric": ["Symbol", "Dataset Size", "Latest Date", "Last Close", "Mean Price", "Std Dev", "Max Price", "Min Price", "Prediction Direction"],
        "Value": [symbol, len(df), df.iloc[-1,0], round(last_close,2), round(closes.mean(),2), round(closes.std(),2),
                  round(closes.max(),2), round(closes.min(),2), direction]
    }
    st.table(performance_data)

# ---------------- SYSTEM STATUS ----------------
st.markdown("## ⚙️ System Status")
status = "Loaded" if df is not None else "Not Loaded"
st.table({
    "Feature":["CSV Dataset","Charts","AI Prediction","Portfolio Tracker"],
    "Status":[status, "Active" if df is not None else "Inactive", "Ready" if df is not None else "Inactive", "Not Available"]
})

# ---------------- FOOTER ----------------
st.markdown('<div class="footer">© 2026 Stock Trend AI Dashboard</div>', unsafe_allow_html=True)