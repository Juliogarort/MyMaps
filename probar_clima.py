"""
probar_clima.py

Ejecuta este script para verificar que la API del tiempo funciona.

Uso:
    python probar_clima.py
"""
from apis.clima import obtener_clima_sevilla

if __name__ == "__main__":
    print("=" * 40)
    print("  Clima actual en Sevilla")
    print("=" * 40)

    clima = obtener_clima_sevilla()

    print(f"  Descripción:  {clima['descripcion']}")
    print(f"  Temperatura:  {clima['temperatura']} °C")
    print(f"  Lluvia:       {'Sí' if clima['lluvia'] else 'No'}")
    print(f"  Viento:       {clima['viento_kmh']} km/h")
    print(f"  Condición:    {clima['condicion']}")
    print("=" * 40)