import streamlit as st

# --- [메모리: 로얄동물메디컬센터 표준 약물 함량] ---
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

# --- 페이지 설정 ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc", layout="wide")
st.title("🐾 로얄동물메디컬센터 Clinical Support System")

# --- [사이드바: 환자 기본 정보 및 아키텍트 표기] ---
st.sidebar.header("📋 Patient Basic Info")
species = st.sidebar.selectbox("품종(Species)", ["개(Canine)", "고양이(Feline)"])
weight = st.sidebar.number_input("체중 (Weight, kg)", min_value=0.1, value=3.07, step=0.01)

# BSA 자동 계산
k_val = 10.1 if species == "개(Canine)" else 10.0
bsa = (k_val * (weight ** (2/3))) / 100
st.sidebar.metric("BSA (Body Surface Area)", f"{bsa:.3f} ㎡")

# 만든이 표기 (세련되고 은은하게)
st.sidebar.markdown("---")
st.sidebar.caption("Clinical Protocol Architect")
st.sidebar.markdown("### **Dr. Jaehee Lee**")

# --- 메인 대시보드 순서 (원장님 지시 순서 준수) ---
# 1. DER 계산 -> 2. 배뇨량 수액 -> 3. 수혈량 -> 4. CRI 조제

tabs = st.tabs([
    "🍴 1. DER (영양)", 
    "💧 2. Fluid (수액)", 
    "🩸 3. Transfusion (수혈)", 
    "💉 4. CRI Recipe (조제)"
])

# --- [1단계: DER 계산] ---
with tabs[0]:
    st.header("1. Daily Energy Requirement")
    col1, col2 = st.columns(2)
    with col1:
        # RER 공식: 70 * BW^0.75
        rer = 70 * (weight ** 0.75)
        st.write(f"**기본 RER:** {round(rer, 1)} kcal/day")
        
        illness_factor = st.select_slider(
            "Illness Factor (질환 계수)", 
            options=[0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0], 
            value=1.0,
            help="1.0: 안정 | 1.2-1.4: 수술/외상 | 1.6+: 패혈증/중증"
        )
    with col2:
        notes = st.multiselect("추가 고려 사항", ["비만(BCS 높음)", "발열/흥분", "활동성 저하"])
        # 비만 시 0.8배 적용 로직
        adj_factor = 0.8 if "비만(BCS 높음)" in notes else 1.0
        if "발열/흥분" in notes: adj_factor *= 1.1

    der = rer * illness_factor * adj_factor
    st.success(f"### 🍴 최종 영양 요구량: **{round(der, 0)}** kcal/day")

# --- [2단계: 배뇨량에 따른 수액처치 (Dry Mode)] ---
with tabs[1]:
    st.header("2. Fluid Therapy (Dry Mode Protocol)")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        uop = st.number_input("현재 시간당 배뇨량 (UOP, mL/h)", value=0.0, step=0.1)
        ongoing_loss = st.number_input("기타 손실 (Ongoing Loss, mL/h)", value=0.0, step=0.1)
    with col_f2:
        # 원장님 지시: Insensible Loss 1ml/kg/day
        insensible = (weight * 1) / 24
        st.info(f"**불감수분 손실 (1ml/kg/d):** {insensible:.2f} mL/h")
        fever_yn = st.checkbox("발열 또는 팬팅 (+10% 고려)")

    total_fluid = uop + insensible + ongoing_loss
    if fever_yn: total_fluid *= 1.1
    
    st.warning(f"### 💧 권장 수액 속도: **{round(total_fluid, 1)}** mL/h")
    st.caption("※ 0.1 mL/h 단위 장비 설정에 최적화되었습니다.")

# --- [3단계: 수혈량 계산] ---
with tabs[2]:
    st.header("3. Transfusion Volume")
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        curr_pcv = st.number_input("환자 현재 PCV (%)", value=15.0, step=0.1)
    with col_t2:
        target_pcv = st.number_input("목표 PCV (%)", value=25.0, step=0.1)
    with col_t3:
        donor_pcv = st.number_input("공혈견/혈액 PCV (%)", value=60.0, step=0.1)

    k_trans = 90 if species == "개(Canine)" else 60
    trans_vol = weight * k_trans * ((target_pcv - curr_pcv) / donor_pcv)
    
    st.error(f"### 🩸 예상 수혈량: **{round(trans_vol, 1)}** mL")

# --- [4단계: CRI 조제 레시피 (Infusion Rate First)] ---
with tabs[3]:
    st.header("4. CRI Preparation Recipe")
    st.write("시린지 펌프의 **속도(mL/h)**를 먼저 결정하면, 그에 맞는 **조제량**을 계산합니다.")
    
    col_c1, col_c2 = st.columns([1, 1.2])
    
    with col_c1:
        cat = st.selectbox("카테고리 선택", list(DRUG_DATA.keys()))
        drug = st.selectbox("약물 선택", list(DRUG_DATA[cat].keys()))
        stock_conc = DRUG_DATA[cat][drug]
        
        # 펌프 속도 고정 (mL/h)
        infusion_rate = st.number_input("설정할 펌프 속도 (mL/h)", value=0.5, step=0.1)
        
        # 목표 용량 설정
        unit = "mcg/kg/min" if drug in ["Epinephrine", "Norepinephrine", "Dopamine", "Dobutamine"] else "mg/kg/h"
        if drug == "Vasopressin": unit = "U/kg/h"
        target_dose = st.number_input(f"목표 용량 ({unit})", value=0.1, step=0.01, format="%.3f")
        
        syringe_vol = st.selectbox("사용할 시린지 전체 용량 (mL)", [10, 20, 50], index=2)

    with col_c2:
        # 계산 로직 (mg/h 또는 mcg/h 환산)
        if unit == "mcg/kg/min":
            needed_drug_hr = (target_dose * weight * 60) / 1000 # mg/h
        else:
            needed_drug_hr = (target_dose * weight) # mg/h or U/h
            
        # 조제 공식
        needed_conc_in_syr = needed_drug_hr / infusion_rate
        total_drug_needed = needed_conc_in_syr * syringe_vol
        drug_ml = total_drug_needed / stock_conc
        diluent_ml = syringe_vol - drug_ml
        
        st.subheader(f"👨‍🍳 {drug} 조제 가이드")
        if drug_ml > syringe_vol:
            st.error("⚠️ 오류: 약물 용량이 시린지 볼륨을 초과합니다. 속도를 높이거나 용량을 조절하세요.")
        else:
            st.info(f"""
            **1. 시린지 펌프 설정:**  ### 🚩 {infusion_rate} mL/h
            
            **2. 조제 레시피 (총 {syringe_vol}mL 기준):**
            *   **{drug} 원액 ({stock_conc}mg/mL):**  **{drug_ml:.2f} mL**
            *   **희석액 (NS 또는 5%DW):**  **{diluent_ml:.2f} mL**
            """)
            
            # 특수 조언 (Epi/NE)
            if drug in ["Epinephrine", "Norepinephrine"]:
                if infusion_rate <= 0.3:
                    st.warning("💡 **Dry Mode 알림:** 현재 속도가 매우 낮습니다. 정확도를 위해 초농축 조제를 고려하십시오.")

st.divider()
st.caption("Royal Animal Medical Center | Clinical Solution | v3.8")
