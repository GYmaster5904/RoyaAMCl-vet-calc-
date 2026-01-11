import streamlit as st

# --- [1. 데이터베이스: 약물, 사료, DER 계수] ---
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

DIET_DATA = {
    "Royal Canin": {
        "Gastrointestinal (Dry)": 3912, "Gastrointestinal (Wet)": 180, 
        "Recovery (Wet)": 105, "Urinary S/O (Dry)": 3884, "Hepatic (Dry)": 3900
    },
    "Hills": {
        "i/d (Dry)": 3663, "i/d (Wet)": 155, "a/d (Wet)": 183, 
        "k/d (Dry)": 4220, "c/d (Dry)": 3873
    }
}

# 첨부파일 Table 1 반영 DER 계수
DER_COEFFS = {
    "개(Canine)": {
        "Growth (4개월 미만)": 3.0,
        "Growth (4개월 이상)": 2.0,
        "성견 (중성화 완료)": 1.6,
        "성견 (미중성화)": 1.8,
        "비만 경향 (Obese prone)": 1.4,
        "체중 감량 중 (Weight loss)": 1.0,
        "Work (Light)": 2.0,
        "Work (Heavy)": 6.0  # 4~8 범위의 평균값
    },
    "고양이(Feline)": {
        "성장기 (Kittens)": 2.5,
        "성묘 (중성화 완료)": 1.2,
        "성묘 (미중성화)": 1.4,
        "비만 경향 (Obese prone)": 1.0,
        "체중 감량 중 (Weight loss)": 0.8
    }
}

# --- [2. 페이지 기본 설정] ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc", layout="wide")
st.title("🐾 로얄동물메디컬센터 Clinical Support System")

# --- [3. 사이드바: 환자 정보] ---
st.sidebar.header("📋 Patient Basic Info")
species_label = st.sidebar.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
weight = st.sidebar.number_input("체중 (kg)", min_value=0.1, value=3.07, step=0.01)

# BSA 계산
k_val = 10.1 if species_label == "개(Canine)" else 10.0
bsa = (k_val * (weight ** (2/3))) / 100
st.sidebar.metric("BSA", f"{bsa:.3f} ㎡")

st.sidebar.markdown("---")
st.sidebar.caption("Clinical Protocol Architect")
st.sidebar.markdown("### **Dr. Jaehee Lee**")

# --- [4. 메인 기능 탭] ---
tabs = st.tabs(["🍽️ 영양 및 수액 요법", "🩸 수혈 계산", "💉 CRI 조제 레시피"])

# --- TAB 1: 영양 및 수액 통합 관리 ---
with tabs[0]:
    col1, col2 = st.columns(2)
    
    # [오른쪽: 영양 관리 - Table 1 반영]
    with col2:
        st.header("🍽️ 영양 관리 (DER & Diet)")
        st.subheader("1. 에너지 요구량 (DER)")
        
        # RER 계산
        rer = 70 * (weight ** 0.75)
        
        # Table 1 계수 선택
        activity_options = list(DER_COEFFS[species_label].keys())
        selected_activity = st.selectbox("환자 상태/활동량 (Table 1)", activity_options)
        activity_factor = DER_COEFFS[species_label][selected_activity]
        
        # Illness Factor (기본값 1.1)
        illness_factor = st.select_slider("Illness Factor (입원 환자 가중치)", options=[0.8, 1.0, 1.1, 1.2, 1.4, 1.6], value=1.1)
        
        # DER 최종 계산: RER * Activity * Illness
        der = rer * activity_factor * illness_factor
        
        st.info(f"RER: {round(rer,1)} kcal | 계수: {activity_factor} | 가중치: {illness_factor}")
        st.success(f"### 🍴 최종 목표 DER: **{round(der, 0)}** kcal/day")

        st.subheader("2. 사료 급여량")
        brand = st.selectbox("사료 브랜드", list(DIET_DATA.keys()))
        product = st.selectbox("제품 선택", list(DIET_DATA[brand].keys()))
        kcal = DIET_DATA[brand][product]
        
        is_wet = "Wet" in product
        unit = "can" if is_wet else "g"
        daily_amt = (der / kcal) * (1 if is_wet else 1000)
        st.warning(f"### 일일 급여량: **{round(daily_amt, 1)} {unit}** ({kcal}kcal 기준)")

    # [왼쪽: 수액 요법]
    with col1:
        st.header("💧 수액 요법 (Fluid Therapy)")
        st.info("표준 유지 범위: 40-60 mL/kg/day (시간당 2-3 mL/kg)")
        
        base_maint = weight * 50 # 선형 기본값
        
        # 특이사항 선택 (사이드바 대신 영양 탭 옆에 배치 가능하나 유지함)
        condition = st.multiselect("수액 제한/증량 조건", ["심장 질환", "신장 질환(무뇨/핍뇨)", "소아(Pediatric)"])
        
        adj_maint = base_maint
        if "심장 질환" in condition or "신장 질환(무뇨/핍뇨)" in condition:
            adj_maint = base_maint * 0.5
            st.warning("⚠️ 유지량 50% 제한 모드")
        elif "소아(Pediatric)" in condition:
            adj_maint = base_maint * 1.5

        st.subheader("속도 상세 설정")
        dehydration = st.number_input("탈수율 (%)", min_value=0, max_value=15, value=0)
        rehyd_hr = st.slider("교정 시간 (hr)", 4, 24, 12)
        ongoing_loss = st.number_input("지속 손실 (mL/day)", value=0)

        maint_rate = (adj_maint + ongoing_loss) / 24
        rehyd_rate = (weight * dehydration * 10) / rehyd_hr if dehydration > 0 else 0
        
        st.success(f"### 🚩 수액 속도: **{round(maint_rate + rehyd_rate, 1)}** mL/h")

# --- TAB 2: 수혈 계산 ---
with tabs[1]:
    st.header("🩸 Transfusion")
    t1, t2, t3 = st.columns(3)
    with t1: c_pcv = st.number_input("현재 PCV (%)", value=15.0)
    with t2: t_pcv = st.number_input("목표 PCV (%)", value=25.0)
    with t3: d_pcv = st.number_input("혈액 PCV (%)", value=60.0)
    k_t = 90 if species_label == "개(Canine)" else 60
    st.error(f"### 예상 수혈량: **{round(weight * k_t * ((t_pcv - c_pcv) / d_pcv), 1)}** mL")

# --- TAB 3: CRI 조제 레시피 ---
with tabs[2]:
    st.header("💉 CRI Preparation")
    c1, c2 = st.columns([1, 1.2])
    with c1:
        cat = st.selectbox("카테고리", list(DRUG_DATA.keys()))
        drug = st.selectbox("약물", list(DRUG_DATA[cat].keys()))
        stock = DRUG_DATA[cat][drug]
        inf_rate = st.number_input("펌프 속도 (mL/h)", value=0.5, step=0.1)
        unit_type = "mcg/kg/min" if drug in ["Epinephrine", "Norepinephrine", "Dopamine", "Dobutamine"] else "mg/kg/h"
        if drug == "Vasopressin": unit_type = "U/kg/h"
        t_dose = st.number_input(f"목표 ({unit_type})", value=0.1, step=0.01, format="%.3f")
        syr_v = st.selectbox("시린지 볼륨 (mL)", [10, 20, 50], index=2)
    with c2:
        mg_hr = (t_dose * weight * 60) / 1000 if unit_type == "mcg/kg/min" else (t_dose * weight)
        drug_ml = ((mg_hr / inf_rate) * syr_v) / stock
        st.subheader(f"👨‍🍳 {drug} 레시피")
        if drug_ml > syr_v: st.error("볼륨 초과!")
        else: st.info(f"**속도: {inf_rate} mL/h**\n\n**원액: {round(drug_ml, 2)} mL**\n\n**희석액: {round(syr_v - drug_ml, 2)} mL**")

st.divider()
st.caption("Royal Animal Medical Center | v4.3 | Protocol by Dr. Jaehee Lee")
