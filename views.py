from datetime import datetime
import uuid
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Facility, Booking, Ticket, SensorEvent, Approval, AuditEvent
from .serializers import FacilitySerializer, BookingSerializer, TicketSerializer, AuditSerializer

@api_view(['GET'])
def health(request): return Response({'status':'ok','service':'smart-campus-api'})
@api_view(['GET'])
def summary(request):
    return Response({'facility_count':Facility.objects.filter(active=True).count(),'booking_count':Booking.objects.count(),'open_tickets':Ticket.objects.exclude(state='CLOSED').count(),'pending_approvals':Booking.objects.filter(state='REQUESTED').count()})
@api_view(['GET'])
def facilities(request): return Response(FacilitySerializer(Facility.objects.filter(active=True),many=True).data)
@api_view(['GET','POST'])
def bookings(request):
    if request.method=='GET': return Response(BookingSerializer(Booking.objects.select_related('facility').order_by('-created_at')[:100],many=True).data)
    data=request.data
    try:
        facility=Facility.objects.get(pk=data.get('facility'))
        start=parse_datetime(data.get('start_at','')); end=parse_datetime(data.get('end_at',''))
        if not start or not end or end<=start: return Response({'error':'invalid_time_range'},status=400)
        if data.get('request_key'):
            existing=Booking.objects.filter(request_key=data['request_key']).first()
            if existing: return Response(BookingSerializer(existing).data,status=200)
        with transaction.atomic():
            Facility.objects.select_for_update().get(pk=facility.pk)
            overlap=Booking.objects.filter(facility=facility,start_at__lt=end,end_at__gt=start).exclude(state__in=['CANCELLED','REJECTED']).exists()
            if overlap: return Response({'error':'booking_conflict','message':'This facility is already reserved for the selected time.'},status=409)
            b=Booking.objects.create(facility=facility,request_key=uuid.UUID(str(data['request_key'])) if data.get('request_key') else uuid.uuid4(),requester=data.get('requester','Faculty Demo'),purpose=data.get('purpose','Academic activity'),start_at=start,end_at=end,state='REQUESTED')
            AuditEvent.objects.create(object_type='Booking',object_id=b.id,actor=b.requester,action='BOOKING_REQUESTED')
        return Response(BookingSerializer(b).data,status=201)
    except Facility.DoesNotExist: return Response({'error':'facility_not_found'},status=404)
    except (ValueError,TypeError): return Response({'error':'invalid_request'},status=400)
@api_view(['GET','POST'])
def tickets(request):
    if request.method=='GET': return Response(TicketSerializer(Ticket.objects.select_related('facility').order_by('-created_at')[:100],many=True).data)
    d=request.data
    try:
        f=Facility.objects.get(pk=d.get('facility'))
        t=Ticket.objects.create(facility=f,title=d.get('title','Maintenance request'),description=d.get('description',''),category=d.get('category','General'),priority=d.get('priority','MEDIUM'))
        AuditEvent.objects.create(object_type='Ticket',object_id=t.id,actor=d.get('actor','Facility Manager'),action='TICKET_CREATED')
        return Response(TicketSerializer(t).data,status=201)
    except Facility.DoesNotExist: return Response({'error':'facility_not_found'},status=404)
@api_view(['PATCH'])
def ticket_update(request,pk):
    try: t=Ticket.objects.get(pk=pk)
    except Ticket.DoesNotExist: return Response({'error':'ticket_not_found'},status=404)
    d=request.data; expected=d.get('expected_version')
    if expected is None or int(expected)!=t.version: return Response({'error':'stale_version','current_version':t.version},status=409)
    target=d.get('state',t.state); notes=d.get('resolution_notes',t.resolution_notes)
    if target=='CLOSED' and not notes.strip(): return Response({'error':'resolution_notes_required'},status=422)
    allowed={'NEW':['ASSIGNED'],'ASSIGNED':['INSPECTING'],'INSPECTING':['PENDING_WORK','IN_PROGRESS'],'PENDING_WORK':['IN_PROGRESS'],'IN_PROGRESS':['RESOLVED'],'RESOLVED':['CLOSED','REOPENED'],'REOPENED':['ASSIGNED']}
    if target!=t.state and target not in allowed.get(t.state,[]): return Response({'error':'invalid_transition','from':t.state,'to':target},status=422)
    with transaction.atomic():
        updated=Ticket.objects.filter(pk=t.pk,version=t.version).update(state=target,assignee=d.get('assignee',t.assignee),resolution_notes=notes,version=t.version+1)
        if updated!=1: return Response({'error':'stale_version'},status=409)
        AuditEvent.objects.create(object_type='Ticket',object_id=t.id,actor=d.get('actor','Demo User'),action='TICKET_UPDATED',detail=f'{t.state} -> {target}')
    t.refresh_from_db(); return Response(TicketSerializer(t).data)
@api_view(['POST'])
def sensor_events(request):
    d=request.data
    try:
        event,created=SensorEvent.objects.get_or_create(source_id=d['source_id'],event_id=d['event_id'],defaults={'metric':d['metric'],'value':float(d['value']),'observed_at':parse_datetime(d['observed_at'])})
        if created and event.value>float(d.get('threshold',28)):
            facility=Facility.objects.get(pk=d['facility'])
            event.ticket=Ticket.objects.create(facility=facility,title=f"Sensor alert: {event.metric}",description=f"Observed {event.value}; threshold {d.get('threshold',28)}",category='Sensor Alert',priority='HIGH')
            event.save(update_fields=['ticket'])
            AuditEvent.objects.create(object_type='Ticket',object_id=event.ticket_id,actor='Sensor Intake',action='TICKET_CREATED_FROM_SENSOR')
        return Response({'created':created,'event_id':event.event_id,'ticket_id':event.ticket_id},status=201 if created else 200)
    except (KeyError,ValueError,Facility.DoesNotExist): return Response({'error':'invalid_sensor_event'},status=400)
@api_view(['POST'])
def approvals(request):
    d=request.data
    if d.get('role')!='approver': return Response({'error':'forbidden'},status=403)
    try:
        b=Booking.objects.get(pk=d['booking_id'])
        decision=d['decision']
        if decision not in ['APPROVED','REJECTED']: return Response({'error':'invalid_decision'},status=400)
        b.state=decision; b.version+=1; b.save(update_fields=['state','version'])
        Approval.objects.create(booking=b,approver=d.get('approver','Approver Demo'),decision=decision,reason=d.get('reason','Reviewed'))
        AuditEvent.objects.create(object_type='Booking',object_id=b.id,actor=d.get('approver','Approver Demo'),action=f'BOOKING_{decision}')
        return Response(BookingSerializer(b).data)
    except (Booking.DoesNotExist,KeyError): return Response({'error':'booking_not_found_or_missing_fields'},status=404)
@api_view(['GET'])
def audit(request): return Response(AuditSerializer(AuditEvent.objects.order_by('-created_at')[:100],many=True).data)
