# app/services/churn.py
import joblib
import numpy as np
import os
from tensorflow.keras.models import load_model

# ✅ Rutas con nombres únicos
MODEL_PATH = "models/churn_model.keras"
VECTORIZER_PATH = "models/churn_vectorizer.pkl"
OHE_PATH = "models/churn_ohe.pkl"

model = None
vectorizer = None
ohe = None

def load_churn_model():
    """Carga el modelo de churn si existe"""
    global model, vectorizer, ohe
    
    if not os.path.exists(MODEL_PATH):
        print(f"⚠️  Modelo de churn no encontrado en: {MODEL_PATH}")
        print(f"   Directorio actual: {os.getcwd()}")
        return False
    
    try:
        model = load_model(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        ohe = joblib.load(OHE_PATH)
        print("✅ Modelo de churn cargado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        import traceback
        traceback.print_exc()
        return False

def predict_churn_score(payload):
    """Predice el score de churn"""
    global model, vectorizer, ohe
    
    # Cargar modelo si no está en memoria
    if model is None:
        if not load_churn_model():
            return {
                "error": "Modelo no disponible. Entrénalo primero con train_churn_model.py"
            }
    
    text = payload.get("Descripcion_Caso", "")
    antiguedad = payload.get("Antiguedad_Contrato", 0)
    volumen = payload.get("Volumen_Tickets_Ult_Mes", 0)
    segmento = payload.get("Segmento_Cliente", "B")

    # TF-IDF del texto
    X_text = vectorizer.transform([text]).toarray()

    # One-hot
    X_segmento = ohe.transform([[segmento]]).toarray()

    # Numéricas
    X_numeric = np.array([[antiguedad, volumen]])

    # Unir todo
    X = np.hstack([X_text, X_segmento, X_numeric])

    pred = model.predict(X, verbose=0)[0][0]
    score = int(pred * 100)

    return {
        "score": score,
        "breakdown": {
            "segmento": segmento,
            "antiguedad": antiguedad,
            "volumen": volumen,
            "text_vector_used": True
        }
    }