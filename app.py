import streamlit as st

# --- [1. 디자인: 선택창 블랙박스 및 시인성 문제 완전 해결 CSS] ---
st.set_page_config(page_title="로얄동물메디컬센터 임상지원 v37", layout="wide")

st.markdown("""
    <style>
    /* 1. 전체 배경 및 기본 텍스트 강제 고정 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        color: #111827 !important;
    }
    
    /* 2. 모든 텍스트 요소를 검은색으로 강제 */
    .stMarkdown, p, span, label, div, h1, h2, h3, h4, li {
        color: #111827 !important;
    }

    /* 3. [VITAL] 선택창(Selectbox) 및 드롭다운 리스트 시인성 해결 */
    /* 선택 전/후의 위젯 배경 및 글자색 강제 */
    div[data-baseweb="select"] > div {
        background-color: #F1F5F9 !important;
        color: #000000 !important;
    }
    
    /* 드롭다운 메뉴(리스트 박스) 내부 색상 강제 */
    div[role="listbox"] ul {
        background-color: #FFFFFF !important;
    }
    div[role="listbox"] li {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    /* 마우스 호버(올렸을 때) 색상 */
    div[role="listbox"] li:hover {
        background-color: #E2E8F0 !important;
    }

    /* 4. 결과 강조 카드 */
    .result-card {
        background-color: #F8FAFC !important;
        padding: 25px; border-radius: 15px;
        border: 1px solid #CBD5E1; border-left: 12px solid #2563EB; margin-bottom: 20px;
    }
    .text-huge { font-size: 48px !important; font-weight: 900; color: #059669 !important; }
    .text-mid { font-size: 26px !important; font-weight: 800; color: #1E3A8A !important; }
    
    /* SOP 배너 */
    .sop-banner {
        background-color: #1E293B !important; color: white !important; padding: 20px; border-radius: 12px;
        border-left: 10px solid #EF4444; margin-bottom: 25px;
    }
    .sop-banner h3, .sop-banner p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 로얄 표준 데이터베이스] ---
STOCK_DB = {
    "Butorphanol": 2.0, "Midazolam": 1.0, "Dexmedetomidine": 0.118,
    "Epinephrine": 1.0, "Norepinephrine": 2.0, "Dopamine": 32.96,
    "Furosemide": 10.0, "Insulin(RI)": 1.0, 
    "KCl": 2.0, "Calcium Gluconate": 100.0, "Sodium Bicarbonate": 1.0,
    "Magnesium Sulfate": 500.0, "KP": 3.0 # mmol P/mL
}

AA_DB = {
    "후라바솔 10% (고용량)": 0.1,
    "후라바소레-페파 6.5% (간질환용)": 0.065,
    "네프리솔 5.6% (신장질환용)": 0.056
}

# --- [3. 사이드바 - 환자 데이터] ---
with st.sidebar:
    st.header("📋 Patient Profile")
    species_idx = st.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
    weight_val = st.number_input("체중 (kg)", 0.1, 150.0, 3.1, 0.1, format="%.1f")
    st.markdown("---")
    st.caption("Clinical Protocol Architect")
    st.markdown("### **Dr. Jaehee Lee**")

# --- [4. 메인 탭 구성] ---
tabs = st.tabs(["🧪 전해질/삼투압 조제", "💧 수액 & 아미노산", "💉 CRI 조제", "🩸 수혈"])

# --- TAB 1: 전해질/삼투압 및 정밀 보정 ---
with tabs[0]:
    st.header("🧪 Electrolyte Correction & Base Fluid Recommendation")
    c_e1, c_e2, c_e3 = st.columns([1.2, 1, 1.2])
    
    with c_e1:
        st.subheader("1. 검사 수치")
        na_v = st.number_input("Na+ (mEq/L)", 100.0, 200.0, 145.0)
        k_v = st.number_input("K+ (mEq/L)", 1.0, 10.0, 4.0)
        ica_v = st.number_input("iCa (mmol/L)", 0.5, 2.0, 1.25)
        hco3_v = st.number_input("HCO3- (mEq/L)", 5.0, 40.0, 20.0)
        mg_v = st.number_input("Mg (mg/dL)", 0.5, 5.0, 2.0)
        glu_v = st.number_input("Glucose (mg/dL)", 10.0, 1000.0, 100.0)
        bun_v = st.number_input("BUN (mg/dL)", 5.0, 300.0, 20.0)
        bag_v = st.selectbox("수액 백/시린지 용량 (mL)", [30, 50, 100, 250, 500, 1000], index=4)

    with c_e2:
        st.subheader("2. 임상 평가")
        # 평가 로직
        corr_na = na_v + 1.6*((glu_v-100)/100) if glu_v > 100 else na_v
        osmo = 2*(na_v+k_v) + (glu_v/18) + (bun_v/2.8)
        
        if corr_na > 155: rec_f, rec_c = "0.45% NS + 2.5% DW (저장성)", "#EF4444"
        elif corr_na < 135: rec_f, rec_c = "0.9% NaCl (등장성/고나트륨)", "#2563EB"
        else: rec_f, rec_c = "Plasmasol (등장성 평형)", "#059669"

        st.markdown(f"""<div class="result-card" style="border-left-color:{rec_c};">
        <b>추천 베이스 수액:</b><br><span style="font-size:22px; color:{rec_c}; font-weight:bold;">{rec_f}</span><hr>
        <b>Corrected Na+:</b> {corr_na:.1f}<br><b>Osmolality:</b> {osmo:.1f}
        </div>""", unsafe_allow_html=True)

    with c_e3:
        st.subheader("3. 보정 레시피")
        # K 보정
        k_map = {2.0: 80, 2.5: 60, 3.0: 40, 3.5: 28}
        t_k = next((v for l, v in k_map.items() if k_v <= l), 10)
        k_ml = (t_k * bag_v / 1000) / 2.0
        # HCO3 결핍
        h_def = max(0.0, 0.3 * weight_val * (22 - hco3_v))
        # iCa Bolus
        ca_bol = weight_val * 0.5 if ica_v < 1.0 else 0.0
        
        st.markdown(f"""<div class="result-card" style="border-left-color:#10B981;">
        <p><b>[ {bag_v}mL 조제 안내 ]</b></p>
        <b>KCl (2mEq/ml):</b> Add {k_ml:.1f} mL<br>
        <b>HCO3- (1mEq/ml):</b> Deficit {h_def:.1f} mEq<br>
        <b>iCa Bolus (10%):</b> {ca_bol:.1f} mL
        </div>""", unsafe_allow_html=True)

# --- TAB 2: 수액 및 아미노산 ---
with tabs[1]:
    st.markdown('<div class="sop-banner"><h3>RER = BW × 50 kcal/day</h3><p>💡 표준 유지: 40-60 mL/kg/day</p></div>', unsafe_allow_html=True)
    f_c1, f_c2 = st.columns(2)
    with f_c1:
        st.subheader("💧 수액 속도")
        mr_s = st.slider("유지계수", 1.0, 4.0, 2.0)
        loss_s = st.number_input("지속 손실 (mL/day)", value=float(round(weight_val*1.0, 1)))
        st.metric("최종 수액 속도", f"{(weight_val * mr_s) + (loss_s / 24):.1f} mL/h")
    
    with f_col2_tab2 := f_c2: # 변수 충돌 방지용
        st.subheader("🧬 질환별 아미노산 보충량")
        aa_c = st.selectbox("질환 상태", ["악액질 (1.5)", "CKD 개 (0.7)", "CKD 고양이 (0.9)", "간-No HE (개 1.4/고양 2.3)", "간+HE (0.7)"])
        t_p = 1.5
        if "CKD 개" in aa_c: t_p = 0.7
        elif "CKD 고양이" in aa_c: t_p = 0.9
        elif "간-No HE" in aa_c: t_p = 1.4 if species_idx == "개(Canine)" else 2.3
        elif "간+HE" in aa_c: t_p = 0.7
        
        in_p = st.number_input("단백질 섭취량 (g/kg/day)", 0.0, 5.0, 0.0)
        aa_p = st.selectbox("아미노산 제제", list(AA_DB.keys()))
        aa_ml_res = max(0.0, (t_p - in_p) * weight_val) / AA_DB[aa_p]
        
        st.markdown(f"""<div class="result-card" style="border-left-color:#3B82F6;">
        <b>일일 아미노산 보충량</b><br><span class="text-huge">Add {aa_ml_res:.1f} mL</span></div>""", unsafe_allow_html=True)

# --- TAB 3: CRI 조제 ---
with tabs[2]:
    st.header("💉 High-Visibility CRI Recipe")
    dr_sel = st.selectbox("CRI 약물", ["Butorphanol", "Midazolam", "Dexmedetomidine", "Epinephrine", "Norepinephrine", "Dopamine", "Furosemide", "Insulin(RI)"])
    cr_c1, cr_c2 = st.columns([1, 2])
    with cr_c1:
        ir_s = st.number_input("펌프 속도 (mL/h)", 0.1, 50.0, 0.5)
        td_s = st.number_input("목표 용량", 0.0, 50.0, 0.1, format="%.3f")
        sv_s = st.selectbox("시린지/백 용량 (mL)", [10, 20, 30, 50, 100, 250, 500])
    with cr_c2:
        mgh_s = (td_s * weight_val * 60 / 1000) if dr_sel in ["Epinephrine", "Norepinephrine", "Dopamine"] else (td_s * weight_val)
        dml_s = (mgh_s / STOCK_DB[dr_sel]) * sv_s / ir_s
        st.markdown(f"""<div class="result-card" style="border-left-color:#10B981;">
        <span class="text-mid">🚩 {dr_sel} 속도: {ir_s:.1f} mL/h</span><br>
        <span class="text-huge">원액 {dml_s:.2f} mL</span><br>
        <span class="text-mid">희석액 {(sv_s-dml_s):.2f} mL</span></div>""", unsafe_allow_html=True)

# --- TAB 4: 수혈 ---
with tabs[3]:
    st.header("🩸 Blood Transfusion")
    tx1, tx2 = st.columns(2)
    with tx1:
        c_pcv = st.number_input("현재 PCV", 1.0, 50.0, 15.0); t_pcv = st.number_input("목표 PCV", 1.0, 50.0, 25.0)
        tx_p = st.radio("제제", ["전혈", "pRBC"], horizontal=True)
        tx_res = weight_val * (90 if species_idx == "개(Canine)" else 60) * ((t_pcv - c_pcv) / (40.0 if tx_p == "전혈" else 70.0))
        st.metric("필요 수혈량", f"{max(0.0, round(tx_res, 1))} mL")
    with tx2: st.info("SOP: 초기 0.25-0.5ml/kg/hr. 4시간 완료 원칙.")

st.divider()
st.caption(f"Royal Animal Medical Center | v37.0 ICU Intelligence | Protocol by Dr. Jaehee Lee")
