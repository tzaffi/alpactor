from llama.base import LlamaBase


class EventHandler(LlamaBase):
    def __init__(self, debug: bool = False):
        LlamaBase.ctor(self, debug=debug)
        self.add_timestamp()
