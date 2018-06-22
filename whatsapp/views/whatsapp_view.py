import coreapibase_python as core
import urllib
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from ..services.whatsapp import Whatsapp, get_stats, fetch_browser
from ..models.log import Log
from ..models.message import Message
from ..models.contact import Contact
from ..views.auth import check_auth_token
from .. import apps

@csrf_exempt
def send_message(req):
    if req.method != 'GET':
        return core.Res().method_not_allowed()

    apikey = phone = text = identifier = chat_id = None
    try:
        apikey = req.GET['apikey']
        text = req.GET['text']
    except Exception as e:
        return core.Res().error("Check required parameters: 'apikey', 'text'")

    try:
        chat_id = req.GET['chat_id']
    except:
        try:
            phone = req.GET['phone']
        except:
            return core.Res().error("At least one of either 'chat_id' or 'phone' should be given")

    try:
        identifier = req.GET['identifier']
        chat_id = req.GET['chat_id']
    except Exception as e:
        pass

    if apikey is not None and apikey == apps.WhatsappConfig.api_key:
        pass
    else:
        return core.Res().error("Unauthorized")

    if text is None: 
        return core.Res().error("Missing text")
    
    # identifier can be phone number or be anything.
    try:
        browser = fetch_browser(identifier)
    except Exception as e:
        return core.Res().error(str(e))

    if browser is not None:
        sent = False
        try:
            text = urllib.parse.unquote(text)
            browser.send_whatsapp_message(phone, text, chat_id)
            sent = True

            if phone is not None:
            # index 0 refers to object, index 1 refers to if insert was executed.
                c = Contact.objects.filter(phone=phone).get_or_create(phone=phone)
                m = Message.objects.filter(text=text).get_or_create(text=text)
                l = Log.objects.filter(message_id=m[0].id).filter(contact_id=c[0].id).get_or_create(message_id=m[0].id, contact_id=c[0].id, sent=True, sent_at=now(), sender_id=identifier, broadcasted=False)
        except Exception as e:
            core.Log.error(repr(e))
            if sent is False:
                return core.Res().success(1, { 'phone': phone, 'text': text, 'identifier': identifier, 'status': 'failed', 'message': str(e) })            

        return core.Res().success(1, { 'phone': phone, 'text': text, 'identifier': identifier, 'status': 'success' })
    else:
        return core.Res().error("No matching browser with given identifier")
    
@csrf_exempt
def open_new_browser(req):
    if req.method != 'GET':
        return core.Res().method_not_allowed()

    identifier = None

    try:
        identifier = req.GET['identifier']
    except:
        return core.Res().error("Missing key 'identifier' in the url query parameter. Must be given like identifier=82108454704")

    # If users turns off browser even before it's logged in, it's not added to the list of available browsers.
    browser = None
    try:
        browser = Whatsapp(identifier)
        browser.start()
        apps.WhatsappConfig.browsers.append(browser)
        return core.Res().success(1, 'success')
    except Exception as e:
        return core.Res().error(str(e))

def get_status(req):
    if req.method != 'GET':
        return core.Res().method_not_allowed()

    stats = get_stats()
    return core.Res().success(len(stats), {'browsers': stats})