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

class ChatBot_state(models.Model):

    # The current modes(could be multiples, but some of them are mutually exclusive!) that the chatbot have
    translation_mode = models.CharField(default="dynamic", verbose_name='translation_mode') # mode of translation bot ; could be  dynamic or static
    # dynamic mode represent the real-time translation during chatiing.
    # static mode represent the single word translation.

    @classmethod
    def create_obj_by_dict(cls, **info_dict):
        # basic attribute
        obj = cls(**info_dict)
        if obj not in cls.objects.all():
            obj.save()  # if not has same data in database , update it .
        return obj

class Group(models.Model):

    # user information
    group_id = models.CharField(max_length=100, null=True ,blank=True ,default=None)
    establish_date = models.DateField(default=datetime.date.today)  # the date client send message
    establish_time = models.TimeField(null=True, blank=True)  # the time client send message
    state = models.OneToOneField(ChatBot_state, null=True, blank=True, on_delete=models.CASCADE) # TODO: why primary key used ? https://stackoverflow.com/questions/69054979/why-would-someone-set-primary-key-true-on-an-one-to-one-reationship-onetoonefie

    @classmethod
    def create_obj_by_dict(cls, **info_dict):
        # basic attribute
        obj = cls(**info_dict)
        if obj not in cls.objects.all():
            obj.save()  # if not has same data in database , update it .

        # Here specially handle in case the object exist, since the object must be saved before it can be assigned to a foreign key relationship.
        # Means that we should return the saved one(the existed one should be saved previously :P ), otherwise it will violate the rule above
        else:
            group_id_info = info_dict["group_id"]
            obj = cls.objects.get(group_id=group_id) 

        return obj

class User(models.Model):

    # user information
    user_id = models.CharField(max_length=100, null=True ,blank=True ,default=None)
    target_language = models.CharField(max_length=100, null=True ,blank=True ,default=None)
    
    group = models.ManyToManyField(Group, related_name='user', blank=True) # A User could belong to different Groups at one time ; In contrast, a Group could contain different Users.

    @classmethod
    def create_obj_by_dict(cls, **info_dict):
        # basic attribute
        obj = cls(**info_dict)
        if obj not in cls.objects.all():
            obj.save()  # if not has same data in database , update it .

        # Here specially handle in case the object exist, since the object must be saved before it can be assigned to a foreign key relationship.
        # Means that we should return the saved one(the existed one should be saved previously :P ), otherwise it will violate the rule above
        else:
            user_id_info = info_dict["user_id"]
            target_language_info = info_dict["target_language"]

            # get the object based on user_id, and check if target_language remain unchanged; If not, update and save it.
            obj = cls.objects.get(user_id=user_id_info) 
            if obj.target_language != target_language_info:
                obj.target_language = target_language_info
                obj.save()

        return obj

    def __eq__(self , other):

        # if client with same id and same "login or query" time , it's the same object.
        return self.user_id == other.user_id 

    # TODO: https://stackoverflow.com/questions/61212514/django-model-objects-became-not-hashable-after-upgrading-to-django-2-2
    def __hash__(self):
        return super().__hash__()

class Message(models.Model):

    message = models.CharField(max_length=100, null=True ,blank=True ,default=None) # the message client send
    message_date = models.DateField(default=datetime.date.today)  # the date client send message
    message_time = models.TimeField(default=datetime.datetime.now , null=True, blank=True)  # the time client send message ??? default ???
    language = models.CharField(max_length=100, null=True ,blank=True ,default=None) # the language of message

    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name='message' ,blank=True, null=True)
    group = models.ForeignKey(Group , on_delete=models.CASCADE , related_name='message' ,blank=True, null=True)

    @classmethod
    def create_obj_by_dict(cls, **info_dict):
        # basic attribute
        obj = cls(**info_dict)
        if obj not in cls.objects.all():
            obj.save()  # if not has same data in database , update it .
        return obj
