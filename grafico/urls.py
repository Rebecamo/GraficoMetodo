from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Página principal
    path('crear/', views.crear_problema, name='crear_problema'),  # Formulario para crear problema
    path('resultado/<int:problema_id>/', views.resultado, name='resultado'),  # Resultado del problema
    path('historial/', views.historial, name='historial'),  # Ver historial de problemas guardados
    path('borrar_historial/', views.borrar_historial, name='borrar_historial'),  # Borrar todo el historial
    path('ejemplo/', views.ejemplo, name='ejemplo'),  # Página con ejemplo de uso
    path('ayuda/', views.ayuda, name='ayuda'),  # Página de ayuda o guía
    path('login/', views.login_view, name='login'),  # Iniciar sesión
    path('logout/', views.logout_view, name='logout'),  # Cerrar sesión
    path('registro/', views.registro, name='registro'),  # Registro de nuevos usuarios
    path('editar/<int:problema_id>/', views.editar_problema, name='editar_problema'),
    path('duplicar/<int:problema_id>/', views.duplicar_problema, name='duplicar_problema'),

    # Exportaciones de resultados
    path('exportar_pdf/<int:problema_id>/', views.exportar_pdf, name='exportar_pdf'),  # Exportar a PDF
    path('exportar_excel/<int:problema_id>/', views.exportar_excel, name='exportar_excel'),  # Exportar a Excel
    path('exportar_word/<int:problema_id>/', views.exportar_word, name='exportar_word'),  # Exportar a Word
]
