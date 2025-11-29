import re

# ============================
# PATRONES DE DETECCIÓN
# ============================

# 1. Correos electrónicos
EMAIL_RE = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b')

# 2. Teléfonos (opcional)
PHONE_RE = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')

# 3. Credenciales explícitas (formato key:value o key=value)
# Ejemplos: user:admin, password=123, usuario: pepe
CRED_EXPLICIT = re.compile(
    r'(?i)\b(user|usuario|username|login|password|pass|pwd|contraseña|clave|passcode|pin)\s*[:=]\s*(\S+)',
    re.IGNORECASE
)

# 4. Credenciales con "es" o "son"
# Ejemplos: "mi usuario es admin", "la contraseña es 123"
CRED_ES_PATTERN = re.compile(
    r'(?i)\b(usuario|contraseña|clave|password|pass)\s+es\s+(\S+)',
    re.IGNORECASE
)

# 5. Patrón para "credenciales son X y Y"
# Ejemplos: "mis credenciales son user@email.com y Pass123"
CREDENTIALS_PATTERN = re.compile(
    r'(?i)credenciales\s+son\s+(\S+)\s+y\s+(\S+)',
    re.IGNORECASE
)

# 6. Números de tarjeta de crédito (opcional)
CC_PATTERN = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')


def anonimizar_texto(texto: str) -> str:
    """
    Anonimiza información sensible en el texto
    """
    anon = texto
    replacements = []  # Para debug

    # ============================
    # 1. CORREOS ELECTRÓNICOS
    # ============================
    correos = EMAIL_RE.findall(anon)
    for i, mail in enumerate(correos, start=1):
        placeholder = f"<email{i}>"
        anon = anon.replace(mail, placeholder)
        replacements.append(f"{mail} → {placeholder}")

    # ============================
    # 2. PATRÓN "credenciales son X y Y"
    # ============================
    for match in CREDENTIALS_PATTERN.finditer(texto):
        user_val = match.group(1)
        pass_val = match.group(2)
        
        # Solo reemplazar si NO son correos (ya anonimizados)
        if '@' not in user_val and '<email' not in user_val:
            placeholder = f"<usuario1>"
            anon = anon.replace(user_val, placeholder)
            replacements.append(f"{user_val} → {placeholder}")
        
        if '@' not in pass_val and '<email' not in pass_val:
            placeholder = f"<password1>"
            anon = anon.replace(pass_val, placeholder)
            replacements.append(f"{pass_val} → {placeholder}")

    # ============================
    # 3. CREDENCIALES EXPLÍCITAS (key:value)
    # ============================
    user_count = 1
    pass_count = 1
    
    for match in CRED_EXPLICIT.finditer(texto):
        key = match.group(1).lower()
        value = match.group(2)
        
        # Saltar si ya fue anonimizado
        if '<' in value or '>' in value:
            continue
            
        if key in ['user', 'usuario', 'username', 'login']:
            placeholder = f"<usuario{user_count}>"
            anon = anon.replace(value, placeholder)
            replacements.append(f"{value} → {placeholder}")
            user_count += 1
        elif key in ['password', 'pass', 'pwd', 'contraseña', 'clave', 'passcode', 'pin']:
            placeholder = f"<password{pass_count}>"
            anon = anon.replace(value, placeholder)
            replacements.append(f"{value} → {placeholder}")
            pass_count += 1

    # ============================
    # 4. CREDENCIALES CON "ES"
    # ============================
    for match in CRED_ES_PATTERN.finditer(texto):
        key = match.group(1).lower()
        value = match.group(2)
        
        # Saltar si ya fue anonimizado
        if '<' in value or '>' in value:
            continue
            
        if key in ['usuario']:
            placeholder = f"<usuario{user_count}>"
            anon = anon.replace(value, placeholder)
            replacements.append(f"{value} → {placeholder}")
            user_count += 1
        elif key in ['contraseña', 'clave', 'password', 'pass']:
            placeholder = f"<password{pass_count}>"
            anon = anon.replace(value, placeholder)
            replacements.append(f"{value} → {placeholder}")
            pass_count += 1

    # ============================
    # 5. TELÉFONOS (opcional)
    # ============================
    telefonos = PHONE_RE.findall(anon)
    for i, phone in enumerate(telefonos, start=1):
        placeholder = f"<telefono{i}>"
        anon = anon.replace(phone, placeholder)
        replacements.append(f"{phone} → {placeholder}")

    # ============================
    # 6. TARJETAS DE CRÉDITO (opcional)
    # ============================
    tarjetas = CC_PATTERN.findall(anon)
    for i, cc in enumerate(tarjetas, start=1):
        placeholder = f"<tarjeta{i}>"
        anon = anon.replace(cc, placeholder)
        replacements.append(f"{cc} → {placeholder}")

    # Debug: imprimir reemplazos
    if replacements:
        print("🔒 Anonimizaciones realizadas:")
        for r in replacements:
            print(f"   {r}")

    return anon