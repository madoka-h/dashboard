import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

## Data Loading
mst = pd.read_excel("dummyDataForBI.xlsx", sheet_name="施設マスタ")
data = pd.read_excel("dummyDataForBI.xlsx", sheet_name="月別患者数")
data["年"] = data["年月"].dt.year
data["年"] = data["年"].astype("str")

## Page Configurations
st.set_page_config(
    page_title = "Dashboard",
    layout = "wide",
)

st.title("Dashboard")

## Slider sample
min_date = data["年月"].min().to_pydatetime()
max_date = data["年月"].max().to_pydatetime()
result = st.slider("集計期間を指定してください。", value = (min_date, max_date), format = "YYYY-MM-DD", min_value = min_date, max_value = max_date)

## Page Contents

st.header("抽出条件")
st.write("疾患：疾患Aに罹患している")
st.write("年齢：18～65歳")
st.write("性別：男女")
st.write("治療：医薬品Xを処方されている")

# 定点データ
data_s = data[(data["年月"] >= result[0]) & (data["年月"] <= result[1])]
st.header(f"患者数平均　集計（{result[0].strftime("%Y-%m-%d")} ~ {result[1].strftime("%Y-%m-%d")}）")
col1, col2 = st.columns(2)

patientsMean = data_s.groupby("年月", as_index=False).agg({"患者数": "sum"})["患者数"].mean()
col1.metric("患者数平均", f"{round(patientsMean, 1)}人")

hospCnt = data_s["施設名"].nunique()
col2.metric("集計対象施設数", f"{hospCnt}施設")

# 患者数推移
st.header("患者数推移")
fig = px.bar(data_s, x="年月", y="患者数", color = "施設名", title="患者数推移")
st.plotly_chart(fig, use_container_width = True)

# 施設ごとの患者数
hosp = st.selectbox("施設を選択してください。", data_s["施設名"].unique())
data_h = data_s[data_s["施設名"] == hosp]

col1, col2, col3 = st.columns([1, 1, 4])
patientsMean_h = data_h["患者数"].mean()
col1.metric("患者数平均", f"{round(patientsMean_h, 1)}人")

newPatientsMean_h = data_h["新規患者数"].mean()
col2.metric("新規患者数平均（月別）", f"{round(newPatientsMean_h, 1)}人")

newPatientsYear = data_h.groupby("年", as_index = False).agg({"新規患者数": "sum"})
fig = px.bar(newPatientsYear, x="年", y="新規患者数", title=f"{hosp}の新規患者数推移(年別)")
col3.plotly_chart(fig, use_container_width = True)

fig = px.bar(data_h, x="年月", y=["新規患者数", "既存患者数"], title=f"{hosp}の患者数推移")
st.plotly_chart(fig, use_container_width = True)
