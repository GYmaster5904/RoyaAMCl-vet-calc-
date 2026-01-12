import streamlit as st

# --- [1. 디자인: 시인성 확보를 위한 전역 CSS 강제 설정] ---
st.set_page_config(page_title="로얄동물메디컬센터 임상지원 v36", layout="wide")

st.markdown("""
    <style>
    /* 다크모드 무시: 배경 흰색, 글자 검정색 고정 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    .stMarkdown, p, span, label, div, h1, h2, h3, h4, li {
        color: #000000 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    /* 입력창 디자인: 시인성 극대화 */
    input, select {
        background-color: #F8FAFC !important;
        color: #000000 !important;
        border: 2px solid #1E3A8A !important;
        font-size: 18px !important;
        font-weight: 700 !important;
    }
    /* 결과 강조 카드 */
    .result-card {
        background-color: #F8FAFC; padding: 25px; border-radius: 15px;
        border: 1px solid #CBD5E1; border-left: 12px solid #2563EB; margin-bottom: 20px;
    }
    .text-huge { font-size: 48px !important; font-weight: 900; color: #059669 !important; }
    .text-mid { font-size: 26px !important; font-weight: 800; color: #1E3A8A !important; }
    
    /* SOP 공지 배너 */
    .sop-banner {
        background-color: #1E293B; color: white !important; padding: 20px; border-radius: 12px;
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
    "KCl": 2.0, # mEq/mL
    "Calcium Gluconate": 100.0, # 10%, mg/mL
    "Sodium Bicarbonate": 1.0, # mEq/mL
    "Magnesium Sulfate": 500.0, # 50%, mg/mL
    "KP": 3.0 # K-Phosphate, mmol P/mL (4.4 mEq K/mL 동반)
}

AA_DB = {
    "후라바솔 10% (고용량)": 0.1,
    "후라바소레-페파 6.5% (간질환)": 0.065,
    "네프리솔 5.6% (신장질환)": 0.056
}

# --- [3. 사이드바 - 환자 고정 데이터] ---
with st.sidebar:
    st.header("📋 Patient Profile")
    species_m = st.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
    weight_m = st.number_input("체중 (kg)", 0.1, 150.0, 3.1, 0.1, format="%.1f")
    st.markdown("---")
    st.caption("Clinical Protocol Architect")
    st.markdown("### **Dr. Jaehee Lee**")

# --- [4. 메인 대시보드] ---
st.title("🛡️ RAMC Advanced Clinical Intelligence System")

tabs = st.tabs(["🧪 전해질/삼투압 조제", "💧 수액 & 아미노산", "💉 CRI 조제", "🩸 수혈"])

# --- TAB 1: 전해질/삼투압 & 베이스 수액 추천 ---
with tabs[0]:
    st.header("🧪 Electrolyte Correction & Compound Recipe")
    col_e1, col_e2, col_e3 = st.columns([1.2, 1, 1.2])
    
    with col_e1:
        st.subheader("1. 검사 수치 입력")
        na_v = st.number_input("Na+ (mEq/L)", 100.0, 200.0, 145.0)
        k_v = st.number_input("K+ (mEq/L)", 1.0, 10.0, 4.0)
        ica_v = st.number_input("iCa (mmol/L)", 0.5, 2.0, 1.25)
        hco3_v = st.number_input("HCO3- (mEq/L)", 5.0, 40.0, 20.0)
        mg_v = st.number_input("Mg (mg/dL)", 0.5, 5.0, 2.0)
        glu_v = st.number_input("Glucose (mg/dL)", 10.0, 1000.0, 100.0)
        bun_v = st.number_input("BUN (mg/dL)", 5.0, 300.0, 20.0)
        bag_s = st.selectbox("수액 백/시린지 용량 (mL)", [30, 50, 100, 250, 500, 1000], index=4)

    with col_e2:
        st.subheader("2. 임상 평가 및 베이스 추천")
        c_na = na_v + 1.6*((glu_v-100)/100) if glu_v > 100 else na_v
        osmo = 2*(na_v+k_v) + (glu_v/18) + (bun_v/2.8)
        
        # 베이스 수액 추천 로직
        if c_na > 155: 
            rec_fluid = "0.45% NS + 2.5% DW (저장성)"
            color = "#EF4444"
        elif c_na < 135: 
            rec_fluid = "0.9% NaCl (등장성/고나트륨)"
            color = "#2563EB"
        else: 
            rec_fluid = "Plasmasol-목표 (등장성)"
            color = "#059669"

        st.markdown(f"""<div class="result-card" style="border-left-color:{color};">
        <b>추천 베이스 수액:</b><br><span style="font-size:22px; color:{color}; font-weight:bold;">{rec_fluid}</span><hr>
        <b>Corrected Na+:</b> {c_na:.1f} mEq/L<br>
        <b>Osmolality:</b> {osmo:.1f} mOsm/kg
        </div>""", unsafe_allow_html=True)

    with col_e3:
        st.subheader("3. 정밀 보정 레시피")
        # 1. K 보정
        k_map = {2.0: 80, 2.5: 60, 3.0: 40, 3.5: 28}
        t_k = next((v for lim, v in k_map.items() if k_v <= lim), 10)
        k_ml = (t_k * bag_s / 1000) / 2.0
        
        # 2. HCO3 결핍 (목표 22)
        h_def = max(0.0, 0.3 * weight_m * (22 - hco3_v))
        
        # 3. iCa 보정 (iCa < 1.0 일 때 bolus 제안)
        ca_bolus = weight_m * 0.5 if ica_v < 1.0 else 0.0
        
        st.markdown(f"""<div class="result-card" style="border-left-color:#10B981;">
        <p><b>[ {bag_s}mL 조제법 ]</b></p>
        <b>KCl (2mEq/ml):</b> <span style="color:#2563EB;">Add {k_ml:.1f} mL</span><br>
        <b>HCO3- (1mEq/ml):</b> <span style="color:#DC2626;">Deficit {h_def:.1f} mEq</span><br>
        <b>Mg-Sulfate:</b> <span style="color:#4B5563;">{('저마그네슘혈증 주의' if mg_v < 1.5 else '정상')}</span><br>
        <b>iCa Bolus:</b> <span style="color:#EAB308;">{ca_bolus:.1f} mL (10%)</span>
        </div>""", unsafe_allow_html=True)

# --- TAB 2: 수액 및 아미노산 ---
with tabs[1]:
    st.markdown('<div class="sop-banner"><h3>RER = BW × 50 kcal/day</h3><p>💡 표준 유지: 40-60 mL/kg/day</p></div>', unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    with f1:
        st.subheader("💧 수액 속도 계산")
        mr = st.slider("유지 (mL/kg/hr)", 1.0, 4.0, 2.0)
        loss = st.number_input("지속 손실 (mL/day)", value=float(round(weight_m*1.0, 1)))
        st.metric("최종 수액 속도", f"{(weight_m * mr) + (loss / 24):.1f} mL/h")
    
    with f2:
        st.subheader("🧬 아미노산 보충량 (Target Protein)")
        cond = st.selectbox("질환", ["악액질 (1.5)", "CKD 개 (0.7)", "CKD 고양이 (0.9)", "간-No HE (개 1.4/고양 2.3)", "간+HE (0.7)"])
        target_p = 1.5
        if "CKD 개" in cond: target_p = 0.7
        elif "CKD 고양이" in cond: target_p = 0.9
        elif "간-No HE" in cond: target_p = 1.4 if species_m == "개(Canine)" else 2.3
        elif "간+HE" in cond: target_p = 0.7
        
        intake = st.number_input("식이 단백질 섭취 (g/kg/day)", 0.0, 5.0, 0.0)
        prod = st.selectbox("제제", list(AA_DB.keys()))
        aa_ml = max(0.0, (target_p - intake) * weight_m) / AA_DB[prod]
        
        st.markdown(f"""<div class="result-card" style="border-left-color:#3B82F6;">
        <b>일일 아미노산 보충량</b><br><span class="text-huge">Add {aa_ml:.1f} mL</span><br>
        <p>농도 {int(AA_DB[prod]*100)}% 기준</p></div>""", unsafe_allow_html=True)

# --- TAB 3: CRI 조제 (안정화) ---
with tabs[2]:
    st.header("💉 CRI High-Visibility Recipe")
    drug = st.selectbox("약물 선택", ["Butorphanol", "Midazolam", "Dexmedetomidine", "Epinephrine", "Norepinephrine", "Dopamine", "Furosemide", "Insulin(RI)"])
    cr1, cr2 = st.columns([1, 2])
    with cr1:
        ir = st.number_input("설정 속도 (mL/h)", 0.1, 50.0, 0.5)
        td = st.number_input("목표 용량", 0.0, 50.0, 0.1, format="%.3f")
        sv = st.selectbox("시린지/백 용량 (mL)", [10, 20, 30, 50, 100], index=3)
    with cr2:
        mgh = (td * weight_m * 60 / 1000) if drug in ["Epinephrine", "Norepinephrine", "Dopamine"] else (td * weight_m)
        dml = (mgh / STOCK_DB[drug]) * sv / ir
        st.markdown(f"""<div class="result-card" style="border-left-color:#10B981;">
        <span class="text-mid">🚩 {drug} 속도: {ir:.1f} mL/h</span><br>
        <span class="text-huge">원액 {dml:.2f} mL</span><br>
        <span class="text-mid">희석액 {(sv-dml):.2f} mL</span></div>""", unsafe_allow_html=True)

# --- TAB 4: 수혈 ---
with tabs[3]:
    st.header("🩸 Blood Transfusion")
    tx1, tx2 = st.columns(2)
    with tx1:
        cp = st.number_input("현재 PCV", 1.0, 50.0, 15.0); tp = st.number_input("목표 PCV", 1.0, 50.0, 25.0)
        pr = st.radio("제제", ["전혈", "pRBC"], horizontal=True)
        kv = 90 if species_m == "개(Canine)" else 60
        res = weight_m * kv * ((tp - cp) / (40.0 if pr == "전혈" else 70.0))
        st.metric("필요 수혈량", f"{max(0.0, round(res, 1))} mL")
    with tx2: st.info("SOP: 초기 0.25-0.5ml/kg/hr. 4시간 완료 원칙.")

st.divider()
st.caption(f"Royal Animal Medical Center | v36.0 ICU Intelligence | Protocol by Dr. Jaehee Lee")
