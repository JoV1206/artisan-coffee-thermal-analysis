import ast, glob, re, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

BASE = "./dados"

# ---------------- carregar planilha (CSV = fonte integra) ----------------
csv = glob.glob(f"{BASE}/**/*.csv", recursive=True)[0]
meta = pd.read_csv(csv)
meta.columns = [c.strip() for c in meta.columns]
meta["Altitude"] = meta["Altitude"].astype(str).str.replace(",", ".").astype(float)
meta["key"] = meta["Código"].str.strip()

# ---------------- carregar .alog ----------------
def key_from_name(fn):
    m = re.search(r"CDANF\s*(\d+)", fn)
    return f"CDANF{int(m.group(1)):02d}" if m else None

recs = {}
for f in sorted(glob.glob(f"{BASE}/**/*.alog", recursive=True)):
    d = ast.literal_eval(open(f, encoding="utf-8", errors="replace").read())
    k = key_from_name(f.split("/")[-1])
    ti, tx = d["timeindex"], np.array(d["timex"])
    ch = ti[0]
    valid = (ch is not None and ch >= 0 and ti[2] > 0 and ti[6] > 0 and ti[2] > ch and ti[6] > ti[2])
    recs[k] = dict(
        key=k, file=f, d=d, ti=ti, tx=tx, ch=ch, valid=valid,
        ET=np.array(d["temp1"]), BT=np.array(d["temp2"]),
        fcs_s=(tx[ti[2]] - tx[ch]) if valid else np.nan,
        drop_s=(tx[ti[6]] - tx[ch]) if valid else np.nan,
        dry_s=(tx[ti[1]] - tx[ch]) if valid and ti[1] > ch else np.nan,
    )

good = [r for r in recs.values() if r["valid"]]
bad = [r for r in recs.values() if not r["valid"]]
print(f"perfis: {len(recs)} | validos: {len(good)} | invalidos: {len(bad)}")
for r in bad:
    print("   EXCLUIR:", r["file"].split("/")[-1], "timeindex:", r["ti"])

# ---------------- reamostragem em grade comum ----------------
GRID = np.arange(0, 12.01, 0.05)  # min

def curve(r):
    t = (r["tx"] - r["tx"][r["ch"]]) / 60.0
    m = (t >= 0) & (np.arange(len(t)) <= r["ti"][6])
    return np.interp(GRID, t[m], r["BT"][m], left=np.nan, right=np.nan)

M = np.vstack([curve(r) for r in good])
print("matriz de curvas:", M.shape)

np.save("./curves.npy", M)
np.save("./grid.npy", GRID)

# ---------------- tabela de eventos ----------------
ev = pd.DataFrame([{k: r[k] for k in ("key", "dry_s", "fcs_s", "drop_s")} for r in good])
df = ev.merge(meta, on="key", how="left", validate="one_to_one")
print("\nmerge:", df.shape, "| sem metadado:", df["Cidade"].isna().sum())
df.to_csv("./analise.csv", index=False)

print("\n=== ESTATISTICAS DE CONSISTENCIA (o que o parecer exige) ===")
for c, lab in [("dry_s", "Fim da secagem"), ("fcs_s", "Primeiro estalo (FC)"), ("drop_s", "Descarga")]:
    s = df[c].dropna()
    print(f"  {lab:22s} media {s.mean():6.1f} s | DP {s.std():5.1f} s | CV {100*s.std()/s.mean():4.1f}% | faixa {s.min():.0f}-{s.max():.0f} s")

# envelope de dispersao
with np.errstate(all="ignore"):
    p50 = np.nanmedian(M, axis=0)
    p10 = np.nanpercentile(M, 10, axis=0)
    p90 = np.nanpercentile(M, 90, axis=0)
band = p90 - p10
sel = (~np.isnan(band)) & (GRID <= 8)
print(f"\n  Largura mediana da banda P10-P90 (0-8 min): {np.nanmedian(band[sel]):.1f} C")
