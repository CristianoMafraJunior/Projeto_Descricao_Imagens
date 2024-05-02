from app_image_caption import views
from django.urls import path

urlpatterns = [
    # rota, view responsável, nome de referencia
    path("", views.home, name="home"),
]
