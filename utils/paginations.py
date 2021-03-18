def create_pagination(items, max_values):
	return [
		items[i:i + max_values] for i in range(0, len(items), max_values)
	]

