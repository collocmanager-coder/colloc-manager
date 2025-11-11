from django.contrib import admin
from users.models import Room,RoomMember
# Register your models here.

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('roomNumber', 'roomTitulor', 'roomStatus')
    list_filter = ('roomStatus',)
    search_fields = ('roomNumber', 'roomTitulor__username')
    ordering = ('roomNumber',)


@admin.register(RoomMember)
class RoomMemberAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phoneNumber', 'memberStatus', 'room')
    list_filter = ('memberStatus', 'room')
    search_fields = ('username', 'email', 'phoneNumber')
    ordering = ('username',)
