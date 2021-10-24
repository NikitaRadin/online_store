from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=50)


class Subcategory(models.Model):
    name = models.CharField(max_length=50)
    image_path = models.CharField(max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    image_path = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)


class ProductImage(models.Model):
    image_path = models.CharField(max_length=250)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class ProductCharacteristic(models.Model):
    name = models.CharField(max_length=12)
    value = models.CharField(max_length=12)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    products = models.ManyToManyField(Product, through='CartProduct')


class CartProduct(models.Model):
    units_number = models.IntegerField(default=1)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Order(models.Model):
    delivery_address = models.CharField(max_length=250)
    entrance = models.IntegerField()
    floor = models.IntegerField()
    apartment = models.IntegerField()
    recipient_first_last_name = models.CharField(max_length=61)
    recipient_phone_number = models.CharField(max_length=12)
    status = models.IntegerField()
    last_change_date_time = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderProduct')


class OrderProduct(models.Model):
    units_number = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
