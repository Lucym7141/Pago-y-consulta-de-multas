from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    # Raíz - redirige a consulta
    path("", lambda request: redirect('consulta'), name="home"),
    
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