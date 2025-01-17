import django_filters
from .models import Weather

class WeatherFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(field_name='city__name', lookup_expr='icontains')  # Filtro por nombre de ciudad
    #city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')  # Filtrar directamente por el campo `city`
    min_temperature = django_filters.NumberFilter(field_name='temperature', lookup_expr='gte')  # Temperatura mínima
    max_temperature = django_filters.NumberFilter(field_name='temperature', lookup_expr='lte')  # Temperatura máxima
    date_fetched = django_filters.DateFromToRangeFilter(field_name='date_fetched')  # Rango de fechas

    class Meta:
        model = Weather
        fields = ['city', 'temperature', 'date_fetched']
