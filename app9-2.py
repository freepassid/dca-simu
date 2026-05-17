# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="DCA 복리 시뮬레이터")

# ── 고급 폰트 및 카드 레이아웃 스타일 적용 ──────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=block');

html, body, [class*="css"], h1, h2, h3, p, div, span, label, button {
    font-family: "Noto Sans KR", "Malgun Gothic", "맑은 고딕", sans-serif !important;
}

.stApp { background-color: #f8f9fa; }

.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0 8px 0;
    border-bottom: 1px solid #e0e0e0;
    margin-bottom: 16px;
}
.main-title {
    font-size: 18px;
    font-weight: 700;
    color: #1a1a1a;
}
.main-subtitle {
    font-size: 13px;
    color: #888;
}

.chart-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}

.slider-card {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}
.slider-card-title {
    font-size: 15px;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 16px;
}

/* 슬라이더 초록색 테마 포인트 */
.stSlider > div > div > div > div {
    background: #2ECC71 !important;
}
.stSlider > div > div > div > div > div {
    background: #2ECC71 !important;
    border-color: #2ECC71 !important;
}
div[data-testid="stSlider"] label {
    font-size: 13px !important;
    color: #666 !important;
    font-weight: 500 !important;
}

.data-card {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}
.data-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}
.data-card-title { font-size: 15px; font-weight: 700; color: #1a1a1a; }
.data-card-hint {
    font-size: 12px;
    color: #f0a500;
    background: #fffbf0;
    padding: 4px 10px;
    border-radius: 20px;
}

.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.styled-table th {
    background: #f5f5f5;
    padding: 10px 12px;
    text-align: right;
    font-weight: 600;
    color: #555;
    border-bottom: 1px solid #eee;
}
.styled-table th:first-child { text-align: center; }
.styled-table td {
    padding: 9px 12px;
    text-align: right;
    border-bottom: 1px solid #f5f5f5;
    color: #333;
}
.styled-table td:first-child { text-align: center; font-weight: 600; }
.styled-table tr:hover td { background: #f9f9f9; }
.highlight-row td { color: #2ECC71 !important; font-weight: 700 !important; }

hr { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Session State 초기화 ───────────────────────────
if "years" not in st.session_state:
    st.session_state.years = 20
if "monthly" not in st.session_state:
    st.session_state.monthly = 100
if "init" not in st.session_state:
    st.session_state.init = 1000
if "rate" not in st.session_state:
    st.session_state.rate = 11.5

# ── 헤더 (요청하신 대로 우측 글자 완전 제외 가능하도록 정돈) ──
st.markdown("""
<div class="main-header">
    <div class="main-title">📈 DCA 복리 시뮬레이터</div>
    <div class="main-subtitle">Compound Interest Calculator</div>
</div>
""", unsafe_allow_html=True)

# ── 복리 계산 (인풋 값 동적 반영) ──────────────────
years       = st.session_state.years
monthly_dep = st.session_state.monthly * 10000
init_money  = st.session_state.init * 10000
annual_ret  = st.session_state.rate / 100

months = years * 12
monthly_rate = (1 + annual_ret) ** (1/12) - 1
balance = init_money
total_principal = init_money
data = []

for m in range(1, months + 1):
    balance = balance * (1 + monthly_rate) + monthly_dep
    total_principal += monthly_dep
    if m % 12 == 0:
        year_num = m // 12
        profit = max(0, balance - total_principal)
        data.append({
            "년차": f"{year_num}년",
            "year": year_num,
            "초기 투자금": init_money / 1e8,
            "누적 적립원금": (total_principal - init_money) / 1e8,
            "복리 수익": profit / 1e8,
            "총자산": balance / 1e8,
            "총원금": total_principal / 1e8,
        })

df = pd.DataFrame(data)

# ── 차트 데이터 정밀 처리 및 카드 배치 ────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)

df["수익률"] = (df["총자산"] / df["총원금"] - 1) * 100

# 호버 커스텀 툴팁 구조 바인딩
hover_template = (
    "<b>%{x}차 &nbsp; 누적 평가액</b><br>"
    "─────────────────────<br>"
    "🔴 초기 투자금 : <b>%{customdata[1]:.2f}억</b><br>"
    "🟡 월 DCA 누계 : <b>%{customdata[2]:.2f}억</b><br>"
    "🟢 복리 수익   : <b>%{customdata[3]:.2f}억</b><br>"
    "─────────────────────<br>"
    "💰 총 자산 : <b>%{customdata[0]:.2f}억</b>"
    " &nbsp;|&nbsp; 수익률 <b>+%{customdata[4]:.1f}%</b>"
    "<extra></extra>"
)

# 꼭 필요한 요소만 인덱스 순서대로 정확히 매핑 (오류 방지)
customdata = list(zip(
    df["총자산"],
    df["초기 투자금"],
    df["누적 적립원금"],
    df["복리 수익"],
    df["수익률"]
))

fig = go.Figure()
fig.add_trace(go.Bar(
    x=df["년차"], y=df["초기 투자금"], name="초기 투자금",
    marker_color="#E74C3C", customdata=customdata, hovertemplate=hover_template,
))
fig.add_trace(go.Bar(
    x=df["년차"], y=df["누적 적립원금"], name="누적 적립원금",
    marker_color="#F1C40F", customdata=customdata, hovertemplate=hover_template,
))
fig.add_trace(go.Bar(
    x=df["년차"], y=df["복리 수익"], name="복리 수익",
    marker_color="#2ECC71",
    text=df["총자산"].apply(lambda x: f"{x:.1f}억" if x >= 0.1 else ""),
    textposition='outside',
    textfont=dict(size=11, color="#333"),
    customdata=customdata, hovertemplate=hover_template,
))

fig.update_layout(
    barmode='stack',
    xaxis_title="경과 년수",
    yaxis_title="자산 규모 (단위: 억 원)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=480,
    margin=dict(t=40, b=20, l=20, r=20),
    font=dict(family="Malgun Gothic, sans-serif"),
    hovermode="closest",
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#ddd",
        font=dict(family="Malgun Gothic, sans-serif", size=13, color="#333"),
    ),
)
fig.update_yaxes(gridcolor="#F0F0F0")

# 표준 모드 크기 설정으로 안전성 확보
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# ── 슬라이더 카드 컨트롤러 블록 ─────────────────────
st.markdown('<div class="slider-card">', unsafe_allow_html=True)
st.markdown('<div class="slider-card-title">🎛 빠른 시뮬레이션 조절</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.slider("투자 기간", min_value=1, max_value=40, step=1, format="%d년", key="years")
with col2:
    st.slider("월 DCA 금액", min_value=0, max_value=1000, step=10, format="%d만원", key="monthly")
with col3:
    st.slider("초기 투자금", min_value=0, max_value=5000, step=100, format="%d만원", key="init")
with col4:
    st.slider("예상 연수익률", min_value=0.0, max_value=30.0, step=0.5, format="%.1f%%", key="rate")

st.markdown('</div>', unsafe_allow_html=True)


# ── 연도별 상세 데이터 테이블 (HTML 태그 누락 완벽 수정) ──
st.markdown("""
<div class="data-card">
  <div class="data-card-header">
    <div class="data-card-title">📊 연도별 상세 데이터
      <span style="font-size:12px;color:#999;font-weight:400">(투자 기간 기준)</span>
    </div>
    <div class="data-card-hint">💡 원금 대비 2배, 4배 등 기하급수적 성장 시점을 확인해보세요.</div>
  </div>
""", unsafe_allow_html=True)

table_rows = ""
for _, row in df.iterrows():
    수익률 = (row["총자산"] / row["총원금"] - 1) * 100 if row["총원금"] > 0 else 0
    # 원금 대비 2배 이상 불어난 해는 자동으로 초록색 강조 효과 부여
    row_class = 'highlight-row' if row["총자산"] >= row["총원금"] * 2 else ''
    table_rows += f"""
    <tr class="{row_class}">
        <td>{row['년차']}</td>
        <td>{row['총원금']:.2f}억</td>
        <td>{row['복리 수익']:.2f}억</td>
        <td>{row['총자산']:.2f}억</td>
        <td>{수익률:.1f}%</td>
    </tr>"""

# 미닫혔던 div 박스 태그 정밀 교정 완료
st.markdown(f"""
  <table class="styled-table">
    <thead>
      <tr><th>년차</th><th>누적 원금</th><th>복리 수익</th><th>총 자산</th><th>수익률</th></tr>
    </thead>
    <tbody>{table_rows}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)