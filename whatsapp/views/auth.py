from ..apps import WhatsappConfig
import os

def check_auth_token(request):
    if 'HTTP_X_APIKEY' in request.META:
        if request.META['HTTP_X_APIKEY'] == WhatsappConfig.api_key:
            return True
    
    return False