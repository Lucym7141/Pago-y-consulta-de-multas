from django import forms
from .models import Multa

class MultaForm(forms.ModelForm):
    class Meta:
        model = Multa
        fields = ['numero_multa','placa','documento','conductor','infraccion','codigo','fecha','valor','estado']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'})
        }