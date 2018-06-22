from django.db import models
from .base_model import BaseModel

class Message(BaseModel):
    text = models.CharField(max_length=255)
    use = models.BooleanField(default=False)
    broadcast = models.BooleanField(default=False)