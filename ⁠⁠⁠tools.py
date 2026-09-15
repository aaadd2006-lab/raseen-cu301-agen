# محاكاة Data Lake على Alibaba Cloud وقاعدة بيانات SQL

ALIBABA_CLOUD_DB = {
    "PUMP-001": {"name": "Industrial Water Pump 01", "cost": 45000, "base_repair": 5000},
    "PUMP-002": {"name": "Cooling Water Pump 02", "cost": 65000, "base_repair": 8000}
}

def query_pump_cost_sql(pump_number: str):
    """Agent 1 Tool: Query SQL for pump cost on Alibaba Cloud Data Lake"""
    pump_data = ALIBABA_CLOUD_DB.get(pump_number.upper(), ALIBABA_CLOUD_DB["PUMP-001"])
    return {
        "pump_number": pump_number,
        "pump_name": pump_data["name"],
        "machine_cost_usd": pump_data["cost"],
        "source": "Alibaba Cloud Data Lake (SQL Query)"
    }

def calculate_damage_cost_api(pump_number: str, pressure_status: str):
    """Agent 2 Tool: Calculate damage and repair cost"""
    pump_data = ALIBABA_CLOUD_DB.get(pump_number.upper(), ALIBABA_CLOUD_DB["PUMP-001"])
    
    if pressure_status == "HIGH_PRESSURE":
        multiplier = 2.5
        risk_level = "High Pressure / Cavitation Risk"
    elif pressure_status == "NO_PRESSURE":
        multiplier = 1.8
        risk_level = "Dry Running Risk"
    else:
        multiplier = 0.0
        risk_level = "Normal Operation"

    repair_cost = pump_data["base_repair"] * multiplier
    return {
        "risk_level": risk_level,
        "repair_cost_usd": repair_cost
    }

def send_user_alert_api(pump_number: str, pressure_status: str, machine_cost: float, repair_cost: float):
    """Agent 3 Tool: Construct alert message for user"""
    alert_msg = (
        f"🚨 [CU 301 Alert] Pump {pump_number} Status: {pressure_status}\n"
        f"💰 Machine Value: ${machine_cost:,.2f} | Est. Repair Cost: ${repair_cost:,.2f}\n"
        f"📍 Data Source: Alibaba Cloud IoT Data Lake"
    )
    return {"status": "SENT", "message": alert_msg}
