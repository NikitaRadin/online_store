from django.contrib import admin
from online_store_app import models


admin.site.register(models.Category)
admin.site.register(models.Subcategory)
admin.site.register(models.Product)
