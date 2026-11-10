from collections import OrderedDict


def agrupar_asientos_por_fila(asientos):
    """
    Agrupa una lista de asientos por fila manteniendo el orden de filas y columnas.
    Retorna:
        - mapa_filas (OrderedDict): {'A': [asiento1, asiento2, ...], 'B': [...]}
        - estadisticas (dict): {'total': int, 'disponibles': int, 'ocupados': int}
    """
    if not isinstance(asientos, list):
        return OrderedDict(), {"total": 0, "disponibles": 0, "ocupados": 0}

    mapa = OrderedDict()
    disponibles = 0
    ocupados = 0

    asientos_ordenados = sorted(
        asientos,
        key=lambda a: (str(a.get("fila", "")).upper(), int(a.get("numero", 0)))
    )

    for asiento in asientos_ordenados:
        fila = str(asiento.get("fila", "")).upper().strip()
        if not fila:
            continue

        if fila not in mapa:
            mapa[fila] = []
        mapa[fila].append(asiento)

        if asiento.get("estado") == "OCUPADO":
            ocupados += 1
        else:
            disponibles += 1

    estadisticas = {
        "total": disponibles + ocupados,
        "disponibles": disponibles,
        "ocupados": ocupados,
    }

    return mapa, estadisticas

