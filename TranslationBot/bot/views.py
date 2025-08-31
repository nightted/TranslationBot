# Python internal functions
import configparser
import os
import random
import matplotlib.pyplot as plt
import pyimgur

# Customerized functions 
from google.cloud import translate

# Django related functions
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from bot.models import *

# Line-ChatBot related functions
from linebot import (
    LineBotApi, WebhookParser , WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (

    MessageEvent, # message  event
    PostbackEvent, # postback event
    FollowEvent, # follow event
    JoinEvent, # join event 

    # Receive message
    TextMessage ,
    StickerMessage ,
    LocationMessage ,

    # Send messages
    TextSendMessage, # send text reply
    FlexSendMessage, # send flex-template reply
    LocationSendMessage, # send location map
    ImageSendMessage,

)

# Google Cloud translate settings
project_id = "gen-lang-client-0876463969"
parent = f"projects/{project_id}"
json_file = os.path.join(os.path.dirname(__file__), 'gcp_key.json')
client = translate.TranslationServiceClient.from_service_account_json(json_file)
mime_type = "text/plain"

# Line bot settings
config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(__file__), 'config.ini') # https://stackoverflow.com/questions/29426483/python3-configparser-keyerror-when-run-as-cronjob
config.read(config_file)

LINE_CHANNEL_ACCESS_TOKEN = config['secret']['channel_access_token']
LINE_CHANNEL_SECRET = config['secret']['channel_secret']
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN) # set line bot api
handler = WebhookHandler(LINE_CHANNEL_SECRET) # set handle

@csrf_exempt
def callback(request):

    if request.method == 'POST':

        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            handler.handle( body , signature )

        except InvalidSignatureError:
            print("DEBUG : InvalidSignatureError!!!")
            return HttpResponseForbidden()
        except LineBotApiError:
            print("DEBUG : LineBotApiError!!!")
            return HttpResponseBadRequest()

        return HttpResponse()

    else:
        print("DEBUG : HttpResponseBadRequest!!!")
        return HttpResponseBadRequest()

# Detect the language based on the text input 
def detect_language(text):

    response = client.detect_language(parent=parent, content=text)

    return response.languages[0].language_code, response.languages[0].confidence 

# Return all the supported language by cloud translation
def return_supported_languages(display_language_code):

    response = client.get_supported_languages(
        parent=parent,
        display_language_code=display_language_code,
    )

    lang_map = {} # dict to store the language mapping
    languages = response.languages
    for language in languages:
        language_code = language.language_code
        display_name = language.display_name
        lang_map[language_code] = display_name
        
    return lang_map

@handler.add(JoinEvent)
def handle_follow_event(event):

    group_id = event.source.group_id
    group_establish_time = event.timestamp
    group_establish_time_dt = datetime.datetime.fromtimestamp(group_establish_time/1000.0)

    group_info = {
        "group_id" : group_id,
        "establish_time" : group_establish_time_dt, 
    }
    group_obj = Group.create_obj_by_dict(**group_info)

    join_text = f"Welcome to this chat group and the group id is : {group_id}"
    reply_action = [TextSendMessage(text=join_text)]
    line_bot_api.reply_message(
        event.reply_token,
        reply_action
    )

@handler.add(MessageEvent, message=[TextMessage , StickerMessage])
def handle_message(event):

    '''
        # function: handling the message event

        :param event: line-bot event object

        :return: None
    '''

    # TODO:
    # To determine the mechanism of how opposite site know and how to get the target language from my site? 
    # Normally the message should be sent by opposite site, how do the bot know the target language of my site?
    # Set up a new feature called the "translated language now" in model ChatBot_Status???

    target_lang = "en"
    
    user_id = event.source.user_id
    received_msg_time = event.timestamp
    received_msg_time_dt = datetime.datetime.fromtimestamp(received_msg_time/1000.0)
    received_msg = event.message.text

    detect_lang, cfd = detect_language(received_msg) # detect the language
    map_lang = return_supported_languages(target_lang) # get the mapping of all supported laguage, and display the mapped name by detected language above

    # create User's object
    user_info = {
        "user_id" : user_id,
        "target_language" : detect_lang,
    }
    user_obj = User.create_obj_by_dict(**user_info)

    # Create a Message's object and link it to User
    msg_info = {
        "message" : received_msg,
        "message_time" : received_msg_time_dt,
        "user" : user_obj, # link message to user
    }
    msg_obj = Message.create_obj_by_dict(**msg_info)

    # Check if User is in specific Group or not, If yes, link Group to User & link Message to Group  ; If not, skip it.
    if "group_id" in vars(event.source):
        group_id = event.source.group_id # check if group attributes exist
        group_obj = Group.objects.get(group_id=group_id)   # If exists, get the group object of this chat group ,aim to point the foreign-key of User to Group
        user_obj.group.add(group_obj) # link Group to User # Could not add Group obj when creating a instance in ManyToMany Field (Note that in ManyToOne Field, it could!). See:  https://stackoverflow.com/questions/50015204/direct-assignment-to-the-forward-side-of-a-many-to-many-set-is-prohibited-use-e
        group_obj.message.add(msg_obj) # link Message to Group 



    # Only do translation in case detected language is differ from target one; Else return the origonal contents.
    if detect_lang != target_lang:

        response = client.translate_text(
            contents=[received_msg],
            parent=parent,
            mime_type=mime_type,
            source_language_code = detect_lang,
            target_language_code = target_lang,
        )
        #result = client.translate(received_msg, target_language="en")
        translated_msg = f"({map_lang[target_lang]})" + str(response.translations[0].translated_text)

    else:
        translated_msg = f"({map_lang[target_lang]})" + received_msg

    #translated_msg = str( "group_id" in vars(event.source))

    reply_action = [TextSendMessage(text=translated_msg)]
    line_bot_api.reply_message(
        event.reply_token,
        reply_action
    )