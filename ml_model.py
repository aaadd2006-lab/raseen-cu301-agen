import numpy as np
from sklearn.ensemble import RandomForestClassifier

def train_cu301_model():
    # Synthetic CU 301 Sensor Data: [Pressure (Bar), Temperature (°C), Flow Rate (L/min)]
    X_train = np.array([
        [0.2, 85, 5],    # NO_PRESSURE (Dry running)
        [0.5, 80, 10],   # NO_PRESSURE
        [4.5, 65, 50],   # NORMAL_PRESSURE
        [5.0, 70, 55],   # NORMAL_PRESSURE
        [9.5, 95, 85],   # HIGH_PRESSURE (Overpressure)
        [10.0, 90, 90]   # HIGH_PRESSURE
    ])
    y_train = ['NO_PRESSURE', 'NO_PRESSURE', 'NORMAL_PRESSURE', 'NORMAL_PRESSURE', 'HIGH_PRESSURE', 'HIGH_PRESSURE']

    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    return rf_model

model = train_cu301_model()

def predict_cu301_pressure(pressure: float, temp: float, flow: float) -> str:
    """التنبؤ بحالة الضغط باستخدام Random Forest Classifier"""
    prediction = model.predict([[pressure, temp, flow]])[0]
    return prediction
