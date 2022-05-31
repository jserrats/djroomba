from django.db import models
from django.contrib.auth.models import Group
from django.conf import settings

from django.utils import timezone
from telegram import User


class Season(models.Model):
    season_id = models.AutoField(primary_key=True)
    init_time = models.DateTimeField("date started", auto_now_add=True)
    end_time = models.DateTimeField("date ended", blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return "#{}: {}".format(self.season_id, self.init_time.strftime("%d-%b-%Y"))

    @classmethod
    def get_active(self):
        """Returns the only active season"""
        try:
            season = Season.objects.get(active=True)
        except Season.DoesNotExist:
            season = Season()
            season.save()
        return season

    @classmethod
    def change_seasons(self):
        """Ends the last season and creates a new one"""
        try:
            old_season = Season.objects.get(active=True)
            old_season.active = False
            old_season.end_time = timezone.now()
            old_season.save()
        except Season.DoesNotExist:
            pass
        finally:
            season = Season()
            season.save()
        return season


class Joke(models.Model):
    update_id = models.IntegerField(primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    joke = models.TextField(max_length=1000)
    pub_date = models.DateTimeField("date sent", auto_now_add=True)
    score = models.IntegerField(default=0)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return "{}".format(self.joke[:20])

    @classmethod
    def get_voted_jokes(self, voting_user: User, group: Group, season: Season):
        """Returns all jokes from a group during a season that have been voted from a user"""
        votes_from_user = Vote.objects.filter(user=voting_user)
        jokes_voted = Joke.objects.filter(
            votes__in=votes_from_user, group=group, season=season
        )
        return jokes_voted

    @classmethod
    def get_not_voted_jokes(self, voting_user: User, group: Group, season: Season):
        """Returns all jokes from a group during a season that have not been voted yet from a user"""
        return Joke.objects.filter(group=group, season=season).exclude(
            update_id__in=self.get_voted_jokes(voting_user, group, season)
        )

    @classmethod
    def season_joke_podium(self, season: Season, group: Group):
        """Returns the 3 jokes that won the season for this group"""
        return (
            Joke.objects.filter(group=group, season=season)
            .order_by("score")
            .reverse()[:3]
        )


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joke = models.ForeignKey(Joke, on_delete=models.CASCADE, related_name="votes")
    pick = models.SmallIntegerField(default=0)

    def __str__(self) -> str:
        return "{}: {}".format(self.pick, self.user.username)

    @classmethod
    def user_finished_voting(self, voting_user: User, group: Group, season: Season):
        """Checks if a given user has spent all their votes in a season and group"""
        voted_jokes = Joke.get_voted_jokes(voting_user, group, season)
        return voted_jokes.count() == settings.JOM_VOTES_PER_SEASON

    @classmethod
    def group_finished_voting(self, group: Group, season: Season):
        """Check if all users in a group have spent their votes in a season"""
        users = group.user_set.all()
        for user in users:
            if not self.user_finished_voting(user, group, season):
                return False
        return True
