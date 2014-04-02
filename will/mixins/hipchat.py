import json
import logging
import requests
import traceback

from will import settings

ROOM_NOTIFICATION_URL = "https://api.hipchat.com/v2/room/%(room_id)s/notification?auth_token=%(token)s"
ROOM_TOPIC_URL = "https://api.hipchat.com/v2/room/%(room_id)s/topic?auth_token=%(token)s"
PRIVATE_MESSAGE_URL = "https://api.hipchat.com/v2/user/%(user_id)s/message?auth_token=%(token)s"
SET_TOPIC_URL = "https://api.hipchat.com/v2/room/%(room_id)s/topic?auth_token=%(token)s"
USER_DETAILS_URL = "https://api.hipchat.com/v2/user/%(user_id)s?auth_token=%(token)s"
ALL_USERS_URL = "https://api.hipchat.com/v2/user?auth_token=%(token)s&start-index=%(starti)s&include-deleted=%(includedd)s"


class HipChatMixin(object):

    def send_direct_message(self, user_id, message_body):
        try:
            # https://www.hipchat.com/docs/apiv2/method/private_message_user
            url = PRIVATE_MESSAGE_URL % {"user_id": user_id, "token": settings.WILL_V2_TOKEN}
            data = {"message": message_body}
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            requests.post(url, headers=headers, data=json.dumps(data))
        except:
            logging.critical("Error in send_direct_message: \n%s" % traceback.format_exc())

    def send_direct_message_reply(self, message, message_body):
        try:
            message.reply(message_body).send()
        except:
            logging.critical("Error in send_direct_message_reply: \n%s" % traceback.format_exc())

    def send_room_message(self, room_id, message_body, html=False, color="green", notify=False, **kwargs):
        if kwargs:
            logging.warn("Unknown keyword args for send_room_message: %s" % kwargs)
        
        format = "text"
        if html:
            format = "html"

        try:
            # https://www.hipchat.com/docs/apiv2/method/send_room_notification
            url = ROOM_NOTIFICATION_URL % {"room_id": room_id, "token": settings.WILL_V2_TOKEN}
            
            data = {
                "message": message_body,
                "message_format": format,
                "color": color,
                "notify": notify,
            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            requests.post(url, headers=headers, data=json.dumps(data))
        except:
            logging.critical("Error in send_room_message: \n%s" % traceback.format_exc())

    def set_room_topic(self, room_id, topic):
        try:
            # https://www.hipchat.com/docs/apiv2/method/send_room_notification
            url = ROOM_TOPIC_URL % {"room_id": room_id, "token": settings.WILL_V2_TOKEN}
            
            data = {
                "topic": topic,
            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            requests.put(url, headers=headers, data=json.dumps(data))
        except:
            logging.critical("Error in set_room_topic: \n%s" % traceback.format_exc())

    def get_hipchat_user(self, user_id):
        url = USER_DETAILS_URL % {"user_id": user_id, "token": settings.WILL_V2_TOKEN}
        r = requests.get(url)
        return r.json()

    def get_all_users(self):
        fullroster={}
        url = ALL_USERS_URL % { "token" : settings.WILL_V2_TOKEN, "starti": 0, "includedd": "false" }
        r = requests.get(url)
        for user in r.json()['items']:
            fullroster[user['id']]=user
        while 'next' in r.json()['links']:
            url = '%(link)s&auth_token=%(token)s' % { 'link': r.json()['links']['next'], 'token' : settings.WILL_V2_TOKEN }
            r = requests.get(url)
            for user in r.json()['items']:
                fullroster[user['id']]=user
        return fullroster
