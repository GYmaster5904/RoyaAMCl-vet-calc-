import streamlit as st
import streamlit.components.v1 as components

# --- [1. 디자인 및 시인성 해결을 위한 강력한 CSS 프로토콜] ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc v21.0", layout="wide")

st.markdown("""
    <style>
    /* 배경 및 기본 텍스트 고정 */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        color: #111827 !important;
    }
    
    /* CSU 스타일 테이블 디자인 */
    .csu-table {
        width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 15px;
    }
    .csu-table th {
        background-color: #F3F4F6; color: #374151; text-align: left;
        padding: 12px; border-bottom: 2px solid #D1D5DB; font-weight: 800;
    }
    .csu-table td {
        padding: 12px; border-bottom: 1px solid #E5E7EB; color: #111827;
    }
    .csu-condition {
        font-size: 13px; color: #6B7280; font-style: italic; background-color: #F9FAFB; padding: 5px;
    }

    /* 원장님 강조 공지 배너 */
    .notice-banner {
        background-color: #1E293B; color: #FFFFFF !important;
        padding: 20px; border-radius: 10px; border-left: 8px solid #EF4444; margin-bottom: 25px;
    }
    .notice-banner h3 { color: #F87171 !important; margin-bottom: 10px; }
    .notice-banner p { color: #E5E7EB !important; font-size: 16px; margin: 5px 0; }

    /* CRI 조제 카드 - 가독성 및 세련미 강화 */
    .cri-pro-card {
        background-color: #F9FAFB; border: 1px solid #D1D5DB; border-left: 12px solid #10B981;
        padding: 30px; border-radius: 12px; margin-top: 20px;
    }
    .val-large { font-size: 42px; font-weight: 900; color: #059669 !important; }
    .val-mid { font-size: 30px; font-weight: 800; color: #1E3A8A !important; }

    /* 탭 메뉴 시인성 */
    .stTabs [data-baseweb="tab"] { color: #4B5563 !important; font-weight: 600; font-size: 16px; }
    .stTabs [aria-selected="true"] { color: #1E3A8A !important; border-bottom-color: #1E3A8A !important; }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 데이터베이스] ---
STOCK_CONC = {
    "Epinephrine": 1.0, "Atropine": 0.5, "Vasopressin": 20.0, "Lidocaine": 20.0, "Amiodarone": 50.0,
    "Naloxone": 0.4, "Flumazenil": 0.1, "Atipamezole": 5.0, "Butorphanol": 2.0, "Midazolam": 1.0, 
    "Diazepam": 5.0, "Dexmedetomidine": 0.118, "Dopamine": 32.96, "Dobutamine": 50.0, 
    "Furosemide": 10.0, "Insulin(RI)": 1.0, "KCl": 2.0, "Calcium Gluconate": 100.0, "Sodium Bicarbonate": 1.0
}

DIET_DATA = {
    "Royal Canin (Prescription)": {
        "Recovery (Wet, 100g)": 105, "GI (Dry)": 3912, "GI (Wet, 400g)": 432, "GI Low Fat (Dry)": 3461, 
        "GI Low Fat (Wet, 410g)": 385, "Urinary S/O (Dry)": 3884, "Renal (Dry)": 3988, "Hepatic (Dry)": 3906
    },
    "Hill's (Prescription)": {
        "a/d Urgent Care": 183, "i/d Digestive": 3663, "i/d Wet": 155, "i/d Low Fat Wet": 341, "k/d Kidney": 4220
    }
}

DISEASE_FACTORS = {
    "기본/비만": {"성장기": 2.0, "중성화 성견/성묘": 1.2, "미중성화": 1.4, "비만감량": 0.8, "저활동": 1.0},
    "신장/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전": 1.05},
    "췌장/간/소화기": {"췌장염 안정": 1.1, "간질환 안정": 1.15, "고양이 지방간(HL)": 1.35, "EPI": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

# --- [3. 사이드바 - 고정 환자 정보] ---
with st.sidebar:
    st.header("📋 Patient Info")
    species = st.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
    weight = st.number_input("체중 (kg)", 0.1, 150.0, 3.1, 0.1, format="%.1f")
    st.markdown("---")
    cat_n = st.selectbox("질환 카테고리", list(DISEASE_FACTORS.keys()))
    sub_cat = st.selectbox("세부 상태", list(DISEASE_FACTORS[cat_n].keys()))
    st.markdown("---")
    st.caption("Clinical Protocol Architect")
    st.markdown("### Dr. Jaehee Lee")

# --- [4. 메인 탭 구성] ---
tabs = st.tabs(["🚨 CPCR (CSU Style)", "🧪 전해질/삼투압", "💉 CRI 조제", "💧 수액 요법", "🍴 영양 관리", "🩸 수혈"])

# --- TAB 1: CPCR (CSU 스타일 완벽 반영) ---
with tabs[0]:
    st.subheader(f"🚨 CPCR Protocol for {weight:.1f}kg patient")
    
    # Reversal narcotics Section (상단 고정)
    rev_nal = (weight * 0.04 / 0.4)
    rev_flu = (weight * 0.01 / 0.1)
    rev_ati = (weight * 0.1 / 5.0)
    st.markdown(f"""<div style="background-color:#FEE2E2; padding:10px; border-radius:5px; margin-bottom:15px; border:1px solid #EF4444;">
    <b>Reverse narcotics with:</b> Naloxone {rev_nal:.2f}ml | Flumazenil {rev_flu:.2f}ml | Atipamezole {rev_ati:.2f}ml</div>""", unsafe_allow_html=True)

    # Metronome
    bpm = st.number_input("Compression Rate (BPM)", 80, 140, 120, 1)
    metronome_html = f"""
    <div style="display: flex; align-items: center; gap: 20px; background: #1E293B; padding: 15px; border-radius: 10px; color: white; margin-bottom:20px;">
        <button id="pBtn" style="padding: 10px 25px; font-weight: 900; cursor: pointer; background: #10B981; color: white; border:none; border-radius:5px;">▶ START METRONOME</button>
        <div id="heart">❤️</div><div style="font-size: 20px;">{bpm} BPM</div>
    </div>
    <script>
        let audioCtx = null; let nextT = 0; let timer = null;
        const btn = document.getElementById('pBtn'); const ht = document.getElementById('heart');
        function tick() {{
            while (nextT < audioCtx.currentTime + 0.1) {{
                const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                osc.connect(gain); gain.connect(audioCtx.destination);
                osc.frequency.value = 880; gain.gain.value = 0.05;
                osc.start(nextT); osc.stop(nextT + 0.05);
                nextT += 60 / {bpm};
            }}
            timer = setTimeout(tick, 25);
        }}
        btn.onclick = () => {{
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (timer) {{ clearTimeout(timer); timer = null; btn.innerText = '▶ START METRONOME'; btn.style.background = '#10B981'; }}
            else {{ nextT = audioCtx.currentTime; tick(); btn.innerText = '■ STOP'; btn.style.background = '#EF4444'; }}
        }};
    </script>
    """
    components.html(metronome_html, height=100)

    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.markdown("#### Ventricular Fibrillation / V-Tach")
        st.markdown(f"""<table class="csu-table">
        <tr><th>Treatment</th><th>Dose Instruction</th><th>Amount (ml)</th></tr>
        <tr><td>Defibrillation</td><td>EXTERNAL: 4-6 J/kg</td><td><b>{weight*4:.1f} - {weight*6:.1f} J</b></td></tr>
        <tr><td>Defibrillation</td><td>INTERNAL: 0.5-1 J/kg</td><td><b>{weight*0.5:.1f} - {weight*1.0:.1f} J</b></td></tr>
        <tr><td colspan="3" class="csu-condition">Provide 1 shock, then resume chest compressions for 120 seconds.</td></tr>
        <tr><td>Epinephrine (Low)</td><td>0.01 mg/kg IV (Prolonged >10m)</td><td><b>{(weight*0.01):.2f} ml</b></td></tr>
        <tr><td>Vasopressin</td><td>0.8 U/kg IV</td><td><b>{(weight*0.8/20):.2f} ml</b></td></tr>
        <tr><td>Amiodarone</td><td>5 mg/kg IV</td><td><b>{(weight*5/50):.2f} ml</b></td></tr>
        <tr><td>Lidocaine (Dogs)</td><td>2 mg/kg IV (If Amiodarone N/A)</td><td><b>{(weight*2/20):.2f} ml</b></td></tr>
        </table>""", unsafe_allow_html=True)

    with col_c2:
        st.markdown("#### Asystole / PEA / Bradycardia")
        st.markdown(f"""<table class="csu-table">
        <tr><th>Drug</th><th>Cycle Condition</th><th>Amount (ml)</th></tr>
        <tr><td>Epinephrine (Low)</td><td>Every other 2 min BLS cycle</td><td><b>{(weight*0.01):.2f} ml</b></td></tr>
        <tr><td>Vasopressin</td><td>One time only (instead of Epi)</td><td><b>{(weight*0.8/20):.2f} ml</b></td></tr>
        <tr><td>Atropine</td><td>Every other cycle only</td><td><b>{(weight*0.04/0.5):.2f} ml</b></td></tr>
        <tr><td colspan="3" class="csu-condition">If available, consider transthoracic pacing (Must be early).</td></tr>
        </table>
        <br>
        <table class="csu-table">
        <tr><th colspan="2">Intratracheal Doses (IT) - Dose = 2x-3x IV</th></tr>
        <tr><td>Epinephrine</td><td><b>{(weight*0.02):.2f} ml</b></td></tr>
        <tr><td>Atropine</td><td><b>{(weight*0.16):.2f} ml</b></td></tr>
        <tr><td>Lidocaine</td><td><b>{(weight*0.20):.2f} ml</b></td></tr>
        </table>""", unsafe_allow_html=True)

# --- TAB 2: 전해질 / 삼투압 ---
with tabs[1]:
    st.header("🧪 Electrolyte & Osmolality Evaluation")
    e1, e2, e3 = st.columns(3)
    with e1:
        st.subheader("1. Input Data")
        na_m = st.number_input("Measured Na+", 100.0, 200.0, 145.0, 0.1)
        cl_m = st.number_input("Measured Cl-", 70.0, 150.0, 110.0, 0.1)
        glu_m = st.number_input("Measured Glucose", 10.0, 1000.0, 100.0, 1.0)
        bun_m = st.number_input("Measured BUN", 5.0, 300.0, 20.0, 1.0)
        k_m = st.number_input("Measured K+", 1.0, 10.0, 4.0, 0.1)
        hco3_m = st.number_input("Measured HCO3-", 5.0, 40.0, 20.0, 0.1)
        bag_s = st.selectbox("Fluid Bag Size (mL)", [30, 50, 100, 250, 500, 1000], index=4)

    with e2:
        st.subheader("2. Evaluation")
        c_na = na_m + 1.6 * ((glu_m - 100) / 100) if glu_m > 100 else na_m
        osmo_m = 2 * (na_m + k_m) + (glu_m / 18) + (bun_m / 2.8)
        c_cl_m = cl_m * (145 / na_m)
        
        st.markdown(f"""
        <div class="info-card"><b>Corrected Na+:</b><br><span class="deficit-text">{c_na:.1f} mEq/L</span></div>
        <div class="info-card"><b>Osmolality:</b><br><span class="deficit-text">{osmo_m:.1f} mOsm/kg</span></div>
        <div class="info-card"><b>Corrected Cl-:</b><br><span class="deficit-text">{c_cl_m:.1f} mEq/L</span></div>
        """, unsafe_allow_html=True)

    with e3:
        st.subheader("3. Correction Recipe")
        k_step = {2.0: 80, 2.5: 60, 3.0: 40, 3.5: 28}
        k_targ = next((v for kr, v in k_step.items() if k_m <= kr), 10)
        k_ml_add = (k_targ * bag_s / 1000) / 2.0
        st.markdown(f"""<div class="info-card" style="border-left-color:#2563EB;">
        <b>KCl (2mEq/ml) Additive:</b><br><span class="supply-text">Add {k_ml_add:.1f} mL</span><br>
        <small>Targeting {k_targ} mEq/L in {bag_s}mL bag</small></div>""", unsafe_allow_html=True)
        
        if hco3_m < 18:
            b_def = 0.3 * weight * (22 - hco3_m)
            st.markdown(f'<div class="info-card" style="border-left-color:#EF4444;"><b>Bicarb Deficit:</b><br><span class="deficit-text">{b_def:.1f} mEq</span></div>', unsafe_allow_html=True)

# --- TAB 3: CRI 조제 ---
with tabs[2]:
    st.header("💉 High-Visibility CRI Recipe")
    dr_c = st.selectbox("약물 선택", ["Butorphanol", "Midazolam", "Dexmedetomidine", "Epinephrine", "Norepinephrine", "Dopamine", "Furosemide", "Insulin(RI)"])
    cr1, cr2 = st.columns([1, 2.5])
    with cr1:
        ir_v = st.number_input("설정 속도 (mL/h)", 0.1, 100.0, 0.5, 0.1)
        td_v = st.number_input("목표 용량 (mg/kg/h or mcg/kg/min)", 0.0, 50.0, 0.1, 0.01, format="%.3f")
        sv_v = st.selectbox("시린지 용량 (mL)", [10, 20, 50], index=2)
    with cr2:
        mgh_v = (td_v * weight * 60 / 1000) if dr_c in ["Epinephrine", "Norepinephrine", "Dopamine"] else (td_v * weight)
        dml_v = (mgh_v / STOCK_CONC[dr_c]) * sv_v / ir_v
        st.markdown(f"""<div class="cri-pro-card">
            <span class="cri-label">🚩 {dr_c} 설정 속도: </span><br><span class="val-large">{ir_v:.1f} mL/h</span><br><br>
            <span class="cri-label">🧪 조제 레시피: </span><br><span class="val-mid">원액 {dml_v:.2f} mL + 희석액 {(sv_v-dml_v):.2f} mL</span>
        </div>""", unsafe_allow_html=True)

# --- TAB 4: 수액 요법 (공지사항 고정) ---
with tabs[3]:
    st.markdown("""<div class="notice-banner">
        <h3>🚨 Royal Standard Protocol</h3>
        <p><b>RER 공식: BW × 50 kcal/day</b></p>
        <p>💡 표준 유지 범위: 40-60 mL/kg/day (시간당 약 2-3 mL/kg)</p>
    </div>""", unsafe_allow_html=True)
    
    f1, f2 = st.columns([1.5, 1])
    with f1:
        ms = st.radio("상황 선택", ["로얄 Dry Mode (입원)", "AAHA 2024 마취"], horizontal=True)
        if "Dry" in ms:
            mr = st.slider("유지 (mL/kg/hr)", 1.0, 4.0, 2.0, 0.5)
            dy = st.number_input("탈수 (%)", 0, 15, 0)
            lo = st.number_input("지속 손실 (mL/day)", value=float(round(weight*1.0, 1)), step=0.1)
            st.metric("최종 수액 속도", f"{(weight*mr)+((weight*dy*10)/12)+(lo/24):.1f} mL/h")
        else: st.metric("마취 수액 속도", f"{(weight*5 if species=='개(Canine)' else weight*3):.1f} mL/h")
    with f2:
        st.subheader("⚠️ Monitoring Guide")
        st.markdown("- Chemosis & Nasal Discharge 확인\n- RR 20%↑ 또는 Crackles 발생 시 중단\n- 24시간 내 체중 10%↑ 증가 시 감량")

# --- TAB 5: 영양 관리 ---
with tabs[4]:
    st.markdown('<div class="notice-banner"><h3>🍽️ Nutrition Protocol (3/4/5 Stages)</h3></div>', unsafe_allow_html=True)
    n1, n2 = st.columns(2)
    with n1:
        rer_val = weight * 50
        fv = DISEASE_FACTORS[cat_n][sub_cat]
        if st.checkbox("입원 가중치(1.1) 적용", value=True): fv *= 1.1
        der = rer_val * fv
        st_opt = st.radio("급여 전략", ["3단계", "4단계", "5단계"], horizontal=True)
        s_m = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        cs = st.select_slider("현재 단계", options=s_m[st_opt], value=s_m[st_opt][-1])
        st.metric("목표 DER", f"{der*cs:.0f} kcal")
    with n2:
        br = st.selectbox("사료 브랜드", list(DIET_DATA.keys()))
        pd = st.selectbox("제품 선택", list(DIET_DATA[br].keys()))
        kcal = DIET_DATA[br][pd]
        amt = ((der*cs)/kcal) * (1 if "Wet" in pd else 1000)
        st.success(f"### 급여량: **{amt:.1f} {'can' if 'Wet' in pd else 'g'}**")

# --- TAB 6: 수혈 ---
with tabs[5]:
    st.header("🩸 Blood Transfusion")
    tx1, tx2 = st.columns([1, 1.2])
    with tx1:
        pr = st.radio("제제", ["전혈", "pRBC"], horizontal=True)
        cp = st.number_input("환자 현재 PCV (%)", 1.0, 50.0, 15.0)
        tp = st.number_input("목표 PCV (%)", 1.0, 50.0, 25.0)
        kv = 90 if species == "개(Canine)" else 60
        res = weight * kv * ((tp - cp) / (40.0 if pr == "전혈" else 70.0))
        st.metric("필요 수혈량", f"{max(0.0, round(res, 1))} mL")
    with tx2:
        st.info("""
        **[수혈 관리 표준 지침]**
        1. **초기 속도:** 0.25-0.5 ml/kg/hr (첫 30분간 부작용 집중 감시)
        2. **최대 속도:** 건강 환자 10ml/kg/hr, 심장병 환자 2-4ml/kg/hr
        3. **시간 제한:** 세균 증식 방지를 위해 반드시 **4시간 이내** 완료
        4. **전용 세트:** 170-260μm 필터가 포함된 수혈 전용 세트 사용 필수
        5. **가온:** 저체온증 환자가 아니면 과도한 가온 금지 (용혈 방지)
        """)

st.divider()
st.caption(f"Royal Animal Medical Center | v21.0 Pro | Clinical Solution by Dr. Jaehee Lee")
