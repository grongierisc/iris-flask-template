import json

from iop import BusinessService, target

from interop.msg import HttpMessageRequest, HttpMessageResponse

class BS(BusinessService):
    Output = target()

    def process_input(self, message_input)->HttpMessageResponse:
        try:
            # Build transport-safe request for BO.
            body = message_input.get_data(cache=False, as_text=True)
            msg = HttpMessageRequest(
                method=message_input.method,
                url=message_input.url,
                headers={k: v for k, v in message_input.headers.items()},
                body=body,
            )
            self.log_info(f"Request: {msg}")
            response = self.send_request_sync(self.Output, msg)

            if not isinstance(response, HttpMessageResponse):
                return HttpMessageResponse(
                    status=502,
                    headers={'Content-Type': 'application/json'},
                    body=json.dumps({
                        'error': 'invalid_bo_response',
                        'detail': f'Unexpected response type: {type(response).__name__}'
                    }),
                )

            return response
        except Exception as exc:
            self.log_error(f"BS.sprocess_input failed: {exc}")
            return HttpMessageResponse(
                status=500,
                headers={'Content-Type': 'application/json'},
                body=json.dumps({
                    'error': 'bs_processing_failed',
                    'detail': str(exc)
                }),
            )