import streamlit as st
import streamlit.components.v1 as components

# --- [1. 페이지 설정 및 디자인 CSS 강제 주입] ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc v19.0", layout="wide")

st.markdown("""
    <style>
    /* 기본 배경 및 글자색 강제 고정 */
    .stApp { background-color: #ffffff !important; color: #1e293b !important; }
    h1, h2, h3, h4, p, span, div { color: #1e293b !important; }

    /* CSU 스타일 카드 레이아웃 */
    .info-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .emergency-card { background-color: #fff1f2; border: 2px solid #e11d48; padding: 15px; border-radius: 10px; }
    
    /* 탭 스타일링 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9; border-radius: 5px 5px 0 0; padding: 10px 20px; font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: #1e3a8a !important; color: white !important; }

    /* CRI 시인성 극대화 (원장님 지시 사항) */
    .cri-display {
        background-color: #f8fafc; padding: 30px; border-radius: 15px;
        border-left: 12px solid #10b981; box-shadow: 0 10px 20px rgba(0,0,0,0.05);
    }
    .cri-label { font-size: 22px; color: #64748b; font-weight: bold; }
    .speed-val { font-size: 50px; color: #059669; font-weight: 900; line-height: 1.2; }
    .recipe-val { font-size: 38px; color: #1e3a8a; font-weight: 800; line-height: 1.3; }

    /* 전해질 가시성 */
    .deficit-text { color: #e11d48; font-size: 28px; font-weight: 900; }
    .supply-text { color: #2563eb; font-size: 28px; font-weight: 900; }
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
        "Recovery (Wet)": 105, "GI (Dry)": 3912, "GI (Wet)": 432, "GI Low Fat (Dry)": 3461, "GI Low Fat (Wet)": 385,
        "Urinary S/O (Dry)": 3884, "Renal (Dry)": 3988, "Hepatic (Dry)": 3906, "Hypoallergenic (Dry)": 3880
    },
    "Hill's (Prescription)": {
        "a/d Urgent Care": 183, "i/d Digestive": 3663, "i/d Wet": 155, "i/d Low Fat Dry": 3316, 
        "i/d Low Fat Wet": 341, "k/d Kidney": 4220, "c/d Multicare": 3873
    }
}

DISEASE_FACTORS = {
    "기본/비만": {"성장기": 2.0, "중성화 성견/성묘": 1.2, "미중성화": 1.4, "비만감량": 0.8, "저활동": 1.0},
    "신장/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전": 1.05},
    "췌장/간/소화기": {"췌장염 안정": 1.1, "간질환 안정": 1.15, "고양이 지방간(HL)": 1.35, "EPI": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

# --- [3. 사이드바: 환자 정보 입력] ---
with st.sidebar:
    st.image("https://via.placeholder.com/200x60.png?text=ROYAL+MEDICAL+CENTER", use_container_width=True)
    st.header("📋 Patient Data")
    species = st.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
    weight = st.number_input("체중 (kg)", 0.1, 150.0, 3.1, 0.1, format="%.1f")
    st.markdown("---")
    cat_n = st.sidebar.selectbox("질환 카테고리", list(DISEASE_FACTORS.keys()))
    sub_cat = st.sidebar.selectbox("세부 상태", list(DISEASE_FACTORS[cat_n].keys()))
    st.markdown("---")
    st.caption("Protocol Architect")
    st.markdown("### Dr. Jaehee Lee")

# --- [4. 메인 대시보드] ---
st.title("🐾 Royal Animal Medical Center Clinical Support")

tabs = st.tabs(["🚨 CPCR (CSU)", "🧪 전해질/삼투압 교정", "💉 CRI 조제", "💧 수액 요법", "🍴 영양 관리", "🩸 수혈"])

# --- TAB 1: CPCR ---
with tabs[0]:
    st.subheader(f"🚨 CPCR Protocol for {weight:.1f}kg")
    bpm = st.number_input("Compression Rate (BPM)", 80, 140, 120, 1, key="bpm_input")
    
    # 안정화된 메트로놈 JS
    metronome_html = f"""
    <div style="display: flex; align-items: center; gap: 20px; background: #1e293b; padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <button id="pBtn" style="padding: 15px 40px; font-weight: 900; cursor: pointer; background: #10b981; color: white; border-radius:8px; border:none; font-size:24px;">▶ START</button>
        <div id="heart" style="font-size: 50px; transition: transform 0.05s;">❤️</div>
        <div style="font-size: 30px; font-weight: bold;">{bpm} BPM</div>
    </div>
    <script>
        let audioCtx = null; let nextT = 0; let timer = null;
        const btn = document.getElementById('pBtn'); const ht = document.getElementById('heart');
        function tick() {{
            while (nextT < audioCtx.currentTime + 0.1) {{
                const osc = audioCtx.createOscillator(); const g = audioCtx.createGain();
                osc.connect(g); g.connect(audioCtx.destination);
                osc.frequency.value = 880; g.gain.value = 0.1;
                osc.start(nextT); osc.stop(nextT + 0.05);
                setTimeout(() => {{ ht.style.transform = 'scale(1.3)'; setTimeout(() => ht.style.transform = 'scale(1)', 50); }}, (nextT - audioCtx.currentTime) * 1000);
                nextT += 60 / {bpm};
            }}
            timer = setTimeout(tick, 25);
        }}
        btn.onclick = () => {{
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (timer) {{ clearTimeout(timer); timer = null; btn.innerText = '▶ START'; btn.style.background = '#10b981'; }}
            else {{ nextT = audioCtx.currentTime; tick(); btn.innerText = '■ STOP'; btn.style.background = '#ef4444'; }}
        }};
    </script>
    """
    components.html(metronome_html, height=140)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div style="background-color:#334155;color:white;padding:10px;border-radius:6px;font-weight:bold;margin-bottom:10px;">VF / Pulseless VT</div>', unsafe_allow_html=True)
        st.error(f"External: {weight*2:.1f} - {weight*4:.1f} J")
        st.write(f"Epi (L): {(weight*0.01):.2f} ml | Amiodarone: {(weight*5/50):.2f} ml")
    with c2:
        st.markdown('<div style="background-color:#334155;color:white;padding:10px;border-radius:6px;font-weight:bold;margin-bottom:10px;">Asystole / PEA</div>', unsafe_allow_html=True)
        st.error(f"Epi (L): {(weight*0.01):.2f} ml | Atropine: {(weight*0.04/0.5):.2f} ml")
    with c3:
        st.markdown('<div style="background-color:#334155;color:white;padding:10px;border-radius:6px;font-weight:bold;margin-bottom:10px;">IT Doses (2x-3x)</div>', unsafe_allow_html=True)
        st.info(f"Epi: {(weight*0.02):.2f} ml | Atropine: {(weight*0.16):.2f} ml")

# --- TAB 2: 전해질 / 삼투압 ---
with tabs[1]:
    st.header("🧪 Electrolyte & Osmolality Evaluation")
    e1, e2, e3 = st.columns(3)
    with e1:
        na = st.number_input("Measured Na+ (mEq/L)", 100.0, 200.0, 145.0, 0.1)
        cl = st.number_input("Measured Cl- (mEq/L)", 70.0, 150.0, 110.0, 0.1)
        glu = st.number_input("Glucose (mg/dL)", 10.0, 1000.0, 100.0, 1.0)
        bun = st.number_input("BUN (mg/dL)", 5.0, 300.0, 20.0, 1.0)
        k_in = st.number_input("Measured K+ (mEq/L)", 1.0, 10.0, 4.0, 0.1)
        hco3 = st.number_input("Measured HCO3- (mEq/L)", 5.0, 40.0, 20.0, 0.1)
        bag = st.selectbox("Fluid Bag Size (mL)", [100, 250, 500, 1000], index=2)

    with e2:
        st.subheader("📊 Assessment")
        corr_na = na + 1.6 * ((glu - 100) / 100) if glu > 100 else na
        osmo = 2 * (na + k_in) + (glu / 18) + (bun / 2.8)
        c_cl = cl * (145 / na)
        
        st.markdown(f"**Corrected Na+:** <span class='deficit-text'>{corr_na:.1f} mEq/L</span>", unsafe_allow_html=True)
        st.markdown(f"**Osmolality:** <span class='deficit-text'>{osmo:.1f} mOsm/kg</span>", unsafe_allow_html=True)
        st.markdown(f"**Corrected Cl-:** <span class='deficit-text'>{c_cl:.1f} mEq/L</span>", unsafe_allow_html=True)
        
        if hco3 < 18:
            def_h = 0.3 * weight * (22 - hco3)
            st.markdown(f"**HCO3- Deficit:** <span class='deficit-text'>{def_h:.1f} mEq</span>", unsafe_allow_html=True)

    with e3:
        st.subheader("👨‍🍳 Recipe")
        k_table = {2.0: 80, 2.5: 60, 3.0: 40, 3.5: 28}
        k_goal = next((v for kr, v in k_table.items() if k_in <= kr), 10)
        k_add = (k_goal * bag / 1000) / 2.0 # KCl 2mEq/ml 기준
        st.markdown(f"**K+ Additive (KCl):** <br><span class='supply-text'>Add {k_add:.1f} mL</span><br><small>in {bag}mL bag (Goal: {k_goal}mEq/L)</small>", unsafe_allow_html=True)
        
        if na > 155:
            fwd = 0.6 * weight * ((na / 145) - 1)
            st.markdown(f"**Free Water Deficit:** <br><span class='supply-text'>{fwd:.2f} Liters</span>", unsafe_allow_html=True)

# --- TAB 3: CRI 조제 (시인성 극대화) ---
with tabs[2]:
    st.header("💉 High-Visibility CRI Recipe")
    dr_sel = st.selectbox("약물 선택", ["Butorphanol", "Midazolam", "Dexmedetomidine", "Epinephrine", "Norepinephrine", "Dopamine", "Furosemide", "Insulin(RI)"])
    cr1, cr2 = st.columns([1, 2])
    with cr1:
        ir_v = st.number_input("설정 속도 (mL/h)", 0.1, 100.0, 0.5, 0.1)
        td_v = st.number_input("목표 용량 (mg/kg/h or mcg/kg/min)", 0.0, 50.0, 0.1, 0.01, format="%.3f")
        sv_v = st.selectbox("시린지 용량 (mL)", [10, 20, 50], index=2)
    with cr2:
        is_mc = dr_sel in ["Epinephrine", "Norepinephrine", "Dopamine"]
        mgh_v = (td_v * weight * 60 / 1000) if is_mc else (td_v * weight)
        dml_v = (mgh_v / STOCK_CONC[dr_sel]) * sv_v / ir_v
        st.markdown(f"""
        <div class="cri-display">
            <span class="cri-label">{dr_sel} 조제 프로토콜</span><br>
            <span class="cri-label">🚩 설정 속도: </span> <span class="speed-val">{ir_v:.1f} mL/h</span><br><br>
            <span class="cri-label">🧪 조제 레시피: </span><br>
            <span class="recipe-val">원액 {dml_v:.2f} mL + 희석액 {(sv_v-dml_v):.2f} mL</span>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 4: 수액 요법 (공지 문구 포함) ---
with tabs[3]:
    st.markdown("""<div style="background-color:#1e293b; color:white; padding:25px; border-radius:12px; border-left:10px solid #ff4b4b; margin-bottom:20px;">
        <h2 style="margin:0; color:#ff4b4b;">RER = BW × 50 kcal/day</h2>
        <p style="margin:5px 0 0 0; font-size:18px;">💡 <b>표준 유지 범위:</b> 40-60 mL/kg/day (시간당 약 2-3 mL/kg)</p></div>""", unsafe_allow_html=True)
    f_c1, f_c2 = st.columns([1.5, 1])
    with f_c1:
        ms = st.radio("수액 상황", ["로얄 Dry Mode (입원)", "AAHA 2024 마취"], horizontal=True)
        if "Dry" in ms:
            m_r = st.slider("유지 (mL/kg/hr)", 1.0, 4.0, 2.0, 0.5)
            d_y = st.number_input("탈수 (%)", 0, 15, 0)
            l_o = st.number_input("지속 손실 (mL/day)", value=float(round(weight*1.0, 1)), step=0.1)
            st.metric("최종 수액 속도", f"{(weight*m_r)+((weight*d_y*10)/12)+(l_o/24):.1f} mL/h")
        else: st.metric("마취 속도", f"{(weight*5 if species=='개(Canine)' else weight*3):.1f} mL/h")
    with f_c2:
        if "심장" in sub_cat: st.error("심장: 유지량 감량 및 RR 모니터링 필수")

# --- TAB 5: 영양 관리 (공식 사료 DB 확장) ---
with tabs[4]:
    st.markdown("""<div style="background-color:#1e293b; color:white; padding:15px; border-radius:10px; border-left:8px solid #3b82f6; margin-bottom:20px;">
        <h3 style="margin:0; color:#3b82f6;">Royal Standard Nutrition Protocol</h3></div>""", unsafe_allow_html=True)
    n1, n2 = st.columns(2)
    with n1:
        rer_v = weight * 50
        fv = DISEASE_FACTORS[cat_n][sub_cat]
        if st.checkbox("입원 가중치(1.1) 적용", value=True): fv *= 1.1
        der = rer_v * fv
        st_sel = st.radio("전략", ["3단계", "4단계", "5단계"], horizontal=True)
        s_m = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        cs = st.select_slider("단계", options=s_m[st_sel], value=s_m[st_sel][-1])
        st.metric("목표 DER", f"{der*cs:.0f} kcal")
    with n2:
        br = st.selectbox("브랜드", list(DIET_DATA.keys()))
        pd = st.selectbox("제품", list(DIET_DATA[br].keys()))
        kc = DIET_DATA[br][pd]
        amt = ((der*cs)/kc) * (1 if "Wet" in pd or "파우치" in pd else 1000)
        st.success(f"### 급여량: **{amt:.1f} {'can' if 'Wet' in pd else 'g'}**")

# --- TAB 6: 수혈 ---
with tabs[5]:
    st.header("🩸 Blood Transfusion")
    tx1, tx2 = st.columns(2)
    with tx1:
        pr = st.radio("제제", ["전혈", "pRBC"], horizontal=True)
        cp = st.number_input("현재 PCV", 1.0, 50.0, 15.0)
        tp = st.number_input("목표 PCV", 1.0, 50.0, 25.0)
        kv = 90 if species == "개(Canine)" else 60
        res = weight * kv * ((tp - cp) / (40.0 if pr == "전혈" else 70.0))
        st.metric("필요 수혈량", f"{max(0.0, round(res, 1))} mL")
    with tx2: st.info("초기 15-30분 0.25-0.5ml/kg/hr 투여.")

st.divider()
st.caption(f"Royal Animal Medical Center | v19.0 Pro | Clinical Solution by Dr. Jaehee Lee")
