from sklearn.feature_extraction.text import TfidfVectorizer #Trae el vectorizador TF-IDF de scikit-learn
import joblib #Utilidad para serializar (guardar/cargar) objetos Python de forma eficiente
import os
 
VECT_PATH = "models/tfidf.joblib" # Ruta al archivo del vectorizador guardado

def load_vectorizer():
    if os.path.exists(VECT_PATH):
        return joblib.load(VECT_PATH)
    
    # prototipo: crear uno simple
    vec = TfidfVectorizer(ngram_range=(1,2), max_features=5000)

    return vec
