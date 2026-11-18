# Documentación de Endpoints — Frontend Cine Paradiso

> El Frontend es una aplicación BFF (*Backend for Frontend*) desarrollada en **Flask + Jinja2** (`puerto 5001`) que renderiza plantillas HTML y se comunica exclusivamente con el Backend API REST (`puerto 5000`) mediante la librería **`requests` de Python** (sin peticiones `fetch`, `axios` ni `XMLHttpRequest` desde el navegador).
>
> Como los formularios HTML solo admiten `GET` y `POST`, las operaciones que en el Backend utilizan `PATCH` o `DELETE` se reciben por `POST` en el Frontend y se traducen al verbo HTTP correspondiente hacia la API REST, propagando la cookie de sesión (`session["backend_session"]`).

---

## 1. Autenticación y Sesión (`routes/auth_routes.py`)

| Método | Ruta Frontend | Acceso | Consume en Backend | Parámetros / Formulario y Comportamiento |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/registro` | Público | — | Renderiza `pages/login_registro.html` en modo registro. |
| `POST` | `/registro` | Público | `POST /api/usuarios` | Recibe `nombre`, `email` y `password`. Si se crea (`201`), redirige a `/login`. |
| `GET` | `/login` | Público | — | Renderiza `pages/login_registro.html` en modo inicio de sesión. |
| `POST` | `/login` | Público | `POST /api/sesiones` | Recibe `email` y `password`. Guarda `id_usuario`, `nombre`, `rol` y `backend_session` en sesión y redirige a `/`. |
| `POST` | `/logout` | Autenticado | `DELETE /api/sesiones` | Cierra la sesión en el Backend, limpia la sesión local de Flask y redirige a `/login`. |

---

## 2. Cartelera, Películas y Perfil (`routes/main_routes.py`)

| Método | Ruta Frontend | Acceso | Consume en Backend | Parámetros / Formulario y Comportamiento |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Público | `GET /api/peliculas`<br>`GET /api/sucursales`<br>`GET /api/funciones` | Renderiza la cartelera (`pages/index.html`). Admite filtros por query params: `genero`, `id_sucursal` y `fecha`. |
| `GET` | `/pelicula/<int:id_pelicula>` | Público | `GET /api/peliculas/<id_pelicula>`<br>`GET /api/funciones`<br>`GET /api/sucursales` | Renderiza el detalle de la película (`pages/pelicula_detalle.html`) y sus funciones filtrables por `id_sucursal` y `fecha`. Devuelve `404` si no existe. |
| `GET` | `/perfil` | Autenticado | `GET /api/perfil` | Renderiza `pages/perfil.html` con los datos del usuario, su historial de compras y las películas asistidas (`estado_qr == "USADO"`). |

---

## 3. Compra de Entradas, Servicios y Mis Compras (`routes/main_routes.py`)

| Método | Ruta Frontend | Acceso | Consume en Backend | Parámetros / Formulario y Comportamiento |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/funciones/<int:id_funcion>/butacas` | Público | `GET /api/funciones/<id_funcion>`<br>`GET /api/peliculas/<id_pelicula>`<br>`GET /api/funciones/<id_funcion>/asientos` | Renderiza la grilla visual de butacas libres y ocupadas agrupadas por fila (`pages/seleccion_butacas.html`). |
| `POST` | `/funciones/<int:id_funcion>/butacas` | Público | `GET /api/funciones/<id_funcion>`<br>`GET /api/funciones/<id_funcion>/asientos` | Recibe `asientos_ids` (entre 1 y 6 butacas), almacena la selección en `session["compra_pendiente"]` y `session["compra_actual"]`, y redirige a `/compras/servicios`. |
| `GET` | `/compras/servicios` | Solo `CLIENTE` | `GET /api/servicios` | Renderiza `pages/seleccion_servicios.html` con el catálogo de servicios adicionales opcionales. Requiere selección previa de butacas. |
| `POST` | `/compras/servicios` | Solo `CLIENTE` | `GET /api/servicios`<br>`POST /api/compras` | Recibe cantidades (`servicio_<id_servicio>`, de `0` a `10`) y confirma la compra completa. Si hay conflicto de butacas (`409`), redirige a `/funciones/<id_funcion>/butacas`; si es exitosa (`201`), redirige a `/perfil`. |
| `GET` | `/mis-compras/<int:id_compra>` | Autenticado | `GET /api/compras/<id_compra>`<br>`GET /api/funciones/<id_funcion>` | Renderiza `pages/compra_detalle.html` con las entradas, servicios y el código QR generado en Data URL (cuando `estado_qr == "PENDIENTE"`). |
| `POST` | `/mis-compras/<int:id_compra>/cancelacion` | Autenticado | `PATCH /api/compras/<id_compra>` | Envía `{"estado_qr": "CANCELADO"}` para cancelar una compra vigente y redirige a `/perfil` con el resultado. |

---

## 4. Backoffice de Administración (`routes/admin_routes.py`)

| Método | Ruta Frontend | Acceso | Consume en Backend | Parámetros / Formulario y Comportamiento |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/admin/`<br>`/admin/peliculas`<br>`/admin/cargar-pelicula` | Solo `ADMIN` | `GET /api/sucursales`<br>`GET /api/sucursales/<id>/salas`<br>`GET /api/peliculas`<br>`GET /api/funciones`<br>`GET /api/peliculas-externas?q=...` | Renderiza `pages/admin_cargar_pelicula.html`. Si recibe el query param `busqueda_tmdb`, consulta candidatos en TMDb para importarlos. |
| `POST` | `/admin/peliculas` | Solo `ADMIN` | `POST /api/peliculas` | Recibe `titulo`, `sinopsis`, `poster_url`, `genero`, `duracion_min` y `clasificacion`, persiste la película en el catálogo local y redirige a `/admin/peliculas`. |
| `POST` | `/admin/salas` | Solo `ADMIN` | `POST /api/sucursales/<id_sucursal>/salas` | Recibe `id_sucursal`, `nombre` y `capacidad` para crear una sala con sus butacas y redirige a `/admin/peliculas`. |
| `POST` | `/admin/salas/eliminar/<int:id_sucursal>/<int:id_sala>` | Solo `ADMIN` | `DELETE /api/sucursales/<id_sucursal>/salas/<id_sala>` | Elimina la sala indicada (si no tiene funciones ni entradas asociadas) y redirige a `/admin/peliculas`. |
| `POST` | `/admin/funciones` | Solo `ADMIN` | `POST /api/funciones` | Recibe `id_pelicula`, `id_sala`, `fecha_hora` (convertida a zona horaria `-03:00`) y `precio_entrada`, crea la función y redirige a `/admin/peliculas`. |
| `POST` | `/admin/funciones/eliminar/<int:id_funcion>` | Solo `ADMIN` | `DELETE /api/funciones/<id_funcion>` | Elimina una función sin entradas vendidas y redirige a `/admin/peliculas`. |
| `GET` | `/admin/servicios` | Solo `ADMIN` | `GET /api/servicios` | Renderiza `pages/admin_abm_servicios.html` con el listado de servicios adicionales. |
| `GET` | `/admin/validador` | Solo `ADMIN` | `GET /api/funciones` | Renderiza `pages/admin_validador.html` para ingresar o escanear códigos QR en puerta. |
| `POST` | `/admin/validador` | Solo `ADMIN` | `PATCH /api/codigos-qr/<codigo_qr>`<br>`GET /api/funciones` | Recibe `codigo_qr` e `id_funcion`, valida el ingreso y muestra en pantalla si el acceso fue `permitido` o `denegado`. |
| `GET` | `/admin/dashboard` | Solo `ADMIN` | `GET /api/estadisticas/ocupacion`<br>`GET /api/estadisticas/ventas-por-genero`<br>`GET /api/estadisticas/franjas-horarias`<br>`GET /api/estadisticas/cancelaciones`<br>`GET /api/peliculas`<br>`GET /api/funciones` | Renderiza `pages/admin_dashboard.html`. Admite filtros opcionales por query params `id_pelicula` e `id_funcion` para la ocupación. |
| `GET` | `/admin/estadisticas/reporte-pdf` | Solo `ADMIN` | `GET /api/estadisticas/reporte-pdf` | Descarga directamente el archivo binario `reporte-cine-paradiso.pdf` (`application/pdf`). |
