# train_churn_model.py
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras import models, layers
import joblib
import os

# 1. Cargar dataset
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET_PATH = os.path.join(BASE_DIR, "app/models", "dataset_churn.csv")

print(f"📂 Buscando dataset en: {DATASET_PATH}")

if not os.path.exists(DATASET_PATH):
    print(f"❌ No se encontró el archivo: {DATASET_PATH}")
    exit(1)

df = pd.read_csv(DATASET_PATH)
print(f"✅ Dataset cargado: {len(df)} registros")

# 2. Procesar texto (TF-IDF)
vectorizer = TfidfVectorizer(max_features=500)
X_text = vectorizer.fit_transform(df["Descripcion_Caso"]).toarray()

# 3. One-hot segmento
ohe = OneHotEncoder()
X_segmento = ohe.fit_transform(df[["Segmento_Cliente"]]).toarray()

# 4. Variables numéricas
X_numeric = df[["Antiguedad_Contrato", "Volumen_Tickets_Ult_Mes"]].values

# 5. Unir todas las features
X = np.hstack([X_text, X_segmento, X_numeric])
y = df["Churn_Score"].values / 100  # normalizado 0-1

# 6. Entrenar con TODOS los datos
X_train = X  # Usar todo
y_train = y  # Usar todo

# 7. Red neuronal
model = models.Sequential([
    layers.Dense(128, activation='relu', input_shape=(X.shape[1],)),
    layers.Dropout(0.3),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])
model.fit(X_train, y_train, epochs=20, batch_size=32, verbose=1)

# 8. ✅ Guardar en la carpeta models/
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)  # Crear carpeta si no existe

MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.keras")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "churn_vectorizer.pkl")
OHE_PATH = os.path.join(MODEL_DIR, "churn_ohe.pkl")

model.save(MODEL_PATH)
joblib.dump(vectorizer, VECTORIZER_PATH)
joblib.dump(ohe, OHE_PATH)

print(f"\n✅ Modelo de churn entrenado y guardado.")
print(f"📂 Archivos guardados en: {MODEL_DIR}")
print(f"   - {MODEL_PATH}")
print(f"   - {VECTORIZER_PATH}")
print(f"   - {OHE_PATH}")