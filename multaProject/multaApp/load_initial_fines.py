from .models import Multa

initial_fines_data = [
    { "placa": "ABC-123", "infraccion": "Exceso de Velocidad", "fecha": "2024-11-10", "valor": 150, "estado": "Pendiente", "documento": None, "conductor": None, "codigo": None },
    { "placa": "ABC-123", "infraccion": "Estacionamiento Indebido", "fecha": "2024-11-08", "valor": 80, "estado": "Pendiente", "documento": None, "conductor": None, "codigo": None },
    { "placa": "XYZ-789", "infraccion": "Semáforo en Rojo", "fecha": "2024-11-05", "valor": 200, "estado": "Pagada", "documento": None, "conductor": None, "codigo": None },
    { "placa": "XYZ-789", "infraccion": "Estacionamiento Indebido", "fecha": "2024-11-09", "valor": 250, "estado": "Pendiente", "documento": None, "conductor": None, "codigo": None },
    { "placa": "DEF-456", "infraccion": "Exceso de Velocidad", "fecha": "2024-11-12", "valor": 175, "estado": "Pendiente", "documento": None, "conductor": None, "codigo": None },
    { "placa": "GHI-789", "infraccion": "Uso de Celular", "fecha": "2024-11-11", "valor": 120, "estado": "Pendiente", "documento": None, "conductor": None, "codigo": None },
]

def load_initial_data():
    # Eliminar todas las multas existentes
    count_before = Multa.objects.count()
    Multa.objects.all().delete()
    print(f"✔ Eliminadas {count_before} multas existentes")

    # Crear las nuevas multas
    multas_creadas = []
    for data in initial_fines_data:
        multa = Multa.objects.create(**data)
        multas_creadas.append(multa)
        print(f"  ✓ Creada: {multa.numero_multa} - {multa.placa} - {multa.infraccion}")

    print(f"\n✔ Total cargado: {len(multas_creadas)} multas")
    print(f"✔ Total en BD: {Multa.objects.count()} multas")