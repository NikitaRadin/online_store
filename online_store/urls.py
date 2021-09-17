from django.urls import path
from online_store_app import views


urlpatterns = [
    path('category/', views.category),
    path('subcategory/', views.subcategory),
    path('product/', views.product),
    path('user_login/', views.user_login),
    path('user_logout/', views.user_logout),
    path('user_registration/', views.user_registration)
]
