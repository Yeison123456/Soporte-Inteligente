# # app/services/churn.py
# # Heurística combinada para score de churn 0-100, tomando en cuenta variables que enviaste.
from typing import Dict, Any
from app.core.preprocess import text_signals

def predict_churn_score(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    payload incluye:
    - Descripcion_Caso (text)
    - Antiguedad_Contrato (months)
    - Volumen_Tickets_Ult_Mes
    - Segmento_Cliente
    Devuelve {'score': int, 'breakdown': {...}}
    """
    text = payload.get("Descripcion_Caso", "")
    antiguedad = payload.get("Antiguedad_Contrato")
    volumen = payload.get("Volumen_Tickets_Ult_Mes")
    segmento = (payload.get("Segmento_Cliente") or "").upper()

    signals = text_signals(text)

    # Base score
    score = 10

    # Señales de texto negativas / urgencia
    score += signals["urgent_count"] * 60
    score += signals["negative_count"] * 20

    # URLs sospechosas aumentan riesgo
    if signals["has_shortener"]:
        score += 40
    if signals["num_urls"] > 0:
        score += 5 * signals["num_urls"]

    # Volumen tickets en el último mes
    if volumen is not None:
        if volumen >= 20:
            score += 25
        elif volumen >= 5:
            score += 10

    # Antiguedad del contrato: contratos muy nuevos más riesgo de churn
    if antiguedad is not None:
        if antiguedad < 6:
            score += 35
        elif antiguedad > 24:
            score -= 20
        else: 
            score += 15

    # Segmento de cliente: A => menos riesgo (valor alto), C => más riesgo
    if segmento == "A":
        score -= 5
    elif segmento == "C":
        score += 5

    # clamp 0-100
    score = max(0, min(100, int(score)))

    breakdown = {
        "urgent_count": signals["urgent_count"] * 20,
        "negative_count": signals["negative_count"] * 10,
        "num_urls": signals["num_urls"],
        "has_shortener": signals["has_shortener"],
        "volumen_tickets": volumen,
        "antiguedad": antiguedad,
        "segmento": segmento
    }
    return {"score": score, "breakdown": breakdown}


# app/services/churn.py

# import joblib
# import numpy as np
# from tensorflow.keras.models import load_model
# from app.core.preprocess import text_signals

# # Cargar modelo y vectorizadores
# model = load_model("models/churn_model.h5")
# vectorizer = joblib.load("models/vectorizer.pkl")
# ohe = joblib.load("models/ohe.pkl")

# def predict_churn_score(payload):
#     text = payload.get("Descripcion_Caso", "")
#     antiguedad = payload.get("Antiguedad_Contrato", 0)
#     volumen = payload.get("Volumen_Tickets_Ult_Mes", 0)
#     segmento = payload.get("Segmento_Cliente", "B")

#     # TF-IDF del texto
#     X_text = vectorizer.transform([text]).toarray()

#     # One-hot
#     X_segmento = ohe.transform([[segmento]]).toarray()

#     # Numéricas
#     X_numeric = np.array([[antiguedad, volumen]])

#     # Unir todo
#     X = np.hstack([X_text, X_segmento, X_numeric])

#     pred = model.predict(X)[0][0]
#     score = int(pred * 100)

#     return {
#         "score": score,
#         "breakdown": {
#             "segmento": segmento,
#             "antiguedad": antiguedad,
#             "volumen": volumen,
#             "text_vector_used": True
#         }
#     }