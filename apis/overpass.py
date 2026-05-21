import httpx

URL_OVERPASS = "https://overpass-api.de/api/interpreter"

# Bounding box de Sevilla ciudad (no provincia, solo la ciudad)
SEVILLA_CIUDAD = {
    "lat_min": 37.32,
    "lat_max": 37.43,
    "lng_min": -6.05,
    "lng_max": -5.90,
}


def obtener_incidencias_overpass() -> list:

    print("[Overpass] Consultando incidencias urbanas de Sevilla...")

    bbox = (
        f"{SEVILLA_CIUDAD['lat_min']},"
        f"{SEVILLA_CIUDAD['lng_min']},"
        f"{SEVILLA_CIUDAD['lat_max']},"
        f"{SEVILLA_CIUDAD['lng_max']}"
    )

    # Consulta Overpass QL
    consulta = f"""
    [out:json][timeout:10];
    (
      way["highway"="construction"]({bbox});
      way["access"="no"]["highway"]({bbox});
      way["construction"="yes"]["highway"]({bbox});
    );
    out center;
    """

    try:
        respuesta = httpx.post(
            URL_OVERPASS,
            data={"data": consulta},
            timeout=12.0
        )
        respuesta.raise_for_status()
        datos = respuesta.json()

        incidencias = []
        for elemento in datos.get("elements", []):
            centro = elemento.get("center")
            if not centro:
                continue

            lat = centro.get("lat")
            lng = centro.get("lon")
            if not lat or not lng:
                continue

            tags = elemento.get("tags", {})
            nombre_calle = (
                tags.get("name") or
                tags.get("addr:street") or
                "Calle sin nombre"
            )

            # Determinar tipo según etiquetas OSM
            if tags.get("access") == "no":
                tipo     = "corte"
                gravedad = 3
                descripcion = f"Calle cortada al tráfico: {nombre_calle}"
            else:
                tipo     = "obras"
                gravedad = 2
                descripcion = f"Obras en calle: {nombre_calle}"

            incidencias.append({
                "id":          f"osm_{elemento.get('id', '')}",
                "tipo":        tipo,
                "gravedad":    gravedad,
                "carretera":   nombre_calle,
                "municipio":   "Sevilla",
                "provincia":   "Sevilla",
                "lat":         lat,
                "lng":         lng,
                "descripcion": descripcion,
                "fuente":      "OpenStreetMap"
            })

        print(f"[Overpass] Incidencias urbanas encontradas: {len(incidencias)}")
        return incidencias

    except httpx.TimeoutException:
        print("[Overpass] ⚠️  Timeout — Overpass tardó demasiado")
        return []
    except Exception as e:
        print(f"[Overpass] ❌ Error: {e}")
        return []