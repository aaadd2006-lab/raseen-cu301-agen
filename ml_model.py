import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score

def train_turbofan_knn_model():
    # Synthetic Turbofan Sensor Data (Mocking NASA Turbofan dataset structure)
    # Features: [Sensor_1_Pressure, Sensor_2_Temp, Sensor_3_Vibration, Sensor_4_Flow]
    np.random.seed(42)
    n_samples = 150
    
    # Normal operations
    normal_data = np.random.normal(loc=[4.5, 65, 0.2, 55], scale=[0.5, 5, 0.05, 5], size=(50, 4))
    # Warning condition (Degradation)
    warning_data = np.random.normal(loc=[7.0, 85, 0.6, 75], scale=[0.7, 7, 0.1, 7], size=(50, 4))
    # Critical failure (High Pressure/Failure)
    failure_data = np.random.normal(loc=[10.5, 105, 1.2, 95], scale=[0.8, 8, 0.15, 8], size=(50, 4))

    X = np.vstack([normal_data, warning_data, failure_data])
    y = np.array(['NORMAL'] * 50 + ['WARNING'] * 50 + ['HIGH_PRESSURE_FAILURE'] * 50)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # GridSearch_CV for KNN Hyperparameter Tuning
    param_grid = {'n_neighbors': [3, 5, 7, 9], 'weights': ['uniform', 'distance']}
    knn = KNeighborsClassifier()
    
    # Optimize based on F1-Score (macro)
    grid_search = GridSearchCV(knn, param_grid, cv=3, scoring='f1_macro')
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)
    
    best_f1 = f1_score(y_test, y_pred, average='macro')
    cm = confusion_matrix(y_test, y_pred, labels=['NORMAL', 'WARNING', 'HIGH_PRESSURE_FAILURE'])

    return best_model, grid_search.best_params_, best_f1, cm

# Train model on startup
model, best_params, f1_score_val, cm_matrix = train_turbofan_knn_model()

def predict_turbofan_status(p_val, temp_val, vib_val, flow_val):
    """Predict failure/status using tuned KNN model"""
    pred = model.predict([[p_val, temp_val, vib_val, flow_val]])[0]
    return pred
