import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

st.title("영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 10위권 데이터를 이용해 영화의 시간에 따른 관객 변화를 살펴봅니다.")

# ─────────────────────────────────────────────
# 데이터 불러오기 및 전처리
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜 열을 실제 날짜형으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")

    # 숫자형 열 정리
    numeric_cols = ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
    st.stop()


# ─────────────────────────────────────────────
# 그래프 1. 영화별 일관객 변화
# ─────────────────────────────────────────────
st.header("그래프 1. 영화별 일관객 변화")

movie_list = (
    df["영화명"]
    .dropna()
    .drop_duplicates()
    .sort_values()
    .tolist()
)

selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_list,
    index=0,
)

movie_df = (
    df[df["영화명"] == selected_movie]
    .sort_values("날짜")
    .copy()
)

fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"〈{selected_movie}〉 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
    },
    hover_data={
        "날짜": "|%Y-%m-%d",
        "일관객": ":,",
    },
)

fig.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
)

fig.update_layout(
    hovermode="x unified",
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.info("여기에 이 그래프를 통해 알 수 있는 내용을 한 문장으로 적어 주세요.")


# ─────────────────────────────────────────────
# 그래프 2. 일관객 합계 TOP 5 영화의 날짜별 변화
# ─────────────────────────────────────────────
st.divider()
st.header("그래프 2. 일관객 합계 TOP 5 영화의 날짜별 변화")

top5_movies = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
    .head(5)["영화명"]
    .tolist()
)

top5_df = (
    df[df["영화명"].isin(top5_movies)]
    .sort_values(["영화명", "날짜"])
    .copy()
)

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="이 기간 일관객 합계가 가장 큰 5편의 날짜별 일관객",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화",
    },
    hover_data={
        "날짜": "|%Y-%m-%d",
        "일관객": ":,",
        "영화명": True,
    },
)

fig2.update_traces(
    hovertemplate="영화: %{fullData.name}<br>날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
)

fig2.update_layout(
    hovermode="x unified",
    legend_title_text="영화",
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(
    fig2,
    use_container_width=True,
    config={"displayModeBar": True},
)

st.markdown("**이 그래프로 알 수 있는 것**")
st.info("여기에 이 그래프를 통해 알 수 있는 내용을 한 문장으로 적어 주세요.")


# ─────────────────────────────────────────────
# 앞으로 그래프를 추가할 공간
# ─────────────────────────────────────────────
st.divider()
