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

    # Geocodificar almacén
    coords_almacen = direccion_a_coordenadas(peticion.almacen.direccion)
    if not coords_almacen:
        raise HTTPException(
            status_code=400,
            detail=f"No se encontró el almacén: {peticion.almacen.direccion}"
        )

    punto_almacen = {
        "nombre": peticion.almacen.nombre,
        "lat":    coords_almacen["lat"],
        "lng":    coords_almacen["lng"]
    }

    # Geocodificar paradas
    puntos = [punto_almacen]
    no_encontradas = []

    for parada in peticion.paradas:
        coords = direccion_a_coordenadas(parada.direccion)
        if coords:
            puntos.append({
                "nombre": parada.nombre,
                "lat":    coords["lat"],
                "lng":    coords["lng"]
            })
        else:
            no_encontradas.append(parada.direccion)

    if len(puntos) < 2:
        raise HTTPException(
            status_code=400,
            detail="No se encontraron suficientes paradas en Sevilla"
        )

    # Datos en tiempo real
    incidencias_activas = obtener_incidencias_sevilla()
    clima_actual        = obtener_clima_sevilla()

    # Calcular ruta óptima
    resultado = calcular_ruta_optima(puntos, incidencias_activas, clima_actual)

    return {
        "ruta_ordenada":  resultado["ruta_ordenada"],
        "coste_total":    resultado["coste_total"],
        "distancias":     resultado["distancias"],
        "clima":          clima_actual,
        "incidencias":    incidencias_activas,
        "no_encontradas": no_encontradas
    }