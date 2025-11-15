from django.db import models

class Multa(models.Model):
    ESTADOS = (
        ("Pendiente", "Pendiente"),
        ("Pagada", "Pagada"),
    )

    numero_multa = models.CharField(max_length=50, unique=True, blank=True, null=True)
    placa = models.CharField(max_length=15)
    documento = models.CharField(max_length=30, null=True, blank=True)
    conductor = models.CharField(max_length=120, null=True, blank=True)
    infraccion = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50, null=True, blank=True)
    fecha = models.DateField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="Pendiente")
    archivada = models.BooleanField(default=False)  # ← NUEVO CAMPO

    class Meta:
        ordering = ["-fecha"]

    def save(self, *args, **kwargs):
        # Generar número de multa automáticamente si no existe
        if not self.numero_multa:
            last = Multa.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.numero_multa = f"MP-{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_multa} — {self.placa} ({self.estado})"