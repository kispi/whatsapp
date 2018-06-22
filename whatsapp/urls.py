from django.urls import path
from . import main
from .views import *

urlpatterns = [
    path('v1/message', send_message, name='send_message'),
    path('v1/openNewBrowser', open_new_browser, name='open_new_browser'),
    path('v1/status', get_status, name='get_status'),
    path('v1/contacts', crud_contacts, name='crud_contacts'),
    path('v1/contacts/<int:id>', crud_contacts, name='crud_contacts'),
    path('v1/messages', crud_messages, name='crud_messages'),
    path('v1/messages/<int:id>', crud_messages, name='crud_messages'),
    path('v1/logs', crud_logs, name='crud_logs'),
    path('v1/logs/<int:id>', crud_logs, name='crud_logs'),
]

main.__init__()