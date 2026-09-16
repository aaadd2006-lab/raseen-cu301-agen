import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml_model import predict_turbofan_status, best_params, f1_score_val
from tools import query_engine_cost_sql, calculate_rul_and_maintenance_cost_api, send_user_alert_api

try:
    from langchain.agents import AgentExecutor
    HAS_LANGCHAIN = True
except ModuleNotFoundError:
    HAS_LANGCHAIN = False

def run_supervisor(engine_id: str, sensor_s2: float, sensor_s3: float, sensor_s4: float, sensor_s11: float):
    logs = []
    
    # الخطوة 1: تنبؤ نموذج KNN بالتدهور عبر قراءات حساسات التوربوفان
    status_label = predict_turbofan_status(sensor_s2, sensor_s3, sensor_s4, sensor_s11)
    logs.append(f"🔍 **[KNN Classifier & GridSearchCV]:** المعلمات `{best_params}` | F1-Score: `{f1_score_val:.2f}`")
    logs.append(f"⚡ **[NASA C-MAPSS Diagnosis]:** حالة المحرك النفاث $\rightarrow$ `{status_label}`")
    
    # الخطوة 2: الوكيل الأول - استعلام بيانات المحرك
    logs.append(f"🤖 **[Agent 1 - Fleet Registry]:** استعلام بيانات المحرك النفاث من NASA C-MAPSS...")
    cost_info = query_engine_cost_sql(engine_id)
    logs.append(f"   └─ معرف المحرك: `{cost_info['engine_id']}` | القيمة التقديرية: **${cost_info['asset_cost_usd']:,}**")
    
    # الخطوة 3: الوكيل الثاني - حساب الـ RUL
    logs.append(f"🤖 **[Agent 2 - RUL Degradation Agent]:** حساب العمر التشغيلي المتبقي (Remaining Useful Life - RUL)...")
    damage_info = calculate_rul_and_maintenance_cost_api(engine_id, status_label)
    logs.append(f"   └─ RUL المتبقي: **{damage_info['rul_cycles']} دورات (Cycles)** | حالة الخطر: `{damage_info['risk_level']}`")
    logs.append(f"   └─ تكلفة الصيانة والشفرات/التوربين المتوقعة: **${damage_info['repair_cost_usd']:,}**")
    
    # الخطوة 4: الوكيل الثالث - التنبيهات
    logs.append(f"🤖 **[Agent 3 - Notification Agent (LangChain Integrator)]:** إرسال تقرير الصيانة الوقائية...")
    alert_info = send_user_alert_api(engine_id, status_label, cost_info['asset_cost_usd'], damage_info['repair_cost_usd'])
    logs.append(f"   └─ التقرير النهائي:\n> {alert_info['message']}")
    
    return {
        "status_label": status_label,
        "logs": logs
    }
