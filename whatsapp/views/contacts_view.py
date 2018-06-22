import coreapibase_python as core
from django.views.decorators.csrf import csrf_exempt
from ..models import Contact
from ..views.auth import check_auth_token
import json

@csrf_exempt
def crud_contacts(req, id = None):
    if not check_auth_token(req):
        return core.Res().error("Unauthorized")

    if req.method == 'POST':
        if id is not None:
            return core.Res().method_not_allowed()
        
        contact = core.BaseView.ParseJsonBodyStruct(req, Contact)
        contact.save()
        return core.Res().success(1, "success")
    elif req.method == 'GET':
        if id is not None:
            try:
                contacts = Contact.objects.all().filter(id=id).values()
                contacts_list = list(contacts)
            except Contact.DoesNotExist:
                return core.Res().error("no row found")
            
            if len(contacts_list) == 0:
                return core.Res().error("no row found")
            # Since exception will be treated above, this must be safe.
            return core.Res().success(1, contacts_list[0])
        else:
            try:
                contacts = Contact.objects.all().values()
                contacts_list = list(contacts)
            except Exception as e:
                return core.Res().success(1, str(e))

            return core.Res().success(len(contacts), contacts_list)
    elif req.method == 'PUT':
        if id is None:
            return core.Res().method_not_allowed()

        try:
            c = Contact.objects.get(pk=id)
        except Exception:
            return core.Res().error("no row found")
        
        json_body = json.loads(req.body)
        if json_body['id'] != id:
            return core.Res().error("id in payload and endpoint don't match")
        uf = []
        for key in json_body:
            if key != 'id':
                uf.append(key)

        contact = core.BaseView.ParseJsonBodyStruct(req, Contact)
        contact.save(update_fields=uf)
        return core.Res().success(1, "success")
    elif req.method == 'DELETE':
        if id is None:
            return core.Res().method_not_allowed()

        c = Contact.objects.get(pk=id)
        c.delete()
        return core.Res().success(1, "success")