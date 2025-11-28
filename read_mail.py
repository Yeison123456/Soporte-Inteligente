# leer_correos.py
import asyncio
from app.services.gmail.receive import leer_correos_y_crear_tickets

async def main():
    while True:
        try:
            print("🔄 Revisando correos...")
            leer_correos_y_crear_tickets()  # tu función que lee Gmail y crea tickets
            print("✅ Revisión de correos completada")
        except Exception as e:
            print("❌ Error al revisar correos:", e)
        await asyncio.sleep(120)  # revisar cada 60 segundos

if __name__ == "__main__":
    asyncio.run(main())
