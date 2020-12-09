import json
import signal
import time

from .channel import Channel, ChannelError, MessageFormatError, MessageTimeout


class ChannelWebSocket(Channel):
    def __init__(self, ws):
        self._ws = ws

    def close(self):
        self._ws.close()

    def send_message(self, message):
        if self._ws.closed:
            raise ChannelError("Unable to send data to the remote host (not connected)")

        try:
            self._ws.send(json.dumps(message))
        except:
            raise ChannelError("Unable to send data to the remote host")

    def recv_message(self, timeout_epoch=None):
        def timeout_handler(signum, frame):
            raise MessageTimeout("Timed out")

        if self._ws.closed:
            raise ChannelError("Unable to receive data from the remote host (not connected)")

        if timeout_epoch:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(round(timeout_epoch - time.time())))

        try:
            message = self._ws.receive()
        finally:
            if timeout_epoch:
                signal.alarm(0)

        if not message:
            raise ChannelError("Unable to receive data from the remote host (message was empty)")
        try:
            # Deserialize and return the message
            return json.loads(message)
        except ValueError:
            # Invalid json
            raise MessageFormatError(desc="Unable to decode the JSON message")
