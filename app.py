import streamlit as st

# --- [1. 데이터베이스: 최신 사료 칼로리 (공식 사이트 데이터 반영)] ---
# 건식: kcal/kg | 습식: 캔/파우치 당 총 칼로리
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
        "Renal (Wet, 100g)": 110
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

# --- [2. 약물 데이터베이스 (로얄 표준 함량)] ---
DRUG_DATA = {
    "a. 향정신성/진정/경련": {"Butorphanol": 2.0, "Midazolam": 1.0, "Diazepam": 5.0, "Medetomidine": 1.0, "Dexmedetomidine": 0.118, "Alfaxalone": 10.0, "Propofol": 10.0},
    "b. 심혈관계/승압제": {"Epinephrine": 1.0, "Norepinephrine": 2.0, "Vasopressin": 20.0, "Dobutamine": 50.0, "Dopamine": 32.96, "Lidocaine": 20.0, "Esmolol": 10.0, "Amiodarone": 50.0},
    "c. 기타 약물": {"Furosemide": 10.0, "Mannitol": 200.0, "Insulin(RI)": 1.0, "Ulinastatin": 10000.0, "Ca-Gluconate": 50.0, "Atropine": 0.5, "Glycopyrrolate": 0.2}
}

# --- [3. 보수적 DER Factor (원장님 프로토콜)] ---
DISEASE_FACTORS = {
    "일반/비만": {"성장기(2-12m)": 2.0, "중성화 성견/성묘": 1.2, "미중성화": 1.4, "비만감량(BCS 7+)": 0.8},
    "신장/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전/이뇨제사용": 1.05},
    "췌장/간/소화기": {"췌장염 안정(Day 3+)": 1.1, "간질환/IBD 안정기": 1.15, "고양이 지방간(HL)": 1.35, "EPI(췌장부전)": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

# --- [4. 페이지 설정 및 사이드바] ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc", layout="wide")
st.title("🐾 로얄동물메디컬센터 Clinical Support System")

st.sidebar.header("📋 Patient Basic Info")
species = st.sidebar.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
weight = st.sidebar.number_input("체중 (kg)", min_value=0.1, value=3.07, step=0.01)

# BSA 계산
k_val = 10.1 if species == "개(Canine)" else 10.0
bsa = (k_val * (weight ** (2/3))) / 100
st.sidebar.metric("BSA", f"{bsa:.3f} ㎡")

st.sidebar.markdown("---")
st.sidebar.caption("Clinical Protocol Architect")
st.sidebar.markdown("### **Dr. Jaehee Lee**")

# --- 메인 탭 구성 ---
tabs = st.tabs(["🍽️ 통합 영양/급여 관리", "💧 수액 요법 (질환별 검토)", "🩸 수혈 계산", "💉 CRI 조제 레시피"])

# --- TAB 1: 통합 영양/급여 관리 ---
with tabs[0]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("1. DER (에너지 요구량)")
        rer = weight * 50 # 선형 RER (원장님 지시)
        st.write(f"**선형 RER (BW × 50):** {rer:.0f} kcal/day")
        
        cat = st.selectbox("질환 카테고리", list(DISEASE_FACTORS.keys()))
        sub_cat = st.selectbox("세부 상태 선택", list(DISEASE_FACTORS[cat].keys()))
        f_val = DISEASE_FACTORS[cat][sub_cat]
        
        # 보수적 관리: 입원 환자 가중치 (기본 1.1)
        if st.checkbox("입원 환자 가중치 적용 (×1.1)", value=True):
            f_val *= 1.1
            
        der = rer * f_val
        st.success(f"### 최종 목표 DER: **{der:.0f}** kcal/day")

    with col2:
        st.header("2. 급여 플랜 (Fasting 대응)")
        strategy = st.radio("급여 전략 선택", ["3단계 (Standard)", "4단계 (Prolonged)", "5단계 (Critical)"], horizontal=True)
        
        if strategy == "3단계 (Standard)":
            stages = {"1단계 (33%)": 0.33, "2단계 (66%)": 0.66, "3단계 (100%)": 1.0}
        elif strategy == "4단계 (Prolonged)":
            stages = {"1단계 (25%)": 0.25, "2단계 (50%)": 0.50, "3단계 (75%)": 0.75, "4단계 (100%)": 1.0}
        else:
            stages = {"1단계 (20%)": 0.20, "2단계 (40%)": 0.40, "3단계 (60%)": 0.60, "4단계 (80%)": 0.80, "5단계 (100%)": 1.0}
        
        current_stage = st.select_slider("현재 급여 단계", options=list(stages.keys()), value=list(stages.keys())[-1])
        target_kcal = der * stages[current_stage]
        
        st.info(f"**목표 칼로리:** {target_kcal:.0f} kcal ({current_stage})")
        
        brand = st.selectbox("사료 브랜드", list(DIET_DATA.keys()))
        product = st.selectbox("제품명 선택", list(DIET_DATA[brand].keys()))
        kcal_val = DIET_DATA[brand][product]
        
        is_wet = "Wet" in product or "파우치" in product
        unit = "can" if is_wet else "g"
        amount = (target_kcal / kcal_val) * (1 if is_wet else 1000)
        
        st.warning(f"### 일일 급여량: **{amount:.1f} {unit}**")
        st.caption(f"기준: {kcal_val} kcal/{'can(pouch)' if is_wet else 'kg'}")

# --- TAB 2: 수액 요법 (질환별 검토) ---
with tabs[1]:
    col3, col4 = st.columns(2)
    with col3:
        st.header("수액 속도 계산")
        m_rate = st.slider("유지 용량 기준 (mL/kg/hr)", 1.0, 4.0, 2.0, 0.5)
        dehy = st.number_input("탈수율 (%)", 0, 15, 0)
        loss = st.number_input("지속 손실량 (Ongoing Loss, mL/day)", 0)
        
        # 공식: 유지 + 탈수(12hr 교정) + 지속손실
        total_rate = (weight * m_rate) + ((weight * dehy * 10) / 12) + (loss / 24)
        st.success(f"### 최종 수액 속도: **{total_rate:.1f} mL/h**")

    with col4:
        st.header("⚠️ 임상 검토 가이드")
        if "췌장" in sub_cat:
            st.error("**[췌장염]**\n- 구토/설사 손실 실시간 반영\n- 전해질(K, Mg) 보정 필수\n- 저지방 식단 유지")
        elif "간" in sub_cat or "HL" in sub_cat:
            st.error("**[간 질환/지방간]**\n- 저알부민 시 부종 주의(수액 20-30% 감량)\n- 지방간 환자 절식 절대 금지\n- 혈당 모니터링")
        elif "심장" in sub_cat:
            st.error("**[심장 질환]**\n- 수액 과부하 극히 주의\n- 호흡수(RR) 실시간 모니터링\n- 유지량 하한선(1.0-1.5 mL/kg/hr) 권장")
        else:
            st.info("상단 영양 탭에서 환자 상태를 선택하면 관련 가이드가 표시됩니다.")

# --- TAB 3: 수혈 계산 ---
with tabs[2]:
    st.header("🩸 Transfusion Volume")
    t1, t2, t3 = st.columns(3)
    with t1: c_pcv = st.number_input("현재 PCV (%)", value=15.0)
    with t2: t_pcv = st.number_input("목표 PCV (%)", value=25.0)
    with t3: d_pcv = st.number_input("혈액 PCV (%)", value=60.0)
    
    k_t = 90 if species == "개(Canine)" else 60
    st.error(f"### 예상 수혈량: **{round(weight * k_t * ((t_pcv - c_pcv) / d_pcv), 1)}** mL")

# --- TAB 4: CRI 조제 레시피 ---
with tabs[3]:
    st.header("💉 CRI Preparation (Rate-First)")
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        category = st.selectbox("카테고리 선택", list(DRUG_DATA.keys()))
        drug_name = st.selectbox("약물 선택", list(DRUG_DATA[category].keys()))
        stock = DRUG_DATA[category][drug_name]
        
        inf_rate = st.number_input("펌프 설정 속도 (mL/h)", value=0.5, step=0.1)
        unit = "mcg/kg/min" if drug_name in ["Epinephrine", "Norepinephrine", "Dopamine", "Dobutamine"] else "mg/kg/h"
        if drug_name == "Vasopressin": unit = "U/kg/h"
        
        t_dose = st.number_input(f"목표 용량 ({unit})", value=0.1, step=0.01, format="%.3f")
        syr_v = st.selectbox("시린지 총 용량 (mL)", [10, 20, 50], index=2)

    with c2:
        if unit == "mcg/kg/min":
            mg_hr = (t_dose * weight * 60) / 1000
        else:
            mg_hr = (t_dose * weight)
            
        drug_ml = ((mg_hr / inf_rate) * syr_v) / stock
        dil_ml = syr_v - drug_ml
        
        st.subheader(f"👨‍🍳 {drug_name} 조제 결과")
        if drug_ml > syr_v:
            st.error("⚠️ 오류: 약물 용량이 시린지 볼륨을 초과합니다!")
        else:
            st.info(f"**설정 속도: {inf_rate} mL/h**\n\n**약물 원액: {round(drug_ml, 2)} mL**\n\n**희석액: {round(dil_ml, 2)} mL**")
            if drug_name in ["Epinephrine", "Norepinephrine"] and inf_rate <= 0.3:
                st.warning("💡 Dry Mode 조언: 속도가 낮으므로 초농축 조제를 고려하십시오.")

st.divider()
st.caption("Royal Animal Medical Center | v6.1 | Clinical Solution by Dr. Jaehee Lee")
