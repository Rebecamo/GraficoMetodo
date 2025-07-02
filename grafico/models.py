from django.db import models
from django.contrib.auth.models import User

#Modelo Problema
class Problema(models.Model):
    """Representa un problema de programación lineal creado por un usuario.
    Permite almacenar información necesaria para resolverlo mediante
    el método gráfico o en un futuro con Simplex."""
   

    # Relación con el usuario que creó el problema
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    # Si el usuario es eliminado, también se eliminan sus problemas.

    # Nombre personalizado del problema (editable por el usuario)
    nombre = models.CharField(max_length=100, default='Sin título')

    # Descripción opcional del problema (puede dejarse en blanco)
    descripcion = models.TextField(blank=True)

    # Tipo de método de resolución (por ahora solo 'gráfico' está implementado)
    tipo = models.CharField(
        max_length=20,
        choices=[('grafico', 'Gráfico'), ('simplex', 'Simplex')],
        default='grafico'
    )

    # Campo reservado para posibles datos adicionales (no utilizado aún)
    datos = models.TextField(blank=True, null=True)

    # Tipo de optimización: maximizar o minimizar Z
    objetivo = models.CharField(
        max_length=10,
        choices=[('max', 'Maximizar'), ('min', 'Minimizar')],
        default='max'
    )

    # Función objetivo ingresada por el usuario. Ej: "3x + 2y"
    funcion_objetivo = models.CharField(max_length=200)

    # Restricciones ingresadas. Una por línea. Ej: "2x + y <= 6"
    restricciones = models.TextField(
        help_text="Una por línea. Ej: 2x+3y<=6"
    )

    # Límites de las variables. Ej: "x>=0, y>=0"
    limites = models.CharField(
        max_length=200,
        help_text="Ej: x>=0, y>=0"
    )

    # Fecha y hora de creación automática del problema
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        
        #Representación legible del problema en el panel de administración
        #y otras interfaces: incluye nombre, tipo de optimización y función Z.
       
        return f"{self.nombre} ({self.objetivo.upper()} Z = {self.funcion_objetivo})"
