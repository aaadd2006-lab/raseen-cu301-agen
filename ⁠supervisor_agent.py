from ml_model import predict_cu301_pressure
from tools import query_pump_cost_sql, calculate_damage_cost_api, send_user_alert_api

def run_supervisor(pump_number: str, pressure: float, temp: float, flow: float):
    logs = []
    
    # 1. Random Forest Classification
    pressure_label = predict_cu301_pressure(pressure, temp, flow)
    logs.append(f"🌲 **[Random Forest Classifier]:** تحليل قراءات CU 301 ➔ الحالة: `{pressure_label}`")
    
    # 2. Agent 1 (Pump Cost)
    logs.append(f"🤖 **[Agent 1 - Pump Cost Agent]:** استعلام SQL عبر Alibaba Cloud Data Lake...")
    cost_info = query_pump_cost_sql(pump_number)
    logs.append(f"   └─ قيمة المضخة الأصلية ({cost_info['pump_name']}): **${cost_info['machine_cost_usd']:,}**")
    
    # 3. Agent 2 (Damage Cost)
    logs.append(f"🤖 **[Agent 2 - Damage Cost Agent]:** حساب تكلفة الأضرار والإصلاح المتوقعة...")
    damage_info = calculate_damage_cost_api(pump_number, pressure_label)
    logs.append(f"   └─ مستوى الخطر: `{damage_info['risk_level']}` | التكلفة التقديرية: **${damage_info['repair_cost_usd']:,}**")
    
    # 4. Agent 3 (Notification)
    logs.append(f"🤖 **[Agent 3 - Notification Agent]:** صياغة وإرسال التنبيه المفصل للمستخدم...")
    alert_info = send_user_alert_api(
        pump_number, pressure_label, cost_info['machine_cost_usd'], damage_info['repair_cost_usd']
    )
    logs.append(f"   └─ نص الإشعار المرسل:\n> {alert_info['message']}")
    
    return {
        "pressure_label": pressure_label,
        "machine_cost": cost_info['machine_cost_usd'],
        "repair_cost": damage_info['repair_cost_usd'],
        "logs": logs
    }
