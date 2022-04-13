from django.db import models
from django.contrib.auth.models import User
from telegram import Update


class TelegramUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.IntegerField(unique=True, null=True)

    @classmethod
    def get_from_update(self, update: Update) -> User:
        """Returns a django User that has sent the given telegram update"""
        telegram_id = update.effective_user.id
        user = self.objects.get(telegram_id=telegram_id).user
        return user

    @classmethod
    def get_from_update_forwarded(self, update: Update) -> User:
        """Returns a django User that has sent the original message from a forwarded message"""
        telegram_id = update.message.forward_from.id
        user = self.objects.get(telegram_id=telegram_id).user
        return user

    def __str__(self) -> str:
        return "{} - {}".format(self.user.username, self.telegram_id)
