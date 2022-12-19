# A PLUS
import json
import time

# message = {
#       "action": "connect" | "message" | "disconnect",
# action = "connect"
#       "id": "client_id",
# action = "message"
#       "sender": "sender_id",
#       "recipient": "recipient_id",
#       "timestamp": "timestamp",
#       "data": "message"
# }


def format_message(message: bytes):
    payload = json.loads(message.decode())
    if payload.get("action") == "connect" or payload.get("action") == "disconnect":
        return {
            "action": payload["action"],
            "status": payload.get("status"),
            "client_id": payload.get("id"),
        }
    elif payload.get("action") == "message":
        return {
            "action": payload["action"],
            "sender": payload.get("sender"),
            "recipient": payload.get("recipient"),
            "timestamp": time.time(),
            "data": payload.get("data"),
        }


class Message:
    def __init__(self, payload: dict):
        self.action = payload["action"]
        if self.action == "connect" or self.action == "disconnect":
            self.client_id = payload["id"]
        elif self.action == "connect" or self.action == "disconnect":
            self.client_id = payload["id"]
        elif self.action == "message":
            self.sender = payload["sender"]
            self.recipient = payload["recipient"]
            self.timestamp = payload["timestamp"]
            self.data = payload["data"]

        self.client_id = client_id
        self.message = message
