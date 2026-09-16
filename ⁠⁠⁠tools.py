# =========================================================
# NASA C-MAPSS Turbofan Engine Fleet
# Simulated Fleet Registry
# =========================================================


NASA_CMAPSS_FLEET = {

    "ENGINE-001": {

        "engine_id": "FD001_ENG_04",

        "max_cycles": 200,

        "current_cycle": 165,

        "unit_cost": 12000000

    },


    "ENGINE-002": {

        "engine_id": "FD002_ENG_12",

        "max_cycles": 250,

        "current_cycle": 242,

        "unit_cost": 15000000

    }

}


# =========================================================
# Agent 1
# Fleet Registry
# =========================================================

def query_engine_cost_sql(

    engine_id: str

):


    engine_data = NASA_CMAPSS_FLEET.get(

        engine_id.upper(),

        NASA_CMAPSS_FLEET["ENGINE-001"]

    )


    return {

        "engine_name":

            engine_id,


        "engine_id":

            engine_data["engine_id"],


        "asset_cost_usd":

            engine_data["unit_cost"],


        "current_cycle":

            engine_data["current_cycle"],


        "source":

            "NASA C-MAPSS Simulator Fleet Registry"

    }


# =========================================================
# Agent 2
# RUL + Maintenance Cost
# =========================================================

def calculate_rul_and_maintenance_cost_api(

    engine_id: str,

    health_status: str

):


    engine_data = NASA_CMAPSS_FLEET.get(

        engine_id.upper(),

        NASA_CMAPSS_FLEET["ENGINE-001"]

    )


    # =====================================================
    # Critical
    # =====================================================

    if health_status == "HIGH_PRESSURE_FAILURE":


        rul_cycles = max(

            0,

            engine_data["max_cycles"]

            - engine_data["current_cycle"]

            - 25

        )


        risk_level = (

            "Critical Degradation "
            "(Low RUL / Imminent Failure)"

        )


        damage_multiplier = 3.0


    # =====================================================
    # Warning
    # =====================================================

    elif health_status == "WARNING":


        rul_cycles = max(

            5,

            engine_data["max_cycles"]

            - engine_data["current_cycle"]

            - 10

        )


        risk_level = (

            "Moderate Subsystem Degradation"

        )


        damage_multiplier = 1.4


    # =====================================================
    # Normal
    # =====================================================

    else:


        rul_cycles = max(

            50,

            engine_data["max_cycles"]

            - engine_data["current_cycle"]

        )


        risk_level = (

            "Healthy / Optimal RUL State"

        )


        damage_multiplier = 0.1


    # =====================================================
    # Maintenance Cost
    # =====================================================

    estimated_overhaul = (

        450000 * damage_multiplier

    )


    return {

        "risk_level":

            risk_level,


        "rul_cycles":

            rul_cycles,


        "repair_cost_usd":

            estimated_overhaul

    }


# =========================================================
# Agent 3
# Notification
# =========================================================

def send_user_alert_api(

    engine_id: str,

    health_status: str,

    asset_cost: float,

    repair_cost: float

):


    alert_msg = (

        f"🚨 [Turbofan Alert] "
        f"Engine {engine_id} "
        f"Health Status: {health_status}\n"

        f"💰 Engine Asset Value: "
        f"${asset_cost:,.2f} | "

        f"Estimated Overhaul Cost: "
        f"${repair_cost:,.2f}\n"

        f"📊 Benchmark: "
        f"NASA C-MAPSS Simulator"

    )


    return {

        "status":

            "SENT",


        "message":

            alert_msg

    }
