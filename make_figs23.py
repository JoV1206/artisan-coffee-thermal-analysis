import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Liberation Serif", "Times New Roman", "DejaVu Serif"]

M = np.load("./curves.npy")
G = np.load("./grid.npy")
D = pd.read_csv("./analise.csv")

C_BT = "#1f4e79"; C_ACC = "#c00000"

# ---------------- Fig 2: overlay + envelope ----------------
fig, ax = plt.subplots(figsize=(3.4, 2.5), dpi=600)
for i in range(M.shape[0]):
    ax.plot(G, M[i], color=C_BT, lw=0.35, alpha=0.30, zorder=2)
with np.errstate(all="ignore"):
    p10 = np.nanpercentile(M, 10, axis=0)
    p50 = np.nanmedian(M, axis=0)
    p90 = np.nanpercentile(M, 90, axis=0)
ok = ~np.isnan(p50)
ax.fill_between(G[ok], p10[ok], p90[ok], color=C_ACC, alpha=0.16, lw=0, zorder=3,
                label="Envelope P10–P90")
ax.plot(G[ok], p50[ok], color=C_ACC, lw=1.3, zorder=4, label="Mediana")

fc = D["fcs_s"].dropna() / 60
ax.axvspan(fc.min(), fc.max(), color="#888888", alpha=0.13, lw=0, zorder=1)
ax.annotate(f"faixa do FC\n{fc.min():.1f}–{fc.max():.1f} min", xy=(fc.mean(), 133),
            ha="center", fontsize=5.6, color="#333333", zorder=6)

ax.set_xlabel("Tempo desde a carga (min)", fontsize=7.5)
ax.set_ylabel("BT — temperatura do grão (°C)", fontsize=7.5)
ax.set_xlim(0, 12); ax.set_ylim(120, 225)
ax.tick_params(labelsize=7, length=2.5, width=0.6)
ax.grid(True, ls=":", lw=0.4, color="#bbbbbb", zorder=0)
for s in ax.spines.values(): s.set_linewidth(0.6)
leg = ax.legend(fontsize=6.2, loc="lower right", framealpha=0.95, borderpad=0.35,
                handlelength=1.7, labelspacing=0.25)
leg.get_frame().set_linewidth(0.5)
fig.tight_layout(pad=0.25)
fig.savefig("./fig2_overlay.png", dpi=600, bbox_inches="tight", facecolor="white")

# ---------------- Fig 3: metadados ----------------
fig, axs = plt.subplots(1, 3, figsize=(7.0, 1.95), dpi=600)

axs[0].hist(D["Altitude"], bins=10, color=C_BT, alpha=0.8, edgecolor="white", lw=0.4)
axs[0].set_xlabel("Altitude da lavoura (m)", fontsize=7)
axs[0].set_ylabel("Nº de lotes", fontsize=7)

axs[1].hist(D["massa_grao"], bins=10, color=C_BT, alpha=0.8, edgecolor="white", lw=0.4)
axs[1].set_xlabel("Massa de grão verde (g)", fontsize=7)
axs[1].set_ylabel("Nº de lotes", fontsize=7)

cats = D["Variedade"].unique()
mk = {cats[0]: ("o", C_BT), cats[1]: ("^", C_ACC)}
for c in cats:
    s = D[D["Variedade"] == c]
    axs[2].scatter(s["temp_amb"], s["umid_amb"], s=13, marker=mk[c][0],
                   facecolor="none", edgecolor=mk[c][1], lw=0.7, label=c)
axs[2].set_xlabel("Temp. ambiente na carga (°C)", fontsize=7)
axs[2].set_ylabel("Umidade relativa (fração)", fontsize=7)
lg = axs[2].legend(fontsize=5.6, loc="upper right", framealpha=0.95, borderpad=0.3,
                   handletextpad=0.3)
lg.get_frame().set_linewidth(0.5)

for a in axs:
    a.tick_params(labelsize=6.5, length=2.2, width=0.5)
    a.grid(True, ls=":", lw=0.35, color="#c8c8c8")
    a.set_axisbelow(True)
    for s in a.spines.values(): s.set_linewidth(0.55)

fig.tight_layout(pad=0.3, w_pad=1.3)
fig.savefig("./fig3_metadados.png", dpi=600, bbox_inches="tight", facecolor="white")
print("figuras ok")

print("\n=== dados p/ legendas ===")
print(f"n curvas: {M.shape[0]}")
print(f"FC: {fc.min():.2f}-{fc.max():.2f} min")
print(f"Altitude: {D['Altitude'].min():.0f}-{D['Altitude'].max():.0f} m")
print(f"massa: {D['massa_grao'].min():.0f}-{D['massa_grao'].max():.0f} g")
print(f"temp_amb: {D['temp_amb'].min():.1f}-{D['temp_amb'].max():.1f} C")
print(f"umid_amb: {D['umid_amb'].min():.2f}-{D['umid_amb'].max():.2f}")
print(D["Variedade"].value_counts().to_string())
print(D["Cidade"].value_counts().to_string())
