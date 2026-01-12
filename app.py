import streamlit as st
import streamlit.components.v1 as components

# --- [1. 디자인 및 시인성 완전 해결: 강력한 CSS 고정] ---
st.set_page_config(page_title="RAMC Advanced Clinical Intelligence", layout="wide")

st.markdown("""
    <style>
    /* [VITAL] 배경 및 모든 텍스트 색상 강제 고정 (다크모드 무시) */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], .stTabs, .stTabs [data-baseweb="tab-list"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* 모든 마크다운, 라벨, 텍스트 요소를 검은색으로 고정 */
    .stMarkdown, p, span, label, div, h1, h2, h3, h4, li, .stSelectbox p, .stNumberInput label {
        color: #000000 !important;
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif !important;
    }

    /* [CRITICAL] 선택창, 입력창 내부 블랙박스 및 시인성 해결 */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    input, select, textarea {
        background-color: #F1F5F9 !important;
        color: #000000 !important;
        border: 2px solid #1E3A8A !important;
        font-size: 20px !important;
        font-weight: 700 !important;
    }
    
    /* 드롭다운 리스트 가독성 */
    div[role="listbox"] div {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }

    /* 상단 배너 SOP 공지 스타일 */
    .sop-banner {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        padding: 30px;
        border-radius: 15px;
        border-left: 12px solid #EF4444 !important;
        margin-bottom: 25px;
    }
    .sop-banner h2, .sop-banner h3, .sop-banner p { color: #FFFFFF !important; }

    /* CRI 조제 카드 - 초대형 시인성 (원장님 요청 사항) */
    .card-cri-final {
        background-color: #F8FAFC !important;
        border: 2px solid #CBD5E1 !important;
        border-left: 20px solid #10B981 !important;
        padding: 40px;
        border-radius: 20px;
        margin-top: 20px;
    }
    .val-speed-huge { font-size: 60px !important; font-weight: 950 !important; color: #059669 !important; display: block; }
    .val-recipe-large { font-size: 40px !important; font-weight: 800 !important; color: #1E3A8A !important; display: block; }

    /* 전해질 평가 카드 */
    .eval-box {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 글로벌 데이터베이스 정의] ---
STOCK_DB = {
    "Epinephrine": 1.0, "Atropine": 0.5, "Vasopressin": 20.0, "Lidocaine": 20.0, "Amiodarone": 50.0,
    "Naloxone": 0.4, "Flumazenil": 0.1, "Atipamezole": 5.0, "Butorphanol": 2.0, "Midazolam": 1.0, 
    "Diazepam": 5.0, "Dexmedetomidine": 0.118, "Dopamine": 32.96, "Dobutamine": 50.0, 
    "Furosemide": 10.0, "Insulin(RI)": 1.0, "KCl": 2.0, "Calcium Gluconate": 100.0, "Sodium Bicarbonate": 1.0
}

AMINO_ACID_DB = {
    "후라바솔 10% (고용량 아미노산)": {"conc": 10.0},
    "후라바소레-페파 6.5% (간질환용)": {"conc": 6.5},
    "네프리솔 5.6% (신장질환용)": {"conc": 5.6}
}

DISEASE_FACTORS_DB = {
    "기본/비만": {"성장기": 2.0, "중성화 완료": 1.2, "미중성화": 1.4, "비만감량": 0.8},
    "신장(CKD)/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전": 1.05},
    "췌장/간/소화기": {"췌장염 안정": 1.1, "간질환 안정": 1.15, "지방간(HL)": 1.35, "EPI": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

DIET_DB = {
    "Royal Canin": {"Recovery": 105, "GI (Dry)": 3912, "GI Low Fat (Wet)": 385, "Urinary S/O": 3884, "Renal": 3988, "Hepatic": 3906},
    "Hill's": {"a/d": 183, "i/d Digestive": 3663, "i/d Low Fat Wet": 341, "k/d Kidney": 4220, "c/d": 3873}
}

# --- [3. 사이드바 - 고정 환자 정보 (변수명 weight_master로 고정)] ---
with st.sidebar:
    st.markdown("## 📋 Patient Profile")
    species_master = st.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
    weight_master = st.number_input("체중 (kg)", 0.1, 150.0, 3.1, 0.1, format="%.1f")
    st.markdown("---")
    cat_master = st.selectbox("질환 카테고리", list(DISEASE_FACTORS_DB.keys()))
    sub_cat_master = st.selectbox("세부 상태", list(DISEASE_FACTORS_DB[cat_master].keys()))
    st.markdown("---")
    st.caption("Protocol Architect")
    st.markdown("### **Dr. Jaehee Lee**")

# --- [4. 메인 대시보드 구조] ---
st.title("🛡️ RAMC Advanced Clinical Intelligence System")
st.markdown("#### 로얄동물메디컬센터 임상 의사결정 지원 시스템")

tabs = st.tabs(["🚨 CPCR (CSU)", "🧪 전해질/삼투압", "💉 CRI 조제", "💧 수액 & 아미노산", "🍽️ 영양 관리", "🩸 수혈"])

# --- TAB 1: CPCR ---
with tabs[0]:
    st.subheader(f"🚨 CPCR Protocol for {weight_master:.1f}kg patient")
    col_bpm, col_rev = st.columns([1, 2])
    with col_bpm:
        bpm_val = st.radio("Compression BPM", [90, 120], horizontal=True)
        met_js = f"""
        <div style="text-align:center; background:#1E293B; padding:15px; border-radius:15px; color:white;">
            <div id="gauge" style="width:60px; height:60px; border-radius:50%; border:5px solid #374151; margin:0 auto 10px; position:relative; display:flex; align-items:center; justify-content:center;">
                <div id="p" style="width:0%; height:0%; background:#10B981; border-radius:50%; position:absolute; opacity:0.5;"></div>
                <b style="font-size:18px; color:white !important;">{bpm_val}</b>
            </div>
            <button id="btn" style="width:100%; padding:8px; font-weight:900; background:#10B981; color:white; border:none; border-radius:5px; cursor:pointer;">START</button>
        </div>
        <script>
            let ctx=null, tid=null, n=0, play=false; const btn=document.getElementById('btn'), p=document.getElementById('p');
            function t(){{ while(n<ctx.currentTime+0.1){{ const o=ctx.createOscillator(), g=ctx.createGain(); o.connect(g); g.connect(ctx.destination); o.frequency.value=880; g.gain.value=0.03; o.start(n); o.stop(n+0.05);
                setTimeout(()=>{{ p.style.width='100%'; p.style.height='100%'; p.style.opacity='0.5'; setTimeout(()=>{{ p.style.width='0%'; p.style.height='0%'; p.style.opacity='0'; }}, 80); }}, (n-ctx.currentTime)*1000); n+=60/{bpm_val}; }} tid=setTimeout(t,25); }}
            btn.onclick=()=>{{ if(!ctx)ctx=new (window.AudioContext||window.webkitAudioContext)(); if(play){{clearInterval(tid); tid=null; btn.innerText='START'; btn.style.background='#10B981';}} else{{n=ctx.currentTime; t(); btn.innerText='STOP'; btn.style.background='#EF4444';}} play=!play; }};
        </script>"""
    components.html(met_js, height=160)
    
    st.markdown(f"""<div style="background-color:#F8FAFC; border:2px solid #CBD5E1; padding:20px; border-radius:12px;">
    <b>1. VF / Pulseless VT:</b> Defib Ext {weight_master*4:.1f}-{weight_master*6:.1f}J | Epi(L) {(weight_master*0.01):.2f}ml | Vaso {(weight_master*0.8/20):.2f}ml<br>
    <b>2. Asystole / PEA:</b> Epi(L) {(weight_master*0.01):.2f}ml (격주 사이클) | Atropine {(weight_master*0.04/0.5):.2f}ml (격주 사이클)<br>
    <b>3. Reversals:</b> Naloxone {(weight_master*0.04/0.4):.2f}ml | Flumazenil {(weight_master*0.01/0.1):.2f}ml | Atip {(weight_master*0.1/5.0):.2f}ml</div>""", unsafe_allow_html=True)

# --- TAB 2: 전해질/삼투압 ---
with tabs[1]:
    st.header("🧪 Electrolyte & Osmolality Evaluation")
    e1, e2, e3 = st.columns(3)
    with e1:
        na_in = st.number_input("Measured Na+", 100.0, 200.0, 145.0, 0.1)
        glu_in = st.number_input("Glucose", 10.0, 1000.0, 100.0, 1.0)
        bun_in = st.number_input("BUN", 5.0, 300.0, 20.0, 1.0)
        k_in = st.number_input("Measured K+", 1.0, 10.0, 4.0, 0.1)
        hco3_in = st.number_input("Measured HCO3-", 5.0, 40.0, 20.0, 0.1)
        bag_master = st.selectbox("Fluid Bag (mL)", [30, 50, 100, 250, 500, 1000], index=5)
    with e2:
        cna = na_in + 1.6*((glu_in-100)/100) if glu_in > 100 else na_in
        osmo = 2*(na_in+k_in) + (glu_in/18) + (bun_in/2.8)
        st.markdown(f"""<div class="card-eval"><b>Corrected Na+:</b><br><span style="font-size:32px; font-weight:900; color:#DC2626 !important;">{cna:.1f} mEq/L</span></div>
        <div class="card-eval"><b>Osmolality:</b><br><span style="font-size:32px; font-weight:900; color:#2563EB !important;">{osmo:.1f} mOsm/kg</span></div>""", unsafe_allow_html=True)
    with e3:
        kt = next((v for kr, v in {2.0:80, 2.5:60, 3.0:40, 3.5:28}.items() if k_in <= kr), 10)
        st.markdown(f"""<div class="card-eval" style="border-left:10px solid #3B82F6 !important;">
        <b>KCl (2mEq/ml) 첨가량:</b><br><span style="font-size:32px; font-weight:900; color:#1E3A8A !important;">Add {(kt*bag_master/1000)/2.0:.1f} mL</span><br>
        <p>Target: {kt}mEq/L (in {bag_master}ml)</p></div>""", unsafe_allow_html=True)

# --- TAB 3: CRI 조제 (변수명 weight_master 사용으로 NameError 방지) ---
with tabs[2]:
    st.header("💉 High-Visibility CRI Protocol")
    dr_sel = st.selectbox("약물 선택", ["Butorphanol", "Midazolam", "Dexmedetomidine", "Epinephrine", "Norepinephrine", "Dopamine", "Furosemide", "Insulin(RI)"])
    cr1, cr2 = st.columns([1, 2])
    with cr1:
        irate = st.number_input("펌프 속도 (mL/h)", 0.1, 100.0, 0.5, 0.1)
        tdose = st.number_input("목표 용량 (mpk/h or mcg/kg/min)", 0.0, 50.0, 0.1, 0.01, format="%.3f")
        svol = st.selectbox("시린지 용량", [10, 20, 50], index=2)
    with cr2:
        is_mcg = dr_sel in ["Epinephrine", "Norepinephrine", "Dopamine"]
        mgh_calc = (tdose * weight_master * 60 / 1000) if is_mcg else (tdose * weight_master)
        dml_calc = (mgh_calc / STOCK_DB[dr_sel]) * svol / irate
        st.markdown(f"""<div class="card-cri-final">
            <span class="cri-label">🚩 {dr_sel} 설정 속도</span><br><span class="val-speed-huge">{irate:.1f} mL/h</span><br><br>
            <span class="cri-label">🧪 조제법 (총 {svol}mL)</span><br><span class="val-recipe-large">원액 {dml_calc:.2f} mL + 희석액 {(svol-dml_calc):.2f} mL</span>
        </div>""", unsafe_allow_html=True)

# --- TAB 4: 수액 & 아미노산 ---
with tabs[3]:
    st.markdown("""<div class="sop-banner"><h2>RER = BW × 50 kcal/day</h2><p style="font-size:22px;">💡 표준 유지 범위: 40-60 mL/kg/day (시간당 약 2-3 mL/kg)</p></div>""", unsafe_allow_html=True)
    f1, f2 = st.columns([1.2, 1])
    with f1:
        st.subheader("💧 수액 속도 (Dry Mode)")
        total_f = (weight_master * st.slider("유지 (mL/kg/hr)", 1.0, 4.0, 2.0)) + (st.number_input("지속 손실 (mL/day)", value=float(round(weight_master*1.0, 1))) / 24)
        st.metric("최종 수액 속도", f"{total_f:.1f} mL/h")
    with f2:
        st.subheader("🧬 아미노산 공급")
        aa_key = st.selectbox("아미노산 제제", list(AMINO_ACID_DB.keys()))
        aa_val = (1.0 / AMINO_ACID_DB[aa_key]['conc']) * 100
        st.markdown(f"""<div style="background-color:#F0FDF4; padding:25px; border-radius:12px; border:2px solid #22C55E;">
        <b style="font-size:20px; color:#166534 !important;">{aa_key}</b><br>
        <span style="font-size:34px; font-weight:900; color:#15803D !important;">{aa_val:.1f} mL / 100 kcal</span><br>
        <p>단백질 1g/100kcal 충족 시 필요량</p></div>""", unsafe_allow_html=True)

# --- TAB 5: 영양 관리 ---
with tabs[4]:
    st.markdown('<div class="sop-banner"><h3>🍽️ Nutrition Protocol</h3></div>', unsafe_allow_html=True)
    n1, n2 = st.columns(2)
    with n1:
        der_m = (weight_master * 50) * DISEASE_FACTORS_DB[cat_name][sub_cat_name] * (1.1 if st.checkbox("입원 가중치", value=True) else 1.0)
        st_sel = st.radio("전략", ["3단계", "4단계", "5단계"], horizontal=True)
        sm = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        cs_m = st.select_slider("현재 단계", options=sm[st_sel], value=sm[st_sel][-1])
        st.metric("목표 DER", f"{der_m*cs_m:.0f} kcal")
    with n2:
        br_m = st.selectbox("사료 브랜드", list(DIET_DB.keys()))
        pd_m = st.selectbox("사료 제품", list(DIET_DB[br_m].keys()))
        kcal_m = DIET_DB[br_m][pd_m]
        is_w_m = any(x in pd_m for x in ["Wet", "Recovery", "a/d"])
        amt_m = ((der_m*cs_m)/kcal_m) * (1 if is_w_m else 1000)
        st.success(f"### 급여량: **{amt_m:.1f} {'can' if is_w_m else 'g'}**")

# --- TAB 6: 수혈 ---
with tabs[5]:
    st.header("🩸 Blood Transfusion")
    tx1, tx2 = st.columns([1, 1.5])
    with tx1:
        cp_m = st.number_input("현재 PCV", 1.0, 50.0, 15.0); tp_m = st.number_input("목표 PCV", 1.0, 50.0, 25.0)
        pr_m = st.radio("제제", ["전혈", "pRBC"], horizontal=True)
        res_m = weight_master * (90 if species_master == "개(Canine)" else 60) * ((tp_m - cp_m) / (40.0 if pr_m == "전혈" else 70.0))
        st.metric("수혈 필요량", f"{max(0.0, round(res_m, 1))} mL")
    with tx2:
        st.info("**[수혈 가이드]** 1. 일반 4시간 완료. 2. 심장/신장 환자 12-24시간 연장 가능 (분할 투여 권장).")

st.divider()
st.caption(f"Royal Animal Medical Center | v32.0 Final | Clinical Intelligence by Dr. Jaehee Lee")
