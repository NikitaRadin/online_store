from django.urls import path
from online_store_app import views


urlpatterns = [
    path('category/', views.category),
    path('subcategory/', views.subcategory),
    path('product/', views.product),
    path('user_registration/', views.user_registration)
]
