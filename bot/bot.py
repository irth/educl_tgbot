from telegram.ext import CommandHandler
from telegram.ext import Updater
import telegram.ext
import telegram
import os
import json
import logging
import redis
import uuid
BASE_URL = os.environ['BASE_URL']

r = redis.Redis(host=os.environ.get('REDIS_HOST', "localhost"),
                port=os.environ.get('REDIS_PORT', 6379), db=0)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = Updater(token=os.environ['TELEGRAM_TOKEN'], use_context=True)
dispatcher = updater.dispatcher


def start(update: telegram.Update, context):
    # TODO: disallow working in multi user chats

    token = uuid.uuid4().hex
    r.set("chat_id_by_token:%s" % token, update.effective_chat.id)
    url = "%s/login/%s" % (BASE_URL, token)
    context.bot.send_message(
        parse_mode="HTML",
        chat_id=update.effective_chat.id,
        text="<b>Hi!</b> I am a bot that sends you messages from WUST's EdukacjaCL (with content!) on Telegram. <a href=\"%s\">Click here</a> to log in with your Edukacja account." % url)


def logout(update: telegram.Update, context: telegram.ext.CallbackContext):
    if len(context.args) == 0 or context.args[0].upper() != "YES":
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please type \"/logout yes\" to confirm."
        )
        return
    r.publish("logout", json.dumps({
        "chat_id": update.effective_chat.id
    }))
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Logging out...")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

logout_handler = CommandHandler('logout', logout)
dispatcher.add_handler(logout_handler)

jq = updater.job_queue

pubsub = r.pubsub()


def login_results_handler(message):
    payload = json.loads(message['data'])

    def send_results(context: telegram.ext.CallbackContext):
        msg = ""
        if payload['success']:
            msg = "You are now logged in. We will notify you of any new EdukacjaCL messages. Type /login any time to log out"
        else:
            msg = "We could not log you in. Try again by typing or clicking /start."
        context.bot.send_message(chat_id=int(payload['chat_id']), text=msg)
    jq.run_once(send_results, 0)


def logout_results_handler(message):
    payload = json.loads(message['data'])

    def send_result(context: telegram.ext.CallbackContext):
        msg = ""
        if payload['success']:
            msg = "You are now logged out."
        else:
            msg = "An error occured. Try again later."
        context.bot.send_message(chat_id=payload['chat_id'], text=msg)
    jq.run_once(send_result, 0)


pubsub.subscribe(login_results=login_results_handler,
                 logout_results=logout_results_handler)
thread = pubsub.run_in_thread(sleep_time=0.001)

updater.start_polling()
