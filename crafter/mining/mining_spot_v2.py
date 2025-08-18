from AutoComplete import *
from typing import Callable, List, Any, Union, Optional, Literal, TypeAlias
from threading import Thread


BaseListener: TypeAlias = Callable[[], Union[dict, Literal[False], None]]
BaseCallback: TypeAlias = Callable[[dict], Any]


class BaseHandler:
    def __init__(self, listener: BaseListener, callback: BaseCallback):
        self.listener = listener
        self.callback = callback

    def listen(self):
        return self.listener()

    def handle(self, data: dict):
        return self.callback(data)



class BaseEventGenerator:
    def __init__(self):
        ...