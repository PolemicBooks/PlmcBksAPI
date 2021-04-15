HTTP_HEADERS = [
	("Access-Control-Allow-Methods", "*"),
	("Access-Control-Allow-Headers", "*"),
	("Access-Control-Allow-Origin", "*"),
	("Access-Control-Expose-Headers", "*"),
	("Access-Control-Max-Age", "3600"),
	("Content-Language", "en-US"),
	("Cache-Control", "public, max-age=3600"),
	("Cross-Origin-Embedder-Policy", "require-corp"),
	("Cross-Origin-Opener-Policy", "same-origin"),
	("Cross-Origin-Resource-Policy", "cross-origin"),
	("X-Content-Type-Options", "nosniff"),
	("Referrer-Policy", "no-referrer"),
	("Content-Security-Policy", "default-src 'none'; connect-src 'self'; img-src https://fastapi.tiangolo.com; script-src 'unsafe-inline' https://cdn.jsdelivr.net; style-src https://cdn.jsdelivr.net; frame-ancestors 'none'; form-action 'none'; navigate-to 'none'"),
	("Accept-Ranges", "none"),
	("X-Robots-Tag", "noindex, nofollow, noarchive, nocache, noimageindex, noodp"),
	("Strict-Transport-Security", "max-age=31536000"),
	("Alt-Svc", 'http/1.1=":443"; ma=2592000; persist=1; h2=":443"; ma=2592000; persist=1')
]