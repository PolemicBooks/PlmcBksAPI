HTTP_HEADERS = [
	("Access-Control-Allow-Methods", "*"),
	("Access-Control-Allow-Headers", "*"),
	("Access-Control-Allow-Origin", "*"),
	("Access-Control-Expose-Headers", "*"),
	("Access-Control-Max-Age", "3600"),
	("Cache-Control", "public, max-age=3600"),
	("Cross-Origin-Embedder-Policy", "require-corp"),
	("Cross-Origin-Opener-Policy", "same-origin"),
	("Cross-Origin-Resource-Policy", "cross-origin"),
	("X-Content-Type-Options", "nosniff"),
	("Referrer-Policy", "no-referrer"),
	("Content-Security-Policy", "; ".join(
		[
			"default-src 'none'",
			"connect-src 'self'",
			"img-src https://fastapi.tiangolo.com",
			"script-src 'unsafe-inline' https://cdn.jsdelivr.net",
			"style-src https://cdn.jsdelivr.net",
			"frame-ancestors 'none'",
			"form-action 'none'",
			"navigate-to 'none'"
		]
	)),
	("Accept-Ranges", "none"),
	("Permissions-Policy", ", ".join(
		[
			"accelerometer=()",
			"ambient-light-sensor()",
			"autoplay=()",
			"battery=()",
			"camera=()",
			"display-capture=()",
			"document-domain=()",
			"encrypted-media=()",
			"execution-while-not-rendered=()",
			"execution-while-out-of-viewport=()",
			"fullscreen=()",
			"geolocation=()",
			"gyroscope=()",
			"layout-animations=()",
			"legacy-image-formats=()",
			"magnetometer=()",
			"microphone=()",
			"midi=()",
			"navigation-override=()",
			"oversized-images=()",
			"payment=()",
			"picture-in-picture=()",
			"publickey-credentials-get=()",
			"sync-xhr=()",
			"usb=()",
			"vr=()",
			"wake-lock=()",
			"screen-wake-lock=()",
			"web-share=()",
			"xr-spatial-tracking=()",
			"interest-cohort=()"
		]
	)),
	("X-Robots-Tag", ", ".join(
		[
			"noindex",
			"nofollow",
			"noarchive",
			"nocache",
			"noimageindex",
			"noodp"
		]
	))
]
