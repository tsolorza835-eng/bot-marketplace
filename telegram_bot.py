import asyncio
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from main import buscar_oportunidades

# Cargar variables del archivo .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("No se encontró TELEGRAM_TOKEN en el archivo .env")


# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚗 Hola, soy Lucas Investiga Bot.\n\n"
        "Envíame una búsqueda con este formato:\n"
        "marca_o_modelo año precio_min precio_max puntaje\n\n"
        "Ejemplo:\n"
        "Mazda 3 2010 3.000.000 8.000.000 40"
    )


# Procesar mensajes normales
async def analizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    texto = update.message.text.strip()
    partes = texto.split()

    if len(partes) < 5:
        await update.message.reply_text(
            "❌ Formato incorrecto.\n\n"
            "Ejemplo:\n"
            "Mazda 3 2010 3.000.000 8.000.000 40"
        )
        return

    try:
        puntaje_minimo = int(partes[-1])
        precio_maximo = int(partes[-2].replace('.', ''))
        precio_minimo = int(partes[-3].replace('.', ''))
        anio_minimo = int(partes[-4])
        busqueda = " ".join(partes[:-4])
    except ValueError:
        await update.message.reply_text("❌ No pude interpretar los datos.")
        return

    await update.message.reply_text(
        f"🔍 Buscando oportunidades...\n\n"
        f"🚗 Búsqueda: {busqueda}\n"
        f"📅 Año mínimo: {anio_minimo}\n"
        f"💰 Precio mínimo: ${precio_minimo:,}\n"
        f"💰 Precio máximo: ${precio_maximo:,}\n"
        f"⭐ Puntaje mínimo: {puntaje_minimo}\n\n"
        f"⏳ Esto puede tardar algunos minutos."
    )

    try:
        oportunidades = await asyncio.to_thread(
            buscar_oportunidades,
            busqueda=busqueda,
            anio_minimo=anio_minimo,
            precio_minimo=precio_minimo,
            precio_maximo=precio_maximo,
            puntaje_minimo=puntaje_minimo,
            max_resultados=5,
        )

        if not oportunidades:
            await update.message.reply_text(
                "😕 No encontré oportunidades que cumplan tus criterios."
            )
            return

        for item in oportunidades:
            mensaje = (
                f"🚗 {item['titulo']}\n"
                f"💰 {item['precio']}\n"
                f"⭐ Puntaje: {item['puntaje']}\n"
                f"🏆 {item['categoria']}\n"
                f"🔗 {item['url']}"
            )
            await update.message.reply_text(mensaje)

        await update.message.reply_text(
            f"✅ Se enviaron {len(oportunidades)} oportunidades."
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Ocurrió un error durante la búsqueda:\n{e}"
        )


# Función principal
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analizar))

    print("🤖 Bot de Telegram iniciado...")
    # Ignorar mensajes antiguos pendientes para que el bot no procese
    # automáticamente la última búsqueda al iniciarse.
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()