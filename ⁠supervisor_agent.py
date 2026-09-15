import sys
import os

# إضافة المسار الحالي لضمان الوصول للملفات المجاورة
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml_model import predict_turbofan_status, best_params, f1_score_val
from tools import query_pump_cost_sql, calculate_damage_cost_api, send_user_alert_api

# استدعاء آمن لـ LangChain لمنع انهيار السيرفر أثناء تثبيت الحزم
try:
    from langchain.agents import AgentExecutor
    HAS_LANGCHAIN = True
except ModuleNotFoundError:
    HAS_LANGCHAIN = False

def run_supervisor(pump_number: str, pressure: float, temp: float, vib: float, flow: float):
    logs = []
    
    # الخطوة 1: تنبؤ نموذج KNN المطور بـ GridSearchCV
    status_label = predict_turbofan_status(pressure, temp, vib, flow)
    logs.append(f"🔍 **[KNN Classifier & GridSearchCV]:** أفضل المعلمات `{best_params}` | F1-Score: `{f1_score_val:.2f}`")
    logs.append(f"⚡ **[Turbofan AI Diagnosis]:** التصنيف المتوقع $\rightarrow$ `{status_label}`")
    
    # الخطوة 2: الوكيل الأول - استعلام قاعدة البيانات
    logs.append(f"🤖 **[Agent 1 - Pump Cost]:** استعلام SQL لـ Turbofan Asset...")
    cost_info = query_pump_cost_sql(pump_number)
    logs.append(f"   └─ قيمة المحرك الأصلي: **${cost_info['machine_cost_usd']:,}**")
    
    # الخطوة 3: الوكيل الثاني - حساب تكاليف الضرر
    logs.append(f"🤖 **[Agent 2 - Damage Cost]:** حساب تكلفة التلف والإصلاح...")
    damage_info = calculate_damage_cost_api(pump_number, status_label)
    logs.append(f"   └─ مستوى المخاطرة: `{damage_info['risk_level']}` | تكلفة الإصلاح: **${damage_info['repair_cost_usd']:,}**")
    
    # الخطوة 4: الوكيل الثالث - إرسال التنبيهات مع LangChain
    logs.append(f"🤖 **[Agent 3 - Notification Agent (LangChain Integrator)]:** إنشاء الإشعار والتقرير...")
    alert_info = send_user_alert_api(pump_number, status_label, cost_info['machine_cost_usd'], damage_info['repair_cost_usd'])
    logs.append(f"   └─ الرسالة النهائية:\n> {alert_info['message']}")
    
    return {
        "status_label": status_label,
        "logs": logs
    }
