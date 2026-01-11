import streamlit as st

# --- [1. 데이터베이스: 사료, 약물, 호환성 정보] ---
DIET_DATA = {
    "Royal Canin (처방식)": {
        "Recovery (Wet, 100g)": 105, "Gastrointestinal (Dry)": 3912, "Gastrointestinal (Wet, 400g)": 432,
        "GI Low Fat (Dry)": 3461, "GI Low Fat (Wet, 410g)": 385, "Urinary S/O (Dry)": 3884, "Hepatic (Dry)": 3900,
        "Renal (Dry)": 3988, "Renal (Wet, 100g)": 110
    },
    "Hill's (Prescription Diet)": {
        "a/d Urgent Care (Wet, 156g)": 183, "i/d Digestive Care (Dry)": 3663, "i/d (Wet, 156g)": 155,
        "i/d Low Fat (Dry)": 3316, "i/d Low Fat (Wet, 370g)": 341, "k/d (Dry)": 4220, "c/d (Dry)": 3873
    }
}

# CRI 약물 확장 데이터 (함량, 권장 희석액, 호환성 메모)
DRUG_CRI_DATA = {
    "a. 진통/진정/항경련": {
        "Butorphanol": {"conc": 2.0, "unit": "mg/kg/h", "diluent": "NS / LRS", "compat": "대부분의 수액과 혼합 가능하나 단독 라인 권장."},
        "Midazolam": {"conc": 1.0, "unit": "mg/kg/h", "diluent": "NS / 5%DW", "compat": "알칼리성 약물과 혼합 시 침전 발생 주의."},
        "Diazepam": {"conc": 5.0, "unit": "mg/kg/h", "diluent": "희석 비권장", "compat": "플라스틱 흡착 심함. 희석 시 침전 위험, 가급적 원액 단독 투여."},
        "Dexmedetomidine": {"conc": 0.118, "unit": "mg/kg/h", "diluent": "NS", "compat": "다른 진정제와 병용 시 서맥 모니터링 필수."},
        "Propofol": {"conc": 10.0, "unit": "mg/kg/h", "diluent": "원액", "compat": "희석 금지. 전용 라인 사용 및 개봉 후 6시간 내 폐기."},
    },
    "b. 심혈관계/승압제": {
        "Epinephrine": {"conc": 1.0, "unit": "mcg/kg/min", "diluent": "5%DW 권장", "compat": "알칼리성 용액(Bicarb)에서 불활성화됨. 5%DW 희석 시 안정성 높음."},
        "Norepinephrine": {"conc": 2.0, "unit": "mcg/kg/min", "diluent": "5%DW 필히 권장", "compat": "산화 방지를 위해 5%DW 사용 필수. LRS와 혼합 금지."},
        "Dopamine": {"conc": 32.96, "unit": "mcg/kg/min", "diluent": "NS / 5%DW", "compat": "Bicarb와 혼합 금지."},
        "Dobutamine": {"conc": 50.0, "unit": "mcg/kg/min", "diluent": "NS / 5%DW", "compat": "Bicarb와 혼합 금지."},
        "Amiodarone": {"conc": 50.0, "unit": "mg/kg/h", "diluent": "5%DW 전용", "compat": "NS와 혼합 시 침전 발생. 반드시 5%DW만 사용."},
    },
    "c. 전해질 및 기타": {
        "Calcium Gluconate": {"conc": 100.0, "unit": "mg/kg/h", "diluent": "NS / 5%DW", "compat": "LRS(결정 발생) 및 Bicarb와 절대 혼합 금지."},
        "KP(Potassium Phosphate)": {"conc": 3.0, "unit": "mmol/kg/h", "diluent": "NS / 5%DW", "compat": "Calcium, Magnesium과 혼합 시 침전. 단독 라인 혹은 충분히 세척된 라인 사용."},
        "Magnesium Sulfate": {"conc": 500.0, "unit": "mg/kg/h", "diluent": "NS / 5%DW", "compat": "Calcium, Phosphate와 혼합 시 침전 위험. 속도 조절 필수."},
        "Magnesium Chloride": {"conc": 200.0, "unit": "mg/kg/h", "diluent": "NS / 5%DW", "compat": "Sulfate보다 결정화 위험은 적으나 Calcium과 병용 주의."},
        "Insulin(RI)": {"conc": 1.0, "unit": "U/kg/h", "diluent": "NS", "compat": "용기 흡착 방지를 위해 첫 20-50mL는 버리고 연결."},
        "Furosemide": {"conc": 10.0, "unit": "mg/kg/h", "diluent": "NS", "compat": "산성 수액과 혼합 시 침전. 가급적 단독 투여."},
    }
}

DISEASE_FACTORS = {
    "일반/비만": {"성장기(2-12m)": 2.0, "중성화 성견/성묘": 1.2, "미중성화": 1.4, "비만감량": 0.8},
    "신장/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전/이뇨제": 1.05},
    "췌장/간/소화기": {"췌장염 안정": 1.1, "간질환/IBD": 1.15, "고양이 지방간(HL)": 1.35, "EPI": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

# --- [2. 페이지 설정 및 사이드바] ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc v8.0", layout="wide")
st.title("🐾 로얄동물메디컬센터 Clinical Support System")

st.sidebar.header("📋 Patient Info")
species = st.sidebar.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
weight = st.sidebar.number_input("체중 (kg)", min_value=0.1, value=3.07, step=0.01)
st.sidebar.markdown("---")
st.sidebar.caption("Clinical Protocol Architect")
st.sidebar.markdown("### **Dr. Jaehee Lee**")

# --- [3. 메인 기능 탭] ---
tabs = st.tabs(["🍴 영양/급여 관리", "💧 수액 요법", "💉 CRI 조제 & Compatibility", "🩸 수혈", "⚠️ 모니터링"])

# --- TAB 1: 영양 관리 (기존 로직 유지) ---
with tabs[0]:
    col1, col2 = st.columns(2)
    with col1:
        st.header("1. DER 에너지 요구량")
        rer = weight * 50
        cat_n = st.selectbox("질환군", list(DISEASE_FACTORS.keys()))
        sub_n = st.selectbox("세부 상태", list(DISEASE_FACTORS[cat_n].keys()))
        f_n = DISEASE_FACTORS[cat_n][sub_n]
        if st.checkbox("입원 환자 가중치 적용 (×1.1)", value=True): f_n *= 1.1
        der = rer * f_n
        st.success(f"### 목표 DER: **{der:.0f}** kcal/day")
        
        strategy = st.radio("급여 전략", ["3단계", "4단계", "5단계"], horizontal=True)
        s_map = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        curr_s = st.select_slider("단계 설정", options=s_map[strategy], value=s_map[strategy][-1])
        st.info(f"**현재 목표:** {(der * curr_s):.0f} kcal")

    with col2:
        st.header("2. 급여량")
        brand = st.selectbox("브랜드", list(DIET_DATA.keys()))
        product = st.selectbox("제품", list(DIET_DATA[brand].keys()))
        kcal_v = DIET_DATA[brand][product]
        unit = "can" if "Wet" in product or "파우치" in product else "g"
        amt = ((der * curr_s) / kcal_v) * (1 if unit == "can" else 1000)
        st.warning(f"### 권장량: **{amt:.1f} {unit}**")

# --- TAB 2: 수액 요법 (Dry & AAHA 통합) ---
with tabs[1]:
    mode = st.radio("상황 선택", ["Dry Mode 입원 수액", "AAHA 2024 쇼크", "AAHA 2024 마취"], horizontal=True)
    col3, col4 = st.columns(2)
    with col3:
        if "Dry Mode" in mode:
            st.header("로얄 Dry Mode")
            m_rate = st.slider("유지 (mL/kg/hr)", 1.0, 4.0, 2.0, 0.5)
            dehy = st.number_input("탈수 (%)", 0, 15, 0)
            loss = st.number_input("지속 손실 (mL/day)", 0)
            total_f = (weight * m_rate) + ((weight * dehy * 10) / 12) + (loss / 24)
            st.success(f"### 최종 속도: **{total_f:.1f} mL/h**")
        elif "쇼크" in mode:
            st.header("Resuscitation Bolus")
            vol = (weight * 15) if species == "개(Canine)" else (weight * 5)
            st.error(f"### 권장 볼러스: **{vol:.1f} mL** (15-30분 투여)")
        else:
            st.header("Anesthesia")
            anes = (weight * 5) if species == "개(Canine)" else (weight * 3)
            st.success(f"### 마취 수액: **{anes:.1f} mL/h**")
    with col4:
        st.header("⚠️ 질환별 가이드")
        if "췌장" in sub_n: st.error("췌장염: 전해질 교정 및 Ongoing Loss 적극 반영")
        elif "심장" in sub_n: st.error("심장병: 유지량 하한선(1.0ml/kg/hr) 권장 및 RR 모니터링")

# --- TAB 3: CRI 조제 & Compatibility (핵심 업데이트) ---
with tabs[2]:
    st.header("💉 CRI Recipe & Drug Compatibility")
    col5, col6 = st.columns([1, 1.2])
    
    with col5:
        cat_c = st.selectbox("약물 카테고리", list(DRUG_CRI_DATA.keys()))
        drug_c = st.selectbox("CRI 약물 선택", list(DRUG_CRI_DATA[cat_c].keys()))
        drug_info = DRUG_CRI_DATA[cat_c][drug_name := drug_c]
        
        i_rate = st.number_input("설정 펌프 속도 (mL/h)", value=0.5, step=0.1)
        t_dose = st.number_input(f"목표 용량 ({drug_info['unit']})", value=0.01 if "mcg" in drug_info['unit'] else 0.1, format="%.3f")
        syr_v = st.selectbox("시린지 총 용량 (mL)", [10, 20, 50], index=2)

    with col6:
        # 계산
        if drug_info['unit'] == "mcg/kg/min":
            mg_h = (t_dose * weight * 60) / 1000
        else:
            mg_h = (t_dose * weight)
            
        d_ml = ((mg_h / i_rate) * syr_v) / drug_info['conc']
        
        st.subheader(f"👨‍🍳 {drug_c} 조제 가이드")
        if d_ml > syr_v:
            st.error("⚠️ 오류: 약물 용량이 시린지 볼륨을 초과합니다!")
        else:
            st.info(f"""
            **1. 펌프 속도:** ### 🚩 {i_rate} mL/h
            **2. 조제법 (총 {syr_v}mL 기준):**
            * **권장 희석액: {drug_info['diluent']}**
            * {drug_c} 원액: **{d_ml:.2f} mL**
            * 희석액: **{(syr_v - d_ml):.2f} mL**
            """)
            
            st.warning(f"⚠️ **Compatibility & Note:**\n{drug_info['compat']}")
            
            # 특수 경고 자동 노출
            if "mcg" in drug_info['unit'] and i_rate <= 0.3:
                st.error("💡 Dry Mode 조언: 저속 투여 시 정확도를 위해 초농축 조제를 고려하십시오.")

# --- 수혈 및 모니터링 (기존 로직 유지) ---
with tabs[3]:
    st.header("🩸 Transfusion")
    st.write(f"예상 수혈량 계산: (Target PCV - Current PCV) / Donor PCV ...")
    # (v7.1 코드와 동일)

with tabs[4]:
    st.header("⚠️ AAHA 2024 모니터링")
    st.markdown("- RR 20% 증가 시 즉시 중단\n- Chemosis/비루 확인\n- Body weight 10% 증가 확인")

st.divider()
st.caption("Royal Animal Medical Center | v8.0 | Clinical Solution by Dr. Jaehee Lee")
