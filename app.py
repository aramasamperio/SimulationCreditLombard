import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Investment Simulator", layout="wide")

st.title("📊 Investment vs Debt Simulation")

# --- SIDEBAR ---
st.sidebar.header("Inputs")

credit = st.sidebar.slider("Loan Amount (€)", 50000, 200000, 105825)
monthly_invest = st.sidebar.slider("Monthly Investment (€)", 0, 2000, 500)
years = st.sidebar.slider("Years", 1, 10, 5)
tax_rate = st.sidebar.slider("Tax Rate (%)", 0, 50, 30) / 100

st.sidebar.subheader("Simulation Range")

interest_min = st.sidebar.slider("Min Interest (%)", 0.5, 10.0, 1.0)
interest_max = st.sidebar.slider("Max Interest (%)", 1.0, 15.0, 8.0)

return_min = st.sidebar.slider("Min Return (%)", 1.0, 10.0, 2.0)
return_max = st.sidebar.slider("Max Return (%)", 2.0, 20.0, 12.0)

interest_rates = np.linspace(interest_min/100, interest_max/100, 30)
returns = np.linspace(return_min/100, return_max/100, 30)

def future_value(rate, nper, pmt):
    if abs(rate) < 1e-6:
        return pmt * nper
    return pmt * ((1 + rate)**nper - 1) / rate

X, Y = np.meshgrid(interest_rates, returns)
Z = np.zeros_like(X)

n = years * 12

for i in range(len(returns)):
    for j in range(len(interest_rates)):
        annual_return = returns[i]
        annual_interest = interest_rates[j]

        r_inv = (1 + annual_return)**(1/12) - 1

        fv = future_value(r_inv, n, monthly_invest)

        invested = monthly_invest * n
        gains = fv - invested
        net_fv = invested + gains * (1 - tax_rate)

        total_interest = credit * annual_interest * years

        Z[i, j] = net_fv - total_interest

# --- PLOTS ---
st.subheader("3D Surface")

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X*100, Y*100, Z)

ax.set_xlabel("Interest (%)")
ax.set_ylabel("Return (%)")
ax.set_zlabel("Net Profit (€)")

st.pyplot(fig)

st.subheader("Heatmap")

fig2, ax2 = plt.subplots()
c = ax2.imshow(Z, extent=[interest_min, interest_max, return_min, return_max], origin='lower', aspect='auto')

ax2.set_xlabel("Interest (%)")
ax2.set_ylabel("Return (%)")

fig2.colorbar(c)

st.pyplot(fig2)

st.subheader("Results")
st.write(f"Max Profit: €{np.max(Z):,.0f}")
st.write(f"Worst Case: €{np.min(Z):,.0f}")
