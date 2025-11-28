import re

# Correos
EMAIL_RE = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

# Palabras que indican credenciales de usuario
USER_KEYWORDS = r"(user|usuario|username|login)"
PASS_KEYWORDS = r"(Pass|pass|password|pwd|contraseña|clave|passcode|pin)"

# Formas posibles: user: xx | user = xx | user xx | usuario es xx
USER_PATTERN = re.compile(
    rf"(?i)\b{USER_KEYWORDS}\b(?:\s*(?:=|:)\s*|\s+es\s+|\s+)\S+"
)

PASS_PATTERN = re.compile(
    rf"(?i)\b{PASS_KEYWORDS}\b(?:\s*(?:=|:)\s*|\s+es\s+|\s+)\S+"
)

# Captura combinaciones como "user admin pass 123"
CRED_COMBINED_PATTERN = re.compile(
    rf"(?i)({USER_KEYWORDS}|{PASS_KEYWORDS})\s*\S*"
)


def anonimizar_texto(texto: str) -> str:
    anon = texto

    # ============================
    # 1. Reemplazar correos
    # ============================
    correos = EMAIL_RE.findall(anon)
    for i, mail in enumerate(correos, start=1):
        anon = anon.replace(mail, f"<correo{i}>")

    # ============================
    # 2. Reemplazar usuarios
    # ============================
    usuarios = USER_PATTERN.findall(anon)
    count_user = 0

    for match in USER_PATTERN.finditer(anon):
        segmento = match.group()
        count_user += 1

        # extraer valor real (lo que está después de user...)
        partes = segmento.split()
        if len(partes) > 1:
            valor = partes[-1]
        else:
            valor = segmento.split(":")[-1].replace("=", "").strip()

        anon = anon.replace(valor, f"<usuario{count_user}>")

    # ============================
    # 3. Reemplazar contraseñas
    # ============================
    claves = PASS_PATTERN.findall(anon)
    count_pass = 0

    for match in PASS_PATTERN.finditer(anon):
        segmento = match.group()
        count_pass += 1

        partes = segmento.split()
        if len(partes) > 1:
            valor = partes[-1]
        else:
            valor = segmento.split(":")[-1].replace("=", "").strip()

        anon = anon.replace(valor, f"<password{count_pass}>")

    # ============================
    # 4. Extra: limpiado adicional
    # detecta credenciales sin formato estándar
    # ============================

    # Ej: "mi usuario es admin123" → reemplazar admin123
    extra_user = re.compile(rf"(?i)usuario\s+es\s+(\S+)")
    for i, val in enumerate(extra_user.findall(anon), start=1):
        anon = anon.replace(val, f"<usuario_extra{i}>")

    extra_pass = re.compile(rf"(?i)(contraseña|clave)\s+es\s+(\S+)")
    for i, val in enumerate(extra_pass.findall(anon), start=1):
        real = val[1]
        anon = anon.replace(real, f"<password_extra{i}>")

    return anon
