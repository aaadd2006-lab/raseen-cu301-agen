import sys
import os
import streamlit as st

# =========================================================
# إضافة مسار المشروع
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# =========================================================
# مكتبات الرسم
# =========================================================

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOT_LIBS = True

except ModuleNotFoundError:
    HAS_PLOT_LIBS = False


# =========================================================
# استدعاء Supervisor Agent 
# =========================================================

try:

    from supervisor_agent import run_supervisor

except ModuleNotFoundError as e:

    st.error(
        f"❌ يوجد ملف أو مكتبة مفقودة: {e.name}"
    )

    st.error(
        "تأكدي أن ملفات المشروع موجودة في نفس المجلد:"
    )

    st.code(
        "app.py\n"
        "supervisor_agent.py\n"
        "ml_model.py\n"
        "tools.py\n"
        "requirements.txt"
    )

    st.stop()

# =========================================================
# استدعاء نتائج نموذج Machine Learning
# =========================================================

from ml_model import (
    best_params,
    f1_score_val,
    cm_matrix
)


# =========================================================
# إعداد صفحة Streamlit
# =========================================================

st.set_page_config(
    page_title="رَصِين | Turbofan Maintenance",
    page_icon="⚙️",
    layout="wide"
)


# =========================================================
# عنوان المنصة
# =========================================================

st.title("⚙️ منصة رَصِين | Turbofan Maintenance MAS")

st.caption(
    "نظام ذكي لمراقبة حالة محركات Turbofan "
    "باستخدام KNN و GridSearchCV ووكلاء الصيانة"
)


# =========================================================
# SIDEBAR - قراءات الحساسات
# =========================================================

st.sidebar.header("🎛️ قراءات حساسات Turbofan Engine")


engine_id = st.sidebar.selectbox(
    "رقم المحرك",
    [
        "ENGINE-001",
        "ENGINE-002"
    ]
)


pressure = st.sidebar.slider(
    "الضغط (Bar)",
    0.0,
    15.0,
    10.5
)


temp = st.sidebar.slider(
    "الحرارة (°C)",
    30,
    130,
    105
)


vib = st.sidebar.slider(
    "الاهتزاز (Vibration)",
    0.0,
    2.0,
    1.2
)


flow = st.sidebar.slider(
    "التدفق (L/min)",
    0,
    120,
    95
)


# =========================================================
# MODEL METRICS
# =========================================================

c1, c2, c3 = st.columns(3)


c1.metric(
    "الموديل المستخدم",
    "KNN Classifier"
)


c2.metric(
    "أعلى F1-Score",
    f"{f1_score_val:.2f}"
)


c3.metric(
    "Best Parameters",
    str(best_params)
)


st.divider()


# =========================================================
# MAIN CONTENT
# =========================================================

col_left, col_right = st.columns([6, 4])


# =========================================================
# SUPERVISOR AGENT
# =========================================================

with col_left:

    st.subheader(
        "🤖 سجل تفكير المشرف والوكلاء"
    )


    if st.button(
        "🚀 تشغيل الـ Supervisor Agent",
        type="primary",
        use_container_width=True
    ):

        import time


        with st.status(
            "🧠 [Supervisor Engine] جاري تنفيذ العمليات...",
            expanded=True
        ) as status:


            result = run_supervisor(

                engine_id,

                pressure,

                temp,

                vib,

                flow
            )


            for log in result["logs"]:

                st.write(log)

                time.sleep(0.5)


            status.update(

                label="✅ اكتمل التحليل والتنفيذ بنجاح",

                state="complete"
            )


# =========================================================
# CONFUSION MATRIX
# =========================================================

with col_right:

    st.subheader(
        "📊 Confusion Matrix للنموذج"
    )


    if HAS_PLOT_LIBS:

        fig, ax = plt.subplots(
            figsize=(4, 3)
        )


        sns.heatmap(

            cm_matrix,

            annot=True,

            fmt="d",

            cmap="Blues",

            xticklabels=[
                "Normal",
                "Warning",
                "Failure"
            ],

            yticklabels=[
                "Normal",
                "Warning",
                "Failure"
            ],

            ax=ax
        )


        ax.set_ylabel(
            "Actual"
        )


        ax.set_xlabel(
            "Predicted"
        )


        st.pyplot(fig)


    else:

        st.warning(
            "⚠️ مكتبات الرسم غير متوفرة"
        )


        st.write(
            "مصفوفة الارتباك:",
            cm_matrix
        )
