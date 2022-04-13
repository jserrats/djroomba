from django.contrib import admin

from .models import Joke, Season, Vote


class JokeAdmin(admin.ModelAdmin):
    list_display = ["user", "group", "joke", "pub_date", "season", "score"]
    readonly_fields = ["pub_date", "update_id"]


class SeasonAdmin(admin.ModelAdmin):
    list_display = ["season_id", "init_time", "end_time", "active"]
    readonly_fields = ["init_time"]


admin.site.register(Joke, JokeAdmin)
admin.site.register(Season, SeasonAdmin)
admin.site.register(Vote)
