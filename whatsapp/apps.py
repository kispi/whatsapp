from django.apps import AppConfig
import os

class WhatsappConfig(AppConfig):
    browsers = []
    spammer = os.getenv('SPAMMER')
    app_name = os.getenv('APP_NAME')
    api_ver = os.getenv('API_VERSION')
    api_address = os.getenv('API_ADDR')
    api_mode = os.getenv('API_RUNMODE')
    api_port = os.getenv('API_PORT')
    api_key = os.getenv('API_KEY')
    api_endpoint = os.getenv('API_ENDPOINT')
    message_interval = os.getenv('MESSAGE_INTERVAL')