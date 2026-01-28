import time
from fastapi import Request
from utils.viewLog import logger


async def process_time_middleware(request: Request, call_next):
	"""Dynamic middleware that tracks processing time from API hit to response"""
	request.state.start_time = time.perf_counter()
	try:
		response = await call_next(request)
		return response
	finally:
		# Calculate and store processing time in milliseconds
		total_time = time.perf_counter() - request.state.start_time
		request.state.process_time_ms = round(total_time * 1000, 2)
		
		logger.info(
			f"{request.method} {request.url.path} "
			f"completed in {request.state.process_time_ms} ms"
		)


