import ast, glob, re, warnings
import numpy as np, pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import RidgeCV
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
BASE = "./dados"
CUT = 4.0  # minutos de observacao disponiveis ao preditor

csv = glob.glob(f"{BASE}/**/*.csv", recursive=True)[0]
meta = pd.read_csv(csv)
meta.columns = [c.strip() for c in meta.columns]
meta["Altitude"] = meta["Altitude"].astype(str).str.replace(",", ".").astype(float)
meta["key"] = meta["Código"].str.strip()

def key_from_name(fn):
    m = re.search(r"CDANF\s*(\d+)", fn)
    return f"CDANF{int(m.group(1)):02d}" if m else None

rows = []
for f in sorted(glob.glob(f"{BASE}/**/*.alog", recursive=True)):
    d = ast.literal_eval(open(f, encoding="utf-8", errors="replace").read())
    ti, tx = d["timeindex"], np.array(d["timex"])
    ch = ti[0]
    if not (ch is not None and ch >= 0 and ti[2] > ch and ti[6] > ti[2]):
        continue
    t = (tx - tx[ch]) / 60.0
    BT, ET = np.array(d["temp2"]), np.array(d["temp1"])
    m = (t >= 0) & (np.arange(len(t)) <= ti[6])
    t, BT, ET = t[m], BT[m], ET[m]

    w = t <= CUT
    tw, BTw, ETw = t[w], BT[w], ET[w]
    if tw[-1] < CUT - 0.2:
        continue

    tp_i = int(np.argmin(BTw))
    ror = np.gradient(BTw, tw)

    feat = dict(
        key=key_from_name(f.split("/")[-1]),
        bt_charge=BT[0],
        tp_time=tw[tp_i] * 60,
        tp_bt=BTw[tp_i],
        bt_1=np.interp(1.0, tw, BTw), bt_2=np.interp(2.0, tw, BTw),
        bt_3=np.interp(3.0, tw, BTw), bt_4=np.interp(4.0, tw, BTw),
        et_4=np.interp(4.0, tw, ETw),
        ror_2_4=np.nanmean(ror[(tw >= 2) & (tw <= 4)]),
        ror_max=np.nanmax(ror[tw > tw[tp_i]]) if (tw > tw[tp_i]).any() else np.nan,
        slope_tp_4=(np.interp(4.0, tw, BTw) - BTw[tp_i]) / max(4.0 - tw[tp_i], 1e-6),
        y=(tx[ti[2]] - tx[ch]),  # alvo: instante do FC em s
    )
    rows.append(feat)

D = pd.DataFrame(rows).merge(meta, on="key", how="left", validate="one_to_one")
print(f"amostras: {len(D)}")

sig = ["bt_charge", "tp_time", "tp_bt", "bt_1", "bt_2", "bt_3", "bt_4", "et_4",
       "ror_2_4", "ror_max", "slope_tp_4"]
md = ["massa_grao", "temp_amb", "umid_amb", "Altitude"]
D["is_catuai"] = (D["Variedade"].str.contains("Catuaí Vermelho")).astype(int)

y = D["y"].values
loo = LeaveOneOut()

def ev(name, X, model):
    p = cross_val_predict(model, X, y, cv=loo)
    mae = np.mean(np.abs(p - y)); rmse = np.sqrt(np.mean((p - y) ** 2))
    ss = 1 - np.sum((p - y) ** 2) / np.sum((y - y.mean()) ** 2)
    print(f"  {name:34s} MAE {mae:5.1f} s | RMSE {rmse:5.1f} s | R2 {ss:6.3f}")
    return mae

print(f"\nAlvo: instante do FC | media {y.mean():.1f} s | DP {y.std(ddof=1):.1f} s")
print(f"Observacao disponivel ao preditor: primeiros {CUT:.0f} min\n")

ev("Baseline trivial (media)", D[sig].values, DummyRegressor(strategy="mean"))
ev("Ridge - sinal", D[sig].values, make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-2, 3, 30))))
ev("Ridge - sinal + metadados", D[sig + md + ["is_catuai"]].values,
   make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-2, 3, 30))))
gb = lambda: GradientBoostingRegressor(n_estimators=200, max_depth=2, learning_rate=0.05, random_state=0)
ev("Gradient boosting - sinal", D[sig].values, gb())
mae_gb = ev("Gradient boosting - sinal + metadados", D[sig + md + ["is_catuai"]].values, gb())

D.to_csv("./baseline_features.csv", index=False)
