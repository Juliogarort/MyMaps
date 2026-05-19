"""
probar_reglas.py

Prueba el sistema de reglas calculando el coste entre dos puntos
reales de Sevilla con datos reales de la DGT y el clima.

Uso:
    python probar_reglas.py
"""

from apis.dgt import obtener_incidencias_sevilla
from apis.clima import obtener_clima_sevilla
from sevilla.reglas import calcular_coste, calcular_distancia

# Dos puntos de prueba: Almacén → Triana
ALMACEN = {
    "nombre": "Almacén Central",
    "lat": 37.3985,
    "lng": -5.9936
}

TRIANA = {
    "nombre": "Triana",
    "lat": 37.3814,
    "lng": -6.0023
}

NERVION = {
    "nombre": "Nervión",
    "lat": 37.3881,
    "lng": -5.9729
}

if __name__ == "__main__":
    print("=" * 50)
    print("  Sistema de reglas — coste entre puntos")
    print("=" * 50)

    # Obtenemos datos reales
    print("\n📡 Obteniendo datos en tiempo real...")
    incidencias = obtener_incidencias_sevilla()
    clima       = obtener_clima_sevilla()

    print(f"\n🌤  Clima: {clima['descripcion']} — condición: {clima['condicion']}")
    print(f"🚦 Incidencias activas en Sevilla: {len(incidencias)}")

    # Calculamos costes
    print("\n📊 Costes calculados:")
    print("-" * 50)

    tramos = [
        (ALMACEN, TRIANA),
        (ALMACEN, NERVION),
        (TRIANA, NERVION),
    ]

    for origen, destino in tramos:
        distancia = calcular_distancia(origen, destino)
        coste     = calcular_coste(origen, destino, incidencias, clima)

        print(f"\n  {origen['nombre']} → {destino['nombre']}")
        print(f"  Distancia real:  {distancia:.2f} km")
        print(f"  Coste ajustado:  {coste:.2f} km equivalentes")
        if coste > distancia:
            print(f"  ⚠️  Penalizado x{coste/distancia:.2f} por incidencias/clima")

    print("\n" + "=" * 50)