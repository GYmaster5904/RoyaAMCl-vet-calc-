import streamlit as st

# --- [1. 페이지 설정 및 디자인 주입] ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc Pro", layout="wide")

# CSU 스타일의 세련된 디자인을 위한 CSS 주입
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stApp { color: #2c3e50; }
    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #1e3a8a;
        margin-bottom: 20px;
    }
    .emergency-card {
        background-color: #fff5f5;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #e11d48;
        margin-bottom: 10px;
    }
    .formula-box {
        background-color: #1e293b;
        color: #f8fafc;
        padding: 15px;
        border-radius: 8px;
        font-family: 'Courier New', Courier, monospace;
        margin-bottom: 20px;
    }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 데이터베이스] ---
DRUG_CRI_DATA = {
    "a. 진통/진정/항경련": {
        "Butorphanol": {"conc": 2.0, "unit": "mg/kg/h", "diluent": "NS / LRS", "compat": "대부분의 수액과 혼합 가능."},
        "Midazolam": {"conc": 1.0, "unit": "mg/kg/h", "diluent": "NS / 5%DW", "compat": "알칼리성 약물과 혼합 시 침전 주의."},
        "Diazepam": {"conc": 5.0, "unit": "mg/kg/h", "diluent": "원액 권장", "compat": "플라스틱 흡착 심함."},
        "Dexmedetomidine": {"conc": 0.118, "unit": "mg/kg/h", "diluent": "NS", "compat": "심각한 서맥 주의."},
        "Propofol": {"conc": 10.0, "unit": "mg/kg/h", "diluent": "원액전용", "compat": "희석 금지. 개봉 6시간 내 폐기."}
    },
    "b. 심혈관계/승압제": {
        "Epinephrine": {"conc": 1.0, "unit": "mcg/kg/min", "diluent": "5%DW 권장", "compat": "Bicarb와 혼합 금지."},
        "Norepinephrine": {"conc": 2.0, "unit": "mcg/kg/min", "diluent": "5%DW 필수", "compat": "LRS 혼합 금지."},
        "Dopamine": {"conc": 32.96, "unit": "mcg/kg/min", "diluent": "NS / 5%DW", "compat": "알칼리 용액 혼합 금지."},
        "Dobutamine": {"conc": 50.0, "unit": "mcg/kg/min", "diluent": "NS / 5%DW", "compat": "Bicarb와 혼합 금지."}
    },
    "c. 전해질 및 기타": {
        "Calcium Gluconate": {"conc": 100.0, "unit": "mg/kg/h", "diluent": "NS / 5%DW", "compat": "LRS와 절대 혼합 금지."},
        "KP(Potassium Phosphate)": {"conc": 3.0, "unit": "mmol/kg/h", "diluent": "NS / 5%DW", "compat": "Ca, Mg와 혼합 시 침전."},
        "Mg-Sulfate": {"conc": 500.0, "unit": "mg/kg/h", "diluent": "NS / 5%DW", "compat": "Phosphate와 침전 주의."},
        "Insulin(RI)": {"conc": 1.0, "unit": "U/kg/h", "diluent": "NS", "compat": "첫 50mL 라인 세척 필수."},
        "Furosemide": {"conc": 10.0, "unit": "mg/kg/h", "diluent": "NS", "compat": "산성 수액과 침전 발생."}
    }
}

DIET_DATA = {
    "Royal Canin (처방식)": {
        "Recovery (Wet, 100g)": 105, "Gastrointestinal (Dry)": 3912, "Gastrointestinal (Wet, 400g)": 432,
        "GI Low Fat (Dry)": 3461, "GI Low Fat (Wet, 410g)": 385, "Urinary S/O (Dry)": 3884, "Renal (Dry)": 3988
    },
    "Hill's (Prescription Diet)": {
        "a/d Urgent Care (Wet, 156g)": 183, "i/d Digestive Care (Dry)": 3663, "i/d (Wet, 156g)": 155,
        "k/d Kidney Care (Dry)": 4220, "c/d Multicare (Dry)": 3873
    }
}

DISEASE_FACTORS = {
    "기본/비만": {"성장기(2-12m)": 2.0, "중성화 성견/성묘": 1.2, "미중성화": 1.4, "비만감량": 0.8, "저활동": 1.0},
    "신장/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전/이뇨제": 1.05},
    "췌장/간/소화기": {"췌장염 안정": 1.1, "간질환 안정기": 1.15, "고양이 지방간(HL)": 1.35, "EPI": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

# --- [3. 사이드바: CSU 스타일 고정] ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50.png?text=ROYAL+AM&text=ROYAL+ANIMAL", use_container_width=True) # 로고 대체
    st.header("🐾 환자 정보 입력")
    species = st.selectbox("품종(Species)", ["개(Canine)", "고양이(Feline)"])
    weight = st.number_input("체중 (kg)", min_value=0.1, value=3.07, step=0.01)
    
    st.subheader("🏥 환자 상태 설정")
    cat_n = st.selectbox("질환 카테고리", list(DISEASE_FACTORS.keys()))
    selected_sub_cat = st.selectbox("세부 상태 선택", list(DISEASE_FACTORS[cat_n].keys()))
    
    st.markdown("---")
    st.caption("Clinical Protocol Architect")
    st.markdown("### Dr. Jaehee Lee")

# --- [4. 메인 대시보드] ---
st.title("로얄동물메디컬센터 Clinical Support System")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚨 응급/CPCR", "🍽️ 영양/급여", "💧 수액 요법", "💉 CRI 조제", "🩸 수혈/감시"])

# --- TAB 1: 응급/CPCR (CSU 스타일 레이아웃) ---
with tab1:
    st.header("🚨 CPR Emergency Protocol (CSU/RECOVER)")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.subheader("💊 Emergency Drugs")
        def drug_box(name, vol, dose, unit):
            st.markdown(f"""<div class="emergency-card"><b>{name}</b><br><span style="font-size:20px; color:#e11d48;">{vol:.2f} mL</span><br><small>{dose}{unit}</small></div>""", unsafe_allow_html=True)
        
        drug_box("Epinephrine (Low)", (weight*0.01)/1.0, 0.01, "mg/kg")
        drug_box("Atropine", (weight*0.04)/0.5, 0.04, "mg/kg")
        drug_box("Vasopressin", (weight*0.8)/20.0, 0.8, "U/kg")

    with c2:
        st.subheader("💓 Anti-Arrhythmics")
        drug_box("Lidocaine (Dog)", (weight*2.0)/20.0, 2.0, "mg/kg")
        drug_box("Amiodarone", (weight*5.0)/50.0, 5.0, "mg/kg")
        drug_box("Esmolol", (weight*0.5)/10.0, 0.5, "mg/kg")

    with c3:
        st.subheader("⚡ Defibrillation")
        st.markdown(f"""
        <div class="result-card" style="border-left-color:#f59e0b;">
            <p><b>Biphasic Setting</b></p>
            <h2 style="color:#f59e0b; margin:0;">{weight*2:.1f} ~ {weight*4:.1f} J</h2>
            <small>2 - 4 J/kg</small>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Checklist:**\n- 2분 압박 중단 금지\n- 10회/분 Ventilation\n- 즉시 압박 재개")

# --- TAB 2: 영양/급여 (세련된 계산기) ---
with tab2:
    st.header("🍽️ Nutritional Planning")
    st.markdown('<div class="formula-box">Standard Formula: RER = BW(kg) × 50 kcal/day</div>', unsafe_allow_html=True)
    
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        rer = weight * 50
        f_val = DISEASE_FACTORS[cat_n][selected_sub_cat]
        if st.checkbox("입원 환자 가중치 적용 (×1.1)", value=True): f_val *= 1.1
        der = rer * f_val
        st.metric("최종 목표 DER", f"{der:.0f} kcal/day")
        
        strat = st.radio("급여 전략", ["3단계", "4단계", "5단계"], horizontal=True)
        s_map = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        curr_s = st.select_slider("단계 선택", options=s_map[strat], value=s_map[strat][-1])

    with col_n2:
        brand = st.selectbox("사료 브랜드", list(DIET_DATA.keys()))
        prod = st.selectbox("제품 선택", list(DIET_DATA[brand].keys()))
        kcal = DIET_DATA[brand][prod]
        unit = "can" if "Wet" in prod or "파우치" in prod else "g"
        amt = ((der * curr_s) / kcal) * (1 if unit == "can" else 1000)
        
        st.markdown(f"""
        <div class="result-card">
            <p><b>일일 권장 급여량 ({(curr_s*100):.0f}%)</b></p>
            <h2 style="color:#1e3a8a; margin:0;">{amt:.1f} {unit}</h2>
            <small>{prod} ({kcal} kcal/{unit})</small>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 3: 수액 요법 (교차 검증 가이드) ---
with tab3:
    st.header("💧 Fluid Therapy (Dry Mode & AAHA)")
    st.markdown('<div class="formula-box">표준 유지 요구량: 40-60 mL/kg/day (약 2-3 mL/kg/h)</div>', unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns([1.5, 1])
    with col_f1:
        mode = st.radio("상황 선택", ["Dry Mode 입원", "AAHA 2024 마취"], horizontal=True)
        if mode == "Dry Mode 입원":
            m_rate = st.slider("유지 용량 (mL/kg/hr)", 1.0, 4.0, 2.0, 0.5)
            dehy = st.number_input("탈수 (%)", 0, 15, 0)
            loss = st.number_input("지속 손실 (mL/day)", 0)
            total_f = (weight * m_rate) + ((weight * dehy * 10) / 12) + (loss / 24)
            st.metric("최종 수액 속도", f"{total_f:.1f} mL/h")
        else:
            anes = (weight * 5) if species == "개(Canine)" else (weight * 3)
            st.metric("마취 중 수액 속도", f"{anes:.1f} mL/h")

    with col_f2:
        st.subheader("⚠️ Clinical Guide")
        if "심장" in selected_sub_cat:
            st.error("심장 질환: 수액 과부하 고위험군. 호흡수 감시 필수.")
        elif "췌장" in selected_sub_cat:
            st.error("췌장염: Ongoing Loss 실시간 반영 및 전해질 교정.")
        else:
            st.info("사이드바에서 선택한 질환에 따라 가이드가 표시됩니다.")

# --- TAB 4: CRI 조제 (CSU 스타일 표 레이아웃) ---
with tab4:
    st.header("💉 CRI Recipe & Compatibility")
    c_cat = st.selectbox("CRI 카테고리", list(DRUG_CRI_DATA.keys()))
    c_drug = st.selectbox("약물 선택", list(DRUG_CRI_DATA[c_cat].keys()))
    info = DRUG_CRI_DATA[c_cat][c_drug]
    
    col_c1, col_c2 = st.columns([1, 2])
    with col_c1:
        i_rate = st.number_input("펌프 속도 (mL/h)", 0.1, 50.0, 0.5, 0.1)
        t_dose = st.number_input(f"목표 용량 ({info['unit']})", value=0.1 if "mg" in info['unit'] else 0.01, format="%.3f")
        s_vol = st.selectbox("시린지 볼륨 (mL)", [10, 20, 50], index=2)
    
    with col_c2:
        mg_h = (t_dose * weight * 60) / 1000 if "mcg" in info['unit'] else (t_dose * weight)
        d_ml = ((mg_h / i_rate) * s_vol) / info['conc']
        
        st.markdown(f"""
        <div class="result-card" style="border-left-color:#10b981;">
            <p><b>{c_drug} 조제 레시피</b></p>
            <h3 style="color:#10b981;">속도: {i_rate} mL/h</h3>
            <p><b>원액: {d_ml:.2f} mL</b> | <b>희석액: {(s_vol-d_ml):.2f} mL</b></p>
            <small><b>권장 희석액:</b> {info['diluent']}</small><br>
            <small><b>Compatibility:</b> {info['compat']}</small>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 5: 수혈 및 모니터링 ---
with tab5:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("🩸 Transfusion")
        prod = st.radio("혈액 제제", ["전혈", "pRBC"], horizontal=True)
        c_p = st.number_input("현재 PCV", 1.0, 50.0, 15.0)
        t_p = st.number_input("목표 PCV", 1.0, 50.0, 25.0)
        k_vt = 90 if species == "개(Canine)" else 60
        d_p = 40.0 if prod == "전혈" else 70.0
        tx_v = weight * k_vt * ((t_p - c_p) / d_p)
        st.metric("필요 수혈량", f"{max(0.0, round(tx_v, 1))} mL")
    
    with col_t2:
        st.subheader("⚠️ Monitoring (AAHA 2024)")
        st.markdown("""
        - **Chemosis / 비루 확인**
        - **RR 20% 이상 증가 시 폐수종 경고**
        - **체중 10% 이상 증가 시 즉시 감량**
        """)

st.divider()
st.caption("Royal Animal Medical Center | v11.0 Pro | Powered by Dr. Jaehee Lee")
