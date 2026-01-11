import streamlit as st

# --- [데이터베이스: 병원 표준 약물 함량] ---
DRUG_DATA = {
    "a. 향정신성/진정/경련": {
        "Butorphanol": 2.0, "Midazolam": 1.0, "Diazepam": 5.0, 
        "Medetomidine": 1.0, "Dexmedetomidine": 0.118, "Alfaxalone": 10.0, "Propofol": 10.0
    },
    "b. 심혈관계/승압제": {
        "Epinephrine": 1.0, "Norepinephrine": 2.0, "Vasopressin": 20.0, 
        "Dobutamine": 50.0, "Dopamine": 32.96, "Lidocaine": 20.0, "Esmolol": 10.0, "Amiodarone": 50.0
    },
    "c. 기타 약물": {
        "Furosemide": 10.0, "Mannitol": 200.0, "Insulin(RI)": 1.0, 
        "Ulinastatin": 10000.0, "Ca-Gluconate": 50.0, "Atropine": 0.5, "Glycopyrrolate": 0.2
    }
}

# --- [데이터베이스: 사료 칼로리 정보 (예시 포함)] ---
# 실제 병원 사용 품목에 맞춰 kcal/kg(건식) 또는 kcal/can(습식) 조정 가능
DIET_DATA = {
    "Royal Canin": {
        "Gastrointestinal (Dry)": 3912, # kcal/kg
        "Gastrointestinal (Wet)": 180,  # kcal/can (400g)
        "Recovery (Wet)": 105,          # kcal/can (100g)
        "Urinary S/O (Dry)": 3884,
        "Hepatic (Dry)": 3900
    },
    "Hills": {
        "i/d (Dry)": 3663,              # kcal/kg
        "i/d (Wet)": 155,               # kcal/can (156g)
        "a/d (Wet)": 183,               # kcal/can (156g)
        "k/d (Dry)": 4220,
        "c/d (Dry)": 3873
    }
}

st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc v4.0", layout="wide")
st.title("🐾 로얄동물메디컬센터 Clinical Support System")

# --- [사이드바: 환자 정보 및 아키텍트] ---
st.sidebar.header("📋 Patient Basic Info")
species = st.sidebar.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
weight = st.sidebar.number_input("체중 (kg)", min_value=0.1, value=3.07, step=0.01)
is_obese = st.sidebar.checkbox("비만 환자 (제지방 체중 고려)")
condition = st.sidebar.multiselect("환자 상태 고려", ["심장 질환", "신장 질환(무뇨/핍뇨)", "소아(Pediatric)"])

k_val = 10.1 if species == "개(Canine)" else 10.0
bsa = (k_val * (weight ** (2/3))) / 100
st.sidebar.metric("BSA", f"{bsa:.3f} ㎡")

st.sidebar.markdown("---")
st.sidebar.caption("Clinical Protocol Architect")
st.sidebar.markdown("### **Dr. Jaehee Lee**")

# --- 메인 탭 구성 ---
tabs = st.tabs(["🍽️ 영양 및 수액 요법", "🩸 수혈", "💉 CRI 조제 레시피"])

# --- [1단계: 영양 및 수액 요법 통합 관리] ---
with tabs[0]:
    col1, col2 = st.columns(2)
    
    # --- 수액 요법 (Fluid Therapy) ---
    with col1:
        st.header("💧 수액 요법 (Fluid Therapy)")
        st.subheader("1. 유지 용량 (Maintenance)")
        st.info("성견/성묘 표준 범위: 40~60 mL/kg/day (시간당 2~3 mL/kg)")
        
        # 선형 계산법 (원장님 지시: BW * 50)
        base_maint = weight * 50
        
        # 비만/기저질환에 따른 조정 조언
        adj_maint = base_maint
        if "심장 질환" in condition or "신장 질환(무뇨/핍뇨)" in condition:
            adj_maint = base_maint * 0.5
            st.warning("⚠️ 심장/신장 질환: 유지 용량의 50%부터 시작을 권장합니다.")
        elif "소아(Pediatric)" in condition:
            adj_maint = base_maint * 1.5
            st.info("👶 소아 환자: 높은 대사율을 고려하여 1.5배 증량 고려.")

        st.write(f"**기본 유지 요구량 (50ml/kg):** {round(base_maint, 1)} mL/day")
        
        st.subheader("2. 탈수 및 지속 손실 (Rehydration & Loss)")
        dehydration = st.number_input("탈수율 (%)", min_value=0, max_value=15, value=0)
        rehyd_hr = st.slider("탈수 교정 시간 (hr)", 4, 24, 12)
        ongoing_loss = st.number_input("지속 손실량 (구토/설사 등, mL/day)", value=0)

        # 계산
        rehyd_total = weight * (dehydration / 100) * 1000 # mL
        total_fluid_day = adj_maint + ongoing_loss
        
        # 시간당 속도 계산
        maint_ongoing_rate = total_fluid_day / 24
        rehyd_rate = rehyd_total / rehyd_hr if dehydration > 0 else 0
        
        final_rate = maint_ongoing_rate + rehyd_rate
        
        st.success(f"### 🚩 최종 수액 속도: **{round(final_rate, 1)}** mL/h")
        st.caption(f"(유지+지속손실: {round(maint_ongoing_rate,1)} + 탈수교정: {round(rehyd_rate,1)})")

    # --- 영양 관리 (Nutrition & DER) ---
    with col2:
        st.header("🍽️ 영양 관리 (DER & Feeding)")
        st.subheader("1. 에너지 요구량 (Energy)")
        # RER 계산 (지수형 보존)
        rer = 70 * (weight ** 0.75)
        factor = st.select_slider("Illness Factor", options=[0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0], value=1.0)
        
        der = rer * factor
        if is_obese: der *= 0.8
        
        st.write(f"**목표 DER:** {round(der, 0)} kcal/day")

        st.subheader("2. 사료 급여량 계산")
        brand = st.selectbox("사료 브랜드", list(DIET_DATA.keys()))
        product = st.selectbox("제품 선택", list(DIET_DATA[brand].keys()))
        kcal_content = DIET_DATA[brand][product]
        
        is_wet = "Wet" in product
        unit = "can" if is_wet else "g"
        
        if is_wet:
            daily_amount = der / kcal_content
        else:
            daily_amount = (der / kcal_content) * 1000 # g 단위 환산

        st.success(f"### 🍴 일일 급여량: **{round(daily_amount, 1)} {unit}**")
        st.caption(f"기준 칼로리: {kcal_content} kcal/{'can' if is_wet else 'kg'}")
        
        st.markdown("""
        **[영양 고려사항]**
        * 자발적 음수/섭식 시작 시 수액 속도를 비례하여 감량하십시오.
        * 장기 유지 시 저장성 수액(Hypotonic) 선택을 고려하십시오.
        """)

# --- [2단계: 수혈량 계산] ---
with tabs[1]:
    st.header("🩸 Transfusion Volume")
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1: curr_pcv = st.number_input("현재 PCV (%)", value=15.0)
    with t_col2: target_pcv = st.number_input("목표 PCV (%)", value=25.0)
    with t_col3: donor_pcv = st.number_input("혈액 PCV (%)", value=60.0)
    
    k_t = 90 if species == "개(Canine)" else 60
    trans_vol = weight * k_t * ((target_pcv - curr_pcv) / donor_pcv)
    st.error(f"### 예상 수혈량: **{round(trans_vol, 1)}** mL")

# --- [3단계: CRI 조제 레시피] ---
with tabs[2]:
    st.header("💉 CRI Preparation (Rate-First)")
    c_col1, c_col2 = st.columns([1, 1.2])
    
    with c_col1:
        cat = st.selectbox("카테고리", list(DRUG_DATA.keys()))
        drug = st.selectbox("약물", list(DRUG_DATA[cat].keys()))
        stock = DRUG_DATA[cat][drug]
        
        inf_rate = st.number_input("펌프 설정 속도 (mL/h)", value=0.5, step=0.1)
        
        unit = "mcg/kg/min" if drug in ["Epinephrine", "Norepinephrine", "Dopamine", "Dobutamine"] else "mg/kg/h"
        if drug == "Vasopressin": unit = "U/kg/h"
        t_dose = st.number_input(f"목표 용량 ({unit})", value=0.1, step=0.01, format="%.3f")
        syr_vol = st.selectbox("시린지 용량 (mL)", [10, 20, 50], index=2)

    with c_col2:
        if unit == "mcg/kg/min":
            need_mg_hr = (t_dose * weight * 60) / 1000
        else:
            need_mg_hr = (t_dose * weight)
            
        drug_ml = ((need_mg_hr / inf_rate) * syr_vol) / stock
        diluent_ml = syr_vol - drug_ml
        
        st.subheader(f"👨‍🍳 {drug} 조제 가이드")
        if drug_ml > syr_vol:
            st.error("⚠️ 약물 용량 초과!")
        else:
            st.info(f"**속도: {inf_rate} mL/h**\n\n**원액: {round(drug_ml, 2)} mL**\n\n**희석액: {round(diluent_ml, 2)} mL**")
            if drug in ["Epinephrine", "Norepinephrine"] and inf_rate <= 0.3:
                st.warning("💡 Dry Mode: 초농축 조제 고려 구간")

st.divider()
st.caption("Royal Animal Medical Center | Clinical Solution v4.0 | Precision 0.1 mL/h")
