import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, f1_score

def load_ncmapss_pandas(file_path='nasa_sample.csv'):
    """قراءة بيانات ناسا المصغرة بـ Pandas"""
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        X = df[['s2', 's3', 's4', 's11']].values
        
        # تصنيف الحالات بناءً على مستويات القراءات
        y = np.where(X[:, 0] > np.percentile(X[:, 0], 70), 'HIGH_PRESSURE_FAILURE',
            np.where(X[:, 0] > np.percentile(X[:, 0], 35), 'WARNING', 'NORMAL'))
        return X, y
    else:
        # Fallback بيانات محاكاة احتياطية
        np.random.seed(42)
        normal = np.random.normal(loc=[4.5, 65, 0.2, 55], scale=[0.5, 5, 0.05, 5], size=(50, 4))
        warning = np.random.normal(loc=[7.0, 85, 0.6, 75], scale=[0.7, 7, 0.1, 7], size=(50, 4))
        failure = np.random.normal(loc=[10.5, 105, 1.2, 95], scale=[0.8, 8, 0.15, 8], size=(50, 4))
        X = np.vstack([normal, warning, failure])
        y = np.array(['NORMAL'] * 50 + ['WARNING'] * 50 + ['HIGH_PRESSURE_FAILURE'] * 50)
        return X, y

def train_turbofan_knn_model():
    X, y = load_ncmapss_pandas()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # GridSearch_CV لتعديل البرامترات
    param_grid = {'n_neighbors': [3, 5, 7, 9], 'weights': ['uniform', 'distance']}
    knn = KNeighborsClassifier()
    
    grid_search = GridSearchCV(knn, param_grid, cv=3, scoring='f1_macro')
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)
    
    best_f1 = f1_score(y_test, y_pred, average='macro')
    cm = confusion_matrix(y_test, y_pred, labels=['NORMAL', 'WARNING', 'HIGH_PRESSURE_FAILURE'])

    return best_model, grid_search.best_params_, best_f1, cm

# تدريب النموذج عند التشغيل
model, best_params, f1_score_val, cm_matrix = train_turbofan_knn_model()

def predict_turbofan_status(p_val, temp_val, vib_val, flow_val):
    """التنبؤ بحالة المحرك النفاث"""
    pred = model.predict([[p_val, temp_val, vib_val, flow_val]])[0]
    return pred
