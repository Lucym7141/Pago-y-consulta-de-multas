from django.contrib import admin
from .models import Multa

@admin.register(Multa)
class MultaAdmin(admin.ModelAdmin):
    list_display = ['numero_multa', 'placa', 'usuario', 'infraccion', 'fecha', 'valor', 'estado']
    list_filter = ['estado', 'usuario', 'fecha']
    search_fields = ['numero_multa', 'placa', 'conductor', 'documento']