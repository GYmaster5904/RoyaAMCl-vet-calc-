import streamlit as st

# --- [1. 데이터베이스: 사료, 약물 함량, 호환성] ---
DIET_DATA = {
    "Royal Canin (처방식)": {
        "Recovery (Wet, 100g)": 105, "Gastrointestinal (Dry)": 3912, "Gastrointestinal (Wet, 400g)": 432,
        "GI Low Fat (Dry)": 3461, "GI Low Fat (Wet, 410g)": 385, "Urinary S/O (Dry)": 3884,
        "Hepatic (Dry)": 3900, "Renal (Dry)": 3988, "Renal (Wet, 100g)": 110
    },
    "Hill's (Prescription Diet)": {
        "a/d Urgent Care (Wet, 156g)": 183, "i/d Digestive Care (Dry)": 3663, "i/d (Wet, 156g)": 155,
        "i/d Low Fat (Dry)": 3316, "i/d Low Fat (Wet, 370g)": 341, "k/d Kidney Care (Dry)": 4220, "c/d (Dry)": 3873
    }
}

DRUG_CRI_DATA = {
    "a. 진통/진정/항경련": {
        "Butorphanol": {"conc": 2.0, "unit": "mg/kg/h", "diluent": "NS / LRS", "compat": "대부분의 수액과 혼합 가능하나 단독 라인 권장."},
        "Midazolam": {"conc": 1.0, "unit": "mg/kg/h", "diluent": "NS / 5%DW", "compat": "알칼리성 약물과 혼합 시 침전 주의."},
        "Diazepam": {"conc": 5.0, "unit": "mg/kg/h", "diluent": "희석 비권장", "compat": "플라스틱 흡착 심함. 원액 단독 투여 권장."},
        "Dexmedetomidine": {"conc": 0.118, "unit": "mg/kg/h", "diluent": "NS", "compat": "심각한 서맥 주의."},
        "Propofol": {"conc": 10.0, "unit": "mg/kg/h", "diluent": "원액", "compat": "희석 금지. 개봉 6시간 내 폐기."}
    },
    "b. 심혈관계/승압제": {
        "Epinephrine": {"conc": 1.0, "unit": "mcg/kg/min", "diluent": "5%DW 권장", "compat": "Bicarb와 혼합 시 불활성화."},
        "Norepinephrine": {"conc": 2.0, "unit": "mcg/kg/min", "diluent": "5%DW 필수", "compat": "LRS 혼합 금지. 산화 방지를 위해 5%DW 필수."},
        "Dopamine": {"conc": 32.96, "unit": "mcg/kg/min", "diluent": "NS / 5%DW", "compat": "알칼리 용액 혼합 금지."},
        "Dobutamine": {"conc": 50.0, "unit": "mcg/kg/min", "diluent": "NS / 5%DW", "compat": "Bicarb와 혼합 금지."},
        "Vasopressin": {"conc": 20.0, "unit": "U/kg/h", "diluent": "NS / 5%DW", "compat": "단독 라인 권장."}
    },
    "c. 전해질 및 기타": {
        "Calcium Gluconate": {"conc": 100.0, "unit": "mg/kg/h", "diluent": "NS / 5%DW", "compat": "LRS(결정화) 및 Bicarb와 절대 혼합 금지."},
        "KP(Potassium Phosphate)": {"conc": 3.0, "unit": "mmol/kg/h", "diluent": "NS / 5%DW", "compat": "Ca, Mg와 혼합 시 침전 발생."},
        "Magnesium Sulfate": {"conc": 500.0, "unit": "mg/kg/h", "diluent": "NS / 5%DW", "compat": "Ca, Phosphate와 혼합 시 침전 주의."},
        "Magnesium Chloride": {"conc": 200.0, "unit": "mg/kg/h", "diluent": "NS / 5%DW", "compat": "Calcium과 병용 시 결정화 확인."},
        "Insulin(RI)": {"conc": 1.0, "unit": "U/kg/h", "diluent": "NS", "compat": "첫 20-50mL는 라인 세척 후 버리고 연결."},
        "Furosemide": {"conc": 10.0, "unit": "mg/kg/h", "diluent": "NS", "compat": "산성 수액과 혼합 시 침전 발생."}
    }
}

DISEASE_FACTORS = {
    "기본/비만": {"성장기(2-12m)": 2.0, "중성화 성견/성묘": 1.2, "미중성화": 1.4, "비만감량": 0.8, "저활동": 1.0},
    "신장/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전/이뇨제사용": 1.05},
    "췌장/간/소화기": {"췌장염 안정": 1.1, "간질환 안정기": 1.15, "고양이 지방간(HL)": 1.35, "EPI(췌장부전)": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

# --- [2. 페이지 설정 및 사이드바] ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc v10.1", layout="wide")
st.title("🐾 로얄동물메디컬센터 Clinical Support System")

st.sidebar.header("📋 Patient Info")
species = st.sidebar.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
weight = st.sidebar.number_input("체중 (kg)", min_value=0.1, value=3.07, step=0.01)

st.sidebar.markdown("---")
st.sidebar.subheader("🏥 Clinical Status")
cat_n = st.sidebar.selectbox("질환 카테고리", list(DISEASE_FACTORS.keys()))
selected_sub_cat = st.sidebar.selectbox("세부 상태", list(DISEASE_FACTORS[cat_n].keys()))

st.sidebar.markdown("---")
st.sidebar.caption("Clinical Protocol Architect")
st.sidebar.markdown("### **Dr. Jaehee Lee**")

# --- [3. 메인 기능 탭] ---
tabs = st.tabs(["🚨 CPCR/응급", "🍴 영양/급여 관리", "💧 수액 요법", "💉 CRI 조제 & Compatibility", "🩸 수혈", "⚠️ 모니터링"])

# --- TAB 1: CPCR & 부정맥 (CSU/RECOVER 기준) ---
with tabs[0]:
    st.header("🚨 Cardiopulmonary Resuscitation (CPCR)")
    col_c1, col_c2 = st.columns([1.2, 1])
    
    with col_c1:
        st.subheader("1. CPR Emergency Drugs (IV/IO)")
        cpr_doses = {
            "Epinephrine (Low Dose)": 0.01, "Epinephrine (High Dose)": 0.1,
            "Atropine": 0.04, "Vasopressin (U/kg)": 0.8
        }
        for name, dose in cpr_doses.items():
            s_name = "Epinephrine" if "Epinephrine" in name else (name.split(" (")[0] if " " in name else name)
            # Vasopressin 예외처리
            if "Vasopressin" in name: s_name = "Vasopressin"
            conc = 1.0 if s_name == "Epinephrine" else (0.5 if s_name == "Atropine" else 20.0)
            vol = (weight * dose) / conc
            st.error(f"**{name}**: {vol:.2f} mL")

        st.markdown("---")
        st.subheader("2. Anti-Arrhythmics (부정맥)")
        arr_doses = {"Lidocaine (Dog)": 2.0, "Amiodarone": 5.0, "Esmolol": 0.5}
        for name, dose in arr_doses.items():
            conc = 20.0 if "Lidocaine" in name else (50.0 if name == "Amiodarone" else 10.0)
            vol = (weight * dose) / conc
            st.warning(f"**{name}**: {vol:.2f} mL (Dose: {dose}mg/kg)")
        st.caption("※ 고양이는 Lidocaine 주의 (0.25-0.5mg/kg 감량 또는 Amiodarone 권장)")

    with col_c2:
        st.subheader("⚡ Defibrillation (제세동)")
        energy_low = weight * 2
        energy_high = weight * 4
        st.info(f"**Biphasic Setting:** {energy_low:.1f} ~ {energy_high:.1f} J (2-4 J/kg)")
        st.write(f"**Monophasic Setting:** {weight*4:.1f} ~ {weight*6:.1f} J (4-6 J/kg)")
        st.markdown("""
        **[CSU/RECOVER Key Point]**
        - 2분간 중단 없는 가슴 압박 (100-120회/분)
        - 10회/분 Ventilation (과호흡 금지)
        - 제세동 후 즉시 압박 재개
        """)

# --- TAB 2: 영양 관리 (RER BWx50) ---
with tabs[1]:
    col1, col2 = st.columns(2)
    with col1:
        st.header("1. DER 에너지 요구량")
        st.markdown("""
        <div style="background-color:#1e1e1e; padding:15px; border-radius:10px; border-left:5px solid #ff4b4b;">
            <p style="margin:0; color:white; font-size:16px;"><b>Royal Standard Formula:</b></p>
            <h3 style="margin:0; color:#ff4b4b;">RER = BW × 50 kcal/day</h3>
        </div>
        """, unsafe_allow_html=True)
        rer = weight * 50
        f_val = DISEASE_FACTORS[cat_n][selected_sub_cat]
        if st.checkbox("입원 환자 가중치 적용 (×1.1)", value=True): f_val *= 1.1
        der = rer * f_val
        st.success(f"### 최종 DER: **{der:.0f}** kcal/day")
        
        strategy = st.radio("급여 전략", ["3단계", "4단계", "5단계"], horizontal=True)
        s_map = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        curr_s = st.select_slider("단계(%)", options=s_map[strategy], value=s_map[strategy][-1])

    with col2:
        st.header("2. 일일 급여량")
        brand = st.selectbox("사료 브랜드", list(DIET_DATA.keys()))
        product = st.selectbox("제품 선택", list(DIET_DATA[brand].keys()))
        kcal_v = DIET_DATA[brand][product]
        unit = "can" if "Wet" in product or "파우치" in product else "g"
        amt = ((der * curr_s) / kcal_v) * (1 if unit == "can" else 1000)
        st.warning(f"### 급여량: **{amt:.1f} {unit}**")
        st.caption(f"기준 칼로리: {kcal_v} kcal / {unit}")

# --- TAB 3: 수액 요법 (AAHA 2024 & Royal Protocol) ---
with tabs[2]:
    st.markdown("""
    <div style="background-color:#e1f5fe; padding:10px; border-radius:5px; color:#01579b; margin-bottom:15px;">
        💡 <b>임상 표준 안내:</b> 성견/성묘 유지 범위 40-60 mL/kg/day (시간당 약 2-3 mL/kg)
    </div>
    """, unsafe_allow_html=True)
    mode = st.radio("상황 선택", ["로얄 Dry Mode (입원)", "AAHA 2024 쇼크", "AAHA 2024 마취"], horizontal=True)
    
    col3, col4 = st.columns(2)
    with col3:
        if "Dry Mode" in mode:
            st.header("로얄 표준 Dry Mode")
            m_rate = st.slider("유지 용량 기준 (mL/kg/hr)", 1.0, 4.0, 2.0, 0.5)
            dehy = st.number_input("탈수율 (%)", 0, 15, 0)
            loss = st.number_input("지속 손실 (mL/day)", 0)
            total_f = (weight * m_rate) + ((weight * dehy * 10) / 12) + (loss / 24)
            st.success(f"### 최종 수액 속도: **{total_f:.1f} mL/h**")
            st.caption(f"💡 불감수분 통제(1ml/kg/d) 포함 보수적 수치")
        elif "쇼크" in mode:
            vol = (weight * 15) if species == "개(Canine)" else (weight * 5)
            st.error(f"### 1차 Bolus 투여량: **{vol:.1f} mL** (15-30분)")
        else: # Anesthesia
            anes = (weight * 5) if species == "개(Canine)" else (weight * 3)
            st.success(f"### 마취 중 속도: **{anes:.1f} mL/h**")

    with col4:
        st.header("⚠️ 실시간 임상 가이드")
        if "심장" in selected_sub_cat:
            st.error("**[심장 질환군]** 수액 불내성 고위험군. 하한선(1.0mL/kg/h) 권장 및 RR 20% 증가 시 즉시 중단.")
        elif "췌장" in selected_sub_cat:
            st.error("**[췌장염]** Ongoing Loss를 정밀 반영하고 전해질(K, Mg) 보정 필수.")
        elif "간" in selected_sub_cat:
            st.error("**[간 질환]** 저알부민 확인 및 부종 시 20-30% 감량.")
        else:
            st.info("사이드바에서 질환을 선택하면 가이드가 여기에 나타납니다.")

# --- TAB 4: CRI 조제 & Compatibility ---
with tabs[3]:
    st.header("💉 CRI Recipe & Compatibility")
    col5, col6 = st.columns([1, 1.2])
    with col5:
        cat_c = st.selectbox("카테고리", list(DRUG_CRI_DATA.keys()))
        drug_c = st.selectbox("약물 선택", list(DRUG_CRI_DATA[cat_c].keys()))
        d_info = DRUG_CRI_DATA[cat_c][drug_c]
        i_rate = st.number_input("펌프 속도 고정 (mL/h)", 0.1, 50.0, 0.5, 0.1)
        t_dose = st.number_input(f"목표 용량 ({d_info['unit']})", value=0.1 if "mg" in d_info['unit'] else 0.01, format="%.3f")
        syr_v = st.selectbox("시린지 볼륨 (mL)", [10, 20, 50], index=2)
    with col6:
        mg_h = (t_dose * weight * 60) / 1000 if "mcg" in d_info['unit'] else (t_dose * weight)
        d_ml = ((mg_h / i_rate) * syr_v) / d_info['conc']
        st.subheader(f"👨‍🍳 {drug_c} 조제 가이드")
        if d_ml > syr_v: st.error("⚠️ 볼륨 초과!")
        else:
            st.info(f"**속도:** ### {i_rate} mL/h\n\n**원액:** **{d_ml:.2f} mL** | **희석액:** **{(syr_v - d_ml):.2f} mL**\n\n**희석액 종류: {d_info['diluent']}**")
            st.warning(f"⚠️ **Compatibility:** {d_info['compat']}")

# --- TAB 5: 수혈 ---
with tabs[4]:
    st.header("🩸 Blood Transfusion")
    t1, t2 = st.columns(2)
    with t1:
        prod = st.radio("제제", ["전혈", "pRBC"])
        c_p = st.number_input("현재 PCV (%)", 1.0, 50.0, 15.0)
        t_p = st.number_input("목표 PCV (%)", 1.0, 50.0, 25.0)
        d_p = st.number_input("혈액 PCV (%)", 1.0, 80.0, (40.0 if prod=="전혈" else 70.0))
    with t2:
        k_t = 90 if species == "개(Canine)" else 60
        tx_vol = weight * k_t * ((t_p - c_p) / d_p)
        st.error(f"### 예상 수혈량: **{max(0.0, round(tx_vol, 1))}** mL")
        st.info(f"K-계수 {k_t} 적용 (품종: {species})")

# --- TAB 6: 모니터링 ---
with tabs[5]:
    st.header("⚠️ Monitoring Checklist")
    st.markdown("""
    - **Chemosis & Nasal Discharge:** 수액 불내성의 가장 빠른 신호
    - **RR 증가:** 안정 시 대비 20% 증가 시 즉시 중단
    - **Body Weight:** 24시간 내 10% 이상 증가 시 수액 감량
    """)

st.divider()
st.caption("Royal Animal Medical Center | v10.1 | Clinical Solution by Dr. Jaehee Lee")
