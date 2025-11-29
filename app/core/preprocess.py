# Funciones comunes de preprocesamiento: limpieza básica, detección de URLs, conteo de urgencia, etc.
import re
from typing import Dict, Any

URL_REGEX = re.compile(r"https?://[^\s]+", re.IGNORECASE)
SHORTENER_DOMAINS = ["bit.ly", "tinyurl.com", "t.co", "goo.gl"]

URGENT_KEYWORDS = [
    "urgente", "inmediato", "por favor", "lo antes posible",
    "critical", "critico", "no funciona", "caído", "down"
]

NEGATIVE_KEYWORDS = [
    "frustrado", "enojado", "mal", "malo", "hate", "odio", "decepcionado"
]

POSITIVE_KEYWORDS = ["gracias", "perfecto", "excelente", "bien"]

def clean_text(text: str) -> str:
    """Limpieza simple: eliminar múltiples espacios, tags HTML, trim."""
    if not text:
        return ""
    t = re.sub(r"<[^>]+>", " ", text)            # quitar HTML simple
    t = re.sub(r"\s+", " ", t)                   # normalizar espacios
    return t.strip()

def contains_shortener(text: str) -> bool:
    """Detecta si el texto contiene un enlace con dominio acortador."""
    for m in URL_REGEX.findall(text):
        domain = m.split("//")[-1].split("/")[0].lower()
        for s in SHORTENER_DOMAINS:
            if s in domain:
                return True
    return False

def count_keywords(text: str, keywords:list) -> int:
    low = text.lower()
    return sum(1 for k in keywords if k in low)

def text_signals(text: str) -> Dict[str, Any]:
    """
    Extrae señales simples del texto: num_urls, has_shortener, urgent_count,
    negative_count, positive_count, length.
    """
    t = clean_text(text)
    urls = URL_REGEX.findall(t)
    return {
        "clean_text": t,
        "num_urls": len(urls),
        "has_shortener": contains_shortener(t),
        "urgent_count": count_keywords(t, URGENT_KEYWORDS),
        "negative_count": count_keywords(t, NEGATIVE_KEYWORDS),
        "positive_count": count_keywords(t, POSITIVE_KEYWORDS),
        "length": len(t)
    }
