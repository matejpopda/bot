import numpy as np
import d20

import seaborn as sns
import matplotlib.pyplot as plt
import io
import discord


def simulate_roll(dice_notation, cumulative_plot, rolls=10000):

    results = np.array([d20.roll(dice_notation).total for _ in range(rolls)])

    totals = np.arange(results.min(), results.max() + 1)
    counts = np.array([np.sum(results == t) for t in totals])
    pdf = counts / counts.sum()

    avg = float(np.mean(results))
    mode = float(np.median(results))
    variance = float(np.var(results))

    plt.figure(figsize=(6, 4))

    if cumulative_plot == True:
        cdf = np.cumsum(pdf)
        plt.bar(totals, cdf)
    else:
        plt.bar(totals, pdf)

    # Use the plt.legend in order to write out avg, mode and mean
    plt.axvline(avg, color=(0, 0, 0, 0), linestyle="--", label=f"Mean = {avg:.2f}")
    plt.axvline(mode, color=(0, 0, 0, 0), linestyle="--", label=f"Mode = {mode:.2f}")
    plt.axvline(
        variance, color=(0, 0, 0, 0), linestyle="--", label=f"Variance = {variance:.2f}"
    )
    plt.legend(markerfirst=False, markerscale=0, handlelength=0)

    plt.title(f"{dice_notation} — {rolls:,} rolls")
    plt.xlabel("Roll Result")
    plt.ylabel("Probability")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=200)
    buf.seek(0)
    plt.close()
    file = discord.File(buf, filename="histogram.png")
    return file
