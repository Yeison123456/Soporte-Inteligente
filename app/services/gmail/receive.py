import os
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.utils import parseaddr
import base64

# Scopes para leer y modificar etiquetas de los correos
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

API_CREATE_TICKET = "http://localhost:8000/api/tickets"

def leer_correos_y_crear_tickets():
    creds = None

    # Cargar token si existe
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Si no hay token válido, pedir login
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # Obtener mensajes no leídos
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
    messages = results.get('messages', [])

    print(f"Mensajes no leídos: {len(messages)}")

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data['payload']['headers']

        # Obtener remitente y asunto
        correo_cliente_raw = next((h['value'] for h in headers if h['name'] == 'From'), '')
        _, correo_cliente = parseaddr(correo_cliente_raw)
        titulo = next((h['value'] for h in headers if h['name'] == 'Subject'), '')

        # Obtener cuerpo (texto plano)
        cuerpo = ""
        if 'parts' in msg_data['payload']:
            for part in msg_data['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    cuerpo_bytes = base64.urlsafe_b64decode(part['body']['data'])
                    cuerpo = cuerpo_bytes.decode('utf-8')
                    break
        else:
            cuerpo_bytes = base64.urlsafe_b64decode(msg_data['payload']['body']['data'])
            cuerpo = cuerpo_bytes.decode('utf-8')

        print(f"Creando ticket: {titulo} de {correo_cliente}")

        # Crear ticket en API
        response = requests.post(API_CREATE_TICKET, json={
            "correo_cliente": correo_cliente,
            "titulo": titulo,
            "Descripcion_Caso": cuerpo,
        })
        print("API response:", response.status_code, response.text)

        # Marcar el correo como leído para no procesarlo otra vez
        service.users().messages().modify(
            userId='me',
            id=msg['id'],
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

    print("✅ Revisión de correos finalizada")
