import telebot
import requests

from ._config import BOT_TOKEN

telegram = telebot.TeleBot(token=BOT_TOKEN)

http = requests.Session()
