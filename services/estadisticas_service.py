import math

import requests
from flask import current_app
from services.admin_service import _backend_url, _get_backend_cookies


def consultar_estadistica(recurso, params=None, tipo=list):
    datos, error = None, None
    cookies = _get_backend_cookies()

    try:
        if not cookies:
            error = 'Sesión del backend ausente. Iniciá sesión nuevamente.'
        else:
            respuesta = requests.get(
                f'{_backend_url()}/{recurso}',
                params=params,
                cookies=cookies,
                timeout=10
            )

            if respuesta.status_code in (401, 403):
                error = 'Sesión expirada o sin permisos. Iniciá sesión nuevamente.'

            elif not respuesta.ok:
                current_app.logger.warning(
                    'Error HTTP %s consultando %s',
                    respuesta.status_code,
                    recurso
                )
                error = 'No se pudieron consultar los datos.'

            else:
                cuerpo = respuesta.json()

                if (
                    not isinstance(cuerpo, dict)
                    or cuerpo.get('status') != 'success'
                    or not isinstance(cuerpo.get('data'), tipo)
                ):
                    raise ValueError('Estructura inesperada')

                datos = cuerpo['data']

    except (requests.RequestException, ValueError, TypeError) as exc:
        current_app.logger.warning(
            'Fallo consultando %s: %s',
            recurso,
            exc
        )
        datos, error = None, 'No se pudieron consultar los datos.'

    return datos, error


def validar_estadistica(datos, campos, lista=True):
    valido = isinstance(datos, list if lista else dict)
    filas = datos if lista and valido else ([datos] if valido else [])

    for fila in filas:
        if not isinstance(fila, dict):
            valido = False
            break

        for nombre, tipo in campos.items():
            valor = fila.get(nombre)

            if tipo == 'numero':
                correcto = (
                    isinstance(valor, (int, float))
                    and not isinstance(valor, bool)
                    and math.isfinite(valor)
                    and valor >= 0
                )
            else:
                correcto = (
                    isinstance(valor, str)
                    and bool(valor.strip())
                )

            if not correcto:
                valido = False
                break

    return valido


def obtener_estadistica(recurso, campos, params=None, lista=True):
    datos, error = consultar_estadistica(
        recurso,
        params,
        list if lista else dict
    )

    if error is None and not validar_estadistica(datos, campos, lista):
        current_app.logger.warning(
            'Datos inválidos en %s',
            recurso
        )
        datos, error = None, 'La respuesta recibida no es válida.'

    return datos, error


def obtener_pdf():
    contenido, error, estado = None, None, 502
    cookies = _get_backend_cookies()

    try:
        if not cookies:
            error = 'Sesión del backend ausente. Iniciá sesión nuevamente.'
            estado = 401

        else:
            respuesta = requests.get(
                f'{_backend_url()}/estadisticas/reporte-pdf',
                cookies=cookies,
                timeout=30
            )

            tipo_contenido = (
                respuesta.headers.get('Content-Type', '')
                .split(';')[0]
                .strip()
                .lower()
            )

            if respuesta.status_code in (401, 403):
                error = 'Sesión expirada o sin permisos. Iniciá sesión nuevamente.'
                estado = respuesta.status_code

            elif (
                not respuesta.ok
                or tipo_contenido != 'application/pdf'
                or not respuesta.content.startswith(b'%PDF-')
            ):
                current_app.logger.warning(
                    'Respuesta PDF inválida: HTTP %s',
                    respuesta.status_code
                )
                error = 'No se pudo descargar el reporte PDF.'

            else:
                contenido = respuesta.content
                estado = 200

    except requests.RequestException as exc:
        current_app.logger.warning(
            'Fallo descargando reporte PDF: %s',
            exc
        )
        error = 'No se pudo descargar el reporte PDF.'

    return contenido, error, estado