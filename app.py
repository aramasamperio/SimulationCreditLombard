import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.title("Corrected Financial Simulation")

credit = st.sidebar.slider("Loan (€)", 50000, 200000, 105825)
monthly_invest = st.sidebar.slider("Monthly Invest (€)", 0, 2000, 500)
years = st.sidebar.slider("Years", 1, 10, 5)

tax_rate = st.sidebar.slider("Tax (%)", 0, 50, 30) / 100

interest_min = st.sidebar.slider("Min Interest (%)", 1, 10, 3)
interest_max = st.sidebar.slider("Max Interest (%)", 3, 15, 8)

return_min = st.sidebar.slider("Min Return (%)", 1, 10, 4)
return_max = st.sidebar.slider("Max Return (%)", 5, 20, 12)

interest_rates = np.linspace(interest_min/100, interest_max/100, 30)
returns = np.linspace(return_min/100, return_max/100, 30)

months = years * 12

def simulate(loan_rate, inv_rate):
    debt = credit
    inv = 0

    r_month = (1 + inv_rate)**(1/12) - 1
    loan_month = loan_rate / 12

    for _ in range(months):
        # debt grows (interest only model)
        interest_payment = debt * loan_month

        # investment grows
        inv = inv * (1 + r_month) + monthly_invest

        # optional: if you want amortization, we can extend here

    invested = monthly_invest * months
    gains = inv - invested

    taxed = gains * (1 - tax_rate)

    return invested + taxed - (credit * loan_rate * years)

X, Y = np.meshgrid(interest_rates, returns)
Z = np.zeros_like(X)

for i in range(len(returns)):
    for j in range(len(interest_rates)):
        Z[i, j] = simulate(interest_rates[j], returns[i])

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X*100, Y*100, Z)

ax.set_xlabel("Interest (%)")
ax.set_ylabel("Return (%)")
ax.set_zlabel("Net Value")

st.pyplot(fig)
