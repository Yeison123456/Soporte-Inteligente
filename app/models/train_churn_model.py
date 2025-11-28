# # train_churn_model.py
# import numpy as np
# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import OneHotEncoder
# from sklearn.feature_extraction.text import TfidfVectorizer
# from tensorflow.keras import models, layers

# # 1. Cargar dataset
# df = pd.read_csv("dataset_churn.csv")

# # 2. Procesar texto (TF-IDF)
# vectorizer = TfidfVectorizer(max_features=500)
# X_text = vectorizer.fit_transform(df["Descripcion_Caso"]).toarray()

# # 3. One-hot segmento
# ohe = OneHotEncoder()
# X_segmento = ohe.fit_transform(df[["Segmento_Cliente"]]).toarray()

# # 4. Variables numéricas
# X_numeric = df[["Antiguedad_Contrato", "Volumen_Tickets_Ult_Mes"]].values

# # 5. Unir todas las features
# X = np.hstack([X_text, X_segmento, X_numeric])
# y = df["Churn_Score"].values / 100  # normalizado 0-1

# # 6. Red neuronal
# model = models.Sequential([
#     layers.Dense(128, activation='relu', input_shape=(X.shape[1],)),
#     layers.Dense(64, activation='relu'),
#     layers.Dense(1, activation='sigmoid')  # salida entre 0–1
# ])

# model.compile(optimizer='adam', loss='mse')
# model.fit(X, y, epochs=20, batch_size=32)

# # 7. Guardar modelo y vectorizadores
# model.save("churn_model.h5")
# import joblib
# joblib.dump(vectorizer, "vectorizer.pkl")
# joblib.dump(ohe, "ohe.pkl")
