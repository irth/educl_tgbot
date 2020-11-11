from telegram.ext import CommandHandler
from telegram.ext import Updater
import telegram
import os
import logging
import redis
import uuid
BASE_URL = os.environ['BASE_URL']

r = redis.Redis(host=os.environ['REDIS_HOST'],
                port=os.environ.get('REDIS_PORT', 6379), db=0)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = Updater(token=os.environ['TELEGRAM_TOKEN'], use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    # TODO: disallow working in multi user chats

    token = uuid.uuid4().hex
    r.set("user_id_by_token:%s" % token, update.effective_user.id)
    url = "%s/login/%s" % (BASE_URL, token)
    context.bot.send_message(
        parse_mode="HTML",
        chat_id=update.effective_chat.id,
        text="<b>Hi!</b> I am a bot that sends you messages from WUST's EdukacjaCL (with content!) on Telegram. <a href=\"%s\">Click here</a> to log in with your Edukacja account." % url)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()
