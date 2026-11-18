from django.urls import path
from . import views
urlpatterns=[path('health/',views.health),path('summary/',views.summary),path('facilities/',views.facilities),path('bookings/',views.bookings),path('tickets/',views.tickets),path('tickets/<int:pk>/',views.ticket_update),path('sensor-events/',views.sensor_events),path('approvals/',views.approvals),path('audit/',views.audit)]
