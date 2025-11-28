def rule_engine(churn_score: int, sentiment: str):
    """
    Motor de reglas mejorado, basado en prácticas reales de Customer Success.
    Devuelve un nivel de riesgo y recomendaciones accionables.
    """

    # --- CRÍTICO ---
    # Riesgo extremo: churn muy alto o sentimiento muy negativo + score alto
    if churn_score >= 85 or (churn_score >= 70 and sentiment == "Negativo"):
        return {
            "level": "CRITICO",
            "message": (
                "⚠ Riesgo extremo de pérdida. Acciones recomendadas:\n"
                "- Contactar al cliente en menos de 1 hora.\n"
                "- Escalar al Director de Cuenta.\n"
                "- Ofrecer plan de retención (10–20% descuento, horas adicionales o upgrade temporal).\n"
                "- Programar reunión estratégica en las próximas 24 horas.\n"
                "- Enviar resumen ejecutivo del estado del servicio y medidas inmediatas.\n"
                "- Priorizar TODOS los tickets del cliente como urgentes hasta estabilizar la relación."
            )
        }

    # --- ALTA ---
    # Riesgo alto pero controlable
    if churn_score >= 60:
        return {
            "level": "ALTA",
            "message": (
                "⚠ Riesgo alto. Acciones recomendadas:\n"
                "- Asignar un ingeniero senior dedicado.\n"
                "- Reducir tiempos de respuesta .\n"
                "- Llamada de seguimiento cada 3–5 días.\n"
                "- Validar satisfacción tras cada ticket cerrado.\n"
                "- Ofrecer mejora sin costo (optimización/diagnóstico preventivo)."
            )
        }

    # --- MEDIA ---
    # Riesgo moderado por mal sentimiento aunque el score sea medio
    if churn_score >= 40 or sentiment == "Negativo":
        return {
            "level": "MEDIA",
            "message": (
                "⚠ Riesgo moderado. Acciones sugeridas:\n"
                "- Revisar historial de tickets para detectar patrones.\n"
                "- Mejorar comunicación proactiva (correos de avance más frecuentes).\n"
                "- Preguntar directamente por puntos de insatisfacción.\n"
                "- Entregar recomendaciones preventivas personalizadas."
            )
        }

    # --- NORMAL ---
    return {
        "level": "NORMAL",
        "message": (
            "✔ Riesgo bajo. Acciones estándar:\n"
            "- Mantener monitoreo rutinario.\n"
            "- Responder tickets en SLA normal.\n"
            "- Ofrecer tips o buenas prácticas mensualmente.\n"
            "- Realizar encuesta NPS ligera cada 90 días."
        )
    }