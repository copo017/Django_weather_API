from django.urls import path
from .views import ItemListCreateView, ItemDetailView, get_weather, fetch_and_save_weather, fetch_and_savew_weather, \
    fetch_weather_and_forecast, WeatherListView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('items', ItemListCreateView.as_view(), name='item-list-create'),
    path('items/<int:pk>', ItemDetailView.as_view(), name='item-detail'),
    path('weather/', get_weather, name='get-weather'),
    path('weather/save/', fetch_and_save_weather, name='fetch-and-save-weather'),
    path('weather/guardar/', fetch_and_savew_weather, name='fetch-and-savew-weather'),

    path('fetch/', fetch_weather_and_forecast, name='fetch-weather-forecast'),
    path('list/', WeatherListView.as_view(), name='weather-list'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
