import streamlit as st
import streamlit.components.v1 as components

# --- [1. 디자인 및 시인성 완전 해결을 위한 강제 CSS 프로토콜] ---
st.set_page_config(page_title="로얄동물메디컬센터 임상 지능 시스템", layout="wide")

st.markdown("""
    <style>
    /* 구글 폰트 로드 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

    /* [CRITICAL] 모든 배경과 글자색을 테마와 관계없이 강제 고정 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], [data-testid="stHeader"], .stTabs {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    /* 사이드바 텍스트 보정 */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #111111 !important;
        font-size: 18px !important;
    }

    /* [VITAL] 입력창, 선택창 내부 글자색 및 배경색 강제 해결 */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    input, select, textarea, div[role="listbox"] {
        background-color: #F0F2F6 !important;
        color: #000000 !important;
        border: 1px solid #1E3A8A !important;
        font-size: 18px !important;
    }
    
    /* 선택된 항목 텍스트 강제 */
    div[data-testid="stSelectbox"] p, div[data-testid="stNumberInput"] p {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* 공식 및 안내 배너 - 배경 검정, 글자 흰색 강제 */
    .formula-banner-v29 {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        padding: 25px;
        border-radius: 12px;
        border-left: 10px solid #EF4444 !important;
        margin-bottom: 25px;
    }
    .formula-banner-v29 h2, .formula-banner-v29 h3, .formula-banner-v29 p, .formula-banner-v29 b {
        color: #FFFFFF !important;
    }

    /* CRI 조제 카드 시인성 극대화 */
    .cri-card-v29 {
        background-color: #F8FAFC !important;
        border: 2px solid #E2E8F0 !important;
        border-left: 15px solid #10B981 !important;
        padding: 35px;
        border-radius: 15px;
        margin-top: 20px;
    }
    .text-speed-v29 { font-size: 56px !important; font-weight: 900 !important; color: #059669 !important; line-height: 1.2; }
    .text-recipe-v29 { font-size: 38px !important; font-weight: 800 !important; color: #1E3A8A !important; line-height: 1.3; }

    /* 전해질 평가 카드 */
    .eval-card-v29 {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .eval-val-red { font-size: 32px !important; font-weight: 900 !important; color: #DC2626 !important; }
    .eval-val-blue { font-size: 32px !important; font-weight: 900 !important; color: #2563EB !important; }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 로얄 표준 데이터베이스] ---
STOCK = {
    "Epinephrine": 1.0, "Atropine": 0.5, "Vasopressin": 20.0, "Lidocaine": 20.0, "Amiodarone": 50.0,
    "Naloxone": 0.4, "Flumazenil": 0.1, "Atipamezole": 5.0, "Butorphanol": 2.0, "Midazolam": 1.0, 
    "Diazepam": 5.0, "Dexmedetomidine": 0.118, "Dopamine": 32.96, "Dobutamine": 50.0, 
    "Furosemide": 10.0, "Insulin(RI)": 1.0, "KCl": 2.0, "Calcium Gluconate": 100.0, "Sodium Bicarbonate": 1.0
}

AMINO_ACID_DATA = {
    "후라바솔 10% (고용량 아미노산)": {"conc": 10.0},
    "후라바소레-페파 6.5% (간질환용)": {"conc": 6.5},
    "네프리솔 5.6% (신장질환용)": {"conc": 5.6}
}

DISEASE_FACTORS = {
    "기본/비만": {"성장기": 2.0, "중성화 완료": 1.2, "미중성화": 1.4, "비만감량": 0.8},
    "신장(CKD)/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전": 1.05},
    "췌장/간/소화기": {"췌장염 안정": 1.1, "간질환 안정": 1.15, "지방간(HL)": 1.35, "EPI": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

DIET_LIST = {
    "Royal Canin": {"Recovery": 105, "GI (Dry)": 3912, "GI Low Fat (Wet)": 385, "Urinary S/O": 3884, "Renal": 3988},
    "Hill's": {"a/d": 183, "i/d Digestive": 3663, "i/d Low Fat Wet": 341, "k/d Kidney": 4220}
}

# --- [3. 사이드바 - 환자 데이터 입력] ---
with st.sidebar:
    st.markdown("## 📋 Patient Profile")
    species = st.selectbox("품종(Species)", ["개(Canine)", "고양이(Feline)"])
    weight = st.number_input("체중(Weight, kg)", 0.1, 150.0, 3.1, 0.1, format="%.1f")
    st.markdown("---")
    cat_n = st.selectbox("질환 카테고리", list(DISEASE_FACTORS.keys()))
    sub_cat = st.selectbox("세부 상태", list(DISEASE_FACTORS[cat_n].keys()))
    st.markdown("---")
    st.caption("Protocol Architect")
    st.markdown("### **Dr. Jaehee Lee**")

# --- [4. 메인 대시보드 제목] ---
st.title("🐾 RAMC Clinical Decision Support Engine")
st.markdown("#### 로얄동물메디컬센터 임상 의사결정 지원 시스템")

tabs = st.tabs(["🚨 CPCR (CSU)", "🧪 전해질/삼투압", "💉 CRI 조제", "💧 수액 & 아미노산", "🍴 영양 관리", "🩸 수혈"])

# --- TAB 1: CPCR ---
with tabs[0]:
    st.subheader(f"🚨 CPCR Protocol for {weight:.1f}kg patient")
    bpm_val = st.radio("Compression Rate (BPM)", [90, 120], horizontal=True)
    metronome_html = f"""
    <div style="display: flex; align-items: center; gap: 20px; background: #1E293B; padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <button id="pBtn" style="padding: 12px 30px; font-weight: 900; cursor: pointer; background: #10B981; color: white; border:none; border-radius:8px; font-size:20px;">▶ START</button>
        <div id="heart" style="font-size: 40px;">❤️</div> <div style="font-size: 24px; font-weight: bold;">{bpm_val} BPM</div>
    </div>
    <script>
        let ctx = null; let nextT = 0; let tid = null; const btn = document.getElementById('pBtn'); const ht = document.getElementById('heart');
        function t() {{ while (nextT < ctx.currentTime + 0.1) {{ const o = ctx.createOscillator(); const g = ctx.createGain(); o.connect(g); g.connect(ctx.destination); o.frequency.value = 880; g.gain.value = 0.05; o.start(nextT); o.stop(nextT + 0.05); nextT += 60 / {bpm_val}; }} tid = setTimeout(t, 25); }}
        btn.onclick = () => {{ if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)(); if (tid) {{ clearTimeout(tid); tid = null; btn.innerText = '▶ START'; btn.style.background = '#10B981'; }} else {{ nextT = ctx.currentTime; t(); btn.innerText = '■ STOP'; btn.style.background = '#EF4444'; }} }};
    </script>
    """
    components.html(metronome_html, height=120)
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown(f"""<div style="background-color:#F8FAFC; border:1px solid #CBD5E1; border-radius:12px; padding:20px;">
        <b style="font-size:22px; color:#1E3A8A;">1. VF / Pulseless VT</b><br><br>
        <b>Defibrillation:</b> Ext {weight*4:.1f}-{weight*6:.1f}J | Int {weight*0.5:.1f}-{weight*1J}<br>
        - Epinephrine(L): {(weight*0.01):.2f} ml IV<br>
        - Vasopressin: {(weight*0.8/20):.2f} ml IV (OR)<br>
        - Amiodarone: {(weight*5/50):.2f} ml IV (AND)</div>""", unsafe_allow_html=True)
    with col_c2:
        st.markdown(f"""<div style="background-color:#F8FAFC; border:1px solid #CBD5E1; border-radius:12px; padding:20px;">
        <b style="font-size:22px; color:#1E3A8A;">2. Asystole / PEA</b><br><br>
        - Epinephrine(L): {(weight*0.01):.2f} ml (격주 사이클)<br>
        - Vasopressin: {(weight*0.8/20):.2f} ml (1회 한정)<br>
        - Atropine: {(weight*0.04/0.5):.2f} ml (격주 사이클)<br>
        <b>Intratracheal:</b> Epi {(weight*0.02):.2f}ml | Atropine {(weight*0.16):.2f}ml</div>""", unsafe_allow_html=True)

# --- TAB 2: 전해질/삼투압 ---
with tabs[1]:
    st.header("🧪 전해질 및 삼투압 정밀 평가")
    e1, e2, e3 = st.columns(3)
    with e1:
        st.subheader("검사 결과 입력")
        na = st.number_input("Measured Na+", 100.0, 200.0, 145.0, 0.1)
        k_in = st.number_input("Measured K+", 1.0, 10.0, 4.0, 0.1)
        glu = st.number_input("Glucose (mg/dL)", 10.0, 1000.0, 100.0, 1.0)
        bun = st.number_input("BUN (mg/dL)", 5.0, 300.0, 20.0, 1.0)
        bag_v = st.selectbox("Fluid Bag (mL)", [30, 50, 100, 250, 500, 1000], index=5)
    with e2:
        st.subheader("종합 임상 평가")
        c_na = na + 1.6*((glu-100)/100) if glu > 100 else na
        osmo = 2*(na+k_in) + (glu/18) + (bun/2.8)
        st.markdown(f"""<div class="eval-card-v29"><b>Corrected Na+:</b><br><span class="eval-val-red">{c_na:.1f} mEq/L</span></div>
        <div class="eval-card-v29"><b>Osmolality:</b><br><span class="eval-val-blue">{osmo:.1f} mOsm/kg</span></div>""", unsafe_allow_html=True)
    with e3:
        st.subheader("보정 레시피")
        kt = next((v for kr, v in {2.0:80, 2.5:60, 3.0:40, 3.5:28}.items() if k_in <= kr), 10)
        st.markdown(f"""<div class="eval-card-v29" style="border-left:8px solid #3B82F6 !important;">
        <b>KCl (2mEq/ml) 첨가량:</b><br><span style="font-size:32px; font-weight:900; color:#1E3A8A !important;">Add {(kt*bag_v/1000)/2.0:.1f} mL</span><br>
        <p>Target: {kt}mEq/L (in {bag_v}ml Bag)</p></div>""", unsafe_allow_html=True)

# --- TAB 3: CRI 조제 (최강 시인성) ---
with tabs[2]:
    st.header("💉 High-Visibility CRI Protocol")
    dr_c = st.selectbox("CRI 약물 선택", ["Butorphanol", "Midazolam", "Dexmedetomidine", "Epinephrine", "Norepinephrine", "Dopamine", "Furosemide", "Insulin(RI)"])
    cr1, cr2 = st.columns([1, 2])
    with cr1:
        ir_v = st.number_input("설정 속도 (mL/h)", 0.1, 100.0, 0.5, 0.1)
        td_v = st.number_input("목표 용량 (mpk/h or mcg/kg/min)", 0.0, 50.0, 0.1, 0.01, format="%.3f")
        sv_v = st.selectbox("시린지 용량", [10, 20, 50], index=2)
    with cr2:
        mgh = (td_v*weight*60/1000) if dr_sel in ["Epinephrine", "Norepinephrine", "Dopamine"] else (td_v*weight)
        dml = (mgh / STOCK[dr_c]) * sv_v / ir_v
        st.markdown(f"""<div class="cri-card-v29">
            <span class="text-label">🚩 {dr_c} 설정 속도</span><br><span class="text-speed-v29">{ir_v:.1f} mL/h</span><br><br>
            <span class="text-label">🧪 조제 레시피 (총 {sv_v}mL)</span><br><span class="text-recipe-v29">원액 {dml:.2f} mL + 희석액 {(sv_v-dml):.2f} mL</span>
        </div>""", unsafe_allow_html=True)

# --- TAB 4: 수액 & 아미노산 요법 ---
with tabs[3]:
    st.markdown("""<div class="formula-banner-v29">
        <h2>RER = BW × 50 kcal/day</h2>
        <p style="font-size:22px;">💡 <b>표준 유지 범위:</b> 40-60 mL/kg/day (시간당 약 2-3 mL/kg)</p></div>""", unsafe_allow_html=True)
    f1, f2 = st.columns([1.2, 1])
    with f1:
        st.subheader("💧 수액 속도 계산 (Dry Mode)")
        mr = st.slider("유지 (mL/kg/hr)", 1.0, 4.0, 2.0, 0.5)
        total_f = (weight * mr) + (st.number_input("탈수 (%)", 0, 15, 0) * weight * 10 / 12) + (st.number_input("지속 손실 (mL/day)", value=float(round(weight*1.0, 1))) / 24)
        st.metric("최종 수액 속도", f"{total_f:.1f} mL/h")
    with f2:
        st.subheader("🧬 아미노산(Amino Acid) 영양 공급")
        aa_sel = st.selectbox("아미노산 제제", list(AMINO_ACID_DATA.keys()))
        aa_ml = (1.0 / AMINO_ACID_DATA[aa_sel]['conc']) * 100
        st.markdown(f"""<div style="background-color:#F0FDF4; padding:25px; border-radius:12px; border:2px solid #22C55E;">
        <b style="font-size:22px; color:#166534 !important;">{aa_sel} 급여 기준</b><br>
        <span style="font-size:36px; font-weight:900; color:#15803D !important;">{aa_ml:.1f} mL / 100 kcal</span><br>
        <p style="font-size:16px; color:#166534 !important;">※ 100kcal당 단백질 1g을 공급하기 위한 mL 수치입니다.</p></div>""", unsafe_allow_html=True)

# --- TAB 5: 영양 관리 ---
with tabs[4]:
    st.markdown('<div class="formula-banner-v29"><h3>Royal Standard Nutrition Protocol</h3></div>', unsafe_allow_html=True)
    n1, n2 = st.columns(2)
    with n1:
        der = (weight * 50) * DISEASE_FACTORS[cat_n][sub_cat] * (1.1 if st.checkbox("입원 가중치(1.1)", value=True) else 1.0)
        s_m = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        st_sel = st.radio("급여 전략", ["3단계", "4단계", "5단계"], horizontal=True)
        cs = st.select_slider("현재 단계", options=s_m[st_sel], value=s_m[st_sel][-1])
        st.metric("목표 DER", f"{der*cs:.0f} kcal")
    with n2:
        prod = st.selectbox("사료 선택", list(DIET_LIST["Royal Canin"].keys()) + list(DIET_LIST["Hill's"].keys()))
        kcal_v = {**DIET_LIST["Royal Canin"], **DIET_LIST["Hill's"]}[prod]
        amt = ((der*cs)/kcal_v) * (1 if "Recovery" in prod or "a/d" in prod else 1000)
        st.success(f"### 최종 급여량: **{amt:.1f} {'can' if 'Recovery' in prod or 'a/d' in prod else 'g'}**")

# --- TAB 6: 수혈 ---
with tabs[5]:
    st.header("🩸 Blood Transfusion Calculator")
    tx_col1, tx_col2 = st.columns([1, 1.5])
    with tx_col1:
        cp = st.number_input("현재 PCV", 1.0, 50.0, 15.0); tp = st.number_input("목표 PCV", 1.0, 50.0, 25.0)
        pr = st.radio("제제", ["전혈", "pRBC"], horizontal=True)
        tx_v = weight * (90 if species == "개(Canine)" else 60) * ((tp - cp) / (40.0 if pr == "전혈" else 70.0))
        st.metric("수혈 필요량", f"{max(0.0, round(tx_v, 1))} mL")
    with tx_col2:
        st.info("**[수혈 SOP]**\n1. 기본 4시간 내 완료 권장.\n2. 심장/신장 환자 0.5-1ml/kg/h로 최대 12-24시간 연장 가능 (분할 투여 권장).")

st.divider()
st.caption(f"Royal Animal Medical Center | v29.0 Pro | Clinical Decision Support by Dr. Jaehee Lee")
