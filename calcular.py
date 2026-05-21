import csv
from datetime import datetime

from apis.geocodificador import direccion_a_coordenadas
from apis.dgt import obtener_incidencias_sevilla
from apis.clima import obtener_clima_sevilla
from sevilla.tsp import calcular_ruta_optima


def pedir_numero_paradas() -> int:
    while True:
        try:
            n = int(input("\n¿Cuántas paradas de entrega tienes? "))
            if n < 1:
                print("  ⚠️  Introduce al menos 1 parada.")
            elif n > 20:
                print("  ⚠️  Máximo 20 paradas por ruta.")
            else:
                return n
        except ValueError:
            print("  ⚠️  Introduce un número válido.")


def pedir_paradas(total: int) -> list:
    print(f"\n📦 Introduce las {total} direcciones de entrega.")
    print("   Puedes usar direcciones o nombres de lugares.")
    print("   Ejemplo: 'Calle Sierpes 10' o 'Hospital Virgen del Rocío'\n")

    paradas = []

    while len(paradas) < total:
        numero    = len(paradas) + 1
        direccion = input(f"  Parada {numero}/{total}: ").strip()

        if not direccion:
            continue

        print(f"  🔍 Buscando en Sevilla...")
        resultado = direccion_a_coordenadas(direccion)

        if resultado:
            parada = {
                "nombre": f"Entrega {numero} - {direccion}",
                "lat":    resultado["lat"],
                "lng":    resultado["lng"]
            }
            paradas.append(parada)
            nombre_corto = resultado["nombre"].split(",")[0]
            print(f"  ✅ {nombre_corto}")
            print(f"     lat={resultado['lat']:.4f}, lng={resultado['lng']:.4f}\n")
        else:
            print(f"  ❌ No encontrado en Sevilla. Intenta con más detalle.\n")

    return paradas


def exportar_csv(resultado: dict, clima: dict, incidencias: list):
    timestamp      = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"ruta_{timestamp}.csv"

    with open(nombre_archivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["MyMaps — Ruta óptima de reparto"])
        writer.writerow(["Fecha",           datetime.now().strftime("%d/%m/%Y %H:%M")])
        writer.writerow(["Clima",           clima["descripcion"]])
        writer.writerow(["Condición",       clima["condicion"]])
        writer.writerow(["Incidencias DGT", len(incidencias)])
        writer.writerow([])
        writer.writerow(["Orden", "Parada", "Latitud", "Longitud"])
        for i, parada in enumerate(resultado["ruta_ordenada"]):
            if i == 0 or i == len(resultado["ruta_ordenada"]) - 1:
                tipo = "ALMACÉN"
            else:
                tipo = f"Parada {i}"
            writer.writerow([tipo, parada["nombre"], parada["lat"], parada["lng"]])
        writer.writerow([])
        writer.writerow(["Desde", "Hasta", "Coste (km equiv.)"])
        for tramo in resultado["distancias"]:
            writer.writerow([tramo["desde"], tramo["hasta"], tramo["coste"]])
        writer.writerow([])
        writer.writerow(["Coste total", resultado["coste_total"], "km equivalentes"])

    print(f"\n💾 Resultado exportado a: {nombre_archivo}")


if __name__ == "__main__":
    print("=" * 55)
    print("  MyMaps — Sistema de rutas óptimas de reparto")
    print("=" * 55)

    ALMACEN = {
        "nombre": "Almacén Central",
        "lat":    37.3985,
        "lng":   -5.9936
    }

    total   = pedir_numero_paradas()
    paradas = pedir_paradas(total)

    print("\n📡 Obteniendo datos en tiempo real...")
    incidencias = obtener_incidencias_sevilla()
    clima       = obtener_clima_sevilla()

    print(f"🌤  Clima: {clima['descripcion']} — {clima['condicion']}")
    print(f"🚦 Incidencias en Sevilla: {len(incidencias)}")
    print(f"📦 Paradas a visitar: {len(paradas)}")

    todas = [ALMACEN] + paradas
    print("\n⏳ Calculando ruta óptima...")
    resultado = calcular_ruta_optima(todas, incidencias, clima)

    print("\n✅ Ruta óptima encontrada:")
    print("-" * 55)
    for i, parada in enumerate(resultado["ruta_ordenada"]):
        if i == 0:
            print(f"  🏭 SALIDA:    {parada['nombre']}")
        elif i == len(resultado["ruta_ordenada"]) - 1:
            print(f"  🏭 REGRESO:   {parada['nombre']}")
        else:
            print(f"  📦 Parada {i}: {parada['nombre']}")

    print(f"\n📊 Detalle de tramos:")
    for tramo in resultado["distancias"]:
        print(f"  {tramo['desde'][:25]:25} → {tramo['hasta'][:25]:25} {tramo['coste']} km")

    print(f"\n🏁 Coste total: {resultado['coste_total']} km equivalentes")
    exportar_csv(resultado, clima, incidencias)
    print("=" * 55)