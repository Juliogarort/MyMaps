from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver.routing_enums_pb2 import FirstSolutionStrategy
from sevilla.reglas import calcular_coste


def calcular_ruta_optima(paradas: list, incidencias: list, clima: dict) -> dict:

    n = len(paradas)

    if n < 2:
        return {"ruta_ordenada": paradas, "coste_total": 0.0, "distancias": []}

    matriz_costes = []
    for i in range(n):
        fila = []
        for j in range(n):
            if i == j:
                fila.append(0)
            else:
                coste = calcular_coste(paradas[i], paradas[j], incidencias, clima)
                fila.append(int(coste * 1000))
        matriz_costes.append(fila)

    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    modelo = pywrapcp.RoutingModel(manager)

    def coste_tramo(desde_idx, hasta_idx):
        desde = manager.IndexToNode(desde_idx)
        hasta = manager.IndexToNode(hasta_idx)
        return matriz_costes[desde][hasta]

    id_transito = modelo.RegisterTransitCallback(coste_tramo)
    modelo.SetArcCostEvaluatorOfAllVehicles(id_transito)

    parametros = pywrapcp.DefaultRoutingSearchParameters()
    parametros.first_solution_strategy = FirstSolutionStrategy.PATH_CHEAPEST_ARC
    parametros.time_limit.seconds = 10

    solucion = modelo.SolveWithParameters(parametros)

    if not solucion:
        print("[TSP] ⚠️  No se encontró solución óptima")
        return {"ruta_ordenada": paradas, "coste_total": 0.0, "distancias": []}

    ruta_ordenada = []
    distancias    = []
    coste_total   = 0.0

    indice = modelo.Start(0)
    while not modelo.IsEnd(indice):
        nodo = manager.IndexToNode(indice)
        ruta_ordenada.append(paradas[nodo])
        siguiente_indice = solucion.Value(modelo.NextVar(indice))
        siguiente_nodo   = manager.IndexToNode(siguiente_indice)
        if not modelo.IsEnd(siguiente_indice):
            coste_tramo_actual = matriz_costes[nodo][siguiente_nodo] / 1000
            distancias.append({
                "desde": paradas[nodo]["nombre"],
                "hasta": paradas[siguiente_nodo]["nombre"],
                "coste": round(coste_tramo_actual, 2)
            })
            coste_total += coste_tramo_actual
        indice = siguiente_indice

    ruta_ordenada.append(paradas[0])

    return {
        "ruta_ordenada": ruta_ordenada,
        "coste_total":   round(coste_total, 2),
        "distancias":    distancias
    }