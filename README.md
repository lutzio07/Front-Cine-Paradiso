<div align="right">
    <img width="32px" src="img/logo_intro.desarrollo.software.png">
</div>

# Proyecto Integrador - Sistema de venta de entradas de cine

## 🔗 Estructura del Proyecto
Este sistema de venta de entradas está compuesto por dos repositorios complementarios:

*   **[Backend (API REST)](https://github.com/Fachaso/Backend-Cine-Paradiso):** Desarrollado en Flask, maneja la lógica de negocio, la conexión a la base de datos MySQL, el sistema de estadísticas y la seguridad de los endpoints.
*   **[Frontend (Interfaz de Usuario)](https://github.com/lutzio07/Front---Cine-Paradiso):** Contiene tanto la aplicación web de acceso para los usuarios finales como el backoffice para que los administradores configuren las salas y películas.

## Información de los estudiantes:

* Ramiro Tomas Martinez - 115961 - rtmartinez@fi.uba.ar - https://github.com/Fachaso
* Juan Francisco Misiac - 116102 - jmisiac@fi.uba.ar
* Eliel Jone Castillo - 116526 - ejone@fi.uba.ar
* Lucas Nahuel Uran -116478 - luran@fi.uba.ar
* Matias Ezequiel Montiel - 116556 -memontiel@fi.uba.ar
* Joaquín Transillo - 116250- jtransillo@fi.uba.ar
* Jorge Félix García Sánchez - 116133 - jfgarcias@fi.uba.ar
* Diego Oliver Yujra Cossio - 116532 - dyujra@fi.uba.ar
* Maximiliano Alexis Silva - 115666 - masilva@fi.uba.ar
* Lucio Valentin Villagra - 116288 - lvillagra@fi.uba.ar
---

## Enlaces del Proyecto (Hito 1)
* **Tablero Kanban (GitHub Project / Backlog):** [Agregar link al tablero]
* **Mockups de pantallas:** [Agregar link a Canva / Figma / Miro / Drive]

## Versiones utilizadas 
* Python 3.10 o superior
* Flask
* Requests

## Principales decisiones de diseño

## Dificultades encontradas 

## Conclusiones

## Ejecución 

## Configuración

## Índice
* [0. Enunciado](#0-Enunciado)
* [1. Instrucciones](#1-Instrucciones)
* [2. Funcionamiento](#2-Funcionamiento)
* [3. Estructura](#3-Estructura)
* [4. Decisiones de diseño y/o complejidades de implementación](#4-Decisiones-de-diseño-yo-complejidades-de-implementación)


## 0. Enunciado



## 1. Instrucciones
### 1.1. Compilación

### 1.2. Para ejecutar
1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Iniciar la aplicación:
   ```bash
   python app.py
   ```
3. Abrir en el navegador: `http://127.0.0.1:5001`

## 2. Funcionamiento


## 3. Estructura
```text
Front Cine-Paradiso/
├── routes/
│   ├── admin_routes.py
│   ├── auth_routes.py
│   └── main_routes.py
├── services/
│   ├── __init__.py
│   ├── admin_service.py
│   ├── api_client.py
│   ├── auth_service.py
│   ├── cartelera_service.py
│   └── perfil_service.py
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── login_registro.js
├── templates/
│   ├── components/
│   │   ├── _form_crear_funcion.html
│   │   ├── _form_crear_sala.html
│   │   ├── _tabla_funciones.html
│   │   ├── _tabla_salas.html
│   │   ├── footer.html
│   │   └── navbar.html
│   ├── pages/
│   │   ├── 404.html
│   │   ├── admin_cargar_pelicula.html
│   │   ├── index.html
│   │   ├── login_registro.html
│   │   ├── pelicula_detalle.html
│   │   └── perfil.html
│   ├── auth.html
│   ├── base.html
│   └── index.html
├── .env.example
├── .gitignore
├── README.md
├── app.py
├── config.py
├── endpoints.md
├── init.sh
└── requirements.txt
```

## 4. Decisiones de diseño y/o complejidades de implementación



