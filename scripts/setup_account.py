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

OPTIONS = {
	"session_name": "bot",
	"api_id": options.api_id,
	"api_hash": options.api_hash,
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
