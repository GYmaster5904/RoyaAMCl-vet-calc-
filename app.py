import streamlit as st

# --- [1. 데이터베이스: 약물 함량 및 사료 칼로리] ---
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

# --- [2. 페이지 기본 설정] ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc", layout="wide")
st.title("🐾 로얄동물메디컬센터 Clinical Support System")

# --- [3. 사이드바: 환자 정보 및 아키텍트] ---
st.sidebar.header("📋 Patient Basic Info")
species = st.sidebar.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
weight = st.sidebar.number_input("체중 (kg)", min_value=0.1, value=3.07, step=0.01)
is_obese = st.sidebar.checkbox("비만 환자 (제지방 체중 고려)")
condition = st.sidebar.multiselect("기저 질환/특이 사항", ["심장 질환", "신장 질환(무뇨/핍뇨)", "소아(Pediatric)"])

k_val = 10.1 if species == "개(Canine)" else 10.0
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
    
    with col1:
        st.header("💧 수액 요법 (Fluid Therapy)")
        # 물결표(~) 대신 대시(-)를 사용하여 마크다운 오류 방지
        st.info("표준 범위: 40-60 mL/kg/day (시간당 2-3 mL/kg)")
        
        base_maint = weight * 50
        
        adj_maint = base_maint
        if "심장 질환" in condition or "신장 질환(무뇨/핍뇨)" in condition:
            adj_maint = base_maint * 0.5
            st.warning("⚠️ 심장/신장 질환: 유지량의 50% 수준에서 조절을 권장합니다.")
        elif "소아(Pediatric)" in condition:
            adj_maint = base_maint * 1.5
            st.info("👶 소아: 높은 대사율로 인해 증량(약 1.5배)이 필요할 수 있습니다.")

        st.subheader("수액 속도 상세 설정")
        dehydration = st.number_input("탈수율 (%)", min_value=0, max_value=15, value=0)
        rehyd_hr = st.slider("탈수 교정 시간 (hr)", 4, 24, 12)
        ongoing_loss = st.number_input("지속 손실량 (구토/설사 등, mL/day)", value=0)

        rehyd_total = weight * (dehydration / 100) * 1000
        maint_ongoing_rate = (adj_maint + ongoing_loss) / 24
        rehyd_rate = rehyd_total / rehyd_hr if dehydration > 0 else 0
        final_fluid_rate = maint_ongoing_rate + rehyd_rate
        
        st.success(f"### 🚩 최종 수액 속도: **{round(final_fluid_rate, 1)}** mL/h")
        st.caption(f"유지+손실: {round(maint_ongoing_rate, 1)} / 탈수교정: {round(rehyd_rate, 1)}")

    with col2:
        st.header("🍽️ 영양 관리 (DER & Diet)")
        st.subheader("1. 에너지 요구량")
        rer = 70 * (weight ** 0.75)
        factor = st.select_slider("Illness Factor", options=[0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0], value=1.0)
        
        der = rer * factor
        if is_obese: der *= 0.8
        
        st.write(f"**목표 DER:** {round(der, 0)} kcal/day")

        st.subheader("2. 사료 급여량")
        brand = st.selectbox("사료 브랜드", list(DIET_DATA.keys()))
        product = st.selectbox("제품 선택", list(DIET_DATA[brand].keys()))
        kcal = DIET_DATA[brand][product]
        
        is_wet = "Wet" in product
        unit = "can" if is_wet else "g"
        daily_amt = (der / kcal) * (1 if is_wet else 1000)

        st.success(f"### 🍴 일일 급여량: **{round(daily_amt, 1)} {unit}**")
        st.caption(f"기준: {kcal} kcal/{'can' if is_wet else 'kg'}")

# --- TAB 2: 수혈 계산 ---
with tabs[1]:
    st.header("🩸 Transfusion Volume")
    t1, t2, t3 = st.columns(3)
    with t1: c_pcv = st.number_input("환자 현재 PCV (%)", value=15.0)
    with t2: t_pcv = st.number_input("목표 PCV (%)", value=25.0)
    with t3: d_pcv = st.number_input("혈액 PCV (%)", value=60.0)
    
    k_t = 90 if species == "개(Canine)" else 60
    t_vol = weight * k_t * ((t_pcv - c_pcv) / d_pcv)
    st.error(f"### 예상 수혈량: **{round(t_vol, 1)}** mL")

# --- TAB 3: CRI 조제 레시피 ---
with tabs[2]:
    st.header("💉 CRI Preparation (Rate-First)")
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        cat = st.selectbox("카테고리", list(DRUG_DATA.keys()))
        drug = st.selectbox("약물", list(DRUG_DATA[cat].keys()))
        stock = DRUG_DATA[cat][drug]
        
        inf_rate = st.number_input("펌프 설정 속도 (mL/h)", value=0.5, step=0.1)
        unit = "mcg/kg/min" if drug in ["Epinephrine", "Norepinephrine", "Dopamine", "Dobutamine"] else "mg/kg/h"
        if drug == "Vasopressin": unit = "U/kg/h"
        t_dose = st.number_input(f"목표 용량 ({unit})", value=0.1, step=0.01, format="%.3f")
        syr_v = st.selectbox("시린지 용량 (mL)", [10, 20, 50], index=2)

    with c2:
        if unit == "mcg/kg/min":
            mg_hr = (t_dose * weight * 60) / 1000
        else:
            mg_hr = (t_dose * weight)
            
        drug_ml = ((mg_hr / inf_rate) * syr_v) / stock
        dil_ml = syr_v - drug_ml
        
        st.subheader(f"👨‍🍳 {drug} 조제 가이드")
        if drug_ml > syr_v:
            st.error("⚠️ 약물 용량이 시린지 볼륨을 초과합니다!")
        else:
            st.info(f"**속도: {inf_rate} mL/h**\n\n**원액: {round(drug_ml, 2)} mL**\n\n**희석액: {round(dil_ml, 2)} mL**")

st.divider()
st.caption("Royal Animal Medical Center | v4.1 | Protocol by Dr. Jaehee Lee")
