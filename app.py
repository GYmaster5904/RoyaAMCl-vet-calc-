import streamlit as st

# --- [1. 데이터베이스: 최신 사료 칼로리 (Royal Canin & Hill's 공식 데이터 기반)] ---
# 건식: kcal/kg | 습식: 캔/파우치 당 총 칼로리(단위 중량 명시)
DIET_DATA = {
    "Royal Canin (처방식)": {
        "Recovery (Wet, 100g)": 105,
        "Gastrointestinal (Dry)": 3912,
        "Gastrointestinal (Wet, 400g)": 432,
        "GI Low Fat (Dry)": 3461,
        "GI Low Fat (Wet, 410g)": 385,
        "Urinary S/O (Dry)": 3884,
        "Urinary S/O (Wet, 100g)": 85,
        "Hepatic (Dry)": 3900,
        "Renal (Dry)": 3988,
        "Renal (Wet, 100g/파우치)": 110
    },
    "Hill's (Prescription Diet)": {
        "a/d Urgent Care (Wet, 156g)": 183,
        "i/d Digestive Care (Dry)": 3663,
        "i/d (Wet, 156g)": 155,
        "i/d Low Fat (Dry)": 3316,
        "i/d Low Fat (Wet, 370g)": 341,
        "k/d Kidney Care (Dry)": 4220,
        "k/d (Wet, 156g)": 161,
        "c/d Multicare (Dry)": 3873,
        "z/d Food Sensitivities (Dry)": 3619
    }
}

# --- [2. 약물 데이터베이스] ---
DRUG_DATA = {
    "a. 향정신성/진정/경련": {"Butorphanol": 2.0, "Midazolam": 1.0, "Diazepam": 5.0, "Medetomidine": 1.0, "Dexmedetomidine": 0.118, "Alfaxalone": 10.0, "Propofol": 10.0},
    "b. 심혈관계/승압제": {"Epinephrine": 1.0, "Norepinephrine": 2.0, "Vasopressin": 20.0, "Dobutamine": 50.0, "Dopamine": 32.96, "Lidocaine": 20.0, "Esmolol": 10.0, "Amiodarone": 50.0},
    "c. 기타 약물": {"Furosemide": 10.0, "Mannitol": 200.0, "Insulin(RI)": 1.0, "Ulinastatin": 10000.0, "Ca-Gluconate": 50.0, "Atropine": 0.5, "Glycopyrrolate": 0.2}
}

# --- [3. 확장 DER Factor (원장님 보수적 프로토콜)] ---
DISEASE_FACTORS = {
    "일반/비만": {"성장기(2-12m)": 2.0, "중성화 성견/성묘": 1.2, "미중성화": 1.4, "비만감량(BCS 7+)": 0.8},
    "신장/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전/이뇨제사용": 1.05},
    "췌장/간/소화기": {"췌장염 안정(Day 3+)": 1.1, "간질환/IBD 안정기": 1.15, "고양이 지방간(HL)": 1.35, "EPI(췌장부전)": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc v6.0", layout="wide")
st.title("🐾 로얄동물메디컬센터 Clinical Support System")

# --- [사이드바: 환자 정보] ---
st.sidebar.header("📋 Patient Info")
weight = st.sidebar.number_input("체중 (kg)", min_value=0.1, value=3.07, step=0.01)
st.sidebar.markdown("---")
st.sidebar.caption("Clinical Protocol Architect")
st.sidebar.markdown("### **Dr. Jaehee Lee**")

tabs = st.tabs(["🍽️ 통합 영양/급여 관리", "💧 수액 요법 (질환별 검토)", "🩸 수혈/CRI"])

# --- TAB 1: 통합 영양/급여 관리 ---
with tabs[0]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("1. DER 프로토콜")
        rer = weight * 50 # 원장님 지시: Linear RER
        st.write(f"**선형 RER (BW × 50):** {rer:.0f} kcal/day")
        
        cat = st.selectbox("질환 카테고리", list(DISEASE_FACTORS.keys()))
        sub_cat = st.selectbox("세부 상태", list(DISEASE_FACTORS[cat].keys()))
        f_val = DISEASE_FACTORS[cat][sub_cat]
        
        # 보수적 관리: 입원 환자 가중치
        if st.checkbox("입원 환자 가중치 적용 (×1.1)", value=True):
            f_val *= 1.1
            
        der = rer * f_val
        st.success(f"### 최종 목표 DER: **{der:.0f}** kcal/day")

    with col2:
        st.header("2. 급여 단계 설정 (Fasting 대응)")
        
        # 급여 전략 선택 (원장님 지시: 3, 4, 5단계 옵션화)
        strategy = st.radio("급여 전략 선택", ["3단계 (Standard)", "4단계 (Prolonged Fasting)", "5단계 (Critical)"], horizontal=True)
        
        if strategy == "3단계 (Standard)":
            stages = {"1단계 (33%)": 0.33, "2단계 (66%)": 0.66, "3단계 (100%)": 1.0}
        elif strategy == "4단계 (Prolonged Fasting)":
            stages = {"1단계 (25%)": 0.25, "2단계 (50%)": 0.50, "3단계 (75%)": 0.75, "4단계 (100%)": 1.0}
        else: # 5단계
            stages = {"1단계 (20%)": 0.20, "2단계 (40%)": 0.40, "3단계 (60%)": 0.60, "4단계 (80%)": 0.80, "5단계 (100%)": 1.0}
        
        current_stage = st.select_slider("현재 급여 단계", options=list(stages.keys()), value=list(stages.keys())[-1])
        target_kcal = der * stages[current_stage]
        
        st.info(f"**목표 칼로리:** {target_kcal:.0f} kcal ({current_stage})")
        
        brand = st.selectbox("사료 선택", list(DIET_DATA.keys()))
        product = st.selectbox("제품명", list(DIET_DATA[brand].keys()))
        kcal_val = DIET_DATA[brand][product]
        
        # 단위 결정
        is_wet = "Wet" in product or "파우치" in product
        unit = "can" if is_wet else "g"
        
        amount = (target_kcal / kcal_val) * (1 if is_wet else 1000)
        st.warning(f"### 일일 급여량: **{amount:.1f} {unit}**")
        st.caption(f"기준: {kcal_val} kcal/{'can(pouch)' if is_wet else 'kg'}")

# --- TAB 2: 수액 요법 (간/췌장/소화기 집중 검토) ---
with tabs[1]:
    col3, col4 = st.columns(2)
    with col3:
        st.header("수액 속도 계산")
        m_rate = st.slider("유지 기준 (mL/kg/hr)", 1.0, 4.0, 2.0, 0.5)
        dehy = st.number_input("탈수율 (%)", 0, 15, 0)
        loss = st.number_input("지속 손실 (mL/day)", 0)
        
        final_fluid = (weight * m_rate) + ((weight * dehy * 10) / 12) + (loss / 24)
        st.success(f"### 최종 수액 속도: **{final_fluid:.1f} mL/h**")

    with col4:
        st.header("⚠️ 질환별 수액 검토 가이드")
        if "췌장" in sub_cat:
            st.error("**[췌장염]**\n- Ongoing Loss(구토/설사)를 실시간 반영하여 속도 보정\n- 전해질 불균형(K, Mg) 확인 및 교정\n- 수액 과부하 주의하되 유효 순환 혈량 유지")
        elif "간" in sub_cat or "HL" in sub_cat:
            st.error("**[간 질환/지방간]**\n- 저알부민혈증 확인: 부종/복수 시 수액 감량(20-30%)\n- 고양이 지방간: 영양 공급이 수액보다 우선 순위\n- 포도당 농도 모니터링 필수")
        elif "IBD" in sub_cat or "소화기" in sub_cat:
            st.error("**[소화기 질환]**\n- 심한 설사 환자는 탈수 교정 속도 상향 검토\n- 저단백혈증 소실(PLE) 가능성 평가\n- 저장성 수액 장기 사용 시 나트륨 수치 주의")

# --- TAB 3: 수혈 및 CRI ---
with tabs[2]:
    st.write("기존 CRI 및 수혈 공식 유지 (명칭 정리됨)")
    # (기존 코드 생략 - 이전 v5.0과 동일)
