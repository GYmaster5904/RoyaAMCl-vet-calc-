import streamlit as st
import streamlit.components.v1 as components

# --- [1. 페이지 설정 및 디자인 CSS] ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc v18.0", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    [data-theme="dark"] .stApp { background-color: #0f172a; color: #f8fafc; }

    /* 결과 카드 디자인 - 고대비 확보 */
    .result-card {
        padding: 25px; border-radius: 12px; margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15); border-left: 10px solid;
    }
    .deficit-card { background-color: #ffffff; border-color: #ef4444; color: #1e293b; }
    .supply-card { background-color: #ffffff; border-color: #3b82f6; color: #1e293b; }
    
    .card-title { font-size: 1.2rem; font-weight: 800; margin-bottom: 5px; display: block; }
    .card-value { font-size: 2.3rem; font-weight: 900; display: block; margin: 5px 0; }
    .card-sub { font-size: 1rem; color: #475569; font-weight: 600; }

    /* CRI 조제 카드 - 시인성 극대화 */
    .cri-card {
        background-color: #ffffff; padding: 35px; border-radius: 15px; border-left: 12px solid #10b981;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); color: #1e293b;
    }
    .speed-value { color: #059669; font-weight: 900; font-size: 40px; }
    .recipe-value { color: #1e3a8a; font-weight: 800; font-size: 32px; }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 데이터베이스] ---
STOCK_CONC = {
    "Epinephrine": 1.0, "Atropine": 0.5, "Vasopressin": 20.0, "Lidocaine": 20.0, "Amiodarone": 50.0,
    "Butorphanol": 2.0, "Midazolam": 1.0, "Diazepam": 5.0, "Dexmedetomidine": 0.118,
    "Dopamine": 32.96, "Dobutamine": 50.0, "Furosemide": 10.0, "Insulin(RI)": 1.0,
    "KCl": 2.0, "Calcium Gluconate": 100.0, "Sodium Bicarbonate": 1.0
}

DIET_DATA = {
    "Royal Canin (Prescription)": {
        "Recovery (Wet, 100g)": 105, "GI (Dry)": 3912, "GI (Wet, 400g)": 432, "GI Low Fat (Dry)": 3461, 
        "GI Low Fat (Wet, 410g)": 385, "Urinary S/O (Dry)": 3884, "Renal (Dry)": 3988, "Hepatic (Dry)": 3906
    },
    "Hill's (Prescription Diet)": {
        "a/d Urgent Care (Wet, 156g)": 183, "i/d Digestive Care (Dry)": 3663, "i/d (Wet, 156g)": 155,
        "i/d Low Fat (Dry)": 3316, "k/d Kidney Care (Dry)": 4220, "c/d Multicare (Dry)": 3873
    }
}

DISEASE_FACTORS = {
    "기본/비만": {"성장기": 2.0, "중성화 성견/성묘": 1.2, "미중성화": 1.4, "비만감량": 0.8, "저활동": 1.0},
    "신장/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전": 1.05},
    "췌장/간/소화기": {"췌장염 안정": 1.1, "간질환 안정": 1.15, "고양이 지방간(HL)": 1.35, "EPI": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

# --- [3. 사이드바 정보] ---
with st.sidebar:
    st.header("📋 Patient Info")
    species = st.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
    weight = st.number_input("체중 (kg)", min_value=0.1, value=3.1, step=0.1, format="%.1f")
    st.markdown("---")
    cat_n = st.sidebar.selectbox("질환 카테고리", list(DISEASE_FACTORS.keys()))
    sub_cat = st.sidebar.selectbox("세부 상태", list(DISEASE_FACTORS[cat_n].keys()))
    st.markdown("---")
    st.caption("Clinical Protocol Architect")
    st.markdown(f"### **Dr. Jaehee Lee**")

# --- [4. 메인 탭 구성] ---
tabs = st.tabs(["🚨 CPCR", "🧪 전해질/삼투압 교정", "💉 CRI 조제", "💧 수액 요법", "🍴 영양 관리", "🩸 수혈"])

# --- TAB 1: CPCR (안정화된 메트로놈) ---
with tabs[0]:
    st.markdown(f"### 🚨 CPCR Protocol for {weight:.1f}kg patient")
    bpm = st.number_input("Compression Rate (BPM)", 80, 140, 120, 1)
    metronome_js = f"""
    <div style="display: flex; align-items: center; gap: 20px; background: #1e293b; padding: 20px; border-radius: 12px; color: white;">
        <button id="pBtn" style="padding: 12px 30px; font-weight: bold; cursor: pointer; background: #10b981; color: white; border-radius:8px; border:none; font-size:20px;">▶ START</button>
        <div id="heart" style="font-size: 40px; transition: transform 0.05s;">❤️</div> <div style="font-size: 24px; font-weight: bold;">{bpm} BPM</div>
    </div>
    <script>
        let audioCtx = null; let nextTick = 0; let timerID = null;
        const btn = document.getElementById('pBtn'); const ht = document.getElementById('heart');
        function scheduleTick() {{
            while (nextTick < audioCtx.currentTime + 0.1) {{
                const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                osc.connect(gain); gain.connect(audioCtx.destination);
                osc.frequency.value = 880; gain.gain.value = 0.1;
                osc.start(nextTick); osc.stop(nextTick + 0.05);
                setTimeout(() => {{ ht.style.transform = 'scale(1.3)'; setTimeout(() => ht.style.transform = 'scale(1)', 50); }}, (nextTick - audioCtx.currentTime) * 1000);
                nextTick += 60 / {bpm};
            }}
            timerID = setTimeout(scheduleTick, 25);
        }}
        btn.onclick = () => {{
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (timerID) {{ clearTimeout(timerID); timerID = null; btn.innerText = '▶ START'; btn.style.background = '#10b981'; }}
            else {{ nextTick = audioCtx.currentTime; scheduleTick(); btn.innerText = '■ STOP'; btn.style.background = '#ef4444'; }}
        }};
    </script>
    """
    components.html(metronome_js, height=120)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div style="background-color:#334155;color:white;padding:8px;border-radius:4px;font-weight:bold;">VF / VT</div>', unsafe_allow_html=True)
        st.error(f"External: {weight*2:.1f}-{weight*4:.1f} J")
        st.write(f"Epi (L): {(weight*0.01):.2f} ml | Amiodarone: {(weight*5/50):.2f} ml")
    with c2:
        st.markdown('<div style="background-color:#334155;color:white;padding:8px;border-radius:4px;font-weight:bold;">Asystole / PEA</div>', unsafe_allow_html=True)
        st.error(f"Epi (L): {(weight*0.01):.2f} ml | Atropine: {(weight*0.04/0.5):.2f} ml")
    with c3:
        st.markdown('<div style="background-color:#334155;color:white;padding:8px;border-radius:4px;font-weight:bold;">IT Doses (2-3x)</div>', unsafe_allow_html=True)
        st.info(f"Epi: {(weight*0.02):.2f} ml | Atropine: {(weight*0.16):.2f} ml")

# --- TAB 2: 전해질 & 삼투압 교정 ( v18.0 핵심 업데이트) ---
with tabs[1]:
    st.header("🧪 Electrolyte, Osmolality & Glucose Correction")
    col_e1, col_e2, col_e3 = st.columns([1.2, 1.2, 1.2])
    
    with col_e1:
        st.subheader("1. 검사 결과 입력")
        cur_na = st.number_input("Measured Na+ (mEq/L)", 100.0, 200.0, 145.0, 0.1)
        cur_k = st.number_input("Measured K+ (mEq/L)", 1.0, 10.0, 4.0, 0.1)
        cur_cl = st.number_input("Measured Cl- (mEq/L)", 70.0, 150.0, 110.0, 0.1)
        cur_hco3 = st.number_input("Measured HCO3- (mEq/L)", 5.0, 40.0, 20.0, 0.1)
        cur_ica = st.number_input("Measured iCa (mmol/L)", 0.50, 2.00, 1.20, 0.01)
        cur_glu = st.number_input("Measured Glucose (mg/dL)", 10.0, 1000.0, 100.0, 1.0)
        cur_bun = st.number_input("Measured BUN (mg/dL)", 5.0, 300.0, 20.0, 1.0)
        bag_v = st.selectbox("수액 백 용량 (mL)", [100, 250, 500, 1000], index=2)

    with col_e2:
        st.subheader("2. 종합 평가 (Assessment)")
        
        # 고혈당 Na 교정
        corr_na = cur_na + 1.6 * ((cur_glu - 100) / 100) if cur_glu > 100 else cur_na
        st.markdown(f'<div class="result-card deficit-card"><span class="card-title">Corrected Na+ (for Glu)</span><span class="card-value">{corr_na:.1f} mEq/L</span><span class="card-sub">고혈당을 배제한 실제 Na+ 수치</span></div>', unsafe_allow_html=True)
        
        # 삼투압 계산
        osmo = 2 * (cur_na + cur_k) + (cur_glu / 18) + (cur_bun / 2.8)
        st.markdown(f'<div class="result-card deficit-card"><span class="card-title">Calculated Osmolality</span><span class="card-value">{osmo:.1f} mOsm/kg</span><span class="card-sub">정상 범위: 290-310 mOsm/kg</span></div>', unsafe_allow_html=True)

        # Cl Corrected
        corr_cl = cur_cl * (145 / cur_na)
        st.markdown(f'<div class="result-card deficit-card"><span class="card-title">Corrected Chloride</span><span class="card-value">{corr_cl:.1f} mEq/L</span><span class="card-sub">산-염기 불균형 감별 (정상: 107-113)</span></div>', unsafe_allow_html=True)

    with col_e3:
        st.subheader("3. 보정 레시피 (Recipe)")
        
        # Potassium Supply (v17.0 검증 로직)
        k_map = {2.0: 80, 2.5: 60, 3.0: 40, 3.5: 28}
        k_goal = next((v for k_lim, v in k_map.items() if cur_k <= k_lim), 10)
        k_ml = (k_goal * bag_v / 1000) / 2.0 # KCl 2mEq/ml 기준
        st.markdown(f'<div class="result-card supply-card"><span class="card-title">K+ Additive (KCl)</span><span class="card-value">Add {k_ml:.1f} mL</span><span class="card-sub">수액 {bag_v}mL 당 혼합량 (목표: {k_goal}mEq/L)</span></div>', unsafe_allow_html=True)

        # HCO3 Deficit
        if cur_hco3 < 18:
            h_def = 0.3 * weight * (22 - cur_hco3)
            st.markdown(f'<div class="result-card supply-card"><span class="card-title">HCO3- Deficit</span><span class="card-value">{h_def:.1f} mEq</span><span class="card-sub">Bicarb 원액(1mEq/ml) 총 보정량</span></div>', unsafe_allow_html=True)

        # iCa Bolus
        if cur_ica < 1.0:
            ca_v = weight * 0.5
            st.markdown(f'<div class="result-card supply-card"><span class="card-title">iCa Emergency Bolus</span><span class="card-value">{ca_v:.1f} mL</span><span class="card-sub">10% Ca-Gluconate (Over 10-20m)</span></div>', unsafe_allow_html=True)

# --- TAB 3: CRI 조제 (전해질 통합으로 간소화) ---
with tabs[2]:
    st.header("💉 CRI 조제 가이드")
    dr_cri = st.selectbox("약물 선택", ["Butorphanol", "Midazolam", "Dexmedetomidine", "Epinephrine", "Norepinephrine", "Dopamine", "Furosemide", "Insulin(RI)"])
    cr1, cr2 = st.columns([1, 2])
    with cr1:
        ir = st.number_input("펌프 속도 (mL/h)", 0.1, 100.0, 0.5, 0.1)
        td = st.number_input("목표 (mg/kg/h or mcg/kg/min)", 0.0, 50.0, 0.1, 0.01, format="%.3f")
        sv = st.selectbox("시린지 볼륨 (mL)", [10, 20, 50], index=2)
    with cr2:
        is_m = dr_cri in ["Epinephrine", "Norepinephrine", "Dopamine"]
        mgh = (td * weight * 60 / 1000) if is_m else (td * weight)
        dml = (mgh / STOCK_CONC[dr_cri]) * sv / ir
        st.markdown(f"""<div class="cri-card"><span class="cri-label">{dr_cri} 조제 레시피</span><br><span class="cri-label">설정 속도: </span> <span class="speed-value">{ir:.1f} mL/h</span><br><br><span class="cri-label">조제법: </span> <span class="recipe-value">원액 {dml:.2f} mL + 희석액 {(sv-dml):.2f} mL</span></div>""", unsafe_allow_html=True)

# --- TAB 4: 수액 요법 (공지사항 상시 노출) ---
with tabs[3]:
    st.markdown("""<div style="background-color:#1e293b; color:white; padding:20px; border-radius:12px; border-left:8px solid #ff4b4b;">
        <h3 style="margin:0; color:#ff4b4b;">RER = BW × 50 kcal/day</h3>
        <p style="margin:5px 0 0 0;">💡 <b>표준 유지 범위:</b> 40-60 mL/kg/day (시간당 약 2-3 mL/kg)</p></div>""", unsafe_allow_html=True)
    f1, f2 = st.columns([1.5, 1])
    with f1:
        m_sel = st.radio("상황", ["로얄 Dry Mode (입원)", "AAHA 2024 마취"], horizontal=True)
        if "Dry" in m_sel:
            mr = st.slider("유지 용량 (mL/kg/hr)", 1.0, 4.0, 2.0, 0.5)
            dy = st.number_input("탈수 (%)", 0, 15, 0)
            lo = st.number_input("지속 손실 (mL/day)", value=float(round(weight*1.0, 1)), step=0.1)
            st.metric("최종 수액 속도", f"{(weight*mr)+((weight*dy*10)/12)+(lo/24):.1f} mL/h")
        else: st.metric("마취 속도", f"{(weight*5 if species=='개(Canine)' else weight*3):.1f} mL/h")
    with f2:
        if "심장" in sub_cat: st.error("심장질환: 유지량 하향 조절 및 RR 감시 필수")

# --- TAB 5: 영양 관리 ---
with tabs[4]:
    n1, n2 = st.columns(2)
    with n1:
        rer_v = weight * 50
        fv = DISEASE_FACTORS[cat_n][sub_cat]
        if st.checkbox("입원 가중치(1.1) 적용", value=True, key="nut_v18"): fv *= 1.1
        der = rer_v * fv
        st_opt = st.radio("급여 전략", ["3단계", "4단계", "5단계"], horizontal=True)
        s_m = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        cs = st.select_slider("현재 단계", options=s_m[st_opt], value=s_m[st_opt][-1])
        st.metric("목표 DER", f"{der*cs:.0f} kcal")
    with n2:
        br = st.selectbox("사료 브랜드", list(DIET_DATA.keys()))
        pd = st.selectbox("제품 선택", list(DIET_DATA[br].keys()))
        kcal = DIET_DATA[br][pd]
        amt = ((der*cs)/kcal) * (1 if "Wet" in pd else 1000)
        st.success(f"### 최종 급여량: **{amt:.1f} {'can/pouch' if 'Wet' in pd else 'g'}**")

# --- TAB 6: 수혈 ---
with tabs[5]:
    st.header("🩸 Blood Transfusion")
    tx1, tx2 = st.columns(2)
    with tx1:
        pr = st.radio("제제", ["전혈", "pRBC"], horizontal=True)
        cp, tp = st.number_input("현재 PCV", 1.0, 50.0, 15.0), st.number_input("목표 PCV", 1.0, 50.0, 25.0)
        kv = 90 if species == "개(Canine)" else 60
        res = weight * kv * ((tp - cp) / (40.0 if pr == "전혈" else 70.0))
        st.metric("예상 수혈량", f"{max(0.0, round(res, 1))} mL")
    with tx2: st.info("수혈 관리: 초기 속도 0.25-0.5ml/kg/hr. 4시간 이내 완료 필수.")

st.divider()
st.caption(f"Royal Animal Medical Center | v18.0 | Clinical Solution by Dr. Jaehee Lee")
