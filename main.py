from playwright.sync_api import sync_playwright
from urllib.parse import quote


def evaluar_oportunidad(titulo, precio, anio_minimo=2010):
    puntaje = 0
    titulo_lower = titulo.lower()

    # Extraer precio numérico
    precio_num = 0
    try:
        solo_numeros = ''.join(c for c in precio if c.isdigit())
        if solo_numeros:
            precio_num = int(solo_numeros)
    except Exception:
        pass

    # Precio atractivo
    if 0 < precio_num <= 12000000:
        puntaje += 40

    # Detectar año en el título
    anio_detectado = None
    for anio in range(1990, 2031):
        if str(anio) in titulo:
            anio_detectado = anio
            break

    if anio_detectado and anio_detectado >= anio_minimo:
        puntaje += 30

    # Marcas con alta demanda
    marcas = ["toyota", "honda", "mazda", "hyundai", "kia", "subaru"]
    if any(marca in titulo_lower for marca in marcas):
        puntaje += 10

    # Clasificación
    if puntaje >= 90:
        categoria = "Excelente oportunidad"
    elif puntaje >= 80:
        categoria = "Muy buena oportunidad"
    elif puntaje >= 60:
        categoria = "Oportunidad moderada"
    else:
        categoria = "Poco atractiva"

    return puntaje, categoria


def buscar_oportunidades(
    busqueda,
    anio_minimo=2010,
    precio_minimo=0,
    precio_maximo=999999999,
    puntaje_minimo=80,
    max_resultados=5,
    max_publicaciones=20,
):
    def extraer_precio_num(precio_texto):
        try:
            solo_numeros = ''.join(c for c in precio_texto if c.isdigit())
            if solo_numeros:
                return int(solo_numeros)
        except Exception:
            pass
        return 0

    oportunidades = []

    url_busqueda = (
        "https://www.facebook.com/marketplace/concepcion/vehicles"
        f"?query={quote(busqueda)}"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="mi_sesion.json")
        page = context.new_page()

        print(f"Abriendo búsqueda: {busqueda}")
        page.goto(url_busqueda, wait_until="networkidle")
        page.wait_for_timeout(8000)

        # Esperar explícitamente a que aparezcan enlaces de Marketplace (si cargan)
        try:
            page.wait_for_selector("a[href*='/marketplace/item/']", timeout=10000)
        except Exception:
            print("No aparecieron enlaces inmediatamente; continuando con scroll.")

        # Scroll para cargar más resultados
        for _ in range(10):
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(2000)

        # Obtener enlaces únicos
        enlaces = page.locator(
            "a[href*='/marketplace/item/'], "
            "a[href*='facebook.com/marketplace/item/']"
        )
        total = enlaces.count()

        resultados = []
        vistos = set()

        for i in range(total):
            try:
                href = enlaces.nth(i).get_attribute("href")
                if href:
                    if href.startswith("/"):
                        href = "https://www.facebook.com" + href
                    href = href.split("?")[0]

                    if href not in vistos:
                        vistos.add(href)
                        resultados.append(href)
            except Exception:
                pass

        print(f"Se encontraron {len(resultados)} publicaciones.")

        # Analizar publicaciones
        for url in resultados[:max_publicaciones]:
            if len(oportunidades) >= max_resultados:
                break

            try:
                detalle = context.new_page()
                detalle.goto(url)
                detalle.wait_for_timeout(3000)

                # Título
                try:
                    titulo = detalle.locator("h1").first.inner_text().strip()
                except Exception:
                    titulo = "Título no encontrado"

                # Precio
                precio = "No encontrado"
                try:
                    textos = detalle.locator("span").all_inner_texts()
                    for texto in textos:
                        if "$" in texto:
                            precio = texto.strip()
                            break
                except Exception:
                    pass

                puntaje, categoria = evaluar_oportunidad(
                    titulo,
                    precio,
                    anio_minimo=anio_minimo,
                )

                precio_num = extraer_precio_num(precio)

                # Agregar siempre la publicación para pruebas
                oportunidades.append({
                    "titulo": titulo,
                    "precio": precio,
                    "puntaje": puntaje,
                    "categoria": categoria,
                    "url": url,
                })

                detalle.close()

            except Exception as e:
                print(f"Error analizando {url}: {e}")

        browser.close()

    return oportunidades


if __name__ == "__main__":
    print("Este archivo es el motor de búsqueda.")
    print("Para usar el bot, ejecuta: python3 telegram_bot.py")