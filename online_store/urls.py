from django.urls import path
from online_store_app import views


urlpatterns = [
    path('', views.clothes),
    path('clothes/', views.clothes),
    path('shoes/', views.shoes)
]
