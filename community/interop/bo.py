import json
import dataclasses

from iop import BusinessOperation

from interop.msg import HttpMessageRequest, HttpMessageResponse

class BO(BusinessOperation):
    def on_http_request(self, message_request: HttpMessageRequest)->HttpMessageResponse:
        try:
            payload = dataclasses.asdict(message_request)
            response = HttpMessageResponse(
                status=200,
                headers={'Content-Type': 'application/json'},
                body=json.dumps(payload),
            )
            return response
        except Exception as exc:
            self.log_error(f"BO.on_http_request failed: {exc}")
            return HttpMessageResponse(
                status=500,
                headers={'Content-Type': 'application/json'},
                body=json.dumps({
                    'error': 'bo_processing_failed',
                    'detail': str(exc)
                }),
            )