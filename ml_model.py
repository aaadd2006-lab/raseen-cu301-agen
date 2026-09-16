import numpy as np

from sklearn.model_selection import (
    train_test_split,
    GridSearchCV
)

from sklearn.neighbors import KNeighborsClassifier

from sklearn.metrics import (
    confusion_matrix,
    f1_score
)


# =========================================================
# تدريب نموذج KNN
# =========================================================

def train_turbofan_knn_model():

    # تثبيت النتائج
    np.random.seed(42)


    # =====================================================
    # NORMAL DATA
    # =====================================================

    normal_data = np.random.normal(

        loc=[
            4.5,
            65,
            0.2,
            55
        ],

        scale=[
            0.5,
            5,
            0.05,
            5
        ],

        size=(50, 4)
    )


    # =====================================================
    # WARNING DATA
    # =====================================================

    warning_data = np.random.normal(

        loc=[
            7.0,
            85,
            0.6,
            75
        ],

        scale=[
            0.7,
            7,
            0.1,
            7
        ],

        size=(50, 4)
    )


    # =====================================================
    # FAILURE DATA
    # =====================================================

    failure_data = np.random.normal(

        loc=[
            10.5,
            105,
            1.2,
            95
        ],

        scale=[
            0.8,
            8,
            0.15,
            8
        ],

        size=(50, 4)
    )


    # =====================================================
    # دمج البيانات
    # =====================================================

    X = np.vstack([

        normal_data,

        warning_data,

        failure_data
    ])


    # Labels

    y = np.array(

        ["NORMAL"] * 50

        + ["WARNING"] * 50

        + ["HIGH_PRESSURE_FAILURE"] * 50
    )


    # =====================================================
    # تقسيم البيانات
    # =====================================================

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.2,

        random_state=42,

        stratify=y
    )


    # =====================================================
    # GridSearchCV
    # =====================================================

    param_grid = {

        "n_neighbors": [
            3,
            5,
            7,
            9
        ],

        "weights": [
            "uniform",
            "distance"
        ]
    }


    knn = KNeighborsClassifier()


    grid_search = GridSearchCV(

        knn,

        param_grid,

        cv=3,

        scoring="f1_macro"
    )


    grid_search.fit(

        X_train,

        y_train
    )


    # =====================================================
    # أفضل موديل
    # =====================================================

    best_model = grid_search.best_estimator_


    # =====================================================
    # Prediction
    # =====================================================

    y_pred = best_model.predict(

        X_test
    )


    # =====================================================
    # F1 Score
    # =====================================================

    best_f1 = f1_score(

        y_test,

        y_pred,

        average="macro"
    )


    # =====================================================
    # Confusion Matrix
    # =====================================================

    cm = confusion_matrix(

        y_test,

        y_pred,

        labels=[
            "NORMAL",
            "WARNING",
            "HIGH_PRESSURE_FAILURE"
        ]
    )


    return (

        best_model,

        grid_search.best_params_,

        best_f1,

        cm
    )


# =========================================================
# تدريب النموذج عند تشغيل التطبيق
# =========================================================

model, best_params, f1_score_val, cm_matrix = (

    train_turbofan_knn_model()
)


# =========================================================
# دالة التنبؤ
# =========================================================

def predict_turbofan_status(

    p_val,

    temp_val,

    vib_val,

    flow_val

):

    """
    Predict turbofan health status
    using the trained KNN model.
    """


    prediction = model.predict([

        [

            p_val,

            temp_val,

            vib_val,

            flow_val

        ]

    ])[0]


    return prediction
