# # # Clasificación heurística para tipo de mantenimiento. 

# from typing import Tuple

# EVOLUTIVO_KEYWORDS = ["nueva feature", "feature", "mejora", "agregar", "añadir", "requerimos", "deseamos"]
# CORRECTIVO_KEYWORDS = ["no funciona", "falla", "error", "critico", "caído", "urgent", "urgente", "bug"]

# def classify_mantenimiento(text: str) -> Tuple[dict, dict]:
#     """
#     Retorna (classification_dict, reasons)
#     classification_dict: {"class": "Correctivo"/"Evolutivo", "prob": float}
#     reasons: explicacion de por qué
#     """
#     low = text.lower()
#     score_e = sum(1 for k in EVOLUTIVO_KEYWORDS if k in low)
#     score_c = sum(1 for k in CORRECTIVO_KEYWORDS if k in low)

#     # decisión simple: si score_e > score_c => evolutivo, si score_c > score_e => correctivo
#     if score_e > score_c:
#         return {"class": "Evolutivo", "prob": 0.85}, {"score_e": score_e, "score_c": score_c}
#     if score_c > score_e:
#         return {"class": "Correctivo", "prob": 0.90}, {"score_e": score_e, "score_c": score_c}
#     # empate o ninguno: fallback por longitud/urgency
#     if "urgente" in low or "urgent" in low:
#         return {"class": "Correctivo", "prob": 0.8}, {"note": "urgente_detectado"}
#     return {"class": "Evolutivo", "prob": 0.6}, {"note": "falta_evidencia"}


from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras import models, layers
import numpy as np
import pickle  # Para guardar el vectorizador
from tensorflow.keras.callbacks import EarlyStopping


# Datos de entrenamiento (agregar más ejemplos mejorará el modelo)
# 0 = Correctivo (problemas, errores, bugs)
# 1 = Evolutivo (mejoras, nuevas funcionalidades)

texts = [
    "el sistema no funciona",
    "error critico en producción",
    "bug urgente",
    "falla en el servidor",
    "pantalla azul de la muerte",
    "el botón no responde",
    "la aplicación se cae constantemente",
    "error 500 en el servidor",
    "no puedo acceder al sistema",
    "la página no carga",
    "el login falla",
    "problema urgente con la base de datos",
    "se perdieron datos importantes",
    "el sistema está caído",
    "crash al iniciar la aplicación",
    "error al guardar información",
    "no se pueden procesar pagos",
    "fallo crítico en producción",
    "bug en el módulo de facturación",
    "la app se congela",
    "el sistema está muy lento",
    "timeout en las consultas",
    "la carga es demasiado lenta",
    "problemas de rendimiento",
    "demora mucho en responder",
    "se traba al cargar datos",
    "lentitud extrema en reportes",
    "el dashboard tarda mucho",
    "problemas de velocidad",
    "consumo excesivo de memoria",
    "los reportes no se generan correctamente",
    "el cálculo de impuestos está mal",
    "error en la sincronización de datos",
    "no se envían los emails",
    "las notificaciones no llegan",
    "problema con la autenticación",
    "error al exportar archivos",
    "los filtros no funcionan",
    "bug en la búsqueda",
    "error al eliminar registros",
    "no se guardan los cambios",
    "problema con los permisos",
    "falla la integración con el API",
    "error al cargar imágenes",
    "bug en el formulario de contacto",
    "no funciona el reset de contraseña",
    "error al procesar archivos CSV",
    "problema con el checkout",
    "falla el sistema de pagos",
    "bug en el carrito de compras",
    "no hay conexión con la base de datos",
    "error de red",
    "timeout en la conexión",
    "problema con el servidor",
    "se perdió la conexión",
    "error al conectar con el API",
    "falla la sincronización",
    "no se puede establecer conexión",
    "problema de conectividad",
    "error de comunicación entre servicios",
    "la interfaz no se muestra bien",
    "problema de visualización",
    "error en el diseño responsive",
    "los botones están desalineados",
    "bug en la vista móvil",
    "problema con el CSS",
    "error al renderizar componentes",
    "la página se ve rota",
    "bug visual en el dashboard",
    "problema con el layout",
    "se requiere nueva funcionalidad",
    "deseamos agregar una mejora",
    "quiero añadir una feature nueva",
    "implementar nuevo módulo",
    "agregar integración con API",
    "desarrollar dashboard de reportes",
    "necesitamos nueva función de exportación",
    "solicitud de módulo de analytics",
    "queremos añadir chat en vivo",
    "implementar sistema de notificaciones push",
    "agregar funcionalidad de búsqueda avanzada",
    "desarrollar app móvil",
    "crear nuevo módulo de inventarios",
    "implementar autenticación de dos factores",
    "agregar soporte para múltiples idiomas",
    "desarrollar sistema de reportes personalizados",
    "implementar dashboard ejecutivo",
    "añadir integración con redes sociales",
    "crear módulo de facturación electrónica",
    "desarrollar sistema de tickets",
    "mejorar el rendimiento del sistema",
    "optimizar la velocidad de carga",
    "actualizar el diseño de la interfaz",
    "mejorar la experiencia de usuario",
    "optimizar las consultas a base de datos",
    "mejorar el sistema de búsqueda",
    "actualizar la documentación",
    "mejorar la seguridad del sistema",
    "optimizar el código legacy",
    "actualizar las librerías del proyecto",
    "mejorar el flujo de checkout",
    "optimizar el proceso de registro",
    "actualizar el sistema de permisos",
    "mejorar la gestión de usuarios",
    "optimizar el almacenamiento de datos",
    "actualizar la arquitectura del sistema",
    "mejorar los tiempos de respuesta",
    "optimizar el uso de recursos",
    "actualizar el diseño responsive",
    "mejorar la accesibilidad",
    "ampliar funcionalidades del CRM",
    "extender el módulo de ventas",
    "expandir capacidad del sistema",
    "aumentar límites de almacenamiento",
    "agregar más opciones de configuración",
    "implementar nuevas métricas",
    "añadir más filtros de búsqueda",
    "desarrollar nuevas integraciones",
    "crear versión enterprise",
    "implementar modo offline",
    "agregar exportación a más formatos",
    "desarrollar API pública",
    "implementar webhooks",
    "añadir customización avanzada",
    "desarrollar marketplace de plugins",
    "implementar sistema de roles avanzado",
    "agregar analytics predictivo",
    "desarrollar módulo de BI",
    "implementar automatizaciones",
    "añadir inteligencia artificial",
    "personalizar el logo y colores",
    "customizar reportes corporativos",
    "adaptar interfaz a marca",
    "configurar flujos personalizados",
    "ajustar campos del formulario",
    "personalizar emails automáticos",
    "customizar dashboard principal",
    "adaptar nomenclaturas",
    "configurar reglas de negocio",
    "personalizar permisos por rol",
    "ajustar plantillas de documentos",
    "customizar notificaciones",
    "adaptar flujo de aprobaciones",
    "configurar integraciones específicas",
    "personalizar métricas de KPI",
    "necesitamos capacitación del equipo",
    "solicitud de training avanzado",
    "requerimos documentación técnica",
    "crear guías de usuario",
    "desarrollar tutoriales interactivos",
    "implementar sistema de ayuda contextual",
    "agregar tooltips explicativos",
    "crear videos demostrativos",
    "desarrollar centro de ayuda",
    "implementar onboarding interactivo",
    "error al validar formularios",
    "bug en la paginación",
    "problema con las sesiones",
    "falla el autocompletado",
    "error en el drag and drop",
    "bug con las fechas",
    "problema al subir archivos",
    "error en el calendario",
    "falla la validación de campos",
    "bug en el selector de color",
    "problema con los checkboxes",
    "error al ordenar columnas",
    "falla el modal de confirmación",
    "bug en el menú desplegable",
    "problema con los tooltips",
    "error en las notificaciones toast",
    "falla el infinite scroll",
    "bug en el lazy loading",
    "problema con el cache",
    "error en el local storage",
    "implementar sistema de comentarios",
    "agregar versionamiento de documentos",
    "desarrollar módulo de colaboración",
    "implementar firma digital",
    "agregar geolocalización",
    "desarrollar sistema de reservas",
    "implementar calendario compartido",
    "agregar sistema de calificaciones",
    "desarrollar módulo de encuestas",
    "implementar gamificación",
    "agregar badges y logros",
    "desarrollar sistema de referidos",
    "implementar programa de lealtad",
    "agregar marketplace interno",
    "desarrollar sistema de subastas",
    "implementar chat grupal",
    "agregar videollamadas",
    "desarrollar pizarra colaborativa",
    "implementar gestión de proyectos",
    "agregar timesheet automático"
]

labels = [
    # CORRECTIVO: 100 ejemplos (0)
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 10
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 20
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 30
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 40
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 50
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 60
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 70
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 80
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 90
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 100
    
    # EVOLUTIVO: 100 ejemplos (1)
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 10
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 20
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 30
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 40
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 50
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 60
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 70
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 80
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 90
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 100
]


# Vectorización con mejores parámetros
vectorizer = TfidfVectorizer(
    max_features=100,  # 100 features es suficiente para este vocabulario
    ngram_range=(1, 2),  # Unigramas y bigramas
    lowercase=True,
    strip_accents='unicode'
)
X = vectorizer.fit_transform(texts).toarray()
y = np.array(labels)

# Dividir datos: 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y  # stratify mantiene balance
)

print(f"📊 Dataset dividido:")
print(f"   Training: {len(X_train)} ejemplos")
print(f"   Testing: {len(X_test)} ejemplos")
print(f"   Features: {X.shape[1]}")

# Modelo MLP optimizado para 200 ejemplos
model = models.Sequential([
    layers.Dense(32, activation='relu', input_shape=(X.shape[1],)),
    layers.Dropout(0.3),
    layers.Dense(16, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy', 'Precision', 'Recall']
)

# EARLY STOPPING - Se detiene cuando deja de mejorar
early_stop = EarlyStopping(
    monitor='val_loss',        # Monitorear pérdida en validación
    patience=10,               # Esperar 10 épocas sin mejora
    restore_best_weights=True, # Restaurar los mejores pesos
    verbose=1
)

# Entrenar con early stopping
history = model.fit(
    X_train, y_train,
    epochs=50,                    # Máximo 50, pero se detendrá antes
    batch_size=8,                 # Batch size mayor para 200 ejemplos
    validation_data=(X_test, y_test),
    callbacks=[early_stop],       # Activar early stopping
    verbose=1
)

# Evaluar modelo
loss, accuracy, precision, recall = model.evaluate(X_test, y_test, verbose=0)

# Guardar modelo y vectorizador
model.save('models/mantenimiento_classifier.keras')
with open('models/vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

# Función de predicción
def classify_mantenimiento(text: str):
    """
    Predice si un ticket es Correctivo o Evolutivo
    """
    X_test = vectorizer.transform([text]).toarray()
    pred = model.predict(X_test, verbose=0)[0][0]
    
    confidence = pred if pred > 0.5 else (1 - pred)
    
    return {
        "class": "Evolutivo" if pred > 0.5 else "Correctivo",
        "probability": float(pred),
        "confidence": float(confidence)
    }
