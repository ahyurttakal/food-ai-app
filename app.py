import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Akıllı Et Raf Ömrü Tahmin Sistemi",
    page_icon="🥩",
    layout="wide"
)

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }
.title-box {
    padding: 22px;
    border-radius: 18px;
    background: linear-gradient(90deg, #7f1d1d, #dc2626);
    color: black;
    margin-bottom: 20px;
}
.info-card {
    padding: 18px;
    border-radius: 16px;
    background-color: white;
    color: #111827;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    min-height: 130px;
}

.info-card h4 {
    color: #111827;
}

.info-card p {
    color: #374151;
}
.metric-card {
    padding: 20px;
    border-radius: 18px;
    background-color: white;
    border-left: 8px solid #dc2626;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
.metric-label { font-size: 15px; color: #6b7280; }
.metric-value { font-size: 32px; font-weight: 800; color: #111827; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-box">
    <h1>🥩 Akıllı Et Raf Ömrü Tahmin Paneli</h1>
    <p>Sıcaklık ve mikrobiyal büyüme verisine göre bozulma riski, kalan raf ömrü ve risk/güven skoru hesaplanır.</p>
</div>
""", unsafe_allow_html=True)

st.subheader("📌 Panelde Gösterilen 3 Ana Çıktı")
i1, i2, i3 = st.columns(3)

with i1:
    st.markdown("""
    <div class="info-card">
        <h4>⏳ Bozulmaya Kalan Gün</h4>
        <p><b>Tahmini Kalan Gün</b></p>
        <p>Ürünün tahmini olarak kaç gün daha güvenli kalabileceğini gösterir.</p>
    </div>
    """, unsafe_allow_html=True)

with i2:
    st.markdown("""
    <div class="info-card">
        <h4>🚨 Risk Seviyesi</h4>
        <p><b>Düşük / Orta / Yüksek / Kritik</b></p>
        <p>Ürünün satış, sevkiyat veya kalite kontrol açısından risk durumunu gösterir.</p>
    </div>
    """, unsafe_allow_html=True)

with i3:
    st.markdown("""
    <div class="info-card">
        <h4>📊 Risk Skoru</h4>
        <p><b>0 = güvenli, 1 = yüksek risk</b></p>
        <p>Teknik karar desteği için kullanılan sayısal risk göstergesidir.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

uploaded_file = st.file_uploader("📤 Excel dosyasını yükle", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("Analiz için Excel dosyasını yükleyiniz.")
    st.stop()

df = pd.read_excel(uploaded_file)

required_cols = ["Sample_ID", "Temperature_C", "Day", "Total_Viable_Count"]
missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"Eksik kolonlar: {missing}")
    st.stop()

df = df.copy()
df = df.sort_values(["Sample_ID", "Temperature_C", "Day"]).reset_index(drop=True)

st.sidebar.header("⚙️ Ayarlar")

threshold = st.sidebar.slider(
    "Bozulma eşiği - Total Viable Count",
    min_value=5.0,
    max_value=9.0,
    value=7.0,
    step=0.1
)

low_risk_days = st.sidebar.slider(
    "Düşük risk için minimum kalan gün",
    min_value=1.0,
    max_value=10.0,
    value=4.0,
    step=0.5
)

high_risk_days = st.sidebar.slider(
    "Yüksek risk için maksimum kalan gün",
    min_value=0.0,
    max_value=5.0,
    value=1.5,
    step=0.5
)

shelf_life = []

for _, g in df.groupby(["Sample_ID", "Temperature_C"]):
    g = g.sort_values("Day")
    spoil = g[g["Total_Viable_Count"] >= threshold]["Day"]

    if len(spoil) > 0:
        spoil_day = float(spoil.iloc[0])
    else:
        spoil_day = float(g["Day"].max() + 1)

    for d in g["Day"]:
        shelf_life.append(spoil_day - float(d))

df["true_shelf_life"] = shelf_life
df["spoiled_now"] = (df["Total_Viable_Count"] >= threshold).astype(int)

feature_cols = ["Temperature_C", "Day", "Total_Viable_Count"]

X = df[feature_cols].values
y = df["true_shelf_life"].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = Ridge(alpha=1.0)
model.fit(X_scaled, y)

df["pred_shelf_life"] = model.predict(X_scaled)
df["pred_shelf_life"] = df["pred_shelf_life"].clip(0)

denom = max(low_risk_days - high_risk_days, 1e-6)
df["risk_score"] = 1 - ((df["pred_shelf_life"] - high_risk_days) / denom)
df["risk_score"] = df["risk_score"].clip(0, 1)

def risk_level(row):
    if row["spoiled_now"] == 1:
        return "🔴 Bozulmuş / Kritik"
    if row["pred_shelf_life"] <= high_risk_days:
        return "🔴 Yüksek Risk"
    elif row["pred_shelf_life"] <= low_risk_days:
        return "🟡 Orta Risk"
    return "🟢 Düşük Risk"

df["risk_level"] = df.apply(risk_level, axis=1)

def decision_text(row):
    if "Bozulmuş" in row["risk_level"]:
        return "Satıştan çek / kalite kontrol"
    if "Yüksek" in row["risk_level"]:
        return "Öncelikli tüketim / sevkiyat uyarısı"
    if "Orta" in row["risk_level"]:
        return "Yakından takip et"
    return "Normal"

df["recommended_action"] = df.apply(decision_text, axis=1)

total_rows = len(df)
avg_shelf = df["pred_shelf_life"].mean()
high_risk_count = df["risk_level"].str.contains("Yüksek|Kritik|Bozulmuş").sum()
avg_risk = df["risk_score"].mean()

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Toplam Kayıt</div>
        <div class="metric-value">{total_rows}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Ortalama Kalan Gün</div>
        <div class="metric-value">{avg_shelf:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Yüksek/Kritik Riskli</div>
        <div class="metric-value">{high_risk_count}</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Ortalama Risk Skoru</div>
        <div class="metric-value">{avg_risk:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.subheader("🔎 Filtreler")

f1, f2, f3 = st.columns(3)

with f1:
    samples = sorted(df["Sample_ID"].unique())
    selected_sample = st.selectbox("Numune seç", options=["Tümü"] + list(samples))

with f2:
    temps = sorted(df["Temperature_C"].unique())
    selected_temp = st.selectbox("Sıcaklık seç", options=["Tümü"] + list(temps))

with f3:
    risk_options = ["Tümü"] + sorted(df["risk_level"].unique())
    selected_risk = st.selectbox("Risk seviyesi seç", options=risk_options)

filtered = df.copy()

if selected_sample != "Tümü":
    filtered = filtered[filtered["Sample_ID"] == selected_sample]

if selected_temp != "Tümü":
    filtered = filtered[filtered["Temperature_C"] == selected_temp]

if selected_risk != "Tümü":
    filtered = filtered[filtered["risk_level"] == selected_risk]

st.subheader("📋 Ürün Karar Tablosu")

result = filtered[[
    "Sample_ID",
    "Temperature_C",
    "Day",
    "Total_Viable_Count",
    "pred_shelf_life",
    "risk_score",
    "risk_level",
    "recommended_action"
]].copy()

result = result.rename(columns={
    "Sample_ID": "Numune",
    "Temperature_C": "Sıcaklık (°C)",
    "Day": "Gün",
    "Total_Viable_Count": "Mikrobiyal Yük",
    "pred_shelf_life": "Tahmini Kalan Gün",
    "risk_score": "Risk Skoru",
    "risk_level": "Risk Seviyesi",
    "recommended_action": "Önerilen Aksiyon"
})

def color_risk(val):
    val = str(val)
    if "Düşük" in val:
        return "background-color: #dcfce7; color: #166534; font-weight: bold;"
    if "Orta" in val:
        return "background-color: #fef9c3; color: #854d0e; font-weight: bold;"
    if "Yüksek" in val or "Kritik" in val or "Bozulmuş" in val:
        return "background-color: #fee2e2; color: #991b1b; font-weight: bold;"
    return ""

styled = result.style.map(color_risk, subset=["Risk Seviyesi"]).format({
    "Mikrobiyal Yük": "{:.2f}",
    "Tahmini Kalan Gün": "{:.2f}",
    "Risk Skoru": "{:.2f}"
})

st.dataframe(styled, use_container_width=True, height=420)

st.subheader("📈 Görsel Analiz")

c1, c2 = st.columns(2)

with c1:
    risk_counts = df["risk_level"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(risk_counts.index.astype(str), risk_counts.values)
    ax.set_title("Risk Seviyesi Dağılımı")
    ax.set_ylabel("Kayıt Sayısı")
    ax.tick_params(axis="x", rotation=25)
    st.pyplot(fig)

with c2:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(df["Temperature_C"], df["pred_shelf_life"], alpha=0.55)
    ax.set_title("Sıcaklık - Tahmini Kalan Gün")
    ax.set_xlabel("Sıcaklık (°C)")
    ax.set_ylabel("Tahmini Kalan Gün")
    st.pyplot(fig)

st.subheader("🧪 Numune Bazlı Raf Ömrü Eğrisi")

sample_for_plot = st.selectbox(
    "Grafik için numune seç",
    options=sorted(df["Sample_ID"].unique()),
    key="plot_sample"
)

plot_df = df[df["Sample_ID"] == sample_for_plot].copy()

fig, ax1 = plt.subplots(figsize=(10, 4.8))

for temp, g in plot_df.groupby("Temperature_C"):
    g = g.sort_values("Day")
    ax1.plot(g["Day"], g["pred_shelf_life"], marker="o", label=f"{temp}°C")

ax1.set_title(f"Numune {sample_for_plot} - Tahmini Kalan Raf Ömrü")
ax1.set_xlabel("Gün")
ax1.set_ylabel("Tahmini Kalan Gün")
ax1.legend(title="Sıcaklık")
st.pyplot(fig)

st.subheader("📥 Sonuçları İndir")

download_df = result.copy()
csv = download_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="📥 Panel sonucunu CSV olarak indir",
    data=csv,
    file_name="raf_omru_risk_sonuclari.csv",
    mime="text/csv"
)

st.markdown("""
---
### 🧠 Sistem Mantığı

- **Tahmini Kalan Gün:** Model tarafından tahmin edilir.
- **Risk Skoru:** Tahmini kalan gün azaldıkça 1'e yaklaşır.
- **Risk Seviyesi:** Risk skoru ve mikrobiyal eşik değerine göre otomatik atanır.
- **Önerilen Aksiyon:** Ticari karar desteği için üretilir.

Bu panel bir MVP ürün çekirdeğidir. Gerçek saha kullanımı için sensör entegrasyonu, daha fazla gerçek veri ve validasyon önerilir.
""")
