#!/usr/bin/python3

# -*- coding: utf-8 -*-

import subprocess
import os
import platform
import urllib.parse
import http.client


if __name__ != '__main__':
	quit()

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
	"uvicorn[standard]",
	"pyrogram==1.1.13",
	"tgcrypto",
	"aiohttp[speedups]",
	"git+https://github.com/PolemicBooks/PlmcBks"
]

subprocess.call(command)

site_packages = os.path.join(virtualenv, f"lib/python{python_version}/site-packages")

urls = [
	(
		"https://raw.githubusercontent.com/SnwMds/pyrogram/master/pyrogram/client.py",
		os.path.join(site_packages, "pyrogram/client.py")
	),
	(
		"https://raw.githubusercontent.com/SnwMds/pyrogram/master/pyrogram/methods/messages/download_media.py",
		os.path.join(site_packages, "pyrogram/methods/messages/download_media.py")
	)
]

for url, file in urls:
	
	scheme, netloc, path, params, query, fragment = urllib.parse.urlparse(url)
	
	connection = http.client.HTTPSConnection(netloc, timeout=8)
	connection.request("GET", path)
	
	response = connection.getresponse()
	content = response.read().decode()
	
	with open(file=file, mode="w") as pyfile:
		pyfile.write(content)
