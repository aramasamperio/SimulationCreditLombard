import numpy as np
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📊 Leveraged Investment Engine v2.1")

# ---------------- INPUTS ----------------
with st.sidebar:
    st.header("Parameters")
    C = st.slider("Capital / Loan (€)", 50000, 200000, 105825)
    years = st.slider("Years", 1, 30, 5)
    tax = st.slider("Tax (%)", 0, 50, 30) / 100
    g = st.slider("Annual Capital Growth (g) (%)", 0.0, 10.0, 2.0) / 100

    st.header("Range Settings")
    i_min = st.slider("Min Interest (%)", 1.0, 10.0, 3.0)
    i_max = st.slider("Max Interest (%)", 3.0, 15.0, 8.0)
    r_min = st.slider("Min Return (%)", 1.0, 10.0, 4.0)
    r_max = st.slider("Max Return (%)", 5.0, 20.0, 12.0)

interest_rates = np.linspace(i_min/100, i_max/100, 40)
returns = np.linspace(r_min/100, r_max/100, 40)

# ---------------- REVISED MODEL ----------------
def simulate(i, r, g, C, years, tax):
    asset_value = C
    accumulated_cash = 0
    
    for _ in range(years):
        # 1. Annual Yield (Dividends/Rent/Returns)
        yearly_income = asset_value * r
        
        # 2. Interest Expense (Interest-only loan assumed)
        yearly_interest = C * i
        
        # 3. Tax on Net Yield (Income minus interest deduction)
        taxable_yield = max(0, yearly_income - yearly_interest)
        net_yearly_cash = yearly_income - yearly_interest - (taxable_yield * tax)
        
        # 4. Accumulate cash and grow capital
        accumulated_cash += net_yearly_cash
        asset_value *= (1 + g)

    # 5. Final Liquidation
    # Capital gain is the growth in asset value
    capital_gain = asset_value - C
    cap_gain_tax = max(0, capital_gain * tax)
    
    # Net = Total Assets + Cash - Loan - Tax
    net_result = (asset_value + accumulated_cash) - C - cap_gain_tax
    
    return net_result

# ---------------- MATRIX ----------------
X, Y = np.meshgrid(interest_rates, returns)
Z = np.zeros_like(X)

for row in range(len(returns)):
    for col in range(len(interest_rates)):
        # FIXED: Corrected parameter order to match function signature
        Z[row, col] = simulate(
            i = interest_rates[col],
            r = returns[row],
            g = g,
            C = C,
            years = years,
            tax = tax
        )

# ---------------- 3D SURFACE ----------------
fig = go.Figure()
fig.add_trace(go.Surface(
    x=interest_rates*100,
    y=returns*100,
    z=Z,
    colorscale="RdYlGn",
    colorbar=dict(title="Net Profit (€)")
))

fig.update_layout(
    title="Net Wealth Generated (After Loan Repayment & Tax)",
    scene=dict(
        xaxis_title="Loan Interest (%)",
        yaxis_title="Asset Return (%)",
        zaxis_title="Net Profit (€)"
    ),
    margin=dict(l=0, r=0, b=0, t=40)
)
st.plotly_chart(fig, use_container_width=True)

# ---------------- HEATMAP + ZERO LINE ----------------
st.subheader("Profitability Heatmap (Break-even Analysis)")

fig2 = go.Figure()
fig2.add_trace(go.Heatmap(
    z=Z,
    x=interest_rates*100,
    y=returns*100,
    colorscale="RdYlGn",
    zmid=0
))

# ZERO CONTOUR LINE (The "Break-even" boundary)
fig2.add_trace(go.Contour(
    z=Z,
    x=interest_rates*100,
    y=returns*100,
    contours=dict(coloring="lines", showlabels=True, start=0, end=0),
    line=dict(color="black", width=4),
    showscale=False
))

fig2.update_layout(
    xaxis_title="Loan Interest Rate (%)",
    yaxis_title="Asset Return Rate (%)"
)
st.plotly_chart(fig2, use_container_width=True)

# ---------------- STATS ----------------
col1, col2, col3 = st.columns(3)
col1.metric("Max Potential Profit", f"€{np.max(Z):,.0f}")
col2.metric("Min Potential Profit", f"€{np.min(Z):,.0f}")
col3.metric("Break-even Return", f"~{returns[np.argmin(np.abs(Z[:, 0]))]*100:.2f}%", help="At the lowest interest rate")
