from django.db import models

# Create your models here.
from django.db import models
import django_filters

class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Weather(models.Model):
    #city = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    temperature = models.FloatField()
    description = models.CharField(max_length=255)
    date_fetched = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.city} - {self.temperature} °C'



class Forecast(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    date = models.DateTimeField()
    temperature = models.FloatField()
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.city.name} - {self.date}"



