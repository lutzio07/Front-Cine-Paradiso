"""Ejecutar con PYTHONPATH=. python tests/test_dashboard.py, sin backend."""
from unittest.mock import Mock, patch

from app import create_app


def respuesta(data=None, status=200, tipo='application/json', contenido=b''):
    objeto = Mock(status_code=status, ok=200 <= status < 400, headers={'Content-Type': tipo}, content=contenido)
    objeto.json.return_value = {'status': 'success', 'data': data}
    return objeto


def ejecutar_pruebas():
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY='test', BACKEND_URL='http://backend/api')
    cliente = app.test_client()
    llamadas = []
    datos = {
        'ocupacion': [{'id_funcion': 12, 'titulo_pelicula': 'Interestelar', 'nombre_sala': 'Sala 1', 'fecha_hora': '2026-11-08T20:30:00', 'capacidad': 100, 'entradas_vendidas': 75, 'porcentaje_ocupacion': 75.0}],
        'ventas-por-genero': [{'genero': 'Acción', 'total_ventas': 15000.50, 'entradas_vendidas': 10}],
        'franjas-horarias': [{'hora': '20:30', 'entradas_vendidas': 25}],
        'cancelaciones': {'total_cancelaciones': 12},
        'peliculas': [{'id_pelicula': 1, 'titulo': 'Interestelar'}],
        'funciones': [{'id_funcion': 12, 'id_pelicula': 1, 'titulo_pelicula': 'Interestelar', 'nombre_sala': 'Sala 1', 'fecha_hora': '2026-11-08T20:30:00'}],
    }
    fallas = {}
    def get(url, **kwargs):
        clave = url.rsplit('/', 1)[-1]
        llamadas.append((clave, kwargs))
        assert kwargs['cookies'] == {'session': 'cookie-backend'}
        if clave in fallas:
            resultado = fallas[clave]
        elif clave == 'reporte-pdf':
            resultado = respuesta(tipo='application/pdf', contenido=b'%PDF-1.4\ncontenido')
        else:
            resultado = respuesta(datos[clave])
        return resultado

    with patch('services.estadisticas_service.requests.get', side_effect=get):
        assert cliente.get('/admin/dashboard').status_code == 302
        assert cliente.get('/admin/estadisticas/reporte-pdf').status_code == 403
        with cliente.session_transaction() as sesion:
            sesion['rol'] = 'CLIENTE'
        assert cliente.get('/admin/dashboard').status_code == 302
        assert cliente.get('/admin/estadisticas/reporte-pdf').status_code == 403
        assert not llamadas
        with cliente.session_transaction() as sesion:
            sesion['rol'], sesion['backend_session'] = 'ADMIN', 'cookie-backend'
        for query, esperado in [('', {}), ('?id_pelicula=1', {'id_pelicula': 1}), ('?id_funcion=12', {'id_funcion': 12}), ('?id_pelicula=1&id_funcion=12', {'id_pelicula': 1, 'id_funcion': 12}), ('?id_pelicula=&id_funcion=12', {'id_funcion': 12}), ('?id_pelicula=1&id_funcion=', {'id_pelicula': 1})]:
            llamadas.clear()
            resultado = cliente.get('/admin/dashboard' + query)
            assert resultado.status_code == 200
            assert 'Interestelar' in resultado.text and '$ 15.000,50' in resultado.text and '20:30' in resultado.text
            assert next(k['params'] for n, k in llamadas if n == 'ocupacion') == esperado
            assert all(k.get('params') is None for n, k in llamadas if n in ('ventas-por-genero', 'franjas-horarias', 'cancelaciones'))
        llamadas.clear()
        assert 'enteros positivos' in cliente.get('/admin/dashboard?id_pelicula=-1').text
        assert all(n != 'ocupacion' for n, _ in llamadas)
        datos['ocupacion'] = []
        datos['ventas-por-genero'] = []
        assert 'No se encontraron funciones' in cliente.get('/admin/dashboard').text
        fallas['cancelaciones'] = respuesta(status=500)
        fallas['ocupacion'] = respuesta(status=401)
        pagina = cliente.get('/admin/dashboard').text
        assert 'Sesión expirada' in pagina and 'No se pudieron consultar los datos' in pagina and 'Sin datos de ventas' in pagina
        pdf = cliente.get('/admin/estadisticas/reporte-pdf')
        assert pdf.data.startswith(b'%PDF-') and pdf.mimetype == 'application/pdf' and 'reporte-cine-paradiso.pdf' in pdf.headers['Content-Disposition']
        for invalido in (respuesta(status=500), respuesta(tipo='text/html', contenido=b'<html>login</html>'), respuesta(tipo='application/pdf', contenido=b'no pdf')):
            fallas['reporte-pdf'] = invalido
            assert cliente.get('/admin/estadisticas/reporte-pdf').mimetype == 'application/json'
        assert cliente.get('/login').status_code == 200
        with app.test_request_context():
            from flask import url_for
            assert url_for('admin.dashboard') == '/admin/dashboard'
            assert url_for('admin.peliculas') in ('/admin/', '/admin/peliculas')
            assert url_for('admin.admin_salas_funciones') == '/admin/cargar-pelicula'
            assert url_for('admin.peliculas', _external=False) != '/admin/dashboard'
        assert {(rule.rule, rule.endpoint) for rule in app.url_map.iter_rules()} >= {('/admin/', 'admin.peliculas'), ('/admin/peliculas', 'admin.peliculas'), ('/admin/cargar-pelicula', 'admin.admin_salas_funciones')}
        with patch('routes.main_routes.obtener_peliculas', return_value=[]), patch('routes.main_routes.obtener_funciones', return_value=[]), patch('routes.main_routes.obtener_sucursales', return_value=[]):
            assert cliente.get('/').status_code == 200
    print('Pruebas del dashboard: OK')
    return None


if __name__ == '__main__':
    ejecutar_pruebas()
