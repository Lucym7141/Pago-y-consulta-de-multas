from django import forms
from .models import Multa
from django.contrib.auth.models import User

class MultaForm(forms.ModelForm):
    # Campo para seleccionar usuario
    usuario = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        label="Usuario",
        help_text="Selecciona el usuario al que pertenece esta multa"
    )
    
    class Meta:
        model = Multa
        fields = ['usuario', 'numero_multa', 'placa', 'documento', 'conductor', 'infraccion', 'codigo', 'fecha', 'valor', 'estado']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'})
        }