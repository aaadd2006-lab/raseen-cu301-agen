import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml_model import predict_turbofan_status, best_params, f1_score_val
from tools import (
    query_engine_cost_sql,
    calculate_rul_and_maintenance_cost_api,
    send_user_alert_api,
)

from langchain.tools import tool
from langchain.agents import create_agent


# ============================================================
# LangChain Tools
# ============================================================


@tool
def fleet_registry_tool(engine_id: str) -> dict:
    """Retrieve engine asset information from the fleet registry."""
    return query_engine_cost_sql(engine_id)


@tool
def rul_degradation_tool(engine_id: str, health_status: str) -> dict:
    """Calculate remaining useful life, risk level, and estimated repair cost."""
    return calculate_rul_and_maintenance_cost_api(
        engine_id,
        health_status
    )


@tool
def notification_tool(
    engine_id: str,
    health_status: str,
    asset_cost: float,
    repair_cost: float
) -> dict:
    """Create the final preventive-maintenance notification."""
    return send_user_alert_api(
        engine_id,
        health_status,
        asset_cost,
        repair_cost
    )


SUPERVISOR_SYSTEM_PROMPT = """
You are the Supervisor Agent for the Raseen predictive maintenance system.

Your responsibilities:
1. Understand the engine health status provided by the system.
2. Use the Fleet Registry Tool to retrieve engine information.
3. Use the RUL Degradation Tool to calculate remaining useful life,
   risk level, and estimated maintenance cost.
4. Use the Notification Tool to generate the final maintenance report.
5. Coordinate the tools in the correct order.
6. Do not invent engine data or maintenance values.
"""

def build_supervisor(model):
    """
    Build the LangChain Supervisor Agent.

    The model is passed from outside so we can choose the LLM later.
    This function only builds the agent; it does not execute it.
    """

    supervisor = create_agent(
        model=model,
        tools=[
            fleet_registry_tool,
            rul_degradation_tool,
            notification_tool
        ],
        system_prompt=SUPERVISOR_SYSTEM_PROMPT,
        name="raseen_supervisor"
    )

    return supervisor



# ============================================================
# Supervisor
# ============================================================

def run_supervisor(
    engine_id: str,
    sensor_s2: float,
    sensor_s3: float,
    sensor_s4: float,
    sensor_s11: float
):
    """
    Supervisor workflow.

    The KNN model determines the engine health status.
    LangChain tools provide the fleet, RUL, and notification
    capabilities used by the supervisor architecture.
    """

    logs = []

    # --------------------------------------------------------
    # Step 1: KNN diagnosis
    # --------------------------------------------------------

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
        f"⚡ **[NASA C-MAPSS Diagnosis]:** "
        f"حالة المحرك النفاث → `{status_label}`"
    )

    # --------------------------------------------------------
    # Step 2: Fleet Registry Tool
    # --------------------------------------------------------

    logs.append(
        "🤖 **[Agent 1 - Fleet Registry]:** "
        "استعلام بيانات المحرك النفاث من NASA C-MAPSS..."
    )

    cost_info = fleet_registry_tool.invoke({
        "engine_id": engine_id
    })

    logs.append(
        f"   └─ معرف المحرك: `{cost_info['engine_id']}` | "
        f"القيمة التقديرية: "
        f"**${cost_info['asset_cost_usd']:,}**"
    )

    # --------------------------------------------------------
    # Step 3: RUL Degradation Tool
    # --------------------------------------------------------

    logs.append(
        "🤖 **[Agent 2 - RUL Degradation Agent]:** "
        "حساب العمر التشغيلي المتبقي (RUL)..."
    )

    damage_info = rul_degradation_tool.invoke({
        "engine_id": engine_id,
        "health_status": status_label
    })

    logs.append(
        f"   └─ RUL المتبقي: "
        f"**{damage_info['rul_cycles']} دورات (Cycles)** | "
        f"حالة الخطر: `{damage_info['risk_level']}`"
    )

    logs.append(
        f"   └─ تكلفة الصيانة المتوقعة: "
        f"**${damage_info['repair_cost_usd']:,}**"
    )

    # --------------------------------------------------------
    # Step 4: Notification Tool
    # --------------------------------------------------------

    logs.append(
        "🤖 **[Agent 3 - Notification Agent]:** "
        "إنشاء تقرير الصيانة الوقائية..."
    )

    alert_info = notification_tool.invoke({
        "engine_id": engine_id,
        "health_status": status_label,
        "asset_cost": cost_info["asset_cost_usd"],
        "repair_cost": damage_info["repair_cost_usd"]
    })

    logs.append(
        f"   └─ التقرير النهائي:\n"
        f"> {alert_info['message']}"
    )

    return {
        "status_label": status_label,
        "logs": logs
    }
