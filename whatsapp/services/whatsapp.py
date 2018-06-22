import requests
import os
import time as t
import threading
from django.utils.timezone import now
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message
from webwhatsapi import ChatNotFoundError
from .. import apps
from ..models import Contact, Message, Log
from coreapibase_python import Log as Logger

# When this Whatsapp instance is created, it opens firefox waiting for the user to read QR code.
class Whatsapp(threading.Thread):
    def __init__(self, identifier):
        self.driver = WhatsAPIDriver(loadstyles=True)
        self.identifier = identifier
        self.messagesSent = 0
        self.messageQueue = []
        self.status = {}
        
        print("Waiting for QR")
        try:
            self.driver.wait_for_login()
            super(Whatsapp, self).__init__()
            self.setDaemon(True)
        except Exception as ex:
            print("Error", ex)

        print("New Browser Opened")
        
    def get_chat(self, phone):
        try:
            chat = self.driver.get_chat_from_phone_number(phone)
        except ChatNotFoundError:
            url = self.driver._URL+"/send?phone="+phone
            self.driver.driver.get(url)
            t.sleep(5)
            chat = self.driver.get_chat_from_phone_number(phone)
        return chat

    # Give timeout_after_sent to avoid being suspected as a spammer.
    # Assign high value after multithreading is implemented.
    def send_whatsapp_message(self, phone, message, chat_id=None):
        try:
            if chat_id is None:
                chat = self.get_chat(phone)
                self.driver.chat_send_message(chat.id, message)
            else:
                self.driver.send_message_to_id(chat_id, message)

            self.messagesSent += 1
        except ChatNotFoundError:
            # This means the given number is invalid.
            Logger.warning("Invalid phone number: " + str(phone) + " will be deleted")
            c = Contact.objects.get(phone=phone)
            c.delete()
            raise ChatNotFoundError
        except Exception as e:
            # This means browser is still not available even after 5 seconds.
            # But the number is not invalid.(= valid)
            Logger.error(repr(e))
            raise e

    def send_message_and_save_log(self):
        messages = Message.objects.all().filter(use=True).filter(broadcast=True)
        for m in messages:
            logs = Log.objects.all().filter(message_id=m.id).filter(sent=True)
            contacts_already_sent = []
            for l in logs:
                contacts_already_sent.append(l.contact_id)
            contacts_to_send = Contact.objects.all().exclude(id__in=contacts_already_sent)

            if len(contacts_to_send) > 0:
                # Save the log first so that the same contact cannot be used in another browsers.
                for contact in contacts_to_send:
                    newLogs = Log.objects.filter(message_id=m.id).filter(contact_id=contact.id).get_or_create(message_id=m.id, contact_id=contact.id, sent=False, sender_id=self.identifier, broadcasted=True)
                    if len(newLogs) > 0:
                        l = newLogs[0]
                    
                    try:
                        print("Try to send message: [phone(", contact.id, ": ", contact.phone, "), text(", m.id, ": ", m.text, ")", sep="")
                        # If no exception, update 'sent', 'sent_at'
                        self.send_whatsapp_message(contact.phone, m.text)
                        l.sent = True
                        l.sent_at = now()
                        l.save(update_fields=['sent', 'sent_at'])
                        # The reason returning here is: once the message is sent to anyone of contacts,
                        # then server should bring available contacts again, not iterating over the given list.
                        # Otherwise, there is no way to control server immediately after insert new messages, contacts to DB.
                        return
                    except Exception as e:
                        Logger.warning(repr(e))
                        # Wait when error occurred so that browser can be opened again.
                        t.sleep(5)

    def poll_unread(self):
        try:
            if self.driver.is_logged_in():
                # Spam only works when this server is used as a spammer.
                if apps.WhatsappConfig.spammer == 'true':
                    try:
                        self.send_message_and_save_log()
                    except Exception as e:
                        Logger.error(repr(e))
                # Otherwise, this server will fetch unread messages and send webhook.
                else:
                    data = []
                    
                    try:
                        Logger.debug("(" + self.identifier + "): get_unread()")
                        for messageGroup in self.driver.get_unread():
                            unread_messages = []
                            for m in messageGroup.messages:
                                unread_messages.append({
                                    "content": m.content,
                                    "timestamp": "{timestamp}".format(timestamp=m.timestamp)
                                })
                            data.append({ "chatId": messageGroup.chat.id, "unreadMessages": unread_messages })
                    except Exception as e:
                        Logger.error(repr(e))

                    # Doesn't have to make a request when there is no unread message.
                    if len(data) > 0:
                        payload = {'data': data}
                        webhook_url = apps.WhatsappConfig.api_endpoint + '/no_auth/whatsapp/webhook'
                        try:
                            print("Request:", webhook_url)
                            r = requests.post(webhook_url, json=payload, timeout=3)
                            print("Response:", r.text)
                        except Exception as e:
                            print("Tokotalk API(" + webhook_url + ") doesn't respond in 3 second", sep='')

        except Exception as e:
            Logger.error(repr(e))

    def run(self):
        while True:
            try:
                self.poll_unread()
            except Exception as e:
                Logger.debug(repr(e) + ": POLL FAILED")
            
            # in case the interval is not set in .env
            interval = 5
            if apps.WhatsappConfig.message_interval is not None:
                interval = int(apps.WhatsappConfig.message_interval)
            t.sleep(interval)
    
def get_stats():
    browsers = apps.WhatsappConfig.browsers
    statuses = []
    for browser in browsers:
        print("ping: browser is ready to send messages")
        status = {}
        status['index'] = len(statuses)

        try:
            status['status'] = browser.driver.is_logged_in()
            status['messagesSent'] = browser.messagesSent
            status['identifier'] = browser.identifier
        except Exception as e:
            status['error'] = str(e)

        browser.status = status
        statuses.append(status)

    return statuses

def remove_dead_browser():
    ids_to_be_removed = []
    for idx, browser in enumerate(apps.WhatsappConfig.browsers):
        status = None
        try:
            status = browser.status['status']
            print(status)
            if status == 'LoggedIn':
                pass
        except Exception as e:
            ids_to_be_removed.append(idx)
            print(e)
            
    for i in reversed(ids_to_be_removed):
        del apps.WhatsappConfig.browsers[i]
        print("browser at index " + str(i) + " is removed")
        

# It fetches the available browser within the list of opened browsers.
def fetch_browser(identifier = None):
    get_stats()
    browsers = apps.WhatsappConfig.browsers

    if len(browsers) == 0:
        raise Exception("At least 1 browser must be available")

    # If user specifies which browser to use for sending message
    if identifier is not None:
        for browser in browsers:
            if browser.identifier == identifier:
                return browser
        return None

    # Otherwise just follow the algorithm. I don't think this way matters for now.
    browser = getBrowserThatSentLowestNumberOfMessages(browsers)
    # this browser can be 'None' if not found in above function.
    return browser

def getBrowserThatSentLowestNumberOfMessages(browsers):
    lowestIndex = 0
    for idx, b in enumerate(browsers):
        if b.messagesSent < browsers[lowestIndex].messagesSent:
            lowestIndex = idx
    
    return browsers[lowestIndex]
        