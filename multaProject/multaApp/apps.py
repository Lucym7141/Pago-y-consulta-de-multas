from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class MultaAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "multaApp"

   # def ready(self):
   #     from .models import Multa
   #     from .load_initial_fines import load_initial_data

   #     try:
   #         load_initial_data()
   #     except (OperationalError, ProgrammingError):
            # Esto evita errores cuando la BD aún no está lista
   #         pass
