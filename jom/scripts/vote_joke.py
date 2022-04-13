from django.contrib.auth.models import User, Group
import logging
from jom.models import Joke, Season, Vote
from djroomba.settings import TELEGRAM_BOT_TOKEN

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


def run():
    """
    Django script that performs all the necessary stuff in order to change seasons and begin the voting process
    """
    logger.info("Running ending season script!")
    
    if not Season.objects.all():
        logger.info("No season exists at all. Creating it and quitting")
        season = Season.get_active()
        return
    
    bot = Bot(TELEGRAM_BOT_TOKEN)
    groups = Group.objects.all()
    season = Season.get_active()

    for group in groups:
        jokes = Joke.objects.filter(group=group, season=season)
        users = group.user_set.all()

        if not jokes:
            # nobody played :(
            logger.info("Nobody told any joke this season :(")
            message = (
                "Nobody told any joke this season :(\nI hope next one somebody does..."
            )
            for user in users:
                bot.send_message(user.telegramuser.telegram_id, message)
        elif jokes.count() < 3:
            # not enough jokes to make a podium :(
            logger.info("Not enough jokes to make a podium")

            message = "There were less than 3 jokes this month\nEverybody wins! :/"
            for joke in jokes:
                message = message + "\n🥉- {}".format(joke.joke)
                joke.score = 1
                joke.save()

            for user in users:
                bot.send_message(user.telegramuser.telegram_id, message)
        else:
            logger.info("Sending users the podium...")
            for user in users:
                message = "Time to choose the best joke!\n"
                keyboard = []
                for index, joke in enumerate(jokes):
                    message = message + "{}: {}\n".format(index, joke.joke)
                    keyboard.append(
                        [InlineKeyboardButton(joke.joke, callback_data=joke.update_id)]
                    )

                bot.send_message(
                    user.telegramuser.telegram_id,
                    message,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )
    logger.info("Changing seasons")
    season.change_seasons()
