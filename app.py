import sys
import os
import streamlit as st

# إضافة المسار الحالي لضمان وصول بايثون لجميع الملفات المجاورة
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# استدعاء المشرف بعد تحديد المسار
from supervisor_agent import run_supervisor

# إعدادات الصفحة
st.set_page_config(
    page_title="رَصِين | Multi-Agent Architecture",
    page_icon="⚙️",
    layout="wide"
)

# تنسيق العنوان
st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 800; color: #1E88E5; text-align: right; }
    .sub-title { font-size: 1rem; color: #555555; text-align: right; margin-bottom: 25px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚙️ منصة رَصِين | Multi-Agent Supervisor System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">نظام الوكلاء المتعددين لتحليل إشارات جهاز Grundfos CU 301 واستجابة الصيانة الآلية (Alibaba Cloud & Random Forest)</div>', unsafe_allow_html=True)

# القائمة الجانبية لحساسات CU 301
st.sidebar.header("🎛️ محاكاة جهاز Grundfos CU 301")
pump_num = st.sidebar.selectbox("اختر رقم المضخة", ["PUMP-001", "PUMP-002"])
pressure = st.sidebar.slider("🌐 الضغط Pressure (Bar)", 0.0, 12.0, 9.5)
temp = st.sidebar.slider("🌡️ الحرارة Temp (°C)", 40, 120, 85)
flow = st.sidebar.slider("💧 التدفق Flow Rate (L/min)", 0, 100, 70)

# عرض البيانات الأساسية
col1, col2, col3 = st.columns(3)
col1.metric("المعدة المختارة", pump_num)
col2.metric("قراءة الضغط الحالية", f"{pressure} Bar")
col3.metric("مصدر البيانات السحابية", "Alibaba Cloud Data Lake")

st.divider()

st.subheader("🤖 سجل تفكير المشرف والوكلاء الثلاثة (Supervisor Multi-Agent Reasoning)")

if st.button("🚀 تشغيل الـ Supervisor Agent للتحليل والتنفيذ", type="primary", use_container_width=True):
    import time
    with st.status("🧠 [Supervisor Active] جاري تنسيق المهام بين الوكلاء...", expanded=True) as status:
        result = run_supervisor(pump_num, pressure, temp, flow)
        
        for log in result["logs"]:
            st.write(log)
            time.sleep(0.8)
        
        if result["pressure_label"] == "NORMAL_PRESSURE":
            status.update(label="✅ جميع المؤشرات ضمن النطاق الطبيعي", state="complete")
            st.success("✨ المضخة تعمل بكفاءة عالية ولا تتطلب أي تدخل.")
        else:
            status.update(label="🚨 تم رصد خطر وتفعيل التدخل التلقائي!", state="error")
            st.error(f"⚠️ تم تصنيف الحالة بـ ({result['pressure_label']}). تم إرسال الإشعارات وحساب الخسائر التقديرية بنجاح.")
