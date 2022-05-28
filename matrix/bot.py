import logging
import io

from djroomba.models import TelegramUser
from djroomba.bot_template import BotConfig
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

from matrix.matrix import open_as_image, process_image, send_image
from matrix.models import Image

logger = logging.getLogger(__name__)


class MatrixBot(BotConfig):
    def add_handlers(self, dispatcher):
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(MessageHandler(Filters.photo, self.image))

    @BotConfig.authenticated
    def start(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /start is issued."""
        user = TelegramUser.get_from_update(update)
        message = "Hello {} from {} app".format(user.username, __package__)
        update.message.reply_text(message)

    def image(self, update: Update, context: CallbackContext) -> None:
        try:
            user = TelegramUser.get_from_update(update)
            logger.info("Received a picture from {}".format(user.username))
        except TelegramUser.DoesNotExist:
            logger.info(
                "Received a picture from @{} - {}".format(
                    update.effective_user.username, update.effective_user.id
                )
            )
        file_id = update.message.photo[-1].file_id
        file_downloaded = context.bot.get_file(file_id).download_as_bytearray()
        im = open_as_image(io.BytesIO(file_downloaded))
        send_image(process_image(im))

        Image.store_new(update, im)

        update.message.reply_text("Thanks for the pic! Hoping it was a fun one")
