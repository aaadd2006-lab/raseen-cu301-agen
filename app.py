import sys
import os
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supervisor_agent import run_supervisor
from ml_model import best_params, f1_score_val, cm_matrix

st.set_page_config(page_title="رَصِين | Turbofan Multi-Agent", page_icon="⚙️", layout="wide")

st.title("⚙️ منصة رَصِين | Turbofan Maintenance MAS (KNN & GridSearchCV)")
st.caption("نظام وكلاء متعددين ذكي لتتبع أداء محركات ومضخات Turbofan باستخدام KNN وLangChain")

st.sidebar.header("🎛️ قراءات حساسات Turbofan Engine")
pump_num = st.sidebar.selectbox("رقم المحرك", ["PUMP-001", "PUMP-002"])
pressure = st.sidebar.slider("الضغط (Bar)", 0.0, 15.0, 10.5)
temp = st.sidebar.slider("الحرارة (°C)", 30, 130, 105)
vib = st.sidebar.slider("الاهتزاز (Vibration)", 0.0, 2.0, 1.2)
flow = st.sidebar.slider("التدفق (L/min)", 0, 120, 95)

# Metrics section
c1, c2, c3 = st.columns(3)
c1.metric("الموديل المستخدم", "KNN Classifier")
c2.metric("أعلى F1-Score للموديل", f"{f1_score_val:.2f}")
c3.metric("GridSearchCV Best Params", str(best_params))

st.divider()

col_left, col_right = st.columns([6, 4])

with col_left:
    st.subheader("🤖 سجل تفكير المشرف والوكلاء (Supervisor reasoning)")
    if st.button("🚀 تشغيل الـ Supervisor Agent", type="primary", use_container_width=True):
        import time
        with st.status("🧠 [Supervisor Engine] جاري تنفيذ العمليات...", expanded=True) as status:
            res = run_supervisor(pump_num, pressure, temp, vib, flow)
            for l in res["logs"]:
                st.write(l)
                time.sleep(0.5)
            status.update(label="✅ اكتمل التحليل والتنفيذ بنجاح", state="complete")

with col_right:
    st.subheader("📊 Confusion Matrix للنموذج")
    fig, ax = plt.subplots(figsize=(4, 3))
    sns.heatmap(cm_matrix, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Normal', 'Warning', 'Failure'], 
                yticklabels=['Normal', 'Warning', 'Failure'], ax=ax)
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    st.pyplot(fig)
