#!/usr/bin/python3

# -*- coding: utf-8 -*-

import subprocess
import os

virtualenv = f"{os.getcwd()}/virtualenv"

command = [
	"python3",
	"-m",
	"pip",
	"install",
	"--force-reinstall",
	"--disable-pip-version-check",
	"--no-warn-script-location",
	"--user",
	"--upgrade",
	"setuptools",
	"wheel",
	"virtualenv",
	"pip"
]

subprocess.call(command)

command = [
	"python3",
	"-m",
	"virtualenv",
	"--download",
	"--no-periodic-update",
	virtualenv
]

subprocess.call(command)

command = [
	os.path.join(virtualenv, "bin/pip"),
	"install",
	"--force-reinstall",
	"--disable-pip-version-check",
	"--no-warn-script-location",
	"--upgrade",
	"fastapi",
	"uvicorn",
	"tgcrypto",
	"httpx[http2]",
	"git+https://github.com/SnwMds/pyrogram#egg=Pyrogram",
	"git+https://github.com/PolemicBooks/PlmcBks"
]

subprocess.call(command)
