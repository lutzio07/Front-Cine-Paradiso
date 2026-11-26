from collections import OrderedDict


def agrupar_asientos_por_fila(asientos):
    """
    Agrupa una lista de asientos por fila manteniendo el orden de filas y columnas.
    Retorna:
        - mapa_filas (OrderedDict): {'A': [asiento1, asiento2, ...], 'B': [...]}
        - estadisticas (dict): incluye totales y la última columna del mapa.
    """
    if not isinstance(asientos, list):
        return OrderedDict(), {"total": 0, "disponibles": 0, "ocupados": 0, "columnas": 0}

    mapa = OrderedDict()
    disponibles = 0
    ocupados = 0
    columnas = 0

    asientos_ordenados = sorted(
        asientos,
        key=lambda a: (
            len(str(a.get("fila", "")).strip()),
            str(a.get("fila", "")).upper().strip(),
            int(a.get("columna") or a.get("numero") or 1),
        ),
    )

    for asiento in asientos_ordenados:
        fila = str(asiento.get("fila", "")).upper().strip()
        if not fila:
            continue

        if fila not in mapa:
            mapa[fila] = []
        asiento_con_columna = dict(asiento)
        asiento_con_columna["columna"] = max(
            1, int(asiento.get("columna") or asiento.get("numero") or 1)
        )
        mapa[fila].append(asiento_con_columna)
        columnas = max(columnas, asiento_con_columna["columna"])

        if asiento.get("estado") == "OCUPADO":
            ocupados += 1
        else:
            disponibles += 1

    estadisticas = {
        "total": disponibles + ocupados,
        "disponibles": disponibles,
        "ocupados": ocupados,
        "columnas": columnas,
    }

    return mapa, estadisticas
