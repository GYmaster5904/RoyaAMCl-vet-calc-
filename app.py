
import streamlit as st
import streamlit.components.v1 as components

# --- [1. 디자인 및 시인성 해결을 위한 최상위 CSS 고정] ---
st.set_page_config(page_title="로얄동물메디컬센터 Vet Calc v27.0", layout="wide")

st.markdown("""
    <style>
    /* 배경 및 사이드바 강제 화이트 고정 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
        color: #111827 !important;
    }
    
    /* 사이드바 내부 텍스트 색상 강제 */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #111827 !important;
    }

    /* 위젯 텍스트 시인성 확보 */
    .stMarkdown, p, span, label, div { color: #111827 !important; }
    input, select { background-color: #F9FAFB !important; color: #111827 !important; }

    /* CSU 스타일 테이블 및 로직 박스 */
    .csu-logic-box {
        background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .logic-title { font-size: 18px; font-weight: 800; color: #1E3A8A !important; margin-bottom: 10px; }
    .logic-item { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #F1F5F9; }
    .tag-or { color: #EF4444 !important; font-weight: 900; margin: 0 10px; }
    .tag-and { color: #3B82F6 !important; font-weight: 900; margin: 0 10px; }

    /* CRI 조제법 시인성 - 초대형 폰트 */
    .cri-final-card {
        background-color: #F1F5F9; border-left: 12px solid #10B981; padding: 30px; border-radius: 15px;
    }
    .val-speed { font-size: 52px; font-weight: 900; color: #059669 !important; }
    .val-recipe { font-size: 36px; font-weight: 800; color: #1E3A8A !important; }

    /* 공식 및 SOP 공지 배너 */
    .sop-notice {
        background-color: #1E293B; color: #FFFFFF !important; padding: 20px; border-radius: 10px;
        border-left: 8px solid #EF4444; margin-bottom: 25px;
    }
    .sop-notice h3, .sop-notice p { color: #FFFFFF !important; }
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
    "기본/비만": {"성장기": 2.0, "중성화 완료": 1.2, "미중성화": 1.4, "비만감량": 0.8},
    "신장/심장": {"CKD 안정기": 1.15, "CKD 저체중": 1.25, "심장병 안정": 1.15, "심부전": 1.05},
    "췌장/간/소화기": {"췌장염 안정기": 1.1, "간질환 안정": 1.15, "지방간(HL)": 1.35, "EPI": 1.25},
    "중증/암": {"암 환자": 1.2, "악액질/중증": 1.4}
}

DIET_LIST = {
    "Royal Canin": {"Recovery": 105, "GI (Dry)": 3912, "GI Low Fat (Wet)": 385, "Urinary S/O": 3884, "Renal": 3988},
    "Hill's": {"a/d": 183, "i/d Digestive": 3663, "i/d Low Fat Wet": 341, "k/d Kidney": 4220}
}

# --- [3. 사이드바 환자 고정 데이터] ---
with st.sidebar:
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
tabs = st.tabs(["🚨 CPCR (CSU)", "🧪 전해질/삼투압", "💉 CRI 조제", "💧 수액 요법", "🍴 영양 관리", "🩸 수혈"])

# --- TAB 1: CPCR (시계형 컴팩트 메트로놈) ---
with tabs[0]:
    st.subheader(f"🚨 CPCR Protocol for {weight:.1f}kg patient")
    
    col_met, col_rev = st.columns([1, 2.5])
    with col_met:
        bpm_val = st.radio("BPM", [90, 120], horizontal=True)
        metronome_html = f"""
        <div style="text-align:center; background:#1E293B; padding:15px; border-radius:15px; color:white;">
            <div id="clock" style="width:60px; height:60px; border-radius:50%; border:4px solid #374151; margin:0 auto 10px; display:flex; align-items:center; justify-content:center; position:relative;">
                <div id="pulse" style="width:0%; height:0%; background:#10B981; border-radius:50%; position:absolute; opacity:0.5;"></div>
                <b style="font-size:16px; z-index:1;">{bpm_val}</b>
            </div>
            <button id="mB" style="width:100%; padding:8px; font-weight:900; background:#10B981; color:white; border:none; border-radius:5px; cursor:pointer;">START</button>
        </div>
        <script>
            let c=null, i=null, n=0, p=false; const b=document.getElementById('mB'), pulse=document.getElementById('pulse');
            function t(){{ while(n<c.currentTime+0.1){{ const o=c.createOscillator(), g=c.createGain(); o.connect(g); g.connect(c.destination); o.frequency.value=880; g.gain.value=0.03; o.start(n); o.stop(n+0.05);
                setTimeout(()=>{{ pulse.style.width='100%'; pulse.style.height='100%'; pulse.style.opacity='0.5'; setTimeout(()=>{{ pulse.style.width='0%'; pulse.style.height='0%'; pulse.style.opacity='0'; }}, 100); }}, (n-c.currentTime)*1000); n+=60/{bpm_val}; }} i=setTimeout(t,25); }}
            b.onclick=()=>{{ if(!c)c=new(window.AudioContext||window.webkitAudioContext)(); if(p){{clearInterval(i); i=null; b.innerText='START'; b.style.background='#10B981';}} else{{n=c.currentTime; t(); b.innerText='STOP'; b.style.background='#EF4444';}} p=!p; }};
        </script>
        """
        components.html(metronome_html, height=160)
    
    with col_rev:
        st.markdown(f"""<div style="background-color:#F8FAFC; padding:15px; border-radius:10px; border:1px solid #CBD5E1;">
        <b>Reversals:</b> Naloxone {(weight*0.04/0.4):.2f}ml | Flumazenil {(weight*0.01/0.1):.2f}ml | Atipamezole {(weight*0.1/5.0):.2f}ml</div>""", unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="csu-logic-box">
            <div class="logic-title">1. VF / Pulseless VT</div>
            <p><b>Defibrillation:</b> Ext {weight*4:.1f}-{weight*6:.1f}J | Int {weight*0.5:.1f}-{weight*1.0:.1f}J</p>
            <div class="logic-item"><span>Epinephrine (L)</span><b>{(weight*0.01):.2f} ml IV</b></div>
            <div class="tag-or">OR (Prolonged >10m)</div>
            <div class="logic-item"><span>Vasopressin</span><b>{(weight*0.8/20):.2f} ml IV</b></div>
            <div class="tag-and">AND</div>
            <div class="logic-item"><span>Amiodarone</span><b>{(weight*5/50):.2f} ml IV</b></div>
            <div class="tag-or">OR (Dogs Only)</div>
            <div class="logic-item"><span>Lidocaine</span><b>{(weight*2/20):.2f} ml IV</b></div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""<div class="csu-logic-box">
            <div class="logic-title">2. Asystole / PEA / Bradycardia</div>
            <p><i>Every other 2-min cycle 마다 투여 고려</i></p>
            <div class="logic-item"><span>Epinephrine (L)</span><b>{(weight*0.01):.2f} ml IV</b></div>
            <div class="tag-or">OR</div>
            <div class="logic-item"><span>Vasopressin</span><b>{(weight*0.8/20):.2f} ml IV (1회 한정)</b></div>
            <div class="tag-and">AND</div>
            <p><i>Every other cycle only</i></p>
            <div class="logic-item"><span>Atropine</span><b>{(weight*0.04/0.5):.2f} ml IV</b></div>
            <hr>
            <p><b>Intratracheal:</b> Epi {(weight*0.02):.2f}ml | Atropine {(weight*0.16):.2f}ml</p>
        </div>""", unsafe_allow_html=True)

# --- TAB 2: 전해질/삼투압 (30, 50ml 추가) ---
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
        st.markdown(f"""<div class="csu-logic-box"><b>Corrected Na+:</b><br><span style="font-size:26px; font-weight:900; color:#DC2626;">{c_na:.1f} mEq/L</span></div>
        <div class="csu-logic-box"><b>Osmolality:</b><br><span style="font-size:26px; font-weight:900; color:#2563EB;">{osmo:.1f} mOsm/kg</span></div>""", unsafe_allow_html=True)
    with e3:
        st.subheader("조제 레시피")
        kt = next((v for kr, v in {2.0:80, 2.5:60, 3.0:40, 3.5:28}.items() if k_in <= kr), 10)
        st.markdown(f"""<div class="csu-logic-box" style="border-left:8px solid #3B82F6;">
        <b>KCl (2mEq/ml) 첨가량:</b><br><span style="font-size:30px; font-weight:900; color:#1E3A8A;">Add {(kt*bag_v/1000)/2.0:.1f} ml</span><br>
        <p>목표: {kt}mEq/L (in {bag_v}ml)</p></div>""", unsafe_allow_html=True)

# --- TAB 3: CRI 조제 (초대형 시인성) ---
with tabs[2]:
    st.header("💉 CRI High-Visibility Protocol")
    dr_c = st.selectbox("약물", ["Butorphanol", "Midazolam", "Dexmedetomidine", "Epinephrine", "Norepinephrine", "Dopamine", "Furosemide", "Insulin(RI)"])
    cr1, cr2 = st.columns([1, 2])
    with cr1:
        ir_v = st.number_input("설정 속도 (mL/h)", 0.1, 100.0, 0.5, 0.1); td_v = st.number_input("목표 용량 (mpk/h or mcg/kg/min)", 0.0, 50.0, 0.1, 0.01, format="%.3f")
        sv_v = st.selectbox("시린지 용량", [10, 20, 50], index=2)
    with cr2:
        mgh = (td_v*weight*60/1000) if dr_c in ["Epinephrine", "Norepinephrine", "Dopamine"] else (td_v*weight)
        dml = (mgh / STOCK[dr_c]) * sv_v / ir_v
        st.markdown(f"""<div class="cri-final-card">
            <span style="font-size:22px; font-weight:bold; color:#4B5563;">🚩 {dr_c} 설정 속도</span><br><span class="val-speed">{ir_v:.1f} mL/h</span><br><br>
            <span style="font-size:22px; font-weight:bold; color:#4B5563;">🧪 조제법 (총 {sv_v}mL)</span><br><span class="val-recipe">원액 {dml:.2f} mL + 희석액 {(sv_v-dml):.2f} mL</span>
        </div>""", unsafe_allow_html=True)

# --- TAB 4: 수액 요법 ---
with tabs[3]:
    st.markdown("""<div class="sop-notice">
        <h2>RER = BW × 50 kcal/day</h2>
        <p style="font-size:18px;">💡 표준 유지 범위: 40-60 mL/kg/day (시간당 약 2-3 mL/kg)</p></div>""", unsafe_allow_html=True)
    f1, f2 = st.columns([1.5, 1])
    with f1:
        ms = st.radio("상황 선택", ["로얄 Dry Mode (입원)", "AAHA 2024 마취"], horizontal=True)
        if "Dry" in ms:
            mr = st.slider("유지 (mL/kg/hr)", 1.0, 4.0, 2.0, 0.5)
            dy = st.number_input("탈수 (%)", 0, 15, 0)
            lo = st.number_input("지속 손실 (mL/day)", value=float(round(weight*1.0, 1)), step=0.1)
            st.metric("최종 수액 속도", f"{(weight*mr)+(lo/24):.1f} mL/h")
        else: st.metric("마취 수액 속도 (AAHA)", f"{(weight*5 if species=='개(Canine)' else weight*3):.1f} mL/h")
    with f2:
        if "심장" in sub_cat: st.error("심장 질환: 수액 과부하 주의. RR 감시 필수.")

# --- TAB 5: 영양 관리 ---
with tabs[4]:
    st.markdown('<div class="sop-notice"><h3>🍽️ Nutrition Protocol (3/4/5 Stages)</h3></div>', unsafe_allow_html=True)
    n1, n2 = st.columns(2)
    with n1:
        der = (weight * 50) * DISEASE_FACTORS[cat_n][sub_cat] * (1.1 if st.checkbox("입원 가중치 적용", value=True) else 1.0)
        st_opt = st.radio("전략", ["3단계", "4단계", "5단계"], horizontal=True)
        s_m = {"3단계": [0.33, 0.66, 1.0], "4단계": [0.25, 0.5, 0.75, 1.0], "5단계": [0.2, 0.4, 0.6, 0.8, 1.0]}
        cs = st.select_slider("현재 단계", options=s_m[st_opt], value=s_m[st_opt][-1])
        st.metric("목표 DER", f"{der*cs:.0f} kcal")
    with n2:
        br = st.selectbox("사료 브랜드", list(DIET_LIST.keys()))
        pd = st.selectbox("제품 선택", list(DIET_LIST[br].keys()))
        kcal = DIET_LIST[br][pd]
        amt = ((der*cs)/kcal) * (1 if "Recovery" in pd else 1000)
        st.success(f"### 급여량: **{amt:.1f} {'can' if 'Recovery' in pd else 'g'}**")

# --- TAB 6: 수혈 (12~24시간 연장 근거 반영) ---
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
        **[수혈 관리 표준 SOP]**
        1. **기본 원칙:** 일반 환자는 세균 증식 방지를 위해 **4시간 이내** 완료 권장.
        2. **연장 투여 (심장/신장 질환 환자):** 볼륨 부하(TACO) 위험이 높은 환자는 속도를 0.5~1.0 mL/kg/hr 이하로 조절하여 **12~24시간까지 유연하게 연장 투여** 가능.
           *(※ 혈액 오염 방지를 위해 가급적 혈액백을 분할하여 냉장 보관하며 연결 권장)*
        3. **초기 속도:** 첫 15~30분간 0.25~0.5 ml/kg/hr로 시작하여 부작용 감시.
        """)

st.divider()
st.caption(f"Royal Animal Medical Center | v27.0 Final | Clinical Solution by Dr. Jaehee Lee")
