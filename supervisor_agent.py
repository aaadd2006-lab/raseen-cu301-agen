import sys
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


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


deepseek_model = ChatOpenAI(
    model="deepseek-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

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

@tool
def engine_prediction_tool(
    sensor_s2: float,
    sensor_s3: float,
    sensor_s4: float,
    sensor_s11: float
) -> dict:
    """Predict the current engine health status using the ML model."""

    status = predict_turbofan_status(
        sensor_s2,
        sensor_s3,
        sensor_s4,
        sensor_s11
    )

    return {
        "health_status": status,
        "model": "KNN"
    }


SUPERVISOR_SYSTEM_PROMPT = """
You are the Supervisor Agent for the Raseen predictive maintenance system.

You are responsible for coordinating the complete predictive maintenance workflow.

Follow these steps in order:

1. Use the Engine Prediction Tool with the provided sensor readings
   to determine the current engine health status.

2. Use the Fleet Registry Tool with the engine ID
   to retrieve the engine asset information and asset cost.

3. Use the RUL Degradation Tool with the engine ID and the predicted
   health status to calculate remaining useful life, risk level,
   and estimated repair cost.

4. Use the Notification Tool with the engine ID, health status,
   asset cost, and repair cost to generate the final maintenance report.

5. Do not skip any required tool.

6. Do not invent engine data, health status, RUL values,
   asset costs, repair costs, or notification results.

7. Use the output of each tool as input for the next required tool.

8. After all tools have been completed, provide a concise final response
   containing the engine ID, health status, model used, RUL,
   risk level, repair cost, and final maintenance message.
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
            engine_prediction_tool,
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

    The LangChain Supervisor Agent coordinates the complete
    predictive maintenance workflow.
    """

    logs = []

    # --------------------------------------------------------
    # Model information
    # --------------------------------------------------------

    logs.append(
        f"🔍 **[KNN Classifier & GridSearchCV]:** "
        f"المعلمات `{best_params}` | "
        f"F1-Score: `{f1_score_val:.2f}`"
    )

    # --------------------------------------------------------
    # LangChain Supervisor Agent
    # --------------------------------------------------------

    supervisor = build_supervisor(deepseek_model)

    agent_result = supervisor.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"""
Analyze engine {engine_id} using the following sensor readings.

Engine ID: {engine_id}

Sensor S2: {sensor_s2}
Sensor S3: {sensor_s3}
Sensor S4: {sensor_s4}
Sensor S11: {sensor_s11}

Complete the full predictive maintenance workflow.

First, use the Engine Prediction Tool to determine the engine health status.

Then, use the Fleet Registry Tool to retrieve the engine asset information.

Then, use the RUL Degradation Tool to calculate the remaining useful life,
risk level, and estimated repair cost.

Finally, use the Notification Tool to generate the preventive maintenance report.

Use the output of each tool when calling the next tool.

Do not invent any values.

Return a final maintenance report containing:
- Engine ID
- Health Status
- Model Used
- RUL
- Risk Level
- Asset Cost
- Repair Cost
- Final Maintenance Message
"""
                }
            ]
        }
    )

    agent_response = agent_result["messages"][-1].content

    logs.append(
        f"**[LangChain Supervisor]:**\n{agent_response}"
    )

    return {
        "logs": logs
    }
