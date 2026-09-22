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
# 그래프 3. 날짜별 10위권 일관객 합계
# ─────────────────────────────────────────────
st.divider()
st.header("그래프 3. 날짜별 10위권 일관객 합계")

daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

top3_days = (
    daily_total.nlargest(3, "일관객")
    .sort_values("일관객", ascending=False)
    .copy()
)

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 10위권 일관객 합계",
    labels={
        "날짜": "날짜",
        "일관객": "10위권 일관객 합계",
    },
    hover_data={
        "날짜": "|%Y-%m-%d",
        "일관객": ":,",
    },
)

# 합계가 가장 컸던 3일을 그래프 위에 표시
fig3.add_scatter(
    x=top3_days["날짜"],
    y=top3_days["일관객"],
    mode="markers+text",
    text=top3_days["날짜"].dt.strftime("%Y-%m-%d"),
    textposition="top center",
    marker=dict(size=10),
    name="합계 TOP 3",
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>10위권 일관객 합계: %{y:,}명<extra></extra>",
)

fig3.update_layout(
    hovermode="x unified",
    showlegend=True,
    margin=dict(l=20, r=20, t=70, b=20),
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.info("여기에 이 그래프를 통해 알 수 있는 내용을 한 문장으로 적어 주세요.")

# ─────────────────────────────────────────────
# 그래프 4. 영화별 기간 일관객 TOP 10
# ─────────────────────────────────────────────
st.divider()
st.header("그래프 4. 영화별 기간 일관객 TOP 10")

# 영화별로 기간 내 일관객 합계와 10위권에 등장한 날짜 수를 계산합니다.
movie_summary = (
    df.dropna(subset=["영화명", "일관객", "날짜"])
    .groupby("영화명")
    .agg(
        기간_일관객=("일관객", "sum"),
        top10_days=("날짜", "nunique"),
    )
    .reset_index()
    .nlargest(10, "기간_일관객")
    .sort_values("기간_일관객", ascending=True)
)

fig4 = px.bar(
    movie_summary,
    x="기간_일관객",
    y="영화명",
    orientation="h",
    title="이 기간 일관객 합계 TOP 10",
    labels={
        "기간_일관객": "기간 일관객 합계",
        "영화명": "영화",
    },
)

# 마우스를 올리면 일관객 합계와 10위권에 든 날수를 함께 표시합니다.
fig4.update_traces(
    customdata=movie_summary[["top10_days"]].to_numpy(),
    hovertemplate=(
        "영화: %{y}<br>"
        "기간 일관객 합계: %{x:,.0f}명<br>"
        "10위권에 든 날수: %{customdata[0]}일"
        "<extra></extra>"
    ),
)

fig4.update_layout(
    yaxis=dict(
        categoryorder="array",
        categoryarray=movie_summary["영화명"].tolist(),
    ),
    xaxis=dict(tickformat=","),
    margin=dict(l=20, r=40, t=70, b=20),
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.info("여기에 이 그래프를 통해 알 수 있는 내용을 한 문장으로 적어 주세요.")

# Graph 5
st.divider()
st.header("그래프 5. 월 × 요일별 일관객 합계")

# 날짜에서 월과 요일을 추출합니다.
heatmap_df = df.copy()
heatmap_df["월"] = heatmap_df["날짜"].dt.month
weekday_order = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
heatmap_df["요일"] = heatmap_df["날짜"].dt.dayofweek.map(
    dict(enumerate(weekday_order))
)

# 월 × 요일별 일관객 합계를 계산하고, 월요일~일요일 순서로 정렬합니다.
heatmap_data = (
    heatmap_df.groupby(["월", "요일"], as_index=False)["일관객"]
    .sum()
    .pivot(index="월", columns="요일", values="일관객")
    .reindex(columns=weekday_order)
    .fillna(0)
)

fig5 = px.imshow(
    heatmap_data,
    labels={
        "x": "요일",
        "y": "월",
        "color": "일관객 합계",
    },
    x=weekday_order,
    y=heatmap_data.index,
    color_continuous_scale="Blues",
    aspect="auto",
    text_auto=",.0f",
    title="월 × 요일별 일관객 합계",
)

fig5.update_traces(
    hovertemplate=(
        "월: %{y}월<br>"
        "요일: %{x}<br>"
        "일관객 합계: %{z:,}명"
        "<extra></extra>"
    )
)

fig5.update_layout(
    xaxis=dict(
        categoryorder="array",
        categoryarray=weekday_order,
    ),
    yaxis=dict(
        dtick=1,
        autorange="reversed",
    ),
    coloraxis_colorbar=dict(
        title="일관객 합계",
    ),
    margin=dict(l=20, r=20, t=70, b=20),
)

st.plotly_chart(fig5, use_container_width=True)
st.markdown("**이 그래프로 알 수 있는 것**")
st.info("월과 요일에 따라 10위권 영화의 일관객 합계가 어떻게 달라지는지 비교할 수 있습니다.")
