import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "META", "JPM", "BAC", "GS", "XOM", "CVX", "WMT", "COST", "JNJ","PFE", "CAT", "BA", "TSLA", "AMZN", "SPY", "QQQ"]

start_date = "2018-01-01"
window = 60

data = yf.download(tickers, start=start_date, auto_adjust=True)
prices = data["Close"]

returns = np.log(prices / prices.shift(1)).dropna()

dates = []
collapse_scores = []
max_eigs = []
corr_matrices = []

for i in range(window, len(returns)):
    window_data = returns.iloc[i-window:i]
    corr = window_data.corr().values

    n = corr.shape[0]
    mask = np.ones((n, n), dtype=bool)
    np.fill_diagonal(mask, False)

    collapse_score = np.mean(np.abs(corr[mask]))
    eigvals = np.linalg.eigvalsh(corr)
    max_eig = eigvals[-1]

    dates.append(returns.index[i])
    collapse_scores.append(collapse_score)
    max_eigs.append(max_eig)
    corr_matrices.append(corr)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(dates, collapse_scores)

ax.axhline(0.35, linestyle="--")
ax.axhline(0.50, linestyle="--")
ax.axhline(0.70, linestyle="--")

ax.set_title("Correlation Collapse Score Over Time")
ax.set_xlabel("Date")
ax.set_ylabel("Avg Absolute Correlation")
fig.tight_layout()
fig.savefig("collapse_score.png")

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(dates, max_eigs)

ax.set_title("Largest Eigenvalue of Correlation Matrix")
ax.set_xlabel("Date")
ax.set_ylabel("Eigenvalue")
fig.tight_layout()
fig.savefig("eigenvalue.png")

min_idx = np.argmin(collapse_scores)
max_idx = np.argmax(collapse_scores)

calm_corr = corr_matrices[min_idx]
stress_corr = corr_matrices[max_idx]

labels = list(returns.columns)

def plot_heatmap(corr, title, filename):
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(corr, vmin=-1, vmax=1)
    fig.colorbar(im)

    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=90)
    ax.set_yticklabels(labels)

    ax.set_title(title)

    fig.tight_layout()
    fig.savefig(filename)

plot_heatmap(calm_corr, "Calm Market Correlation", "calm.png")
plot_heatmap(stress_corr, "Stress Market Correlation", "stress.png")

future_vol = returns.rolling(10).std().shift(-10).mean(axis=1)

aligned_scores = collapse_scores[:-10]
aligned_vol = future_vol.iloc[window:-10]

fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(aligned_scores, aligned_vol)

ax.set_xlabel("Collapse Score")
ax.set_ylabel("Future Volatility")
ax.set_title("Does Correlation Predict Risk?")

fig.tight_layout()
fig.savefig("prediction.png")

print("All outputs generated.")
print("Max collapse date:", dates[max_idx])
print("Min collapse date:", dates[min_idx])


