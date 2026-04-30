import numpy as np
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📊 Leveraged Investment Simulator (Fixed Model)")

# ---------------- INPUTS ----------------
credit = st.sidebar.slider("Loan (€)", 50000, 200000, 105825)

years = st.sidebar.slider("Years", 1, 10, 5)

tax_rate = st.sidebar.slider("Tax (%)", 0, 50, 30) / 100

interest_min = st.sidebar.slider("Min Interest (%)", 1, 10, 3)
interest_max = st.sidebar.slider("Max Interest (%)", 3, 15, 8)

return_min = st.sidebar.slider("Min Return (%)", 1, 10, 4)
return_max = st.sidebar.slider("Max Return (%)", 5, 20, 12)

# grids
interest_rates = np.linspace(interest_min/100, interest_max/100, 40)
returns = np.linspace(return_min/100, return_max/100, 40)

# ---------------- MODEL ----------------
import numpy as np

def simulate(loan, r, i, tax, years=5):

    value = loan
    total_interest = 0

    for _ in range(years):

        # investment grows
        value = value * (1 + r)

        # interest paid on loan (balloon structure → interest only yearly)
        interest_payment = loan * i
        total_interest += interest_payment

    # capital gain
    gain = value - loan

    tax_paid = max(gain, 0) * tax

    net = value - total_interest - tax_paid - loan

    return net

# ---------------- MATRIX ----------------
X, Y = np.meshgrid(interest_rates, returns)
Z = np.zeros_like(X)

for i in range(len(returns)):
    for j in range(len(interest_rates)):

        val = simulate(interest_rates[j], returns[i])

        if val is None:
            st.error(f"simulate returned None at i={i}, j={j}")
            val = 0   # fallback so app doesn't crash

        Z[i, j] = val

# ---------------- BREAK-EVEN CURVE ----------------
breakeven = []

for r in returns:
    row = []
    for j in range(len(interest_rates)):
        val = simulate(interest_rates[j], r)
        row.append(val)
    row = np.array(row)

    # find closest zero crossing
    idx = np.argmin(np.abs(row))
    breakeven.append(interest_rates[idx] * 100)

# ---------------- 3D PLOT (INTERACTIVE) ----------------
fig = go.Figure()

fig.add_trace(go.Surface(
    x=X*100,
    y=Y*100,
    z=Z,
    colorscale=[
        [0, "red"],
        [0.5, "white"],
        [1, "green"]
    ],
    opacity=0.9
))

fig.update_layout(
    title="Net Value Surface (Interactive)",
    scene=dict(
        xaxis_title="Interest Rate (%)",
        yaxis_title="Return (%)",
        zaxis_title="Net Value (€)"
    )
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- HEATMAP ----------------
st.subheader("Heatmap View")

fig2 = go.Figure(data=go.Heatmap(
    z=Z,
    x=interest_rates*100,
    y=returns*100,
    colorscale="RdYlGn"
))

fig2.update_layout(
    xaxis_title="Interest (%)",
    yaxis_title="Return (%)"
)

st.plotly_chart(fig2, use_container_width=True)

# ---------------- BREAKEVEN CURVE ----------------
st.subheader("Break-even Curve")

st.line_chart({
    "Breakeven Interest (%)": breakeven
})

# ---------------- STATS ----------------
st.subheader("Summary")

st.write(f"Max Profit: €{np.max(Z):,.0f}")
st.write(f"Min Profit: €{np.min(Z):,.0f}")
