from djroomba.settings import MATRIX_TELEGRAM_BOT_TOKEN
from django.apps import AppConfig

import logging

from telegram.ext import Updater
from telegram.error import InvalidToken, TelegramError

logger = logging.getLogger(__name__)


class MatrixConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "matrix"
    bot_token = MATRIX_TELEGRAM_BOT_TOKEN

    def ready(self) -> None:
        from matrix.bot import MatrixBot

        logger.debug("{} ready() called".format(__class__.__name__))
        MatrixBot(self.bot_token, self.name)
