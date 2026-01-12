
import streamlit as st
import streamlit.components.v1 as components

# --- [1. 시인성 및 테마 충돌 완전 해결을 위한 강력한 CSS 프로토콜] ---
st.set_page_config(page_title="RAMC Advanced Clinical Intelligence", layout="wide")

st.markdown("""
    <style>
    /* [VITAL] 다크모드 무시 및 배경/글자색 강제 고정 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        color: #111827 !important;
    }

    /* 모든 마크다운 텍스트 검은색 강제 */
    .stMarkdown, p, span, label, div {
        color: #111827 !important;
    }

    /* [CRITICAL] 선택창(Selectbox) 및 입력창 내부 시인성 해결 */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    input, select, textarea {
        background-color: #F1F5F9 !important;
        color: #000000 !important;
        border: 2px solid #CBD5E1 !important;
        font-weight: 600 !important;
    }
    
    /* 드롭다운 리스트 항목 가독성 확보 */
    div[role="listbox"] div {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }

    /* 상단 공식 공지 배너 - 시인성 확보를 위해 배경색 조정 */
    .sop-banner-final {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        padding: 30px;
        border-radius: 15px;
        border-left: 10px solid #EF4444 !important;
        margin-bottom: 25px;
    }
    .sop-banner-final h2, .sop-banner-final p, .sop-banner-final b {
        color: #FFFFFF !important;
    }

    /* CRI 조제 카드 시인성 극대화 */
    .cri-premium-box {
        background-color: #F8FAFC !important;
        border: 2px solid #E2E8F0 !important;
        border-left: 15px solid #10B981 !important;
        padding: 40px;
        border-radius: 20px;
    }
    .val-speed-v30 { font-size: 58px !important; font-weight: 900 !important; color: #059669 !important; }
    .val-recipe-v30 { font-size: 38px !important; font-weight: 800 !important; color: #1E3A8A !important; }

    /* CPCR 로직 카드 */
    .csu-card-v30 {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .logic-tag {
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 4px;
        margin: 0 5px;
    }
    .tag-or { background-color: #FEE2E2; color: #DC2626 !important; }
    .tag-and { background-color: #DBEAFE; color: #2563EB !important; }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 로얄 표준 데이터베이스] ---
STOCK = {
    "Epinephrine": 1.0, "Atropine": 0.5, "Vasopressin": 20.0, "Lidocaine": 20.0, "Amiodarone": 50.0,
    "Naloxone": 0.4, "Flumazenil": 0.1, "Atipamezole": 5.0, "Butorphanol": 2.0, "Midazolam": 1.0, 
    "Diazepam": 5.0, "Dexmedetomidine": 0.118, "Dopamine": 32.96, "Dobutamine": 50.0, 
    "Furosemide": 10.0, "Insulin(RI)": 1.0, "KCl": 2.0, "Calcium Gluconate": 100.0, "Sodium Bicarbonate": 1.0
}

AMINO_ACID_DB = {
    "후라바솔 10% (고용량)": {"conc": 10.0, "kcal_per_ml": 0.4},
    "후라바소레-페파 6.5% (간질환용)": {"conc": 6.5, "kcal_per_ml": 0.26},
    "네프리솔 5.6% (신장질환용)": {"conc": 5.6, "kcal_per_ml": 0.224}
}

DISEASE_FACTORS = {
    "기본/비만": {"성장기": 2.0, "중성화 완료": 1.2, "미중성화": 1.4, "비만감량": 0.8},
    "신장(CKD)/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전": 1.05},
    "췌장/간/소화기": {"췌장염 안정": 1.1, "간질환 안정": 1.15, "지방간(HL)": 1.35, "EPI": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

DIET_DB = {
    "Royal Canin": {"Recovery": 105, "GI (Dry)": 3912, "GI Low Fat (Wet)": 385, "Urinary S/O": 3884, "Renal": 3988},
    "Hill's": {"a/d": 183, "i/d Digestive": 3663, "i/d Low Fat Wet": 341, "k/d Kidney": 4220}
}

# --- [3. 사이드바 - 환자 데이터 입력] ---
with st.sidebar:
    st.markdown("# 📋 Patient Profile")
    species = st.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
    weight = st.number_input("체중 (kg)", 0.1, 150.0, 3.1, 0.1, format="%.1f")
    st.markdown("---")
    cat_n = st.selectbox("질환 카테고리", list(DISEASE_FACTORS.keys()))
    sub_cat = st.selectbox("세부 상태", list(DISEASE_FACTORS[cat_n].keys()))
    st.markdown("---")
    st.caption("Protocol Architect")
    st.markdown("### **Dr. Jaehee Lee**")

# --- [4. 메인 타이틀] ---
st.title("🛡️ RAMC Advanced Clinical Intelligence System")
st.markdown("#### 로얄동물메디컬센터 고도의 임상 의사결정 지원 시스템")

tabs = st.tabs(["🚨 CPCR (CSU)", "🧪 전해질/삼투압", "💉 CRI 조제", "💧 수액 & 아미노산", "🍽️ 영양 관리", "🩸 수혈"])

# --- TAB 1: CPCR (시계형 컴팩트 메트로놈) ---
with tabs[0]:
    st.subheader(f"🚨 CPCR Protocol for {weight:.1f}kg patient")
    
    col_met, col_rev = st.columns([1, 2.5])
    with col_met:
        bpm_val = st.radio("Compression Rate", [90, 120], horizontal=True)
        met_html = f"""
        <div style="text-align:center; background:#1E293B; padding:15px; border-radius:15px; color:white;">
            <div id="c" style="width:60px; height:60px; border-radius:50%; border:4px solid #374151; margin:0 auto 10px; position:relative; display:flex; align-items:center; justify-content:center;">
                <div id="p" style="width:0%; height:0%; background:#10B981; border-radius:50%; position:absolute; opacity:0.5;"></div>
                <b style="font-size:16px; color:white !important;">{bpm_val}</b>
            </div>
            <button id="b" style="width:100%; padding:8px; font-weight:900; background:#10B981; color:white; border:none; border-radius:5px; cursor:pointer;">START</button>
        </div>
        <script>
            let ctx=null, tid=null, n=0, play=false; const btn=document.getElementById('b'), pulse=document.getElementById('p');
            function t(){{ while(n<ctx.currentTime+0.1){{ const o=ctx.createOscillator(), g=ctx.createGain(); o.connect(g); g.connect(ctx.destination); o.frequency.value=880; g.gain.value=0.03; o.start(n); o.stop(n+0.05);
                setTimeout(()=>{{ pulse.style.width='100%'; pulse.style.height='100%'; pulse.style.opacity='0.5'; setTimeout(()=>{{ pulse.style.width='0%'; pulse.style.height='0%'; pulse.style.opacity='0'; }}, 100); }}, (n-ctx.currentTime)*1000); n+=60/{bpm_val}; }} tid=setTimeout(t,25); }}
            btn.onclick=()=>{{ if(!ctx)ctx=new (window.AudioContext||window.webkitAudioContext)(); if(play){{clearInterval(tid); tid=null; btn.innerText='START'; btn.style.background='#10B981';}} else{{n=ctx.currentTime; t(); btn.innerText='STOP'; btn.style.background='#EF4444';}} play=!play; }};
        </script>
        """
        components.html(met_html, height=160)
    with col_rev:
        st.markdown(f"""<div style="background-color:#F8FAFC; border:1px solid #CBD5E1; border-radius:10px; padding:20px;">
        <b style="font-size:18px;">Reversals:</b><br>Naloxone {(weight*0.04/0.4):.2f}ml | Flumazenil {(weight*0.01/0.1):.2f}ml | Atipamezole {(weight*0.1/5.0):.2f}ml</div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="csu-card-v30"><b>1. VF / Pulseless VT</b><br><br>
        <b>Defibrillation:</b> Ext {weight*4:.1f}-{weight*6:.1f}J | Int {weight*0.5:.1f}-{weight*1J}<br>
        - Epi(L): {(weight*0.01):.2f} ml IV <span class="logic-tag tag-or">OR</span> Vaso: {(weight*0.8/20):.2f} ml IV<br>
        - Amiodarone: {(weight*5/50):.2f} ml IV <span class="logic-tag tag-and">AND</span> (Lidocaine Dog: {(weight*2/20):.2f}ml)</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="csu-card-v30"><b>2. Asystole / PEA</b><br><br>
        - Epi(L): {(weight*0.01):.2f} ml IV (Every other cycle)<br>
        - Vasopressin: {(weight*0.8/20):.2f} ml IV (One-time)<br>
        - Atropine: {(weight*0.04/0.5):.2f} ml IV (AND)<br>
        <b>Intratracheal:</b> Epi {(weight*0.02):.2f}ml | Atropine {(weight*0.16):.2f}ml</div>""", unsafe_allow_html=True)

# --- TAB 2: 전해질/삼투압 ---
with tabs[1]:
    st.header("🧪 Electrolyte & Osmolality Intelligence")
    e1, e2, e3 = st.columns(3)
    with e1:
        na = st.number_input("Measured Na+", 100.0, 200.0, 145.0, 0.1)
        glu = st.number_input("Measured Glucose", 10.0, 1000.0, 100.0, 1.0)
        bun = st.number_input("Measured BUN", 5.0, 300.0, 20.0, 1.0)
        k_in = st.number_input("Measured K+", 1.0, 10.0, 4.0, 0.1)
        bag_v = st.selectbox("Fluid Bag (mL)", [30, 50, 100, 250, 500, 1000], index=5)
    with e2:
        c_na = na + 1.6*((glu-100)/100) if glu > 100 else na
        osmo = 2*(na+k_in) + (glu/18) + (bun/2.8)
        st.markdown(f"""<div class="csu-card-v30"><b>Corrected Na+:</b><br><span style="font-size:32px; font-weight:900; color:#DC2626 !important;">{c_na:.1f} mEq/L</span></div>
        <div class="csu-card-v30"><b>Osmolality:</b><br><span style="font-size:32px; font-weight:900; color:#2563EB !important;">{osmo:.1f} mOsm/kg</span></div>""", unsafe_allow_html=True)
    with e3:
        kt = next((v for kr, v in {2.0:80, 2.5:60, 3.0:40, 3.5:28}.items() if k_in <= kr), 10)
        st.markdown(f"""<div class="csu-card-v30" style="border-left:8px solid #3B82F6 !important;">
        <b>KCl (2mEq/ml) Additive:</b><br><span style="font-size:32px; font-weight:900; color:#1E3A8A !important;">Add {(kt*bag_v/1000)/2.0:.1f} mL</span><br>
        <p>Target: {kt}mEq/L (in {bag_v}ml)</p></div>""", unsafe_allow_html=True)

# --- TAB 3: CRI 조제 (Error Fixed) ---
with tabs[2]:
    st.header("💉 High-Visibility CRI Protocol")
    dr_sel = st.selectbox("CRI 약물 선택", ["Butorphanol", "Midazolam", "Dexmedetomidine", "Epinephrine", "Norepinephrine", "Dopamine", "Furosemide", "Insulin(RI)"])
    cr1, cr2 = st.columns([1, 2])
    with cr1:
        ir_v = st.number_input("설정 속도 (mL/h)", 0.1, 100.0, 0.5, 0.1)
        td_v = st.number_input("목표 용량 (mpk/h or mcg/kg/min)", 0.0, 50.0, 0.1, 0.01, format="%.3f")
        sv_v = st.selectbox("시린지 용량", [10, 20, 50], index=2)
    with cr2:
        # [FIXED] dr_sel 변수 일치 확인
        mgh = (td_v*weight*60/1000) if dr_sel in ["Epinephrine", "Norepinephrine", "Dopamine"] else (td_v*weight)
        dml = (mgh / STOCK[dr_sel]) * sv_v / ir_v
        st.markdown(f"""<div class="cri-premium-box">
            <span class="text-label">🚩 {dr_sel} 설정 속도</span><br><span class="val-speed-v30">{ir_v:.1f} mL/h</span><br><br>
            <span class="text-label">🧪 조제 레시피 (총 {sv_v}mL)</span><br><span class="val-recipe-v30">원액 {dml:.2f} mL + 희석액 {(sv_v-dml):.2f} mL</span>
        </div>""", unsafe_allow_html=True)

# --- TAB 4: 수액 & 아미노산 ---
with tabs[3]:
    st.markdown("""<div class="sop-banner-final"><h2>RER = BW × 50 kcal/day</h2><p>💡 표준 유지 범위: 40-60 mL/kg/day (시간당 약 2-3 mL/kg)</p></div>""", unsafe_allow_html=True)
    f1, f2 = st.columns([1.2, 1])
    with f1:
        st.subheader("💧 수액 속도 (Dry Mode)")
        total_fluid = (weight * st.slider("유지 (mL/kg/hr)", 1.0, 4.0, 2.0)) + (st.number_input("지속 손실 (mL/day)", value=float(round(weight*1.0, 1))) / 24)
        st.metric("최종 수액 속도", f"{total_fluid:.1f} mL/h")
    with f2:
        st.subheader("🧬 아미노산 공급 기준")
        aa_sel = st.selectbox("제제 선택", list(AMINO_ACID_DATA.keys()))
        aa_ml = (1.0 / AMINO_ACID_DATA[aa_sel]['conc']) * 100
        st.markdown(f"""<div style="background-color:#F0FDF4; padding:25px; border-radius:12px; border:2px solid #22C55E;">
        <b style="font-size:20px; color:#166534 !important;">{aa_sel}</b><br>
        <span style="font-size:34px; font-weight:900; color:#15803D !important;">{aa_ml:.1f} mL / 100 kcal</span><br>
        <p style="color:#166534 !important;">(단백질 1g/100kcal 충족 시 필요량)</p></div>""", unsafe_allow_html=True)

# --- TAB 5: 영양 관리 ---
with tabs[4]:
    st.markdown('<div class="sop-banner-final"><h2>Royal Nutrition Protocol</h2></div>', unsafe_allow_html=True)
    n1, n2 = st.columns(2)
    with n1:
        der = (weight * 50) * DISEASE_FACTORS[cat_n][sub_cat] * (1.1 if st.checkbox("입원 가중치", value=True) else 1.0)
        s_m = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        st_sel = st.radio("전략 선택", ["3단계", "4단계", "5단계"], horizontal=True)
        cs = st.select_slider("현재 단계", options=s_m[st_sel], value=s_m[st_sel][-1])
        st.metric("목표 DER", f"{der*cs:.0f} kcal")
    with n2:
        prod = st.selectbox("사료 선택", list(DIET_DB["Royal Canin"].keys()) + list(DIET_DB["Hill's"].keys()))
        kcal_v = {**DIET_DB["Royal Canin"], **DIET_DB["Hill's"]}[prod]
        amt = ((der*cs)/kcal_v) * (1 if "Recovery" in prod or "a/d" in prod else 1000)
        st.success(f"### 급여량: **{amt:.1f} {'can' if 'Recovery' in prod or 'a/d' in prod else 'g'}**")

# --- TAB 6: 수혈 ---
with tabs[5]:
    st.header("🩸 Blood Transfusion Calculator")
    tx1, tx2 = st.columns([1, 1.5])
    with tx1:
        cp = st.number_input("현재 PCV", 1.0, 50.0, 15.0); tp = st.number_input("목표 PCV", 1.0, 50.0, 25.0)
        pr = st.radio("제제", ["전혈", "pRBC"], horizontal=True)
        kv = 90 if species == "개(Canine)" else 60
        txv = weight * kv * ((tp - cp) / (40.0 if pr == "전혈" else 70.0))
        st.metric("수혈 필요량", f"{max(0.0, round(txv, 1))} mL")
    with tx2:
        st.info("**[수혈 지침]** 1. 일반 환자 4시간 원칙. 2. 심장/신장 환자 12-24시간 연장 가능 (분할 투여 권장).")

st.divider()
st.caption(f"Royal Animal Medical Center | v30.0 | Clinical Intelligence by Dr. Jaehee Lee")
