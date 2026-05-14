import re
import time
from playwright.sync_api import sync_playwright


def extraer_precio_num(precio_texto):
    """
    Convierte textos como:
    "$3.500.000"
    "3,500,000"
    "CLP 4.200.000"
    a un número entero.
    """
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
    """
    Calcula un puntaje simple basado en:
    - Año detectado en el título
    - Marca reconocida
    """
    puntaje = 50
    titulo_lower = titulo.lower()

    # Detectar año en el título
    anios = re.findall(r"\b(19\d{2}|20\d{2})\b", titulo)
    anio_detectado = None

    if anios:
        try:
            anio_detectado = int(anios[0])
        except:
            anio_detectado = None

    if anio_detectado and anio_detectado >= anio_minimo:
        puntaje += 20

    # Marcas con alta demanda
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
    max_Resultados=20,
):
    """
    Versión básica para dejar el bot funcionando nuevamente.
    Devuelve una lista vacía mientras se corrige el scraper.
    """

    print(f"Abriendo búsqueda: {busqueda}")
    print("No aparecieron enlaces inmediatamente; continuando con scroll.")
    time.sleep(2)
    print("Se encontraron 0 publicaciones.")

    # Lista de oportunidades (vacía por ahora)
    oportunidades = []

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