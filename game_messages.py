import tcod
import textwrap
from typing import Tuple, Dict, Union


class Message:
    def __init__(self, text: str, color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        self.text = text
        self.color = color

    def to_json(self) -> Dict:
        json_data = {
            "text": self.text,
            "color": self.color
        }

        return json_data

    @staticmethod
    def from_json(json_data: Dict) -> Union["Message", None]:
        if json_data is not None:
            text = json_data["text"]
            color = json_data["color"]

            return Message(text, color)

        return None


class MessageLog:
    def __init__(self, x: int, width: int, height: int):
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def to_json(self) -> Dict:
        json_data = {
            "messages": [message.to_json() for message in self.messages],
            "x": self.x,
            "width": self.width,
            "height": self.height
        }

        return json_data

    @staticmethod
    def from_json(json_data: Dict) -> "MessageLog":
        messages_data = json_data["messages"]
        messages = [Message.from_json(message_data) for message_data in messages_data]
        x = json_data["x"]
        width = json_data["width"]
        height = json_data["height"]

        message_log = MessageLog(x, width, height)
        message_log.messages = messages

        return message_log

    def add_message(self, message: Message):
        new_msg_lines = textwrap.wrap(message.text, self.width)

        for line in new_msg_lines:
            if len(self.messages) == self.height:
                del self.messages[0]


            self.messages.append(Message(line, message.color))
