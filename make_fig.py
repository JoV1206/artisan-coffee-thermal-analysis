import ast
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Liberation Serif", "Times New Roman", "DejaVu Serif"]

raw = open("/mnt/user-data/uploads/CDANF_11_-_11-02-26.alog", encoding="utf-8", errors="replace").read()
d = ast.literal_eval(raw)

ti = d["timeindex"]
timex = np.array(d["timex"])
ET = np.array(d["temp1"])
BT = np.array(d["temp2"])

charge = ti[0]
t = (timex - timex[charge]) / 60.0  # minutos desde a carga

drop = ti[6]
m = (t >= 0) & (np.arange(len(t)) <= drop)
t_p, ET_p, BT_p = t[m], ET[m], BT[m]

# RoR (delta BT) em C/min, suavizado
win = 9
dBT = np.gradient(BT_p, t_p)
k = np.ones(win) / win
dBT_s = np.convolve(dBT, k, mode="same")
dBT_s[: win // 2] = np.nan
dBT_s[-(win // 2):] = np.nan

# Turning Point = minimo de BT apos a carga
tp_i = int(d["computed"]["TP_idx"]) - charge  # usa o TP calculado pelo proprio Artisan

C_BT = "#1f4e79"
C_ET = "#c00000"
C_ROR = "#4d4d4d"

fig, ax = plt.subplots(figsize=(3.4, 2.7), dpi=600)

ax.plot(t_p, BT_p, color=C_BT, lw=1.3, label="BT (grão)", zorder=3)
ax.plot(t_p, ET_p, color=C_ET, lw=1.1, label="ET (ambiente)", zorder=2)

ax.set_xlabel("Tempo desde a carga (min)", fontsize=7.5)
ax.set_ylabel("Temperatura (°C)", fontsize=7.5)
ax.set_xlim(-0.3, t_p[-1] + 0.9)
ax.set_ylim(110, 235)
ax.tick_params(labelsize=7, length=2.5, width=0.6)
ax.grid(True, ls=":", lw=0.4, color="#bbbbbb", zorder=0)
for s in ax.spines.values():
    s.set_linewidth(0.6)

ax2 = ax.twinx()
ax2.plot(t_p, dBT_s, color=C_ROR, lw=0.9, ls="--", label="RoR (ΔBT)", zorder=1)
ax2.set_ylabel("RoR (°C/min)", fontsize=7.5)
ax2.set_ylim(-4, 34)
ax2.tick_params(labelsize=7, length=2.5, width=0.6)
for s in ax2.spines.values():
    s.set_linewidth(0.6)

# eventos: (rotulo, indice em t_p, deslocamento do texto)
events = [
    ("CARGA", 0, (4, 7)),
    ("TP", tp_i, (2, -11)),
    ("FS", int(np.searchsorted(t_p, (timex[ti[1]] - timex[charge]) / 60.0)), (-16, 8)),
    ("1C", int(np.searchsorted(t_p, (timex[ti[2]] - timex[charge]) / 60.0)), (-19, -4)),
    ("F1C", int(np.searchsorted(t_p, (timex[ti[3]] - timex[charge]) / 60.0)), (-9, 9)),
    ("DESCARGA", len(t_p) - 1, (-13, 10)),
]

for lab, i, off in events:
    i = min(i, len(t_p) - 1)
    ax.plot(t_p[i], BT_p[i], "o", ms=2.6, mfc="white", mec=C_BT, mew=0.8, zorder=5)
    ax.annotate(
        lab,
        xy=(t_p[i], BT_p[i]),
        xytext=off,
        textcoords="offset points",
        fontsize=6.2,
        color="black",
        zorder=6,
    )

h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
leg = ax.legend(h1 + h2, l1 + l2, fontsize=6.3, loc="lower right", framealpha=0.95,
                borderpad=0.35, handlelength=1.8, labelspacing=0.25)
leg.get_frame().set_linewidth(0.5)

fig.tight_layout(pad=0.25)
fig.savefig("./fig1_perfil.png", dpi=600, bbox_inches="tight", facecolor="white")
print("ok")

print("TP:", round(t_p[tp_i], 2), "min", round(BT_p[tp_i], 1), "C")
for lab, i, _ in events:
    i = min(i, len(t_p) - 1)
    print(f"{lab:9s} t={t_p[i]:5.2f} min  BT={BT_p[i]:6.1f}  ET={ET_p[i]:6.1f}")
