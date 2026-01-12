import streamlit as st

# --- [1. 페이지 설정 및 디자인 CSS] ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc v12.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stApp { color: #1e293b; }
    /* CRI 조제 카드 스타일 */
    .cri-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #10b981;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        font-size: 16px;
        line-height: 1.6;
    }
    .speed-text { color: #10b981; font-weight: bold; font-size: 18px; }
    .recipe-text { color: #1e3a8a; font-weight: bold; font-size: 18px; }
    
    /* CPCR 섹션 스타일 */
    .cpr-section {
        background-color: #ffffff;
        padding: 15px;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .cpr-header {
        background-color: #f1f5f9;
        padding: 5px 10px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
        border-bottom: 2px solid #cbd5e1;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 데이터베이스: 로얄 표준 함량 및 사료] ---
STOCK_CONC = {
    "Epinephrine": 1.0, "Atropine": 0.5, "Vasopressin": 20.0,
    "Lidocaine": 20.0, "Amiodarone": 50.0, "Esmolol": 10.0,
    "Naloxone": 0.4, "Flumazenil": 0.1, "Atipamezole": 5.0,
    "Butorphanol": 2.0, "Midazolam": 1.0, "Diazepam": 5.0,
    "Dexmedetomidine": 0.118, "Dopamine": 32.96, "Dobutamine": 50.0,
    "Calcium Gluconate": 100.0, "KP": 3.0, "Mg-Sulfate": 500.0, "Mg-Chloride": 200.0,
    "Insulin(RI)": 1.0, "Furosemide": 10.0
}

DIET_DATA = {
    "Royal Canin": {
        "Recovery (Wet, 100g)": 105, "Gastrointestinal (Dry)": 3912, "Gastrointestinal (Wet, 400g)": 432,
        "GI Low Fat (Dry)": 3461, "GI Low Fat (Wet, 410g)": 385, "Urinary S/O (Dry)": 3884, "Renal (Dry)": 3988
    },
    "Hill's": {
        "a/d Urgent Care (Wet, 156g)": 183, "i/d Digestive Care (Dry)": 3663, "i/d (Wet, 156g)": 155,
        "k/d Kidney Care (Dry)": 4220, "c/d Multicare (Dry)": 3873
    }
}

DISEASE_FACTORS = {
    "기본/비만": {"성장기(2-12m)": 2.0, "중성화 성견/성묘": 1.2, "미중성화": 1.4, "비만감량": 0.8, "저활동": 1.0},
    "신장/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전/이뇨제사용": 1.05},
    "췌장/간/소화기": {"췌장염 안정": 1.1, "간질환 안정기": 1.15, "고양이 지방간(HL)": 1.35, "EPI(췌장부전)": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

# --- [3. 사이드바: 환자 기본 정보] ---
with st.sidebar:
    st.header("🐾 Patient Info")
    species = st.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
    weight = st.number_input("체중 (kg)", min_value=0.1, value=3.07, step=0.01)
    st.markdown("---")
    cat_n = st.selectbox("질환 카테고리", list(DISEASE_FACTORS.keys()))
    sub_cat = st.selectbox("세부 상태", list(DISEASE_FACTORS[cat_n].keys()))
    st.markdown("---")
    st.caption("Clinical Protocol Architect")
    st.markdown("### Dr. Jaehee Lee")

# --- [4. 메인 대시보드 탭 구성] ---
tabs = st.tabs(["🚨 CPCR", "🍴 영양/급여 관리", "💧 수액 요법", "💉 CRI 조제 & Compatibility", "🩸 수혈"])

# --- TAB 1: CPCR (CSU Style Layout) ---
with tabs[0]:
    st.markdown(f"### 🚨 CPCR Protocol for {weight}kg patient")
    
    # Reversals 상단 배치
    reversals = {
        "Naloxone": (weight * 0.04 / STOCK_CONC["Naloxone"]),
        "Flumazenil": (weight * 0.01 / STOCK_CONC["Flumazenil"]),
        "Atipamezole": (weight * 0.1 / STOCK_CONC["Atipamezole"])
    }
    st.markdown(f"**Reverse narcotics with:** Naloxone {reversals['Naloxone']:.2f}ml | Flumazenil {reversals['Flumazenil']:.2f}ml | Atipamezole {reversals['Atipamezole']:.2f}ml")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    
    with col_c1:
        st.markdown('<div class="cpr-header">Ventricular Fibrillation / VT</div>', unsafe_allow_html=True)
        st.write("**Defibrillation (Biphasic)**")
        st.error(f"External: {weight*2:.1f} - {weight*4:.1f} Joules")
        st.write(f"Internal: {weight*0.5:.1f} - {weight*1.0:.1f} Joules")
        st.caption("Provide 1 shock, then resume CPR for 120s")
        
        st.markdown("---")
        st.write("**If prolonged (>10 min):**")
        st.write(f"Epinephrine (L): {(weight*0.01):.2f} ml")
        st.write(f"Vasopressin: {(weight*0.8/20):.2f} ml")
        st.write(f"Amiodarone: {(weight*5/50):.2f} ml")
        if species == "개(Canine)":
            st.write(f"Lidocaine: {(weight*2/20):.2f} ml")

    with col_c2:
        st.markdown('<div class="cpr-header">Asystole / PEA / Bradycardia</div>', unsafe_allow_html=True)
        st.write("**Every other 2-min cycle:**")
        st.error(f"Epinephrine (Low): {(weight*0.01):.2f} ml")
        st.write("**OR**")
        st.write(f"Vasopressin: {(weight*0.8/20):.2f} ml")
        
        st.markdown("---")
        st.write("**Consider every other cycle:**")
        st.warning(f"Atropine: {(weight*0.04/0.5):.2f} ml")
        st.caption("Institue early if available: Transthoracic pacing")

    with col_c3:
        st.markdown('<div class="cpr-header">Intratracheal Doses (IT)</div>', unsafe_allow_html=True)
        st.write("Dose = 2x - 3x IV dose")
        st.info(f"Epinephrine: {(weight*0.01*2):.2f} ml")
        st.info(f"Atropine: {(weight*0.04*2/0.5):.2f} ml")
        st.info(f"Lidocaine: {(weight*2*2/20):.2f} ml")
        st.info(f"Naloxone: {(weight*0.04*2/0.4):.2f} ml")

# --- TAB 2: 영양 관리 ---
with tabs[1]:
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.header("1. Energy Requirements")
        st.markdown('<div style="background-color:#1e293b; color:white; padding:10px; border-radius:5px;">RER = BW × 50</div>', unsafe_allow_html=True)
        rer = weight * 50
        f_val = DISEASE_FACTORS[cat_n][sub_cat]
        if st.checkbox("입원 가중치(1.1) 적용", value=True): f_val *= 1.1
        der = rer * f_val
        st.metric("목표 DER", f"{der:.0f} kcal/day")
        strat = st.radio("급여 전략", ["3단계", "4단계", "5단계"], horizontal=True)
        s_map = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        curr_s = st.select_slider("단계 선택", options=s_map[strat], value=s_map[strat][-1])
    with col_n2:
        st.header("2. Feeding Plan")
        brand = st.selectbox("사료 브랜드", list(DIET_DATA.keys()))
        prod = st.selectbox("제품 선택", list(DIET_DATA[brand].keys()))
        kcal = DIET_DATA[brand][prod]
        unit = "can" if "Wet" in prod or "파우치" in prod else "g"
        amt = ((der * curr_s) / kcal) * (1 if unit == "can" else 1000)
        st.success(f"### 일일 급여량: {amt:.1f} {unit}")

# --- TAB 3: 수액 요법 (모니터링 통합) ---
with tabs[2]:
    st.header("💧 Fluid Therapy & Monitoring")
    col_f1, col_f2 = st.columns([1.5, 1])
    with col_f1:
        st.info("성견/성묘 유지 범위: 40-60 mL/kg/day (시간당 2-3 mL/kg)")
        m_rate = st.slider("유지 용량 (mL/kg/hr)", 1.0, 4.0, 2.0, 0.5)
        dehy = st.number_input("탈수율 (%)", 0, 15, 0)
        loss = st.number_input("지속 손실 (mL/day)", 0)
        total_f = (weight * m_rate) + ((weight * dehy * 10) / 12) + (loss / 24)
        st.metric("최종 수액 속도", f"{total_f:.1f} mL/h")
    with col_f2:
        st.subheader("⚠️ Monitoring (AAHA 2024)")
        st.markdown("""
        - **Chemosis / Serous Nasal Discharge**
        - **RR 20%↑** (안정 시 대비)
        - **Body Weight 10%↑** (24hr 내)
        - **Gallop Rhythm / Crackles**
        """)
        if "심장" in sub_cat: st.error("심장질환: 유지량 1.0-1.5ml/kg/h 권장")

# --- TAB 4: CRI 조제 & Compatibility (스타일 통일) ---
with tabs[3]:
    st.header("💉 CRI 조제 및 호환성")
    cat_cri = st.selectbox("카테고리", ["a. 진통/진정/항경련", "b. 심혈관계/승압제", "c. 전해질 및 기타"])
    # 내부 딕셔너리 구조에 맞춰 접근
    from itertools import chain
    drug_list = {**STOCK_CONC} # 약물 리스트는 상단 STOCK_CONC 참조
    selected_drug = st.selectbox("약물 선택", ["Butorphanol", "Midazolam", "Dexmedetomidine", "Epinephrine", "Norepinephrine", "Dopamine", "Calcium Gluconate", "Insulin(RI)", "Furosemide"])
    
    col_cri1, col_cri2 = st.columns([1, 2])
    with col_cri1:
        irate = st.number_input("펌프 속도 (mL/h)", 0.1, 50.0, 0.5, 0.1)
        tdose = st.number_input("목표 용량 (mg/kg/h 또는 mcg/kg/min)", value=0.1, format="%.3f")
        svol = st.selectbox("시린지 볼륨 (mL)", [10, 20, 50], index=2)
    
    with col_cri2:
        # 계산 로직 (에피, 노르, 도파민은 mcg 기준)
        is_mcg = selected_drug in ["Epinephrine", "Norepinephrine", "Dopamine"]
        mg_h = (tdose * weight * 60 / 1000) if is_mcg else (tdose * weight)
        dml = (mg_h / STOCK_CONC[selected_drug]) * svol / irate
        
        st.markdown(f"""
        <div class="cri-card">
            <b>{selected_drug} 조제 레시피</b><br>
            <span class="speed-text">속도: {irate} mL/h</span><br>
            <span class="recipe-text">원액: {dml:.2f} mL | 희석액: {(svol-dml):.2f} mL</span><br>
            <small>호환성: 각 약물별 특이사항 확인 필수</small>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 5: 수혈 (계산기 + 공지) ---
with tabs[4]:
    st.header("🩸 Blood Transfusion")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        prod = st.radio("제제", ["전혈", "pRBC"], horizontal=True)
        c_p = st.number_input("현재 PCV", 1.0, 50.0, 15.0)
        t_p = st.number_input("목표 PCV", 1.0, 50.0, 25.0)
        k_vt = 90 if species == "개(Canine)" else 60
        d_p = 40.0 if prod == "전혈" else 70.0
        tx_v = weight * k_vt * ((t_p - c_p) / d_p)
        st.metric("필요 수혈량", f"{max(0.0, round(tx_v, 1))} mL")
    with col_t2:
        st.info("""
        **[수혈 관리 공지]**
        1. **초기 속도:** 0.25~0.5 ml/kg/hr (첫 15-30분)
        2. **최대 속도:** 5~10 ml/kg/hr (심장 안정 시)
        3. **시간 제한:** 4시간 이내 투여 완료 필수 (오염 방지)
        4. **필터:** 전용 수혈 세트(필터 포함) 사용 필수
        """)

st.divider()
st.caption(f"Royal Animal Medical Center | v12.0 | Clinical Protocol by Dr. Jaehee Lee")
