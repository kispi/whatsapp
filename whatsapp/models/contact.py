from django.db import models
from .base_model import BaseModel

class Contact(BaseModel):
    phone = models.CharField(max_length=255)