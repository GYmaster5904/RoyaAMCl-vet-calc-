import streamlit as st
import streamlit.components.v1 as components

# --- [1. 디자인 및 시인성 프로토콜 CSS] ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc v25.0", layout="wide")

st.markdown("""
    <style>
    /* 배경 및 기본 텍스트 강제 고정 (다크모드 시인성 해결) */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #FDFDFD !important;
        color: #0F172A !important;
    }
    
    /* 모든 위젯 텍스트 및 라벨 검은색 고정 */
    .stMarkdown, p, span, label, .stSelectbox, .stNumberInput, div {
        color: #0F172A !important;
    }
    
    /* 대형 알림 배너 스타일 */
    .sop-header-banner {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        padding: 20px;
        border-radius: 12px;
        border-left: 10px solid #EF4444;
        margin-bottom: 20px;
    }
    .sop-header-banner h2, .sop-header-banner p { color: #FFFFFF !important; }

    /* CPCR 로직 카드 스타일 */
    .csu-logic-card {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .logic-tag-or { background-color: #FEE2E2; color: #B91C1C !important; padding: 2px 10px; border-radius: 4px; font-weight: 800; font-size: 14px; }
    .logic-tag-and { background-color: #DBEAFE; color: #1E40AF !important; padding: 2px 10px; border-radius: 4px; font-weight: 800; font-size: 14px; }

    /* CRI 조제법 - 시인성 극대화 */
    .cri-display-final {
        background-color: #F8FAFC !important;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #D1D5DB;
        border-left: 12px solid #10B981;
    }
    .text-speed { font-size: 48px !important; font-weight: 900; color: #059669 !important; }
    .text-recipe { font-size: 34px !important; font-weight: 800; color: #1E3A8A !important; }
    .text-label { font-size: 20px; color: #475569 !important; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 로얄 표준 데이터베이스] ---
STOCK = {
    "Epinephrine": 1.0, "Atropine": 0.5, "Vasopressin": 20.0, "Lidocaine": 20.0, "Amiodarone": 50.0,
    "Naloxone": 0.4, "Flumazenil": 0.1, "Atipamezole": 5.0, "Butorphanol": 2.0, "Midazolam": 1.0, 
    "Diazepam": 5.0, "Dexmedetomidine": 0.118, "Dopamine": 32.96, "Dobutamine": 50.0, 
    "Furosemide": 10.0, "Insulin(RI)": 1.0, "KCl": 2.0, "Calcium Gluconate": 100.0, "Sodium Bicarbonate": 1.0
}

DISEASE_FACTORS = {
    "기본/비만": {"성장기": 2.0, "중성화 완료": 1.2, "미중성화": 1.4, "비만감량": 0.8, "저활동": 1.0},
    "신장/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전": 1.05},
    "췌장/간/소화기": {"췌장염 안정": 1.1, "간질환 안정": 1.15, "지방간(HL)": 1.35, "EPI": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

DIET_LIST = {
    "Royal Canin": {"Recovery": 105, "GI (Dry)": 3912, "GI Low Fat (Wet)": 385, "Urinary S/O": 3884, "Renal": 3988},
    "Hill's": {"a/d": 183, "i/d Digestive": 3663, "i/d Low Fat Wet": 341, "k/d Kidney": 4220}
}

# --- [3. 사이드바 - 환자 고정 데이터] ---
with st.sidebar:
    st.header("🐾 Patient Profile")
    species = st.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
    weight = st.number_input("체중 (kg)", 0.1, 150.0, 3.1, 0.1, format="%.1f")
    st.markdown("---")
    cat_n = st.selectbox("질환 카테고리", list(DISEASE_FACTORS.keys()))
    sub_cat = st.selectbox("세부 상태", list(DISEASE_FACTORS[cat_n].keys()))
    st.markdown("---")
    st.caption("Protocol Architect")
    st.markdown("### **Dr. Jaehee Lee**")

# --- [4. 메인 탭 구성] ---
tabs = st.tabs(["🚨 CPCR (CSU)", "🧪 전해질/삼투압", "💉 CRI 조제", "💧 수액 요법", "🍴 영양 관리", "🩸 수혈"])

# --- TAB 1: CPCR (컴팩트 메트로놈 & 정밀 논리) ---
with tabs[0]:
    st.subheader(f"🚨 CPCR Protocol for {weight:.1f}kg")
    
    col_c1, col_c2 = st.columns([1, 2])
    with col_c1:
        bpm = st.radio("Compression Rate (BPM)", [90, 120], horizontal=True)
        metronome_html = f"""
        <div style="background:#1E293B; padding:15px; border-radius:10px; text-align:center;">
            <button id="mB" style="width:100%; padding:12px; font-weight:900; background:#10B981; color:white; border:none; border-radius:5px; cursor:pointer; font-size:18px;">START {bpm} BPM</button>
        </div>
        <script>
            let c=null, i=null, n=0, p=false; const b=document.getElementById('mB');
            function t(){{ while(n<c.currentTime+0.1){{ const o=c.createOscillator(), g=c.createGain(); o.connect(g); g.connect(c.destination); o.frequency.value=880; g.gain.value=0.04; o.start(n); o.stop(n+0.05); n+=60/{bpm}; }} i=setTimeout(t,25); }}
            b.onclick=()=>{{ if(!c)c=new(window.AudioContext||window.webkitAudioContext)(); if(p){{clearInterval(i); i=null; b.innerText='START {bpm} BPM'; b.style.background='#10B981';}} else{{n=c.currentTime; t(); b.innerText='STOP'; b.style.background='#EF4444';}} p=!p; }};
        </script>
        """
        components.html(metronome_html, height=100)
    
    with col_c2:
        st.markdown(f"""<div style="background-color:#F1F5F9; padding:15px; border-radius:10px; border:1px solid #CBD5E1;">
        <b>Reversals:</b> Naloxone {(weight*0.04/0.4):.2f}ml | Flumazenil {(weight*0.01/0.1):.2f}ml | Atipamezole {(weight*0.1/5.0):.2f}ml</div>""", unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="csu-logic-card"><b>1. VF / Pulseless VT</b>', unsafe_allow_html=True)
        st.write(f"**Defibrillation:** Ext **{weight*4:.1f}-{weight*6:.1f}J** | Int {weight*0.5:.1f}-{weight*1J}")
        st.write(f"- Epinephrine(L): **{(weight*0.01):.2f} ml** <span class='logic-tag-or'>OR</span> Vasopressin: **{(weight*0.8/20):.2f} ml**")
        st.write(f"- Amiodarone: **{(weight*5/50):.2f} ml** <span class='logic-tag-and'>AND</span> (Lidocaine Dog: **{(weight*2/20):.2f}ml**)")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="csu-logic-card"><b>2. Asystole / PEA</b>', unsafe_allow_html=True)
        st.write(f"- Epinephrine(L): **{(weight*0.01):.2f} ml** (격주 사이클)")
        st.write(f"- Vasopressin: **{(weight*0.8/20):.2f} ml** <span class='logic-tag-or'>OR</span> (1회 한정)")
        st.write(f"- Atropine: **{(weight*0.04/0.5):.2f} ml** <span class='logic-tag-and'>AND</span> (격주 사이클)")
        st.write(f"**Intratracheal:** Epi {(weight*0.02):.2f}ml | Atropine {(weight*0.16):.2f}ml")
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: 전해질/삼투압 (소량 백 옵션) ---
with tabs[1]:
    st.header("🧪 Electrolyte & Osmolality Evaluation")
    e1, e2, e3 = st.columns(3)
    with e1:
        st.subheader("검사 수치")
        na = st.number_input("Na+", 100.0, 200.0, 145.0, 0.1); glu = st.number_input("Glucose", 10.0, 1000.0, 100.0, 1.0)
        bun = st.number_input("BUN", 5.0, 300.0, 20.0, 1.0); k_in = st.number_input("K+", 1.0, 10.0, 4.0, 0.1)
        bag_v = st.selectbox("수액 백 용량 (mL)", [30, 50, 100, 250, 500, 1000], index=4)
    with e2:
        st.subheader("종합 평가")
        c_na = na + 1.6*((glu-100)/100) if glu > 100 else na
        osmo = 2*(na+k_in) + (glu/18) + (bun/2.8)
        st.markdown(f"""<div class="csu-logic-card"><b>Corrected Na+:</b><br><span style="font-size:28px; font-weight:900; color:#DC2626;">{c_na:.1f} mEq/L</span></div>
        <div class="csu-logic-card"><b>Osmolality:</b><br><span style="font-size:28px; font-weight:900; color:#2563EB;">{osmo:.1f} mOsm/kg</span></div>""", unsafe_allow_html=True)
    with e3:
        st.subheader("조제 레시피")
        kt = next((v for kr, v in {2.0:80, 2.5:60, 3.0:40, 3.5:28}.items() if k_in <= kr), 10)
        st.markdown(f"""<div class="csu-logic-card" style="border-left:8px solid #3B82F6;">
        <b>KCl (2mEq/ml) 첨가량:</b><br><span style="font-size:32px; font-weight:900; color:#1E3A8A;">Add {(kt*bag_v/1000)/2.0:.1f} ml</span><br>
        <p>목표: {kt}mEq/L (In {bag_v}ml Bag)</p></div>""", unsafe_allow_html=True)

# --- TAB 3: CRI 조제 (최강 시인성) ---
with tabs[2]:
    st.header("💉 CRI High-Visibility Protocol")
    dr_c = st.selectbox("약물", ["Butorphanol", "Midazolam", "Dexmedetomidine", "Epinephrine", "Norepinephrine", "Dopamine", "Furosemide", "Insulin(RI)"])
    cr1, cr2 = st.columns([1, 2])
    with cr1:
        ir_v = st.number_input("설정 속도 (mL/h)", 0.1, 100.0, 0.5, 0.1)
        td_v = st.number_input("목표 용량 (mg/kg/h or mcg/kg/min)", 0.0, 50.0, 0.1, 0.01, format="%.3f")
        sv_v = st.selectbox("시린지 용량", [10, 20, 50], index=2)
    with cr2:
        mgh = (td_v*weight*60/1000) if dr_c in ["Epinephrine", "Norepinephrine", "Dopamine"] else (td_v*weight)
        dml = (mgh / STOCK[dr_c]) * sv_v / ir_v
        st.markdown(f"""<div class="cri-display-final">
            <span class="text-label">🚩 {dr_c} 설정 속도</span><br><span class="text-speed">{ir_v:.1f} mL/h</span><br><br>
            <span class="text-label">🧪 조제법 (총 {sv_v}mL)</span><br><span class="text-recipe">원액 {dml:.2f} mL + 희석액 {(sv_v-dml):.2f} mL</span>
        </div>""", unsafe_allow_html=True)

# --- TAB 4: 수액 요법 (BWx50 공지) ---
with tabs[3]:
    st.markdown("""<div class="sop-header-banner">
        <h2>RER = BW × 50 kcal/day</h2>
        <p>💡 <b>표준 유지 범위:</b> 40-60 mL/kg/day (시간당 약 2-3 mL/kg)</p></div>""", unsafe_allow_html=True)
    f1, f2 = st.columns([1.5, 1])
    with f1:
        ms = st.radio("상황", ["로얄 Dry Mode (입원)", "AAHA 2024 마취"], horizontal=True)
        if "Dry" in ms:
            mr = st.slider("유지 (mL/kg/hr)", 1.0, 4.0, 2.0, 0.5)
            dy = st.number_input("탈수 (%)", 0, 15, 0)
            lo = st.number_input("지속 손실 (mL/day)", value=float(round(weight*1.0, 1)), step=0.1)
            st.metric("권장 수액 속도", f"{(weight*mr)+(lo/24):.1f} mL/h")
        else: st.metric("마취 수액 속도 (AAHA)", f"{(weight*5 if species=='개(Canine)' else weight*3):.1f} mL/h")
    with f2:
        if "심장" in sub_cat: st.error("심장 질환: 수액 과부하 주의. RR 모니터링 필수.")

# --- TAB 5: 영양 관리 ---
with tabs[4]:
    st.markdown('<div class="sop-header-banner"><h2>Royal Nutrition Protocol (3/4/5 Stages)</h2></div>', unsafe_allow_html=True)
    n1, n2 = st.columns(2)
    with n1:
        der = (weight * 50) * DISEASE_FACTORS[cat_n][sub_cat] * (1.1 if st.checkbox("입원 가중치", value=True) else 1.0)
        s_m = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        st_sel = st.radio("전략", list(s_m.keys()), horizontal=True)
        cs = st.select_slider("단계", options=s_m[st_sel], value=s_m[st_sel][-1])
        st.metric("목표 DER", f"{der*cs:.0f} kcal")
    with n2:
        prod = st.selectbox("사료 선택", list(DIET_LIST["Royal Canin"].keys()) + list(DIET_LIST["Hill's"].keys()))
        kcal_v = {**DIET_LIST["Royal Canin"], **DIET_LIST["Hill's"]}[prod]
        amt = ((der*cs)/kcal_v) * (1 if "Recovery" in prod or "a/d" in prod else 1000)
        st.success(f"### 급여 권장량: **{amt:.1f} {'can' if 'Recovery' in prod or 'a/d' in prod else 'g'}**")

# --- TAB 6: 수혈 (SOP 및 근거 업데이트) ---
with tabs[5]:
    st.header("🩸 Blood Transfusion Calculator")
    tx1, tx2 = st.columns([1, 1.5])
    with tx1:
        cp = st.number_input("현재 PCV", 1.0, 50.0, 15.0); tp = st.number_input("목표 PCV", 1.0, 50.0, 25.0)
        pr = st.radio("제제 선택", ["전혈", "pRBC"], horizontal=True)
        tx_v = weight * (90 if species == "개(Canine)" else 60) * ((tp - cp) / (40.0 if pr == "전혈" else 70.0))
        st.metric("수혈 필요량", f"{max(0.0, round(tx_v, 1))} mL")
    with tx2:
        st.info("""
        **[수혈 관리 표준 SOP 및 근거]**
        1. **기본 원칙:** 세균 증식 방지를 위해 **4시간 이내** 투여 완료 권장.
        2. **연장 투여 (Evidence):** 심장 질환 환자 등 볼륨 부하에 취약한 경우, 모니터링 하에 **최대 6시간**까지 투여 가능함. 
           (※ 단, 상온 방치가 길어지므로 수혈백 분할 투여가 가장 안전함)
        3. **초기 속도:** 첫 15-30분간 0.25-0.5 ml/kg/hr로 시작하여 부작용 감시.
        4. **전용 세트:** 필터(170-260μm) 포함 수혈 세트 사용 필수.
        """)

st.divider()
st.caption(f"Royal Animal Medical Center | v25.0 Final | Clinical Solution by Dr. Jaehee Lee")
