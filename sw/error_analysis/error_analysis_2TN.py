import numpy as np
import pandas as pd
import csv

# =========================================
# READ ADDER STATISTICS FROM CSV
# =========================================
df = pd.read_csv("adder_stats.csv")
mu    = df["mean_gamma"][0]
sigma = df["std_gamma"][0]

print(f"Loaded gamma stats: mean={mu}, std={sigma}")

# =========================================
# CORDIC MONTE-CARLO SIMULATION
# =========================================
MC = 200_000
rng = np.random.default_rng(123456)

with open("cordic_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["K", "MeanE", "StdE", "Emin", "Emax"])

    for K in range(4, 17):
        alphas = np.array([2.0 ** (-i) for i in range(K)])

        gamma = rng.normal(mu, sigma, size=(MC, K))
        signs = rng.choice([-1, 1], size=(MC, K))

        E = np.sum(alphas * gamma * signs, axis=1)

        meanE = E.mean()
        stdE  = E.std()
        Emin  = E.min()
        Emax  = E.max()

        print(f"K={K:2d} Mean(E)={meanE:.6e} Std(E)={stdE:.6e}")

        writer.writerow([K, meanE, stdE, Emin, Emax])

print("Saved results.csv")
