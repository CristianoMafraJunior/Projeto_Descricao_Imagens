from django.urls import path
from app_image_caption import views

urlpatterns = [
    # rota, view responsável, nome de referencia
    path('',views.home,name='home'),

]
