import uuid
from django.db import models

class Facility(models.Model):
    name = models.CharField(max_length=120)
    campus = models.CharField(max_length=80, default='Main Campus')
    category = models.CharField(max_length=60, default='Laboratory')
    capacity = models.PositiveIntegerField(default=30)
    location = models.CharField(max_length=120, blank=True)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

class Booking(models.Model):
    STATES = [('REQUESTED','Requested'),('APPROVED','Approved'),('CONFIRMED','Confirmed'),('IN_USE','In Use'),('COMPLETED','Completed'),('CANCELLED','Cancelled'),('REJECTED','Rejected')]
    facility = models.ForeignKey(Facility,on_delete=models.PROTECT,related_name='bookings')
    requester = models.CharField(max_length=120)
    purpose = models.CharField(max_length=240)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    state = models.CharField(max_length=20,choices=STATES,default='REQUESTED')
    request_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

class Ticket(models.Model):
    STATES = [('NEW','New / Intake'),('ASSIGNED','Assigned'),('INSPECTING','Inspecting'),('PENDING_WORK','Pending Work'),('IN_PROGRESS','In Progress'),('RESOLVED','Resolved'),('CLOSED','Closed'),('REOPENED','Reopened')]
    facility = models.ForeignKey(Facility,on_delete=models.PROTECT,related_name='tickets')
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=60,default='General')
    priority = models.CharField(max_length=20,default='MEDIUM')
    assignee = models.CharField(max_length=120,blank=True)
    state = models.CharField(max_length=20,choices=STATES,default='NEW')
    resolution_notes = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

class SensorEvent(models.Model):
    source_id = models.CharField(max_length=100)
    event_id = models.CharField(max_length=100)
    metric = models.CharField(max_length=80)
    value = models.FloatField()
    observed_at = models.DateTimeField()
    ticket = models.ForeignKey(Ticket,null=True,blank=True,on_delete=models.SET_NULL)
    class Meta: constraints = [models.UniqueConstraint(fields=['source_id','event_id'],name='uniq_sensor_source_event')]

class Approval(models.Model):
    booking = models.ForeignKey(Booking,on_delete=models.CASCADE)
    approver = models.CharField(max_length=120)
    decision = models.CharField(max_length=12,choices=[('APPROVED','Approved'),('REJECTED','Rejected')])
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class AuditEvent(models.Model):
    object_type = models.CharField(max_length=40)
    object_id = models.PositiveIntegerField()
    actor = models.CharField(max_length=120)
    action = models.CharField(max_length=80)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
