from django.shortcuts import render
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Item, Weather, City, Forecast
from .serializers import ItemSerializer, WeatherSerializer
import json
from django.views.decorators.csrf import csrf_exempt

# api clima
import requests
from django.http import JsonResponse
from django.conf import settings

# autenticacion
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# filtro
from django_filters.rest_framework import DjangoFilterBackend
from .filters import WeatherFilter


# Create your views here.
class ItemListCreateView(APIView):
    def get(self, request):
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItemDetailView(APIView):
    def get(self, request, pk):
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def get_weather(request):
    # Leer la ciudad desde los parámetros de la solicitud
    city = request.GET.get('city', 'Santiago')  # Default: Santiago
    api_key = settings.OPENWEATHER_API_KEY
    base_url = 'https://api.openweathermap.org/data/2.5/weather'

    # Construir la URL de la API
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',
        'lang': 'es',  # Idioma español
    }
    response = requests.get(base_url, params=params)

    # Manejar errores de la API
    if response.status_code == 200:
        data = response.json()
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'No se pudo obtener el clima'}, status=response.status_code)

def fetch_and_save_weather(request):
    city = request.GET.get('city', 'Santiago')  # Default: Santiago
    api_key = settings.OPENWEATHER_API_KEY
    base_url = 'https://api.openweathermap.org/data/2.5/weather'

    # Construir la URL de la API
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',
        'lang': 'es',  # Idioma español
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            weather = Weather.objects.create(
                city=city,
                temperature=data['main']['temp'],
                description=data['weather'][0]['description'],
            )
            #return JsonResponse(data)
            return JsonResponse({'success': 'Data saved', 'weather_id': weather.id, 'data': data})
        except KeyError as e:
            return JsonResponse({'error': f'Data missing: {str(e)}'}, status=400)
    else:
        return JsonResponse({'error': 'Failed to fetch weather'}, status=response.status_code)


@csrf_exempt  # Solo necesario si no tienes un token CSRF configurado
def fetch_and_savew_weather(request):
    if request.method == 'POST':
        try:
            # Leer el JSON enviado en el cuerpo de la solicitud
            body = json.loads(request.body)
            city = body.get('city')

            if not city:
                return JsonResponse({'error': 'City is required'}, status=400)

            # Consumir la API de OpenWeatherMap
            api_key = settings.OPENWEATHER_API_KEY
            base_url = 'https://api.openweathermap.org/data/2.5/weather'
            params = {
                'q': city,
                'appid': api_key,
                'units': 'metric',
                'lang': 'es',
            }
            response = requests.get(base_url, params=params)

            if response.status_code == 200:
                data = response.json()

                # Guardar los datos en la base de datos
                weather = Weather.objects.create(
                    city=city,
                    temperature=data['main']['temp'],
                    description=data['weather'][0]['description'],
                )
                return JsonResponse({'success': 'Data saved', 'weather_id': weather.id, 'data': data})
            else:
                return JsonResponse({'error': 'Failed to fetch weather'}, status=response.status_code)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid HTTP method. Use POST.'}, status=405)

## test hard
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_weather_and_forecast(request):
    city_name = request.GET.get('city', 'Santiago')
    api_key = settings.OPENWEATHER_API_KEY
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric'
    forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={api_key}&units=metric'

    # Consumir APIs
    weather_response = requests.get(weather_url)
    forecast_response = requests.get(forecast_url)

    if weather_response.status_code == 200 and forecast_response.status_code == 200:
        weather_data = weather_response.json()
        forecast_data = forecast_response.json()

        # Guardar clima actual
        city, _ = City.objects.get_or_create(name=city_name)  # sacar city de la url
        Weather.objects.create(
            city=city,
            temperature=weather_data['main']['temp'],
            description=weather_data['weather'][0]['description']
        )

        # Guardar pronósticos
        for forecast in forecast_data['list']:
            Forecast.objects.create(
                city=city,
                date=forecast['dt_txt'],
                temperature=forecast['main']['temp'],
                description=forecast['weather'][0]['description']
            )

        return JsonResponse({'success': 'Weather and forecast saved', 'data weather':weather_data, 'data forecast':forecast_data})
    else:
        return JsonResponse({'error': 'Failed to fetch data'}, status=400)

class WeatherPagination(PageNumberPagination):
    page_size = 10

# solo listar + filtros + autenticacion
class WeatherListView(ListAPIView):
    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer
    pagination_class = WeatherPagination

    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados

    filter_backends = [DjangoFilterBackend]  # filtro
    filterset_class = WeatherFilter  # filtro

    def get_queryset(self):
        city = self.request.GET.get('city')
        if city:
            return self.queryset.filter(city__name__icontains=city)
        return self.queryset

    # def get_queryset(self):
    #     city = self.request.GET.get('city')
    #
    #     # Si el parámetro 'city' está presente
    #     if city:
    #         try:
    #             queryset = self.queryset.filter(city__name__icontains=city)
    #             if not queryset.exists():
    #                 raise NotFound(detail=f"No se encontraron datos para la ciudad: {city}")
    #             return queryset
    #         except Exception as e:
    #             raise ParseError(detail=f"Error al procesar la solicitud: {str(e)}")
    #
    #     # Si no se proporciona 'city', devuelve todo el queryset
    #     return self.queryset













