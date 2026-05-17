# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="DCA 복리 시뮬레이터")

# ── 고급 스타일 및 테마 정의 ───────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght=400;500;700&display=block');
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
.main-title { font-size: 18px; font-weight: 700; color: #1a1a1a; }
.main-subtitle { font-size: 13px; color: #888; }
.chart-card, .slider-card, .data-card {
    background: white; border-radius: 16px; padding: 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 16px;
}
.slider-card-title, .data-card-title { font-size: 15px; font-weight: 700; color: #1a1a1a; margin-bottom: 16px; }
.styled-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.styled-table th { background: #f5f5f5; padding: 10px 12px; text-align: right; font-weight: 600; color: #555; border-bottom: 1px solid #eee; }
.styled-table th:first-child { text-align: center; }
.styled-table td { padding: 9px 12px; text-align: right; border-bottom: 1px solid #f5f5f5; color: #333; }
.styled-table td:first-child { text-align: center; font-weight: 600; }
.highlight-row td { color: #00A86B !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# ── 헤더 표시 ──────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div class="main-title">📈 DCA 복리 시뮬레이터</div>
    <div class="main-subtitle">Compound Interest Calculator</div>
</div>
""", unsafe_allow_html=True)

# ── 좌측/우측 레이아웃 분할 ──────────────────────────────
col_input, col_chart = st.columns([1, 2])

with col_input:
    st.markdown('<div class="slider-card">', unsafe_allow_html=True)
    st.markdown('<div class="slider-card-title">⚙️ 투자 및 은퇴 설정</div>', unsafe_allow_html=True)
    
    # 💡 주요 ETF 20종 카테고리별 라인업 구성
    etf_options = [
        # [미국 시장 지수]
        "QQQ (원조 나스닥 100 기술주)",
        "SPY (미국 시장 대표 S&P 500)",
        "DIA (다우존스 전통 우량주)",
        "VT (전 세계 주식 총망라)",
        # [배당 / 인컴]
        "SCHD (미국 배당성장 시그니처)",
        "JEPI (월배당 커버드콜 고배당)",
        "VIG (미국 배당성장 우량기업)",
        "O (리얼티인컴 월배당 부동산 리츠)",
        # [빅테크 / 반도체 섹터]
        "SMH (글로벌 반도체 대장주 모음)",
        "SOXX (필라델피아 반도체 지수)",
        "XLK (미국 기술주 섹터 종합)",
        "VNQ (미국 부동산 리츠 종합)",
        # [국내 상장 ETF]
        "KODEX 미국S&P500 (환노출형 국내상장)",
        "TIGER 미국나스닥100 (국내상장 빅테크)",
        "ACE 미국배당다우존스 (한국판 SCHD)",
        "TIGER 200 (대한민국 코스피 200)",
        # [레버리지 및 채권]
        "QLD (나스닥 100 2배 레버리지)",
        "TQQQ (나스닥 100 3배 레버리지)",
        "TLT (미국 20년 국채 장기채권)",
        "SHY (미국 1-3년 국채 단기채권)"
    ]
    
    ticker = st.selectbox("티커 선택 (주요 ETF 20종)", etf_options)
    
    # 💡 선택한 ETF별 대략적인 역사적 장기 연평균 수익률(CAGR) 매핑 테이블
    etf_rates = {
        "QQQ (원조 나스닥 100 기술주)": 12.0,
        "SPY (미국 시장 대표 S&P 500)": 9.5,
        "DIA (다우존스 전통 우량주)": 9.0,
        "VT (전 세계 주식 총망라)": 7.5,
        "SCHD (미국 배당성장 시그니처)": 10.5,
        "JEPI (월배당 커버드콜 고배당)": 7.5,
        "VIG (미국 배당성장 우량기업)": 9.0,
        "O (리얼티인컴 월배당 부동산 리츠)": 7.0,
        "SMH (글로벌 반도체 대장주 모음)": 16.0,
        "SOXX (필라델피아 반도체 지수)": 15.5,
        "XLK (미국 기술주 섹터 종합)": 13.0,
        "VNQ (미국 부동산 리츠 종합)": 6.5,
        "KODEX 미국S&P500 (환노출형 국내상장)": 9.5,
        "TIGER 미국나스닥100 (국내상장 빅테크)": 12.0,
        "ACE 미국배당다우존스 (한국판 SCHD)": 10.5,
        "TIGER 200 (대한민국 코스피 200)": 6.5,
        "QLD (나스닥 100 2배 레버리지)": 18.0,
        "TQQQ (나스닥 100 3배 레버리지)": 22.0,
        "TLT (미국 20년 국채 장기채권)": 4.5,
        "SHY (미국 1-3년 국채 단기채권)": 2.5
    }
    
    default_rate = etf_rates.get(ticker, 10.0)

    monthly_dep_input = st.number_input("매달 DCA 매수금액 (만원)", min_value=0, max_value=10000, value=100, step=10)
    st.caption(f"표기: {monthly_dep_input*10000:,}원")
    
    c1, c2 = st.columns(2)
    with c1:
        years_input = st.number_input("총 기간 (년)", min_value=1, max_value=50, value=20, step=1)
    with c2:
        init_money_input = st.number_input("시작액 (만원)", min_value=0, max_value=100000, value=1000, step=100)
    st.caption(f"표기: {init_money_input*10000:,}원")
    
    # 사용자가 직접 미세 조정도 가능하게 유지하되, 티커 변경 시 자동 초기화
    annual_ret_input = st.number_input("연평균 수익률 고정 (%)", min_value=0.0, max_value=50.0, value=default_rate, step=0.5)
    
    with_draw_active = st.checkbox("은퇴 후 인출 설정", value=True)
    withdraw_money_input = 0
    if with_draw_active:
        withdraw_money_input = st.number_input("투자 종료 후 월 인출액 (만원)", min_value=0, max_value=5000, value=1000, step=50)
        st.caption(f"표기: {withdraw_money_input*10000:,}원")
        
    st.markdown('</div>', unsafe_allow_html=True)

# ── 복리 시뮬레이션 계산 로직 ───────────────────────
monthly_dep = monthly_dep_input * 10000
init_money  = init_money_input * 10000
annual_ret  = annual_ret_input / 100
withdraw_money = withdraw_money_input * 10000

months = years_input * 12
monthly_rate = (1 + annual_ret) ** (1/12) - 1
balance = init_money
total_principal = init_money
data = []

# 자산 축적기
for m in range(1, months + 1):
    balance = balance * (1 + monthly_rate) + monthly_dep
    total_principal += monthly_dep
    if m % 12 == 0:
        y = m // 12
        profit = max(0, balance - total_principal)
        data.append({
            "년차": f"{y}년", "구분": "자산 축적기",
            "초기 투자금": init_money / 1e8, "누적 적립원금": (total_principal - init_money) / 1e8,
            "복리 수익": profit / 1e8, "총자산": balance / 1e8, "총원금": total_principal / 1e8
        })

# 은퇴 인출기
if with_draw_active:
    for m in range(months + 1, months + (30 * 12) + 1):
        balance = balance * (1 + monthly_rate) - withdraw_money
        if balance < 0: balance = 0
        if (m - months) % 12 == 0:
            y = years_input + ((m - months) // 12)
            profit = max(0, balance - total_principal)
            data.append({
                "년차": f"{y}년(은퇴)", "구분": "은퇴 인출기",
                "초기 투자금": init_money / 1e8, "누적 적립원금": (total_principal - init_money) / 1e8,
                "복리 수익": profit / 1e8, "총자산": balance / 1e8, "총원금": total_principal / 1e8
            })

df = pd.DataFrame(data)

# ── 차트 구성 및 시각화 ─────────────────────────────
with col_chart:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    df["수익률"] = (df["총자산"] / df["총원금"] - 1) * 100
    
    hover_template = (
        "<b>%{x}차 상태</b><br>─────────────────────<br>"
        "🔴 초기 투자금 : <b>%{customdata[1]:.2f}억</b><br>"
        "🟡 월 DCA 누계 : <b>%{customdata[2]:.2f}억</b><br>"
        "🟢 복리 수익   : <b>%{customdata[3]:.2f}억</b><br>─────────────────────<br>"
        "💰 총 자산 규모 : <b>%{customdata[0]:.2f}억</b> (수익률 %{customdata[4]:.1f}%)<extra></extra>"
    )
    customdata = list(zip(df["총자산"], df["초기 투자금"], df["누적 적립원금"], df["복리 수익"], df["수익률"]))
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["년차"], y=df["초기 투자금"], name="초기 투자금", marker_color="#E74C3C", customdata=customdata, hovertemplate=hover_template))
    fig.add_trace(go.Bar(x=df["년차"], y=df["누적 적립원금"], name="누적 적립원금", marker_color="#F1C40F", customdata=customdata, hovertemplate=hover_template))
    fig.add_trace(go.Bar(x=df["년차"], y=df["복리 수익"], name="복리 수익", marker_color="#00A86B", customdata=customdata, hovertemplate=hover_template))
    
    fig.update_layout(
        barmode='stack', xaxis_title="경과 연수 (은퇴 인출기 포함)", yaxis_title="자산 규모 (억 원)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white", paper_bgcolor="white", height=490, margin=dict(t=40, b=20, l=20, r=20)
    )
    fig.update_yaxes(gridcolor="#F0F0F0")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── 하단 연도별 데이터 테이블 출력 ─────────────────────────
st.markdown('<div class="data-card"><div class="data-card-title">📊 연도별 시뮬레이션 세부 지표</div>', unsafe_allow_html=True)
table_rows = ""
for _, row in df.iterrows():
    r_style = 'class="highlight-row"' if row["총자산"] >= row["총원금"] * 2 else ''
    table_rows += f"""
    <tr {r_style}>
        <td>{row['년차']}</td>
        <td>{row['구분']}</td>
        <td>{row['총원금']:.2f}억</td>
        <td>{row['복리 수익']:.2f}억</td>
        <td>{row['총자산']:.2f}억</td>
        <td>{((row['총자산']/row['총원금'])-1)*100:.1f}%</td>
    </tr>"""

st.markdown(f"""
<table class="styled-table">
    <thead><tr><th>년차</th><th>단계 구분</th><th>누적 원금</th><th>복리 수익</th><th>총 자산</th><th>수익률</th></tr></thead>
    <tbody>{table_rows}</tbody>
</table>
</div>
""", unsafe_allow_html=True)