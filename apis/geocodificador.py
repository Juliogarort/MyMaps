"""
apis/geocodificador.py

Convierte direcciones o nombres de lugares en coordenadas
usando Nominatim (OpenStreetMap). Sin API key necesaria.

Limitado geográficamente a la provincia de Sevilla.
Acepta tanto direcciones como nombres de lugares
(ej: "Ilerna Sevilla", "Estadio Ramón Sánchez Pizjuán")
"""

import httpx
import time

URL_NOMINATIM = "https://nominatim.openstreetmap.org/search"

CABECERAS = {
    "User-Agent": "MyMaps-TSP-Sevilla/1.0"
}

# Límites geográficos de la provincia de Sevilla
LIMITES_SEVILLA = {
    "lat_min": 36.9,
    "lat_max": 38.1,
    "lng_min": -6.6,
    "lng_max": -4.9,
}


def _esta_en_sevilla(lat: float, lng: float) -> bool:
    """Comprueba que las coordenadas están dentro de la provincia de Sevilla."""
    return (
        LIMITES_SEVILLA["lat_min"] <= lat <= LIMITES_SEVILLA["lat_max"] and
        LIMITES_SEVILLA["lng_min"] <= lng <= LIMITES_SEVILLA["lng_max"]
    )


def buscar_direccion(texto: str) -> list:
    """
    Busca una dirección o nombre de lugar en Sevilla.
    Acepta direcciones postales y nombres de sitios conocidos.

    Ejemplos válidos:
        - "Calle Sierpes 10"
        - "Plaza de España"
        - "Ilerna Sevilla"
        - "Hospital Virgen del Rocío"
        - "Centro Comercial Los Arcos"

    Devuelve lista de resultados dentro de la provincia de Sevilla.
    """
    if "sevilla" not in texto.lower():
        texto_busqueda = f"{texto}, Sevilla"
    else:
        texto_busqueda = texto

    try:
        respuesta = httpx.get(
            URL_NOMINATIM,
            params={
                "q":              texto_busqueda,
                "format":         "json",
                "countrycodes":   "es",
                "limit":          10,
                "addressdetails": 1,
            },
            headers=CABECERAS,
            timeout=8.0
        )
        respuesta.raise_for_status()
        datos = respuesta.json()

        resultados = []
        for item in datos:
            lat = float(item["lat"])
            lng = float(item["lon"])
            if _esta_en_sevilla(lat, lng):
                resultados.append({
                    "nombre": item.get("display_name", ""),
                    "lat":    lat,
                    "lng":    lng
                })

        time.sleep(1)
        return resultados

    except Exception as e:
        print(f"[Geocodificador] ❌ Error: {e}")
        return []


def direccion_a_coordenadas(texto: str) -> dict | None:
    """
    Convierte una dirección o nombre de lugar a coordenadas.
    Solo devuelve resultados dentro de la provincia de Sevilla.
    """
    resultados = buscar_direccion(texto)

    if not resultados:
        print(f"[Geocodificador] ⚠️  No encontrado en Sevilla: {texto}")
        return None

    return resultados[0]