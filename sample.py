import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import pydeck as pdk
import numpy as np

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

st.sidebar.header("データ集計期間")
result = st.sidebar.slider("集計期間を指定してください。", value = (min_date, max_date), format = "YYYY-MM-DD", min_value = min_date, max_value = max_date)

## Page Contents

st.sidebar.header("抽出条件")
st.sidebar.write("疾患：疾患Aに罹患している")
st.sidebar.write("年齢：18～65歳")
st.sidebar.write("性別：男女")
st.sidebar.write("治療：医薬品Xを処方されている")

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

# 地図

data_map = data_s[["患者数", "緯度", "経度"]].groupby(["緯度", "経度"], as_index=False).agg({"患者数": "mean"})

layer = pdk.Layer(
    "ColumnLayer",
    data = data_map,
    get_position=["経度", "緯度"],
    get_elevation = "患者数",
    radius=10000,
    elevation_scale=1000,
    get_fill_color=[180, 0, 200, 140],
    pickable=True,
    extruded=True,
)

st.pydeck_chart(
    pdk.Deck(
        map_style = None,
        initial_view_state = pdk.ViewState(
            latitude=36.047, longitude=137.5936, zoom=5, pitch=50, min_zoom=1, max_zoom=15, bearing=0
        ),
        layers = [layer]
    )
)

# 施設ごとの患者数
hosp = st.selectbox("施設を選択してください。", data_s["施設名"].unique())
data_h = data_s[data_s["施設名"] == hosp]

col = st.columns((1, 2), gap = "medium")
with col[0]:
    patientsMean_h = data_h["患者数"].mean()
    st.metric("患者数平均", f"{round(patientsMean_h, 1)}人")

    newPatientsMean_h = data_h["新規患者数"].mean()
    st.metric("新規患者数平均（月別）", f"{round(newPatientsMean_h, 1)}人")

with col[1]:
    fig = px.bar(data_h, x="年", y="新規患者数", title=f"{hosp}の患者数推移")
    st.plotly_chart(fig, use_container_width = True)

fig = px.bar(data_h, x="年月", y=["新規患者数", "既存患者数"], title=f"{hosp}の患者数推移")
st.plotly_chart(fig, use_container_width = True)