async def stream_from_response(client, response):
	
	async for chunk in response.aiter_bytes():
		yield chunk
	
	await response.aclose()
	await client.aclose()
	
	return
	
