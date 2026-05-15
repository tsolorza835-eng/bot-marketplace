import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from main import buscar_oportunidades

TOKEN = os.getenv("TELEGRAM_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚗 Envíame: Marca Modelo Año PrecioMin PrecioMax [PuntajeMinimo]\n"
        "Ejemplo:\n"
        "Toyota Yaris 2010 1000000 9000000\n"
        "o\n"
        "Toyota Yaris 2010 1000000 9000000 70"
    )


async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    partes = texto.split()

    # Formato mínimo:
    # Marca Modelo Año PrecioMin PrecioMax
    if len(partes) < 5:
        await update.message.reply_text(
            "Formato incorrecto.\n"
            "Usa: Marca Modelo Año PrecioMin PrecioMax [PuntajeMinimo]"
        )
        return

    try:
        # Intentar primero con puntaje opcional
        puntaje_minimo = 40

        if len(partes) >= 6:
            try:
                puntaje_minimo = int(partes[-1])
                precio_maximo = int(partes[-2])
                precio_minimo = int(partes[-3])
                anio_minimo = int(partes[-4])
                busqueda = " ".join(partes[:-4])
            except ValueError:
                # Si falla, interpretar sin puntaje
                anio_minimo = int(partes[-3])
                precio_minimo = int(partes[-2])
                precio_maximo = int(partes[-1])
                busqueda = " ".join(partes[:-3])
        else:
            anio_minimo = int(partes[-3])
            precio_minimo = int(partes[-2])
            precio_maximo = int(partes[-1])
            busqueda = " ".join(partes[:-3])

    except ValueError:
        await update.message.reply_text(
            "Los parámetros numéricos deben ser válidos."
        )
        return

    await update.message.reply_text(
        f"🔍 Buscando oportunidades para: {busqueda}"
    )

    try:
        resultados = buscar_oportunidades(
            busqueda=busqueda,
            anio_minimo=anio_minimo,
            precio_minimo=precio_minimo,
            precio_maximo=precio_maximo,
            puntaje_minimo=puntaje_minimo,
            max_resultados=10,
        )

        if not resultados:
            await update.message.reply_text(
                "😕 No encontré oportunidades que cumplan tus criterios."
            )
            return

        for item in resultados[:10]:
            mensaje = (
                f"🚗 {item['titulo']}\n"
                f"💰 {item['precio']}\n"
                f"⭐ Puntaje: {item['puntaje']}\n"
                f"📊 {item['categoria']}\n"
                f"🔗 {item['url']}"
            )
            await update.message.reply_text(mensaje)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


def main():
    print("🤖 Bot de Telegram iniciado...")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))

    app.run_polling()


if __name__ == "__main__":
    main()