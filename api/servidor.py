"""
api/servidor.py

Servidor FastAPI que expone el sistema de rutas como API REST.

Endpoints:
    POST /ruta         → calcula la ruta óptima dado un conjunto de direcciones
    GET  /incidencias  → devuelve incidencias activas en Sevilla
    GET  /clima        → devuelve el clima actual en Sevilla
    GET  /estado       → verifica que el servidor está activo

Uso:
    uvicorn api.servidor:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from apis.geocodificador import direccion_a_coordenadas
from apis.dgt import obtener_incidencias_sevilla
from apis.clima import obtener_clima_sevilla
from sevilla.tsp import calcular_ruta_optima
from sevilla.reglas import calcular_distancia, calcular_penalizacion_dgt, calcular_penalizacion_clima

app = FastAPI(
    title="MyMaps API",
    description="Sistema de optimización de rutas de reparto en Sevilla",
    version="1.0.0"
)

# Permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Modelos de datos ─────────────────────────────────────────

class Parada(BaseModel):
    nombre:    str
    direccion: str
    lat:       float
    lng:       float


class PeticionRuta(BaseModel):
    almacen: Parada
    paradas: List[Parada]


# ── Endpoints ────────────────────────────────────────────────

@app.get("/estado")
def estado():
    """Verifica que el servidor está activo."""
    return {"estado": "activo", "servicio": "MyMaps API"}


@app.get("/clima")
def clima():
    """Devuelve el clima actual en Sevilla."""
    return obtener_clima_sevilla()


@app.get("/incidencias")
def incidencias():
    """Devuelve las incidencias de tráfico activas en Sevilla."""
    return obtener_incidencias_sevilla()


@app.get("/geocodificar")
def geocodificar(direccion: str):
    """Convierte una dirección en coordenadas usando Nominatim."""
    resultado = direccion_a_coordenadas(direccion)
    if not resultado:
        raise HTTPException(status_code=404, detail="Dirección no encontrada en Sevilla")
    return resultado

@app.get("/reversa")
def reversa(lat: float, lng: float):
    from apis.geocodificador import coordenadas_a_direccion
    direccion = coordenadas_a_direccion(lat, lng)
    if not direccion:
        raise HTTPException(status_code=404, detail="No se encontró dirección")
    return {"direccion": direccion}

@app.post("/ruta")
def calcular_ruta(peticion: PeticionRuta):
    """
    Calcula la ruta óptima de reparto.

    Recibe:
        - almacen: punto de salida y regreso
        - paradas: lista de direcciones de entrega

    Devuelve:
        - ruta_ordenada: paradas en orden óptimo
        - coste_total:   coste total del recorrido
        - distancias:    detalle de cada tramo
        - clima:         condiciones meteorológicas
        - incidencias:   incidencias activas
    """

    # Construir puntos directamente desde la petición
    punto_almacen = {
        "nombre": peticion.almacen.nombre,
        "lat":    peticion.almacen.lat,
        "lng":    peticion.almacen.lng
    }

    puntos = [punto_almacen]
    no_encontradas = []

    for parada in peticion.paradas:
        puntos.append({
            "nombre": parada.nombre,
            "lat":    parada.lat,
            "lng":    parada.lng
        })

    if len(puntos) < 2:
        raise HTTPException(
            status_code=400,
            detail="Se requiere el almacén y al menos una parada"
        )

    # Datos en tiempo real
    incidencias_activas = obtener_incidencias_sevilla()
    clima_actual        = obtener_clima_sevilla()

    # Calcular ruta óptima
    resultado = calcular_ruta_optima(puntos, incidencias_activas, clima_actual)

    # Generar justificación real tramo a tramo
    ruta = resultado.get("ruta_ordenada", [])
    n_paradas = len(ruta) - 2
    coste = resultado.get("coste_total", 0)
    factor_clima = calcular_penalizacion_clima(clima_actual)

    lineas = ["% === Análisis de la decisión de ruta ===", ""]

    # Clima
    if factor_clima > 1.0:
        condicion = clima_actual.get("condicion", "adverso")
        lineas.append(f"% ⚠️  Clima adverso: {condicion} → penalización x{factor_clima:.1f} en todos los tramos")
    else:
        temp = clima_actual.get("temperatura", "?")
        lineas.append(f"% ✅ Clima: despejado ({temp}°C), sin penalización por clima")

    lineas.append("")
    lineas.append("% Desglose de tramos (distancia, penalizaciones, coste efectivo):")

    tramos_penalizados = []
    for i in range(len(ruta) - 1):
        p1, p2 = ruta[i], ruta[i + 1]
        dist = calcular_distancia(p1, p2)
        pen = calcular_penalizacion_dgt(p1, p2, incidencias_activas)
        coste_tramo = dist * pen * factor_clima
        penalizado = pen > 1.0
        if penalizado:
            tramos_penalizados.append((p1["nombre"], p2["nombre"], pen, dist))
        icono = "⚠️ " if penalizado else "✅"
        detalle = f"incidencias cerca → coste x{pen:.2f}" if penalizado else "sin incidencias"
        lineas.append(
            f"%   {icono} {p1['nombre']} → {p2['nombre']}: "
            f"{dist:.2f}km | {detalle} | coste efectivo: {coste_tramo:.2f}km"
        )

    lineas.append("")
    lineas.append("% Decisión del algoritmo OR-Tools (TSP PATH_CHEAPEST_ARC):")
    if tramos_penalizados:
        penalizados_str = ", ".join([f"{a}→{b} (x{p:.2f})" for a, b, p, _ in tramos_penalizados])
        lineas.append(f"%   Tramos penalizados por incidencias: {penalizados_str}")
        lineas.append(
            f"%   El algoritmo asignó mayor coste a esos tramos para priorizar"
            f" rutas alternativas con menos carga de tráfico."
        )
    else:
        lineas.append("%   Ningún tramo afectado por incidencias. Orden elegido solo por distancia mínima.")

    orden = " → ".join([p["nombre"] for p in ruta])
    lineas.append(f"%   Orden óptimo final: {orden}")
    lineas.append(f"%   Coste total ponderado: {coste:.2f} km equivalentes")

    justificacion = "\n".join(lineas)

    # Guardar en CSV
    try:
        import csv
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"ruta_{timestamp}.csv", mode="w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            escritor.writerow(["Orden", "Nombre", "Latitud", "Longitud", "Direccion"])
            for idx, p in enumerate(resultado["ruta_ordenada"]):
                escritor.writerow([idx, p["nombre"], p["lat"], p["lng"], p.get("direccion", "")])
    except Exception as e:
        print(f"[CSV] Error guardando archivo: {e}")

    # Obtener trazado OSRM real
    trazado_calles = None
    try:
        import httpx
        coords = ";".join([f"{p['lng']},{p['lat']}" for p in resultado["ruta_ordenada"]])
        url = f"https://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson"
        res = httpx.get(url, timeout=10.0)
        res.raise_for_status()
        osrm_data = res.json()
        if osrm_data.get("routes"):
            trazado_calles = [{"lat": c[1], "lng": c[0]} for c in osrm_data["routes"][0]["geometry"]["coordinates"]]
    except Exception as e:
        print(f"[OSRM] Error obteniendo trazado: {e}")
        trazado_calles = resultado["ruta_ordenada"]

    return {
        "ruta_ordenada":  resultado["ruta_ordenada"],
        "trazado_calles": trazado_calles or resultado["ruta_ordenada"],
        "coste_total":    resultado["coste_total"],
        "distancias":     resultado["distancias"],
        "clima":          clima_actual,
        "incidencias":    incidencias_activas,
        "no_encontradas": no_encontradas,
        "justificacion":  justificacion
    }