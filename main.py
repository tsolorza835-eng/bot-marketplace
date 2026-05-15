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

    anios = re.findall(r"\b(19\d{2}|20\d{2})\b", titulo)
    anio_detectado = None
    if anios:
        try:
            anio_detectado = int(anios[0])
        except:
            pass

    if anio_detectado and anio_detectado >= anio_minimo:
        puntaje += 20

    marcas = ["toyota", "honda", "mazda", "hyundai", "kia", "nissan", "subaru", "suzuki", "chevrolet"]
    if any(marca in titulo_lower for marca in marcas):
        puntaje += 10

    if puntaje >= 90:
        categoria = "Excelente oportunidad"
    elif puntaje >= 80:
        categoria = "Muy buena oportunidad"
    elif puntaje >= 60:
        categoria = "Oportunidad moderada"
    else:
        categoria = "Poco atractiva"

    return puntaje, categoria


def extraer_datos_publicacion(page):
    """Extrae título y precio de una página de publicación de Marketplace."""
    titulo = ""
    precio = ""

    # Intentar extraer título
    selectores_titulo = [
        "h1",
        "[data-testid='marketplace-pdp-title']",
        "span[class*='x1lliihq']",
    ]
    for sel in selectores_titulo:
        try:
            el = page.locator(sel).first
            if el.count() > 0:
                texto = el.inner_text(timeout=3000).strip()
                if texto and len(texto) > 3:
                    titulo = texto
                    break
        except:
            pass

    # Intentar extraer precio
    selectores_precio = [
        "[data-testid='marketplace-pdp-price']",
        "span:has-text('$')",
        "div:has-text('$'):not(:has(*))",  # texto directo con $
    ]
    for sel in selectores_precio:
        try:
            el = page.locator(sel).first
            if el.count() > 0:
                texto = el.inner_text(timeout=3000).strip()
                if "$" in texto or any(c.isdigit() for c in texto):
                    precio = texto
                    break
        except:
            pass

    # Fallback: buscar precio en el texto completo de la página
    if not precio:
        try:
            contenido = page.content()
            match = re.search(r'\$\s?[\d\.,]+', contenido)
            if match:
                precio = match.group(0)
        except:
            pass

    return titulo, precio


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
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])

            # Cargar sesión si existe
            try:
                context = browser.new_context(storage_state="mi_sesion.json")
                print("Sesión cargada correctamente.")
            except Exception:
                context = browser.new_context()
                print("No se pudo cargar mi_sesion.json. Continuando sin sesión.")

            page = context.new_page()
            page.goto(url_busqueda, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(8000)

            # Scroll para cargar más resultados
            for _ in range(10):
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(2000)

            # Recolectar URLs únicas
            enlaces = page.locator(
                "a[href*='/marketplace/item/'], "
                "a[href*='facebook.com/marketplace/item/']"
            )
            total = enlaces.count()
            print(f"Enlaces detectados: {total}")

            urls_unicas = []
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
                            urls_unicas.append(href)
                except:
                    pass

            print(f"URLs únicas encontradas: {len(urls_unicas)}")

            # Analizar publicaciones
            for url in urls_unicas[:max_resultados]:  # limita la cantidad a analizar
                try:
                    print(f"Analizando: {url}")

                    detalle = context.new_page()
                    detalle.goto(url, wait_until="networkidle", timeout=60000)
                    detalle.wait_for_timeout(5000)

                    titulo, precio = extraer_datos_publicacion(detalle)

                    if not titulo or not precio:
                        detalle.close()
                        continue

                    precio_num = extraer_precio_num(precio)

                    # Filtrar por precio
                    if not (precio_minimo <= precio_num <= precio_maximo):
                        detalle.close()
                        continue

                    # Evaluar oportunidad
                    puntaje, categoria = evaluar_oportunidad(
                        titulo,
                        precio,
                        anio_minimo=anio_minimo,
                    )

                    # Filtrar por puntaje
                    if puntaje < puntaje_minimo:
                        detalle.close()
                        continue

                    oportunidades.append({
                        "titulo": titulo,
                        "precio": precio,
                        "puntaje": puntaje,
                        "categoria": categoria,
                        "url": url,
                    })

                    print(f"Agregada: {titulo} | {precio} | Puntaje {puntaje}")

                    detalle.close()

                except Exception as e:
                    print(f"Error analizando publicación: {e}")

            print(f"Oportunidades encontradas: {len(oportunidades)}")

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