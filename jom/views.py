from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from jom.models import Joke, Season
from django.contrib.auth.models import User


@login_required
def index(request):
    group = request.user.groups.all()[0]
    all_seasons = Season.objects.all().order_by("season_id").reverse()

    seasons = {}

    for season in all_seasons:
        jokes = Joke.season_joke_podium(group=group, season=season)
        jokes_list = []
        for joke in jokes:
            jokes_list.append(joke)
        seasons[season] = jokes_list

    users = User.objects.all().filter(groups=group)

    all_time_score = {}
    for user in users:
        all_time_score[user.username] = 0
        jokes = Joke.objects.all().filter(group=group, user=user)
        for joke in jokes:
            all_time_score[user.username] += joke.score

    context = {"scores": all_time_score, "seasons": seasons}
    return render(request, "jom/index.html", context)
