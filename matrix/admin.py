from django.contrib import admin

from .models import Image

class ImageAdmin(admin.ModelAdmin):
    list_display = ["date","telegram_id", "telegram_username", "user", "favorite"]
    readonly_fields = ["date"]

admin.site.register(Image,ImageAdmin)