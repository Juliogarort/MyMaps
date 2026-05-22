import math

# ── Distancia real (Haversine) ───────────────────────────────

def calcular_distancia(punto1: dict, punto2: dict) -> float:
    R = 6371  # radio de la Tierra en km
    lat1 = math.radians(punto1["lat"])
    lat2 = math.radians(punto2["lat"])
    dlat = math.radians(punto2["lat"] - punto1["lat"])
    dlng = math.radians(punto2["lng"] - punto1["lng"])

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


# ── Penalizaciones por incidencias ───────────────────────────

def calcular_penalizacion_incidencias(punto1: dict, punto2: dict, incidencias: list) -> float:

    penalizacion = 1.0

    # Punto medio del tramo de reparto
    medio = {
        "lat": (punto1["lat"] + punto2["lat"]) / 2,
        "lng": (punto1["lng"] + punto2["lng"]) / 2
    }

    for incidencia in incidencias:
        punto_inc = {"lat": incidencia["lat"], "lng": incidencia["lng"]}
        distancia_a_incidencia = calcular_distancia(medio, punto_inc)
        
        fuente = incidencia.get("fuente", "DGT")
        tipo = incidencia.get("tipo", "otros")
        gravedad = incidencia.get("gravedad", 1)

        if fuente == "OpenStreetMap":
            # --- LÓGICA URBANA (Overpass) ---
            # En ciudad, una calle cortada solo afecta si está muy cerca del tramo (ej: menos de 400 metros)
            if distancia_a_incidencia > 0.4: 
                continue
                
            if tipo == "corte":
                penalizacion += 1.5 * gravedad   # Penaliza drásticamente para que el TSP busque otra calle
            elif tipo == "obras":
                penalizacion += 0.4 * gravedad   # Las obras urbanas ralentizan bastante
            else:
                penalizacion += 0.2 * gravedad

        else:
            # --- LÓGICA INTERURBANA (DGT) ---
            # En autopistas/rondas (SE-30, A-4), el impacto se nota a kilómetros de distancia
            if distancia_a_incidencia > 4.0:
                continue

            if tipo == "accidente":
                penalizacion += 0.3 * gravedad
            elif tipo == "obras":
                penalizacion += 0.2 * gravedad
            elif tipo == "corte":
                penalizacion += 1.0 * gravedad
            elif tipo == "congestion":
                penalizacion += 0.15 * gravedad

    return penalizacion


# ── Penalización por clima ───────────────────────────────────

def calcular_penalizacion_clima(clima: dict) -> float:
    condicion = clima.get("condicion", "normal")
    if condicion == "tormenta":
        return 1.5
    elif condicion == "lluvia":
        return 1.2
    else:
        return 1.0


# ── Coste total del tramo ────────────────────────────────────

def calcular_coste(punto1: dict, punto2: dict, incidencias: list, clima: dict) -> float:
    """
    Fórmula unificada que alimenta al algoritmo de OR-Tools.
    """
    distancia = calcular_distancia(punto1, punto2)
    penalizacion_trafico = calcular_penalizacion_incidencias(punto1, punto2, incidencias)
    penalizacion_clima = calcular_penalizacion_clima(clima)

    return distancia * penalizacion_trafico * penalizacion_clima