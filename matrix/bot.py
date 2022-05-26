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
        logger.info(str(update.message.photo))
        file_id = update.message.photo[-1].file_id
        file_downloaded = context.bot.get_file(file_id).download_as_bytearray()
        im = open_as_image(io.BytesIO(file_downloaded))
        send_image(process_image(im))
