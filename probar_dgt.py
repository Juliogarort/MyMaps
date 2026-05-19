"""
probar_dgt.py

Verifica que la conexión con la DGT funciona y muestra
las incidencias activas en Sevilla.

Uso:
    python probar_dgt.py
"""

from apis.dgt import obtener_incidencias_sevilla

if __name__ == "__main__":
    print("=" * 50)
    print("  Incidencias de tráfico en Sevilla — DGT")
    print("=" * 50)

    incidencias = obtener_incidencias_sevilla()

    if not incidencias:
        print("\nℹ️  No hay incidencias activas en Sevilla ahora mismo.")
    else:
        print(f"\n📋 {len(incidencias)} incidencia(s) encontrada(s):\n")
        for i, inc in enumerate(incidencias, 1):
            print(f"  [{i}] Tipo:       {inc['tipo'].upper()}")
            print(f"      Carretera:  {inc['carretera']}")
            print(f"      Municipio:  {inc['municipio']}")
            print(f"      Gravedad:   {inc['gravedad']}/3")
            print(f"      Ubicación:  lat={inc['lat']}, lng={inc['lng']}")
            print()

    print("=" * 50)