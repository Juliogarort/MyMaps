"""
probar_geocodificador.py

Prueba el geocodificador convirtiendo direcciones reales
de Sevilla en coordenadas.

Uso:
    python probar_geocodificador.py
"""

from apis.geocodificador import direccion_a_coordenadas

# Direcciones de prueba
DIRECCIONES = [
    "Calle Sierpes 10, Sevilla",
    "Avenida de la Constitución, Sevilla",
    "Triana, Sevilla",
    "Estación de Santa Justa, Sevilla",
    "Calle San Jacinto 12, Triana",
]

if __name__ == "__main__":
    print("=" * 55)
    print("  Geocodificador — Direcciones a coordenadas")
    print("=" * 55)

    for direccion in DIRECCIONES:
        print(f"\n🔍 Buscando: {direccion}")
        resultado = direccion_a_coordenadas(direccion)

        if resultado:
            print(f"   ✅ Encontrado: {resultado['nombre'][:60]}...")
            print(f"      lat={resultado['lat']}, lng={resultado['lng']}")
        else:
            print(f"   ❌ No encontrado")

    print("\n" + "=" * 55)