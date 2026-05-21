"""
apis/dgt.py

Conecta con la API pública de la DGT y obtiene incidencias de tráfico
en tiempo real para la provincia de Sevilla.

URL: https://nap.dgt.es/datex2/v3/dgt/SituationPublication/datex2_v36.xml
Formato: XML DATEX II (estándar europeo de tráfico)
Sin API key necesaria.
"""
from typing import Optional
import httpx 
from lxml import etree

import os
from dotenv import load_dotenv
load_dotenv()
URL_DGT = os.getenv("DGT_URL", "https://nap.dgt.es/datex2/v3/dgt/SituationPublication/datex2_v36.xml")
# Namespaces del XML de la DGT
NS = {
    "sit": "http://levelC/schema/3/situation",
    "loc": "http://levelC/schema/3/locationReferencing",
    "com": "http://levelC/schema/3/common",
    "lse": "http://levelC/schema/3/locationReferencingSpanishExtension",
    "sse": "http://levelC/schema/3/situationSpanishExtension",
}

# Provincia de Sevilla para filtrar (comparación case-insensitive)
PROVINCIA_SEVILLA = "sevilla"

# Bounding box de la provincia de Sevilla como fallback
SEVILLA_LAT_MIN, SEVILLA_LAT_MAX = 36.8, 38.1
SEVILLA_LNG_MIN, SEVILLA_LNG_MAX = -7.0, -4.8

# Tipos de causa del XML mapeados a nuestro formato
TIPOS_CAUSA = {
    "roadMaintenance": "obras",
    "roadworks":       "obras",
    "accident":        "accidente",
    "obstruction":     "corte",
    "poorRoadConditions": "condicion_vial",
    "congestion":      "congestion",
}


def obtener_incidencias_sevilla() -> list:
    """
    Descarga el XML de la DGT, lo parsea y devuelve solo
    las incidencias de la provincia de Sevilla.

    Cada incidencia devuelta tiene:
        - id:          identificador único de la DGT
        - tipo:        obras | accidente | corte | congestion
        - gravedad:    1 (leve), 2 (moderada), 3 (grave)
        - carretera:   nombre de la carretera (ej: A-49)
        - provincia:   siempre Sevilla
        - municipio:   municipio afectado
        - lat:         latitud
        - lng:         longitud
    """
    print("[DGT] Descargando datos de tráfico...")

    try:
        respuesta = httpx.get(URL_DGT, timeout=15.0)
        respuesta.raise_for_status()
    except Exception as e:
        print(f"[DGT] ❌ Error al conectar: {e}")
        return []

    raiz = etree.fromstring(respuesta.content)
    situaciones = raiz.findall("sit:situation", NS)

    print(f"[DGT] Total situaciones en España: {len(situaciones)}")

    incidencias_sevilla = []

    for situacion in situaciones:
        incidencia = _parsear_situacion(situacion)
        if incidencia and _es_de_sevilla(incidencia):
            incidencias_sevilla.append(incidencia)

    print(f"[DGT] Incidencias en Sevilla: {len(incidencias_sevilla)}")
    return incidencias_sevilla


def _es_de_sevilla(inc: dict) -> bool:
    """Devuelve True si la incidencia pertenece a la provincia de Sevilla.
    Usa comparación case-insensitive y un fallback por bounding box.
    """
    provincia = inc.get("provincia", "").lower().strip()
    if PROVINCIA_SEVILLA in provincia:
        return True
    # Fallback: coordenadas dentro de la provincia
    lat, lng = inc.get("lat", 0), inc.get("lng", 0)
    return (SEVILLA_LAT_MIN <= lat <= SEVILLA_LAT_MAX and
            SEVILLA_LNG_MIN <= lng <= SEVILLA_LNG_MAX)


def _parsear_situacion(situacion) -> Optional[dict]:
    """
    Extrae los datos relevantes de un elemento <sit:situation> del XML.
    Devuelve None si faltan datos esenciales como coordenadas o provincia.
    """
    id_situacion = situacion.get("id", "desconocido")

    # Gravedad
    gravedad_elem = situacion.find("sit:overallSeverity", NS)
    gravedad = _convertir_gravedad(gravedad_elem.text if gravedad_elem is not None else "low")

    # Buscar el primer situationRecord
    record = situacion.find("sit:situationRecord", NS)
    if record is None:
        return None

    # Tipo de incidencia
    tipo = _extraer_tipo(record)

    # Coordenadas
    coords = _extraer_coordenadas(record)
    if not coords:
        return None

    # Carretera, municipio y provincia
    carretera = _extraer_texto(record, ".//loc:roadName")
    municipio = _extraer_texto(record, ".//lse:municipality")
    provincia = _extraer_texto(record, ".//lse:province")

    if not provincia:
        return None

    return {
        "id":         id_situacion,
        "tipo":       tipo,
        "gravedad":   gravedad,
        "carretera":  carretera or "Desconocida",
        "municipio":  municipio or "Desconocido",
        "provincia":  provincia,
        "lat":        coords[0],
        "lng":        coords[1],
    }


def _extraer_tipo(record) -> str:
    """Extrae el tipo de incidencia del campo causeType."""
    causa = _extraer_texto(record, ".//sit:causeType")
    if causa:
        return TIPOS_CAUSA.get(causa, "otros")
    causa_detalle = _extraer_texto(record, ".//sit:roadMaintenanceType")
    if causa_detalle:
        return TIPOS_CAUSA.get(causa_detalle, "otros")
    return "otros"


def _extraer_coordenadas(record) -> Optional[tuple]:
    """
    Extrae las coordenadas del elemento <loc:pointCoordinates>.
    Busca primero en 'to' y luego en 'from'.
    """
    for punto in record.findall(".//loc:pointCoordinates", NS):
        lat_elem = punto.find("loc:latitude", NS)
        lng_elem = punto.find("loc:longitude", NS)
        if lat_elem is not None and lng_elem is not None:
            try:
                return (float(lat_elem.text), float(lng_elem.text))
            except ValueError:
                continue
    return None


def _extraer_texto(elemento, xpath: str) -> Optional[str]:
    """Busca un elemento por xpath y devuelve su texto o None."""
    encontrado = elemento.find(xpath, NS)
    if encontrado is not None and encontrado.text:
        return encontrado.text.strip()
    return None


def _convertir_gravedad(nivel: str) -> int:
    """Convierte el nivel de gravedad del XML a escala 1-3."""
    nivel = nivel.lower()
    if nivel in ("high", "highest"):
        return 3
    if nivel in ("medium",):
        return 2
    return 1