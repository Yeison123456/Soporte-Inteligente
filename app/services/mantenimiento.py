# # Clasificación heurística para tipo de mantenimiento. 

from typing import Tuple

EVOLUTIVO_KEYWORDS = ["nueva feature", "feature", "mejora", "agregar", "añadir", "requerimos", "deseamos"]
CORRECTIVO_KEYWORDS = ["no funciona", "falla", "error", "critico", "caído", "urgent", "urgente", "bug"]

def classify_mantenimiento(text: str) -> Tuple[dict, dict]:
    """
    Retorna (classification_dict, reasons)
    classification_dict: {"class": "Correctivo"/"Evolutivo", "prob": float}
    reasons: explicacion de por qué
    """
    low = text.lower()
    score_e = sum(1 for k in EVOLUTIVO_KEYWORDS if k in low)
    score_c = sum(1 for k in CORRECTIVO_KEYWORDS if k in low)

    # decisión simple: si score_e > score_c => evolutivo, si score_c > score_e => correctivo
    if score_e > score_c:
        return {"class": "Evolutivo", "prob": 0.85}, {"score_e": score_e, "score_c": score_c}
    if score_c > score_e:
        return {"class": "Correctivo", "prob": 0.90}, {"score_e": score_e, "score_c": score_c}
    # empate o ninguno: fallback por longitud/urgency
    if "urgente" in low or "urgent" in low:
        return {"class": "Correctivo", "prob": 0.8}, {"note": "urgente_detectado"}
    return {"class": "Evolutivo", "prob": 0.6}, {"note": "falta_evidencia"}


# from sklearn.model_selection import train_test_split
# from sklearn.feature_extraction.text import TfidfVectorizer
# from tensorflow.keras import models, layers
# import numpy as np

# texts = [
#     "el sistema no funciona",
#     "error critico en producción",
#     "se requiere nueva funcionalidad",
#     "deseamos agregar una mejora",
#     "bug urgente",
#     "quiero añadir una feature nueva",
# ]
# labels = [0,0,1,1,0,1]  # 0 = Correctivo, 1 = Evolutivo

# # Vectorización
# vectorizer = TfidfVectorizer()
# X = vectorizer.fit_transform(texts).toarray()
# y = np.array(labels)

# # Modelo MLP
# model = models.Sequential([
#     layers.Dense(16, activation='relu', input_shape=(X.shape[1],)),
#     layers.Dense(8, activation='relu'),
#     layers.Dense(1, activation='sigmoid')
# ])

# model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
# model.fit(X, y, epochs=20)

# def predict_mantenimiento(text: str):
#     X_test = vectorizer.transform([text]).toarray()
#     pred = model.predict(X_test)[0][0]
#     return {
#         "class": "Evolutivo" if pred > 0.5 else "Correctivo",
#         "prob": float(pred)
#     }
