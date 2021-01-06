from llama.base import LlamaBase


class Trader(LlamaBase):
    """
    Immutable, json-izable class with a timestamp
    """

    @classmethod
    def has_timestamp(cls) -> bool:
        return True

    @classmethod
    def db_table_name(cls) -> str:
        return "trader"

    @classmethod
    def is_immutable(cls) -> bool:
        return False
