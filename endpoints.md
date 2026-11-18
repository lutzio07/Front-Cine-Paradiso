# Documentación de Endpoints — Cine Paradiso

* **Arquitectura:** Frontend BFF (Flask + Jinja2) → `Python requests` → Backend API REST (Flask) → MySQL 8
* **Contrato OpenAPI:** `swagger.yaml` v2.1.0 (`http://localhost:5000`)
* **Formato de intercambio:** `application/json`
* **Autenticación:** Cookie de sesión de Flask (`session`), propagada por el Frontend mediante `session["backend_session"]`.

---

## Convenciones Generales

### Niveles de acceso
* **Público:** No requiere sesión activa.
* **Autenticado (`CLIENTE` / `ADMIN`):** Requiere cookie de sesión válida (`401` si no está autenticado).
* **Solo `CLIENTE`:** Requiere sesión activa con rol `CLIENTE` (`403` si tiene otro rol).
* **Solo `ADMIN`:** Requiere sesión activa con rol `ADMIN` (`403` si no es administrador).

### Formato estándar de respuestas

**Éxito (`200`, `201`):**
```json
{
  "status": "success",
  "data": {}
}
```

**Error (`400`, `401`, `403`, `404`, `405`, `409`, `500`):**
```json
{
  "status": "error",
  "code": "CODIGO_DE_ERROR",
  "message": "Descripción legible del error"
}
```

---

## Parte 1: API REST del Backend (`/api`)

### 1. Estado del Sistema

#### `GET /api/health`
* **Acceso:** Público
* **Descripción:** Verifica que el servidor Backend Flask esté activo y respondiendo.
* **Parámetros / Body:** Ninguno.
* **Respuestas:**
  * `200`: `{"status": "success", "message": "Backend Cine Paradiso activo y funcionando correctamente"}`

---

### 2. Autenticación, Usuarios y Perfil

#### `POST /api/usuarios`
* **Acceso:** Público
* **Descripción:** Registra un nuevo usuario con rol `CLIENTE`.
* **Body JSON:**
  ```json
  {
    "nombre": "Ana García",
    "email": "ana@example.com",
    "password": "clave_segura123"
  }
  ```
  * `nombre`: `string` (obligatorio, máx. 100 caracteres).
  * `email`: `string` (obligatorio, formato email válido, único, máx. 100 caracteres).
  * `password`: `string` (obligatorio, mín. 6 caracteres).
* **Respuestas:**
  * `201`: Usuario creado (`id_usuario`, `nombre`, `email`, `rol: "CLIENTE"`).
  * `400`: Datos faltantes o con formato inválido.
  * `409`: El correo electrónico ya se encuentra registrado.

#### `POST /api/sesiones`
* **Acceso:** Público
* **Descripción:** Autentica credenciales, inicia la sesión en Flask (cookie `session`) y devuelve los datos básicos del usuario.
* **Body JSON:**
  ```json
  {
    "email": "ana@example.com",
    "password": "clave_segura123"
  }
  ```
* **Respuestas:**
  * `200`: Sesión iniciada (`id_usuario`, `nombre`, `email`, `rol`).
  * `400`: Credenciales faltantes o mal formadas.
  * `401`: Email o contraseña incorrectos.

#### `DELETE /api/sesiones`
* **Acceso:** Autenticado (`CLIENTE` o `ADMIN`)
* **Descripción:** Cierra e invalida la sesión activa del usuario.
* **Parámetros / Body:** Ninguno.
* **Respuestas:**
  * `204`: Sesión cerrada correctamente (sin cuerpo).
  * `401`: No autenticado.

#### `GET /api/me`
* **Acceso:** Autenticado (`CLIENTE` o `ADMIN`)
* **Descripción:** Devuelve los datos básicos del usuario actualmente autenticado en la sesión.
* **Parámetros / Body:** Ninguno.
* **Respuestas:**
  * `200`: Objeto `Usuario` (`id_usuario`, `nombre`, `email`, `rol`).
  * `401`: No autenticado.

#### `GET /api/perfil`
* **Acceso:** Autenticado (`CLIENTE` o `ADMIN`)
* **Descripción:** Devuelve los datos del usuario autenticado junto con su historial completo de compras.
* **Parámetros / Body:** Ninguno.
* **Respuestas:**
  * `200`: Objeto `{"usuario": {...}, "compras": [...]}`.
  * `401`: No autenticado.

#### `POST /api/recuperar-password` *(Contrato Swagger — integración en rama pendiente)*
* **Acceso:** Público
* **Descripción:** Genera un token firmado temporal (válido por 30 minutos y de un solo uso) y envía el enlace de restablecimiento si el correo existe. Devuelve siempre respuesta neutra para evitar enumeración de cuentas.
* **Body JSON:**
  ```json
  {
    "email": "ana@example.com",
    "frontend_url": "http://localhost:5001"
  }
  ```
* **Respuestas:**
  * `200`: `{"status": "success", "data": {"message": "Si el correo está registrado, te enviamos un enlace para restablecer tu contraseña."}}`
  * `400`: Email faltante o inválido.
  * `500`: Error interno o falla en el servicio de correo.

#### `POST /api/restablecer-password` *(Contrato Swagger — integración en rama pendiente)*
* **Acceso:** Público
* **Descripción:** Valida la firma y vigencia del token temporal y actualiza la contraseña del usuario.
* **Body JSON:**
  ```json
  {
    "token": "<token_firmado>",
    "password": "nueva_clave_123"
  }
  ```
* **Respuestas:**
  * `200`: `{"status": "success", "data": {"message": "Contraseña actualizada correctamente. Ya podés iniciar sesión."}}`
  * `400`: Token inválido/expirado o contraseña menor a 6 caracteres.
  * `500`: Error interno del servidor.

---

### 3. Películas y Reseñas

#### `GET /api/peliculas`
* **Acceso:** Público
* **Descripción:** Lista las películas cargadas en el catálogo local.
* **Query Params (opcionales):**
  * `genero` (`string`): Filtra por género exacto/coincidente.
  * `titulo` (`string`): Filtra por coincidencia en el título.
* **Respuestas:**
  * `200`: Lista de películas (`id_pelicula`, `titulo`, `sinopsis`, `poster_url`, `genero`, `duracion_min`, `clasificacion`).

#### `POST /api/peliculas`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Persiste una película en el catálogo local de la base de datos.
* **Body JSON:**
  ```json
  {
    "titulo": "Gladiator II",
    "sinopsis": "Lucio ingresa al Coliseo para luchar por el destino de Roma.",
    "poster_url": "[https://image.tmdb.org/t/p/w500/demo1.jpg](https://image.tmdb.org/t/p/w500/demo1.jpg)",
    "genero": "Acción",
    "duracion_min": 148,
    "clasificacion": "+16"
  }
  ```
* **Respuestas:**
  * `201`: Película creada en el catálogo local.
  * `400`: Campos obligatorios faltantes o `duracion_min <= 0`.
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.
  * `409`: La película ya existe en el catálogo local.

#### `GET /api/peliculas/<int:id_pelicula>`
* **Acceso:** Público
* **Descripción:** Obtiene el detalle de una película específica por su ID.
* **Path Params:** `id_pelicula` (`integer >= 1`).
* **Respuestas:**
  * `200`: Objeto `Pelicula`.
  * `404`: Película no encontrada.

#### `GET /api/peliculas-externas`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Consulta películas en la API externa (TMDb) por palabra clave sin guardarlas en MySQL.
* **Query Params:**
  * `q` (`string`, obligatorio): Término de búsqueda.
* **Respuestas:**
  * `200`: Lista de candidatos externos (`id_externo`, `titulo`, `sinopsis`, `poster_url`, `duracion_min`, `clasificacion`, `genero`).
  * `400`: Falta el parámetro `q`.
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.
  * `500`: Error al comunicarse con la API externa.

#### `GET /api/peliculas/<int:id_pelicula>/resenas` *(Contrato Swagger — integración en rama pendiente)*
* **Acceso:** Público
* **Descripción:** Lista las reseñas publicadas para una película.
* **Path Params:** `id_pelicula` (`integer >= 1`).
* **Respuestas:**
  * `200`: Lista de reseñas (`id_resena`, `id_usuario`, `nombre_usuario`, `id_pelicula`, `puntuacion`, `comentario`, `fecha`).
  * `404`: Película no encontrada.

#### `POST /api/peliculas/<int:id_pelicula>/resenas` *(Contrato Swagger — integración en rama pendiente)*
* **Acceso:** Autenticado (`CLIENTE` que posea una compra de esa película con `estado_qr = 'USADO'`)
* **Descripción:** Registra la calificación (1 a 5) y comentario opcional de un espectador que asistió a la película.
* **Path Params:** `id_pelicula` (`integer >= 1`).
* **Body JSON:**
  ```json
  {
    "puntuacion": 5,
    "comentario": "Excelente película y muy buena sala."
  }
  ```
* **Respuestas:**
  * `201`: Reseña creada.
  * `400`: Puntuación fuera de rango (1–5) o datos inválidos.
  * `401`: No autenticado.
  * `403`: El usuario no tiene una entrada validada (`USADO`) para esa película.
  * `404`: Película no encontrada.
  * `409`: El usuario ya publicó una reseña para esta película.

---

### 4. Sucursales y Salas

#### `GET /api/sucursales`
* **Acceso:** Público
* **Descripción:** Lista todas las sucursales de Cine Paradiso.
* **Respuestas:**
  * `200`: Lista de sucursales (`id_sucursal`, `nombre`, `direccion`, `ciudad`).

#### `GET /api/sucursales/<int:id_sucursal>/salas`
* **Acceso:** Público
* **Descripción:** Lista las salas pertenecientes a una sucursal.
* **Path Params:** `id_sucursal` (`integer >= 1`).
* **Respuestas:**
  * `200`: Lista de salas (`id_sala`, `id_sucursal`, `nombre`, `capacidad`).
  * `404`: Sucursal no encontrada.

#### `POST /api/sucursales/<int:id_sucursal>/salas`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Crea una sala dentro de la sucursal indicada y genera automáticamente sus registros de butacas en `asientos` según `capacidad`.
* **Path Params:** `id_sucursal` (`integer >= 1`).
* **Body JSON:**
  ```json
  {
    "nombre": "Sala 3",
    "capacidad": 30
  }
  ```
* **Respuestas:**
  * `201`: Sala creada (`id_sala`, `id_sucursal`, `nombre`, `capacidad`).
  * `400`: Nombre inválido o capacidad no positiva.
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.
  * `404`: Sucursal inexistente.
  * `409`: Conflicto (nombre de sala duplicado en la sucursal).

#### `DELETE /api/sucursales/<int:id_sucursal>/salas/<int:id_sala>`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Elimina una sala siempre que pertenezca a la sucursal y no tenga funciones ni entradas asociadas.
* **Path Params:** `id_sucursal` (`integer >= 1`), `id_sala` (`integer >= 1`).
* **Respuestas:**
  * `200`: `{"status": "success", "data": {"id_sucursal": 1, "id_sala": 2}, "message": "Sala eliminada correctamente"}`
  * `400`: ID inválido.
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.
  * `404`: Sucursal o sala inexistente, o la sala no pertenece a esa sucursal.
  * `409`: La sala tiene funciones o entradas asociadas.
  * `500`: Error interno del servidor.

---

### 5. Funciones y Disponibilidad de Asientos

#### `GET /api/funciones`
* **Acceso:** Público
* **Descripción:** Lista funciones programadas con información de película, sala y sucursal.
* **Query Params (opcionales):**
  * `id_pelicula` (`integer >= 1`)
  * `id_sucursal` (`integer >= 1`)
  * `fecha` (`date`, formato `YYYY-MM-DD`)
* **Respuestas:**
  * `200`: Lista de funciones (`id_funcion`, `id_pelicula`, `titulo_pelicula`, `id_sala`, `nombre_sala`, `id_sucursal`, `nombre_sucursal`, `fecha_hora`, `precio_entrada`).
  * `400`: Parámetros de filtro inválidos.

#### `POST /api/funciones`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Programa una nueva función en una sala validando que no exista solapamiento horario con otras proyecciones de esa misma sala.
* **Body JSON:**
  ```json
  {
    "id_pelicula": 1,
    "id_sala": 1,
    "fecha_hora": "2026-11-05T20:00:00-03:00",
    "precio_entrada": 4500.0
  }
  ```
* **Respuestas:**
  * `201`: Función creada.
  * `400`: Datos faltantes, fecha/hora inválida o precio negativo.
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.
  * `404`: Película o sala inexistente.
  * `409`: Solapamiento horario con otra función en la misma sala.

#### `GET /api/funciones/<id_funcion>`
* **Acceso:** Público
* **Descripción:** Obtiene el detalle completo de una función.
* **Path Params:** `id_funcion` (`integer >= 1`).
* **Respuestas:**
  * `200`: Objeto `Funcion`.
  * `400`: ID inválido.
  * `404`: Función no encontrada.

#### `DELETE /api/funciones/<int:id_funcion>`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Elimina una función programada siempre que no tenga entradas asociadas.
* **Path Params:** `id_funcion` (`integer >= 1`).
* **Respuestas:**
  * `200`: `{"status": "success", "data": {"id_funcion": 1}, "message": "Función eliminada correctamente"}`
  * `400`: ID inválido.
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.
  * `404`: Función no encontrada.
  * `409`: La función posee entradas vendidas asociadas.
  * `500`: Error interno del servidor.

#### `GET /api/funciones/<id_funcion>/asientos`
* **Acceso:** Público
* **Descripción:** Devuelve la grilla de asientos de la sala indicando si cada butaca está `DISPONIBLE` u `OCUPADO` para la función consultada.
* **Path Params:** `id_funcion` (`integer >= 1`).
* **Respuestas:**
  * `200`: Lista de asientos (`id_asiento`, `fila`, `numero`, `estado`).
  * `400`: ID inválido.
  * `404`: Función no encontrada.

---

### 6. Servicios Adicionales

#### `GET /api/servicios`
* **Acceso:** Público
* **Descripción:** Lista el catálogo global de servicios adicionales (comida, bebidas, combos, estacionamiento, acceso VIP, otros).
* **Respuestas:**
  * `200`: Lista de servicios (`id_servicio`, `nombre`, `descripcion`, `tipo`, `precio`).

#### `POST /api/servicios`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Crea un nuevo servicio adicional en el catálogo.
* **Body JSON:**
  ```json
  {
    "nombre": "Combo Popcorn + Gaseosa",
    "descripcion": "Balde grande de pochoclos y gaseosa 500ml",
    "tipo": "COMBO",
    "precio": 3500.0
  }
  ```
  * `tipo`: `COMIDA` | `BEBIDA` | `COMBO` | `ESTACIONAMIENTO` | `VIP` | `OTRO`.
* **Respuestas:**
  * `201`: Servicio creado.
  * `400`: Datos faltantes, tipo no admitido o precio inválido.
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.
  * `409`: Conflicto con servicio existente.

#### `GET /api/servicios/<int:id_servicio>`
* **Acceso:** Público
* **Descripción:** Consulta el detalle de un servicio específico.
* **Path Params:** `id_servicio` (`integer >= 1`).
* **Respuestas:**
  * `200`: Objeto `Servicio`.
  * `404`: Servicio no encontrado.

#### `PATCH /api/servicios/<int:id_servicio>`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Actualiza parcialmente uno o más atributos (`nombre`, `descripcion`, `tipo`, `precio`) de un servicio existente.
* **Path Params:** `id_servicio` (`integer >= 1`).
* **Body JSON:** Campos opcionales a modificar.
* **Respuestas:**
  * `200`: Servicio actualizado.
  * `400`: Ningún campo válido enviado o valores incorrectos.
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.
  * `404`: Servicio no encontrado.

#### `DELETE /api/servicios/<int:id_servicio>`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Elimina un servicio del catálogo si no posee compras históricas asociadas.
* **Path Params:** `id_servicio` (`integer >= 1`).
* **Respuestas:**
  * `204`: Servicio eliminado (sin contenido).
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.
  * `404`: Servicio no encontrado.
  * `409`: El servicio tiene compras asociadas y no puede eliminarse.

---

### 7. Compras

#### `POST /api/compras`
* **Acceso:** Autenticado (`CLIENTE`)
* **Descripción:** Registra una compra completa para una función, asigna las butacas, agrega los servicios opcionales, calcula el `monto_total` en el servidor, genera el `codigo_qr` único en estado `PENDIENTE` y envía el comprobante con QR al correo del cliente.
* **Body JSON:**
  ```json
  {
    "id_funcion": 1,
    "asientos_ids": [1, 2],
    "servicios": [
      { "id_servicio": 1, "cantidad": 2 }
    ]
  }
  ```
* **Respuestas:**
  * `201`: Objeto `CompraDetalle` (`compra`, `entradas`, `servicios`).
  * `400`: Función inválida, lista de asientos vacía/repetida o cantidades de servicio inválidas.
  * `401`: No autenticado.
  * `403`: Solo usuarios con rol `CLIENTE` pueden comprar.
  * `404`: Función, asiento o servicio inexistente.
  * `409`: Uno o más asientos seleccionados ya fueron ocupados.

#### `GET /api/compras/<int:id_compra>`
* **Acceso:** Autenticado (propietario de la compra o `ADMIN`)
* **Descripción:** Obtiene el detalle completo de una compra, incluyendo entradas, servicios contratados y código QR.
* **Path Params:** `id_compra` (`integer >= 1`).
* **Respuestas:**
  * `200`: Objeto `CompraDetalle` (`compra`, `entradas`, `servicios`).
  * `401`: No autenticado.
  * `403`: La compra pertenece a otro usuario.
  * `404`: Compra no encontrada.

#### `PATCH /api/compras/<int:id_compra>`
* **Acceso:** Autenticado (propietario de la compra)
* **Descripción:** Cancela una compra confirmada siempre que `estado_qr` sea `PENDIENTE` y falten al menos **60 minutos** para el inicio de la función. Cambia el estado a cancelado y elimina las filas en `entradas` para liberar las butacas.
* **Path Params:** `id_compra` (`integer >= 1`).
* **Body JSON:**
  ```json
  {
    "estado_qr": "CANCELADO"
  }
  ```
* **Respuestas:**
  * `200`: Compra cancelada y detalle actualizado.
  * `400`: Cuerpo de solicitud inválido.
  * `401`: No autenticado.
  * `403`: La compra no pertenece al usuario autenticado.
  * `404`: Compra no encontrada.
  * `409`: El QR ya fue usado/cancelado o faltan menos de 60 minutos para la función.

---

### 8. Control de Acceso en Sala

#### `PATCH /api/codigos-qr/<codigo_qr>`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Valida un código QR presentado en puerta para una función específica y cambia su `estado_qr` de `PENDIENTE` a `USADO`. Solo permite el ingreso dentro de la ventana habilitada (**desde 40 minutos antes** del inicio de la función hasta la finalización de la película).
* **Path Params:** `codigo_qr` (`string`).
* **Body JSON:**
  ```json
  {
    "id_funcion": 1
  }
  ```
* **Respuestas:**
  * `200`: `{"codigo_qr": "QR-8F92A1B3", "estado_qr": "USADO"}`
  * `400`: Falta `id_funcion` o formato inválido.
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.
  * `404`: Código QR o función inexistente.
  * `409`: QR ya `USADO` o `CANCELADO`, no corresponde a la función indicada o fuera de la ventana horaria permitida.

---

### 9. Estadísticas y Reportes

#### `GET /api/estadisticas/ocupacion`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Devuelve capacidad, entradas vendidas y porcentaje de ocupación por función.
* **Query Params (opcionales):** `id_funcion` (`integer >= 1`), `id_pelicula` (`integer >= 1`).
* **Respuestas:**
  * `200`: Lista de métricas (`id_funcion`, `titulo_pelicula`, `nombre_sala`, `fecha_hora`, `capacidad`, `entradas_vendidas`, `porcentaje_ocupacion`).
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.

#### `GET /api/estadisticas/ventas-por-genero`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Devuelve el total recaudado y entradas vendidas agrupadas por género cinematográfico.
* **Respuestas:**
  * `200`: Lista de métricas (`genero`, `total_ventas`, `entradas_vendidas`).
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.

#### `GET /api/estadisticas/franjas-horarias`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Devuelve la cantidad de entradas vendidas agrupadas por horario de función.
* **Respuestas:**
  * `200`: Lista de métricas (`hora`, `entradas_vendidas`).
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.

#### `GET /api/estadisticas/cancelaciones`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Devuelve el conteo total de compras canceladas.
* **Respuestas:**
  * `200`: `{"total_cancelaciones": 2}`
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.

#### `GET /api/estadisticas/reporte-pdf`
* **Acceso:** Solo `ADMIN`
* **Descripción:** Genera y descarga el informe consolidado de estadísticas en formato PDF.
* **Respuestas:**
  * `200`: Archivo binario `application/pdf`.
  * `401`: No autenticado.
  * `403`: Requiere rol `ADMIN`.
  * `500`: Error al generar el PDF.

---

## Parte 2: Rutas Web BFF del Frontend Flask (`puerto 5001`)

> El Frontend renderiza plantillas Jinja2 y nunca ejecuta `fetch` ni `axios` desde el navegador. Todas las interacciones con el Backend se resuelven desde Python usando `requests` y reenviando la cookie `session["backend_session"]`.

### 1. Autenticación (`routes/auth_routes.py`)

| Método | Ruta Frontend | Acceso | Endpoint Backend consumido | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/registro` | Público | — | Renderiza `pages/login_registro.html` en modo registro. |
| `POST` | `/registro` | Público | `POST /api/usuarios` | Procesa el alta de cliente y redirige a `/login`. |
| `GET` | `/login` | Público | — | Renderiza `pages/login_registro.html` en modo login. |
| `POST` | `/login` | Público | `POST /api/sesiones` | Inicia sesión y guarda `id_usuario`, `nombre`, `rol` y `backend_session`. |
| `POST` | `/logout` | Autenticado | `DELETE /api/sesiones` | Cierra la sesión en Backend y limpia la sesión local del Front. |

### 2. Cartelera, Compra y Perfil (`routes/main_routes.py`)

| Método | Ruta Frontend | Acceso | Endpoints Backend consumidos | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Público | `GET /api/peliculas`, `GET /api/sucursales`, `GET /api/funciones` | Cartelera principal con filtros por `genero`, `id_sucursal` y `fecha`. |
| `GET` | `/pelicula/<int:id_pelicula>` | Público | `GET /api/peliculas/<id>`, `GET /api/funciones`, `GET /api/sucursales` | Ficha de película y horarios disponibles filtrables. |
| `GET` | `/funciones/<int:id_funcion>/butacas` | Público | `GET /api/funciones/<id>`, `GET /api/peliculas/<id>`, `GET /api/funciones/<id>/asientos` | Mapa visual de butacas disponibles y ocupadas por fila. |
| `POST` | `/funciones/<int:id_funcion>/butacas` | Público | `GET /api/funciones/<id>`, `GET /api/funciones/<id>/asientos` | Valida selección (1 a 6 butacas), guarda en `session["compra_pendiente"]` y redirige a `/compras/servicios`. |
| `GET` | `/compras/servicios` | Solo `CLIENTE` | `GET /api/servicios` | Pantalla de selección opcional de servicios adicionales. |
| `POST` | `/compras/servicios` | Solo `CLIENTE` | `GET /api/servicios`, `POST /api/compras` | Confirma la compra completa (entradas + servicios) y redirige a `/perfil`. |
| `GET` | `/perfil` | Autenticado | `GET /api/perfil` | Muestra datos del usuario, historial de compras y películas vistas (`estado_qr == "USADO"`). |
| `GET` | `/mis-compras/<int:id_compra>` | Autenticado | `GET /api/compras/<id>`, `GET /api/funciones/<id>` | Detalle de una compra con sus butacas, servicios y código QR renderizado. |
| `POST` | `/mis-compras/<int:id_compra>/cancelacion` | Autenticado | `PATCH /api/compras/<id>` | Solicita la cancelación de una compra vigente. |

### 3. Backoffice de Administración (`routes/admin_routes.py`)

| Método | Ruta Frontend | Acceso | Endpoints Backend consumidos | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/admin/`, `/admin/peliculas`, `/admin/cargar-pelicula` | Solo `ADMIN` | `GET /api/peliculas-externas`, `GET /api/peliculas`, `GET /api/sucursales`, `GET /api/sucursales/<id>/salas`, `GET /api/funciones` | Panel de gestión de catálogo externo (TMDb), salas y funciones. |
| `POST` | `/admin/peliculas` | Solo `ADMIN` | `POST /api/peliculas` | Importa una película buscada en TMDb al catálogo local. |
| `POST` | `/admin/salas` | Solo `ADMIN` | `POST /api/sucursales/<id_sucursal>/salas` | Da de alta una nueva sala en una sucursal. |
| `POST` | `/admin/salas/eliminar/<int:id_sucursal>/<int:id_sala>` | Solo `ADMIN` | `DELETE /api/sucursales/<id_sucursal>/salas/<id_sala>` | Elimina una sala sin funciones ni entradas asociadas. |
| `POST` | `/admin/funciones` | Solo `ADMIN` | `POST /api/funciones` | Programa una nueva función en sala con fecha, hora y precio. |
| `POST` | `/admin/funciones/eliminar/<int:id_funcion>` | Solo `ADMIN` | `DELETE /api/funciones/<id_funcion>` | Elimina una función sin entradas vendidas. |
| `GET` | `/admin/servicios` | Solo `ADMIN` | `GET /api/servicios` | Vista de administración del catálogo de servicios. |
| `GET` | `/admin/validador` | Solo `ADMIN` | `GET /api/funciones` | Pantalla de control de acceso y escaneo/ingreso de código QR. |
| `POST` | `/admin/validador` | Solo `ADMIN` | `PATCH /api/codigos-qr/<codigo_qr>`, `GET /api/funciones` | Valida un código QR contra la función seleccionada y muestra acceso permitido o denegado. |
| `GET` | `/admin/dashboard` | Solo `ADMIN` | `GET /api/estadisticas/ocupacion`, `ventas-por-genero`, `franjas-horarias`, `cancelaciones`, `GET /api/peliculas`, `GET /api/funciones` | Tablero analítico con métricas y filtros por película o función. |
| `GET` | `/admin/estadisticas/reporte-pdf` | Solo `ADMIN` | `GET /api/estadisticas/reporte-pdf` | Descarga el archivo `reporte-cine-paradiso.pdf`. |
