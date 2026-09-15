from ml_model import predict_turbofan_status, best_params, f1_score_val
from tools import query_pump_cost_sql, calculate_damage_cost_api, send_user_alert_api

def run_supervisor(pump_number: str, pressure: float, temp: float, vib: float, flow: float):
    logs = []
    
    # Step 1: KNN + GridSearchCV Prediction
    status_label = predict_turbofan_status(pressure, temp, vib, flow)
    logs.append(f"🔍 **[KNN Classifier & GridSearchCV]:** أفضل المعلمات `{best_params}` | F1-Score: `{f1_score_val:.2f}`")
    logs.append(f"⚡ **[Turbofan AI Diagnosis]:** التصنيف المتوقع $\rightarrow$ `{status_label}`")
    
    # Step 2: Agent 1 (Pump Cost SQL Query)
    logs.append(f"🤖 **[Agent 1 - Pump Cost]:** استعلام SQL لـ Turbofan Asset...")
    cost_info = query_pump_cost_sql(pump_number)
    logs.append(f"   └─ قيمة المحرك الأصلي: **${cost_info['machine_cost_usd']:,}**")
    
    # Step 3: Agent 2 (Damage Cost API)
    logs.append(f"🤖 **[Agent 2 - Damage Cost]:** حساب تكلفة التلف والإصلاح...")
    damage_info = calculate_damage_cost_api(pump_number, status_label)
    logs.append(f"   └─ مستوى المخاطرة: `{damage_info['risk_level']}` | تكلفة الإصلاح: **${damage_info['repair_cost_usd']:,}**")
    
    # Step 4: Agent 3 (Notification & LangChain Workflow)
    logs.append(f"🤖 **[Agent 3 - Notification Agent (LangChain Integrator)]:** إنشاء الإشعار والتقرير...")
    alert_info = send_user_alert_api(pump_number, status_label, cost_info['machine_cost_usd'], damage_info['repair_cost_usd'])
    logs.append(f"   └─ الرسالة النهائية:\n> {alert_info['message']}")
    
    return {
        "status_label": status_label,
        "logs": logs
    }
