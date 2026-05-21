import math


# ── Distancia real ───────────────────────────────────────────

def calcular_distancia(punto1: dict, punto2: dict) -> float:
    """
    Calcula la distancia en km entre dos puntos usando Haversine.
    Es la distancia en línea recta sobre la superficie terrestre.

    Parámetros:
        punto1, punto2: diccionarios con claves 'lat' y 'lng'

    Devuelve:
        Distancia en kilómetros
    """
    R = 6371  # radio de la Tierra en km

    lat1 = math.radians(punto1["lat"])
    lat2 = math.radians(punto2["lat"])
    dlat = math.radians(punto2["lat"] - punto1["lat"])
    dlng = math.radians(punto2["lng"] - punto1["lng"])

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


# ── Penalizaciones por incidencias ───────────────────────────

def calcular_penalizacion_dgt(punto1: dict, punto2: dict, incidencias: list) -> float:
    """
    Calcula un factor de penalización según las incidencias de la DGT
    que haya cerca del tramo entre punto1 y punto2.

    Lógica:
        - Calculamos el punto medio del tramo
        - Buscamos incidencias en un radio de 5km alrededor
        - Cada incidencia suma penalización según su tipo y gravedad

    Devuelve:
        Factor multiplicador (1.0 = sin penalización, 2.0 = doble coste)
    """
    penalizacion = 1.0

    # Punto medio del tramo
    medio = {
        "lat": (punto1["lat"] + punto2["lat"]) / 2,
        "lng": (punto1["lng"] + punto2["lng"]) / 2
    }

    for incidencia in incidencias:
        punto_inc = {"lat": incidencia["lat"], "lng": incidencia["lng"]}
        distancia_a_incidencia = calcular_distancia(medio, punto_inc)

        # Solo afecta si está a menos de 5km del tramo
        if distancia_a_incidencia > 5:
            continue

        tipo     = incidencia.get("tipo", "otros")
        gravedad = incidencia.get("gravedad", 1)

        # Reglas de penalización por tipo
        if tipo == "accidente":
            penalizacion += 0.3 * gravedad   # hasta +0.9
        elif tipo == "obras":
            penalizacion += 0.2 * gravedad   # hasta +0.6
        elif tipo == "corte":
            penalizacion += 1.0 * gravedad   # hasta +3.0 (casi bloquea)
        elif tipo == "congestion":
            penalizacion += 0.15 * gravedad  # hasta +0.45

    return penalizacion


# ── Penalización por clima ───────────────────────────────────

def calcular_penalizacion_clima(clima: dict) -> float:
    """
    Devuelve un factor de penalización según el clima actual.

    Reglas:
        - Tormenta: +50% al coste (conducción peligrosa)
        - Lluvia:   +20% al coste (mayor tiempo de viaje)
        - Normal:   sin penalización
    """
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
    Calcula el coste total de ir de punto1 a punto2.
    Este es el valor que usará el TSP para optimizar la ruta.

    Fórmula:
        coste = distancia × penalización_dgt × penalización_clima

    Ejemplo:
        - Distancia: 5 km
        - Obras graves cerca: ×1.6
        - Lluvia: ×1.2
        - Coste final: 5 × 1.6 × 1.2 = 9.6 (equivale a recorrer 9.6 km sin problemas)
    """
    distancia         = calcular_distancia(punto1, punto2)
    penalizacion_dgt  = calcular_penalizacion_dgt(punto1, punto2, incidencias)
    penalizacion_clima = calcular_penalizacion_clima(clima)

    return distancia * penalizacion_dgt * penalizacion_clima