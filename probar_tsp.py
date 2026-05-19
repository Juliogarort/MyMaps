"""
probar_tsp.py

Prueba el algoritmo TSP con paradas de ejemplo en Sevilla.
Muestra el orden óptimo de visita y el coste total del recorrido.

Uso:
    python probar_tsp.py
"""

from apis.dgt import obtener_incidencias_sevilla
from apis.clima import obtener_clima_sevilla
from sevilla.tsp import calcular_ruta_optima

# Paradas de ejemplo — en el futuro vendrán del frontend
PARADAS = [
    {"nombre": "Almacén Central",       "lat": 37.3985, "lng": -5.9936},
    {"nombre": "Entrega - Triana",      "lat": 37.3814, "lng": -6.0023},
    {"nombre": "Entrega - Nervión",     "lat": 37.3881, "lng": -5.9729},
    {"nombre": "Entrega - Macarena",    "lat": 37.4012, "lng": -5.9871},
    {"nombre": "Entrega - Remedios",    "lat": 37.3743, "lng": -6.0003},
    {"nombre": "Entrega - Bellavista",  "lat": 37.3345, "lng": -5.9876},
]

if __name__ == "__main__":
    print("=" * 50)
    print("  TSP — Ruta óptima de reparto en Sevilla")
    print("=" * 50)

    print("\n📡 Obteniendo datos en tiempo real...")
    incidencias = obtener_incidencias_sevilla()
    clima       = obtener_clima_sevilla()

    print(f"🌤  Clima: {clima['descripcion']}")
    print(f"🚦 Incidencias en Sevilla: {len(incidencias)}")
    print(f"📦 Paradas a visitar: {len(PARADAS) - 1}")

    print("\n⏳ Calculando ruta óptima...")
    resultado = calcular_ruta_optima(PARADAS, incidencias, clima)

    print("\n✅ Ruta óptima encontrada:")
    print("-" * 50)
    for i, parada in enumerate(resultado["ruta_ordenada"]):
        if i == 0:
            print(f"  🏭 SALIDA:  {parada['nombre']}")
        elif i == len(resultado["ruta_ordenada"]) - 1:
            print(f"  🏭 REGRESO: {parada['nombre']}")
        else:
            print(f"  📦 Parada {i}: {parada['nombre']}")

    print("\n📊 Detalle de tramos:")
    for tramo in resultado["distancias"]:
        print(f"  {tramo['desde']} → {tramo['hasta']}: {tramo['coste']} km equiv.")

    print(f"\n🏁 Coste total del recorrido: {resultado['coste_total']} km equivalentes")
    print("=" * 50)