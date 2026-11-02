def armar_cartelera(peliculas, funciones, filtrando):
    ids_con_funciones = {f["id_pelicula"] for f in funciones}

    cartelera = []
    for p in peliculas:
        tiene = p["id_pelicula"] in ids_con_funciones
        if filtrando and not tiene:
            continue
        cartelera.append({**p, "con_funciones": tiene})

    return cartelera