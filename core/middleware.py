import logging

logger = logging.getLogger("django")

class LogAPIErrorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code >= 400:
            logger.warning(f"{request.method} {request.path} | Status: {response.status_code}")
        return response
