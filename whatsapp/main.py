from coreapibase_python import Color
from .apps import WhatsappConfig

def __init__():
    c = WhatsappConfig
    print(Color.fg.green + c.app_name + " API Server Ready " + c.api_ver + " " + c.api_address + ":" + c.api_port + " [" + c.api_mode + "]\n" + Color.reset)