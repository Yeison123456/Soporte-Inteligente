def rule_engine(churn_score: int, sentiment: float):
    """
    Motor de reglas mejorado con 6 niveles de riesgo.
    Devuelve un nivel de riesgo y recomendaciones accionables.
    """

    # --- EMERGENCIA (95+) ---
    if churn_score >= 95:
        return {
            "level": "EMERGENCIA",
            "message": (
                "Riesgo de pérdida inminente. Acciones inmediatas:\n"
                "Contactar al cliente por teléfono en menos de 30 minutos.\n"
                "Escalar a VP/Director + asignar ingeniero dedicado 24/7.\n"
                "Ofrecer compensación: 20-30% descuento o créditos de servicio.\n"
                "Reunión presencial/virtual con stakeholders en máximo 12 horas.\n"
                "Pausar facturación hasta resolver la situación crítica."
            )
        }

    # --- CRÍTICO (85-94) ---
    if churn_score >= 85 or (churn_score >= 75 and sentiment < 0):
        return {
            "level": "CRÍTICO",
            "message": (
                "Riesgo extremo de pérdida. Acciones recomendadas:\n"
                "Contactar al cliente en menos de 1 hora.\n"
                "Escalar al Director de Cuenta + CSM Senior.\n"
                "Ofrecer plan de retención (15-20% descuento o upgrade temporal gratuito).\n"
                "Programar reunión estratégica en las próximas 24 horas.\n"
                "Priorizar TODOS los tickets del cliente como urgentes."
            )
        }

    # --- ALTO (70-84) ---
    if churn_score >= 70 or (churn_score >= 60 and sentiment < 0):
        return {
            "level": "ALTO",
            "message": (
                "Riesgo alto. Acciones recomendadas:\n"
                "Asignar ingeniero senior dedicado.\n"
                "Reducir SLA de respuesta a 4 horas máximo.\n"
                "Llamada de seguimiento cada 3 días.\n"
                "Validar satisfacción tras cada ticket cerrado.\n"
                "Ofrecer diagnóstico técnico sin costo."
            )
        }

    # --- MEDIO-ALTO (50-69) ---
    if churn_score >= 50:
        return {
            "level": "MEDIO-ALTO",
            "message": (
                "Riesgo considerable. Acciones sugeridas:\n"
                "Llamada proactiva del CSM en las próximas 48 horas.\n"
                "Revisar historial de tickets (últimos 90 días).\n"
                "Mejorar comunicación: updates cada ticket sin esperar cierre.\n"
                "Ofrecer capacitación específica sobre áreas problemáticas.\n"
                "Programar check-in semanal durante el próximo mes."
            )
        }

    # --- MEDIO (30-49) ---
    if churn_score >= 30 or sentiment < 0:
        return {
            "level": "MEDIO",
            "message": (
                "Riesgo moderado. Acciones sugeridas:\n"
                "Revisar historial de tickets para detectar patrones.\n"
                "Email personalizado del CSM (no automatizado).\n"
                "Preguntar directamente: '¿Qué podríamos mejorar?'.\n"
                "Enviar best practices personalizadas.\n"
                "Programar Quarterly Business Review (QBR)."
            )
        }

    # --- BAJO (15-29) ---
    if churn_score >= 15:
        return {
            "level": "BAJO",
            "message": (
                "Riesgo bajo. Acciones estándar:\n"
                "Mantener monitoreo rutinario de métricas.\n"
                "Responder tickets en SLA normal (12-24h).\n"
                "Check-in trimestral estándar.\n"
                "Enviar newsletter mensual con novedades.\n"
                "Explorar oportunidades de upsell/cross-sell."
            )
        }

    # --- ÓPTIMO (0-14) ---
    return {
        "level": "ÓPTIMO",
        "message": (
            "Cliente saludable. Acciones de crecimiento:\n"
            "Solicitar testimonial o caso de éxito.\n"
            "Invitar a programa de referidos o customer advisory board.\n"
            "Ofrecer acceso anticipado a nuevas funcionalidades.\n"
            "Realizar encuesta NPS cada 120 días.\n"
            "Celebrar renovaciones y expansiones del contrato."
        )
    }
