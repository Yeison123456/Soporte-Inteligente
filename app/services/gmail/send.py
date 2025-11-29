import resend
from dotenv import load_dotenv
import os
load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

print(os.getenv('RESEND_API_KEY'))


def send_correo(to, subject, mensaje):
    r = resend.Emails.send({
      "from": "onboarding@resend.dev",
      "to": to,
      "subject": subject,
      "html": mensaje
    })
    return r
