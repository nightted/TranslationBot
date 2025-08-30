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