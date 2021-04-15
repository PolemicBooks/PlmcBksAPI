async def stream_from_url(client, media_url):
	
	async with client.get(media_url) as response:
		async for chunk in response.aiter_bytes():
			yield media_bytes
		return
