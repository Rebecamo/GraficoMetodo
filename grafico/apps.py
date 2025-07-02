from django.apps import AppConfig


class GraficoConfig(AppConfig):
    """Configuración de la aplicación 'grafico'.
    Django utiliza esta clase para configurar algunos
    aspectos internos de la app."""
   
    default_auto_field = 'django.db.models.BigAutoField'  # Campo de clave primaria por defecto
    name = 'grafico'  # Nombre de la aplicación
