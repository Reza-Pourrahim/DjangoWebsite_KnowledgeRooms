from django.contrib import admin
from .models import Room, Topic, Message

# Register your models here.


class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "updated")
    search_fields = ("name", "description")


admin.site.register(Room, RoomAdmin)
admin.site.register(Topic)
admin.site.register(Message)
