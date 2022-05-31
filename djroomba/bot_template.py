import logging
import traceback
import os

from djroomba.settings import DEBUG


from django.db import connection
from django.core.exceptions import ObjectDoesNotExist

from telegram.ext import Updater, CallbackContext
from telegram.error import InvalidToken, TelegramError, NetworkError


class BotConfig:
    def __init__(self, bot_token, app_name) -> None:
        BotConfig.logger = logging.getLogger(app_name)
        if os.environ.get(
            "RUN_MAIN", ""
        ) != "true" and "gunicorn" not in os.environ.get("SERVER_SOFTWARE", ""):
            # logger.info("No server detected. Telegram bot won't be started")
            return

        self.logger.info("DJRoomba - {} started with Debug {}".format(app_name, DEBUG))
        if bot_token is None:
            self.logger.info(
                "{0}_TELEGRAM_BOT_TOKEN not available, disabling polling for {0}".format(
                    app_name.upper()
                )
            )
            return
        try:
            self.updater = Updater(token=bot_token)
            self.bot = self.updater.bot
        except InvalidToken:
            self.logger.error("Invalid Token : '{}'".format(bot_token))
            return
        except TelegramError as er:
            self.logger.error("Error : {}".format(repr(er)))
            return

        dispatcher = self.updater.dispatcher
        dispatcher.add_error_handler(self.error_handler)
        self.add_handlers(dispatcher)

        self.logger.debug("Bot {} finished adding handlers".format(self.bot.name))

        self.updater.start_polling()
        self.logger.info("Bot {} started polling".format(self.bot.name))

    def add_handlers(dispatcher):
        pass

    def error_handler(self, update: object, context: CallbackContext) -> None:
        """Log the error"""
        
        # ignore the NetworkError error, since it fixes itself, and if not, we won't ever know
        if type(context.error) == NetworkError:
            return
        
        # traceback.format_exception returns the usual python message about an exception, but as a
        # list of strings rather than a single string, so we have to join them together.
        tb_list = traceback.format_exception(
            None, context.error, context.error.__traceback__
        )
        tb_string = "".join(tb_list)
        self.logger.info(
            f"The follwing message will have an exception for {type(context.error).__name__}"
        )
        self.logger.exception(
            msg=f"Bot {self.bot.name} - Exception while handling an update:\n{tb_string}"
        )
        # Finally, send the message
        # context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)

    def authenticated(func):
        """Check that only users in the database have access to the bot"""

        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except ObjectDoesNotExist:
                update = args[1]
                message = (
                    "You are not in the database. Your telegram user id is {}".format(
                        update.effective_user.id
                    )
                )
                update.message.reply_text(message)
                args[0].logger.warn(
                    "User @{} - {} tried to use the bot".format(
                        update.effective_user.username, update.effective_user.id
                    )
                )
            finally:
                connection.close()  # https://code.djangoproject.com/ticket/21597#no1

        return wrapper
