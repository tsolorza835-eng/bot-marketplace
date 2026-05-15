    partes = update.message.text.split()

    # Formato esperado:
    # Marca Modelo Año PrecioMin PrecioMax [PuntajeMinimo]
    # El puntaje es opcional y por defecto será 40.
    if len(partes) < 5:
        await update.message.reply_text(
            "Formato incorrecto. Usa: Marca Modelo Año PrecioMin PrecioMax [PuntajeMinimo]"
        )
        return

    try:
        # Los últimos 3 parámetros son obligatorios
        anio_minimo = int(partes[-3])
        precio_minimo = int(partes[-2])
        precio_maximo = int(partes[-1])

        # Por defecto, el puntaje mínimo será 40
        puntaje_minimo = 40

        # La búsqueda corresponde a todo lo anterior
        busqueda = " ".join(partes[:-3])

        # Si el último parámetro adicional existe y es numérico,
        # interpretar el formato con puntaje opcional:
        # Marca Modelo Año PrecioMin PrecioMax PuntajeMinimo
        if len(partes) >= 6:
            try:
                puntaje_minimo = int(partes[-1])
                precio_maximo = int(partes[-2])
                precio_minimo = int(partes[-3])
                anio_minimo = int(partes[-4])
                busqueda = " ".join(partes[:-4])
            except ValueError:
                # Si no se puede interpretar así, se mantiene el formato sin puntaje.
                pass

    except ValueError:
        await update.message.reply_text(
            "Los parámetros numéricos deben ser válidos."
        )
        return