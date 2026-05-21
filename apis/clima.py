import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
URL_BASE = "https://api.openweathermap.org/data/2.5"

# Coordenadas del centro de Sevilla
LAT_SEVILLA = 37.3891
LNG_SEVILLA = -5.9845


def obtener_clima_sevilla() -> dict:
    """
    Devuelve el clima actual de Sevilla en un formato simple.

    Retorna un diccionario con:
        - descripcion: texto del clima (ej: "lluvia ligera")
        - temperatura: en grados Celsius
        - lluvia: True o False
        - viento_kmh: velocidad del viento
        - condicion: "normal", "lluvia" o "tormenta"
    """
    if not API_KEY:
        print("[Clima] ⚠️  Sin API key. Añádela al .env como OPENWEATHER_API_KEY")
        return _clima_simulado()

    try:
        respuesta = httpx.get(
            f"{URL_BASE}/weather",
            params={
                "lat":   LAT_SEVILLA,
                "lon":   LNG_SEVILLA,
                "appid": API_KEY,
                "units": "metric",
                "lang":  "es"
            },
            timeout=8.0
        )
        respuesta.raise_for_status()
        return _parsear_clima(respuesta.json())

    except httpx.HTTPStatusError as e:
        print(f"[Clima] ❌ Error HTTP {e.response.status_code} — comprueba tu API key")
        return _clima_simulado()
    except Exception as e:
        print(f"[Clima] ❌ Error: {e}")
        return _clima_simulado()


def _parsear_clima(datos: dict) -> dict:
    """Extrae los campos que nos interesan de la respuesta de OpenWeatherMap."""
    descripcion  = datos["weather"][0]["description"]
    temperatura  = datos["main"]["temp"]
    viento_ms    = datos["wind"]["speed"]
    viento_kmh   = round(viento_ms * 3.6, 1)
    id_clima     = datos["weather"][0]["id"]

    # Los códigos de clima de OpenWeatherMap:
    # 2xx = tormenta, 3xx = llovizna, 5xx = lluvia, resto = normal
    if id_clima < 300:
        condicion = "tormenta"
    elif id_clima < 600:
        condicion = "lluvia"
    else:
        condicion = "normal"

    return {
        "descripcion": descripcion,
        "temperatura": temperatura,
        "lluvia":      condicion in ("lluvia", "tormenta"),
        "viento_kmh":  viento_kmh,
        "condicion":   condicion
    }


def _clima_simulado() -> dict:
    """Devuelve datos de clima simulados cuando la API no está disponible."""
    print("[Clima] Usando datos simulados")
    return {
        "descripcion": "cielo despejado (simulado)",
        "temperatura": 24.0,
        "lluvia":      False,
        "viento_kmh":  12.0,
        "condicion":   "normal"
    }