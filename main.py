import re
import time
from urllib.parse import quote
from playwright.sync_api import sync_playwright


def extraer_precio_num(precio_texto):
    if not precio_texto:
        return 0

    numeros = re.sub(r"[^\d]", "", str(precio_texto))

    if not numeros:
        return 0

    try:
        return int(numeros)
    except:
        return 0


def evaluar_oportunidad(titulo, precio, anio_minimo=2010):
    puntaje = 50
    titulo_lower = titulo.lower()

    # Detectar año
    anios = re.findall(r"\b(19\d{2}|20\d{2})\b", titulo)
    anio_detectado = None

    if anios:
        try:
            anio_detectado = int(anios[0])
        except:
            pass

    if anio_detectado and anio_detectado >= anio_minimo:
        puntaje += 20

    # Marcas reconocidas
    marcas = [
        "toyota",
        "honda",
        "mazda",
        "hyundai",
        "kia",
        "nissan",
        "subaru",
        "suzuki",
        "chevrolet",
    ]

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
    puntaje_minimo=40,
    max_resultados=20,
):
    oportunidades = []

    url_busqueda = (
        "https://www.facebook.com/marketplace/concepcion/vehicles"
        f"?query={quote(busqueda)}"
    )

    print(f"Abriendo búsqueda: {busqueda}")
    print(f"URL: {url_busqueda}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox"]
            )

            context = browser.new_context()

            # Si existe la sesión guardada, intenta cargarla
            try:
                context = browser.new_context(storage_state="mi_sesion.json")
                print("Sesión cargada correctamente.")
            except Exception:
                print("No se pudo cargar mi_sesion.json. Continuando sin sesión.")

            page = context.new_page()

            page.goto(url_busqueda, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(8000)

            # Captura y HTML para diagnóstico
            page.screenshot(path="debug_marketplace.png", full_page=True)

            with open("debug_marketplace.html", "w", encoding="utf-8") as f:
                f.write(page.content())

            print("Archivos de diagnóstico creados.")
            print("No aparecieron enlaces inmediatamente; continuando con scroll.")

            # Scroll
            for _ in range(10):
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(2000)

            # Buscar enlaces de Marketplace
            enlaces = page.locator(
                "a[href*='/marketplace/item/'], "
                "a[href*='facebook.com/marketplace/item/']"
            )

            total = enlaces.count()
            print(f"Enlaces detectados por Playwright: {total}")

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

            # Por ahora, devolver lista vacía.
            # Cuando confirmemos que Facebook entrega enlaces,
            # agregaremos el análisis completo de cada publicación.

            browser.close()

    except Exception as e:
        print(f"Error en buscar_oportunidades: {e}")

    return oportunidades


if __name__ == "__main__":
    resultados = buscar_oportunidades(
        "Toyota Yaris",
        anio_minimo=2010,
        precio_minimo=1000000,
        precio_maximo=9000000,
        puntaje_minimo=40,
    )

    print(f"Resultados encontrados: {len(resultados)}")