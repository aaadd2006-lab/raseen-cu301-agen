import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


from ml_model import (
    predict_turbofan_status,
    best_params,
    f1_score_val
)

from tools import (
    query_engine_cost_sql,
    calculate_rul_and_maintenance_cost_api,
    send_user_alert_api
)


def run_supervisor(
    engine_id: str,
    sensor_s2: float,
    sensor_s3: float,
    sensor_s4: float,
    sensor_s11: float
):

    logs = []

    # =========================================
    # STEP 1 - KNN Diagnosis
    # =========================================

    status_label = predict_turbofan_status(
        sensor_s2,
        sensor_s3,
        sensor_s4,
        sensor_s11
    )

    logs.append(
        f"🔍 **[KNN Classifier & GridSearchCV]:** "
        f"المعلمات `{best_params}` | "
        f"F1-Score: `{f1_score_val:.2f}`"
    )

    logs.append(
        f"⚡ **[Turbofan Diagnosis]:** "
        f"حالة المحرك → `{status_label}`"
    )

    # =========================================
    # STEP 2 - Fleet Registry Agent
    # =========================================

    logs.append(
        "🤖 **[Agent 1 - Fleet Registry]:** "
        "استعلام بيانات المحرك من سجل الأسطول..."
    )

    cost_info = query_engine_cost_sql(
        engine_id
    )

    logs.append(
        f"   └─ معرف المحرك: "
        f"`{cost_info['engine_id']}` | "
        f"القيمة التقديرية: "
        f"**${cost_info['asset_cost_usd']:,}**"
    )

    # =========================================
    # STEP 3 - RUL Agent
    # =========================================

    logs.append(
        "🤖 **[Agent 2 - RUL Degradation Agent]:** "
        "حساب العمر التشغيلي المتبقي..."
    )

    damage_info = calculate_rul_and_maintenance_cost_api(
        engine_id,
        status_label
    )

    logs.append(
        f"   └─ RUL المتبقي: "
        f"**{damage_info['rul_cycles']} Cycles** | "
        f"حالة الخطر: "
        f"`{damage_info['risk_level']}`"
    )

    logs.append(
        f"   └─ تكلفة الصيانة المتوقعة: "
        f"**${damage_info['repair_cost_usd']:,.2f}**"
    )

    # =========================================
    # STEP 4 - Notification Agent
    # =========================================

    logs.append(
        "🤖 **[Agent 3 - Notification Agent]:** "
        "إنشاء تقرير الصيانة الوقائية..."
    )

    alert_info = send_user_alert_api(
        engine_id,
        status_label,
        cost_info["asset_cost_usd"],
        damage_info["repair_cost_usd"]
    )

    logs.append(
        f"   └─ التقرير النهائي:\n"
        f"> {alert_info['message']}"
    )

    # =========================================
    # FINAL RESULT
    # =========================================

    return {
        "status_label": status_label,
        "logs": logs
    }
