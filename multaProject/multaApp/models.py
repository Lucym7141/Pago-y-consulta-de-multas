from django.db import models
from django.contrib.auth.models import User

class Multa(models.Model):
    # NUEVO: Relación con el usuario
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='multas',
        null=True,
        blank=True
    )
    
    numero_multa = models.CharField(max_length=20, unique=True, blank=True)
    placa = models.CharField(max_length=10)
    conductor = models.CharField(max_length=100, null=True, blank=True)
    documento = models.CharField(max_length=20, null=True, blank=True)
    infraccion = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50, null=True, blank=True)
    fecha = models.DateField()
    valor = models.IntegerField()
    estado = models.CharField(max_length=20, default="Pendiente")
    archivada = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.numero_multa:
            ultimo = Multa.objects.all().order_by('id').last()
            if ultimo:
                numero = int(ultimo.numero_multa.split('-')[1]) + 1
            else:
                numero = 1
            self.numero_multa = f"MP-{numero:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_multa} - {self.placa}"

    class Meta:
        ordering = ['-fecha']