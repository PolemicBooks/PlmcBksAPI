def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def pagination(items, length):
	return list(chunks(items, length))

def convert_int(string, default_value):
	
	try:
		return int(string)
	except (ValueError, TypeError):
		return default_value