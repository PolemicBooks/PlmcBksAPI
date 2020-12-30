import re

def bytes_to_human(bytes):
	
	bytes = float(bytes)
	kilobytes = float(1024)
	megabytes = float(kilobytes ** 2)
	gigabytes = float(kilobytes ** 3)
	terabytes = float(kilobytes ** 4)
	
	if bytes < kilobytes:
		return '{0} {1}'.format(bytes, 'Bytes' if 0 == bytes > 1 else 'Byte')
	
	if kilobytes <= bytes < megabytes:
		return '{0:.2f} KB'.format(bytes / kilobytes)
	
	if megabytes <= bytes < gigabytes:
		return '{0:.2f} MB'.format(bytes / megabytes)
	
	if gigabytes <= bytes < terabytes:
		return '{0:.2f} GB'.format(bytes / gigabytes)
	
	if terabytes <= bytes:
		return '{0:.2f} TB'.format(bytes / terabytes)


def convert_filename(filename):
	return filename.rstrip(' ')[:240].replace("/", ",").replace("  ", " ").replace("_", " ")


def human_duration_to_seconds(text):
	
	total_seconds = 0
	
	results = re.findall(r"\n\*\*Duração\*\*:\s__([0-9]+) dia\(s\), ([0-9]+) hora\(s\), ([0-9]+) minuto\(s\) e ([0-9]+) segundo\(s\)__", text)
	
	if results:
		for days, hours, minutes, seconds in results:
			total_seconds = total_seconds + int(days) * 86400
			total_seconds = total_seconds + int(hours) * 3600
			total_seconds = total_seconds + int(minutes) * 60
			total_seconds = total_seconds + int(seconds)
	else:
		results = re.findall(r"\n\*\*Duração\*\*:\s__([0-9]+) hora\(s\), ([0-9]+) minuto\(s\) e ([0-9]+) segundo\(s\)__", text)
		if not results:
			return None
		for hours, minutes, seconds in results:
			total_seconds = total_seconds + int(hours) * 3600
			total_seconds = total_seconds + int(minutes) * 60
			total_seconds = total_seconds + int(seconds)
	
	return total_seconds

def capitalize_words(string):
	return " ".join([word.capitalize() if not word.istitle() and len(word) > 3 else word for word in string.split(" ")])
