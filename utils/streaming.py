async def stream_from_response(response):
	
	async for chunk in response.aiter_bytes():
		yield chunk
	
	await response.aclose()
	
	return
	
