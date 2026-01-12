import streamlit as st
import streamlit.components.v1 as components

# --- [1. 페이지 설정 및 디자인 CSS 주입] ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc v16.1", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stApp { color: #1e293b; }
    
    /* 상단 공식 및 공지 배너 */
    .formula-banner {
        background-color: #1e293b; color: white; padding: 20px; border-radius: 12px; 
        border-left: 8px solid #ff4b4b; margin-bottom: 25px;
    }
    
    /* CRI 조제 카드 - 시인성 대폭 강화 (원장님 지시: 32px / 28px) */
    .cri-card {
        background-color: white; padding: 35px; border-radius: 15px; border-left: 10px solid #10b981;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); line-height: 1.6; margin-top: 20px;
    }
    .cri-label { font-size: 22px; color: #64748b; font-weight: bold; }
    .speed-value { color: #10b981; font-weight: 900; font-size: 38px; display: block; margin: 10px 0; }
    .recipe-value { color: #1e3a8a; font-weight: 800; font-size: 30px; display: block; margin-top: 10px; }
    .compat-box { background-color: #fff1f2; color: #e11d48; padding: 15px; border-radius: 8px; margin-top: 15px; font-weight: bold; font-size: 18px; }
    
    /* CPCR CSU 스타일 디자인 */
    .cpr-box { background-color: white; border: 1px solid #cbd5e1; border-radius: 10px; padding: 15px; margin-bottom: 15px; }
    .cpr-header { background-color: #334155; color: white; padding: 10px; border-radius: 6px; font-weight: bold; font-size: 20px; text-align: center; }
    .cpr-dose { font-size: 19px; font-weight: bold; color: #e11d48; }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 데이터베이스: 사료, 약물, 호환성] ---
DIET_DATA = {
    "Royal Canin (Prescription)": {
        "Recovery (Wet, 100g)": 105, "GI (Dry)": 3912, "GI (Wet, 400g)": 432, "GI High Calorie (Dry)": 4085,
        "GI Low Fat (Dry)": 3461, "GI Low Fat (Wet, 410g)": 385, "GI Puppy (Dry)": 4143, "GI Puppy (Wet, 195g)": 205,
        "Urinary S/O (Dry)": 3884, "Urinary S/O (Wet, 100g)": 85, "Renal (Dry)": 3988, "Renal (Wet, 100g)": 110,
        "Hepatic (Dry)": 3906, "Hepatic (Wet, 420g)": 584, "Hypoallergenic (Dry)": 3880, "Cardiac (Dry)": 3926
    },
    "Hill's (Prescription Diet)": {
        "a/d Urgent Care (Wet, 156g)": 183, "i/d Digestive Care (Dry)": 3663, "i/d (Wet, 156g)": 155,
        "i/d Low Fat (Dry)": 3316, "i/d Low Fat (Wet, 370g)": 341, "k/d Kidney Care (Dry)": 4220,
        "k/d (Wet, 156g)": 161, "c/d Multicare (Dry)": 3873, "z/d Food Sensitivities (Dry)": 3619
    }
}

STOCK_CONC = {
    "Epinephrine": 1.0, "Atropine": 0.5, "Vasopressin": 20.0, "Lidocaine": 20.0, "Amiodarone": 50.0, "Esmolol": 10.0,
    "Naloxone": 0.4, "Flumazenil": 0.1, "Atipamezole": 5.0, "Butorphanol": 2.0, "Midazolam": 1.0, "Diazepam": 5.0,
    "Dexmedetomidine": 0.118, "Dopamine": 32.96, "Dobutamine": 50.0, "Calcium Gluconate": 100.0, "KP": 3.0,
    "Mg-Sulfate": 500.0, "Mg-Chloride": 200.0, "Insulin(RI)": 1.0, "Furosemide": 10.0, "Sodium Bicarbonate": 1.0
}

DRUG_COMPAT = {
    "Calcium Gluconate": "LRS(결정화), Bicarb와 절대 혼합 금지. 단독 라인 권장.",
    "Sodium Bicarbonate": "Calcium 함유 수액 금지. 대부분의 카테콜아민과 배합 시 불활성화.",
    "Epinephrine": "알칼리성 용액에서 파괴됨. 5% DW 희석 시 안정성 높음.",
    "Norepinephrine": "산화 방지를 위해 5% DW 필수 사용. LRS 금지.",
    "Diazepam": "플라스틱 흡착 심함. 희석하지 말고 원액 단독 투여 권장.",
    "Amiodarone": "NS와 혼합 시 침전. 반드시 5% DW만 사용.",
    "KP": "Ca, Mg와 혼합 시 즉시 침전 발생 주의."
}

DISEASE_FACTORS = {
    "기본/비만": {"성장기(2-12m)": 2.0, "중성화 성견/성묘": 1.2, "미중성화": 1.4, "비만감량": 0.8, "저활동": 1.0},
    "신장/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전/이뇨제사용": 1.05},
    "췌장/간/소화기": {"췌장염 안정": 1.1, "간질환 안정기": 1.15, "고양이 지방간(HL)": 1.35, "EPI(췌장부전)": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

# --- [3. 사이드바: 환자 정보 (소수점 1자리 적용)] ---
with st.sidebar:
    st.header("📋 Patient Info")
    species = st.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
    weight = st.number_input("체중 (kg)", 0.1, 150.0, 3.1, 0.1, format="%.1f")
    st.markdown("---")
    cat_n = st.selectbox("질환 카테고리", list(DISEASE_FACTORS.keys()))
    sub_cat = st.selectbox("세부 상태", list(DISEASE_FACTORS[cat_n].keys()))
    st.markdown("---")
    st.caption("Clinical Protocol Architect")
    st.markdown(f"### **Dr. Jaehee Lee**")

# --- [4. 메인 탭 구성] ---
tabs = st.tabs(["🚨 CPCR (CSU)", "🧪 전해질 교정", "💉 CRI 조제", "💧 수액 요법", "🍴 영양 관리", "🩸 수혈"])

# --- TAB 1: CPCR (CSU Style + Metronome) ---
with tabs[0]:
    st.markdown(f"### 🚨 CPCR Protocol for {weight:.1f}kg patient")
    bpm = st.slider("압박 속도 (BPM)", 80, 140, 120)
    metronome_html = f"""
    <div style="display: flex; align-items: center; gap: 20px; background: #1e293b; padding: 15px; border-radius: 10px; color: white;">
        <button id="pB" style="padding: 10px 25px; font-weight: bold; cursor: pointer; background: #10b981; color: white; border-radius:5px; border:none;">▶ START</button>
        <div id="ht" style="font-size: 30px;">❤️</div> <div>{bpm} BPM</div>
    </div>
    <script>
        const b=document.getElementById('pB'), h=document.getElementById('ht'); let c=null, p=false, i=null;
        function s(){{ if(!c)c=new(window.AudioContext||window.webkitAudioContext)(); const o=c.createOscillator(), g=c.createGain(); o.type='sine'; o.frequency.setValueAtTime(880, c.currentTime); g.gain.setValueAtTime(0.1, c.currentTime); g.gain.exponentialRampToValueAtTime(0.001, c.currentTime+0.1); o.connect(g); g.connect(c.destination); o.start(); o.stop(c.currentTime+0.1); h.style.transform='scale(1.5)'; setTimeout(()=>h.style.transform='scale(1)', 100); }}
        b.onclick=()=>{{ if(p){{clearInterval(i); b.innerText='▶ START'; b.style.background='#10b981';}} else{{i=setInterval(s,(60/{bpm})*1000); b.innerText='■ STOP'; b.style.background='#ef4444';}} p=!p; }};
    </script>
    """
    components.html(metronome_html, height=100)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="cpr-header">VF / VT</div>', unsafe_allow_html=True)
        st.write("**Defibrillation**")
        st.error(f"External: {weight*2:.1f}-{weight*4:.1f} J")
        st.write(f"Internal: {weight*0.5:.1f}-{weight*1.0:.1f} J")
        st.write(f"Epinephrine (L): {(weight*0.01):.2f} ml")
        st.write(f"Amiodarone: {(weight*5/50):.2f} ml")
    with c2:
        st.markdown('<div class="cpr-header">Asystole / PEA</div>', unsafe_allow_html=True)
        st.write("**Every other 2m cycle**")
        st.error(f"Epinephrine (L): {(weight*0.01):.2f} ml")
        st.write(f"Vasopressin: {(weight*0.8/20):.2f} ml (1x)")
        st.write(f"Atropine: {(weight*0.04/0.5):.2f} ml")
    with c3:
        st.markdown('<div class="cpr-header">IT Doses (2x)</div>', unsafe_allow_html=True)
        st.info(f"Epi: {(weight*0.01*2):.2f} ml")
        st.info(f"Atropine: {(weight*0.04*2/0.5):.2f} ml")
        st.info(f"Lidocaine: {(weight*2*2/20):.2f} ml")

# --- TAB 2: 전해질 교정 ---
with tabs[1]:
    st.header("🧪 전해질 불균형 교정")
    e1, e2 = st.columns(2)
    with e1:
        cur_na = st.number_input("Na+ (mEq/L)", 100.0, 200.0, 145.0)
        cur_hco3 = st.number_input("HCO3- (mEq/L)", 5.0, 40.0, 20.0)
        cur_k = st.number_input("K+ (mEq/L)", 1.0, 10.0, 4.0)
    with e2:
        if cur_na > 155: st.error(f"**Free Water Deficit:** {0.6*weight*((cur_na/145)-1):.2f} L")
        if cur_hco3 < 18: st.info(f"**Bicarb Deficit:** {0.3*weight*(22-cur_hco3):.1f} mEq")
        k_rec = next((v for kr, v in {3.5:20, 3.0:40, 2.5:60, 2.0:80}.items() if cur_k <= kr), 0)
        st.success(f"**Recommended K+ Supplement:** {k_rec} mEq/L")

# --- TAB 3: CRI 조제 (원장님 지시: 시인성 극대화) ---
with tabs[2]:
    st.header("💉 CRI 조제 및 호환성")
    dr = st.selectbox("약물 선택", list(STOCK_CONC.keys()))
    cr1, cr2 = st.columns([1, 2])
    with cr1:
        ir = st.number_input("펌프 속도 (mL/h)", 0.1, 100.0, 0.5, 0.1)
        td = st.number_input("목표 용량 (mg/kg/h or mcg/kg/min)", 0.0, 50.0, 0.1, 0.01, format="%.3f")
        sv = st.selectbox("시린지 볼륨 (mL)", [10, 20, 50], index=2)
    with cr2:
        is_mcg = dr in ["Epinephrine", "Norepinephrine", "Dopamine", "Dobutamine"]
        mgh = (td * weight * 60 / 1000) if is_mcg else (td * weight)
        dml = (mgh / STOCK_CONC[dr]) * sv / ir
        st.markdown(f"""
        <div class="cri-card">
            <span class="cri-label">{dr} 조제 레시피</span>
            <span class="speed-value">설정 속도: {ir:.1f} mL/h</span>
            <span class="recipe-value">원액 {dml:.2f} mL + 희석액 {(sv-dml):.2f} mL</span>
            <div class="compat-box">⚠️ {DRUG_COMPAT.get(dr, "타 약물 배합 전 호환성 차트 확인 필수")}</div>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 4: 수액 요법 (배너 및 공지 포함) ---
with tabs[3]:
    st.markdown("""
    <div class="formula-banner">
        <p style="margin:0; font-size:18px;"><b>Royal Clinical Standard:</b></p>
        <h2 style="margin:0; color:#ff4b4b;">RER = BW × 50 kcal/day</h2>
        <p style="margin:5px 0 0 0; color:#cbd5e1;">💡 성견/성묘 유지 범위: 40-60 mL/kg/day (시간당 약 2-3 mL/kg)</p>
    </div>
    """, unsafe_allow_html=True)
    f1, f2 = st.columns([1.5, 1])
    with f1:
        m = st.radio("상황 선택", ["로얄 Dry Mode (입원)", "AAHA 2024 마취"], horizontal=True)
        if "Dry" in m:
            mr = st.slider("유지 용량 (mL/kg/hr)", 1.0, 4.0, 2.0, 0.5)
            dy = st.number_input("탈수율 (%)", 0, 15, 0)
            # 지속손실 소수점 1자리 + 체중당 1ml 반영
            lo = st.number_input("지속 손실 (mL/day)", value=float(round(weight*1.0, 1)), step=0.1, format="%.1f")
            total = (weight * mr) + ((weight * dy * 10) / 12) + (lo / 24)
            st.metric("최종 수액 속도", f"{total:.1f} mL/h")
        else:
            st.metric("마취 중 속도 (AAHA 2024)", f"{(weight*5 if species=='개(Canine)' else weight*3):.1f} mL/h")
    with f2:
        st.subheader("임상 가이드")
        if "심장" in sub_cat: st.error("심장: 수액 불내성 고위험군. RR 20%↑ 시 즉시 중단.")
        elif "췌장" in sub_cat: st.error("췌장: Ongoing Loss 철저 반영 및 전해질 교정.")

# --- TAB 5: 영양 관리 (확장된 사료 DB) ---
with tabs[4]:
    st.header("🍴 영양 및 급여 관리")
    n1, n2 = st.columns(2)
    with n1:
        rer_v = weight * 50
        fv = DISEASE_FACTORS[cat_n][sub_cat]
        if st.checkbox("입원 가중치(1.1) 적용", value=True, key="nw_11"): fv *= 1.1
        der_v = rer_v * fv
        st.metric("목표 DER", f"{der_v:.0f} kcal/day")
        st_opt = st.radio("급여 전략 (Fasting 기간 고려)", ["3단계", "4단계", "5단계"], horizontal=True)
        sm = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        cs_v = st.select_slider("현재 단계", options=sm[st_opt], value=sm[st_opt][-1])
    with n2:
        br = st.selectbox("브랜드", list(DIET_DATA.keys()))
        pd = st.selectbox("제품 선택", list(DIET_DATA[br].keys()))
        kcal = DIET_DATA[br][pd]
        is_w = any(x in pd for x in ["Wet", "파우치", "100g", "156g", "400g"])
        un = "can/pouch" if is_w else "g"
        amt = ((der_v * cs_v) / kcal) * (1 if is_w else 1000)
        st.success(f"### 최종 급여량: **{amt:.1f} {un}**")

# --- TAB 6: 수혈 ---
with tabs[5]:
    st.header("🩸 Blood Transfusion")
    tx1, tx2 = st.columns(2)
    with tx1:
        pr = st.radio("제제", ["전혈", "pRBC"], horizontal=True)
        cp = st.number_input("현재 PCV (%)", 1.0, 50.0, 15.0)
        tp = st.number_input("목표 PCV (%)", 1.0, 50.0, 25.0)
        kv = 90 if species == "개(Canine)" else 60
        res = weight * kv * ((tp - cp) / (40.0 if pr == "전혈" else 70.0))
        st.metric("예상 수혈량", f"{max(0.0, round(res, 1))} mL")
    with tx2:
        st.info("초기 15-30분 0.25-0.5ml/kg/hr. 필터 포함 전용 세트 사용 및 4시간 내 완료 필수.")

st.divider()
st.caption(f"Royal Animal Medical Center | v16.1 | Protocol by Dr. Jaehee Lee")
