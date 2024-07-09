from iop import BusinessService
from msg import HttpMessageRequest, HttpMessageResponse

class BS(BusinessService):
    def on_process_input(self, message_input)->HttpMessageResponse:
        # Create a new HttpMessageRequest
        msg = HttpMessageRequest(
            method=message_input.method,
            url=message_input.url,
            headers={k: v for k, v in message_input.headers.items()},
            body=message_input.data.decode('utf-8')
        )
        self.log_info(f"Request: {msg}")
        response = self.send_request_sync('BO', msg)
        return response