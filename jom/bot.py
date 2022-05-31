import logging

from django.contrib.auth.models import Group
from djroomba.models import TelegramUser
from djroomba.settings import JOM_VOTES_PER_SEASON
from djroomba.bot_template import BotConfig

from telegram import Update, User, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
)

from jom.models import Joke, Season, Vote


logger = logging.getLogger(__name__)

class JomBot(BotConfig):
    def add_handlers(self, dispatcher):
        dispatcher.add_handler(CommandHandler("start", self.start))

        # on non command i.e message - echo the message on Telegram
        dispatcher.add_handler(
            MessageHandler(
                Filters.text & ~Filters.command & ~Filters.forwarded, self.joke
            )
        )
        dispatcher.add_handler(MessageHandler(Filters.forwarded, self.joke_forwarded))
        dispatcher.add_handler(CallbackQueryHandler(self.vote_joke))

    @BotConfig.authenticated
    def start(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /start is issued."""
        user = TelegramUser.get_from_update(update)
        message = "Hello {}".format(user.username)
        update.message.reply_text(message)

    @BotConfig.authenticated
    def joke(self, update: Update, context: CallbackContext):
        """Add a new joke to the database"""
        logging.debug("New update - direct joke")
        user = TelegramUser.get_from_update(update)
        message = self.store_joke(user, update)
        update.message.reply_text(message)

    @BotConfig.authenticated
    def joke_forwarded(self, update: Update, context: CallbackContext):
        """Add a new joke to the database that has been forwarded from another user"""
        logging.debug("New update - forwarded joke")
        try:
            user = TelegramUser.get_from_update_forwarded(update)
            message = self.store_joke(user, update)
            logger.info(
                "User @{} - {} stored joke forwarded from @{} - {}".format(
                    update.effective_user.username,
                    update.effective_user.id,
                    update.message.forward_from.username,
                    update.message.forward_from.id,
                )
            )
        except TelegramUser.DoesNotExist:
            message = "User @{} - {} is not on the database".format(
                update.message.forward_from.username,
                update.message.forward_from.id,
            )
            logger.warn(
                "User @{} - {} tried to forward message from @{} - {}".format(
                    update.effective_user.username,
                    update.effective_user.id,
                    update.message.forward_from.username,
                    update.message.forward_from.id,
                )
            )
        finally:
            update.message.reply_text(message)

    def store_joke(self, user: User, update: Update):
        """Store the joke in the database"""
        group = user.groups.all()[0]  # TODO: add a group selector
        joke = Joke(
            user=user,
            group=group,
            joke=update.message.text,
            update_id=update.update_id,
            season=Season.get_active(),
        )
        joke.save()
        message = "Joke saved at {}:{}".format(user.username, group.name)
        return message

    @BotConfig.authenticated
    def vote_joke(self, update: Update, context: CallbackContext):
        """Handle a callback query from a InlineKeyboard"""
        query = update.callback_query
        query.answer()

        ## retrieve user and joke objects
        user = TelegramUser.get_from_update(update)
        joke = Joke.objects.get(update_id=query.data)

        ## get the jokes already voted by this user
        voted_jokes = Joke.get_voted_jokes(
            voting_user=user, group=joke.group, season=joke.season
        )
        times_voted = voted_jokes.count()

        logging.info(
            "User @{} has voted {} times".format(user.username, times_voted + 1)
        )

        if times_voted >= JOM_VOTES_PER_SEASON:
            query.edit_message_text(text="You have voted enough already")
        else:
            # if user still has votes left
            # we create a new vote and save it
            vote = Vote(joke=joke, user=user, pick=times_voted + 1)
            vote.save()

            # the choosen joke gets an updated score
            joke.score = joke.score + JOM_VOTES_PER_SEASON - times_voted
            joke.save()

            not_voted_jokes = Joke.get_not_voted_jokes(
                voting_user=user, group=joke.group, season=joke.season
            )

            # if the user has no more votes left we quit
            if times_voted > (JOM_VOTES_PER_SEASON - 2):
                query.edit_message_text(text=f"Thank you for voting!")
            else:
                # generating the keyboard with all the options not already voted
                keyboard = []
                message = "Time to choose the best joke!\n"
                for index, joke in enumerate(not_voted_jokes):
                    message = message + "{}: {}\n".format(index, joke.joke)
                    keyboard.append(
                        [
                            InlineKeyboardButton(
                                "📩{}: {}".format(index, joke.joke),
                                callback_data=joke.update_id,
                            )
                        ]
                    )

                # reply with new keyboard options
                query.edit_message_text(
                    text=message,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )

        votation_ended = Vote.group_finished_voting(joke.group, joke.season)
        logging.info(
            "Group {} has finished voting? {}".format(joke.group.name, votation_ended)
        )

        # if everybody has voted, we can announce the results
        if votation_ended:
            self.votation_ended(joke.group, joke.season)

        else:
            user_ended = Vote.user_finished_voting(
                voting_user=user, group=joke.group, season=joke.season
            )
            logging.info(
                "User {} has finished voting? {}".format(user.username, user_ended)
            )

            # if this user has ended voting we can remind other users
            if user_ended:
                for group_user in joke.group.user_set.exclude(
                    username__in=user.username
                ):
                    if not Vote.user_finished_voting(
                        voting_user=group_user, group=joke.group, season=joke.season
                    ):
                        self.send_reminder(group_user)

    def send_reminder(self, user):
        """Sends a reminder to a user that they still have votes left"""
        message = """Hello! This is a friendly reminder that you have not completed your voting yet! 
        Somebody on your group has already completed it and is waiting for you"""
        self.bot.send_message(user.telegramuser.telegram_id, message)

    def votation_ended(self, group: Group, season: Season):
        message = "Hello {}! Season {} has ended! These are the winner jokes:"
        winner_jokes = Joke.objects.filter(season=season, group=group).order_by(
            "-score"
        )

        podium = "\n🥇 {} - {} \n🥈 {} - {} \n🥉 {} - {}".format(
            winner_jokes[0].user.username,
            winner_jokes[0].joke,
            winner_jokes[1].user.username,
            winner_jokes[1].joke,
            winner_jokes[2].user.username,
            winner_jokes[2].joke,
        )

        for user in group.user_set.all():
            result_message = message.format(user.username, season.season_id) + podium
            self.bot.send_message(user.telegramuser.telegram_id, result_message)

    def help_command(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /help is issued."""
        update.message.reply_text(
            "Write me a joke and I will add it to the contest of this season.\nYou can also forward it directly from the chat and I will assign it to the right user"
        )
