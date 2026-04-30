import numpy as np
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📊 Leveraged Investment Engine v2")

# ---------------- INPUTS ----------------
C = st.sidebar.slider("Capital / Loan (€)", 50000, 200000, 105825)

years = st.sidebar.slider("Years", 1, 10, 5)

tax = st.sidebar.slider("Tax (%)", 0, 50, 30) / 100

# NEW PARAMETER: capital growth
g = st.sidebar.slider("Capital Growth (g) (%)", 0.0, 10.0, 2.0) / 100

# RANGES
i_min = st.sidebar.slider("Min Interest (%)", 1.0, 10.0, 3.0)
i_max = st.sidebar.slider("Max Interest (%)", 3.0, 15.0, 8.0)

r_min = st.sidebar.slider("Min Return (%)", 1.0, 10.0, 4.0)
r_max = st.sidebar.slider("Max Return (%)", 5.0, 20.0, 12.0)

interest_rates = np.linspace(i_min/100, i_max/100, 40)
returns = np.linspace(r_min/100, r_max/100, 40)

# ---------------- MODEL ----------------
def simulate(i, r, g, C, years, tax):

    V = C
    annual_interest = C * i

    for _ in range(years):

        # 1. investment return
        gains = V * r
        gains_after_tax = gains * (1 - tax)

        # 2. reinvest
        V += gains_after_tax

        # 3. structural capital growth
        V += C * g

        # 4. pay interest
        V -= annual_interest

    # 5. final capital gain
    gain = max(V - C, 0)

    final_tax = gain * tax

    # 6. final repayment + tax
    net = V - C - final_tax

    return net

# ---------------- MATRIX ----------------
X, Y = np.meshgrid(interest_rates, returns)
Z = np.zeros_like(X)

for i in range(len(returns)):
    for j in range(len(interest_rates)):
        Z[i, j] = simulate(
            interest_rates[j],
            returns[i],
            C,
            g,
            years,
            tax
        )

# ---------------- 3D SURFACE ----------------
fig = go.Figure()

fig.add_trace(go.Surface(
    x=X*100,
    y=Y*100,
    z=Z,
    colorscale="RdYlGn",
    showscale=True
))

fig.update_layout(
    title="Net Value Surface (v2)",
    scene=dict(
        xaxis_title="Interest (%)",
        yaxis_title="Return (%)",
        zaxis_title="Net Value (€)"
    )
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- HEATMAP + ZERO LINE ----------------
st.subheader("Heatmap with Break-even (0 line)")

fig2 = go.Figure()

fig2.add_trace(go.Heatmap(
    z=Z,
    x=interest_rates*100,
    y=returns*100,
    colorscale="RdYlGn"
))

# ZERO CONTOUR LINE (critical fix)
fig2.add_trace(go.Contour(
    z=Z,
    x=interest_rates*100,
    y=returns*100,
    contours=dict(
        coloring="lines",
        showlabels=True,
        start=0,
        end=0
    ),
    line=dict(color="black", width=3),
    showscale=False
))

fig2.update_layout(
    xaxis_title="Interest (%)",
    yaxis_title="Return (%)"
)

st.plotly_chart(fig2, use_container_width=True)

# ---------------- STATS ----------------
st.subheader("Summary")

st.write(f"Max Value: €{np.max(Z):,.0f}")
st.write(f"Min Value: €{np.min(Z):,.0f}")
