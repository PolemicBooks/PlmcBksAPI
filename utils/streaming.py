async def stream_from_url(client, media_url):
	
	async with client.get(media_url) as response:
		async for media_bytes, _ in response.content.iter_chunks():
			yield media_bytes
