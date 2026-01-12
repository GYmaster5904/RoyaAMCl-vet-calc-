import streamlit as st
import streamlit.components.v1 as components

# --- [1. 시스템 가독성 및 UI 프로토콜 정의] ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc v23.0", layout="wide")

st.markdown("""
    <style>
    /* 배경 및 텍스트 고대비 강제 고정 */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        color: #111827 !important;
    }
    
    /* CSU 논리 강조 시스템 */
    .csu-card { border: 2px solid #E5E7EB; border-radius: 12px; padding: 20px; background-color: #F9FAFB; margin-bottom: 20px; }
    .header-box { background-color: #1E3A8A; color: white !important; padding: 10px; border-radius: 6px; font-weight: 800; text-align: center; margin-bottom: 15px; }
    .or-badge { background-color: #FEE2E2; color: #DC2626 !important; font-weight: 900; padding: 5px 15px; border-radius: 20px; border: 2px solid #DC2626; display: block; text-align: center; margin: 10px auto; width: fit-content; font-size: 14px; }
    .and-badge { background-color: #DBEAFE; color: #2563EB !important; font-weight: 900; padding: 5px 15px; border-radius: 20px; border: 2px solid #2563EB; display: block; text-align: center; margin: 10px auto; width: fit-content; font-size: 14px; }

    /* CRI 시인성 극대화 (v23.0 전용) */
    .cri-premium-card {
        background-color: #F8FAFC; border: 1px solid #D1D5DB; border-left: 15px solid #10B981;
        padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    .val-speed { font-size: 60px; font-weight: 900; color: #059669 !important; display: block; }
    .val-recipe { font-size: 42px; font-weight: 800; color: #1E3A8A !important; display: block; margin-top: 15px; }

    /* 공식 및 가이드라인 공지 */
    .sop-banner {
        background-color: #111827; color: #FFFFFF !important; padding: 20px; border-radius: 12px; 
        border-left: 10px solid #EF4444; margin-bottom: 25px;
    }
    .sop-banner h3 { color: #F87171 !important; margin: 0 0 10px 0; font-size: 22px; }
    .sop-banner p { color: #E5E7EB !important; font-size: 18px; margin: 5px 0; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 로얄동물메디컬센터 표준 데이터베이스] ---
STOCK = {
    "Epinephrine": 1.0, "Atropine": 0.5, "Vasopressin": 20.0, "Lidocaine": 20.0, "Amiodarone": 50.0,
    "Naloxone": 0.4, "Flumazenil": 0.1, "Atipamezole": 5.0, "Butorphanol": 2.0, "Midazolam": 1.0, 
    "Diazepam": 5.0, "Dexmedetomidine": 0.118, "Dopamine": 32.96, "Dobutamine": 50.0, 
    "Furosemide": 10.0, "Insulin(RI)": 1.0, "KCl": 2.0, "Calcium Gluconate": 100.0, "Sodium Bicarbonate": 1.0,
    "Calcium Chloride": 100.0, "Magnesium Chloride": 200.0, "Dextrose 50%": 500.0
}

DISEASE_FACTORS = {
    "기본/비만": {"성장기": 2.0, "중성화 성견/성묘": 1.2, "미중성화": 1.4, "비만감량": 0.8, "저활동": 1.0},
    "신장/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전": 1.05},
    "췌장/간/소화기": {"췌장염 안정기": 1.1, "간질환 안정": 1.15, "고양이 지방간(HL)": 1.35, "EPI": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

DIET_LIST = {
    "Royal Canin": {"Recovery": 105, "GI (Dry)": 3912, "GI Low Fat (Wet)": 385, "Urinary S/O": 3884, "Renal": 3988},
    "Hill's": {"a/d": 183, "i/d Digestive": 3663, "i/d Low Fat Wet": 341, "k/d Kidney": 4220, "c/d Multicare": 3873}
}

# --- [3. 사이드바 - 고정 환자 정보] ---
with st.sidebar:
    st.image("https://via.placeholder.com/200x50.png?text=ROYAL+ANIMAL+CENTER", use_container_width=True)
    st.header("📋 Patient Profile")
    species = st.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
    weight = st.number_input("체중 (kg)", 0.1, 150.0, 3.1, 0.1, format="%.1f")
    st.markdown("---")
    cat_n = st.selectbox("질환 카테고리", list(DISEASE_FACTORS.keys()))
    sub_cat = st.selectbox("세부 상태", list(DISEASE_FACTORS[cat_n].keys()))
    st.markdown("---")
    st.caption("Clinical Protocol Architect")
    st.markdown("### **Dr. Jaehee Lee**")

# --- [4. 메인 탭 구성] ---
tabs = st.tabs(["🚨 CPCR", "🧪 전해질/삼투압", "💉 CRI 조제", "💧 수액 요법", "🍴 영양 관리", "🩸 수혈"])

# --- TAB 1: CPCR (시계형 메트로놈 & CSU 로직) ---
with tabs[0]:
    st.subheader(f"🚨 CPCR Protocol for {weight:.1f}kg patient")
    
    # 시계형 직관적 메트로놈
    metronome_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; background: #111827; padding: 25px; border-radius: 15px; color: white;">
        <div style="font-size: 24px; margin-bottom: 15px;">Chest Compression Clock</div>
        <div id="gauge" style="width: 120px; height: 120px; border-radius: 50%; border: 8px solid #374151; display: flex; align-items: center; justify-content: center; position: relative;">
            <div id="inner" style="width: 0%; height: 0%; background: #10B981; border-radius: 50%; transition: all 0.05s;"></div>
            <span id="bpmDisp" style="position: absolute; font-size: 28px; font-weight: 900;">120</span>
        </div>
        <div style="margin-top: 20px; width: 80%;">
            <input type="range" id="bpmSlider" min="80" max="140" value="120" style="width: 100%; cursor: pointer;">
        </div>
        <button id="pBtn" style="margin-top: 15px; padding: 10px 40px; font-weight: 900; background: #10B981; border: none; border-radius: 5px; color: white; cursor: pointer;">START</button>
    </div>
    <script>
        const btn = document.getElementById('pBtn'), slider = document.getElementById('bpmSlider'), 
              disp = document.getElementById('bpmDisp'), inner = document.getElementById('gauge');
        let ctx = null, id = null, nextT = 0, play = false;
        function tick() {{
            while (nextT < ctx.currentTime + 0.1) {{
                const o = ctx.createOscillator(), g = ctx.createGain();
                o.connect(g); g.connect(ctx.destination);
                o.frequency.value = 880; g.gain.value = 0.05;
                o.start(nextT); o.stop(nextT + 0.05);
                setTimeout(() => {{ 
                    disp.style.color = '#10B981'; inner.style.boxShadow = '0 0 20px #10B981';
                    setTimeout(() => {{ disp.style.color = 'white'; inner.style.boxShadow = 'none'; }}, 100);
                }}, (nextT - ctx.currentTime) * 1000);
                nextT += 60 / slider.value;
            }}
            id = setTimeout(tick, 25);
        }}
        slider.oninput = () => disp.innerText = slider.value;
        btn.onclick = () => {{
            if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
            if (play) {{ clearTimeout(id); id = null; btn.innerText = 'START'; btn.style.background = '#10B981'; }}
            else {{ nextT = ctx.currentTime; tick(); btn.innerText = 'STOP'; btn.style.background = '#EF4444'; }}
            play = !play;
        }};
    </script>
    """
    components.html(metronome_html, height=320)

    # CSU Logic Columns
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="header-box">VF / Pulseless VT</div>', unsafe_allow_html=True)
        st.write(f"**Defibrillation:** External **{weight*4:.1f}-{weight*6:.1f} J**")
        st.markdown('<div class="or-badge">OR (If prolonged >10 min)</div>', unsafe_allow_html=True)
        st.write(f"**Epinephrine (Low):** {(weight*0.01):.2f} ml IV")
        st.markdown('<div class="or-badge">OR</div>', unsafe_allow_html=True)
        st.write(f"**Vasopressin:** {(weight*0.8/20):.2f} ml IV")
        st.markdown('<div class="and-badge">AND</div>', unsafe_allow_html=True)
        st.write(f"**Amiodarone:** {(weight*5/50):.2f} ml IV")
        st.markdown('<div class="or-badge">OR (Dogs Only)</div>', unsafe_allow_html=True)
        st.write(f"**Lidocaine:** {(weight*2/20):.2f} ml IV")

    with c2:
        st.markdown('<div class="header-box">Asystole / PEA / Bradycardia</div>', unsafe_allow_html=True)
        st.caption("Every other 2 minute BLS cycle 마다 투여 고려")
        st.write(f"**Epinephrine (Low):** {(weight*0.01):.2f} ml IV")
        st.markdown('<div class="or-badge">OR</div>', unsafe_allow_html=True)
        st.write(f"**Vasopressin:** {(weight*0.8/20):.2f} ml IV (1회 한정)")
        st.markdown('<div class="and-badge">AND (Every other cycle)</div>', unsafe_allow_html=True)
        st.write(f"**Atropine:** {(weight*0.04/0.5):.2f} ml IV")
        
        st.markdown("---")
        st.markdown('<div style="background-color:#F3F4F6; padding:10px; border-radius:5px;"><b>Intratracheal (IT):</b> Epi {(weight*0.02):.2f}ml | Atropine {(weight*0.16):.2f}ml</div>', unsafe_allow_html=True)

# --- TAB 2: 전해질/삼투압 ---
with tabs[1]:
    st.header("🧪 Electrolyte & Osmolality Evaluation")
    e1, e2, e3 = st.columns(3)
    with e1:
        st.subheader("1. Input Result")
        na_m = st.number_input("Measured Na+", 100.0, 200.0, 145.0, 0.1); cl_m = st.number_input("Measured Cl-", 70.0, 150.0, 110.0, 0.1)
        glu_m = st.number_input("Glucose", 10.0, 1000.0, 100.0, 1.0); bun_m = st.number_input("BUN", 5.0, 300.0, 20.0, 1.0)
        k_m = st.number_input("Measured K+", 1.0, 10.0, 4.0, 0.1); hco3_m = st.number_input("Measured HCO3-", 5.0, 40.0, 20.0, 0.1)
        bg_s = st.selectbox("Fluid Bag Size (mL)", [30, 50, 100, 250, 500, 1000], index=4)

    with e2:
        st.subheader("2. Assessments")
        c_na = na_m + 1.6*((glu_m-100)/100) if glu_m > 100 else na_m
        osmo = 2*(na_m+k_m) + (glu_m/18) + (bun_m/2.8)
        st.markdown(f'<div class="eval-card"><span class="eval-title">Corrected Na+</span><br><span class="eval-value">{c_na:.1f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="eval-card"><span class="eval-title">Osmolality</span><br><span class="eval-value">{osmo:.1f}</span></div>', unsafe_allow_html=True)
        if hco3_m < 18: st.markdown(f'<div class="eval-card"><span class="eval-title">HCO3- Deficit</span><br><span class="eval-value">{(0.3*weight*(22-hco3_m)):.1f} mEq</span></div>', unsafe_allow_html=True)

    with e3:
        st.subheader("3. Recipe")
        kt = next((v for kr, v in {2.0:80, 2.5:60, 3.0:40, 3.5:28}.items() if k_m <= kr), 10)
        st.markdown(f"""<div class="eval-card" style="border-left-color:#2563EB;">
        <span class="eval-title">KCl (2mEq/ml) Additive</span><br><span class="recipe-text">Add {(kt*bg_s/1000)/2.0:.1f} ml</span><br>
        <p>in {bg_s}ml bag (목표: {kt}mEq/L)</p></div>""", unsafe_allow_html=True)

# --- TAB 3: CRI 조제 (시인성 극대화) ---
with tabs[2]:
    st.header("💉 High-Visibility CRI Protocol")
    dr_c = st.selectbox("약물 선택", ["Butorphanol", "Midazolam", "Dexmedetomidine", "Epinephrine", "Norepinephrine", "Dopamine", "Furosemide", "Insulin(RI)"])
    cr1, cr2 = st.columns([1, 2.5])
    with cr1:
        ir_v = st.number_input("펌프 속도 (mL/h)", 0.1, 100.0, 0.5, 0.1)
        td_v = st.number_input("목표 용량 (mg/kg/h or mcg/kg/min)", 0.0, 50.0, 0.1, 0.01, format="%.3f")
        sv_v = st.selectbox("시린지 용량 (mL)", [10, 20, 50], index=2)
    with cr2:
        mgh = (td_v*weight*60/1000) if dr_c in ["Epinephrine", "Norepinephrine", "Dopamine"] else (td_v*weight)
        dml = (mgh / STOCK[dr_c]) * sv_v / ir_v
        st.markdown(f"""<div class="cri-premium-card">
            <span class="cri-label">🚩 {dr_c} 설정 속도</span><span class="val-speed">{ir_v:.1f} mL/h</span><br>
            <span class="cri-label">🧪 조제법 (총 {sv_v}mL)</span><span class="val-recipe">원액 {dml:.2f} mL + 희석액 {(sv_v-dml):.2f} mL</span>
        </div>""", unsafe_allow_html=True)

# --- TAB 4: 수액 요법 (원장님 SOP) ---
with tabs[3]:
    st.markdown("""<div class="sop-banner"><h3>🚨 Royal Fluid Protocol</h3>
        <p><b>RER 공식: BW × 50 kcal/day</b></p>
        <p>💡 성견/성묘 표준 유지 범위: 40-60 mL/kg/day (시간당 약 2-3 mL/kg)</p></div>""", unsafe_allow_html=True)
    f1, f2 = st.columns([1.5, 1])
    with f1:
        ms = st.radio("수액 모드", ["로얄 Dry Mode (입원)", "AAHA 2024 마취"], horizontal=True)
        if "Dry" in ms:
            mr = st.slider("유지 (mL/kg/hr)", 1.0, 4.0, 2.0, 0.5)
            tf = (weight * mr) + ((weight * st.number_input("탈수 (%)", 0, 15, 0) * 10) / 12) + (st.number_input("지속손실 (mL/day)", value=float(round(weight*1.0, 1))) / 24)
            st.metric("권장 수액 속도", f"{tf:.1f} mL/h")
        else: st.metric("마취 속도 (AAHA)", f"{(weight*5 if species=='개(Canine)' else weight*3):.1f} mL/h")
    with f2:
        if "심장" in sub_cat: st.error("심장 질환: 수액 과부하 주의. RR 20%↑ 시 즉시 중단.")

# --- TAB 5: 영양 관리 (확장 사료 DB) ---
with tabs[4]:
    st.markdown('<div class="sop-banner"><h3>🍽️ Nutrition & Stage Protocol</h3></div>', unsafe_allow_html=True)
    n1, n2 = st.columns(2)
    with n1:
        der = (weight * 50) * DISEASE_FACTORS[cat_n][sub_cat] * (1.1 if st.checkbox("입원 가중치", value=True) else 1.0)
        st_opt = st.radio("전략", ["3단계", "4단계", "5단계"], horizontal=True)
        s_m = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        cs = st.select_slider("현재 단계", options=s_m[st_opt], value=s_m[st_opt][-1])
        st.metric("목표 DER", f"{der*cs:.0f} kcal")
    with n2:
        brand = st.selectbox("사료 브랜드", list(DIET_LIST.keys()))
        prod = st.selectbox("제품", list(DIET_LIST[brand].keys()))
        amt = ((der*cs)/DIET_LIST[brand][prod]) * (1 if "Wet" in prod or "a/d" in prod else 1000)
        st.success(f"### 급여량: **{amt:.1f} {'can' if 'Wet' in prod or 'a/d' in prod else 'g'}**")

# --- TAB 6: 수혈 ---
with tabs[5]:
    st.header("🩸 Blood Transfusion")
    tx1, tx2 = st.columns([1, 1.2])
    with tx1:
        c_p = st.number_input("현재 PCV (%)", 1.0, 50.0, 15.0); t_p = st.number_input("목표 PCV (%)", 1.0, 50.0, 25.0)
        pr = st.radio("제제", ["전혈", "pRBC"], horizontal=True)
        tx_v = weight * (90 if species == "개(Canine)" else 60) * ((t_p - c_p) / (40.0 if pr == "전혈" else 70.0))
        st.metric("수혈 필요량", f"{max(0.0, round(tx_v, 1))} mL")
    with tx2:
        st.info("**[Royal SOP]**\n1. 초기 속도: 0.25-0.5 ml/kg/hr (첫 30분)\n2. 최대 속도: 10ml/kg/hr (심장 안정 시)\n3. 반드시 4시간 이내 완료")

st.divider()
st.caption(f"Royal Animal Medical Center | v23.0 Pro | Clinical Solution by Dr. Jaehee Lee")
