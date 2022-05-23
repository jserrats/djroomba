from django.apps import AppConfig
from djroomba.settings import JOM_TELEGRAM_BOT_TOKEN, DEBUG

import logging
import os

from telegram.ext import Updater
from telegram.error import InvalidToken, TelegramError


logger = logging.getLogger(__name__)


class JomConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jom"
    bot_token = JOM_TELEGRAM_BOT_TOKEN
    dispatcher = ""
    bot = ""
    botconfig = ""
    updater = ""

    def ready(self) -> None:

        from jom.bot import BotConfig

        logger.debug("{} ready() called".format(__class__.__name__))
        logger.info("DJRoomba - JOM started with Debug {}".format(DEBUG))
        if self.bot_token is None:
            logger.info("JOM_TELEGRAM_BOT_TOKEN not available, disabling polling")
            return
        try:
            self.updater = Updater(token=self.bot_token)
            self.bot = self.updater.bot
            JomConfig.updater = self.updater
            JomConfig.dispatcher = self.updater.dispatcher
        except InvalidToken:
            logger.error("Invalid Token : {}".format(self.bot_token))
            return
        except TelegramError as er:
            logger.error("Error : {}".format(repr(er)))
            return

        self.botconfig = BotConfig(updater=self.updater)

        if os.environ.get(
            "RUN_MAIN", ""
        ) != "true" and "gunicorn" not in os.environ.get("SERVER_SOFTWARE", ""):
            # logger.info("No server detected. Telegram bot won't be started")
            return

        JomConfig.updater.start_polling()
        logger.info("Bot {} started polling".format(self.bot.name))
