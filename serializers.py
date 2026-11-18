from rest_framework import serializers
from .models import Facility, Booking, Ticket, SensorEvent, AuditEvent
class FacilitySerializer(serializers.ModelSerializer):
    class Meta: model=Facility; fields='__all__'
class BookingSerializer(serializers.ModelSerializer):
    facility_name=serializers.CharField(source='facility.name',read_only=True)
    class Meta: model=Booking; fields='__all__'; read_only_fields=['request_key','version','created_at']
class TicketSerializer(serializers.ModelSerializer):
    facility_name=serializers.CharField(source='facility.name',read_only=True)
    class Meta: model=Ticket; fields='__all__'; read_only_fields=['version','created_at']
class SensorEventSerializer(serializers.ModelSerializer):
    class Meta: model=SensorEvent; fields='__all__'; read_only_fields=['ticket']
class AuditSerializer(serializers.ModelSerializer):
    class Meta: model=AuditEvent; fields='__all__'
