from llama.base import LlamaBase


class EventHandler(LlamaBase):
    def __init__(self):
        self.add_timestamp()
        LlamaBase.__init__(self)
