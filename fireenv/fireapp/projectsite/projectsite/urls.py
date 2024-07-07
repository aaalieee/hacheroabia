from django.contrib import admin
from django.urls import path
from fire import views
from fire.views import HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth, MultilineIncidentTop3Country, multipleBarbySeverity
from fire.views import map_station, fire_incident_map, station_list, station_create, station_detail,station_update, station_delete
from fire.views import LocationsList, LocationsCreateView, LocationsUpdateView, LocationsDeleteView
from fire.views import IncidentList,IncidentCreateView, IncidentUpdateView, IncidentDeleteView
from fire.views import FireFightersList, FireFightersCreateView, FireFightersUpdateView, FireFightersDeleteView
from fire.views import FireTruckList, FireTruckCreateView, FireTruckUpdateView, FireTruckDeleteView
from fire.views import WeatherConditionsList, WeatherConditionsCreateView, WeatherConditionsUpdateView, WeatherConditionsDeleteView


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard-chart'),
    path('PieChart/', PieCountbySeverity, name='chart'),
    path('lineChart/', LineCountbyMonth, name='chart'),
    path('multilineChart/', MultilineIncidentTop3Country, name='chart'),
    path('multiBarChart/', multipleBarbySeverity, name='chart'),
    path('stations', views.map_station, name='map-station'),
    path('fire_incident_map/', views.fire_incident_map, name='fire-incident-map'),
    

    path('locations/', LocationsList.as_view(), name='locations-list'),
    path('locations/add/', LocationsCreateView.as_view(), name='locations-add'),
    path('locations/<pk>/', LocationsUpdateView.as_view(), name='locations-update'),
    path('locations/<pk>/delete/', LocationsDeleteView.as_view(), name='locations-delete'),

    path('stations/', views.station_list, name='station-list'),
    path('stations/create/', views.station_create, name='station-create'),
    path('stations/<int:id>/update/', views.station_update, name='station-detail'),
    path('stations/<int:id>/delete/', views.station_delete, name='station-delete'),

    path('incidents/', IncidentList.as_view(), name='incident-list'),
    path('incidents/add/', IncidentCreateView.as_view(), name='incident-add'),
    path('incidents/<pk>/', IncidentUpdateView.as_view(), name='incident-update'),
    path('incidents/<pk>/delete/', IncidentDeleteView.as_view(), name='incident-delete'),

    path('firefighters/', FireFightersList.as_view(), name='firefighters-list'),
    path('firefighters/add/', FireFightersCreateView.as_view(), name='firefighters-add'),
    path('firefighters/<pk>/', FireFightersUpdateView.as_view(), name='firefighters-update'),
    path('firefighters/<pk>/delete/', FireFightersDeleteView.as_view(), name='firefighters-delete'),

    path('firetrucks/', FireTruckList.as_view(), name='firetruck-list'),
    path('firetrucks/add/', FireTruckCreateView.as_view(), name='firetruck-add'),
    path('firetrucks/<pk>/', FireTruckUpdateView.as_view(), name='firetruck-update'),
    path('firetrucks/<pk>/delete/', FireTruckDeleteView.as_view(), name='firetruck-delete'),

    path('weather/', WeatherConditionsList.as_view(), name='weather-list'),
    path('weather/add/', WeatherConditionsCreateView.as_view(), name='weather-add'),
    path('weather/<pk>/', WeatherConditionsUpdateView.as_view(), name='weather-update'),
    path('weather/<pk>/delete/', WeatherConditionsDeleteView.as_view(), name='weather-delete'),


]