from django.urls import path
from online_store_app import views


urlpatterns = [
    path('category/', views.category)
]
