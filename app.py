import streamlit as st
import streamlit.components.v1 as components

# --- [1. 디자인 및 시인성 완전 해결: 강력한 CSS 고정] ---
st.set_page_config(page_title="로얄동물메디컬센터 임상 지능 시스템", layout="wide")

st.markdown("""
    <style>
    /* [VITAL] 배경 및 텍스트 색상 강제 고정 (다크모드 무시) */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], .stTabs {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* 모든 텍스트 요소를 검은색으로 고정 */
    .stMarkdown, p, span, label, div, h1, h2, h3, h4 {
        color: #000000 !important;
    }

    /* [CRITICAL] 위젯(선택창, 입력창) 블랙박스 현상 해결 */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    input, select, textarea {
        background-color: #F8FAFC !important;
        color: #000000 !important;
        border: 2px solid #1E3A8A !important;
        font-weight: 700 !important;
    }

    /* 드롭다운 리스트 내부 텍스트 가시성 */
    div[role="listbox"] div {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }

    /* 상단 배너 */
    .banner-sop {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        padding: 30px;
        border-radius: 15px;
        border-left: 12px solid #EF4444 !important;
        margin-bottom: 25px;
    }
    .banner-sop h2, .banner-sop p { color: #FFFFFF !important; }

    /* CRI 조제 카드 - 초대형 시인성 */
    .card-cri-v31 {
        background-color: #F1F5F9 !important;
        border: 2px solid #CBD5E1 !important;
        border-left: 15px solid #10B981 !important;
        padding: 40px;
        border-radius: 20px;
        margin-top: 20px;
    }
    .val-speed { font-size: 60px !important; font-weight: 900 !important; color: #059669 !important; }
    .val-recipe { font-size: 40px !important; font-weight: 800 !important; color: #1E3A8A !important; }

    /* 전해질 평가 카드 */
    .card-eval {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    .eval-red { font-size: 34px !important; font-weight: 900 !important; color: #DC2626 !important; }
    .eval-blue { font-size: 34px !important; font-weight: 900 !important; color: #2563EB !important; }
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
    "후라바솔 10% (고용량)": {"conc": 10.0},
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
    "Royal Canin": {"Recovery": 105, "GI (Dry)": 3912, "GI Low Fat (Wet)": 385, "Urinary S/O": 3884, "Renal": 3988},
    "Hill's": {"a/d": 183, "i/d Digestive": 3663, "i/d Low Fat Wet": 341, "k/d Kidney": 4220}
}

# --- [3. 공통 환자 데이터 (사이드바 고정)] ---
with st.sidebar:
    st.markdown("## 📋 Patient Profile")
    species_val = st.selectbox("품종", ["개(Canine)", "고양이(Feline)"])
    weight_val = st.number_input("체중 (kg)", 0.1, 150.0, 3.1, 0.1, format="%.1f")
    st.markdown("---")
    cat_name = st.selectbox("질환 카테고리", list(DISEASE_FACTORS_DB.keys()))
    sub_cat_name = st.selectbox("세부 상태", list(DISEASE_FACTORS_DB[cat_name].keys()))
    st.markdown("---")
    st.caption("Protocol Architect")
    st.markdown("### **Dr. Jaehee Lee**")

# --- [4. 메인 대시보드 구조] ---
st.title("🛡️ RAMC Advanced Clinical Intelligence System")
st.markdown("#### 로얄동물메디컬센터 임상 의사결정 지원 시스템")

tabs = st.tabs(["🚨 CPCR (CSU)", "🧪 전해질/삼투압", "💉 CRI 조제", "💧 수액 & 아미노산", "🍽️ 영양 관리", "🩸 수혈"])

# --- TAB 1: CPCR ---
with tabs[0]:
    st.subheader(f"🚨 CPCR Protocol for {weight_val:.1f}kg patient")
    bpm_val = st.radio("Compression Rate", [90, 120], horizontal=True)
    met_html = f"""
    <div style="display: flex; align-items: center; gap: 20px; background: #1E293B; padding: 20px; border-radius: 12px; color: white;">
        <button id="b" style="padding: 15px 30px; font-weight: 900; background: #10B981; color: white; border:none; border-radius:8px; font-size:20px;">▶ START</button>
        <div id="c" style="width:50px; height:50px; border-radius:50%; border:4px solid #374151; display:flex; align-items:center; justify-content:center;">❤️</div> 
        <div style="font-size: 24px; font-weight: bold; color:white !important;">{bpm_val} BPM</div>
    </div>
    <script>
        let ctx=null, tid=null, n=0, p=false; const btn=document.getElementById('b'), pulse=document.getElementById('c');
        function t(){{ while(n<ctx.currentTime+0.1){{ const o=ctx.createOscillator(), g=ctx.createGain(); o.connect(g); g.connect(ctx.destination); o.frequency.value=880; g.gain.value=0.03; o.start(n); o.stop(n+0.05); n+=60/{bpm_val}; }} tid=setTimeout(t,25); }}
        btn.onclick=()=>{{ if(!ctx)ctx=new (window.AudioContext||window.webkitAudioContext)(); if(p){{clearInterval(tid); tid=null; btn.innerText='▶ START'; btn.style.background='#10B981';}} else{{n=ctx.currentTime; t(); btn.innerText='■ STOP'; btn.style.background='#EF4444';}} p=!p; }};
    </script>"""
    components.html(met_html, height=120)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="card-eval"><b>1. VF / Pulseless VT</b><br><br>
        <b>Defib:</b> Ext {weight_val*4:.1f}-{weight_val*6:.1f}J | Int {weight_val*0.5:.1f}-{weight_val*1J}<br>
        - Epi(L): {(weight_val*0.01):.2f} ml IV | Vaso: {(weight_val*0.8/20):.2f} ml IV<br>
        - Amiodarone: {(weight_val*5/50):.2f} ml IV</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="card-eval"><b>2. Asystole / PEA</b><br><br>
        - Epi(L): {(weight_val*0.01):.2f} ml IV (Every other cycle)<br>
        - Vasopressin: {(weight_val*0.8/20):.2f} ml IV (One-time)<br>
        - Atropine: {(weight_val*0.04/0.5):.2f} ml IV (Every other cycle)</div>""", unsafe_allow_html=True)

# --- TAB 2: 전해질/삼투압 ---
with tabs[1]:
    st.header("🧪 Electrolyte & Osmolality Evaluation")
    e1, e2, e3 = st.columns(3)
    with e1:
        cur_na = st.number_input("Measured Na+", 100.0, 200.0, 145.0, 0.1)
        cur_glu = st.number_input("Glucose", 10.0, 1000.0, 100.0, 1.0)
        cur_bun = st.number_input("BUN", 5.0, 300.0, 20.0, 1.0)
        cur_k = st.number_input("Measured K+", 1.0, 10.0, 4.0, 0.1)
        cur_hco3 = st.number_input("Measured HCO3-", 5.0, 40.0, 20.0, 0.1)
        cur_bag = st.selectbox("Fluid Bag (mL)", [30, 50, 100, 250, 500, 1000], index=5)
    with e2:
        st.subheader("평가 결과")
        calc_cna = cur_na + 1.6*((cur_glu-100)/100) if cur_glu > 100 else cur_na
        calc_osmo = 2*(cur_na+cur_k) + (cur_glu/18) + (cur_bun/2.8)
        st.markdown(f"""<div class="card-eval"><b>Corrected Na+:</b><br><span class="eval-red">{calc_cna:.1f} mEq/L</span></div>
        <div class="card-eval"><b>Osmolality:</b><br><span class="eval-blue">{calc_osmo:.1f} mOsm/kg</span></div>""", unsafe_allow_html=True)
    with e3:
        st.subheader("보정 레시피")
        k_target = next((v for kr, v in {2.0:80, 2.5:60, 3.0:40, 3.5:28}.items() if cur_k <= kr), 10)
        k_add_ml = (k_target * cur_bag / 1000) / 2.0
        st.markdown(f"""<div class="card-eval" style="border-left:8px solid #3B82F6 !important;">
        <b>KCl (2mEq/ml) 첨가량:</b><br><span class="eval-blue">Add {k_add_ml:.1f} mL</span><br>
        <p>Target: {k_target}mEq/L (in {cur_bag}ml Bag)</p></div>""", unsafe_allow_html=True)

# --- TAB 3: CRI 조제 (변수 이름 완벽 통일) ---
with tabs[2]:
    st.header("💉 High-Visibility CRI Protocol")
    # [IMPORTANT] 변수 이름을 dr_sel_tab3로 고유화하여 충돌 방지
    dr_sel_tab3 = st.selectbox("CRI 약물 선택", ["Butorphanol", "Midazolam", "Dexmedetomidine", "Epinephrine", "Norepinephrine", "Dopamine", "Furosemide", "Insulin(RI)"])
    cr1, cr2 = st.columns([1, 2])
    with cr1:
        irate = st.number_input("설정 속도 (mL/h)", 0.1, 100.0, 0.5, 0.1)
        tdose = st.number_input("목표 용량 (mpk/h or mcg/kg/min)", 0.0, 50.0, 0.1, 0.01, format="%.3f")
        svolume = st.selectbox("시린지 용량 (mL)", [10, 20, 50], index=2)
    with cr2:
        # Epinephrine, Norepinephrine, Dopamine은 mcg 기준 계산
        is_mcg_dr = dr_sel_tab3 in ["Epinephrine", "Norepinephrine", "Dopamine"]
        mgh_val = (tdose * weight_val * 60 / 1000) if is_mcg_dr else (tdose * weight_val)
        dml_val = (mgh_val / STOCK_DB[dr_sel_tab3]) * svolume / irate
        st.markdown(f"""<div class="card-cri-v31">
            <span style="font-size:24px; font-weight:bold;">🚩 {dr_sel_tab3} 설정 속도</span><br><span class="val-speed">{irate:.1f} mL/h</span><br><br>
            <span style="font-size:24px; font-weight:bold;">🧪 조제 레시피 (총 {svolume}mL)</span><br><span class="val-recipe">원액 {dml_val:.2f} mL + 희석액 {(svolume-dml_val):.2f} mL</span>
        </div>""", unsafe_allow_html=True)

# --- TAB 4: 수액 & 아미노산 ---
with tabs[3]:
    st.markdown("""<div class="banner-sop"><h2>RER = BW × 50 kcal/day</h2><p style="font-size:22px;">💡 표준 유지 범위: 40-60 mL/kg/day (시간당 약 2-3 mL/kg)</p></div>""", unsafe_allow_html=True)
    f1, f2 = st.columns([1.2, 1])
    with f1:
        st.subheader("💧 수액 속도 계산 (Dry Mode)")
        mr_val = st.slider("유지 용량 (mL/kg/hr)", 1.0, 4.0, 2.0)
        total_f_val = (weight_val * mr_val) + (st.number_input("지속 손실 (mL/day)", value=float(round(weight_val*1.0, 1))) / 24)
        st.metric("최종 수액 속도", f"{total_f_val:.1f} mL/h")
    with f2:
        st.subheader("🧬 아미노산 공급")
        aa_sel_v = st.selectbox("아미노산 제제", list(AMINO_ACID_DB.keys()))
        aa_ml_v = (1.0 / AMINO_ACID_DB[aa_sel_v]['conc']) * 100
        st.markdown(f"""<div style="background-color:#F0FDF4; padding:25px; border-radius:12px; border:2px solid #22C55E;">
        <b style="font-size:22px; color:#166534 !important;">{aa_sel_v}</b><br>
        <span style="font-size:34px; font-weight:900; color:#15803D !important;">{aa_ml_v:.1f} mL / 100 kcal</span><br>
        <p>단백질 1g/100kcal 보정 시 필요량</p></div>""", unsafe_allow_html=True)

# --- TAB 5: 영양 관리 ---
with tabs[4]:
    st.markdown('<div class="banner-sop"><h2>Royal Nutrition Protocol</h2></div>', unsafe_allow_html=True)
    n1, n2 = st.columns(2)
    with n1:
        der_final = (weight_val * 50) * DISEASE_FACTORS_DB[cat_name][sub_cat_name] * (1.1 if st.checkbox("입원 환자 가중치", value=True) else 1.0)
        strat_v = st.radio("급여 전략", ["3단계", "4단계", "5단계"], horizontal=True)
        sm_v = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        cs_v = st.select_slider("현재 급여 단계", options=sm_v[strat_v], value=sm_v[strat_v][-1])
        st.metric("목표 DER", f"{der_final*cs_v:.0f} kcal")
    with n2:
        brand_v = st.selectbox("사료 브랜드", list(DIET_DB.keys()))
        prod_v = st.selectbox("제품 선택", list(DIET_DB[brand_v].keys()))
        kcal_val_v = DIET_DB[brand_v][prod_v]
        amt_v = ((der_final*cs_v)/kcal_val_v) * (1 if "Recovery" in prod_v or "a/d" in prod_v or "Wet" in prod_v else 1000)
        st.success(f"### 급여량: **{amt_v:.1f} {'can' if 'Recovery' in prod_v or 'a/d' in prod_v or 'Wet' in prod_v else 'g'}**")

# --- TAB 6: 수혈 ---
with tabs[5]:
    st.header("🩸 Blood Transfusion Calculator")
    tx1, tx2 = st.columns([1, 1.5])
    with tx1:
        cp_v = st.number_input("현재 PCV", 1.0, 50.0, 15.0); tp_v = st.number_input("목표 PCV", 1.0, 50.0, 25.0)
        pr_v = st.radio("수혈 제제", ["전혈", "pRBC"], horizontal=True)
        kv_v = 90 if species_val == "개(Canine)" else 60
        res_v = weight_val * kv_v * ((tp_v - cp_v) / (40.0 if pr_v == "전혈" else 70.0))
        st.metric("예상 수혈량", f"{max(0.0, round(res_v, 1))} mL")
    with tx2:
        st.info("**[수혈 SOP]** 1. 일반 환자 4시간 원칙. 2. 심장/신장 환자 12-24시간 연장 가능 (분할 투여 권장).")

st.divider()
st.caption(f"Royal Animal Medical Center | v31.0 Final Stable | Clinical Intelligence by Dr. Jaehee Lee")
