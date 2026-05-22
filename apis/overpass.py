import httpx
from typing import Optional

URL_OVERPASS = "https://overpass-api.de/api/interpreter"

# Bounding box de Sevilla (Centro y áreas urbanas)
SEVILLA_LAT_MIN, SEVILLA_LAT_MAX = 37.3500, 37.4300
SEVILLA_LNG_MIN, SEVILLA_LNG_MAX = -6.0200, -5.9500

MAPEO_TIPOS_OSM = {
    "construction": "obras",
    "roadworks":    "obras",
    "block":        "corte",
    "bollard":      "corte",
    "gate":         "corte",
}

def obtener_incidencias_overpass() -> list:
    print("[Overpass] Descargando datos de tráfico urbano...")

    bbox = f"{SEVILLA_LAT_MIN},{SEVILLA_LNG_MIN},{SEVILLA_LAT_MAX},{SEVILLA_LNG_MAX}"

    # Consulta QL hiper-optimizada
    consulta = f"""
    [out:json][timeout:15];
    (
      way["highway"~"construction|roadworks"]({bbox});
      way["access"="no"]["highway"]({bbox});
      node["highway"~"construction|roadworks"]({bbox});
      node["barrier"~"block|bollard|gate"]["access"="no"]({bbox});
    );
    out center;
    """

    # 🛑 LA MAGIA ESTÁ AQUÍ: Sin este User-Agent, Overpass te bloquea el acceso
    cabeceras = {
        "User-Agent": "MyMapsApp/1.0 (julio.garort16@gmail.com)"
    }

    try:
        respuesta = httpx.post(URL_OVERPASS, data={"data": consulta}, headers=cabeceras, timeout=15.0)
        respuesta.raise_for_status()
    except Exception as e:
        print(f"[Overpass] ❌ Error al conectar: {e}")
        return []

    datos = respuesta.json()
    elementos = datos.get("elements", [])
    print(f"[Overpass] Total elementos urbanos encontrados: {len(elementos)}")

    incidencias_overpass = []
    for elemento in elementos:
        incidencia = _parsear_elemento_osm(elemento)
        if incidencia:
            incidencias_overpass.append(incidencia)

    print(f"[Overpass] Incidencias procesadas y válidas en Sevilla: {len(incidencias_overpass)}")
    return incidencias_overpass


def _parsear_elemento_osm(elemento: dict) -> Optional[dict]:
    id_osm = elemento.get("id", "desconocido")
    coords = _extraer_coordenadas(elemento)
    
    if not coords:
        return None

    tags = elemento.get("tags", {})
    carretera = tags.get("name") or tags.get("addr:street") or tags.get("description") or "Calle urbana"

    tipo_osm = tags.get("highway") or tags.get("barrier") or "incidencia"
    access_osm = tags.get("access")

    # Mapeo idéntico al de la DGT para que tu frontend lo entienda perfecto
    if access_osm == "no" or tipo_osm in ["block", "bollard", "gate"]:
        tipo = "corte"
        gravedad = 3
    else:
        tipo = MAPEO_TIPOS_OSM.get(tipo_osm, "otros")
        gravedad = 2 if tipo == "obras" else 1

    return {
        "id":         f"osm_{id_osm}",
        "tipo":       tipo,
        "gravedad":   gravedad,
        "carretera":  carretera,
        "municipio":  "Sevilla",
        "provincia":  "Sevilla",
        "lat":        float(coords[0]),
        "lng":        float(coords[1]),
        "fuente":     "OpenStreetMap"    # ← añade esta línea

    }


def _extraer_coordenadas(elemento: dict) -> Optional[tuple]:
    # Las calles (ways) vienen con 'center', los puntos (nodes) con 'lat'/'lon'
    centro = elemento.get("center")
    if centro:
        return (centro.get("lat"), centro.get("lon"))
        
    lat = elemento.get("lat")
    lng = elemento.get("lon")
    if lat is not None and lng is not None:
        return (lat, lng)
        
    return None