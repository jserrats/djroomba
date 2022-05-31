from djroomba.settings import JOM_TELEGRAM_BOT_TOKEN
from django.apps import AppConfig

import logging


logger = logging.getLogger(__name__)


class JomConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jom"
    bot_token = JOM_TELEGRAM_BOT_TOKEN

    def ready(self) -> None:
        from jom.bot import JomBot

        #logger.debug("{} ready() called".format(__class__.__name__))
        JomBot(self.bot_token, self.name)
