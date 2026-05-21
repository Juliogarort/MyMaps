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
from apis.overpass import obtener_incidencias_overpass
from apis.clima import obtener_clima_sevilla
from sevilla.tsp import calcular_ruta_optima
from sevilla.reglas import calcular_distancia, calcular_penalizacion_dgt, calcular_penalizacion_clima

app = FastAPI(
    title="MyMaps API",
    description="Sistema de optimización de rutas de reparto en Sevilla",
    version="1.0.0"
)

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


# ── Combinar incidencias de todas las fuentes ────────────────

def obtener_todas_incidencias() -> list:
    """
    Combina incidencias de la DGT (carreteras) y Overpass (calles urbanas).
    """
    incidencias_dgt      = obtener_incidencias_sevilla()
    incidencias_overpass = obtener_incidencias_overpass()
    todas = incidencias_dgt + incidencias_overpass
    print(f"[Incidencias] DGT: {len(incidencias_dgt)} | Overpass: {len(incidencias_overpass)} | Total: {len(todas)}")
    return todas


# ── Justificación en lenguaje humano ─────────────────────────

def generar_justificacion(ruta: list, incidencias: list, clima: dict) -> str:
    """
    Genera un mensaje simple y entendible explicando las decisiones de la ruta.
    """
    mensajes = []
    factor_clima = calcular_penalizacion_clima(clima)

    # Mensaje sobre el clima
    condicion = clima.get("condicion", "normal")
    if condicion == "tormenta":
        mensajes.append(f"⛈️ Hay tormenta en Sevilla. Se ha aumentado la precaución en todos los tramos.")
    elif condicion == "lluvia":
        mensajes.append(f"🌧️ Está lloviendo en Sevilla. Se ha tenido en cuenta para el cálculo.")

    # Analizar cada tramo de la ruta
    tramos_con_incidencias = []
    for i in range(len(ruta) - 1):
        p1, p2 = ruta[i], ruta[i + 1]
        penalizacion = calcular_penalizacion_dgt(p1, p2, incidencias)

        if penalizacion > 1.0:
            # Buscar qué incidencias afectan a este tramo
            medio = {
                "lat": (p1["lat"] + p2["lat"]) / 2,
                "lng": (p1["lng"] + p2["lng"]) / 2
            }
            incidencias_cercanas = []
            for inc in incidencias:
                punto_inc = {"lat": inc["lat"], "lng": inc["lng"]}
                if calcular_distancia(medio, punto_inc) < 5:
                    incidencias_cercanas.append(inc)

            if incidencias_cercanas:
                nombres_paradas = f"{p1['nombre']} y {p2['nombre']}"
                tipos = list(set([inc.get("tipo", "incidencia") for inc in incidencias_cercanas]))
                tipo_texto = _tipo_a_texto(tipos[0]) if tipos else "una incidencia"
                carretera = incidencias_cercanas[0].get("carretera", "")
                if carretera and carretera != "Calle sin nombre":
                    tramos_con_incidencias.append(
                        f"⚠️ Entre {nombres_paradas} se detectó {tipo_texto} en {carretera}. "
                        f"Se ajustó el coste del tramo para optimizar la ruta."
                    )
                else:
                    tramos_con_incidencias.append(
                        f"⚠️ Entre {nombres_paradas} se detectó {tipo_texto}. "
                        f"Se ajustó el coste del tramo para optimizar la ruta."
                    )

    if tramos_con_incidencias:
        mensajes.extend(tramos_con_incidencias)
    else:
        mensajes.append("✅ No se detectaron incidencias en ningún tramo de la ruta.")

    # Mensaje final con el orden elegido
    nombres_orden = " → ".join([p["nombre"] for p in ruta])
    mensajes.append(f"🗺️ Orden óptimo calculado: {nombres_orden}")

    return "\n".join(mensajes)


def _tipo_a_texto(tipo: str) -> str:
    """Convierte el tipo de incidencia a texto legible."""
    textos = {
        "obras":      "obras en la vía",
        "accidente":  "un accidente",
        "corte":      "un corte de tráfico",
        "congestion": "congestión de tráfico",
        "otros":      "una incidencia de tráfico"
    }
    return textos.get(tipo, "una incidencia")


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
    """Devuelve las incidencias de tráfico activas en Sevilla (DGT + Overpass)."""
    return obtener_todas_incidencias()


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
    Calcula la ruta óptima de reparto combinando datos de DGT, Overpass y clima.
    """
    punto_almacen = {
        "nombre": peticion.almacen.nombre,
        "lat":    peticion.almacen.lat,
        "lng":    peticion.almacen.lng
    }

    puntos = [punto_almacen]
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

    # Datos en tiempo real — DGT + Overpass + clima
    incidencias_activas = obtener_todas_incidencias()
    clima_actual        = obtener_clima_sevilla()

    # Calcular ruta óptima
    resultado = calcular_ruta_optima(puntos, incidencias_activas, clima_actual)

    # Justificación en lenguaje humano
    ruta = resultado.get("ruta_ordenada", [])
    justificacion = generar_justificacion(ruta, incidencias_activas, clima_actual)

    # Guardar CSV
    try:
        import csv
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"ruta_{timestamp}.csv", mode="w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            escritor.writerow(["Orden", "Nombre", "Latitud", "Longitud"])
            for idx, p in enumerate(resultado["ruta_ordenada"]):
                escritor.writerow([idx, p["nombre"], p["lat"], p["lng"]])
    except Exception as e:
        print(f"[CSV] Error guardando archivo: {e}")

    # Trazado real por calles con OSRM
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
        "no_encontradas": [],
        "justificacion":  justificacion
    }