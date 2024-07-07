from django.forms import CharField
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import connection
from django.http import JsonResponse
from django.db.models import Count, Q
from datetime import datetime
from .models import Locations, Incident, FireStation, Firefighters, FireTruck, WeatherConditions
from .forms import FireStationForm, IncidentForm, FirefightersForm, LocationsForm, FireTruckForm, WeatherConditionsForm

# General Views
class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"


class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass

# JSON Response Views
def PieCountbySeverity(request):
    query = '''
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level;
    '''
    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    data = {severity: count for severity, count in rows} if rows else {}
    return JsonResponse(data)


def LineCountbyMonth(request):
    current_year = datetime.now().year
    result = {month: 0 for month in range(1, 13)}

    incidents_per_month = Incident.objects.filter(date_time__year=current_year).values_list('date_time', flat=True)
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    result_with_month_names = {month_names[int(month)]: count for month, count in result.items()}
    return JsonResponse(result_with_month_names)


def MultilineIncidentTop3Country(request):
    query = '''
        SELECT 
        fl.country,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    JOIN 
        fire_locations fl ON fi.location_id = fl.id
    WHERE 
        fl.country IN (
            SELECT 
                fl_top.country
            FROM 
                fire_incident fi_top
            JOIN 
                fire_locations fl_top ON fi_top.location_id = fl_top.id
            WHERE 
                strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
            GROUP BY 
                fl_top.country
            ORDER BY 
                COUNT(fi_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY 
        fl.country, month
    ORDER BY 
        fl.country, month;
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))
    for row in rows:
        country, month, total_incidents = row
        if country not in result:
            result[country] = {month: 0 for month in months}
        result[country][month] = total_incidents

    while len(result) < 3:
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}

    for country in result:
        result[country] = dict(sorted(result[country].items()))

    return JsonResponse(result)


def multipleBarbySeverity(request):
    query = '''
    SELECT 
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    GROUP BY fi.severity_level, month
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))
    for row in rows:
        level, month, total_incidents = row
        if level not in result:
            result[level] = {month: 0 for month in months}
        result[level][month] = total_incidents

    for level in result:
        result[level] = dict(sorted(result[level].items()))

    return JsonResponse(result)


# Fire Station CRUD
def map_station(request):
    fireStations = FireStation.objects.values('name', 'latitude', 'longitude')
    for fs in fireStations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])

    fireStations_list = list(fireStations)
    context = {'fireStations': fireStations_list}
    return render(request, 'map_station.html', context)


def fire_incident_map(request):
    locations_with_incident = Locations.objects.annotate(num_incidents=Count('incident')).values('id', 'name', 'latitude', 'longitude', 'city', 'num_incidents')
    for location in locations_with_incident:
        location['latitude'] = float(location['latitude'])
        location['longitude'] = float(location['longitude'])

    context = {'locations': list(locations_with_incident)}
    return render(request, 'fire_incident_map.html', context)


def station_list(request):
    stations = FireStation.objects.all()
    return render(request, 'station_list.html', {'stations': stations})


def station_create(request):
    if request.method == 'POST':
        form = FireStationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('station-list')
    else:
        form = FireStationForm()
    return render(request, 'station_form.html', {'form': form})


def station_detail(request, id):
    station = get_object_or_404(FireStation, id=id)
    return render(request, 'station_detail.html', {'station': station})


def station_update(request, id):
    station = get_object_or_404(FireStation, id=id)
    if request.method == 'POST':
        form = FireStationForm(request.POST, instance=station)
        if form.is_valid():
            form.save()
            return redirect('station-list')
    else:
        form = FireStationForm(instance=station)
    return render(request, 'station_form.html', {'form': form})


def station_delete(request, id):
    station = get_object_or_404(FireStation, id=id)
    if request.method == 'POST':
        station.delete()
        return redirect('station-list')
    return render(request, 'station_confirm_delete.html', {'station': station})


# Location Views
class LocationsList(ListView):
    model = Locations
    template_name = 'locations_list.html'
    context_object_name = 'locations'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query)
            )
        return qs


class LocationsCreateView(CreateView):
    model = Locations
    form_class = LocationsForm
    template_name = 'locations_add.html'
    success_url = reverse_lazy('locations-list')


class LocationsUpdateView(UpdateView):
    model = Locations
    form_class = LocationsForm
    template_name = 'locations_edit.html'
    success_url = reverse_lazy('locations-list')


class LocationsDeleteView(DeleteView):
    model = Locations
    template_name = 'locations_del.html'
    success_url = reverse_lazy('locations-list')


def delete_location(request, location_id):
    location = get_object_or_404(Locations, id=location_id)
    if request.method == 'POST':
        location.delete()
        return redirect('database')
    return render(request, 'del_location.html', {'location': location})


def location_view(request):
    locations = Locations.objects.all()
    incidents = Incident.objects.all()
    context = {
        'locations': locations,
        'incidents': incidents,
    }
    return render(request, 'location.html', context)


# Incident Views
class IncidentList(ListView):
    model = Incident
    context_object_name = 'incident'
    template_name = 'incident_list.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) |
                        Q (address__icontains=query) |
                        Q (city__icontains=query) |
                        Q (country__icontains=query))
        return qs


class IncidentCreateView(CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'incident_add.html'
    success_url = reverse_lazy('incident-list')


class IncidentUpdateView(UpdateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'incident_edit.html'
    success_url = reverse_lazy('incident-list')


class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = 'incident_del.html'
    success_url = reverse_lazy('incident-list')


# Firefighters Views
class FireFightersList(ListView):
    model = Firefighters
    context_object_name = 'firefighters'
    template_name = 'firefighters_list.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(rank__icontains=query) |
                Q(experience_level__icontains=query) |
                Q(station__icontains=query)
            )
        return qs


class FireFightersCreateView(CreateView):
    model = Firefighters
    form_class = FirefightersForm
    template_name = 'firefighters_add.html'
    success_url = reverse_lazy('firefighters-list')


class FireFightersUpdateView(UpdateView):
    model = Firefighters
    form_class = FirefightersForm
    template_name = 'firefighters_edit.html'
    success_url = reverse_lazy('firefighters-list')


class FireFightersDeleteView(DeleteView):
    model = Firefighters
    template_name = 'firefighters_del.html'
    success_url = reverse_lazy('firefighters-list')

#fire truck
class FireTruckList(ListView):
    model = FireTruck
    context_object_name = 'firetrucks'
    template_name = 'firetruck_list.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(
                Q(truck_number__icontains=query) |
                Q(model__icontains=query) |
                Q(capacity__icontains=query) |
                Q(station__icontains=query)
            )
        return qs

class FireTruckCreateView(CreateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'firetruck_add.html'
    success_url = reverse_lazy('firetruck-list')

class FireTruckUpdateView(UpdateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'firetruck_edit.html'
    success_url = reverse_lazy('firetruck-list')

class FireTruckDeleteView(DeleteView):
    model = FireTruck
    template_name = 'firetruck_del.html'
    success_url = reverse_lazy('firetruck-list')

class WeatherConditionsList(ListView):
    model = WeatherConditions
    template_name = 'weather_list.html'
    context_object_name = 'weather'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(WeatherConditionsList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(
                Q(incident__icontains=query) |
                Q(temperature__icontains=query) |
                Q(humidity__icontains=query) |
                Q(wind_speed__icontains=query) |
                Q(weather_description__icontains=query)
            )
        return qs

class WeatherConditionsCreateView(CreateView):
    model = WeatherConditions
    form_class = WeatherConditionsForm
    template_name = 'weather_add.html'
    success_url = reverse_lazy('weather-list')

class WeatherConditionsUpdateView(UpdateView):
    model = WeatherConditions
    form_class = WeatherConditionsForm
    template_name = 'weather_edit.html'
    success_url = reverse_lazy('weather-list')

class WeatherConditionsDeleteView(DeleteView):
    model = WeatherConditions
    template_name = 'weather_del.html'
    success_url = reverse_lazy('weather-list')