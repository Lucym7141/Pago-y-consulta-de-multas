from django.db import models

class Multa(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
    )

    numero = models.CharField(max_length=50, unique=True)
    fecha = models.DateField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Multa {self.numero}"
