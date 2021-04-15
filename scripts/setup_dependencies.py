#!/usr/bin/python3

# -*- coding: utf-8 -*-

import subprocess
import os
import platform

major, minor, micro = platform.python_version_tuple()
python_version = float(f"{major}.{minor}")

if not python_version >= 3.6:
	raise ValueError(f"Python {python_version} is not supported!")

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
	"orjson",
	"uvicorn",
	"tgcrypto",
	"aiohttp[speedups]",
	"git+https://github.com/SnwMds/pyrogram#egg=Pyrogram",
	"git+https://github.com/PolemicBooks/PlmcBks"
]

subprocess.call(command)
