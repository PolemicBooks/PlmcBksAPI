#!/usr/bin/python3

# -*- coding: utf-8 -*-

import argparse
import os

import pyrogram
from pyrogram.errors import ChannelInvalid, ChannelPrivate

if __name__ != '__main__':
	quit()

parser = argparse.ArgumentParser()

parser.add_argument("--api-id", type=int, help="telegram api id", required=True)
parser.add_argument("--api-hash", type=str, help="telegram api hash", required=True)

options = parser.parse_args()

api_id = options.api_id
api_hash = options.api_hash

OPTIONS = {
	"session_name": "bot",
	"api_id": api_id,
	"api_hash": api_hash,
	"no_updates": True,
	"app_version": "PlmcBksAPI v0.1 (PolemicBooks/PlmcBksAPI)",
	"workdir": "./.pyrogram"
}

session_file = "./.pyrogram/bot.session"

if os.path.exists(session_file):
	os.remove(session_file)

client = pyrogram.Client(**OPTIONS)
client.start()

try:
	chat = client.get_chat(chat_id=-1001436494509)
except (ChannelInvalid, ChannelPrivate):
	client.join_chat("https://t.me/joinchat/VZ8qrRKuIvT4gDBa")
else:
	if not chat:
		client.join_chat("https://t.me/joinchat/VZ8qrRKuIvT4gDBa")

config = f"""\
import os


# Configurações usadas para realizar login no Telegram.
PYROGRAM_OPTIONS = {{
	"session_name": "bot",
	"api_id": {api_id},
	"api_hash": "{api_hash}",
	"workdir": os.path.join(os.getcwd(), ".pyrogram"),
	"no_updates": True,
	"app_version": "(PlmcBksAPI v0.1)"
}}
"""

with open(file="./config/pyrogram/config.py", mode="w") as file:
	file.write(config)
