from django.db import models


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
