from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    # Página principal
    path("", views.home, name="home"),
    
    # Autenticación
    path("login/", views.user_login, name="user_login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.user_logout, name="user_logout"),
    path("mi-cuenta/", views.user_dashboard, name="user_dashboard"),
    
    # Públicas
    path("consulta/", views.consulta, name="consulta"),
    path("resultados/", views.resultados_consulta, name="resultados_consulta"),
    path("pagar/<int:id>/", views.pagar_multa, name="pagar_multa"),
    path("confirmacion/<int:id>/", views.confirmacion_pago, name="confirmacion_pago"),
    
    # Admin
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/crear/", views.crear_multa, name="crear_multa"),
    path("dashboard/editar/<int:id>/", views.editar_multa, name="editar_multa"),
    path("dashboard/eliminar/<int:id>/", views.eliminar_multa, name="eliminar_multa"),
    
    # Descargas de informes
    path("dashboard/informe/<int:id>/", views.descargar_informe_multa, name="descargar_informe_multa"),
    path("dashboard/informe-general/", views.descargar_informe_general, name="descargar_informe_general"),
]