from django.contrib import admin
from .models import ToDoModel, User

admin.site.register(ToDoModel)
admin.site.register(User)
