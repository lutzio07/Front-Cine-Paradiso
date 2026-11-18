# Cine Paradiso — Frontend Web (BFF Flask + Jinja2)

Aplicación web del sistema de venta de entradas de cine **Cine Paradiso**, desarrollada como Proyecto Integrador para la cátedra **Introducción al Desarrollo de Software (FIUBA)**. Implementa la interfaz pública de cartelera y compra de entradas para clientes (`CLIENTE`), así como el panel de administración (`ADMIN`) para gestión de películas, salas, funciones, validación de códigos QR y visualización de estadísticas.

---

## 🔗 Estructura del Proyecto
Este sistema de venta de entradas está compuesto por dos repositorios complementarios:

*   **[Backend (API REST)](https://github.com/Fachaso/Backend-Cine-Paradiso):** Desarrollado en Flask, maneja la lógica de negocio, la conexión a la base de datos MySQL, el sistema de estadísticas y la seguridad de los endpoints.
*   **[Frontend (Interfaz de Usuario)](https://github.com/lutzio07/Front---Cine-Paradiso):** Contiene tanto la aplicación web de acceso para los usuarios finales como el backoffice para que los administradores configuren las salas y películas.

## Enlaces y Documentación del Proyecto

* **Diseño / Mockups:** [[https://www.figma.com/proto/sehm8206edP58cDz0Sj8f8/Figma-basics?node-id=3825-988&p=f&t=nzzL0frzXv6JGVMO-1&scaling=min-zoom&content-scaling=fixed&page-id=3825%3A5]
* **Documentación de Rutas Frontend:** [endpoints.md](./endpoints.md)

---

## Integrantes del Equipo

* Ramiro Tomas Martinez — `115961` — rtmartinez@fi.uba.ar — [@Fachaso](https://github.com/Fachaso)
* Juan Francisco Misiac — `116102` — jmisiac@fi.uba.ar
* Eliel Jone Castillo — `116526` — ejone@fi.uba.ar
* Lucas Nahuel Uran — `116478` — luran@fi.uba.ar
* Matias Ezequiel Montiel — `116556` — memontiel@fi.uba.ar
* Joaquín Transillo — `116250` — jtransillo@fi.uba.ar
* Jorge Félix García Sánchez — `116133` — jfgarcias@fi.uba.ar
* Diego Oliver Yujra Cossio — `116532` — dyujra@fi.uba.ar
* Maximiliano Alexis Silva — `115666` — masilva@fi.uba.ar
* Lucio Valentín Villagra — `116288` — lvillagra@fi.uba.ar

---

## Arquitectura del Sistema

El Frontend sigue el patrón **BFF (*Backend for Frontend*)** renderizado en servidor con **Flask y Jinja2**:

```text
[ Navegador (Responsive Web) ]
      │  (HTML / Formularios GET-POST, sin fetch/AJAX)
      ▼
[ Frontend BFF — Flask + Jinja2 ]  (Puerto 5001)
      │  (HTTP JSON + Cookie de sesión vía Python requests)
      ▼
[ Backend API REST — Flask ]       (Puerto 5000)
      │  (SQL explícito sin ORM)
      ▼
[ Base de Datos — MySQL 8.0+ ]
```

* **Comunicación exclusiva desde servidor:** Siguiendo las reglas de la cátedra, el navegador nunca realiza llamadas directas al Backend (`fetch`, `axios` o `XMLHttpRequest`). Todas las peticiones HTTP hacia la API REST se ejecutan en Python desde la capa `services/` mediante la librería `requests`.
* **Propagación de sesión:** Al autenticarse, el Frontend almacena la cookie de sesión del Backend (`session["backend_session"]`) junto con los datos de rol del usuario (`CLIENTE` o `ADMIN`) y la reenvía en cada operación protegida.
* **Adaptación de verbos HTTP:** Dado que los formularios HTML solo admiten `GET` y `POST`, las rutas del Frontend reciben `POST` y los servicios traducen la llamada al verbo REST correspondiente (`PATCH` o `DELETE`) hacia el Backend.

---

## Tecnologías y Versiones Utilizadas

* **Lenguaje:** Python 3.10 o superior
* **Framework Web y Plantillas:** Flask + Jinja2
* **Cliente HTTP:** `requests`
* **Variables de Entorno:** `python-dotenv`
* **Generación de Códigos QR en vista:** `qrcode[pil]` (renderizado en memoria como Data URL PNG base64)
* **Estilos y Maquetado:** HTML5, CSS3 responsive (`static/css/styles.css`) y JavaScript de interfaz local (`static/js/login_registro.js`)

---

## Estructura del Repositorio

```text
Front-Cine-Paradiso/
├── routes/                        # Blueprints Flask del Frontend (BFF)
│   ├── admin_routes.py            # Rutas de backoffice (/admin/*)
│   ├── auth_routes.py             # Registro, login y logout (/registro, /login, /logout)
│   └── main_routes.py             # Cartelera, detalle, butacas, compras y perfil
├── services/                      # Clientes HTTP (Python requests) y lógica de presentación
│   ├── __init__.py
│   ├── admin_service.py           # Operaciones administrativas contra la API REST
│   ├── api_client.py              # Cliente HTTP base y consultas públicas/compras
│   ├── auth_service.py            # Gestión de sesiones y registro contra /api
│   ├── butacas_service.py         # Agrupamiento matricial de butacas por fila
│   ├── cartelera_service.py       # Armado y filtrado de películas con funciones
│   ├── compras_service.py         # Consulta de detalle de compras
│   ├── estadisticas_service.py    # Consumo y validación de métricas y reporte PDF
│   ├── perfil_service.py          # Consulta de perfil e historial del cliente
│   └── qr_service.py              # Generación de QR en formato Data URL base64
├── static/                        # Recursos estáticos
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── login_registro.js
├── templates/                     # Plantillas HTML Jinja2
│   ├── components/                # Componentes reutilizables
│   │   ├── _form_crear_funcion.html
│   │   ├── _form_crear_sala.html
│   │   ├── _form_importar_pelicula.html
│   │   ├── _tabla_funciones.html
│   │   ├── _tabla_salas.html
│   │   ├── footer.html
│   │   └── navbar.html
│   ├── pages/                     # Vistas completas de la aplicación
│   │   ├── 404.html
│   │   ├── admin_cargar_pelicula.html
│   │   ├── admin_dashboard.html
│   │   ├── admin_validador.html
│   │   ├── compra_detalle.html
│   │   ├── index.html
│   │   ├── login_registro.html
│   │   ├── pelicula_detalle.html
│   │   ├── perfil.html
│   │   ├── seleccion_butacas.html
│   │   └── seleccion_servicios.html
│   ├── auth.html
│   ├── base.html
│   └── index.html
├── .env.example                   # Plantilla de variables de entorno
├── .gitignore
├── app.py                         # Fábrica de aplicación Flask (create_app) y punto de entrada
├── config.py                      # Carga de configuración desde variables de entorno
├── endpoints.md                   # Documentación de rutas del Frontend y consumo de API
├── init.sh                        # Script de instalación de dependencias
├── README.md
└── requirements.txt
```

---

## Instalación y Configuración en Local

> **Prerrequisito:** Para operar el Frontend es necesario tener ejecutándose previamente el **Backend API REST** en el puerto `5000` con la base de datos MySQL 8 inicializada (`schema.sql` y `seed.sql`).

### 1. Clonar el repositorio y crear el entorno virtual
```bash
git clone [https://github.com/lutzio07/Front---Cine-Paradiso.git](https://github.com/lutzio07/Front---Cine-Paradiso.git)
cd Front---Cine-Paradiso

python3 -m venv venv
source venv/bin/activate        # En Linux / macOS
# venv\Scripts\activate         # En Windows (PowerShell / CMD)
```

### 2. Instalar dependencias
Ejecutá el script `init.sh` o instalá directamente desde `requirements.txt`:
```bash
bash init.sh
# o bien:
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Copiá `.env.example` a `.env` y verificá los valores de configuración:
```bash
cp .env.example .env
```

| Variable | Obligatoria | Valor por defecto / Ejemplo | Descripción |
| :--- | :---: | :--- | :--- |
| `PORT` | No | `5001` | Puerto en el que escucha el servidor Frontend Flask. |
| `FLASK_ENV` | Sí | `development` | Entorno de ejecución de Flask (`development` / `production`). |
| `SECRET_KEY` | Sí | `clave_secreta_frontend_paradiso_2026` | Clave secreta para firmar la cookie de sesión del Frontend. |
| `FRONTEND_SECRET_KEY` | No | — | Clave alternativa opcional; si está definida, sobrescribe `SECRET_KEY`. |
| `BACKEND_URL` | Sí | `http://localhost:5000/api` | URL base de la API REST del Backend. |

---

## Ejecución

Con el Backend activo en `http://localhost:5000` y el entorno virtual activado, iniciá el servidor Frontend:

```bash
python app.py
```

Abrí en el navegador: **`http://localhost:5001`**

### Acceso de prueba
* **Panel Administrativo (`ADMIN`):** `admin@cineparadiso.com` / `admin123` (habilita el menú de gestión de películas TMDb, salas, funciones, validador de QR en puerta y dashboard de estadísticas).
* **Cliente (`CLIENTE`):** Podés registrar una cuenta nueva desde `/registro` para seleccionar funciones, elegir entre 1 y 6 butacas, agregar servicios adicionales, recibir el QR por email, visualizar el comprobante en `/perfil` y gestionar cancelaciones.

---

## Principales Decisiones de Diseño

* **Separación estricta Front / Back:** El Frontend no accede directamente a MySQL ni contiene reglas de persistencia; delega todas las validaciones críticas y cálculos de precios en la API REST mediante `requests`.
* **Flujo de compra en dos pasos sobre sesión:** La selección de butacas (`POST /funciones/<id>/butacas`) se resguarda temporalmente en la sesión del servidor (`compra_pendiente`) para permitir el agregado opcional de servicios adicionales en `/compras/servicios` antes de confirmar la transacción definitiva en `POST /api/compras`.
* **Renderizado de QR sin archivos temporales:** En la vista de detalle de compra (`/mis-compras/<id_compra>`), el código QR activo se genera en memoria como imagen PNG codificada en Base64 (`data:image/png;base64,...`) mediante `qr_service.py`, evitando escribir archivos en disco.
