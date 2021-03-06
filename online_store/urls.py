from django.urls import path
from online_store_app import views
from django.contrib import admin


urlpatterns = [
    path('home/', views.home),
    path('category/', views.category),
    path('subcategory/', views.subcategory),
    path('product/', views.product),
    path('feedback_writing/', views.feedback_writing),
    path('cart/', views.cart),
    path('order_making/', views.order_making),
    path('successful_payment_completion/', views.successful_payment_completion),
    path('unsuccessful_payment_completion/', views.unsuccessful_payment_completion),
    path('orders/', views.orders),
    path('profile/', views.profile),
    path('user_login/', views.user_login),
    path('user_logout/', views.user_logout),
    path('user_registration/', views.user_registration),
    path('email_confirmation/', views.email_confirmation),
    path('admin_interface/', admin.site.urls)
]
