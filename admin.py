from django.contrib import admin
from .models import Facility, Booking, Ticket, SensorEvent, Approval, AuditEvent
admin.site.register([Facility,Booking,Ticket,SensorEvent,Approval,AuditEvent])
