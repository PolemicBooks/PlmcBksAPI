async def stream_from_response(response):
	
	async for chunk in response.aiter_bytes():
		yield media_bytes
	
	await response.aclose()
	
	return
	
