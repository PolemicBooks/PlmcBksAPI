def to_human(bytes):
	
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

