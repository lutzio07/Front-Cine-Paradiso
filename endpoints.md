# Listado de Endpoints (Frontend)

> El front es una app Flask que renderiza templates y consume el backend con `requests` (sin fetch/AJAX desde el navegador). Los formularios HTML solo envían GET y POST: cuando el backend usa PATCH o DELETE, el front recibe un POST y llama al backend con el verbo correcto. Entre paréntesis se indica el endpoint del backend que consume cada ruta. Roles: administrador (`ADMIN`) y cliente (`CLIENTE`).

### 1. Usuarios y sesión
- `GET /registro` : Formulario de registro de cliente.
- `POST /registro` : Crea la cuenta de cliente. (`POST /api/usuarios`)
- `GET /login` : Formulario de inicio de sesión.
- `POST /login` : Inicia sesión. (`POST /api/sesiones`)
- `POST /logout` : Cierra la sesión. (`DELETE /api/sesiones`)
- `GET /perfil` : Datos del usuario, historial de compras y películas vistas. (`GET /api/perfil`)

### 2. Cartelera y detalle de película
- `GET /` : Cartelera con filtros por género, sucursal y fecha. (`GET /api/peliculas`, `GET /api/sucursales`, `GET /api/funciones`)
- `GET /pelicula/<int:id_pelicula>` : Detalle de la película y sus funciones, filtrables por sucursal y fecha. (`GET /api/peliculas/<id>`, `GET /api/funciones`, `GET /api/sucursales`)

### 3. Compra de entradas, servicios y mis compras
- `GET /funciones/<int:id_funcion>/butacas` : Mapa de butacas libres y ocupadas. (`GET /api/funciones/<id>`, `GET /api/peliculas/<id>`, `GET /api/funciones/<id>/asientos`)
- `POST /funciones/<int:id_funcion>/butacas` : Guarda en sesión las butacas elegidas (1 a 6) y redirige a servicios. (`GET /api/funciones/<id>`, `GET /api/funciones/<id>/asientos`)
- `GET /compras/servicios` : Selección opcional de servicios adicionales. (`GET /api/servicios`)
- `POST /compras/servicios` : Confirma la compra completa con entradas y servicios, genera el QR y envía el comprobante por mail. (`GET /api/servicios`, `POST /api/compras`)
- `GET /mis-compras/<int:id_compra>` : Detalle de una compra con entradas, servicios y su QR. (`GET /api/compras/<id>`, `GET /api/funciones/<id>`)
- `POST /mis-compras/<int:id_compra>/cancelacion` : Cancela la compra hasta 60 minutos antes de la función. (`PATCH /api/compras/<id>`)

### 4. Backoffice (Admin)
- `GET /admin/`, `GET /admin/peliculas`, `GET /admin/cargar-pelicula` : Panel de gestión de catálogo externo (TMDb), salas y funciones. (`GET /api/sucursales`, `GET /api/sucursales/<id>/salas`, `GET /api/peliculas`, `GET /api/funciones`, `GET /api/peliculas-externas`)
- `POST /admin/peliculas` : Importa una película al catálogo local. (`POST /api/peliculas`)
- `POST /admin/salas` : Crea una sala con sus butacas en una sucursal. (`POST /api/sucursales/<id>/salas`)
- `POST /admin/salas/eliminar/<int:id_sucursal>/<int:id_sala>` : Elimina una sala sin funciones ni entradas asociadas. (`DELETE /api/sucursales/<id>/salas/<id>`)
- `POST /admin/funciones` : Asigna película a sala, fecha y horario. (`POST /api/funciones`)
- `POST /admin/funciones/eliminar/<int:id_funcion>` : Elimina una función sin entradas vendidas. (`DELETE /api/funciones/<id>`)
- `GET /admin/servicios` : Listado de servicios adicionales. (`GET /api/servicios`)
- `GET /admin/validador` : Pantalla de validación del QR en el ingreso a la sala. (`GET /api/funciones`)
- `POST /admin/validador` : Valida el QR y lo marca como utilizado. (`PATCH /api/codigos-qr/<codigo_qr>`)
- `GET /admin/dashboard` : Panel de estadísticas con ocupación, ventas por género, franjas horarias y cancelaciones. (`GET /api/estadisticas/ocupacion`, `/ventas-por-genero`, `/franjas-horarias`, `/cancelaciones`, `GET /api/peliculas`, `GET /api/funciones`)
- `GET /admin/estadisticas/reporte-pdf` : Descarga el PDF de estadísticas. (`GET /api/estadisticas/reporte-pdf`)
