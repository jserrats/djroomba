from django.db import models
from django.conf import settings
from django.core.files import File

from djroomba.models import TelegramUser

from telegram import Update
from PIL import Image

import io

# Create your models here.
class Image(models.Model):
    date = models.DateTimeField("date received", auto_now_add=True)
    photo = models.ImageField(upload_to="matrix")
    telegram_id = models.IntegerField()
    telegram_username = models.CharField(max_length=255)
    favorite = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self) -> str:
        return "{} - {}".format(self.telegram_username, self.date)

    @classmethod
    def store_new(self, update: Update, im: Image):
        """Look up if the update comes from a registered user and store accordingly"""
        file_id = update.message.photo[-1].file_id
        blob = io.BytesIO()
        im.save(blob, "PNG")
        stored_file = File(blob, name=f"{file_id}.png")
        try:
            user = TelegramUser.get_from_update(update)
            image = Image(
                photo=stored_file,
                telegram_id=update.effective_user.id,
                telegram_username=update.effective_user.username,
                user=user,
            )
        except TelegramUser.DoesNotExist:
            image = Image(
                photo=stored_file,
                telegram_id=update.effective_user.id,
                telegram_username=update.effective_user.username,
            )
        finally:
            image.save()
            return image
