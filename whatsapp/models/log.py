from django.db import models
from .base_model import BaseModel
from .message import Message
from .contact import Contact

class Log(BaseModel):
    # Django doesn't put cascade relationship in Database actually, it just emulates.
    # So if you delete model by Django, cascading behavior will work, but if you delete
    # something in raw query, it won't be deleted since the behavior on ON_DELETE is not set in DB.
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True)
    sent = models.NullBooleanField()
    broadcasted = models.NullBooleanField(default=True)
    sent_at = models.DateTimeField(null=True)
    sender_id = models.CharField(max_length=255, null=True)