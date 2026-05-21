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

    resultados = buscar_direccion(texto)

    if not resultados:
        print(f"[Geocodificador] ⚠️  No encontrado en Sevilla: {texto}")
        return None

    return resultados[0]


def coordenadas_a_direccion(lat: float, lng: float) -> str | None:

    try:
        respuesta = httpx.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": lat,
                "lon": lng,
                "format": "json",
                "addressdetails": 1
            },
            headers=CABECERAS,
            timeout=8.0
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
        time.sleep(1)
        return datos.get("display_name")
    except Exception as e:
        print(f"[Geocodificador] ❌ Error reverse: {e}")
        return None