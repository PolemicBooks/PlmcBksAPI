import os


# Configurações usadas para realizar login no Telegram.
PYROGRAM_OPTIONS = {
	"session_name": "bot",
	"api_id": None,
	"api_hash": None,
	"workdir": os.path.join(os.getcwd(), ".pyrogram"),
	"no_updates": True,
	"app_version": "(PlmcBksAPI v0.1)"
}

