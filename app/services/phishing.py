# heurística para detectar phishing: URLs sospechosas, solicitudes de credenciales, amenazas
from typing import Tuple
from app.core.preprocess import URL_REGEX, clean_text, contains_shortener

BLACKLIST_DOMAINS = {"suspicious.example", "malicious.test", "phish.test"}
SUSPICIOUS_PHRASES = [
    "hacer clic", "hac clic", "ingresar su", "ingrese sus", "verifique su cuenta",
    "renew immediately", "renew your", "su cuenta ha caducado", "please confirm"
]

def detect_phishing(text: str) -> Tuple[bool, dict]:
    """
    Devuelve (is_phishing, reasons_dict)
    reasons_dict incluye evidencias (urls, has_shortener, suspicious_phrases)
    """
    t = clean_text(text).lower()
    reasons = {"urls_blacklisted": [], "has_shortener": False, "suspicious_phrases": []}

    # buscar URLs y dominios en blacklist
    urls = URL_REGEX.findall(t)
    for u in urls:
        domain = u.split("//")[-1].split("/")[0]
        for bad in BLACKLIST_DOMAINS:
            if bad in domain:
                reasons["urls_blacklisted"].append(domain)

    # shortener check
    reasons["has_shortener"] = contains_shortener(t)

    # suspicious phrases
    for p in SUSPICIOUS_PHRASES:
        if p in t:
            reasons["suspicious_phrases"].append(p)

    # Heurística final: si hay dominio malicioso, o shortener + request credentials/urgency => phishing
    is_phish = False
    if reasons["urls_blacklisted"]:
        is_phish = True
    elif reasons["has_shortener"] and any(kw in t for kw in ["credencial","contraseña","ingresar","usuario","pass"]):
        is_phish = True
    elif reasons["suspicious_phrases"] and any(kw in t for kw in ["credencial","contraseña","ingresar","usuario","datos"]):
        is_phish = True

    return is_phish, reasons
