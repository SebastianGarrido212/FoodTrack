# 🌱 FoodTrack
Sistema de Trazabilidad y Logística para Donaciones de Alimentos



FoodTrack es una plataforma web diseñada para combatir el desperdicio de alimentos y la incertidumbre en las donaciones benéficas. Conecta a Donadores con Organizaciones receptoras, permitiendo un seguimiento en tiempo real del transporte de alimentos y generando reportes de gestión.

# Características Principales
- Gestión de Roles: Sistema de autenticación con perfiles diferenciados para Donadores y Organizaciones.

- Trazabilidad en Tiempo Real: Integración con Google Maps API para visualizar la ruta de entrega con animación de vehículo en movimiento.

- Geolocalización Inteligente: Uso de Google Places API para autocompletado y validación de direcciones reales durante el registro.

- Gestión de Donaciones (CRUD): Ciclo completo de donación: Crear, Editar, Cancelar, Aceptar y Finalizar entrega.

- Reportes Administrativos: Generación y descarga automática de reportes en formato Excel (.xlsx) para control de inventario.

- Interfaz Dinámica: Dashboards personalizados según el tipo de usuario y notificaciones visuales de estado.



# Tecnologías Utilizadas
__Backend__:

- Python: Lenguaje principal.

- Django: Framework web robusto.

- Gunicorn: Servidor WSGI para producción.

- OpenPyXL: Para la generación de archivos Excel.

__Frontend__:

- HTML5 / CSS3: Diseño responsivo y animaciones (Animate.css).

- JavaScript (Vanilla): Lógica del cliente y manejo de mapas.

- Google Maps Platform: Maps JS API, Directions API, Places API.

- Base de Datos y Despliegue:

- PostgreSQL: Base de datos en producción.

- SQLite/MariaDB: Base de datos en desarrollo local.

- Render: Plataforma de despliegue en la nube.



# Instalación Local
Si deseas correr este proyecto en tu máquina local, sigue estos pasos:

Clonar el repositorio:

	git clone https://github.com/SebastianGarrido212/FoodTrack.git
	cd FoodTrack

Crear y activar entorno virtual:
```
python -m venv venv
```
# En Windows:
	venv\Scripts\activate
# En Mac/Linux:
	source venv/bin/activate

Instalar dependencias:
```
pip install -r requirements.txt
```
Configurar Base de Datos:
```
python manage.py migrate
```
Crear Superusuario (Administrador):
```
python manage.py createsuperuser
```
Ejecutar el servidor:
```
python manage.py runserver
```
Visita http://127.0.0.1:8000 en tu navegador.

# Configuración de Variables
Para que el proyecto funcione correctamente, especialmente los mapas, asegúrate de configurar las siguientes claves en tu código o variables de entorno
:GOOGLE_MAPS_API_KEY:
Necesaria en views.py y CrearUsuario.html para mapas y autocompletado.SECRET_KEY: Clave de seguridad de Django (en settings.py).

# Despliegue
Este proyecto está configurado para desplegarse automáticamente en Render. 
- El archivo build.sh se encarga de la instalación de dependencias y migraciones.
- La configuración en settings.py detecta automáticamente si está corriendo en Render para usar PostgreSQL (dj-database-url).
- Se utiliza WhiteNoise para servir archivos estáticos en producción.
- Enlace a Producción: https://foodtrack-web.onrender.com
# ------------------------ * --------------------
Desarrollado por: Sebastian Garrido  
Asignatura: Programación Back-End  
Fecha: Diciembre 2025  
