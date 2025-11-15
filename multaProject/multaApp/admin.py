from django.contrib import admin
from .models import Multa

@admin.register(Multa)
class MultaAdmin(admin.ModelAdmin):
    list_display = ("numero_multa","placa","conductor","infraccion","fecha","valor","estado")
    list_filter = ("estado","fecha")
    search_fields = ("placa","conductor","infraccion","codigo","documento")
