# Django related functions
from django.db import models
from django.contrib.postgres.fields import ArrayField

# Python internal functions
import numpy as np
import datetime

# Create your models here.

# Create a model represent the Users' status, parameters includes the User_id, target language, last message(text), time of last message
# Create a model represent the every chat, parameters includes the text, laguage of text, timestamp of sent text, User_id; And remember link this to the Users' status model (Multiples to one, ForeignKey=User)
# 

class User(models.Model):

    # user information
    user_id = models.CharField(max_length=100, null=True ,blank=True ,default=None)
    target_language = models.CharField(max_length=100, null=True ,blank=True ,default=None)

    @classmethod
    def create_obj_by_dict(cls, **info_dict):
        # basic attribute
        obj = cls(**info_dict)
        if obj not in cls.objects.all():
            obj.save()  # if not has same data in database , update it .

        # Here specially handle in case the object exist, since the object must be saved before it can be assigned to a foreign key relationship.
        # Means that we should return the saved one(the existed one should be saved previously, right?), otherwise it will violate the rule above
        else:
            user_id_info = info_dict["user_id"]
            target_language_info = info_dict["target_language"]

            obj = cls.objects.get(user_id=user_id_info) # if the obj exists, query & get it and then return it
            if obj.target_language != target_language_info:
                obj.target_language = target_language_info
                obj.save()

        return obj

    def __eq__(self , other):

        # if client with same id and same "login or query" time , it's the same object.
        return self.user_id == other.user_id 

class Message(models.Model):

    message = models.CharField(max_length=100, null=True ,blank=True ,default=None) # the message client send
    message_date = models.DateField(default=datetime.date.today)  # the date client send message
    message_time = models.TimeField(null=True, blank=True)  # the time client send message

    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name='message')

    @classmethod
    def create_obj_by_dict(cls, **info_dict):
        # basic attribute
        obj = cls(**info_dict)
        if obj not in cls.objects.all():
            obj.save()  # if not has same data in database , update it .
        return obj


class ChatBot_Status(models.Model):

    # The current modes(could be multiples, but some of them are mutually exclusive!) that the chatbot have
    dynamic_translation_mode = models.BooleanField(default=True, verbose_name='dynamic_mode') # For dynamic translation for multi-person chatting
    static_translation_mode = models.BooleanField(default=False, verbose_name='static_mode') # For single words translation to Chinese

    @classmethod
    def create_obj_by_dict(cls, **info_dict):
        # basic attribute
        obj = cls(**info_dict)
        if obj not in cls.objects.all():
            obj.save()  # if not has same data in database , update it .
        return obj
